from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, SimpleTestCase, TestCase
from django.conf import settings
from chess_django.asgi import application
from datetime import datetime, timezone, timedelta

from .models import Game, Board
from menu.models import User
from asgiref.sync import sync_to_async

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from .consumers import (TableConsumer, construct_game_state_message, get_game_from_database,
                        get_latest_board_from_database, get_prev_boards_from_database, push_new_board_to_database,
                        push_players_state_to_db, if_game_started, is_threefold_repetition)
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
        consumer.table_id = 1
        consumer.channel_layer = MagicMock()
        consumer.channel_name = "test_channel"

        # Mock the board state
        mock_board = MagicMock()
        mock_board.total_moves = 1
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
        mock_board.soft_moves = 1
        mock_board.checking = []
        mock_board.last_move = None

        # Mock async methods
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
        mock_game.winner = None
        mock_game.white_draw = False
        mock_game.black_draw = False

        play_audio = False

        # Setup consumer
        consumer, mock_board = await self.setup_consumer(mock_game)
        
        # Patch dependencies
        with (patch('table.pieces.Board') as MockBoard,
              patch('table.consumers.get_game_from_database') as get_game_from_database,
              patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database):
            
            MockBoard.return_value.create_json_class.return_value = (mock_board.board, None, None)
            get_game_from_database.return_value = mock_game
            get_latest_board_from_database.return_value = mock_board

            # Call the method
            await consumer.send_current_state(play_audio)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            get_latest_board_from_database.assert_called_once_with(mock_game)
            consumer.send_game_state_to_websocket.assert_called_once()


            # Verify the message sent to WebSocket
            message = consumer.send_game_state_to_websocket.call_args[0][0]
            assert message['white_player'] == 'test_user'
            assert message['black_player'] == 'black_player'
            assert message['white_player_ready'] == True
            assert message['black_player_ready'] == True
            assert message['winner'] == None
            assert message['board'] is not None
            assert message['turn'] == 'white'
            assert message['checking'] == None
            assert message['total_moves'] == 1
            assert message['soft_moves'] == 1
            assert message['last_move'] == None
            assert message['prev_boards_id_moves'] == mock_game.boards
            assert message['play_audio'] == False
            assert message['white_draw'] == False
            assert message['black_draw'] == False

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
        mock_game.white_draw = False
        mock_game.black_draw = False

        play_audio = False

        # Setup consumer
        consumer, mock_board = await self.setup_consumer(mock_game)
        
        # Patch dependencies
        with (patch('table.pieces.boardSimplify') as MockBoardSimplify,
              patch('table.consumers.get_game_from_database') as get_game_from_database,
              patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database):
            
            MockBoardSimplify.return_value = mock_board.board
            get_game_from_database.return_value = mock_game
            get_latest_board_from_database.return_value = mock_board
            
            # Call the method
            await consumer.send_current_state(play_audio)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            get_latest_board_from_database.assert_called_once_with(mock_game)
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
            assert message['checking'] == []
            assert message['total_moves'] == 1
            assert message['soft_moves'] == 1
            assert message['last_move'] == None
            assert message['prev_boards_id_moves'] == mock_game.boards
            assert message['play_audio'] == False
            assert message['white_draw'] == False
            assert message['black_draw'] == False

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
        mock_game.white_draw = False
        mock_game.black_draw = False

        play_audio = False

        # Setup consumer
        consumer, mock_board = await self.setup_consumer(mock_game)
        
        # Patch dependencies
        with (patch('table.pieces.boardSimplify') as MockBoardSimplify,
              patch('table.consumers.get_game_from_database') as get_game_from_database):
            
            MockBoardSimplify.return_value = mock_board.board
            get_game_from_database.return_value = mock_game
            
            # Call the method
            await consumer.send_current_state(play_audio)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
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
            assert message['last_move'] == None
            assert message['prev_boards_id_moves'] == mock_game.boards
            assert message['play_audio'] == False
            assert message['white_draw'] == False
            assert message['black_draw'] == False


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
        consumer.table_id = 1
        consumer.channel_layer = MagicMock()
        consumer.channel_name = "test_channel"

        # Mock game state
        consumer.mock_game = MagicMock()
        consumer.mock_game.white = None
        consumer.mock_game.black = MagicMock(username="black_player")
        consumer.mock_game.white_ready = False
        consumer.mock_game.black_ready = True
        consumer.mock_game.winner = None
        consumer.mock_game.boards = [[1]]

        # Mock async methods
        # consumer.get_game_from_database = AsyncMock(return_value=mock_game)
        consumer.handle_move = AsyncMock()
        consumer.send_current_state = AsyncMock()
        consumer.handle_board_request = AsyncMock()
        consumer.handle_resign = AsyncMock()
        consumer.handle_draw = AsyncMock()
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
                          'promotion': None,
                          'requested_board': None,
                          'resign': None,
                          'draw': None}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()

        with (patch('table.consumers.get_game_from_database') as get_game_from_database):
            get_game_from_database.return_value = consumer.mock_game

            # Call the method
            await consumer.receive(mock_text_data_json)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            consumer.handle_move.assert_called_once_with(
                consumer.mock_game,
                consumer.scope["user"],
                mock_text_data["move"],
                mock_text_data["promotion"]
            )

    @pytest.mark.asyncio
    async def test_send_current_state(self):
        """
        Test request the board and it's the current one.
        """
        mock_text_data = {'white_player': 'white_player',
                          'black_player': 'black_player',
                          'white_player_ready': None,
                          'black_player_ready': None,
                          'move': None,
                          'promotion': None,
                          'requested_board': 1,
                          'resign': None,
                          'draw': None}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()
        
        with (patch('table.consumers.get_game_from_database') as get_game_from_database):
            get_game_from_database.return_value = consumer.mock_game

            # Call the method
            await consumer.receive(mock_text_data_json)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            consumer.send_current_state.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_handle_board_request(self):
        """
        Test request the board.
        """
        mock_text_data = {'white_player': 'white_player',
                          'black_player': 'black_player',
                          'white_player_ready': None,
                          'black_player_ready': None,
                          'move': None,
                          'promotion': None,
                          'requested_board': 2,
                          'resign': None,
                          'draw': None}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()
        
        with (patch('table.consumers.get_game_from_database') as get_game_from_database):
            get_game_from_database.return_value = consumer.mock_game

            # Call the method
            await consumer.receive(mock_text_data_json)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            consumer.handle_board_request.assert_called_once_with(
                consumer.mock_game,
                consumer.scope["user"],
                mock_text_data["requested_board"]
            )

    @pytest.mark.asyncio
    async def test_handle_resign(self):
        """
        Test the receive method handling a user resign.
        """
        mock_text_data = {'white_player': 'white_player',
                          'black_player': 'black_player',
                          'white_player_ready': None,
                          'black_player_ready': None,
                          'move': None,
                          'promotion': None,
                          'requested_board': None,
                          'resign': True,
                          'draw': None}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()
        
        with (patch('table.consumers.get_game_from_database') as get_game_from_database):
            get_game_from_database.return_value = consumer.mock_game

            # Call the method
            await consumer.receive(mock_text_data_json)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            consumer.handle_resign.assert_called_once_with(
                consumer.mock_game,
                consumer.scope["user"]
            )

    @pytest.mark.asyncio
    async def test_handle_draw(self):
        """
        Test the receive method handling a user draw.
        """
        mock_text_data = {'white_player': 'white_player',
                          'black_player': 'black_player',
                          'white_player_ready': None,
                          'black_player_ready': None,
                          'move': None,
                          'promotion': None,
                          'requested_board': None,
                          'resign': None,
                          'draw': True}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()
        
        with (patch('table.consumers.get_game_from_database') as get_game_from_database):
            get_game_from_database.return_value = consumer.mock_game

            # Call the method
            await consumer.receive(mock_text_data_json)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            consumer.handle_draw.assert_called_once_with(
                consumer.mock_game,
                consumer.scope["user"]
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
                          'promotion': None,
                          'requested_board': None,
                          'resign': None,
                          'draw': None}
        
        mock_text_data_json = json.dumps(mock_text_data)

        # Setup consumer
        consumer = await self.setup_consumer()
        
        with (patch('table.consumers.get_game_from_database') as get_game_from_database):
            get_game_from_database.return_value = consumer.mock_game

            # Call the method
            await consumer.receive(mock_text_data_json)

            # Verify interactions and state
            get_game_from_database.assert_called_once()
            consumer.handle_user_action.assert_called_once_with(
                consumer.mock_game,
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
        consumer.table_id = 1
        consumer.channel_layer = MagicMock()
        consumer.channel_name = "test_channel"

        # Mock async methods
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
        mock_game.white_draw = False
        mock_game.black_draw = False

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
        mock_board_prev.white_time_left = timedelta(minutes=15)
        mock_board_prev.black_time_left = timedelta(minutes=15)
        mock_board_prev.created_at = datetime(2024, 6, 24, 21, 0, 0, tzinfo=timezone.utc)

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
        mock_board_next.white_time_left = timedelta(minutes=15)
        mock_board_next.black_time_left = timedelta(minutes=15)
        mock_board_next.created_at = datetime(2024, 6, 24, 21, 0, 0, tzinfo=timezone.utc)
        mock_board_next.checking = []

        # Mock the next board class for moved_piece
        mock_board_class = [[None, None, {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 0), (3, 0)}, set(), False)}, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None]]
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None
        last_move_string = "0102"
        moved_piece = ('pawn', 'white')

        # Make patches to control its behavior in the test
        with (patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database,
              patch('table.consumers.get_prev_boards_from_database') as get_prev_boards_from_database,
              patch('table.consumers.get_current_time') as get_current_time,
              patch('table.pieces.Board') as MockBoard,
              patch('table.consumers.is_threefold_repetition') as is_threefold_repetition,
              patch('table.tasks.check_game_timeout.apply_async'),
              patch('table.consumers.change_move_to_string') as change_move_to_string,
              patch('table.consumers.push_new_board_to_database') as push_new_board_to_database):
            
            get_latest_board_from_database.return_value = mock_board_prev
            get_prev_boards_from_database.return_value = [mock_board_prev]
            get_current_time.return_value = timedelta(minutes=15), timedelta(minutes=15)
            MockBoard.return_value.create_new_json_board.return_value = (mock_board_next.board, mock_board_next.castling, mock_board_next.enpassant, True)
            MockBoard.return_value.create_json_class.return_value = (mock_board_class, None, None)
            is_threefold_repetition.return_value = False
            change_move_to_string.return_value = "0102"

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            get_latest_board_from_database.assert_called_once()
            get_prev_boards_from_database.assert_called_once()
            push_new_board_to_database.assert_called_once_with(
                consumer.table_id,
                mock_board_next.board,
                mock_board_next.turn,
                mock_board_next.castling,
                mock_board_next.enpassant,
                None,
                mock_board_next.total_moves,
                mock_board_next.soft_moves,
                mock_board_next.white_time_left,
                mock_board_next.black_time_left,
                last_move_string,
                moved_piece,
                mock_board_next.checking
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
            assert message['checking'] == mock_board_next.checking
            assert message['total_moves'] == mock_board_next.total_moves
            assert message['soft_moves'] == mock_board_next.soft_moves
            assert message['white_time_left'] == mock_board_next.white_time_left.total_seconds()
            assert message['black_time_left'] == mock_board_next.black_time_left.total_seconds()
            assert message['last_move'] == last_move_string
            assert message['play_audio'] == True
            assert message['white_draw'] == mock_game.white_draw
            assert message['black_draw'] == mock_game.black_draw

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
        mock_game.white_draw = False
        mock_game.black_draw = False

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
        mock_board_prev.white_time_left = timedelta(minutes=15)
        mock_board_prev.black_time_left = timedelta(minutes=15)
        mock_board_prev.created_at = datetime(2024, 6, 24, 21, 0, 0, tzinfo=timezone.utc)

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
        mock_board_next.white_time_left = timedelta(minutes=15)
        mock_board_next.black_time_left = timedelta(minutes=15)
        mock_board_next.created_at = datetime(2024, 6, 24, 21, 0, 0, tzinfo=timezone.utc)
        mock_board_next.checking = []

        # Mock the next board class for moved_piece
        mock_board_class = [[None, None, {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 0), (3, 0)}, set(), False)}, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None]]
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None
        last_move_string = "0102"
        moved_piece = ('pawn', 'white')

        # Make patches to control its behavior in the test
        with (patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database,
              patch('table.consumers.get_prev_boards_from_database') as get_prev_boards_from_database,
              patch('table.consumers.get_current_time') as get_current_time,
              patch('table.pieces.Board') as MockBoard,
              patch('table.consumers.is_threefold_repetition') as is_threefold_repetition,
              patch('table.tasks.check_game_timeout.apply_async'),
              patch('table.consumers.change_move_to_string') as change_move_to_string,
              patch('table.consumers.push_new_board_to_database') as push_new_board_to_database):
            
            get_latest_board_from_database.return_value = mock_board_prev
            get_prev_boards_from_database.return_value = [mock_board_prev]
            get_current_time.return_value = timedelta(minutes=15), timedelta(minutes=15)
            MockBoard.return_value.create_new_json_board.return_value = (mock_board_next.board, mock_board_next.castling, mock_board_next.enpassant, True)
            MockBoard.return_value.create_json_class.return_value = (mock_board_class, None, None)
            is_threefold_repetition.return_value = True
            change_move_to_string.return_value = "0102"

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], True)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            get_latest_board_from_database.assert_called_once()
            get_prev_boards_from_database.assert_called_once()
            push_new_board_to_database.assert_called_once_with(
                consumer.table_id,
                mock_board_next.board,
                mock_board_next.turn,
                mock_board_next.castling,
                mock_board_next.enpassant,
                'draw',
                mock_board_next.total_moves,
                mock_board_next.soft_moves,
                mock_board_next.white_time_left,
                mock_board_next.black_time_left,
                last_move_string,
                moved_piece,
                mock_board_next.checking
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
            assert message['checking'] == mock_board_next.checking
            assert message['total_moves'] == mock_board_next.total_moves
            assert message['soft_moves'] == mock_board_next.soft_moves
            assert message['white_time_left'] == mock_board_next.white_time_left.total_seconds()
            assert message['black_time_left'] == mock_board_next.black_time_left.total_seconds()
            assert message['last_move'] == last_move_string
            assert message['play_audio'] == True
            assert message['white_draw'] == mock_game.white_draw
            assert message['black_draw'] == mock_game.black_draw
    
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
        mock_game.white_draw = False
        mock_game.black_draw = False

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
        mock_board_prev.white_time_left = timedelta(minutes=15)
        mock_board_prev.black_time_left = timedelta(minutes=15)
        mock_board_prev.created_at = datetime(2024, 6, 24, 21, 0, 0, tzinfo=timezone.utc)


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
        mock_board_next.white_time_left = timedelta(minutes=15)
        mock_board_next.black_time_left = timedelta(minutes=15)
        mock_board_next.created_at = datetime(2024, 6, 24, 21, 0, 5, tzinfo=timezone.utc)
        mock_board_next.checking = []

        # Mock the next board class for moved_piece
        mock_board_class = [[None, None, {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 0), (3, 0)}, set(), False)}, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None],
                            [None, None, None, None, None, None, None, None]]
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None
        last_move_string = "0102"
        moved_piece = ('pawn', 'white')

        # Make patches to control its behavior in the test
        with (patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database,
              patch('table.consumers.get_prev_boards_from_database') as get_prev_boards_from_database,
              patch('table.consumers.get_current_time') as get_current_time,
              patch('table.pieces.Board') as MockBoard,
              patch('table.consumers.is_threefold_repetition') as is_threefold_repetition,
              patch('table.tasks.check_game_timeout.apply_async'),
              patch('table.consumers.change_move_to_string') as change_move_to_string,
              patch('table.consumers.push_new_board_to_database') as push_new_board_to_database):
            
            get_latest_board_from_database.return_value = mock_board_prev
            get_prev_boards_from_database.return_value = [mock_board_prev]
            get_current_time.return_value = timedelta(minutes=15), timedelta(minutes=15)
            MockBoard.return_value.create_new_json_board.return_value = (mock_board_next.board, mock_board_next.castling, mock_board_next.enpassant, True)
            MockBoard.return_value.create_json_class.return_value = (mock_board_class, None, None)
            is_threefold_repetition.return_value = True
            change_move_to_string.return_value = "0102"

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            get_latest_board_from_database.assert_called_once()
            get_prev_boards_from_database.assert_called_once()
            push_new_board_to_database.assert_called_once_with(
                consumer.table_id,
                mock_board_next.board,
                mock_board_next.turn,
                mock_board_next.castling,
                mock_board_next.enpassant,
                'draw',
                mock_board_next.total_moves,
                mock_board_next.soft_moves,
                mock_board_next.white_time_left,
                mock_board_next.black_time_left,
                last_move_string,
                moved_piece,
                mock_board_next.checking
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
            assert message['checking'] == mock_board_next.checking
            assert message['total_moves'] == mock_board_next.total_moves
            assert message['soft_moves'] == mock_board_next.soft_moves
            assert message['white_time_left'] == mock_board_next.white_time_left.total_seconds()
            assert message['black_time_left'] == mock_board_next.black_time_left.total_seconds()
            assert message['last_move'] == last_move_string
            assert message['play_audio'] == True
            assert message['white_draw'] == mock_game.white_draw
            assert message['black_draw'] == mock_game.black_draw
    
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
        
        # Mock the move details
        mock_move = [[0, 1], [0, 2]]
        mock_promotion = None

        # Patch the Board class to control its behavior in the test
        with (patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database,
              patch('table.consumers.get_prev_boards_from_database') as get_prev_boards_from_database,
              patch('table.consumers.get_current_time') as get_current_time,
              patch('table.pieces.Board') as MockBoard,
              patch('table.consumers.push_new_board_to_database') as push_new_board_to_database):
            
            get_latest_board_from_database.return_value = mock_board_prev
            get_prev_boards_from_database.return_value = [mock_board_prev]
            get_current_time.return_value = timedelta(minutes=15), timedelta(minutes=15)
            MockBoard.return_value.create_new_json_board.return_value = (None, None, None, True)

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            get_latest_board_from_database.assert_called_once()
            get_prev_boards_from_database.assert_called_once()
            push_new_board_to_database.assert_not_called()

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
        with (patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database,
              patch('table.consumers.get_prev_boards_from_database') as get_prev_boards_from_database,
              patch('table.consumers.get_current_time') as get_current_time,
              patch('table.pieces.Board') as MockBoard,
              patch('table.consumers.push_new_board_to_database') as push_new_board_to_database):
            
            get_latest_board_from_database.return_value = mock_board_prev
            get_prev_boards_from_database.return_value = [mock_board_prev]
            get_current_time.return_value = timedelta(minutes=15), timedelta(minutes=15)
            MockBoard.return_value.create_new_json_board.return_value = (None, None, None, True)

            # Setup consumers
            consumer = await self.setup_consumer(mock_board_prev, [mock_board_prev], False)
            
            # Call the handle_move method with mocked game state and move
            await consumer.handle_move(mock_game, consumer.scope["user"], mock_move, mock_promotion)

            # Assert that the correct database methods were called
            get_latest_board_from_database.assert_called_once()
            get_prev_boards_from_database.assert_called_once()
            push_new_board_to_database.assert_not_called()

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
        consumer.mock_start_board = MagicMock()
        consumer.mock_start_board.total_moves = 0
        consumer.mock_start_board.board = json.dumps([["R", "N", "B", "K", "Q", "B", "N", "R"],
                                                      ["P", "P", "P", "P", "P", "P", "P", "P"],
                                                      [None, None, None, None, None, None, None, None],
                                                      [None, None, None, None, None, None, None, None],
                                                      [None, None, None, None, None, None, None, None],
                                                      [None, None, None, None, None, None, None, None],
                                                      ["p", "p", "p", "p", "p", "p", "p", "p"],
                                                      ["r", "n", "b", "k", "q", "b", "n", "r"]])
        consumer.mock_start_board.turn = "white"
        consumer.mock_start_board.castling = "KQkq"
        consumer.mock_start_board.enpassant = "__"
        consumer.mock_start_board.soft_moves = 0

        consumer.started = started

        # Mock async methods that will be called during the tests
        # consumer.push_players_state_to_db = AsyncMock()
        # consumer.if_game_started = MagicMock(return_value=started)
        # consumer.get_latest_board_from_database = AsyncMock(return_value=mock_start_board)
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

        # Patch the Board class and check_game_timeout to control its behavior in the test
        with (patch('table.pieces.Board') as MockBoard, patch('table.tasks.check_game_timeout.apply_async'),
              patch('table.consumers.push_players_state_to_db') as push_players_state_to_db,
              patch('table.consumers.if_game_started') as if_game_started,
              patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database):

            # Setup consumers
            consumer = await self.setup_consumer(True)

            MockBoard.return_value.create_json_class.return_value = ("correct_class", None, None)
            if_game_started.return_value = consumer.started
            get_latest_board_from_database.return_value = consumer.mock_start_board

            # Call the handle_user_action method
            await consumer.handle_user_action(mock_game, consumer.scope["user"], mock_text_data)

            # Assert that the database method to update player state was called correctly
            push_players_state_to_db.assert_called_once_with(
                mock_game,
                consumer.scope["user"],
                mock_text_data,
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

        # Patch the BoardSimplify class to control its behavior in the test
        with (patch('table.pieces.Board') as MockBoard, patch('table.tasks.check_game_timeout.apply_async'),
              patch('table.consumers.push_players_state_to_db') as push_players_state_to_db,
              patch('table.consumers.if_game_started') as if_game_started,
              patch('table.consumers.get_latest_board_from_database') as get_latest_board_from_database):
            
            # Setup consumers
            consumer = await self.setup_consumer(False)

            MockBoard.return_value.create_json_class.return_value = ("correct_class", None, None)
            if_game_started.return_value = consumer.started
            get_latest_board_from_database.return_value = consumer.mock_start_board
            
            # Call the handle_user_action method
            await consumer.handle_user_action(mock_game, consumer.scope["user"], mock_text_data)

            # Assert that the database method to update player state was called correctly
            push_players_state_to_db.assert_called_once_with(
                mock_game,
                consumer.scope["user"],
                mock_text_data,
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

    @pytest.mark.asyncio
    async def test_send_new_game_state(self):
        """
        Test send_new_game_state to ensure it sends the correct game state message to WebSocket.
        """
        # Create an instance of your consumer
        consumer = TableConsumer()
        
        # Mock async methods
        consumer.send_game_state_to_websocket = AsyncMock()
        
        # Prepare test data
        event = {
            'white_player': 'white_player',
            'black_player': 'black_player',
            'white_player_ready': True,
            'black_player_ready': True,
            'winner': None,
            'board_id': 1,
            'board': "correct board",
            'turn': 'white',
            'checking': None,
            'total_moves': 0,
            'soft_moves': 0,
            'white_time_left': None,
            'black_time_left': None,
            'last_move': None,
            'prev_boards_id_moves': [],
            'play_audio': False,
            'white_draw': False,
            'black_draw': False,
        }

        expected_message = {
            'white_player': event['white_player'],
            'black_player': event['black_player'],
            'white_player_ready': event['white_player_ready'],
            'black_player_ready': event['black_player_ready'],
            'winner': event['winner'],
            'board_id': event['board_id'],
            'board': event['board'],
            'turn': event['turn'],
            'checking': event['checking'],
            'total_moves': event['total_moves'],
            'soft_moves': event['soft_moves'],
            'white_time_left': event["white_time_left"],
            'black_time_left': event["black_time_left"],
            'last_move': event["last_move"],
            'prev_boards_id_moves': event["prev_boards_id_moves"],
            'play_audio': event["play_audio"],
            'white_draw': event["white_draw"],
            'black_draw': event["black_draw"],
        }
        construct_game_state_message.return_value = expected_message
        
        # Execute the method under test
        await consumer.send_new_game_state(event)

        # Verify that the correct message is sent to the WebSocket
        message = consumer.send_game_state_to_websocket.call_args[0][0]
        assert message == expected_message

class TableConsumerTestCase6(TestCase):

    def test_construct_game_state_message(self):
        """
        Test construct_game_state_message to ensure it returns the correct dictionary.
        """
        white_player = 'white_player'
        black_player = 'black_player'
        white_ready = True
        black_ready = True
        winner = None
        board_id = 1
        board = 'correct board'
        turn = 'white'
        checking = None
        total_moves = 0
        soft_moves = 0
        white_time_left = 900
        black_time_left = 900
        last_move = None
        prev_boards_id_moves = []
        play_audio = False
        white_draw = True
        black_draw = False

        # Call the handle_user_action method
        game_state_message = construct_game_state_message(
            white_player, black_player, white_ready,
            black_ready, winner, board_id, board, turn,
            checking, total_moves, soft_moves,
            white_time_left, black_time_left, last_move,
            prev_boards_id_moves, play_audio, white_draw, black_draw)
    
        # Verify the message sent to WebSocket room group
        assert game_state_message['white_player'] == white_player
        assert game_state_message['black_player'] == black_player
        assert game_state_message['white_player_ready'] == white_ready
        assert game_state_message['black_player_ready'] == black_ready
        assert game_state_message['winner'] == winner
        assert game_state_message['board'] is not None
        assert game_state_message['turn'] == turn
        assert game_state_message['checking'] == checking
        assert game_state_message['total_moves'] == total_moves
        assert game_state_message['soft_moves'] == soft_moves
        assert game_state_message['white_time_left'] == white_time_left
        assert game_state_message['black_time_left'] == black_time_left
        assert game_state_message['last_move'] == last_move
        assert game_state_message['prev_boards_id_moves'] == prev_boards_id_moves
        assert game_state_message['play_audio'] == play_audio
        assert game_state_message['white_draw'] == white_draw
        assert game_state_message['black_draw'] == black_draw

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
        result = await get_game_from_database(consumer.table_id)

        # Assertions
        assert result.pk == game.pk
        assert result.winner == None
        assert result.started == True
        assert result.white.username == "white_player"
        assert result.black.username == "black_player"
        assert result.white_ready == True
        assert result.black_ready == True

    @pytest.mark.asyncio
    async def test_get_latest_board_from_database(self):
        """
        Test get_latest_board_from_database to ensure it retrieves the correct board state from the database.
        """
        consumer, game = await self.setup_consumer()

        # Call the method and test it
        result = await get_latest_board_from_database(game)

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
        result = await get_prev_boards_from_database(game)

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
    async def test_push_new_board_to_database_with_no_winner(self):
        """
        Test the push_new_board_to_database method of TableConsumer.
        """
        consumer, game = await self.setup_consumer()

        updated_board = json.dumps([
            ["R", "N", "B", "K", "Q", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "k", "q", "b", "n", "r"]
        ])
        turn = "b"
        castling = "KQkq"
        enpassant = "__"
        winner = None
        total_moves = 0
        soft_moves = 0
        white_time_left = timedelta(minutes=15)
        black_time_left = timedelta(minutes=15)
        last_move = "1212"
        moved_piece = "pawn"
        checking = []

        # Call the method and test it
        await push_new_board_to_database(
            consumer.table_id, updated_board, turn, castling, enpassant, winner, total_moves, soft_moves, white_time_left, black_time_left, last_move, moved_piece, checking
        )

        current_board = await sync_to_async(Board.objects.filter(game=game).latest)('id')

        # Assertions
        assert json.loads(current_board.board) == updated_board
        assert current_board.turn == turn
        assert current_board.castling == castling
        assert current_board.enpassant == enpassant
        assert current_board.total_moves == total_moves
        assert current_board.soft_moves == soft_moves
        assert current_board.white_time_left == white_time_left
        assert current_board.black_time_left == black_time_left
        assert current_board.last_move == last_move
        assert current_board.checking == checking

        game = await sync_to_async(Game.objects.get)(pk=game.id)
        assert game.winner == None

    @pytest.mark.asyncio
    async def test_push_new_board_to_database_with_winner(self):
        """
        Test the push_new_board_to_database method of TableConsumer.
        """
        consumer, game = await self.setup_consumer()

        updated_board = json.dumps([
            ["R", "N", "B", "K", "Q", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "k", "q", "b", "n", "r"]
        ])
        turn = "b"
        castling = "KQkq"
        enpassant = "__"
        winner = "draw"
        total_moves = 0
        soft_moves = 0
        white_time_left = timedelta(minutes=15)
        black_time_left = timedelta(minutes=15)
        last_move = "1212"
        moved_piece = "pawn"
        checking = []

        # Call the method and test it
        await push_new_board_to_database(
            consumer.table_id, updated_board, turn, castling, enpassant, winner, total_moves, soft_moves, white_time_left, black_time_left, last_move, moved_piece, checking
        )

        current_board = await sync_to_async(Board.objects.filter(game=game).latest)('id')

        # Assertions
        assert json.loads(current_board.board) == updated_board
        assert current_board.turn == turn
        assert current_board.castling == castling
        assert current_board.enpassant == enpassant
        assert current_board.total_moves == total_moves
        assert current_board.soft_moves == soft_moves
        assert current_board.white_time_left == white_time_left
        assert current_board.black_time_left == black_time_left
        assert current_board.last_move == last_move
        assert current_board.checking == checking

        game = await sync_to_async(Game.objects.get)(pk=game.pk)
        assert game.winner == "d"

class TableConsumerTestCase9(TestCase):

    async def setup_consumer(self, white, black, white_ready, black_ready):

        # Set up a game in the test database
        game = await sync_to_async(Game.objects.create)(
            winner = None,
            started = False,
            white = white,
            black = black,
            white_ready = white_ready,
            black_ready = black_ready,
        )

        return game
    
    @pytest.mark.asyncio
    async def test_push_players_state_to_db_add_player(self):
        """
        Test adding a player to the game.
        """
        # Create users for the game
        user1 = await sync_to_async(User.objects.create)(username="white_player")

        game = await self.setup_consumer(None, None, False, False)

        # Mock the input data that would be received from the WebSocket
        mock_text_data = {
            'white_player': True,
            'black_player': None,
            'white_player_ready': None,
            'black_player_ready': None,
            'move': None,
            'promotion': None
        }

        # Call the method and test it
        await push_players_state_to_db(game, user1, mock_text_data)
        game = await sync_to_async(Game.objects.get)(pk=game.pk)

        # Assertions
        assert await sync_to_async(lambda: game.white)() == user1
        assert game.black == None
        assert game.white_ready == False
        assert game.black_ready == False

        # Check if the function creates a board
        try:
            current_board = await sync_to_async(Board.objects.filter(game=game).latest)('id')
            assert current_board is None
        except Board.DoesNotExist:
            assert True

    @pytest.mark.asyncio
    async def test_push_players_state_to_db_remove_player(self):
        """
        Test removing a player from the game.
        """
        # Create users for the game
        user1 = await sync_to_async(User.objects.create)(username="white_player")

        game = await self.setup_consumer(user1, None, False, False)

        # Mock the input data that would be received from the WebSocket
        mock_text_data = {
            'white_player': False,
            'black_player': None,
            'white_player_ready': None,
            'black_player_ready': None,
            'move': None,
            'promotion': None
        }

        # Call the method and test it
        await push_players_state_to_db(game, user1, mock_text_data)
        game = await sync_to_async(Game.objects.get)(pk=game.pk)

        # Assertions
        assert game.white == None
        assert game.black == None
        assert game.white_ready == False
        assert game.black_ready == False

        # Check if the function creates a board
        try:
            current_board = await sync_to_async(Board.objects.filter(game=game).latest)('id')
            assert current_board is None
        except Board.DoesNotExist:
            assert True

    @pytest.mark.asyncio
    async def test_push_players_state_to_db_player_ready(self):
        """
        Test setting a player as ready.
        """
        # Create users for the game
        user1 = await sync_to_async(User.objects.create)(username="white_player")

        game = await self.setup_consumer(user1, None, False, False)

        # Mock the input data that would be received from the WebSocket
        mock_text_data = {
            'white_player': None,
            'black_player': None,
            'white_player_ready': True,
            'black_player_ready': None,
            'move': None,
            'promotion': None
        }

        # Call the method and test it
        await push_players_state_to_db(game, user1, mock_text_data)
        game = await sync_to_async(Game.objects.get)(pk=game.pk)

        # Assertions
        assert await sync_to_async(lambda: game.white)() == user1
        assert game.black == None
        assert game.white_ready == True
        assert game.black_ready == False

        # Check if the function creates a board
        try:
            current_board = await sync_to_async(Board.objects.filter(game=game).latest)('id')
            assert current_board is None
        except Board.DoesNotExist:
            assert True

    @pytest.mark.asyncio
    async def test_push_players_state_to_db_player_unready(self):
        """
        Test setting a player as not ready.
        """
        # Create users for the game
        user1 = await sync_to_async(User.objects.create)(username="white_player")

        game = await self.setup_consumer(user1, None, True, False)

        # Mock the input data that would be received from the WebSocket
        mock_text_data = {
            'white_player': None,
            'black_player': None,
            'white_player_ready': False,
            'black_player_ready': None,
            'move': None,
            'promotion': None
        }

        # Call the method and test it
        await push_players_state_to_db(game, user1, mock_text_data)

        # Assertions
        game = await sync_to_async(Game.objects.get)(pk=game.pk)
        assert await sync_to_async(lambda: game.white)() == user1
        assert game.black == None
        assert game.white_ready == False
        assert game.black_ready == False

        # Check if the function creates a board
        try:
            current_board = await sync_to_async(Board.objects.filter(game=game).latest)('id')
            assert current_board is None
        except Board.DoesNotExist:
            assert True

    @pytest.mark.asyncio
    async def test_push_players_state_to_db_both_player_ready(self):
        """
        Test setting both players as ready and check if the board is created.
        """
        # Create users for the game
        user1 = await sync_to_async(User.objects.create)(username="white_player")

        user2 = await sync_to_async(User.objects.create)(username="black_player")

        game = await self.setup_consumer(user1, user2, True, False)

        # Mock the input data that would be received from the WebSocket
        mock_text_data = {
            'white_player': None,
            'black_player': None,
            'white_player_ready': None,
            'black_player_ready': True,
            'move': None,
            'promotion': None
        }

        # Call the method and test it
        await push_players_state_to_db(game, user2, mock_text_data)

        # Assertions
        game = await sync_to_async(Game.objects.get)(pk=game.pk)
        assert await sync_to_async(lambda: game.white)() == user1
        assert await sync_to_async(lambda: game.black)() == user2
        assert game.white_ready == True
        assert game.black_ready == True

        # Check if the function creates a board
        try:
            current_board = await sync_to_async(Board.objects.filter(game=game).latest)('id')
            assert current_board is not None
        except Board.DoesNotExist:
            assert False

class TableConsumerTestCase10(TestCase):

    async def setup_consumer(self, white, black, white_ready, black_ready):

        # Set up a game in the test database
        game = await sync_to_async(Game.objects.create)(
            winner = None,
            started = False,
            white = white,
            black = black,
            white_ready = white_ready,
            black_ready = black_ready,
        )

        return game
    
    @pytest.mark.asyncio
    async def test_if_game_started_true(self):
        """
        Test if the if_game_started method returns True when both players are ready.
        """
        # Create users for the game
        user1 = await sync_to_async(User.objects.create)(username="white_player")
        user2 = await sync_to_async(User.objects.create)(username="black_player")

        game = await self.setup_consumer(user1, user2, True, True)

        # Call the method and test it
        result = if_game_started(game)

        # Assertions
        assert result == True

    @pytest.mark.asyncio
    async def test_if_game_started_false(self):
        """
        Test if the if_game_started method returns False when one or both players are not ready.
        """
        # Create users for the game
        user1 = await sync_to_async(User.objects.create)(username="white_player")
        user2 = await sync_to_async(User.objects.create)(username="black_player")

        game = await self.setup_consumer(user1, user2, True, False)

        # Call the method and test it
        result = if_game_started(game)

        # Assertions
        assert result == False

class TableConsumerTestCase11(TestCase):

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
                ["R", None, "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, "N", None, None, None, None, None],
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

        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=1,
            board=json.dumps([
                ["R", None, "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, "N", None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, "n", None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", None, "r"]
            ]),
            turn="w",
            castling="KQkq",
            enpassant="__",
            soft_moves=2
        )

        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=1,
            board=json.dumps([
                ["R", "N", "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, "n", None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", None, "r"]
            ]),
            turn="b",
            castling="KQkq",
            enpassant="__",
            soft_moves=3
        )

        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=2,
            board=json.dumps([
                ["R", "N", "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", 'n', "r"]
            ]),
            turn="w",
            castling="KQkq",
            enpassant="__",
            soft_moves=4
        )

        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=2,
            board=json.dumps([
                ["R", None, "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, "N", None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", "n", "r"]
            ]),
            turn="b",
            castling="KQkq",
            enpassant="__",
            soft_moves=5
        )

        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=3,
            board=json.dumps([
                ["R", None, "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, "N", None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, "n", None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", None, "r"]
            ]),
            turn="w",
            castling="KQkq",
            enpassant="__",
            soft_moves=6
        )

        await sync_to_async(Board.objects.create)(
            game=game,
            total_moves=3,
            board=json.dumps([
                ["R", "N", "B", "K", "Q", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, "n", None, None],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "k", "q", "b", None, "r"]
            ]),
            turn="b",
            castling="KQkq",
            enpassant="__",
            soft_moves=7
        )

        return game
    
    @pytest.mark.asyncio
    async def test_is_threefold_repetition_True(self):
        """
        Test if the is_threefold_repetition method correctly identifies a threefold repetition.
        """
        game = await self.setup_consumer()

        prev_boards = await sync_to_async(lambda: list(Board.objects.filter(game=game)))()

        next_board = [
            ["R", "N", "B", "K", "Q", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "k", "q", "b", "n", "r"]
        ]
        next_castling = "KQkq"
        next_enpassant = "__"
        next_turn = "white"

        # Call the method and test it
        result = is_threefold_repetition(prev_boards, next_board, next_castling, next_enpassant, next_turn)

        # Assertions
        assert result == True

    @pytest.mark.asyncio
    async def test_is_threefold_repetition_False(self):
        """
        Test if the is_threefold_repetition method correctly identifies when there is no threefold repetition.
        """
        game = await self.setup_consumer()

        prev_boards = await sync_to_async(lambda: list(Board.objects.filter(game=game)))()

        next_board = [
            ["R", "N", "B", "K", "Q", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, "n", None, None, "n", None, None],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", None, "b", "k", "q", "b", None, "r"]
        ]
        next_castling = "KQkq"
        next_enpassant = "__"
        next_turn = "white"

        # Call the method and test it
        result = is_threefold_repetition(prev_boards, next_board, next_castling, next_enpassant, next_turn)

        # Assertions
        assert result == False