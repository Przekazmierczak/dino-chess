from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_table/", views.create_table, name="create_table"),
    path("<str:table_id>/", views.table, name="table"),
]