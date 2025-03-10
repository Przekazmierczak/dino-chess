from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="menu_index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user", views.user, name="user"),
    path("changepassword", views.change_password, name="changepassword"),
    path("saveavatar", views.save_avatar, name="saveavatar"),
    path("loadmore", views.load_more, name="loadmore")
]