from django.db import models

# Create your models here.
class Game(models.Model):
    pass

class Board(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    total_moves = models.IntegerField()
    board = models.TextField()
    turn = models.CharField(max_length=1)
    castling = models.CharField(max_length=4)
    soft_moves = models.IntegerField()
