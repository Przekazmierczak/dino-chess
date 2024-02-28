from django.db import models

# Create your models here.
class Board(models.Model):
    total_moves = models.IntegerField()
    board = models.TextField()
    player = models.CharField(max_length=1)
    castling = models.CharField(max_length=4)
    soft_moves = models.IntegerField()

class Games(models.Model):
    game_history = models.ManyToManyField(Board)