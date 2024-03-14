# from django.http import JsonResponse
import json
from django.shortcuts import render, redirect

from .models import Game, Board
from . import pieces

# Create your views here.
def index(request):
    return render(request, "table/index.html")

def table(request, table_id):
    return render(request, "table/table_id.html", {
        "table_id": table_id,
    })

def create_table(request):
    starting_board = [["R", "N", "B", "K", "Q", "B", "N", "R"],
                      ["P", "P", "P", "P", "P", "P", "P", "P"],
                      [" ", " ", " ", " ", " ", " ", " ", " "],
                      [" ", " ", " ", " ", " ", " ", " ", " "],
                      [" ", " ", " ", " ", " ", " ", " ", " "],
                      [" ", " ", " ", " ", " ", " ", " ", " "],
                      ["p", "p", "p", "p", "p", "p", "p", "p"],
                      ["r", "n", "b", "k", "q", "b", "n", "r"]]
    
    new_game = Game.objects.create()

    Board.objects.create(
        game = new_game,
        total_moves = 0,
        board = json.dumps({"board": starting_board}),
        turn = "w",
        castling = "----", # "kqKQ"
        soft_moves = 0
    )

    table_id = f"{new_game.id}"
    return redirect("table", table_id=table_id)

# def square(request):
#     row = int(request.GET.get("row"))
#     column = int(request.GET.get("column"))
#     if pieces.curr_board[row][column] is not None:
#         curr_square_piece = pieces.curr_board[row][column].piece
#         curr_square_player = pieces.curr_board[row][column].player
#         curr_square_moves = pieces.curr_board[row][column].check_possible_moves(pieces.curr_board)
#     else:
#         curr_square_piece = None
#         curr_square_player = None
#         curr_square_moves = None
 
#     return JsonResponse({
#         "piece": curr_square_piece,
#         "player": curr_square_player,
#         "moves": curr_square_moves
#     })