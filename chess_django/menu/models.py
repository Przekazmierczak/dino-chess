from django.contrib.auth.models import AbstractUser
from django.db import models
from table.models import Game

# Create your models here.
class User(AbstractUser):
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=19, unique=True)