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

        await self.send_actual_board()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.table_group_id, self.channel_name)


    async def send_actual_board(self):
        actual_state, actual_game, _ = await self.get_state_from_database()
        actual_board_json = json.loads(actual_state.board)
        actual_board_object, winner, checking = pieces.Board(actual_board_json, actual_state.turn, actual_state.castling, actual_state.enpassant).create_json_class()

        # ------------- CHANGE IT IN FUTURE (DON'T CALL THE BOARD CLASS IF THERE IS A WINNER!) ----------------
        if actual_game.winner:
            winner = {"w": "white", "b": "black"}.get(actual_game.winner, "draw")
        # ----------------------------------------------------------------------------------------
            
        await self.send(text_data=json.dumps({
            "board": actual_board_object,
            "turn": actual_state.turn,
            "winner": winner,
            "checking": checking,
            "total_moves": actual_state.total_moves,
            "soft_moves": actual_state.soft_moves
            }))


    @sync_to_async
    def get_state_from_database(self):
        actual_game_db = Game.objects.get(pk=self.table_id)
        actual_board_db = Board.objects.filter(game=actual_game_db).latest('id')
        prev_boards_db = Board.objects.filter(game=actual_game_db)

        prev_boards = list(prev_boards_db)

        actual_board_db.turn = "white" if actual_board_db.turn == "w" else "black"
        
        return actual_board_db, actual_game_db, prev_boards
    
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


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        move = text_data_json["move"]
        promotion = text_data_json["promotion"]

        prev_state, _, prev_boards = await self.get_state_from_database()
        prev_board = json.loads(prev_state.board)

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
                self.table_group_id, {"type": "new_board", "board": updated_json_board, "turn": next_turn, "winner": winner, "checking": checking, "total_moves": next_total_moves, "soft_moves": next_soft_moves}
            )

    # Receive message from room group
    async def new_board(self, event):
        board = event["board"]
        turn = event["turn"]
        winner = event["winner"]
        checking = event["checking"]
        total_moves = event["total_moves"]
        soft_moves = event["soft_moves"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "board": board,
            "turn": turn,
            "winner": winner,
            "checking": checking,
            "total_moves": total_moves,
            "soft_moves": soft_moves
            }))