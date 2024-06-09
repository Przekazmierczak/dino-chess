from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, SimpleTestCase, TestCase
from django.conf import settings
from chess_django.asgi import application

from .models import Game, Board
from menu.models import User
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

class TableConsumerTestCase1(TestCase):

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


class TableConsumerTestCase2(TestCase):

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

class TableConsumerTestCase3(TestCase):

    async def setup_consumer(self, mock_state, mock_boards, treefold):
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

        # Mock async methods
        consumer.get_latest_board_from_database = AsyncMock(return_value=mock_state)
        consumer.get_prev_boards_from_database = AsyncMock(return_value=mock_boards)
        consumer.is_threefold_repetition = MagicMock(return_value=treefold)
        consumer.push_new_board_to_database = AsyncMock()
        consumer.send_game_state_to_room_group = AsyncMock()

        return consumer
    
    @pytest.mark.asyncio
    async def test_handle_valid_move(self):
        """
        Test handle_move to ensure it processes a move correctly and updates the game state.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="test_user")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = None

        # Mock the previous board state before the move
        mock_board_prev = MagicMock()
        mock_board_prev.total_moves = 0
        mock_board_prev.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            ["P", "P", "P", "P", "P", "P", "P", "P"],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_prev.turn = "white"
        mock_board_prev.castling = "KQkq"
        mock_board_prev.enpassant = "__"
        mock_board_prev.soft_moves = 0

        # Mock the next board state after the move
        mock_board_next = MagicMock()
        mock_board_next.total_moves = 0
        mock_board_next.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            [None, "P", "P", "P", "P", "P", "P", "P"],
                                            ["P", None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_next.turn = "black"
        mock_board_next.castling = "KQkq"
        mock_board_next.enpassant = "__"
        mock_board_next.soft_moves = 1
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None

        # Patch the Board class to control its behavior in the test
        with patch('table.pieces.Board') as MockBoard:
            MockBoard.return_value.create_new_json_board.return_value = (mock_board_next.board, None, None, True)
            MockBoard.return_value.create_json_class.return_value = ("correct_class", None, None)

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            consumer.get_latest_board_from_database.assert_called_once()
            consumer.get_prev_boards_from_database.assert_called_once()
            consumer.push_new_board_to_database.assert_called_once_with(
                mock_board_next.board,
                mock_board_next.turn,
                None,
                None,
                None,
                mock_board_next.total_moves,
                mock_board_next.soft_moves,
            )
        
            # Verify the message sent to WebSocket room group
            message = consumer.send_game_state_to_room_group.call_args[0][0]
            assert message['white_player'] == 'test_user'
            assert message['black_player'] == 'black_player'
            assert message['white_player_ready'] == mock_game.white_ready
            assert message['black_player_ready'] == mock_game.black_ready
            assert message['winner'] == None
            assert message['board'] is not None
            assert message['turn'] == mock_board_next.turn
            assert message['checking'] == None
            assert message['total_moves'] == mock_board_next.total_moves
            assert message['soft_moves'] == mock_board_next.soft_moves

    @pytest.mark.asyncio
    async def test_handle_threefold_move(self):
        """
        Test handle_move to ensure it processes a move correctly and updates the game state.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="test_user")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = None

        # Mock the previous board state before the move
        mock_board_prev = MagicMock()
        mock_board_prev.total_moves = 0
        mock_board_prev.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            ["P", "P", "P", "P", "P", "P", "P", "P"],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_prev.turn = "white"
        mock_board_prev.castling = "KQkq"
        mock_board_prev.enpassant = "__"
        mock_board_prev.soft_moves = 0

        # Mock the next board state after the move
        mock_board_next = MagicMock()
        mock_board_next.total_moves = 0
        mock_board_next.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            [None, "P", "P", "P", "P", "P", "P", "P"],
                                            ["P", None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_next.turn = "black"
        mock_board_next.castling = "KQkq"
        mock_board_next.enpassant = "__"
        mock_board_next.soft_moves = 1
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None

        # Patch the Board class to control its behavior in the test
        with patch('table.pieces.Board') as MockBoard:
            MockBoard.return_value.create_new_json_board.return_value = (mock_board_next.board, None, None, True)
            MockBoard.return_value.create_json_class.return_value = ("correct_class", None, None)

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], True)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            consumer.get_latest_board_from_database.assert_called_once()
            consumer.get_prev_boards_from_database.assert_called_once()
            consumer.push_new_board_to_database.assert_called_once_with(
                mock_board_next.board,
                mock_board_next.turn,
                None,
                None,
                'draw',
                mock_board_next.total_moves,
                mock_board_next.soft_moves,
            )
        
            # Verify the message sent to WebSocket room group
            message = consumer.send_game_state_to_room_group.call_args[0][0]
            assert message['white_player'] == 'test_user'
            assert message['black_player'] == 'black_player'
            assert message['white_player_ready'] == mock_game.white_ready
            assert message['black_player_ready'] == mock_game.black_ready
            assert message['winner'] == 'draw'
            assert message['board'] is not None
            assert message['turn'] == mock_board_next.turn
            assert message['checking'] == None
            assert message['total_moves'] == mock_board_next.total_moves
            assert message['soft_moves'] == mock_board_next.soft_moves
    
    @pytest.mark.asyncio
    async def test_handle_50rule_move(self):
        """
        Test handle_move to ensure it processes a move correctly and updates the game state.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="test_user")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = None

        # Mock the previous board state before the move
        mock_board_prev = MagicMock()
        mock_board_prev.total_moves = 0
        mock_board_prev.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            ["P", "P", "P", "P", "P", "P", "P", "P"],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_prev.turn = "white"
        mock_board_prev.castling = "KQkq"
        mock_board_prev.enpassant = "__"
        mock_board_prev.soft_moves = 99

        # Mock the next board state after the move
        mock_board_next = MagicMock()
        mock_board_next.total_moves = 0
        mock_board_next.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            [None, "P", "P", "P", "P", "P", "P", "P"],
                                            ["P", None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_next.turn = "black"
        mock_board_next.castling = "KQkq"
        mock_board_next.enpassant = "__"
        mock_board_next.soft_moves = 100
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None

        # Patch the Board class to control its behavior in the test
        with patch('table.pieces.Board') as MockBoard:
            MockBoard.return_value.create_new_json_board.return_value = (mock_board_next.board, None, None, True)
            MockBoard.return_value.create_json_class.return_value = ("correct_class", None, None)

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            consumer.get_latest_board_from_database.assert_called_once()
            consumer.get_prev_boards_from_database.assert_called_once()
            consumer.push_new_board_to_database.assert_called_once_with(
                mock_board_next.board,
                mock_board_next.turn,
                None,
                None,
                'draw',
                mock_board_next.total_moves,
                mock_board_next.soft_moves,
            )
        
            # Verify the message sent to WebSocket room group
            message = consumer.send_game_state_to_room_group.call_args[0][0]
            assert message['white_player'] == 'test_user'
            assert message['black_player'] == 'black_player'
            assert message['white_player_ready'] == mock_game.white_ready
            assert message['black_player_ready'] == mock_game.black_ready
            assert message['winner'] == 'draw'
            assert message['board'] is not None
            assert message['turn'] == mock_board_next.turn
            assert message['checking'] == None
            assert message['total_moves'] == mock_board_next.total_moves
            assert message['soft_moves'] == mock_board_next.soft_moves
    
    @pytest.mark.asyncio
    async def test_handle_invalid_move(self):
        """
        Test handle_move to ensure it processes a move correctly and updates the game state.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="test_user")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = None

        # Mock the previous board state before the move
        mock_board_prev = MagicMock()
        mock_board_prev.total_moves = 0
        mock_board_prev.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            ["P", "P", "P", "P", "P", "P", "P", "P"],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_prev.turn = "white"
        mock_board_prev.castling = "KQkq"
        mock_board_prev.enpassant = "__"
        mock_board_prev.soft_moves = 0

        # Mock the next board state after the move
        mock_board_next = MagicMock()
        mock_board_next.total_moves = 0
        mock_board_next.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            [None, "P", "P", "P", "P", "P", "P", "P"],
                                            ["P", None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_next.turn = "black"
        mock_board_next.castling = "KQkq"
        mock_board_next.enpassant = "__"
        mock_board_next.soft_moves = 1
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None

        # Patch the Board class to control its behavior in the test
        with patch('table.pieces.Board') as MockBoard:
            MockBoard.return_value.create_new_json_board.return_value = (None, None, None, True)

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            consumer.get_latest_board_from_database.assert_called_once()
            consumer.get_prev_boards_from_database.assert_called_once()
            consumer.push_new_board_to_database.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_wrong_player_move(self):
        """
        Test handle_move to ensure it processes a move correctly and updates the game state.
        """
        # Mock game state
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="white_player")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = None

        # Mock the previous board state before the move
        mock_board_prev = MagicMock()
        mock_board_prev.total_moves = 0
        mock_board_prev.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            ["P", "P", "P", "P", "P", "P", "P", "P"],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_prev.turn = "white"
        mock_board_prev.castling = "KQkq"
        mock_board_prev.enpassant = "__"
        mock_board_prev.soft_moves = 0

        # Mock the next board state after the move
        mock_board_next = MagicMock()
        mock_board_next.total_moves = 0
        mock_board_next.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            [None, "P", "P", "P", "P", "P", "P", "P"],
                                            ["P", None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_board_next.turn = "black"
        mock_board_next.castling = "KQkq"
        mock_board_next.enpassant = "__"
        mock_board_next.soft_moves = 1
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None

        # Patch the Board class to control its behavior in the test
        with patch('table.pieces.Board') as MockBoard:
            MockBoard.return_value.create_new_json_board.return_value = (mock_board_next.board, None, None, True)

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            consumer.get_latest_board_from_database.assert_called_once()
            consumer.get_prev_boards_from_database.assert_called_once()
            consumer.push_new_board_to_database.assert_not_called()

class TableConsumerTestCase4(TestCase):

    async def setup_consumer(self, started):
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

        # Create a mock board representing the initial state of the game
        mock_start_board = MagicMock()
        mock_start_board.total_moves = 0
        mock_start_board.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                            ["P", "P", "P", "P", "P", "P", "P", "P"],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            [None, None, None, None, None, None, None, None],
                                            ["p", "p", "p", "p", "p", "p", "p", "p"],
                                            ["r", "n", "b", "k", "q", "b", "n", "r"]])
        mock_start_board.turn = "white"
        mock_start_board.castling = "KQkq"
        mock_start_board.enpassant = "__"
        mock_start_board.soft_moves = 0

        # Mock async methods that will be called during the tests
        consumer.push_players_state_to_db = AsyncMock()
        consumer.if_game_started = MagicMock(return_value=started)
        consumer.get_latest_board_from_database = AsyncMock(return_value=mock_start_board)
        consumer.send_game_state_to_room_group = AsyncMock()

        return consumer
    
    @pytest.mark.asyncio
    async def test_handle_user_action_when_both_players_ready(self):
        """
        Test handle_user_action to ensure it processes correctly and updates the game state.
        """
        # Mock game state with both players ready and no winner
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="test_user")
        mock_game.black = MagicMock(username="black_player")
        mock_game.white_ready = True
        mock_game.black_ready = True
        mock_game.winner = None
        
        # Mock the input data that would be received from the WebSocket
        mock_text_data = {'white_player': None,
                          'black_player': None,
                          'white_player_ready': True,
                          'black_player_ready': None,
                          'move': None,
                          'promotion': None}
        mock_text_data_json = json.dumps(mock_text_data)     

        # Patch the Board class to control its behavior in the test
        with patch('table.pieces.Board') as MockBoard:
            MockBoard.return_value.create_json_class.return_value = ("correct_class", None, None)

            # Setup consumers
            consumer = await self.setup_consumer(True)
            
            # Call the handle_user_action method
            await consumer.handle_user_action(mock_game, consumer.scope["user"], mock_text_data_json)

            # Assert that the database method to update player state was called correctly
            consumer.push_players_state_to_db.assert_called_once_with(
                mock_game,
                consumer.scope["user"],
                mock_text_data_json,
            )
        
            # Verify the message sent to the WebSocket room group
            message = consumer.send_game_state_to_room_group.call_args[0][0]
            assert message['white_player'] == 'test_user'
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
    async def test_handle_user_action_when_player_missing(self):
        """
        Test handle_user_action to ensure it processes correctly and updates the game state.
        """
        # Mock game state with only one player ready and no winner
        mock_game = MagicMock()
        mock_game.white = MagicMock(username="test_user")
        mock_game.black = None
        mock_game.white_ready = True
        mock_game.black_ready = False
        mock_game.winner = None
        
        # Mock the input data that would be received from the WebSocket
        mock_text_data = {'white_player': None,
                          'black_player': None,
                          'white_player_ready': True,
                          'black_player_ready': None,
                          'move': None,
                          'promotion': None}
        mock_text_data_json = json.dumps(mock_text_data)     

        # Patch the BoardSimplify class to control its behavior in the test
        with patch('table.pieces.boardSimplify') as MockBoardSimplify:
            MockBoardSimplify.return_value = "correct_class"

            # Setup consumers
            consumer = await self.setup_consumer(False)
            
            # Call the handle_user_action method
            await consumer.handle_user_action(mock_game, consumer.scope["user"], mock_text_data_json)

            # Assert that the database method to update player state was called correctly
            consumer.push_players_state_to_db.assert_called_once_with(
                mock_game,
                consumer.scope["user"],
                mock_text_data_json,
            )
        
            # Verify the message sent to WebSocket room group
            message = consumer.send_game_state_to_room_group.call_args[0][0]
            assert message['white_player'] == 'test_user'
            assert message['black_player'] == 'Player 2'
            assert message['white_player_ready'] == True
            assert message['black_player_ready'] == False
            assert message['winner'] == None
            assert message['board'] is not None
            assert message['turn'] == None
            assert message['checking'] == None
            assert message['total_moves'] == 0
            assert message['soft_moves'] == 0

class TableConsumerTestCase5(TestCase):

    def test_construct_game_state_message(self):
        """
        Test construct_game_state_message to ensure it returns the correct dictionary.
        """
        # Create an instance of your consumer
        consumer = TableConsumer()
        
        # Call the handle_user_action method
        game_state_message = consumer.construct_game_state_message(
            'white_player', 'black_player', True,
            True, None, 'correct board',
            'white', None, 0, 0)
    
        # Verify the message sent to WebSocket room group
        assert game_state_message['white_player'] == 'white_player'
        assert game_state_message['black_player'] == 'black_player'
        assert game_state_message['white_player_ready'] == True
        assert game_state_message['black_player_ready'] == True
        assert game_state_message['winner'] == None
        assert game_state_message['board'] is not None
        assert game_state_message['turn'] == 'white'
        assert game_state_message['checking'] == None
        assert game_state_message['total_moves'] == 0
        assert game_state_message['soft_moves'] == 0

class TableConsumerTestCase6(TestCase):

    @pytest.mark.asyncio
    async def test_send_new_game_state(self):
        """
        Test send_new_game_state to ensure it sends the correct game state message to WebSocket.
        """
        # Create an instance of your consumer
        consumer = TableConsumer()
        
        # Prepare test data
        event = {
            'white_player': 'white_player',
            'black_player': 'black_player',
            'white_player_ready': True,
            'black_player_ready': True,
            'winner': None,
            'board': "correct board",
            'turn': 'white',
            'checking': None,
            'total_moves': 0,
            'soft_moves': 0,
        }

        # Mock async methods
        consumer.send_game_state_to_websocket = AsyncMock()
        expected_message = {
            'white_player': event['white_player'],
            'black_player': event['black_player'],
            'white_player_ready': event['white_player_ready'],
            'black_player_ready': event['black_player_ready'],
            'winner': event['winner'],
            'board': event['board'],
            'turn': event['turn'],
            'checking': event['checking'],
            'total_moves': event['total_moves'],
            'soft_moves': event['soft_moves']
        }
        consumer.construct_game_state_message = AsyncMock(return_value=expected_message)
        
        # Execute the method under test
        await consumer.send_new_game_state(event)

        # Verify that the correct message is sent to the WebSocket
        message = await consumer.send_game_state_to_websocket.call_args[0][0]
        assert message == expected_message

class TableConsumerTestCase7(TestCase):

    async def setup_consumer(self):
        # Create two users for the game
        user1 = await sync_to_async(User.objects.create)(
            username="white_player"
        )

        user2 = await sync_to_async(User.objects.create)(
            username="black_player"
        )

        # Set up a game in the test database
        game = await sync_to_async(Game.objects.create)(
            winner = None,
            started = True,
            white = user1,
            black = user2,
            white_ready = True,
            black_ready = True,
        )

        # Instantiate TableConsumer
        consumer = TableConsumer()
        consumer.table_id = 1

        # Add a boards to the game
        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=0,
            board=json.dumps([
                ["R", "N", "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", "n", "r"]
            ]),
            turn="w",
            castling="KQkq",
            enpassant="__",
            soft_moves=0
        )

        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=0,
            board=json.dumps([
                ["R", "N", "B", "K", "Q", "B", "N", "R"],
                [None, "P", "P", "P", "P", "P", "P", "P"],
                ["P", None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", "n", "r"]
            ]),
            turn="b",
            castling="KQkq",
            enpassant="__",
            soft_moves=1
        )

        return consumer, game

    @pytest.mark.asyncio
    async def test_get_game_from_database(self):
        """
        Test get_game_from_database to ensure it retrieves the correct game state from the database.
        """
        consumer, game = await self.setup_consumer()

        # Call the method and test it
        result = await consumer.get_game_from_database()

        # Assertions
        assert result.pk == game.pk
        assert result.winner == None
        assert result.started == True
        assert result.white.username == "white_player"
        assert result.white_ready == True
        assert result.black_ready == True

    @pytest.mark.asyncio
    async def test_get_latest_board_from_database(self):
        """
        Test get_latest_board_from_database to ensure it retrieves the correct board state from the database.
        """
        consumer, game = await self.setup_consumer()

        # Call the method and test it
        result = await consumer.get_latest_board_from_database(game)

        # Assertions
        assert result.pk == 2
        assert result.total_moves == 0
        assert result.board is not None
        assert result.turn == "black"
        assert result.castling == "KQkq"
        assert result.enpassant == "__"
        assert result.soft_moves == 1

    @pytest.mark.asyncio
    async def test_get_prev_boards_from_database(self):
        """
        Test get_prev_boards_from_databasee to ensure it retrieves the correct boards state from the database.
        """
        consumer, game = await self.setup_consumer()

        # Call the method and test it
        result = await consumer.get_prev_boards_from_database(game)

        # Assertions
        assert isinstance(result, list)
        assert result[0].pk == 1
        assert result[1].pk == 2
        assert result[0].total_moves == 0
        assert result[1].total_moves == 0
        assert result[0].board is not None
        assert result[1].board is not None
        assert result[0].turn == "w"
        assert result[1].turn == "b"
        assert result[0].castling == "KQkq"
        assert result[1].castling == "KQkq"
        assert result[0].enpassant == "__"
        assert result[1].enpassant == "__"
        assert result[0].soft_moves == 0
        assert result[1].soft_moves == 1

class TableConsumerTestCase8(TestCase):

    async def setup_consumer(self):
        # Create two users for the game
        user1 = await sync_to_async(User.objects.create)(
            username="white_player"
        )

        user2 = await sync_to_async(User.objects.create)(
            username="black_player"
        )

        # Set up a game in the test database
        game = await sync_to_async(Game.objects.create)(
            winner = None,
            started = True,
            white = user1,
            black = user2,
            white_ready = True,
            black_ready = True,
        )

        # Instantiate TableConsumer
        consumer = TableConsumer()
        consumer.table_id = 1

        return consumer, game
    
    @pytest.mark.asyncio
    async def test_push_new_board_to_database(self):
        """
        ...
        """
        consumer, game = await self.setup_consumer()

        updated_board=json.dumps([
            ["R", "N", "B", "K", "Q", "B", "N", "R"],
            [None, "P", "P", "P", "P", "P", "P", "P"],
            ["P", None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "k", "q", "b", "n", "r"]
        ]),
        turn="b",
        castling="KQkq",
        enpassant="__",
        total_moves=0,
        soft_moves=1



        # Call the method and test it
        result = await consumer.get_game_from_database()

        # Assertions
        assert result.pk == game.pk