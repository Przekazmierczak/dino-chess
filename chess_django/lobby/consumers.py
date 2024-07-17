import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Q

from table.models import Game

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_group = "lobby"

        await self.channel_layer.group_add(self.lobby_group, self.channel_name)
        await self.accept()

        await self.send_current_state()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.lobby_group, self.channel_name)

    async def send_current_state(self):
        formated_free_games = await self.get_free_games_from_database()

        message = self.construct_free_games_message(formated_free_games)
        await self.send_free_games_to_websocket(message)

    def construct_free_games_message(self, free_games):
        # Constructs a dictionary containing the game state
        return {
            "free_games": free_games,
        }
    
    async def send_free_games_to_websocket(self, message):
        # Send the game state to the WebSocket
        await self.send(text_data=json.dumps({**message}))

    @sync_to_async
    def get_free_games_from_database(self):
        free_games = list(Game.objects.filter(Q(white_ready=False) | Q(black_ready=False)).order_by('-id')[:10])

        formated_free_games = []
        for free_game in free_games:
            white_player = free_game.white.username if free_game.white else None
            black_player = free_game.black.username if free_game.black else None
            formated_free_games.append((free_game.id, white_player, black_player, free_game.white_ready, free_game.black_ready))

        return formated_free_games
    
    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #     self.send(text_data=json.dumps({
    #         'message': message
    #     }))