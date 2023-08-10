from django.contrib.auth.models import AbstractUser
from django.db import models
import random


class Profile(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class User(AbstractUser):
    balance = models.FloatField(default=100)


class User_Bet(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    match_id = models.ForeignKey("Match", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    deposit = models.FloatField(default=0)
    outcome = models.FloatField(default=0)
    active = models.BooleanField(default=True, editable=False)

    def __str__(self) -> str:
        return f"{self.user_id.username}'s bet {self.team} -->> {self.match_id}"


class Match(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    home_team = models.ForeignKey(
        "Team", on_delete=models.CASCADE, related_name="homeTeam")
    away_team = models.ForeignKey(
        "Team", on_delete=models.CASCADE, related_name="awayTeam")
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    home_coefficient = models.FloatField(default=1)
    away_coefficient = models.FloatField(default=1)
    group_match = models.BooleanField(default=True)
    finished = models.BooleanField(default=False, editable=False)
    date = models.DateTimeField()

    def save(self):
        if self.home_score != 0 or self.away_score != 0:
            self.finished = True
        if self.finished:
            winner = self.home_team if self.home_score > self.away_score else self.away_team
            loser = self.home_team if winner == self.away_team else self.away_team
            winner.points += 3
            winner.wins += 1
            loser.loses += 1
            winner.save()
            loser.save()
            bets = User_Bet.objects.filter(match_id=self.id)
            if bets.exists():
                for bet in bets:
                    if bet.active:
                        if bet.team == winner:
                            user = bet.user_id
                            user.balance += bet.outcome
                            user.save()
                            bet.active = False
                            bet.save()
        return super().save()

    def __str__(self):
        return f"{self.home_team} - {self.away_team}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Knockout(models.Model):
    stages = [
        ("Semi-Final", "Semi-Final"),
        ("Final", "Final"),
    ]
    name = models.CharField(
        max_length=100, choices=stages, default="Semi-Final")

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Player(models.Model):
    positions = [
        ("GK", "Goalkeeper"),
        ("DF", "Defender"),
        ("MF", "Midfielder"),
        ("ST", "Striker"),
    ]
    team_id = models.ForeignKey("Team", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=2, choices=positions, default="GK")
    goals = models.IntegerField(default=0)
    assist = models.IntegerField(default=0)
    pace = models.IntegerField(default=random.randint(1, 100))
    shooting = models.IntegerField(default=random.randint(1, 100))
    passing = models.IntegerField(default=random.randint(1, 100))
    dribling = models.IntegerField(default=random.randint(1, 100))
    defending = models.IntegerField(default=random.randint(1, 100))
    physical = models.IntegerField(default=random.randint(1, 100))
    overall = models.IntegerField(default=0)

    def save(self):
        self.overall = (self.shooting + self.passing + self.dribling +
                        self.defending + self.physical + self.pace) // 4.5

        return super().save()

    def __str__(self) -> str:
        return self.name
