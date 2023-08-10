from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .models import User, Match, User_Bet, Team, Profile, Group
from django.http import HttpResponseNotFound
from django.contrib import messages


def home(request):
    upcomingMatches = Match.objects.filter(finished=False).order_by("date")
    results = Match.objects.filter(finished=True).order_by("-date")
    context = {
        "upcomingMatches": upcomingMatches,
        "results": results,
    }
    return render(request, "main/home.html", context)


def signUp(request):
    error: str = ""
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == 'POST':
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        password2 = request.POST.get("password2").strip()
        if username is None or password is None or password2 is None:
            error = "An error occured"

        elif User.objects.filter(username=username).exists():
            error = "User with that username already exists"

        elif password != password2:
            error = "Passwords do not match"

        elif len(username) < 5:
            error = "Username must have 5 or more characters"

        elif (len(password) <= 7):
            error = "Password must have 8 or more characters"

        else:
            user = User.objects.create_user(
                username=username, password=password)
            profile = Profile.objects.create(
                username=username, password=password)
            profile.save()
            user.save()
            login(request, user)
            return redirect("home")

    context = {
        "error": error,
    }
    return render(request, "main/signUp.html", context)


def signOut(request):
    if not request.user.is_authenticated:
        return redirect("home")
    logout(request)
    return redirect("home")


def signIn(request):
    if request.user.is_authenticated:
        return redirect("home")

    error: str = ""

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.filter(username=username)
        if not user.exists():
            error = "User with that username does not exist"
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                error = "Password is not correct"
            else:
                login(request, user)
                return redirect("home")

    context = {
        "error": error,
    }
    return render(request, "main/signIn.html", context)


def match(request, id):
    match = Match.objects.filter(id=id)

    if not match.exists():
        return HttpResponseNotFound()
    match = match.get()

    if request.method == 'POST':
        try:
            amount = int(request.POST.get("amount"))
            team = request.POST.get("radio")
            if not request.user.is_authenticated:
                messages.error(request, "You have to be logged in")
            elif amount > request.user.balance:
                messages.error(request, "You have no money")
            elif amount == 0:
                messages.error(request, "You have no money")
            elif team not in ("1", "2"):
                messages.error(request, "An error occured")
            else:
                request.user.balance -= amount
                request.user.save()
                team = match.home_team if team == "1" else match.away_team
                outcome = amount * match.home_coefficient if team == match.home_team else amount * \
                    match.away_coefficient
                bet = User_Bet.objects.create(
                    user_id=request.user, match_id=Match.objects.get(id=id), team=Team.objects.get(id=team.id), deposit=amount, outcome=outcome)
                bet.save()
                messages.success(request, "You have successfully betted")

        except:
            messages.error(request, "An error occured")

    context = {
        "match": match,
    }
    return render(request, "main/match.html", context)


def leaderboard(request):
    users = User.objects.all()
    context = {
        "users": users,
    }
    return render(request, 'main/leaderboard.html', context)


def schedule(request):
    groups = Group.objects.all()
    teams = Team.objects.all()

    context = {
        "groups": groups,
        "teams": teams,
    }
    return render(request, "main/schedule.html", context)
