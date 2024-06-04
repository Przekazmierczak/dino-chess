from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, SimpleTestCase, TestCase
from django.conf import settings
from chess_django.asgi import application

from .models import Game, Board
from asgiref.sync import sync_to_async

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from .consumers import TableConsumer
from django.contrib.auth.models import AnonymousUser

from . import pieces


class ChannelLayerSettingsTest(TestCase):
    def test_channel_layers_for_testing(self):
        self.assertEqual(
            settings.CHANNEL_LAYERS['default']['BACKEND'],
            "channels.layers.InMemoryChannelLayer"
        )

# class WebSocketTests(TransactionTestCase):
#     async def test_websocket_connect(self):
#         new_game = await sync_to_async(Game.objects.create)()

#         communicator = WebsocketCommunicator(application, f"/ws/table/{new_game.id}/")
#         connected, subprotocol = await communicator.connect()
#         self.assertTrue(connected)

#         await communicator.disconnect()

class TableConsumerTestCase(TestCase):

    async def setup_consumer(self, mock_game):
        """
        Set up the TableConsumer instance with mock data and return the consumer and mock board.
        """
        # Create an instance of your consumer
        consumer = TableConsumer()
        
        # Mock the scope with a user and other necessary attributes
        consumer.scope = {
            "type": "websocket",
            "url_route": {"kwargs": {"table_id": 1}},
            "user": MagicMock(username="test_user")
        }
        consumer.channel_layer = MagicMock()
        consumer.channel_name = "test_channel"

        # Mock the board state
        mock_board = MagicMock()
        mock_board.total_moves = 0
        mock_board.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                       ["P", "P", "P", "P", "P", "P", "P", "P"],
                                       [None, None, None, None, None, None, None, None],
                                       [None, None, None, None, None, None, None, None],
                                       [None, None, None, None, None, None, None, None],
                                       [None, None, None, None, None, None, None, None],
                                       ["p", "p", "p", "p", "p", "p", "p", "p"],
                                       ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board.turn = "white"
        mock_board.castling = "KQkq"
        mock_board.enpassant = "__"
        mock_board.soft_moves = 0

        # Mock async methods
        consumer.get_game_from_database = AsyncMock(return_value=mock_game)
        consumer.get_latest_board_from_database = AsyncMock(return_value=mock_board)
        consumer.send_game_state_to_websocket = AsyncMock()

        return consumer, mock_board
    
    @pytest.mark.asyncio
    async def test_send_current_state_users_turn(self):
        """
        Test the state sent to the user when it is their turn.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="test_user")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = "w"

        # Setup consumer
        consumer, mock_board = await self.setup_consumer(mock_game)
        
        # Patch dependencies
        with patch('table.pieces.Board') as MockBoard:
            MockBoard.return_value.create_json_class.return_value = (mock_board.board, None, None)
            
            # Call the method
            await consumer.send_current_state()

            # Verify interactions and state
            consumer.get_game_from_database.assert_called_once()
            consumer.get_latest_board_from_database.assert_called_once_with(mock_game)
            consumer.send_game_state_to_websocket.assert_called_once()

            # Verify the message sent to WebSocket
            message = consumer.send_game_state_to_websocket.call_args[0][0]
            assert message['white_player'] == 'test_user'
            assert message['black_player'] == 'black_player'
            assert message['white_player_ready'] == True
            assert message['black_player_ready'] == True
            assert message['winner'] == 'white'
            assert message['board'] is not None
            assert message['turn'] == 'white'
            assert message['checking'] == None
            assert message['total_moves'] == 0
            assert message['soft_moves'] == 0

    @pytest.mark.asyncio
    async def test_send_current_state_another_users_turn(self):
        """
        Test the state sent to the user when it is another user's turn.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="white_player")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = None

        # Setup consumer
        consumer, mock_board = await self.setup_consumer(mock_game)
        
        # Patch dependencies
        with patch('table.pieces.boardSimplify') as MockBoardSimplify:
            MockBoardSimplify.return_value = mock_board.board
            
            # Call the method
            await consumer.send_current_state()

            # Verify interactions and state
            consumer.get_game_from_database.assert_called_once()
            consumer.send_game_state_to_websocket.assert_called_once()

            # Verify the message sent to WebSocket
            message = consumer.send_game_state_to_websocket.call_args[0][0]
            assert message['white_player'] == 'white_player'
            assert message['black_player'] == 'black_player'
            assert message['white_player_ready'] == True
            assert message['black_player_ready'] == True
            assert message['winner'] == None
            assert message['board'] is not None
            assert message['turn'] == 'white'
            assert message['checking'] == None
            assert message['total_moves'] == 0
            assert message['soft_moves'] == 0

    @pytest.mark.asyncio
    async def test_send_current_state_game_not_started(self):
        """
        Test the state sent to the user when the game has not started.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = None
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = False
        mock_game.black_ready = True
        mock_game.winner = None

        # Setup consumer
        consumer, mock_board = await self.setup_consumer(mock_game)
        
        # Patch dependencies
        with patch('table.pieces.boardSimplify') as MockBoardSimplify:
            MockBoardSimplify.return_value = mock_board.board
            
            # Call the method
            await consumer.send_current_state()

            # Verify interactions and state
            consumer.get_game_from_database.assert_called_once()
            consumer.send_game_state_to_websocket.assert_called_once()

            # Verify the message sent to WebSocket
            message = consumer.send_game_state_to_websocket.call_args[0][0]
            assert message['white_player'] == 'Player 1'
            assert message['black_player'] == 'black_player'
            assert message['white_player_ready'] == False
            assert message['black_player_ready'] == True
            assert message['winner'] == None
            assert message['board'] is not None
            assert message['turn'] == None
            assert message['checking'] == None
            assert message['total_moves'] == 0
            assert message['soft_moves'] == 0


class TableConsumerTestCase(TestCase):

    async def setup_consumer(self):
        """
        Set up the TableConsumer instance with mock data and return the consumer and mock board.
        """
        # Create an instance of your consumer
        consumer = TableConsumer()
        
        # Mock the scope with a user and other necessary attributes
        consumer.scope = {
            "type": "websocket",
            "url_route": {"kwargs": {"table_id": 1}},
            "user": MagicMock(username="test_user")
        }
        consumer.channel_layer = MagicMock()
        consumer.channel_name = "test_channel"

        # Mock game state
        mock_game = MagicMock()
        mock_game.white = None
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = False
        mock_game.black_ready = True
        mock_game.winner = None

        # Mock async methods
        consumer.get_game_from_database = AsyncMock(return_value=mock_game)
        consumer.handle_move = AsyncMock()
        consumer.handle_user_action = AsyncMock()

        return consumer
    
    @pytest.mark.asyncio
    async def test_receive_handle_move(self):
        """
        Test the receive method handling a move.        
        """
        mock_text_data = {'white_player': None,
                          'black_player': None,
                          'white_player_ready': None,
                          'black_player_ready': None,
                          'move': [[1, 1], [2, 2]],
                          'promotion': None}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()
        
        # Call the method
        await consumer.receive(mock_text_data_json)

        # Verify interactions and state
        consumer.get_game_from_database.assert_called_once()
        consumer.handle_move.assert_called_once_with(
            consumer.get_game_from_database.return_value,
            consumer.scope["user"],
            mock_text_data["move"],
            mock_text_data["promotion"]
        )

    @pytest.mark.asyncio
    async def test_receive_handle_user_action(self):
        """
        Test the receive method handling a user action when there is no move.
        """
        mock_text_data = {'white_player': 'white_player',
                          'black_player': 'black_player',
                          'white_player_ready': None,
                          'black_player_ready': None,
                          'move': None,
                          'promotion': None}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()
        
        # Call the method
        await consumer.receive(mock_text_data_json)

        # Verify interactions and state
        consumer.get_game_from_database.assert_called_once()
        consumer.handle_user_action.assert_called_once_with(
            consumer.get_game_from_database.return_value,
            consumer.scope["user"],
            mock_text_data
        )