import asyncio
import json
from datetime import datetime, timezone

from celery import shared_task
from .models import Game, Board
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from . import pieces
from play_with_computer.stockfishAI import Computer

from math import ceil

@shared_task
def check_game_timeout(game_id, turn, total_moves, board_json):
    turn = "w" if turn == "white" else "b"
    game = Game.objects.get(pk=game_id)
    board = Board.objects.filter(game=game).latest('id')

    # Check if the current board state matches the expected turn and move count
    if board.turn == turn and board.total_moves == total_moves and game.winner == None:
        # Get the remaining time for both players
        white_time_left = board.white_time_left.total_seconds()
        black_time_left = board.black_time_left.total_seconds()

        # Determine if the game has timed out for the current player
        if board.turn == "w":
            game.winner = "b"
            winner = "black"
            white_time_left = 0
        else:
            game.winner = "w"
            winner = "white"
            black_time_left = 0
        
        # Save the game state with the winner
        game.save()

        # Construct the message with the updated game state
        message = {
            "white_player": game.white.username,
            "black_player": game.black.username,
            "white_player_ready": game.white_ready,
            "black_player_ready": game.black_ready,
            "winner": winner,
            "board": board_json,
            "turn": board.turn,
            "checking": None,
            "total_moves": board.total_moves,
            "soft_moves": board.soft_moves,
            "white_time_left": white_time_left,
            "black_time_left": black_time_left
        }

        # Get the channel layer to send a message to the room group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'table_{game.id}',
            {
                'type': 'send_new_game_state',
                **message
            }
        )

@shared_task
def computer_move(game_id):
    from .consumers import get_latest_board_from_database, get_prev_boards_from_database, get_current_time, is_threefold_repetition, push_new_board_to_database, format_time, construct_game_state_message
    
    # Fetch the game instance
    game = Game.objects.get(pk=game_id)

    # Fetch the latest board state and previous boards using asyncio.run to execute async functions
    prev_state = asyncio.run(get_latest_board_from_database(game))
    prev_boards = asyncio.run(get_prev_boards_from_database(game))

    # Convert the board state from JSON to a Python list
    prev_board = json.loads(prev_state.board)
    
    # Initialize the Computer instance with the current game state
    computer = Computer(prev_board, prev_state.turn, prev_state.castling, prev_state.enpassant, prev_state.soft_moves, prev_state.total_moves, game.black.username)

    # Generate the new board state after the computer's move
    move, promotion = computer.best_move()

    # Create the new board state
    next_board, next_castling, next_enpassant, soft_move = pieces.Board(prev_board, prev_state.turn, prev_state.castling, prev_state.enpassant).create_new_json_board(move, promotion)

    # Calculate the remaining time for each player
    white_time_left, black_time_left = get_current_time(prev_state.white_time_left, prev_state.black_time_left, prev_state.created_at, prev_state.turn)

    # Determine the next turn and update move counts
    turn = "black" if prev_state.turn == "white" else "white"
    total_moves = prev_state.total_moves + 1 if turn == "white" else prev_state.total_moves
    soft_moves = prev_state.soft_moves + 1 if soft_move else 0

    # Validate and apply the move
    if next_board:
        board, winner, checking = pieces.Board(next_board, turn, next_castling, next_enpassant).create_json_class()

        # Check for threefold repetition
        if is_threefold_repetition(prev_boards, next_board, next_castling, next_enpassant, turn):
            winner = "draw"

        # Check for the 50 move rule
        if soft_moves == 100:
            winner = "draw"

        # Schedule a task to check for timeout
        if not winner:
            if turn == "white":
                timeout = ceil(white_time_left.total_seconds())
            else:
                timeout = ceil(black_time_left.total_seconds())
            
            check_game_timeout.apply_async((game_id, turn, total_moves, board), countdown=timeout)

        # Push the new board state to the database (async operation)
        asyncio.run(push_new_board_to_database(game_id, next_board, turn, next_castling, next_enpassant, winner, total_moves, soft_moves, white_time_left, black_time_left))
    else:
        # Handle invalid move or disconnection
        return
    
    # Format the time values for display
    white_time_left, black_time_left = format_time(white_time_left, black_time_left)

    # Construct a message to update the game state in the frontend
    message = construct_game_state_message(
        game.white.username, game.black.username, True,
        True, winner, board, turn,
        checking, total_moves, soft_moves,
        white_time_left, black_time_left
        )

    # Get the channel layer to send a message to the room group
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'table_{game.id}',
        {
            'type': 'send_new_game_state',
            **message
        }
    )