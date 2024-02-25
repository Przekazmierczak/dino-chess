class Pawn:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False

    def check_possible_moves(self):
        direction = 1 if self.player == "white" else -1
        moves = []
        attacks = []

        move_by_one = self.row + direction

        if move_by_one in range(0, 7) and board[move_by_one][self.column] is None:
            moves.append((move_by_one, self.column))

            move_by_two = self.row + 2 * direction
            if not self.moved and move_by_two in range(0, 7) and board[move_by_two][self.column] is None:
                moves.append((move_by_two, self.column))

        attack_right = self.column + 1
        if move_by_one in range(0, 7) and attack_right in range(0, 7) and board[move_by_one][attack_right] is not None and board[move_by_one][attack_right].player != self.player:
            attacks.append((move_by_one, attack_right))
        
        attack_left = self.column - 1
        if move_by_one in range(0, 7) and attack_left in range(0, 7) and board[move_by_one][attack_right] is not None and board[move_by_one][attack_right].player != self.player:
            attacks.append((move_by_one, attack_left))

        return (moves, attacks)


class Rook:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False

    def check_possible_moves(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        moves = []
        attacks = []

        for direction in directions:
            distance = 1
            while True:
                new_row = self.row + distance * direction[0]
                new_column = self.column + distance * direction[1]

                if new_row not in range(0, 7) or new_column not in range(0, 7):
                    break

                if board[new_row][new_column] is not None:
                    if board[new_row][new_column].player is not self.player:
                        attacks.append(((new_row, new_column)))
                    break

                moves.append((new_row, new_column))
                distance += 1

        return (moves, attacks)
    

class Knight:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False
    
    def check_possible_moves(self):
        directions = [(2, 1), (-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
        moves = []
        attacks = []

        for direction in directions:
            new_row = self.row + direction[0]
            new_column = self.column + direction[1]

            if new_row in range(0, 7) and new_column in range(0, 7):
                if board[new_row][new_column] is None:
                    moves.append((new_row, new_column))
                elif board[new_row][new_column].player is not self.player:
                    attacks.append((new_row, new_column))

        return (moves, attacks)

class Bishop:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False
    
    def check_possible_moves(self):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        moves = []
        attacks = []

        for direction in directions:
            distance = 1
            while True:
                new_row = self.row + distance * direction[0]
                new_column = self.column + distance * direction[1]

                if new_row not in range(0, 7) or new_column not in range(0, 7):
                    break

                if board[new_row][new_column] is not None:
                    if board[new_row][new_column].player is not self.player:
                        attacks.append(((new_row, new_column)))
                    break

                moves.append((new_row, new_column))
                distance += 1

        return (moves, attacks)

class Queen:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False
    
    def check_possible_moves(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        moves = []
        attacks = []

        for direction in directions:
            distance = 1
            while True:
                new_row = self.row + distance * direction[0]
                new_column = self.column + distance * direction[1]

                if new_row not in range(0, 7) or new_column not in range(0, 7):
                    break

                if board[new_row][new_column] is not None:
                    if board[new_row][new_column].player is not self.player:
                        attacks.append(((new_row, new_column)))
                    break

                moves.append((new_row, new_column))
                distance += 1

        return (moves, attacks)

class King:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False

    def check_possible_moves(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        moves = []
        attacks = []

        for direction in directions:
            new_row = self.row + direction[0]
            new_column = self.column + direction[1]

            if new_row in range(0, 7) and new_column in range(0, 7):
                if board[new_row][new_column] is None:
                    moves.append((new_row, new_column))
                elif board[new_row][new_column].player is not self.player:
                    attacks.append((new_row, new_column))

        return (moves, attacks)
    

# initiate new board

board = [[None for _ in range(8)] for _ in range(8)]

for player, row in [("white", 0), ("white", 1), ("black", 6), ("black", 7)]:
    if row == 0 or row == 7:
        for piece, columns in [(Rook, [0, 7]), (Knight, [1, 6]), (Bishop, [2, 5]), (Queen, [3]), (King, [4])]:
            for column in columns:
                board[row][column] = piece(player, (row, column))
    else:
        for column in range(8):
            board[row][column] = Pawn(player, (row, column))

board[4][1] = Knight("black", (4,1))
# board[1][0] = None

print(board[0][3].check_possible_moves())