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

def get_current_time(white_time_left, black_time_left, created_at, turn):
    # Calculate the remaining time for each player
    if turn == "white":
        white_time_left -= datetime.now(timezone.utc) - created_at
    else:
        black_time_left -= datetime.now(timezone.utc) - created_at
    return white_time_left, black_time_left

def is_threefold_repetition(prev_boards, next_board, next_castling, next_enpassant, turn):
    # Check for threefold repetition to determine if the game should end in a draw
    repetition = 1
    next_turn_short = "w" if turn == "white" else "b"
    for prev_board in prev_boards:
        if (prev_board.board, prev_board.turn, prev_board.castling, prev_board.enpassant) == (
            json.dumps(next_board), next_turn_short, next_castling, next_enpassant):
            repetition += 1
        if repetition >= 3:
            return True
    return False

def push_new_board_to_database(updated_board, turn, castling, enpassant, winner, total_moves, soft_moves, white_time_left, black_time_left, game_id):
    # Save the new board state to the database
    game = Game.objects.get(pk=game_id)
    if winner:
        db_winner = {"white": "w", "black": "b"}.get(winner, "d")
        game.winner = db_winner
        game.save()

    db_turn = "w" if turn == "white" else "b"

    Board.objects.create(
        game = game,
        total_moves = total_moves,
        board = json.dumps(updated_board),
        turn = db_turn,
        castling = castling,
        enpassant = enpassant,
        soft_moves = soft_moves,
        white_time_left = white_time_left,
        black_time_left = black_time_left
    )

def format_time(white_time_left, black_time_left):
    # Format time values to ensure compatibility with JSON serialization
    return white_time_left.total_seconds(), black_time_left.total_seconds()

def construct_game_state_message(
        white_player, black_player, white_player_ready,
        black_player_ready, winner, board, turn,
        checking, total_moves, soft_moves, 
        white_time_left, black_time_left
    ):
    # Constructs a dictionary containing the game state
    return {
        "white_player": white_player,
        "black_player": black_player,
        "white_player_ready": white_player_ready,
        "black_player_ready": black_player_ready,
        "winner": winner,
        "board": board,
        "turn": turn,
        "checking": checking,
        "total_moves": total_moves,
        "soft_moves": soft_moves,
        "white_time_left": white_time_left,
        "black_time_left": black_time_left,
    }

@shared_task
def computer_move(game_id):
    game = Game.objects.get(pk=game_id)
    prev_state = Board.objects.filter(game=game).latest('id')
    prev_boards = list(Board.objects.filter(game=game))
    prev_board = json.loads(prev_state.board)

    prev_state.turn = "white" if prev_state.turn == "w" else "black"
    
    fen_board = pieces.get_fen(prev_board, prev_state.turn, prev_state.castling, prev_state.enpassant, prev_state.soft_moves, prev_state.total_moves)
    computer = Computer(fen_board)
    best_move = computer.best_move()

    promotion = best_move[4] if len(best_move) > 4 else None
    move = [[], []]

    letter = {"a": 7, "b": 6, "c": 5, "d": 4, "e": 3, "f": 2, "g": 1, "h": 0}
    move[0] = [int(best_move[1]) - 1, letter[best_move[0]]]
    move[1] = [int(best_move[3]) - 1, letter[best_move[2]]]

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

        # Update database with new board state
        push_new_board_to_database(next_board, turn, next_castling, next_enpassant, winner, total_moves, soft_moves, white_time_left, black_time_left, game_id)
    else:
        # Handle invalid move or disconnection
        return
    
    # Format the time values for display
    white_time_left, black_time_left = format_time(white_time_left, black_time_left)

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

    return best_move