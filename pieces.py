class Pawn:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False
        self.possible_moves = self.check_possible_moves()
        self.possible_attacks = self.check_possible_attacks()

    def check_possible_moves(self):
        moves = []
        direction = 1 if self.player == "white" else -1

        move_by_one = self.row + direction
        if move_by_one in range(0, 7):
            moves.append((move_by_one, self.column))

        move_by_two = self.row + 2 * direction
        if not self.moved and move_by_two in range(0, 7):
            moves.append((move_by_two, self.column))
        return moves

    def check_possible_attacks(self):
        attacks = []
        direction = 1 if self.player == "white" else -1

        move_by_one = self.row + direction
        attack_right = self.column + 1
        if move_by_one in range(0, 7) and attack_right in range(0, 7):
            attacks.append((self.row + direction, attack_right))
        
        attack_left = self.column - 1
        if move_by_one in range(0, 7) and attack_left in range(0, 7):
            attacks.append((self.row + direction, attack_left))
        return attacks

class Rook:
    def __init__(self, player, location):
        self.player = player
        self.row, self.column = location
        self.moved = False
        self.possible_moves = self.check_possible_moves()
        self.possible_attacks = self.check_possible_attacks()

    def check_possible_moves(self):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for direction in directions:
            distance = 1
            while True:
                new_row = self.row + distance * direction[0]
                new_column = self.column + distance * direction[1]

                if new_row not in range(0, 7) or new_column not in range(0, 7):
                    break

                moves.append((new_row, new_column))
                distance += 1
        return moves
        
    def check_possible_attacks(self):
        self.possible_attacks = self.possible_moves

class Knight:
    def __init__(self, player, location):
        pass

class Bishop:
    def __init__(self, player, location):
        pass

class King:
    def __init__(self, player, location):
        pass

class Queen:
    def __init__(self, player, location):
        pass

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

print(board[0][0].possible_moves)