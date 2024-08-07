from django.shortcuts import render, redirect

from table.models import GameWithAi
from menu.models import User

# Create your views here.
def index(request):
    return render(request, "play_with_computer/index.html")

def create_easy_game(request):
    new_game = GameWithAi.objects.create()

    easy_player = User.objects.get(username="Easy_Computer")
    new_game.black = easy_player
    new_game.black_ready = True
    new_game.save()

    table_id = f"ai{new_game.id}"
    return redirect("table", table_id=table_id)