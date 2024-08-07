from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="computer_index"),
    path("create_easy_game", views.create_easy_game, name="create_easy_game"),
]