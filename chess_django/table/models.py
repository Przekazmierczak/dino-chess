from django.db import models

# Create your models here.
class Game(models.Model):
    winner = models.CharField(max_length=1, null=True, choices=[(None, 'None'), ('w', 'white'), ('b', 'black'), ('d', 'draw')])

class Board(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    total_moves = models.IntegerField()
    board = models.TextField()
    turn = models.CharField(max_length=1, choices=[('w', 'white'), ('b', 'black')])
    castling = models.CharField(max_length=4)
    enpassant = models.CharField(max_length=2)
    soft_moves = models.IntegerField()
