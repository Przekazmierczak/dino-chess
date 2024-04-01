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
        actual_state = await self.get_state_from_database()
        actual_board_json = json.loads(actual_state.board)
        actual_board_object = pieces.Board(actual_board_json, actual_state.turn, actual_state.castling, actual_state.enpassant).create_json_class()
        await self.send(text_data=json.dumps({
            "board": actual_board_object,
            "turn": actual_state.turn
            }))


    @sync_to_async
    def get_state_from_database(self):
        actual_game_db = Game.objects.get(pk=self.table_id)
        actual_board_db = Board.objects.filter(game=actual_game_db).latest('id')
        return actual_board_db
    
    @sync_to_async
    def push_new_board_to_database(self, updated_board, turn, enpassant):
        game = Game.objects.get(pk=self.table_id)

        Board.objects.create(
            game = game,
            total_moves = 0,
            board = json.dumps(updated_board),
            turn = turn,
            castling = "kqKQ",
            enpassant = enpassant,
            soft_moves = 0
        )


    # # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        move = text_data_json["move"]

        prev_state = await self.get_state_from_database()
        prev_board = json.loads(prev_state.board)

        next_board, next_enpassant = pieces.Board(prev_board, prev_state.turn, prev_state.castling, prev_state.enpassant).create_new_json_board(move)
        next_turn = "black" if prev_state.turn == "white" else "white"
        next_total_moves = prev_state.total_moves + 1
        next_soft_moves = prev_state.soft_moves + 1

        if next_board:
            await self.push_new_board_to_database(next_board, next_turn, next_enpassant)
            # CHANGE PREV TO NEXT STATE!
            updated_json_board = pieces.Board(next_board, next_turn, prev_state.castling, next_enpassant).create_json_class()

            # Send message to room group
            await self.channel_layer.group_send(
                self.table_group_id, {"type": "new_board", "board": updated_json_board, "turn": next_turn}
            )

    # Receive message from room group
    async def new_board(self, event):
        board = event["board"]
        turn = event["turn"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "board": board,
            "turn": turn
            }))