from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signUp/", views.signUp, name="signUp"),
    path("signOut/", views.signOut, name="signOut"),
    path("signIn/", views.signIn, name="signIn"),
    path("match/<int:id>/", views.match, name="match"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("schedule/", views.schedule, name="schedule"),
]
