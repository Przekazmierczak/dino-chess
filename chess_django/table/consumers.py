import json
from datetime import datetime, timezone, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from .models import Game, Board
from menu.models import User
from . import pieces
from .tasks import check_game_timeout, computer_move

from math import ceil

from lobby.consumers import LobbyConsumer

class TableConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract table ID from the URL route
        self.table_id = self.scope["url_route"]["kwargs"]["table_id"]
        self.table_group_id = f"table_{self.table_id}"

        # Join the room group
        await self.channel_layer.group_add(self.table_group_id, self.channel_name)
        await self.accept()

        # Send the current game state to the new connection
        await self.send_current_state(False)

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(self.table_group_id, self.channel_name)

    async def send_current_state(self, play_audio):
        # Get the current game from the database
        current_game = await get_game_from_database(self.table_id)
        user = self.scope["user"].username
        prev_boards_id_moves = current_game.boards

        # Get player usernames or default names
        white_player = current_game.white.username if current_game.white else "Player 1"
        black_player = current_game.black.username if current_game.black else "Player 2"

        white_avatar = current_game.white.avatar if current_game.white else ""
        black_avatar = current_game.black.avatar if current_game.black else ""

        # Check if the game has started
        if if_game_started(current_game):
            # Fetch the latest board state from the database
            current_state = await get_latest_board_from_database(current_game)
            winner = {"w": "white", "b": "black"}.get(current_game.winner, "draw") if current_game.winner else None
            turn, total_moves, soft_moves, last_move = current_state.turn, current_state.total_moves, current_state.soft_moves, current_state.last_move
            board_id = current_state.id

            # Calculate the remaining time for each player
            white_time_left, black_time_left = get_current_time(current_state.white_time_left, current_state.black_time_left, current_state.created_at, turn)
            white_time_left, black_time_left = format_time(white_time_left, black_time_left)

            # Load the current board state
            current_board_json = json.loads(current_state.board)

            # Determine current player's view
            if ((current_state.turn == "white" and current_game.white.username == user) or
                (current_state.turn == "black" and current_game.black.username == user)) and not winner:
                board, _, checking = pieces.Board(current_board_json, current_state.turn, current_state.castling, current_state.enpassant).create_json_class()
            else:
                board = pieces.boardSimplify(current_board_json)
                checking = current_state.checking

        else:
            # Set up the initial board state if the game hasn't started
            board = pieces.boardSimplify(None)
            winner, turn, checking, total_moves, soft_moves =  None, None, None, 0, 0
            white_time_left, black_time_left, last_move = None, None, None
            board_id = None
        
        # Construct and send the game state message to the room group
        message = construct_game_state_message(
            white_player, black_player, current_game.white_ready,
            current_game.black_ready, winner, board_id, board, turn,
            checking, total_moves, soft_moves,
            white_time_left, black_time_left, last_move,
            prev_boards_id_moves, play_audio, current_game.white_draw, current_game.black_draw,
            white_avatar, black_avatar
            )
        await self.send_game_state_to_websocket(message)

    async def receive(self, text_data):
        # Handle incoming WebSocket messages
        text_data_json = json.loads(text_data)
        current_game = await get_game_from_database(self.table_id)
        user = self.scope["user"]

        # If the message contains a move, handle the move
        if text_data_json["move"]:
            await self.handle_move(current_game, user, text_data_json["move"], text_data_json["promotion"])

        # If the client is requesting the most recent board and it's the current one, send the current state
        elif text_data_json["requested_board"] and text_data_json["requested_board"] == current_game.boards[-1][0]:
            await self.send_current_state(True)

        # If the client is requesting a previous board, handle the request
        elif text_data_json["requested_board"]:
            await self.handle_board_request(current_game, user, text_data_json["requested_board"])

        # If the user clicked resign button, handle the request
        elif text_data_json["resign"]:
            await self.handle_resign(current_game, user)

        # If the user clicked draw button, handle the request
        elif text_data_json["draw"]:
            await self.handle_draw(current_game, user)
        
        # Handle other user actions
        else:
            await self.handle_user_action(current_game, user, text_data_json)

    async def handle_move(self, current_game, user, move, promotion):
        # Get the latest board state and previous boards from the database
        prev_state = await get_latest_board_from_database(current_game)
        prev_boards = await get_prev_boards_from_database(current_game)
        prev_board = json.loads(prev_state.board)
        white_player = current_game.white.username
        black_player = current_game.black.username
        white_avatar = current_game.white.avatar
        black_avatar = current_game.black.avatar
        prev_boards_id_moves = current_game.boards

        # Create the new board state
        next_board, next_castling, next_enpassant, soft_move = pieces.Board(prev_board, prev_state.turn, prev_state.castling, prev_state.enpassant).create_new_json_board(move, promotion)

        # Calculate the remaining time for each player
        white_time_left, black_time_left = get_current_time(prev_state.white_time_left, prev_state.black_time_left, prev_state.created_at, prev_state.turn)
        
        # Determine the next turn and update move counts
        turn = "black" if prev_state.turn == "white" else "white"
        total_moves = prev_state.total_moves + 1 if turn == "white" else prev_state.total_moves
        soft_moves = prev_state.soft_moves + 1 if soft_move else 0

        # Validate and apply the move
        if next_board and ((prev_state.turn == "white" and white_player == user.username) or (prev_state.turn == "black" and black_player == user.username)):
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
                
                check_game_timeout.apply_async((current_game.id, turn, total_moves, board), countdown=timeout)

            # Convert the move to a string representation for database storage and WebSocket communication
            last_move = change_move_to_string(move)

            moved_piece = (board[move[1][0]][move[1][1]]["piece"] if not promotion else "pawn", prev_state.turn)

            checking = [] if not checking else checking

            # Update database with new board state
            new_board_id = await push_new_board_to_database(self.table_id, next_board, turn, next_castling, next_enpassant, winner, total_moves, soft_moves, white_time_left, black_time_left, last_move, moved_piece, checking)
            prev_boards_id_moves.append((new_board_id, last_move, moved_piece))
        else:
            # Handle invalid move or disconnection
            return
        
        # Check if the black player is one of the AI-controlled opponents
        computer = ["Easy AI", "Medium AI", "Hard AI", "Impossible AI"]
        if black_player in computer and prev_state.turn == "white":
            # Schedule a task to make the AI move
            computer_move.apply_async((self.table_id,), countdown=1)

        # Format the time values for display
        white_time_left, black_time_left = format_time(white_time_left, black_time_left)
        
        # Construct and send the game state message to the room group
        message = construct_game_state_message(
            white_player, black_player, current_game.white_ready,
            current_game.black_ready, winner, new_board_id, board, turn,
            checking, total_moves, soft_moves,
            white_time_left, black_time_left, last_move,
            prev_boards_id_moves, True, current_game.white_draw, current_game.black_draw,
            white_avatar, black_avatar
            )
        await self.send_game_state_to_room_group(message)

    async def handle_board_request(self, current_game, user, board_id):
        # Get the latest board state from the database
        latest_board_state  = await get_latest_board_from_database(current_game)

        # Extract the usernames of the white and black players from the game object
        white_player = current_game.white.username
        black_player = current_game.black.username


        white_avatar = current_game.white.avatar
        black_avatar = current_game.black.avatar

        # Fetch the list of previous boards and their associated moves from the game object
        previous_boards_and_moves = current_game.boards

        # Calculate the remaining time for each player
        white_time_left, black_time_left = get_current_time(latest_board_state.white_time_left, latest_board_state.black_time_left, latest_board_state.created_at, latest_board_state.turn)

        # Fetch the specific board requested by board_id from the database
        requested_board_data  = await get_board_from_database(board_id)

        # Convert the board JSON data to a simplified format for easier processing on the front-end
        board_json = json.loads(requested_board_data .board)
        simplified_board = pieces.boardSimplify(board_json)

        # Format the time values for display
        white_time_left, black_time_left = format_time(white_time_left, black_time_left)
        
        # Construct and send the game state message to the user
        message = construct_game_state_message(
            white_player, black_player, current_game.white_ready,
            current_game.black_ready, None, board_id, simplified_board, latest_board_state .turn,
            requested_board_data.checking, latest_board_state .total_moves, latest_board_state .soft_moves,
            white_time_left, black_time_left, requested_board_data .last_move,
            previous_boards_and_moves, True, False, False,
            white_avatar, black_avatar
            )
        await self.send_game_state_to_websocket(message)
    
    async def handle_resign(self, current_game, user):
        # Retrieve the latest board state for the current game from the database
        current_board = await get_latest_board_from_database(current_game)

        # Get the usernames of the white and black players
        white_player = current_game.white.username
        black_player = current_game.black.username

        white_avatar = current_game.white.avatar
        black_avatar = current_game.black.avatar

        # Load the current board state from JSON and simplify it
        current_board_json = json.loads(current_board.board)
        board = pieces.boardSimplify(current_board_json)

        # Calculate the remaining time for each player
        white_time_left, black_time_left = get_current_time(current_board.white_time_left, current_board.black_time_left, current_board.created_at, current_board.turn)

        # Format the time values for display
        white_time_left, black_time_left = format_time(white_time_left, black_time_left)

        # Determine the winner based on who resigned
        if user.username == white_player:
            winner = "black"
        elif user.username == black_player:
            winner = "white"
        else:
            winner = None
        
        await sync_to_async(push_winner_to_database)(current_game, winner)

        # Construct and send the game state message to the room group
        message = construct_game_state_message(
            white_player, black_player, current_game.white_ready,
            current_game.black_ready, winner, current_board.id, board, current_board.turn,
            current_board.checking, current_board.total_moves, current_board.soft_moves,
            white_time_left, black_time_left, current_board.last_move,
            current_game.boards, False, False, False,
            white_avatar, black_avatar
            )
        await self.send_game_state_to_room_group(message)

    async def handle_draw(self, current_game, user):
        # Retrieve the latest board state for the current game from the database
        current_board = await get_latest_board_from_database(current_game)

        # Get the usernames of the white and black players
        white_player = current_game.white.username
        black_player = current_game.black.username

        white_avatar = current_game.white.avatar
        black_avatar = current_game.black.avatar

        # Load the current board state from JSON and simplify it
        current_board_json = json.loads(current_board.board)
        board, _, _ = pieces.Board(current_board_json, current_board.turn, current_board.castling, current_board.enpassant).create_json_class()

        # Calculate the remaining time for each player
        white_time_left, black_time_left = get_current_time(current_board.white_time_left, current_board.black_time_left, current_board.created_at, current_board.turn)

        # Format the time values for display
        white_time_left, black_time_left = format_time(white_time_left, black_time_left)

        # No winner initially
        winner = None

        # Retrieve the current draw states for both players
        white_draw = current_game.white_draw
        black_draw = current_game.black_draw

        # Handle the draw request logic for the white player
        if user.username == white_player:
            if current_game.white_draw:  # If white has already requested a draw, cancel the request
                await push_draw_request_to_database(self.table_id, "white", False)
                white_draw = False
            else:  # Otherwise, proceed with the draw request logic
                if current_game.black_draw:  # If black has already requested a draw, declare the game a draw
                    await sync_to_async(push_winner_to_database)(current_game, "draw")
                    winner = "draw"
                else:  # If black hasn't requested, set white's draw request to True
                    await push_draw_request_to_database(self.table_id, "white", True)
                    white_draw = True

        # Handle the draw request logic for the black player            
        elif user.username == black_player:
            if current_game.black_draw:  # If black has already requested a draw, cancel the request
                await push_draw_request_to_database(self.table_id, "black", False)
                black_draw = False
            else:  # Otherwise, proceed with the draw request logic
                if current_game.white_draw:  # If white has already requested a draw, declare the game a draw
                    await sync_to_async(push_winner_to_database)(current_game, "draw")
                    winner = "draw"
                else:  # If white hasn't requested, set black's draw request to True
                    await push_draw_request_to_database(self.table_id, "black", True)
                    black_draw = True
        
        # Construct and send the game state message to the room group
        message = construct_game_state_message(
            white_player, black_player, current_game.white_ready,
            current_game.black_ready, winner, current_board.id, board, current_board.turn,
            current_board.checking, current_board.total_moves, current_board.soft_moves,
            white_time_left, black_time_left, current_board.last_move,
            current_game.boards, False, white_draw, black_draw,
            white_avatar, black_avatar
            )
        await self.send_game_state_to_room_group(message)
        
    async def handle_user_action(self, current_game, user, text_data_json):
        # Ensure a user cannot join the table if he is already in the game
        refreshed_user = await sync_to_async(User.objects.get)(id=self.scope["user"].id)
        already_in_game = bool(refreshed_user.game_id)  # True if game_id is not None or False otherwise
        if already_in_game and (text_data_json["white_player"] == True or text_data_json["black_player"] == True):
            return
        
        # Update player states in the database
        await push_players_state_to_db(current_game, user, text_data_json)
        await self.send_message_to_lobby()

        # Get player usernames or default names
        white_player = current_game.white.username if current_game.white else "Player 1"
        black_player = current_game.black.username if current_game.black else "Player 2"

        white_avatar = current_game.white.avatar if current_game.white else ""
        black_avatar = current_game.black.avatar if current_game.black else ""

        # Check if the game has started
        if if_game_started(current_game):
            # Fetch the latest board state from the database
            current_state = await get_latest_board_from_database(current_game)
            current_board_json = json.loads(current_state.board)
            board, winner, checking = pieces.Board(current_board_json, current_state.turn, current_state.castling, current_state.enpassant).create_json_class()
            turn, total_moves, soft_moves, last_move = current_state.turn, current_state.total_moves, current_state.soft_moves, current_state.last_move
            board_id = current_state.id

            # Calculate the remaining time for each player
            white_time_left, black_time_left = format_time(current_state.white_time_left, current_state.black_time_left)

            # Schedule a task to check for timeout
            check_game_timeout.apply_async((current_game.id, turn, total_moves, board), countdown=white_time_left)
            
        else:
            # Set up the initial board state if the game hasn't started
            board = pieces.boardSimplify(None)
            winner, turn, checking, total_moves, soft_moves =  None, None, None, 0, 0
            white_time_left, black_time_left, last_move = None, None, None
            board_id = None

        # Construct and send the game state message to the room group
        message = construct_game_state_message(
            white_player, black_player, current_game.white_ready,
            current_game.black_ready, winner, board_id, board, turn,
            checking, total_moves, soft_moves,
            white_time_left, black_time_left, last_move,
            [], False, current_game.white_draw, current_game.black_draw,
            white_avatar, black_avatar
            )
        await self.send_game_state_to_room_group(message)

    async def send_game_state_to_websocket(self, message):
        # Ensure that user is authenticated
        if self.scope["user"].is_authenticated:
            already_in_game = bool(self.scope["user"].game_id) # Checking game_id prevents loading the related game object from the database
        else:
            already_in_game = None
            
        # Send the game state to the WebSocket
        await self.send(text_data=json.dumps({"user": self.scope["user"].username, "already_in_game": already_in_game, **message}))
    
    async def send_game_state_to_room_group(self, message):
        # Send the game state to the room group
        await self.channel_layer.group_send(self.table_group_id, {"type": "send_new_game_state", **message})

    async def send_new_game_state(self, event):
        # Construct and send game state message from the room group event
        message = construct_game_state_message(
            event["white_player"], event["black_player"], event["white_player_ready"], 
            event["black_player_ready"], event["winner"], event["board_id"], event["board"], 
            event["turn"], event["checking"], event["total_moves"], event["soft_moves"],
            event["white_time_left"], event["black_time_left"], event["last_move"],
            event["prev_boards_id_moves"], event["play_audio"], event["white_draw"], event["black_draw"],
            event["white_avatar"], event["black_avatar"]
        )
        await self.send_game_state_to_websocket(message)
    
    async def send_message_to_lobby(self):
        # Send the game state to the LobbyConsumer
        formated_free_games = await LobbyConsumer.get_free_games_from_database()
        message = LobbyConsumer.construct_free_games_message(formated_free_games)

        channel_layer = get_channel_layer()
        await channel_layer.group_send("lobby",{'type': 'send_free_games', **message})

def construct_game_state_message(
        white_player, black_player, white_player_ready,
        black_player_ready, winner, board_id, board, turn,
        checking, total_moves, soft_moves, 
        white_time_left, black_time_left, last_move,
        prev_boards_id_moves, play_audio, white_draw, black_draw,
        white_avatar, black_avatar
    ):
    # Constructs a dictionary containing the game state
    return {
        "white_player": white_player,
        "black_player": black_player,
        "white_player_ready": white_player_ready,
        "black_player_ready": black_player_ready,
        "winner": winner,
        "board_id": board_id,
        "board": board,
        "turn": turn,
        "checking": checking,
        "total_moves": total_moves,
        "soft_moves": soft_moves,
        "white_time_left": white_time_left,
        "black_time_left": black_time_left,
        "last_move": last_move,
        "prev_boards_id_moves": prev_boards_id_moves,
        "play_audio": play_audio,
        "white_draw": white_draw,
        "black_draw": black_draw,
        "white_avatar": white_avatar,
        "black_avatar": black_avatar
    }
        
@sync_to_async
def get_game_from_database(table_id):
    # Fetch the current game instance from the database
    current_game = Game.objects.get(pk=table_id)
    # Ensuring access to players to avoid lazy loading
    _, _ = current_game.white, current_game.black
    return current_game
    
@sync_to_async
def get_latest_board_from_database(game):
    # Fetch the latest board state for the game
    current_board = Board.objects.filter(game=game).latest('id')
    current_board.turn = "white" if current_board.turn == "w" else "black"
    return current_board

@sync_to_async
def get_prev_boards_from_database(game):
    # Fetch all previous board states for the game
    prev_boards = list(Board.objects.filter(game=game))
    return prev_boards

@sync_to_async
def get_board_from_database(board_id):
    # Fetch the board instance from the database
    board = Board.objects.get(pk=board_id)
    return board
    
@sync_to_async
def push_new_board_to_database(table_id, updated_board, turn, castling, enpassant, winner, total_moves, soft_moves, white_time_left, black_time_left, last_move, moved_piece, checking):
    # Save the new board state to the database
    game = Game.objects.get(pk=table_id)

    db_turn = "w" if turn == "white" else "b"

    board = Board.objects.create(
        game = game,
        total_moves = total_moves,
        board = json.dumps(updated_board),
        turn = db_turn,
        castling = castling,
        enpassant = enpassant,
        soft_moves = soft_moves,
        white_time_left = white_time_left,
        black_time_left = black_time_left,
        last_move = last_move,
        checking = checking
    )

    push_winner_to_database(game, winner)

    game.boards.append((board.id, last_move, moved_piece))
    game.save()

    return board.id

def push_winner_to_database(game, winner):
    if winner:
        # Map the winner value to 'w' for white, 'b' for black, or 'd' for draw
        db_winner = {"white": "w", "black": "b"}.get(winner, "d")
        # Assign the mapped winner to the game's winner field
        game.winner = db_winner
        # Assign the current time to the game's finished_at field
        game.finished_at = datetime.utcnow()

        # Save the updated game state in the database
        game.save()

        # Remove the game from both players
        white = game.white # Retrieve white player (User object)
        white.game = None # Clear the game field for white player
        white.save() # Save the changes to the database

        black = game.black # Retrieve black player (User object)
        black.game = None # Clear the game field for black player
        black.save() # Save the changes to the database

@sync_to_async
def push_draw_request_to_database(table_id, player, request):
    # Save the new board state to the database
    game = Game.objects.get(pk=table_id)

    # Set the white_draw or black_draw field based on the player and request status
    game.white_draw = True if player == "white" and request else False
    game.black_draw = True if player == "black" and request else False

    # Save the updated game state in the database
    game.save()

@sync_to_async
def push_players_state_to_db(game, user, data):
    # Update player states and initialize a new board if both players are ready
    if data["white_player"] or data["black_player"]:
        # Associate the user with the current game
        user.game = game
        user.save()  # Save the updated user data

        # Add game to the User
        if data["white_player"]:
            game.white = user
        else:
            game.black = user

    # If white or black player selection is set to False (indicating a player is removed)
    elif data["white_player"] == False or data["black_player"] == False:
        # Associate the user with the current game
        user.game = None
        user.save()  # Save the updated user data

        # Remove the game from the User
        if data["white_player"] == False:
            game.white = None
        else:
            game.black = None

    # Check if white or black player is marked as ready
    elif data["white_player_ready"]:
        # If white player is ready, set their readiness to True
        game.white_ready = True
    elif data["black_player_ready"]:
        # If black player is ready, set their readiness to True
        game.black_ready = True
    elif data["white_player_ready"] == False:
        # If white player is no longer ready, set their readiness to False
        game.white_ready = False
    elif data["black_player_ready"] == False:
        # If black player is no longer ready, set their readiness to False
        game.black_ready = False

    # If both players are ready, initialize a new starting board for the game
    if game.white_ready and game.black_ready:
        # Initialize starting board
        starting_board = [
            ["R", "N", "B", "K", "Q", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "k", "q", "b", "n", "r"]
        ]
        Board.objects.create(
            game = game,
            total_moves = 0,
            board = json.dumps(starting_board),
            turn = "w",
            castling = "KQkq",
            enpassant = "__",
            soft_moves = 0,
            # white_time_left = timedelta(minutes=1),
            # black_time_left = timedelta(minutes=1)
        )
    game.save()
    
def if_game_started(game):
    # Check if both players are ready and the game has started
    return game.white_ready and game.black_ready
    
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
    
def get_current_time(white_time_left, black_time_left, created_at, turn):
    # Calculate the remaining time for each player
    if turn == "white":
        white_time_left -= datetime.now(timezone.utc) - created_at
    else:
        black_time_left -= datetime.now(timezone.utc) - created_at
    return white_time_left, black_time_left
    
def format_time(white_time_left, black_time_left):
    # Format time values to ensure compatibility with JSON serialization
    return white_time_left.total_seconds(), black_time_left.total_seconds()

def change_move_to_string(move):
    # Convert the move to a string representation
    return f"{move[0][0]}{move[0][1]}{move[1][0]}{move[1][1]}"