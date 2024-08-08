from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="computer_index"),
    path("<str:difficulty>/", views.create_game, name="create_game"),
]