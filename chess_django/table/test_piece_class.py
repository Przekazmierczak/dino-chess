import unittest

from pieces import Piece

ROWS, COLS = 8, 8

class BasicMovements(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.board = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.turn, cls.opponents_attacks, cls.checkin_pieces, cls.pinned_pieces = "black", set(), {}, {}

        cls.pieces_positions = [("pawn", "white", (1, 0)), ("pawn", "white", (2, 4)), ("pawn", "white", (1, 6)),
                                ("pawn", "black", (6, 3)), ("pawn", "black", (5, 4)), ("pawn", "black", (6, 7)),
                                ("rook", "white", (0, 0)), ("rook", "white", (5, 7)), ("rook", "black", (7, 0)), ("rook", "black", (7, 4)),
                                ("knight", "white", (2, 0)), ("knight", "white", (6, 4)), ("knight", "black", (7, 1)), ("knight", "black", (5, 5)),
                                ("bishop", "white", (4, 1)), ("bishop", "black", (7, 2)), ("queen", "white", (4, 3)),
                                ("king", "white", (0, 4)), ("king", "black", (7, 3))]

        for piece_position in cls.pieces_positions:
            piece, player, position = piece_position
            row, col = position
            cls.board[row][col] = Piece(piece, player, (row, col))

    
    def get_moves(self, row, col):
        moves, attacks = self.board[row][col].check_piece_possible_moves(self, self.opponents_attacks, self.checkin_pieces, self.pinned_pieces)
        return (set(moves), set(attacks))

    def test_basic_movements_pawn_1_0(self):
        """Examine the movements of the pawn located on square (1, 0)."""
        self.assertEqual(self.get_moves(1, 0), (set(), set()))

    def test_basic_movements_pawn_2_3(self):
        """Examine the movements of the pawn located on square (2, 3)."""
        self.board[2][4].moved = True
        self.assertEqual(self.get_moves(2, 4), ({(3, 4)}, set()))

    def test_basic_movements_pawn_1_6(self):
        """Examine the movements of the pawn located on square (1, 6)."""
        self.assertEqual(self.get_moves(1, 6), ({(2, 6), (3, 6)}, set()))

    def test_basic_movements_pawn_6_3(self):
        """Examine the movements of the pawn located on square (6, 3)."""
        self.assertEqual(self.get_moves(6, 3), ({(5, 3)}, set()))

    def test_basic_movements_pawn_5_4(self):
        """Examine the movements of the pawn located on square (5, 4)."""
        self.board[5][4].moved = True
        self.assertEqual(self.get_moves(5, 4), ({(4, 4)}, {(4, 3)}))

    def test_basic_movements_pawn_6_7(self):
        """Examine the movements of the pawn located on square (6, 7)."""
        self.assertEqual(self.get_moves(6, 7), (set(), set()))

    def test_basic_movements_rook_0_0(self):
        """Examine the movements of the rook located on square (0, 0)."""
        self.assertEqual(self.get_moves(0, 0), ({(0, 1), (0, 2), (0, 3)}, set()))
        
    def test_basic_movements_rook_5_7(self):
        """Examine the movements of the rook located on square (5, 7)."""
        self.assertEqual(self.get_moves(5, 7), ({(4, 7), (3, 7), (2, 7), (1, 7), (0, 7), (5, 6)}, {(6, 7), (5, 5)}))

    def test_basic_movements_rook_7_0(self):
        """Examine the movements of the rook located on square (7, 0)."""
        self.assertEqual(self.get_moves(7, 0), ({(6, 0), (5, 0), (4, 0), (3, 0)}, {(2, 0)}))

    def test_basic_movements_rook_7_4(self):
        """Examine the movements of the rook located on square (7, 4)."""
        self.assertEqual(self.get_moves(7, 4), ({(7, 5), (7, 6), (7, 7)}, {(6, 4)}))

    def test_basic_movements_knight_2_0(self):
        """Examine the movements of the knight located on square (2, 0)."""
        self.assertEqual(self.get_moves(2, 0), ({(0, 1), (3, 2), (1, 2)}, set()))

    def test_basic_movements_knight_6_4(self):
        """Examine the movements of the knight located on square (6, 4)."""
        self.assertEqual(self.get_moves(6, 4), ({(4, 5), (7, 6), (5, 6), (5, 2)}, {(7,2)}))

    def test_basic_movements_knight_7_1(self):
        """Examine the movements of the knight located on square (7, 1)."""
        self.assertEqual(self.get_moves(7, 1), ({(5, 2), (5, 0)}, set()))

    def test_basic_movements_knight_5_5(self):
        """Examine the movements of the knight located on square (5, 5)."""
        self.assertEqual(self.get_moves(5, 5), ({(7, 6), (3, 6), (3, 4), (4, 7)}, {(4, 3)}))

    def test_basic_movements_bishop_4_1(self):
        """Examine the movements of the bishop located on square (4, 1)."""
        self.assertEqual(self.get_moves(4, 1), ({(5, 2), (5, 0), (3, 2), (2, 3), (1, 4), (0, 5), (3, 0)}, {(6, 3)}))
    
    def test_basic_movements_bishop_7_2(self):
        """Examine the movements of the bishop located on square (7, 2)."""
        self.assertEqual(self.get_moves(7, 2), ({(6, 1), (5, 0)}, set()))
    
    def test_basic_movements_queen_4_3(self):
        """Examine the movements of the queen located on square (4, 3)."""
        self.assertEqual(self.get_moves(4, 3), ({(5, 3), (3, 3), (2, 3), (1, 3), (0, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 2), (5, 2), (6, 1), (3, 4), (2, 5), (3, 2), (2, 1)},
                                                {(6, 3), (5, 4), (7, 0)}))

    def test_basic_movements_king_0_4(self):
        """Examine the movements of the bishop located on square (0, 4)."""
        self.assertEqual(self.get_moves(0, 4), ({(1, 4), (0, 5), (0, 3), (1, 5), (1, 3)}, set()))

    def test_basic_movements_king_7_3(self):
        """Examine the movements of the bishop located on square (6, 6)."""
        self.assertEqual(self.get_moves(7, 3), ({(6, 2)}, {(6, 4)}))

class BlockTheKing(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.board = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.possible_moves = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.turn, cls.opponents_attacks, cls.checkin_pieces, cls.pinned_pieces = "black", set(), {}, {}

        cls.pieces_positions = [("pawn", "white", (1, 2)), ("rook", "white", (1, 5)), ("knight", "white", (0, 5)), ("bishop", "white", (2, 6)),
                                ("queen", "white", (3, 7)), ("king", "white", (0, 0)), ("king", "black", (3, 4))]

        for piece_position in cls.pieces_positions:
            piece, player, position = piece_position
            row, col = position
            cls.board[row][col] = Piece(piece, player, (row, col))

        # Opponent
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player != cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)

        # Player
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player == cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)
    
    def get_moves(self, row, col):
        moves, attacks = self.board[row][col].check_piece_possible_moves(self, self.opponents_attacks, self.checkin_pieces, self.pinned_pieces)
        return (set(moves), set(attacks))

    def test_block_the_king_king_3_4(self):
        """Examine the movements of the king located on square (3, 4)."""
        self.assertEqual(self.get_moves(3, 4), ({(4, 3)}, set()))

class AbsolutePin(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.board = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.possible_moves = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.turn, cls.opponents_attacks, cls.checkin_pieces, cls.pinned_pieces = "black", set(), {}, {}

        cls.pieces_positions = [("pawn", "black", (2, 5)),
                                ("rook", "white", (3, 0)),
                                ("knight", "black", (3, 2)),
                                ("bishop", "white", (1, 6)),
                                ("bishop", "black", (5, 2)),
                                ("queen", "white", (7, 0)),
                                ("king", "white", (0, 0)),
                                ("king", "black", (3, 4))]

        for piece_position in cls.pieces_positions:
            piece, player, position = piece_position
            row, col = position
            cls.board[row][col] = Piece(piece, player, (row, col))

        # Opponent
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player != cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)

        # Player
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player == cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)
    
    def get_moves(self, row, col):
        moves, attacks = self.board[row][col].check_piece_possible_moves(self, self.opponents_attacks, self.checkin_pieces, self.pinned_pieces)
        return (set(moves), set(attacks))

    def test_absolute_pin_pawn_2_5(self):
        """Examine the movements of the pawn located on square (2, 5)."""
        self.assertEqual(self.get_moves(2, 5), (set(), {(1, 6)}))

    def test_absolute_pin_knight_3_2(self):
        """Examine the movements of the knight located on square (3, 2)."""
        self.assertEqual(self.get_moves(3, 2), (set(), set()))

    def test_absolute_pin_bishop_5_2(self):
        """Examine the movements of the bishop located on square (5, 2)."""
        self.assertEqual(self.get_moves(5, 2), ({(6, 1), (4, 3)}, {(7, 0)}))

class Check(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.board = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.possible_moves = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.turn, cls.opponents_attacks, cls.checkin_pieces, cls.pinned_pieces = "black", set(), {}, {}

        cls.pieces_positions = [("pawn", "black", (4, 0)),
                                ("pawn", "black", (4, 2)),
                                ("pawn", "black", (3, 7)),
                                ("rook", "black", (7, 5)),
                                ("knight", "black", (1, 2)),
                                ("bishop", "black", (1, 3)),
                                ("queen", "white", (3, 1)),
                                ("queen", "black", (7, 1)),
                                ("king", "white", (0, 0)),
                                ("king", "black", (3, 6))]

        for piece_position in cls.pieces_positions:
            piece, player, position = piece_position
            row, col = position
            cls.board[row][col] = Piece(piece, player, (row, col))

        # Opponent
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player != cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)

        # Player
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player == cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)
    
    def get_moves(self, row, col):
        moves, attacks = self.board[row][col].check_piece_possible_moves(self, self.opponents_attacks, self.checkin_pieces, self.pinned_pieces)
        return (set(moves), set(attacks))

    def test_check_pawn_4_0(self):
        """Examine the movements of the pawn located on square (4, 0)."""
        self.assertEqual(self.get_moves(4, 0), (set(), {(3, 1)}))

    def test_check_pawn_4_2(self):
        """Examine the movements of the pawn located on square (4, 2)."""
        self.assertEqual(self.get_moves(4, 2), ({(3, 2)}, {(3,1)}))

    def test_check_pawn_3_7(self):
        """Examine the movements of the pawn located on square (3, 7)."""
        self.assertEqual(self.get_moves(3, 7), (set(), set()))

    def test_check_rook_7_5(self):
        """Examine the movements of the rook located on square (7, 5)."""
        self.assertEqual(self.get_moves(7, 5), ({(3, 5)}, set()))

    def test_check_knight_1_2(self):
        """Examine the movements of the knight located on square (1, 2)."""
        self.assertEqual(self.get_moves(1, 2), ({(3, 3)}, {(3, 1)}))

    def test_check_bishop_1_3(self):
        """Examine the movements of the bishop located on square (1, 3)."""
        self.assertEqual(self.get_moves(1, 3), ({(3, 5)}, {(3, 1)}))

    def test_check_queen_7_1(self):
        """Examine the movements of the queen located on square (7, 1)."""
        self.assertEqual(self.get_moves(1, 3), ({(3, 5)}, {(3, 1)}))

    def test_check_king_3_6(self):
        """Examine the movements of the queen located on square (3, 6)."""
        self.assertEqual(self.get_moves(3, 6), ({(2, 5), (2, 6), (2, 7), (4, 5), (4, 6), (4, 7)}, set()))

class DoubleCheck(unittest.TestCase):

    # initiate test board
    @classmethod
    def setUpClass(cls):
        cls.board = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.possible_moves = [[None for _ in range(ROWS)] for _ in range(COLS)]
        cls.turn, cls.opponents_attacks, cls.checkin_pieces, cls.pinned_pieces = "black", set(), {}, {}

        cls.pieces_positions = [("pawn", "black", (4, 0)),
                                ("pawn", "black", (4, 2)),
                                ("pawn", "black", (3, 7)),
                                ("rook", "white", (0, 6)),
                                ("rook", "black", (7, 5)),
                                ("knight", "black", (1, 2)),
                                ("bishop", "black", (1, 3)),
                                ("queen", "white", (3, 1)),
                                ("queen", "black", (7, 1)),
                                ("king", "white", (0, 0)),
                                ("king", "black", (3, 6))]

        for piece_position in cls.pieces_positions:
            piece, player, position = piece_position
            row, col = position
            cls.board[row][col] = Piece(piece, player, (row, col))

        # Opponent
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player != cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)

        # Player
        for row in range(ROWS):
            for col in range(COLS):
                curr_piece = cls.board[row][col]
                if curr_piece and curr_piece.player == cls.turn:
                    cls.possible_moves[row][col] = cls.get_moves(cls, row, col)
    
    def get_moves(self, row, col):
        moves, attacks = self.board[row][col].check_piece_possible_moves(self, self.opponents_attacks, self.checkin_pieces, self.pinned_pieces)
        return (set(moves), set(attacks))

    def test_double_check_pawn_4_0(self):
        """Examine the movements of the pawn located on square (4, 0)."""
        self.assertEqual(self.get_moves(4, 0), (set(), set()))

    def test_double_check_pawn_4_2(self):
        """Examine the movements of the pawn located on square (4, 2)."""
        self.assertEqual(self.get_moves(4, 2), (set(), set()))

    def test_double_check_pawn_3_7(self):
        """Examine the movements of the pawn located on square (3, 7)."""
        self.assertEqual(self.get_moves(3, 7), (set(), set()))

    def test_double_check_rook_7_5(self):
        """Examine the movements of the rook located on square (7, 5)."""
        self.assertEqual(self.get_moves(7, 5), (set(), set()))

    def test_double_check_knight_1_2(self):
        """Examine the movements of the knight located on square (1, 2)."""
        self.assertEqual(self.get_moves(1, 2), (set(), set()))

    def test_double_check_bishop_1_3(self):
        """Examine the movements of the bishop located on square (1, 3)."""
        self.assertEqual(self.get_moves(1, 3), (set(), set()))

    def test_double_check_queen_7_1(self):
        """Examine the movements of the queen located on square (7, 1)."""
        self.assertEqual(self.get_moves(1, 3), (set(), set()))
        
    def test_check_king_3_6(self):
        """Examine the movements of the queen located on square (3, 6)."""
        self.assertEqual(self.get_moves(3, 6), ({(2, 5), (2, 7), (4, 5), (4, 7)}, set()))

if __name__ == '__main__':
    unittest.main()