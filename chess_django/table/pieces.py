class Piece:
    def __init__(self, piece, player, location):
        self.piece = piece
        self.player = player
        self.row, self.column = location
        self.moved = False

    def check_possible_moves(self, board):
        if self.piece == "pawn":
            if self.player == "white":
                directions = [(1, 0)]
                if self.moved == False:
                    directions.append((2, 0))
            if self.player == "black":
                directions = [(-1, 0)]
                if self.moved == False:
                    directions.append((-2, 0))

            moves = []
            attacks = []

            is_blocked = False
            for direction in directions:
                new_row = self.row + direction[0]
                new_column = self.column + direction[1]

                if new_row in range(0, 8) and new_column in range(0, 8) and board[new_row][new_column] is None and is_blocked == False:
                    moves.append((new_row, new_column))
                else:
                    is_blocked = True
            
            if self.player == "white":
                directions = [(1, 1), (1, -1)]
            if self.player == "black":
                directions = [(-1, 1), (-1, -1)]

            for direction in directions:
                new_row = self.row + direction[0]
                new_column = self.column + direction[1]

                if new_row in range(0, 8) and new_column in range(0, 8) and board[new_row][new_column] is not None and board[new_row][new_column].player != self.player:
                    attacks.append((new_row, new_column))

            return (moves, attacks)
        
        else:
            if self.piece == "rook":
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            elif self.piece == "bishop":
                directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            elif self.piece == "knight":
                directions = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
            elif self.piece == "queen" or self.piece == "king":
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

            moves = []
            attacks = []

            if self.piece == "rook" or self.piece == "bishop" or self.piece == "queen":
                for direction in directions:
                    distance = 1
                    while True:
                        new_row = self.row + distance * direction[0]
                        new_column = self.column + distance * direction[1]

                        if new_row not in range(0, 8) or new_column not in range(0, 8):
                            break

                        if board[new_row][new_column] is not None:
                            if board[new_row][new_column].player is not self.player:
                                attacks.append(((new_row, new_column)))
                            break

                        moves.append((new_row, new_column))
                        distance += 1

            if self.piece == "knight" or self.piece == "king":
                for direction in directions:
                    new_row = self.row + direction[0]
                    new_column = self.column + direction[1]

                    if new_row in range(0, 8) and new_column in range(0, 8):
                        if board[new_row][new_column] is None:
                            moves.append((new_row, new_column))
                        elif board[new_row][new_column].player is not self.player:
                            attacks.append((new_row, new_column))

            return (moves, attacks)

    

# initiate new board

curr_board = [[None for _ in range(8)] for _ in range(8)]

for player, row in [("white", 0), ("white", 1), ("black", 6), ("black", 7)]:
    if row == 0 or row == 7:
        for piece, columns in [("rook", [0, 7]), ("knight", [1, 6]), ("bishop", [2, 5]), ("queen", [3]), ("king", [4])]:
            for column in columns:
                curr_board[row][column] = Piece(piece, player, (row, column))
    else:
        for column in range(8):
            curr_board[row][column] = Piece("pawn", player, (row, column))

curr_board[4][1] = Piece("knight","black", (4,1))