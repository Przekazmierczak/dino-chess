from django.shortcuts import render
from django.db.models import Q

from table.models import Game

# Create your views here.

def index(request):
    free_tables = Game.objects.filter(Q(white_ready=False) | Q(black_ready=False)).order_by('-id')[:10]
    for free_table in free_tables:
        test = free_table.id

    return render(request, "lobby/index.html", {
        "free_tables": test,
    })
