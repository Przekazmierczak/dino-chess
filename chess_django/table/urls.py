from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("square", views.square, name="square")
    # path("<int:table_id>", views.table, name="table"),
]