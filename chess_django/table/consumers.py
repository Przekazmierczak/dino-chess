import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Game, Board
from . import pieces

class TableConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.table_id = self.scope["url_route"]["kwargs"]["table_id"]
        self.table_group_id = "table_%s" % self.table_id

        # Join room group
        await self.channel_layer.group_add(self.table_group_id, self.channel_name)

        await self.accept()

        await self.check_state()
        # await self.send_actual_board()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.table_group_id, self.channel_name)


    async def check_state(self):
        actual_state, white_player, black_player,  white_player_ready, black_player_ready, actual_game, _ = await self.get_state_from_database()
        if white_player and black_player:
            await self.send_actual_board(actual_state, white_player, black_player, white_player_ready, black_player_ready, actual_game)

        else:
            await self.send_start_board(actual_state, white_player, black_player, white_player_ready, black_player_ready, actual_game)


    async def send_start_board(self, actual_state, white_player, black_player, white_player_ready, black_player_ready, actual_game):
        white_player_name = white_player.username  if white_player else "Player 1"
        black_player_name = black_player.username  if black_player else "Player 2"

        user = self.scope["user"]
        user_name = user.username

        await self.send(text_data=json.dumps({
            "user": user_name,
            "white_player": white_player_name,
            "black_player": black_player_name,
            "white_player_ready": white_player_ready,
            "black_player_ready": black_player_ready,
            "winner": None,
            "board": None,
            "turn": actual_state.turn,
            "checking": None,
            "total_moves": 0,
            "soft_moves": 0
            }))


    async def send_actual_board(self, actual_state, white_player, black_player, white_player_ready, black_player_ready, actual_game):
        actual_board_json = json.loads(actual_state.board)
        actual_board_object, winner, checking = pieces.Board(actual_board_json, actual_state.turn, actual_state.castling, actual_state.enpassant).create_json_class()
        
        white_player_name = white_player.username  if white_player else "Player 1"
        black_player_name = black_player.username  if black_player else "Player 2"

        # ------------- CHANGE IT IN FUTURE (DON'T CALL THE BOARD CLASS IF THERE IS A WINNER!) ----------------
        if actual_game.winner:
            winner = {"w": "white", "b": "black"}.get(actual_game.winner, "draw") 
        # ----------------------------------------------------------------------------------------
        
        user = self.scope["user"]
        user_name = user.username

        await self.send(text_data=json.dumps({
            "user": user_name,
            "white_player": white_player_name,
            "black_player": black_player_name,
            "white_player_ready": white_player_ready,
            "black_player_ready": black_player_ready,
            "winner": winner,
            "board": actual_board_object,
            "turn": actual_state.turn,
            "checking": checking,
            "total_moves": actual_state.total_moves,
            "soft_moves": actual_state.soft_moves
            }))


    @sync_to_async
    def get_state_from_database(self):
        actual_game_db = Game.objects.get(pk=self.table_id)
        white_player = actual_game_db.white
        black_player = actual_game_db.black
        white_player_ready = actual_game_db.white_ready
        black_player_ready = actual_game_db.black_ready
        # if actual_game_db.started:
        actual_board_db = Board.objects.filter(game=actual_game_db).latest('id')
        prev_boards_db = Board.objects.filter(game=actual_game_db)

        prev_boards = list(prev_boards_db)

        actual_board_db.turn = "white" if actual_board_db.turn == "w" else "black"
        # else:
        #     actual_board_db = None
        #     prev_boards = None
        
        return actual_board_db, white_player, black_player, white_player_ready, black_player_ready, actual_game_db, prev_boards
    
    @sync_to_async
    def push_new_board_to_database(self, updated_board, turn, castling, enpassant, winner, total_moves, self_moves):
        game = Game.objects.get(pk=self.table_id)
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
            soft_moves = self_moves
        )

    @sync_to_async
    def push_player_to_database(self, user, player):
        game = Game.objects.get(pk=self.table_id)
        if player == "w": game.white = user
        elif player == "b": game.black = user
        game.save()

    @sync_to_async
    def push_player_ready_to_database(self, user, player):
        game = Game.objects.get(pk=self.table_id)
        if player == "w":
            game.white_ready = True
            if game.black_ready:
                game.started = True
        elif player == "b":
            game.black_ready = True
            if game.white_ready:
                game.started = True
        game.save()

    @sync_to_async
    def remove_player_from_database(self, user, player):
        game = Game.objects.get(pk=self.table_id)
        if player == "w": game.white = None
        elif player == "b": game.black = None
        game.save()

    @sync_to_async
    def remove_player_ready_from_database(self, user, player):
        game = Game.objects.get(pk=self.table_id)
        if player == "w": game.white_ready = False
        elif player == "b": game.black_ready = False
        game.save()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if (text_data_json["white_player"] or text_data_json["black_player"] or text_data_json["white_player"] == False or text_data_json["black_player"] == False
            or text_data_json["white_player_ready"] or text_data_json["black_player_ready"] or text_data_json["white_player_ready"] == False or text_data_json["black_player_ready"] == False):
            self.user = self.scope["user"]

            if text_data_json["white_player"]:
                await self.push_player_to_database(self.user, "w")
            if text_data_json["black_player"]:
                await self.push_player_to_database(self.user, "b")
            if text_data_json["white_player"] == False:
                await self.remove_player_from_database(self.user, "w")
            if text_data_json["black_player"] == False:
                await self.remove_player_from_database(self.user, "b")
            if text_data_json["white_player_ready"]:
                await self.push_player_ready_to_database(self.user, "w")
            if text_data_json["black_player_ready"]:
                await self.push_player_ready_to_database(self.user, "b")
            if text_data_json["white_player_ready"] == False:
                await self.remove_player_ready_from_database(self.user, "w")
            if text_data_json["black_player_ready"] == False:
                await self.remove_player_ready_from_database(self.user, "b")
                
            # CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! 
            actual_state, white_player, black_player, white_player_ready, black_player_ready, actual_game, _ = await self.get_state_from_database()
            # if actual_state:
            actual_board_json = json.loads(actual_state.board)
            actual_board_object, winner, checking = pieces.Board(actual_board_json, actual_state.turn, actual_state.castling, actual_state.enpassant).create_json_class()

            white_player_name = white_player.username  if white_player else "Player 1"
            black_player_name = black_player.username  if black_player else "Player 2"

            # Send message to room group
            await self.channel_layer.group_send(
                self.table_group_id, {
                    "type": "new_board",
                    "white_player": white_player_name,
                    "black_player": black_player_name,
                    "white_player_ready": white_player_ready,
                    "black_player_ready": black_player_ready,
                    "winner": None,
                    "board": actual_board_object,
                    "turn": actual_state.turn,
                    "checking": checking,
                    "total_moves": actual_state.total_moves,
                    "soft_moves": actual_state.soft_moves
                    }
            )
            # CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! CHANGE IT! 
        else:
            move = text_data_json["move"]
            promotion = text_data_json["promotion"]

            prev_state, white_player, black_player, white_player_ready, black_player_ready, game, prev_boards = await self.get_state_from_database()
            prev_board = json.loads(prev_state.board)

            white_player_name = white_player.username  if white_player else "Player 1"
            black_player_name = black_player.username  if black_player else "Player 2"

            next_board, next_castling, next_enpassant, soft_move = pieces.Board(prev_board, prev_state.turn, prev_state.castling, prev_state.enpassant).create_new_json_board(move, promotion)
            next_turn = "black" if prev_state.turn == "white" else "white"
            next_total_moves = prev_state.total_moves + 1 if next_turn == "white" else prev_state.total_moves
            next_soft_moves = prev_state.soft_moves + 1 if soft_move else 0

            if next_board:
                updated_json_board, winner, checking = pieces.Board(next_board, next_turn, next_castling, next_enpassant).create_json_class()

                # Threefold repetition
                repetition = 1
                next_turn_short = "w" if next_turn == "white" else "b"
                for prev_board in prev_boards:
                    if (prev_board.board, prev_board.turn, prev_board.castling, prev_board.enpassant) == (json.dumps(next_board), next_turn_short, next_castling, next_enpassant):
                        repetition += 1
                    if repetition >= 3:
                        winner = "draw"
                        break

                # 50 move rule
                if next_soft_moves == 100:
                    winner = "draw"
                await self.push_new_board_to_database(next_board, next_turn, next_castling, next_enpassant, winner, next_total_moves, next_soft_moves)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.table_group_id, {
                        "type": "new_board",
                        "white_player": white_player_name,
                        "black_player": black_player_name,
                        "white_player_ready": white_player_ready,
                        "black_player_ready": black_player_ready,
                        "winner": winner,
                        "board": updated_json_board,
                        "turn": next_turn,
                        "checking": checking,
                        "total_moves": next_total_moves,
                        "soft_moves": next_soft_moves
                        }
                )

    # Receive message from room group
    async def new_board(self, event):
        user = self.scope["user"]
        user_name = user.username

        white_player = event["white_player"]
        black_player = event["black_player"]
        white_player_ready = event["white_player_ready"]
        black_player_ready = event["black_player_ready"]
        winner = event["winner"]
        board = event["board"]
        turn = event["turn"]
        checking = event["checking"]
        total_moves = event["total_moves"]
        soft_moves = event["soft_moves"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "user": user_name,
            "white_player": white_player,
            "black_player": black_player,
            "white_player_ready": white_player_ready,
            "black_player_ready": black_player_ready,
            "winner": winner,
            "board": board,
            "turn": turn,
            "checking": checking,
            "total_moves": total_moves,
            "soft_moves": soft_moves
            }))