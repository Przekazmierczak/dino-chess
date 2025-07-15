from datetime import datetime

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

import json
from django.http import JsonResponse

from table.models import Game
from django.db.models import Q

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
        if len(username) <= 5:
            return render(request, "menu/register.html", {
                "message": "Username is too short."
            })
        
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure username is not too long
        if len(password) >= 20:
            return render(request, "menu/register.html", {
                "message": "Passwords is too long."
            })

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
    
def user(request):
    return render(request, "menu/user.html")

def change_password(request):
    if request.method == "POST":
        # Check current password'
        current_password = request.POST["currect_password"]
        if not request.user.check_password(current_password):
            return render(request, "menu/changepassword.html", {
                "message": "Invalid current password."
            })
        
        # Ensure password matches confirmation
        new_password = request.POST["new_password"]
        new_confirmation = request.POST["new_confirmation"]
        if new_password != new_confirmation:
            return render(request, "menu/changepassword.html", {
                "message": "Passwords must match."
            })
        
        # Ensure current password doesnt match new password
        if new_password == current_password:
            return render(request, "menu/changepassword.html", {
                "message": "New password cannot be the same as the current password."
            })
        
        # Ensure password is enough length
        if (len(new_password) <= 5):
            return render(request, "menu/changepassword.html", {
                "message": "Passwords is too short."
            })
        
        # Change the password
        request.user.set_password(new_password)
        request.user.save()

        # Update session to prevent logout after password change
        update_session_auth_hash(request, request.user)

        return HttpResponseRedirect(reverse("user"))
    else:
        return render(request, "menu/changepassword.html")

def save_avatar(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            avatar = body.get('avatar')

            # Check if the 'avatar' data is present in the request body
            if not avatar:
                # If no avatar data is provided, return a 400 Bad Request response
                return JsonResponse({'message': 'No avatar provided!'}, status=400)

            # Update the user's avatar field with the provided data
            request.user.avatar = avatar
            request.user.save()

            # Return a success response with a 201 Created status code
            return JsonResponse({'message': 'Avatar saved successfully!'}, status=201)
        
        # Handle database integrity errors, such as unique constraint violations
        except IntegrityError:
            return JsonResponse({'message': 'Avatar could not be saved due to integrity issues!'}, status=500)
        
        # Handle any other exceptions that may occur during the process
        except Exception as e:
            return JsonResponse({'message': f'An error occurred: {str(e)}'}, status=500)

def load_more(request):
    # Get the currently logged-in user
    user = request.user
    # Number of games to retrieve at once
    games_per_batch = 11

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            # Parse the request body to retrieve the last game ID
            last_game_id = body.get('lastID')

            # Check if the 'avatar' data is present in the request body
            if not last_game_id:
                return JsonResponse({'message': 'No ID provided!'}, status=400)
            
            # Determine the timestamp to filter games
            if last_game_id > 0:
                lastTime = Game.objects.get(pk=last_game_id).finished_at
            else:
                lastTime = datetime.utcnow()

            # Retrieve games filtered by the current user, completed status, and timestamp
            games = list(
                Game.objects.filter(finished_at__lte=lastTime)
                .filter((Q(white=user) | Q(black=user)) & Q(finished_at__isnull=False))
                .order_by('-finished_at')[:games_per_batch]
            )
            
            # Prepare the response data
            game_data = []
            for game in games:
                # Determine whether the logged-in user won or lost the game
                winner = game.winner
                if game.winner == "w":
                    winner = "w" if user == game.white else "l"
                if game.winner == "b":
                    winner = "l" if user == game.white else "w"

                # Append game details to the response data
                game_data.append({
                    "id":game.id,
                    "winner":winner,
                    "time":int(game.finished_at.timestamp() * 1000),
                    "white":game.white.username,
                    "black":game.black.username
                })

            # Return the game data as a JSON response with a 201 status code
            return JsonResponse({'message': game_data}, status=201)
        
        # Handle exceptions and return an error response
        except Exception as error:
            return JsonResponse({'message': f'An error occurred: {str(error)}'}, status=500)