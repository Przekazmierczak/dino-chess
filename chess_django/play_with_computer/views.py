from django.shortcuts import render, redirect

from table.models import Game
from menu.models import User

# Create your views here.
def index(request):
    return render(request, "play_with_computer/index.html")

def create_game(request, difficulty):
    new_game = Game.objects.create()

    new_game.with_ai = True
    new_game.black = User.objects.get(username=f"{difficulty} AI")
    new_game.black_ready = True
    new_game.save()

    return redirect("table", table_id=new_game.id)