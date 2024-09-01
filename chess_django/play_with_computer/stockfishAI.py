from pathlib import Path
from stockfish import Stockfish

absolute_path = Path(__file__).resolve().parent.parent.parent
stockfish_loc = absolute_path / 'stockfish' / 'stockfish-windows-x86-64-avx2.exe'

class Computer:
    def __init__(self, board):
        self.stockfish = Stockfish(path=stockfish_loc)
        self.stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

    def best_move(self):
        best_move = self.stockfish.get_best_move()
        return best_move
    
    def board_visual(self):
        board_visual = self.stockfish.get_board_visual()
        return board_visual