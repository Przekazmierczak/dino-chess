from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:table_id>/", views.table, name="table"),
    path("square", views.square, name="square"),
]