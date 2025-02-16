from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

from .models import User

# Create your views here.
def index(request):
    return render(request, "menu/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("menu_index"))
        else:
            return render(request, "menu/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "menu/login.html")
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("menu_index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure username is enough length
        if (len(username) <= 5):
            return render(request, "menu/register.html", {
                "message": "Username is too short."
            })
        
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "menu/register.html", {
                "message": "Passwords must match."
            })
        
        # Ensure password is enough length
        if (len(password) <= 5):
            return render(request, "menu/register.html", {
                "message": "Passwords is too short."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "menu/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("menu_index"))
    else:
        return render(request, "menu/register.html")