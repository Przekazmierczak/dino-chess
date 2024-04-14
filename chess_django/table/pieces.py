class Piece:
    def __init__(self, piece, player, location):
        # Define the dimensions of the chessboard
        self.ROWS, self.COLS = 8, 8
        # Initialize attributes for the piece type, player, and location
        self.piece = piece
        self.player = player
        self.row, self.column = location

    def _is_valid_position(self, row, column):
        # Check if the given row and column are within the bounds of the board
        return 0 <= row < self.ROWS and 0 <= column < self.COLS
    
    def _is_not_pinned(self, piece_position, move, class_board, pinned_pieces):
        # Check if the piece is not pinned, considering the current board state and pinned pieces
        return (self.player != class_board.turn 
                or piece_position not in pinned_pieces 
                or (piece_position in pinned_pieces and move in pinned_pieces[piece_position]))
    
    def _flatting_checkin_pieces(self, checkin_pieces):
        # Flatten the dictionary of checking pieces into a set of positions
        checking_positions = set()
        # If there is only one key in the dictionary - if more moving the king is the only option available
        if len(checkin_pieces) == 1:
            for key in checkin_pieces:
                checking_positions.add(key)
                for value in checkin_pieces[key]:
                    checking_positions.add(value)
        return checking_positions

    def check_piece_possible_moves(self, class_board, attacked_positions, checkin_pieces, pinned_pieces, castling, enpassant):
        # Initialize lists to store possible moves and attacks, and promotion status
        moves = []
        attacks = []
        promotion = False

        # Get the current state of the chessboard
        board = class_board.board
        # Identify whose turn it is now
        opponent = True if class_board.turn != self.player else False

        # Flatten the dictionary of checking pieces into a set of positions
        checking_positions = self._flatting_checkin_pieces(checkin_pieces)

        if self.piece == "pawn":
            # Determine the direction of movement based on the player's color
            direction_by_colour = 1 if self.player == "white" else -1
            # Possible movement directions for a pawn
            directions = [(direction_by_colour, 0)]
            # Allow moving two steps forward if the pawn hasn't moved yet
            if self.player == "white" and self.row == 1 or self.player == "black" and self.row == 6:
                directions.append((direction_by_colour * 2, 0))
            
            # Check if the move will create a promotion
            if self.player == "white" and self.row == 6 or self.player == "black" and self.row == 1:
                promotion = True

            # OPPONENT
            if opponent:
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
                    # Add location to the attacked positions
                    if self._is_valid_position(new_row, new_column):
                        attacked_positions.add((new_row, new_column))
            
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
                    
                    # Check if en passant is possible
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

            # OPPONENT
            if opponent:
                # Check for possible moves and attacks in each direction until blocked
                for direction in directions:
                    distance = 1 # Starting distance
                    current_direction = [] # Stores the current direction of movement for checking purposes
                    absolute_pin_check = False # Continue checking in case the next attacked piece is the opponent's king; if it is, then the piece is in an absolute pin
                    king_check = False # If the attacked piece is the opponent's king, continue once more to prevent its movement along the attacked line
                    while True:
                        new_row = self.row + distance * direction[0]
                        new_column = self.column + distance * direction[1]
                        # Check if the new position is valid
                        if not self._is_valid_position(new_row, new_column):
                            break
                        # If the position is not empty, check if it's an opponent's piece
                        if board[new_row][new_column] is not None:
                            if board[new_row][new_column].player is not self.player and not absolute_pin_check and not king_check:
                                # Record pinned piece position
                                pinned_piece = (new_row, new_column)
                                # Add location to the attacked positions
                                attacked_positions.add((new_row, new_column))
                                # Check whether the current piece is putting the opponent's king in check
                                if board[new_row][new_column].piece == "king" and board[new_row][new_column].player is not self.player:
                                    checkin_pieces[(self.row, self.column)] = current_direction
                                    king_check = True
                                # Check if the current piece is putting the attacked piece in absolute pin
                                else:
                                    absolute_pin_check = True
                            # If the attacked location is occupied by a self piece, add the attack position and break
                            elif board[new_row][new_column].player is self.player and not absolute_pin_check and not king_check:
                                attacked_positions.add((new_row, new_column))
                                break
                            # If the next piece behind the attacked opponent's piece is his king, the attacked piece is absolutely pinned
                            elif absolute_pin_check:
                                if board[new_row][new_column].piece == "king" and board[new_row][new_column].player is not self.player:
                                    pinned_pieces[pinned_piece] = [(self.row, self.column)] + current_direction
                                break
                            else:
                                break
                        else:
                            if not absolute_pin_check and not king_check:
                                # Add to opponent's attacks set
                                attacked_positions.add((new_row, new_column))
                            if king_check:
                                # Add to opponent's attacks set
                                attacked_positions.add((new_row, new_column))
                                break
                            current_direction.append((new_row, new_column))
                        distance += 1
            
            # PLAYER
            else:
                # Check for possible moves and attacks in each direction until blocked
                for direction in directions:
                    distance = 1 # Starting distance
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

            # OPPONENT
            if opponent:
                # Check for possible moves and attacks in each direction
                for direction in directions:
                    new_row = self.row + direction[0]
                    new_column = self.column + direction[1]
                    # Check if the new position is valid
                    if self._is_valid_position(new_row, new_column):
                        if self.piece == "knight":
                            # If the position is empty, it's a possible move, otherwise, it might be an attack
                            if board[new_row][new_column] is None:
                                attacked_positions.add((new_row, new_column))
                            elif board[new_row][new_column].player is not self.player:
                                attacked_positions.add((new_row, new_column))
                                # Check whether the current piece is putting the opponent's king in check
                                if board[new_row][new_column].piece == "king" and board[new_row][new_column].player is not self.player:
                                    checkin_pieces[(self.row, self.column)] = []
                        
                        elif self.piece == "king":
                            # Skip castling
                            if direction == (0, -2) or direction == (0, 2):
                                continue
                            # If the position is empty, it's a possible move, otherwise, it might be an attack
                            attacked_positions.add((new_row, new_column))
            
            # PLAYER
            else:
                # Check for possible moves and attacks in each direction
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
                                # Check if neither the king nor the rook has previously moved and there are no pieces between the king and the rook
                                if (self.player == "white" and castling[0] == "K") or (self.player == "black" and castling[2] == "k"):
                                    # Check if the king is not currently in check and does not pass through or finish on a square that is attacked by an enemy piece
                                    if (not checking_positions
                                        and board[self.row][1] == None and board[self.row][2] == None
                                        and (self.row, 1) not in attacked_positions and (self.row, 2) not in attacked_positions):
                                            moves.append((new_row, new_column))
                            elif direction == (0, 2):
                                # Check if neither the king nor the rook has previously moved and there are no pieces between the king and the rook
                                if (self.player == "white" and castling[1] == "Q") or (self.player == "black" and castling[3] == "q"):
                                    # Check if the king is not currently in check and does not pass through or finish on a square that is attacked by an enemy piece
                                    if (not checking_positions
                                        and board[self.row][4] == None and board[self.row][5] == None and board[self.row][6] == None
                                        and (self.row, 4) not in attacked_positions and (self.row, 5) not in attacked_positions):
                                            moves.append((new_row, new_column))

                            # If the position is empty, it's a possible move, otherwise, it might be an attack
                            elif board[new_row][new_column] is None:
                                # Check if the king is not moving to attacked position
                                if (new_row, new_column) not in attacked_positions:
                                    moves.append((new_row, new_column))
                            elif board[new_row][new_column].player is not self.player:
                                # Check if the king is not attacking attacked position
                                if (new_row, new_column) not in attacked_positions:
                                    attacks.append((new_row, new_column))

        # Return the lists of possible moves and attacks
        return moves, attacks, promotion

class Board:
    def __init__(self, json_board, turn, castling, enpassant):
        # Define the dimensions of the chessboard
        self.ROWS, self.COLS = 8, 8

        self.turn = turn
        self.castling = castling
        self.enpassant = self.unpack_db(enpassant)

        self.json_board = json_board
        self.board = self.create_class(json_board)
        self.moves, self.winner, self.checking = self.add_moves()

    def unpack_db(self, value):
        if value == "__":
            return None
        else:
            row, col = int(value[0]), int(value[1])
            return (row, col)

    def create_class(self, board):
        # Dictionary to map the characters representing pieces to their respective properties
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

        # Initialize an empty 2D array to represent the chessboard
        class_board = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]
        
        # Iterate over each cell in the board
        for row in range(self.ROWS):
            for col in range(self.COLS):
                # Check if the current cell contains a piece
                if board[row][col] in board_piece:
                    # Retrieve the piece type and player color from the dictionary
                    piece = board_piece[board[row][col]]["piece"]
                    player = board_piece[board[row][col]]["player"]
                    # Create a Piece object with the retrieved information and place it on the board
                    class_board[row][col] = Piece(piece, player, (row, col))
        
        return class_board
    
    def add_moves(self):
        # Initialize an empty 2D array to store possible moves for each cell
        possible_moves = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]
        # Set to store positions under attack
        attacked_positions = set()
        # Dictionary to store positions of checking pieces and positions to prevent checking
        checkin_pieces = {}
        # Dictionary to store positions of pinned pieces and positions that pinned pieces still can move
        pinned_pieces = {}
        # Variable to determine if the game has ended
        end = True
        # Variable to store the winner of the game
        winner = None
        # Variable to store pieces that are checking the king
        mark_checking = None
        
        # Iterate over opponent's pieces
        for row in range(self.ROWS):
            for col in range(self.COLS):
                curr_piece = self.board[row][col]
                if curr_piece and curr_piece.player != self.turn:
                    # Calculate possible moves for opponent's pieces
                    possible_moves[row][col] = curr_piece.check_piece_possible_moves(self, attacked_positions, checkin_pieces, pinned_pieces, self.castling, self.enpassant)

        # Iterate over player's pieces
        for row in range(self.ROWS):
            for col in range(self.COLS):
                curr_piece = self.board[row][col]
                if curr_piece and curr_piece.player == self.turn:
                    # Calculate possible moves for player's pieces
                    possible_moves[row][col] = curr_piece.check_piece_possible_moves(self, attacked_positions, checkin_pieces, pinned_pieces, self.castling, self.enpassant)
                    # Check if the game can continue based on available moves for the player
                    if end:
                        moves, attacks, _ = possible_moves[row][col]
                        if moves or attacks:
                            end = False
        
        # Check if the game is finished
        if end:
            if checkin_pieces:
                winner = "white" if self.turn == "black" else "black"
            else:
                winner ="draw"
        
        # Check if any pieces are checking the king, then add them to the list
        if checkin_pieces:
            mark_checking = []
            for element in checkin_pieces:
                mark_checking.append(element)

        return possible_moves, winner, mark_checking

    def create_json_class(self):
        # Initialize an empty 2D array to store JSON representation of the board
        json_class = [[None for _ in range(self.ROWS)] for _ in range(self.COLS)]

        # Iterate over each cell on the board
        for row in range(self.ROWS):
            for col in range(self.COLS):
                # Check if there is a piece on the current cell
                if self.board[row][col]:
                    # Create a dictionary representing the piece with its attributes
                    json_class[row][col] = {
                        "piece": self.board[row][col].piece, # Piece type
                        "player": self.board[row][col].player, # Player color
                        "moves": self.moves[row][col] # Possible moves for the piece
                        }

        return json_class, self.winner, self.checking


    def create_new_json_board(self, move, promotion):
        # Extract old and new positions from the move
        old_position = tuple(move[0])
        new_position = tuple(move[1])

        old_position_row, old_position_col = old_position
        new_position_row, new_position_col = new_position

        # Extract possible moves, attacks, and promotions for the piece being move
        possible_moves, possible_attacks, possible_promotion = self.moves[old_position_row][old_position_col]
        enpassant = "__"

        new_json_board = self.json_board

        # Mark as correct if input is correct
        correct = False

        if (new_position in possible_moves or new_position in possible_attacks) and not possible_promotion:

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
                    new_json_board[old_position_row][0] = " "
                else:
                    new_json_board[old_position_row][4] = new_json_board[old_position_row][7]
                    new_json_board[old_position_row][7] = " "

            # Check if current move create enpassant possibility
            if self.board[old_position_row][old_position_col].piece == "pawn" and abs(old_position_row - new_position_row) == 2:
                enpassant_row = (old_position_row + new_position_row) // 2
                enpassant_col = old_position_col
                enpassant = str(enpassant_row) + str(enpassant_col)

            # Check if the current move is an en passant capture, then correctly remove the pawn
            if new_position == self.enpassant:
                if new_position_row == 2:
                    new_json_board[3][new_position_col] = " "
                else:
                    new_json_board[4][new_position_col] = " "

            # Move the piece to the new position on the board
            new_json_board[new_position_row][new_position_col] = new_json_board[old_position_row][old_position_col]
            new_json_board[old_position_row][old_position_col] = " "

            # Input is correct
            correct = True
        
        # Check if the move is valid and involves promotion
        elif (new_position in possible_moves or new_position in possible_attacks) and possible_promotion:
            # Check if the promotion is for the correct player and if the specified promotion is valid
            if (self.turn == "white" and promotion in ["Q", "R", "N", "B"]) or (self.turn == "black" and promotion in ["q", "r", "n", "b"]):

                # Promote the pawn to the specified piece type
                new_json_board[new_position_row][new_position_col] = promotion
                new_json_board[old_position_row][old_position_col] = " "

                # Input is correct
                correct = True
            
        # If the move is invalid or not made by the correct player, return False
        return (new_json_board, self.castling, enpassant) if correct else False