import json
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Game, Board
from . import pieces

class TableConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.table_id = self.scope["url_route"]["kwargs"]["table_id"]
        self.table_group_id = "table_%s" % self.table_id

        # Join room group
        await self.channel_layer.group_add(self.table_group_id, self.channel_name)

        await self.accept()

        # Push actual board
        actual_board_object = pieces.create_board(board)
        await self.channel_layer.group_send(
            self.table_group_id, {"type": "new_board", "board": actual_board_object}
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.table_group_id, self.channel_name)

    async def get_board_state_from_database(self):
        actual_game_db = await Game.objects.get(pk=self.table_id)
        actual_board_db = await Board.objects.get(game=actual_game_db)
        print(actual_board_db)
        return actual_board_db



    # # Receive message from WebSocket
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json["message"]

    #     # Send message to room group
    #     await self.channel_layer.group_send(
    #         self.table_group_id, {"type": "new_board", "message": message}
    #     )

    # Receive message from room group
    async def new_board(self, event):
        board = event["board"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"board": board}))

board = [["R", "N", "B", "K", "Q", "B", "N", "R"],
         ["P", "P", "P", "P", "P", "P", "P", "P"],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         ["p", "p", "p", "p", "p", "p", "p", "p"],
         ["r", "n", "b", "k", "q", "b", "n", "r"]]