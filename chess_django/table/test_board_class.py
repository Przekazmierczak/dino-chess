import unittest

from table.pieces import Piece, Board

ROWS, COLS = 8, 8

class Unpack_db(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["R", "N", "B", "K", "Q", "B", "N", "R"],
                          ["P", "P", "P", "P", "P", "P", "P", "P"],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          ["p", "p", "p", "p", "p", "p", "p", "p"],
                          ["r", "n", "b", "k", "q", "b", "n", "r"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_unpack_db_1(self):
        """Examine the correctness of the unpack_db function value __"""
        self.assertEqual(self.board.unpack_db("__"), None)

    def test_unpack_db_2(self):
        """Examine the correctness of the unpack_db function value 12"""
        self.assertEqual(self.board.unpack_db("12"), (1, 2))

    def test_unpack_db_3(self):
        """Examine the correctness of the unpack_db function value 35"""
        self.assertEqual(self.board.unpack_db("35"), (3, 5))

    def test_unpack_db_4(self):
        """Examine the correctness of the unpack_db function value 77"""
        self.assertEqual(self.board.unpack_db("77"), (7, 7))

class Create_class(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["R", "N", "B", "K", "Q", "B", "N", "R"],
                          ["P", "P", "P", "P", "P", "P", "P", "P"],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          ["p", "p", "p", "p", "p", "p", "p", "p"],
                          ["r", "n", "b", "k", "q", "b", "n", "r"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_class(self):
        """Examine the correctness of the create_class function"""
        result_board = [[Piece("rook", "white", (0, 0)), Piece("knight", "white", (0, 1)), Piece("bishop", "white", (0, 2)),
                         Piece("king", "white", (0, 3)), Piece("queen", "white", (0, 4)), Piece("bishop", "white", (0, 5)),
                         Piece("knight", "white", (0, 6)), Piece("rook", "white", (0, 7))],
                        [Piece("pawn", "white", (1, 0)), Piece("pawn", "white", (1, 1)), Piece("pawn", "white", (1, 2)),
                         Piece("pawn", "white", (1, 3)), Piece("pawn", "white", (1, 4)), Piece("pawn", "white", (1, 5)),
                         Piece("pawn", "white", (1, 6)), Piece("pawn", "white", (1, 7))],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [Piece("pawn", "black", (6, 0)), Piece("pawn", "black", (6, 1)), Piece("pawn", "black", (6, 2)),
                         Piece("pawn", "black", (6, 3)), Piece("pawn", "black", (6, 4)), Piece("pawn", "black", (6, 5)),
                         Piece("pawn", "black", (6, 6)), Piece("pawn", "black", (6, 7))],
                        [Piece("rook", "black", (7, 0)), Piece("knight", "black", (7, 1)), Piece("bishop", "black", (7, 2)),
                         Piece("king", "black", (7, 3)), Piece("queen", "black", (7, 4)), Piece("bishop", "black", (7, 5)),
                         Piece("knight", "black", (7, 6)), Piece("rook", "black", (7, 7))]]
        
        created_class = self.board.create_class(self.json_board)
        for row in range(ROWS):
            for col in range(COLS):
                if self.json_board[row][col] != " ":
                    self.assertEqual(created_class[row][col].piece, result_board[row][col].piece)
                    self.assertEqual(created_class[row][col].player, result_board[row][col].player)
                    self.assertEqual(created_class[row][col].row, result_board[row][col].row)
                    self.assertEqual(created_class[row][col].column, result_board[row][col].column)
                else:
                    self.assertEqual(created_class[row][col], result_board[row][col])

class Create_class(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["R", "N", "B", "K", "Q", "B", "N", "R"],
                          ["P", "P", "P", "P", "P", "P", "P", "P"],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          ["p", "p", "p", "p", "p", "p", "p", "p"],
                          ["r", "n", "b", "k", "q", "b", "n", "r"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_class(self):
        """Examine the correctness of the create_class function"""
        result_board = [[Piece("rook", "white", (0, 0)), Piece("knight", "white", (0, 1)), Piece("bishop", "white", (0, 2)),
                         Piece("king", "white", (0, 3)), Piece("queen", "white", (0, 4)), Piece("bishop", "white", (0, 5)),
                         Piece("knight", "white", (0, 6)), Piece("rook", "white", (0, 7))],
                        [Piece("pawn", "white", (1, 0)), Piece("pawn", "white", (1, 1)), Piece("pawn", "white", (1, 2)),
                         Piece("pawn", "white", (1, 3)), Piece("pawn", "white", (1, 4)), Piece("pawn", "white", (1, 5)),
                         Piece("pawn", "white", (1, 6)), Piece("pawn", "white", (1, 7))],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [Piece("pawn", "black", (6, 0)), Piece("pawn", "black", (6, 1)), Piece("pawn", "black", (6, 2)),
                         Piece("pawn", "black", (6, 3)), Piece("pawn", "black", (6, 4)), Piece("pawn", "black", (6, 5)),
                         Piece("pawn", "black", (6, 6)), Piece("pawn", "black", (6, 7))],
                        [Piece("rook", "black", (7, 0)), Piece("knight", "black", (7, 1)), Piece("bishop", "black", (7, 2)),
                         Piece("king", "black", (7, 3)), Piece("queen", "black", (7, 4)), Piece("bishop", "black", (7, 5)),
                         Piece("knight", "black", (7, 6)), Piece("rook", "black", (7, 7))]]
        
        created_class = self.board.create_class(self.json_board)
        for row in range(ROWS):
            for col in range(COLS):
                if self.json_board[row][col] != " ":
                    self.assertEqual(created_class[row][col].piece, result_board[row][col].piece)
                    self.assertEqual(created_class[row][col].player, result_board[row][col].player)
                    self.assertEqual(created_class[row][col].row, result_board[row][col].row)
                    self.assertEqual(created_class[row][col].column, result_board[row][col].column)
                else:
                    self.assertEqual(created_class[row][col], result_board[row][col])

class Add_moves1(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "P"],
                          [" ", "P", " ", " ", " ", " ", " ", " "],
                          [" ", "k", " ", " ", " ", " ", " ", " "]]
        cls.turn = "black"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_add_moves1(self):
        possible_moves = [[(set(), set(), False), None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, (set(), set(), False)],
                          [None, (set(), set(), True), None, None, None, None, None, None],
                          [None, ({(6, 0), (6, 2)}, {(6, 1)}, False), None, None, None, None, None, None]]
        """Examine the correctness of the add_moves function - test 1"""
        test_moves = self.board.add_moves()
        moves, winner, checking = test_moves

        new_moves = [[None] * ROWS for _ in range(COLS)]
        for row in range(ROWS):
            for col in range(COLS):
                if moves[row][col]:
                    new_moves[row][col] = (set(moves[row][col][0]), set(moves[row][col][1]), moves[row][col][2])

        self.assertEqual(new_moves, possible_moves)
        self.assertEqual(winner, None)
        self.assertEqual(checking, None)

class Add_moves2(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "R"],
                          [" ", "k", " ", " ", " ", " ", "R", " "]]
        cls.turn = "black"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_add_moves2(self):
        possible_moves = [[(set(), set(), False), None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, (set(), set(), False)],
                          [None, (set(), set(), False), None, None, None, None, (set(), set(), False), None]]
        """Examine the correctness of the add_moves function - test 2"""
        test_moves = self.board.add_moves()
        moves, winner, checking = test_moves

        new_moves = [[None] * ROWS for _ in range(COLS)]
        for row in range(ROWS):
            for col in range(COLS):
                if moves[row][col]:
                    new_moves[row][col] = (set(moves[row][col][0]), set(moves[row][col][1]), moves[row][col][2])

        self.assertEqual(new_moves, possible_moves)
        self.assertEqual(winner, "white")
        self.assertEqual(checking, [(7, 6)])

class Add_moves3(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          ["P", " ", " ", " ", " ", " ", " ", "R"],
                          ["k", " ", " ", " ", " ", " ", " ", " "]]
        cls.turn = "black"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_add_moves3(self):
        possible_moves = [[(set(), set(), False), None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [None, None, None, None, None, None, None, None],
                          [(set(), set(), True), None, None, None, None, None, None, (set(), set(), False)],
                          [(set(), set(), False), None, None, None, None, None, None , None]]
        """Examine the correctness of the add_moves function - test 3"""
        test_moves = self.board.add_moves()
        moves, winner, checking = test_moves

        for row in range(ROWS):
            for col in range(COLS):
                if moves[row][col]:
                    moves[row][col] = (set(moves[row][col][0]), set(moves[row][col][1]), moves[row][col][2])

        self.assertEqual(moves, possible_moves)
        self.assertEqual(winner, "draw")
        self.assertEqual(checking, None)

class Create_json_class(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["R", "N", "B", "K", "Q", "B", "N", "R"],
                          ["P", "P", "P", "P", "P", "P", "P", "P"],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          ["p", "p", "p", "p", "p", "p", "p", "p"],
                          ["r", "n", "b", "k", "q", "b", "n", "r"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"
        cls.checking = None

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_json_class(self):
        """Examine the correctness of the test_create_json_class function"""
        result_board = [[{'piece': 'rook', 'player': 'white', 'moves': (set(), set(), False)}, {'piece': 'knight', 'player': 'white', 'moves': ({(2, 2), (2, 0)}, set(), False)},
                         {'piece': 'bishop', 'player': 'white', 'moves': (set(), set(), False)}, {'piece': 'king', 'player': 'white', 'moves': (set(), set(), False)},
                         {'piece': 'queen', 'player': 'white', 'moves': (set(), set(), False)}, {'piece': 'bishop', 'player': 'white', 'moves': (set(), set(), False)},
                         {'piece': 'knight', 'player': 'white', 'moves': ({(2, 7), (2, 5)}, set(), False)}, {'piece': 'rook', 'player': 'white', 'moves': (set(), set(), False)}],
                        [{'piece': 'pawn', 'player': 'white', 'moves': ({(2, 0), (3, 0)}, set(), False)}, {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 1), (3, 1)}, set(), False)},
                         {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 2), (3, 2)}, set(), False)}, {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 3), (3, 3)}, set(), False)},
                         {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 4), (3, 4)}, set(), False)}, {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 5), (3, 5)}, set(), False)},
                         {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 6), (3, 6)}, set(), False)}, {'piece': 'pawn', 'player': 'white', 'moves': ({(2, 7), (3, 7)}, set(), False)}],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [None, None, None, None, None, None, None, None],
                        [{'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)},
                         {'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)},
                         {'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)},
                         {'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'pawn', 'player': 'black', 'moves': (set(), set(), False)}],
                        [{'piece': 'rook', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'knight', 'player': 'black', 'moves': (set(), set(), False)},
                         {'piece': 'bishop', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'king', 'player': 'black', 'moves': (set(), set(), False)},
                         {'piece': 'queen', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'bishop', 'player': 'black', 'moves': (set(), set(), False)},
                         {'piece': 'knight', 'player': 'black', 'moves': (set(), set(), False)}, {'piece': 'rook', 'player': 'black', 'moves': (set(), set(), False)}]]
        
        json_class, winner, checking = self.board.create_json_class()
        for row in range(ROWS):
            for col in range(COLS):
                if self.json_board[row][col] != " ":
                    json_class[row][col]['moves'] = (set(json_class[row][col]['moves'][0]), set(json_class[row][col]['moves'][1]), json_class[row][col]['moves'][2])

        self.assertEqual((json_class, winner, checking), (result_board, None, None))

class NewJsonBoard1(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "k"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_new_json_board1(self):
        """Examine the correctness of the create_new_json_board function - test 1"""
        new_board = [[" ", " ", " ", " ", " ", " ", " ", " "],
                     ["K", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", "k"]]

        self.assertEqual(self.board.create_new_json_board([[0, 0], [1, 0]], False), (new_board, "____", "__", True))

class NewJsonBoard2(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "r"],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "k"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_new_json_board2(self):
        """Examine the correctness of the create_new_json_board function - test 2"""
        self.assertEqual(self.board.create_new_json_board([[0, 0], [1, 0]], False), (False))

class NewJsonBoard3(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          ["P", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "k"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_new_json_board3(self):
        """Examine the correctness of the create_new_json_board function - test 3"""
        new_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     ["P", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", "k"]]

        self.assertEqual(self.board.create_new_json_board([[1, 0], [3, 0]], False), (new_board, "____", "20", False))

class NewJsonBoard4(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          ["P", "p", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "k"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "51"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_new_json_board4(self):
        """Examine the correctness of the create_new_json_board function - test 4"""
        new_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", "P", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", "k"]]

        self.assertEqual(self.board.create_new_json_board([[4, 0], [5, 1]], False), (new_board, "____", "__", False))

class NewJsonBoard5(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["R", " ", " ", "K", " ", " ", " ", "R"],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "k"]]
        cls.turn = "white"
        cls.castling = "KQkq"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_new_json_board5(self):
        """Examine the correctness of the create_new_json_board function - test 5"""
        new_board = [[" ", " ", " ", "K", " ", " ", " ", "R"],
                     ["R", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", "k"]]

        self.assertEqual(self.board.create_new_json_board([[0, 0], [1, 0]], False), (new_board, "_Qkq", "__", True))

class NewJsonBoard6(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["R", " ", " ", "K", " ", " ", " ", "R"],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "k"]]
        cls.turn = "white"
        cls.castling = "KQkq"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_new_json_board6(self):
        """Examine the correctness of the create_new_json_board function - test 6"""
        new_board = [["R", " ", " ", " ", " ", " ", " ", "R"],
                     [" ", " ", " ", "K", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", "k"]]

        self.assertEqual(self.board.create_new_json_board([[0, 3], [1, 3]], False), (new_board, "__kq", "__", True))

class NewJsonBoard789(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.json_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", " "],
                          ["P", " ", " ", " ", " ", " ", " ", " "],
                          [" ", " ", " ", " ", " ", " ", " ", "k"]]
        cls.turn = "white"
        cls.castling = "____"
        cls.enpassant = "__"

        cls.board = Board(cls.json_board, cls.turn, cls.castling, cls.enpassant)
    
    def test_create_new_json_board7(self):
        """Examine the correctness of the create_new_json_board function - test 7"""
        new_board = [["K", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     [" ", " ", " ", " ", " ", " ", " ", " "],
                     ["Q", " ", " ", " ", " ", " ", " ", "k"]]

        self.assertEqual(self.board.create_new_json_board([[6, 0], [7, 0]], "Q"), (new_board, "____", "__", False))
    
    def test_create_new_json_board8(self):
        """Examine the correctness of the create_new_json_board function - test 8"""
        self.assertEqual(self.board.create_new_json_board([[6, 0], [7, 0]], False), (False))

    def test_create_new_json_board9(self):
        """Examine the correctness of the create_new_json_board function - test 9"""
        self.assertEqual(self.board.create_new_json_board([[6, 0], [7, 0]], "q"), (False))


if __name__ == '__main__':
    unittest.main()