from pathlib import Path
from stockfish import Stockfish

# Define the path to the Stockfish executable by navigating up three levels from the current file's directory
absolute_path = Path(__file__).resolve().parent.parent.parent
stockfish_loc = absolute_path / 'stockfish' / 'stockfish-windows-x86-64-avx2.exe'

class Computer:
    def __init__(self, board, turn, castling, enpassant, soft_moves, total_moves, elo):
        self.stockfish = Stockfish(path=stockfish_loc)
        # Generate FEN string from the current board state
        self.fen = self.get_fen(board, turn, castling, enpassant, soft_moves, total_moves)
        # Set the FEN position in Stockfish
        self.stockfish.set_fen_position(self.fen)
        # Set stockfish rating
        if elo:
            self.stockfish.set_elo_rating(elo)

    def get_fen(self, board, turn, castling, enpassant, soft_moves, total_moves):
        fen = []
        count = 0

        # Construct the piece placement portion of the FEN string
        for i in range(7, -1, -1):
            if count:
                fen.append(str(count))  # Append the count of empty squares
                count = 0
            if i != 7:
                fen.append("/")
            for j in range(7, -1, -1):  # Loop through each file (column) of the board from h to a
                if board[i][j] != " ":
                    if count:
                        fen.append(str(count))  # Append the count of empty squares before placing a piece
                        count = 0
                    fen.append(board[i][j])  # Append the piece notation (e.g., "r", "N")
                else:
                    count += 1

        if count:
            fen.append(str(count))  # Append any remaining empty squares at the end of the row
        
        # Add the active color (turn) to the FEN string
        fen.append(" w ") if turn == "white" else fen.append(" b ")
        
        # Add castling availability to the FEN string
        fen_castling = []
        for letter in castling:
            if letter != "_":
                fen_castling.append(letter)
        if not fen_castling:
            fen_castling.append("-")
        fen_castling.append(" ")
        fen.extend(fen_castling)
        
        # Add en passant target square
        fen.append(f"{enpassant} ") if enpassant != "__" else fen.append("- ")

        # Add half-move clock and full-move number
        fen.append(f"{str(soft_moves)} {str(total_moves)}")

        return ("").join(fen)  # Return the final FEN string
    
    def best_move(self):
        best_move = self.stockfish.get_best_move()

        promotion = best_move[4] if len(best_move) > 4 else None  # Check if the move involves a promotion
        move = [[], []]

        # Mapping from file letter to index
        letter = {"a": 7, "b": 6, "c": 5, "d": 4, "e": 3, "f": 2, "g": 1, "h": 0}
        
        # Convert the algebraic notation to board indices
        move[0] = [int(best_move[1]) - 1, letter[best_move[0]]]
        move[1] = [int(best_move[3]) - 1, letter[best_move[2]]]

        return move, promotion  # Return the move and promotion