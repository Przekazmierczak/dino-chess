from django.conf import settings
from django.db import models
from datetime import timedelta

# Create your models here.
class Game(models.Model):
    winner = models.CharField(max_length=1, null=True, choices=[(None, 'None'), ('w', 'white'), ('b', 'black'), ('d', 'draw')], default=None)
    started = models.BooleanField(default=False)
    white = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='white_games')
    white_ready = models.BooleanField(default=False)
    black = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='black_games')
    black_ready = models.BooleanField(default=False)
    with_ai = models.BooleanField(default=False)
    boards = models.JSONField(default=list)

class Board(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    total_moves = models.IntegerField()
    board = models.TextField()
    turn = models.CharField(max_length=1, choices=[('w', 'white'), ('b', 'black')])
    castling = models.CharField(max_length=4)
    enpassant = models.CharField(max_length=2)
    soft_moves = models.IntegerField()
    white_time_left = models.DurationField(default=timedelta(minutes=15))
    black_time_left = models.DurationField(default=timedelta(minutes=15))
    created_at = models.DateTimeField(auto_now_add=True)
    last_move = models.CharField(max_length=4, null=True, default=None)