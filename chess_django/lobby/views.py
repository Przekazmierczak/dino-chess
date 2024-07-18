from django.shortcuts import render
from django.db.models import Q

from table.models import Game

# Create your views here.

def index(request):
    return render(request, "lobby/index.html")
