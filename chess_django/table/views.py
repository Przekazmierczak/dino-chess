from django.http import JsonResponse
from django.shortcuts import render
from . import pieces

# Create your views here.
def index(request):
    return render(request, "table/index.html", {
        "board": pieces.curr_board
    })

def square(request):
    row = int(request.GET.get("row"))
    column = int(request.GET.get("column"))
    if pieces.curr_board[row][column] is not None:
        curr_square = pieces.curr_board[row][column].check_possible_moves()[0]
        print(curr_square)
    else:
        curr_square = None

    return JsonResponse({
        "piece": curr_square
    })