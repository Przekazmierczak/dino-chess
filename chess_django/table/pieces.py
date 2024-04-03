class Piece:
    def __init__(self, piece, player, location):
        self.piece = piece
        self.player = player
        self.row, self.column = location

    def _is_valid_position(self, row, column):
        # Check if the given row and column are within the bounds of the board
        return 0 <= row < 8 and 0 <= column < 8
    
    def _is_not_pinned(self, piece_position, move, class_board, pinned_pieces):
        return (self.player != class_board.turn 
                or piece_position not in pinned_pieces 
                or (piece_position in pinned_pieces and move in pinned_pieces[piece_position]))
    
    def _flatting_checkin_pieces(self, checkin_pieces):
        checking_positions = set()
        if len(checkin_pieces) == 1:
            for key in checkin_pieces:
                checking_positions.add(key)
                for value in checkin_pieces[key]:
                    checking_positions.add(value)
        return checking_positions

    def check_piece_possible_moves(self, class_board, opponents_attacks, checkin_pieces, pinned_pieces, castling, enpassant):
        # Initialize lists to store possible moves and attacks
        moves = []
        attacks = []

        board = class_board.board
        opponent = True if class_board.turn != self.player else False

        checking_positions = self._flatting_checkin_pieces(checkin_pieces)

        if self.piece == "pawn":
            # Determine the direction of movement based on the player's color
            direction_by_colour = 1 if self.player == "white" else -1
            # Possible movement directions for a pawn
            directions = [(direction_by_colour, 0)]
            # Allow moving two steps forward if the pawn hasn't moved yet
            if self.player == "white" and self.row == 1 or self.player == "black" and self.row == 6:
                directions.append((direction_by_colour * 2, 0))

            # OPPONENT
            if opponent:
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
                    if self._is_valid_position(new_row, new_column) and board[new_row][new_column] is not None: 
                        if board[new_row][new_column].player is not self.player:
                            attacks.append((new_row, new_column))
                        # Check whether the current piece is putting the opponent's king in check
                        if board[new_row][new_column].piece == "king" and board[new_row][new_column].player is not self.player:
                            checkin_pieces[(self.row, self.column)] = []
                    if self._is_valid_position(new_row, new_column):
                        opponents_attacks.add((new_row, new_column))
            
            # PLAYER
            else:
                # Check for forward movements
                can_move_second_time = True
                for direction in directions:
                    new_row = self.row + direction[0]
                    new_column = self.column + direction[1]
                    # Check if the new position is valid and empty
                    if self._is_valid_position(new_row, new_column) and board[new_row][new_column] is None and can_move_second_time:
                        # Check whether the current piece is not absolute pinned
                        if self._is_not_pinned((self.row, self.column), (new_row, new_column), class_board, pinned_pieces):
                            # Check if player king is checked, if move protect the king
                            if not checkin_pieces or (new_row, new_column) in checking_positions:
                                moves.append((new_row, new_column))
                    else:
                        can_move_second_time = False

                # Check for diagonal attacks
                directions = [(direction_by_colour, 1), (direction_by_colour, -1)]
                for direction in directions:
                    new_row = self.row + direction[0]
                    new_column = self.column + direction[1]
                    # Check if the new position is valid and contains an opponent's piece
                    if self._is_valid_position(new_row, new_column) and board[new_row][new_column] is not None: 
                        # Check whether the current piece is not absolute pinned
                        if self._is_not_pinned((self.row, self.column), (new_row, new_column), class_board, pinned_pieces):
                            # Check if player king is checked, if move protect the king
                            if not checkin_pieces or (new_row, new_column) in checking_positions:
                                if board[new_row][new_column].player is not self.player:
                                    attacks.append((new_row, new_column))
                    
                    # Check enpassant
                    if self._is_valid_position(new_row, new_column) and (new_row, new_column) == enpassant:
                        # Check whether the current piece is not absolute pinned
                        if self._is_not_pinned((self.row, self.column), (new_row, new_column), class_board, pinned_pieces):
                            # Check if player king is checked, if move protect the king
                            if not checkin_pieces or (new_row, new_column) in checking_positions:
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
            # OPPONENT
            if opponent:
                for direction in directions:
                    distance = 1
                    curr_direction = []
                    absolute_pin_check = False
                    if_check = False
                    while True:
                        new_row = self.row + distance * direction[0]
                        new_column = self.column + distance * direction[1]
                        # Check if the new position is valid
                        if not self._is_valid_position(new_row, new_column):
                            break
                        # If the position is not empty, check if it's an opponent's piece
                        if board[new_row][new_column] is not None:
                            if board[new_row][new_column].player is not self.player and not absolute_pin_check and not if_check:
                                attacks.append(((new_row, new_column)))
                                opponents_attacks.add((new_row, new_column))
                                # Check whether the current piece is putting the opponent's king in check
                                if board[new_row][new_column].piece == "king" and board[new_row][new_column].player is not self.player:
                                    checkin_pieces[(self.row, self.column)] = curr_direction
                                    if_check = True
                                # Check if the current piece is putting the attacked piece in absolute pin
                                else:
                                    absolute_pin_check = True
                            # If the attacked location is occupied by a self piece, add the attack position and break.
                            elif board[new_row][new_column].player is self.player and not absolute_pin_check and not if_check:
                                opponents_attacks.add((new_row, new_column))
                                break
                            # If the next piece behind the attacked opponent's piece is his king, the attacked piece is absolutely pinned
                            elif absolute_pin_check:
                                if board[new_row][new_column].piece == "king" and board[new_row][new_column].player is not self.player:
                                    pinned_pieces[(attacks[-1])] = [(self.row, self.column)] + curr_direction
                                break
                            else:
                                break
                        else:
                            if not absolute_pin_check and not if_check:
                                moves.append((new_row, new_column))
                                # The current piece belongs to the opponent so add location to attacks
                                opponents_attacks.add((new_row, new_column))
                            if if_check:
                                # The current piece belongs to the opponent so add location to attacks
                                opponents_attacks.add((new_row, new_column))
                            if not if_check:
                                curr_direction.append((new_row, new_column))
                        distance += 1
            
            # PLAYER
            else:
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
                                # Check whether the current piece is not absolute pinned
                                if self._is_not_pinned((self.row, self.column), (new_row, new_column), class_board, pinned_pieces):
                                    # Check if player king is checked, if move protect the king
                                    if not checkin_pieces or (new_row, new_column) in checking_positions:
                                        attacks.append(((new_row, new_column)))
                            break
                        else:
                            # Check whether the current piece is not absolute pinned
                            if self._is_not_pinned((self.row, self.column), (new_row, new_column), class_board, pinned_pieces):
                                # Check if player king is checked, if move protect the king
                                if not checkin_pieces or (new_row, new_column) in checking_positions:
                                    moves.append((new_row, new_column))
                        distance += 1

        elif self.piece in ["knight", "king"]:
            # Possible movement directions for knights and kings
            if self.piece == "knight":
                directions = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
            elif self.piece == "king":
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, -2), (0, 2)]

            # Check for possible moves and attacks in each direction
            # OPPONENT
            if opponent:
                for direction in directions:
                    new_row = self.row + direction[0]
                    new_column = self.column + direction[1]
                    # Check if the new position is valid
                    if self._is_valid_position(new_row, new_column):
                        if self.piece == "knight":
                            # If the position is empty, it's a possible move, otherwise, it might be an attack
                            if board[new_row][new_column] is None:
                                moves.append((new_row, new_column))
                                # The current piece belongs to the opponent so add location to attacks
                                opponents_attacks.add((new_row, new_column))
                            elif board[new_row][new_column].player is not self.player:
                                attacks.append((new_row, new_column))
                                # The current piece belongs to the opponent so add location to attacks
                                opponents_attacks.add((new_row, new_column))
                                # Check whether the current piece is putting the opponent's king in check
                                if board[new_row][new_column].piece == "king" and board[new_row][new_column].player is not self.player:
                                    checkin_pieces[(self.row, self.column)] = []
                        elif self.piece == "king":
                            # Skip castling
                            if direction == (0, -2) or direction == (0, 2):
                                continue
                            # If the position is empty, it's a possible move, otherwise, it might be an attack
                            elif board[new_row][new_column] is None:
                                moves.append((new_row, new_column))
                            elif board[new_row][new_column].player is not self.player:
                                attacks.append((new_row, new_column))
            
            # PLAYER
            else:
                for direction in directions:
                    new_row = self.row + direction[0]
                    new_column = self.column + direction[1]
                    # Check if the new position is valid
                    if self._is_valid_position(new_row, new_column):
                        if self.piece == "knight":
                            # If the position is empty, it's a possible move, otherwise, it might be an attack
                            if board[new_row][new_column] is None:
                                # Check whether the current piece is not absolute pinned
                                if self._is_not_pinned((self.row, self.column), (new_row, new_column), class_board, pinned_pieces):
                                    # Check if player king is checked, if move protect the king
                                    if not checkin_pieces or (new_row, new_column) in checking_positions:
                                        moves.append((new_row, new_column))
                            elif board[new_row][new_column].player is not self.player:
                                # Check whether the current piece is not absolute pinned
                                if self._is_not_pinned((self.row, self.column), (new_row, new_column), class_board, pinned_pieces):
                                    # Check if player king is checked, if move protect the king
                                    if not checkin_pieces or (new_row, new_column) in checking_positions:
                                        attacks.append((new_row, new_column))
                        elif self.piece == "king":
                            # Castling
                            if direction == (0, -2):
                                if (self.player == "white" and castling[0] == "K") or (self.player == "black" and castling[2] == "k"):
                                    if (not checking_positions
                                        and board[self.row][1] == None and board[self.row][2] == None
                                        and (self.row, 1) not in opponents_attacks and (self.row, 2) not in opponents_attacks):
                                            moves.append((new_row, new_column))
                            elif direction == (0, 2):
                                if (self.player == "white" and castling[1] == "Q") or (self.player == "black" and castling[3] == "q"):
                                    if (not checking_positions
                                        and board[self.row][4] == None and board[self.row][5] == None and board[self.row][6] == None
                                        and (self.row, 4) not in opponents_attacks and (self.row, 5) not in opponents_attacks):
                                            moves.append((new_row, new_column))

                            # If the position is empty, it's a possible move, otherwise, it might be an attack
                            elif board[new_row][new_column] is None:
                                # Check if the king is not moving to attacked position
                                if (new_row, new_column) not in opponents_attacks:
                                    moves.append((new_row, new_column))
                            elif board[new_row][new_column].player is not self.player:
                                # Check if the king is not trying to attack attacked position
                                if (new_row, new_column) not in opponents_attacks:
                                    attacks.append((new_row, new_column))

        # Return the lists of possible moves and attacks
        return moves, attacks

class Board:
    def __init__(self, json_board, turn, castling, enpassant):
        self.ROWS, self.COLS = 8, 8
        self.turn = turn
        self.castling = castling
        
        if enpassant == "__":
            self.enpassant = None
        else:
            row, col = int(enpassant[0]), int(enpassant[1])
            self.enpassant = (row, col)

        self.json_board = json_board
        self.board = self.create_class(json_board)
        self.moves, self.winner = self.add_moves()

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
        
        return class_board
    
    def add_moves(self):
        possible_moves = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]
        opponents_attacks = set()
        # [[location of checking piece][extra location to prevent check]]
        checkin_pieces = {}
        # [[location of pinned piece][extra location that piece can still move]]
        pinned_pieces = {}
        end = True
        winner = None
        
        # Opponent
        for row in range(self.ROWS):
            for col in range(self.COLS):
                curr_piece = self.board[row][col]
                if curr_piece and curr_piece.player != self.turn:
                    possible_moves[row][col] = curr_piece.check_piece_possible_moves(self, opponents_attacks, checkin_pieces, pinned_pieces, self.castling, self.enpassant)

        # Player
        for row in range(self.ROWS):
            for col in range(self.COLS):
                curr_piece = self.board[row][col]
                if curr_piece and curr_piece.player == self.turn:
                    possible_moves[row][col] = curr_piece.check_piece_possible_moves(self, opponents_attacks, checkin_pieces, pinned_pieces, self.castling, self.enpassant)
                    if end:
                        moves, attacks = possible_moves[row][col]
                        if moves or attacks:
                            end = False
        
        # Check if the game is finished
        if end:
            if checkin_pieces:
                winner = "white" if self.turn == "black" else "black"
            else:
                winner ="draw"

        return possible_moves, winner

    def create_json_class(self):
        json_class = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]

        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.board[row][col]:
                    json_class[row][col] = {
                        "piece": self.board[row][col].piece, 
                        "player": self.board[row][col].player,
                        "moves": self.moves[row][col]
                        }

        return json_class, self.winner


    def create_new_json_board(self, move):
        old_position = tuple(move[0])
        new_position = tuple(move[1])

        old_position_row, old_position_col = old_position
        new_position_row, new_position_col = new_position

        possible_moves, possible_attacks = self.moves[old_position_row][old_position_col]


        if new_position in possible_moves or new_position in possible_attacks:
            new_json_board = self.json_board

            # Check if any castling options are left
            if self.castling != "____":
                # Convert the castling string to a list for manipulation
                castling_list = list(self.castling)

                # Define the starting positions of kings and rooks for castling
                starting_positions = {(0, 3): [0, 1], # The white king
                                      (7, 3): [2, 3], # The black king
                                      (0, 0): [0], # The white rook on the king side
                                      (0, 7): [1], # The white rook on the queen side
                                      (7, 0): [2], # The black rook on the king side
                                      (7, 7): [3]} # The black rook on the queen side
                
                # Combine old and new positions for comparison
                move_positions = [old_position, new_position]
                
                # Iterate through new and old positions
                for move_position in move_positions:
                    # Check if the move position corresponds to a starting position for castling
                    if move_position in starting_positions:
                        # Iterate through the indices corresponding to the castling options
                        for element in starting_positions[move_position]:
                            # Update the castling option to indicate that the rook or king has moved
                            castling_list[element] = "_"
                
                # Update the castling attribute with the modified list
                self.castling = castling_list[0] + castling_list[1] + castling_list[2] + castling_list[3]
            
            # Check if the current move is a castling, then correctly move the rook
            if self.board[old_position_row][old_position_col].piece == "king" and abs(old_position_col - new_position_col) > 1:
                if new_position_col == 1:
                    new_json_board[old_position_row][2] = new_json_board[old_position_row][0]
                    new_json_board[old_position_row][0] = None
                else:
                    new_json_board[old_position_row][4] = new_json_board[old_position_row][7]
                    new_json_board[old_position_row][7] = None

            # Check if current move create enpassant possibility
            if self.board[old_position_row][old_position_col].piece and self.board[old_position_row][old_position_col].piece == "pawn" and abs(old_position_row - new_position_row) == 2:
                enpassant_row = (old_position_row + new_position_row) // 2
                enpassant_col = old_position_col
                enpassant = str(enpassant_row) + str(enpassant_col)
            else:
                enpassant = "__"

            # Check if the current move is an en passant capture, then correctly remove the pawn
            if new_position == self.enpassant:
                if new_position_row == 2:
                    new_json_board[3][new_position_col] = None
                else:
                    new_json_board[4][new_position_col] = None
            
            new_json_board[new_position_row][new_position_col] = new_json_board[old_position_row][old_position_col]
            new_json_board[old_position_row][old_position_col] = None

            return new_json_board, self.castling, enpassant
        return False