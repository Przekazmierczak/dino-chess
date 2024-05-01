from django.conf import settings
from django.db import models

# Create your models here.
class Game(models.Model):
    winner = models.CharField(max_length=1, null=True, choices=[(None, 'None'), ('w', 'white'), ('b', 'black'), ('d', 'draw')], default=None)
    started = models.BooleanField(default=False)
    white = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='white_games')
    white_ready = models.BooleanField(default=False)
    black = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='black_games')
    black_ready = models.BooleanField(default=False)

class Board(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    total_moves = models.IntegerField()
    board = models.TextField()
    turn = models.CharField(max_length=1, choices=[('w', 'white'), ('b', 'black')])
    castling = models.CharField(max_length=4)
    enpassant = models.CharField(max_length=2)
    soft_moves = models.IntegerField()