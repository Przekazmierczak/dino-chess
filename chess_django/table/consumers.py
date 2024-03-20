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
        actual_turn = actual_state.turn
        actual_board_object = pieces.Board(actual_board_json, actual_turn).create_json_class()
        await self.send(text_data=json.dumps({
            "board": actual_board_object,
            "turn": actual_turn
            }))


    @sync_to_async
    def get_state_from_database(self):
        actual_game_db = Game.objects.get(pk=self.table_id)
        actual_board_db = Board.objects.filter(game=actual_game_db).latest('id')
        return actual_board_db
    
    @sync_to_async
    def push_new_board_to_database(self, updated_board, turn):
        game = Game.objects.get(pk=self.table_id)

        Board.objects.create(
            game = game,
            total_moves = 0,
            board = json.dumps(updated_board),
            turn = turn,
            castling = "----", # "kqKQ"
            soft_moves = 0
        )


    # # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        move = text_data_json["move"]

        prev_state = await self.get_state_from_database()
        prev_board = json.loads(prev_state.board)

        prev_turn = prev_state.turn
        next_turn = "black" if prev_turn == "white" else "white"

        updated_board, correct = pieces.Board(prev_board, prev_turn).create_new_json_board(move)

        if correct:
            await self.push_new_board_to_database(updated_board, next_turn)

            updated_json_board = pieces.Board(updated_board, next_turn).create_json_class()

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