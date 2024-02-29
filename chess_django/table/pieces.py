class Piece:
    def __init__(self, piece, player, location):
        self.piece = piece
        self.player = player
        self.row, self.column = location

    def _is_valid_position(self, row, column):
        # Check if the given row and column are within the bounds of the board
        return 0 <= row < 8 and 0 <= column < 8

    def check_possible_moves(self, board):
        # Initialize lists to store possible moves and attacks
        moves = []
        attacks = []

        if self.piece == "pawn":
            # Determine the direction of movement based on the player's color
            direction_by_colour = 1 if self.player == "white" else -1
            # Possible movement directions for a pawn
            directions = [(direction_by_colour, 0)]
            # Allow moving two steps forward if the pawn hasn't moved yet
            if self.player == "white" and self.row == 1 or self.player == "black" and self.row == 6:
                directions.append((direction_by_colour * 2, 0))

            # Check for forward movements
            can_move_second_time = True
            for direction in directions:
                new_row = self.row + direction[0]
                new_column = self.column + direction[1]
                # Check if the new position is valid and empty
                if self._is_valid_position(new_row, new_column) and board[new_row][new_column] is None and can_move_second_time:
                    moves.append((new_row, new_column))
                else:
                    can_move_second_time = False

            # Check for diagonal attacks
            directions = [(direction_by_colour, 1), (direction_by_colour, -1)]
            for direction in directions:
                new_row = self.row + direction[0]
                new_column = self.column + direction[1]
                # Check if the new position is valid and contains an opponent's piece
                if self._is_valid_position(new_row, new_column) and board[new_row][new_column] is not None and board[new_row][new_column].player is not self.player:
                    attacks.append((new_row, new_column))

        elif self.piece in ["rook", "bishop", "queen"]:
            # Possible movement directions for rooks, bishops, and queens
            if self.piece == "rook":
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            elif self.piece == "bishop":
                directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            elif self.piece == "queen":
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            # Check for possible moves and attacks in each direction until blocked
            for direction in directions:
                distance = 1
                while True:
                    new_row = self.row + distance * direction[0]
                    new_column = self.column + distance * direction[1]
                    # Check if the new position is valid
                    if not self._is_valid_position(new_row, new_column):
                        break
                    # If the position is not empty, check if it's an opponent's piece
                    if board[new_row][new_column] is not None:
                        if board[new_row][new_column].player is not self.player:
                            attacks.append(((new_row, new_column)))
                        break
                    moves.append((new_row, new_column))
                    distance += 1

        elif self.piece in ["knight", "king"]:
            # Possible movement directions for knights and kings
            if self.piece == "knight":
                directions = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
            elif self.piece == "king":
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            # Check for possible moves and attacks in each direction
            for direction in directions:
                new_row = self.row + direction[0]
                new_column = self.column + direction[1]
                # Check if the new position is valid
                if self._is_valid_position(new_row, new_column):
                    # If the position is empty, it's a possible move, otherwise, it might be an attack
                    if board[new_row][new_column] is None:
                        moves.append((new_row, new_column))
                    elif board[new_row][new_column].player is not self.player:
                        attacks.append((new_row, new_column))

        # Return the lists of possible moves and attacks
        return (moves, attacks)


# initiate new board
    
board = [["R", "N", "B", "K", "Q", "B", "N", "R"],
         ["P", "P", "P", "P", "P", "P", "P", "P"],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         [" ", " ", " ", " ", " ", " ", " ", " "],
         ["p", "p", "p", "p", "p", "p", "p", "p"],
         ["r", "n", "b", "k", "q", "b", "n", "r"]]

board_piece = {
    "R": {"piece": "rook", "player": "white"},
    "N": {"piece": "knight", "player": "white"},
    "B": {"piece": "bishop", "player": "white"},
    "K": {"piece": "king", "player": "white"},
    "Q": {"piece": "queen", "player": "white"},
    "P": {"piece": "pawn", "player": "white"},
    "r": {"piece": "rook", "player": "black"},
    "n": {"piece": "knight", "player": "black"},
    "b": {"piece": "bishop", "player": "black"},
    "k": {"piece": "king", "player": "black"},
    "q": {"piece": "queen", "player": "black"},
    "p": {"piece": "pawn", "player": "black"}
}

curr_board = [[None for _ in range(8)] for _ in range(8)]

ROWS = 8
COLS = 8

for row in range(ROWS):
    for col in range(COLS):
        if board[row][col] in board_piece:
            piece = board_piece[board[row][col]]["piece"]
            player = board_piece[board[row][col]]["player"]
            curr_board[row][col] = Piece(piece, player, (row, col))


# curr_board[3][1] = Piece("knight","black", (3,1))