class Piece:
    def __init__(self, piece, player, location):
        self.piece = piece
        self.player = player
        self.row, self.column = location

    def _is_valid_position(self, row, column):
        # Check if the given row and column are within the bounds of the board
        return 0 <= row < 8 and 0 <= column < 8

    def check_piece_possible_moves(self, class_board):
        # Initialize lists to store possible moves and attacks
        moves = []
        attacks = []
        # [[location of checking piece][extra location to prevent check]]
        check = []
        # [[location of pinned piece][extra location that piece can still move]]
        pin = []

        board = class_board.board
        opponent_king = class_board.white_king if class_board.turn == "white" else class_board.black_king

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
                    # Check whether the current piece is putting the opponent's king in check
                    if (new_row, new_column) == opponent_king:
                        check.append([(self.row, self.column)], [])

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
                curr_direction = []
                absolute_pin_check = False
                while True:
                    new_row = self.row + distance * direction[0]
                    new_column = self.column + distance * direction[1]
                    # Check if the new position is valid
                    if not self._is_valid_position(new_row, new_column):
                        break
                    # If the position is not empty, check if it's an opponent's piece
                    if board[new_row][new_column] is not None:
                        if board[new_row][new_column].player is not self.player and not absolute_pin_check:
                            attacks.append(((new_row, new_column)))
                            # Check whether the current piece is putting the opponent's king in check
                            if (new_row, new_column) == opponent_king:
                                check.append([(self.row, self.column), curr_direction])
                                break
                            # Check if the current piece is putting the attacked piece in absolute pin
                            absolute_pin_check = True
                        elif absolute_pin_check:
                            if (new_row, new_column) == opponent_king:
                                pin.append([(attacks[-1]), curr_direction])
                            break
                        else:
                            break
                    moves.append((new_row, new_column))
                    curr_direction.append((new_row, new_column))
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
                        # Check whether the current piece is putting the opponent's king in check
                        if (new_row, new_column) == opponent_king:
                            check.append([(self.row, self.column), []])

        # Return the lists of possible moves and attacks
        return (moves, attacks)

class Board:
    def __init__(self, json_board, turn):
        self.ROWS, self.COLS = 8, 8
        self.turn = turn
        self.json_board = json_board
        self.board, self.white_king, self.black_king = self.create_class(json_board)
        self.add_moves()

    def create_class(self, board):
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

        class_board = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if board[row][col] in board_piece:
                    piece = board_piece[board[row][col]]["piece"]
                    player = board_piece[board[row][col]]["player"]
                    class_board[row][col] = Piece(piece, player, (row, col))
                    if piece == "king" and player == "white":
                        white_king_position = (row, col)
                    if piece == "king" and player == "black":
                        black_king_position = (row, col)
        
        return class_board, white_king_position, black_king_position
    
    def add_moves(self):
        possible_moves = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]
        opponents_attacks = set()
        
        for row in range(self.ROWS):
            for col in range(self.COLS):
                curr_piece = self.board[row][col]
                if curr_piece and curr_piece.player != self.turn:
                    possible_moves = curr_piece.check_piece_possible_moves(self)
                    # flatting
                    if curr_piece.piece == "pawn":
                        for position in possible_moves[1]:
                            opponents_attacks.add(position)
                    else:
                        for type in possible_moves:
                            for position in type:
                                opponents_attacks.add(position)

        # print(opponents_attacks)
        pass

    def create_json_class(self):
        json_class = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]

        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.board[row][col]:
                    json_class[row][col] = {
                        "piece": self.board[row][col].piece, 
                        "player": self.board[row][col].player,
                        "moves": self.board[row][col].check_piece_possible_moves(self)
                        }

        return json_class


    def create_new_json_board(self, move):
        old_position_row, old_position_col = move[0]
        new_position_row, new_position_col = move[1]

        possible_moves = self.board[old_position_row][old_position_col].check_piece_possible_moves(self)
        new_position = (new_position_row, new_position_col)

        if new_position in possible_moves[0] or new_position in possible_moves[1]:
            new_json_board = self.json_board
            new_json_board[new_position_row][new_position_col] = new_json_board[old_position_row][old_position_col]
            new_json_board[old_position_row][old_position_col] = None

            return new_json_board, True