from celery import shared_task
from .models import Game, Board
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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