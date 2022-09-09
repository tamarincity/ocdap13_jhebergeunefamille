from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate

from utils import utils


# Get credentials sent via the form
def _get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


def account(request):
    return HttpResponse("signup is coming soon")


def delete_fake_users(request):
    return HttpResponse("delete_fake_users is coming soon")


def forgoten_pswd(request):
    return HttpResponse("forgoten_pswd is coming soon")


def get_all_cities_with_available_rooms(request):
    return HttpResponse("signup_user is coming soon")


def login_user(request):
    list(messages.get_messages(request))  # Clear all system messages

    if request.method == 'POST':
        username, password = _get_credentials(request)

        if not username or not password:
            messages.success(request, ("Tous les champs doivent être remplis !"))
            return render(request, 'app_accounts/login.html')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('housing_home')

        messages.success(request, ("Identifiants incorrects !"))

    return render(request, "app_accounts/login.html")


def logout_user(request):
    logout(request)
    return redirect('housing_home')


def new_pswd(request):
    return HttpResponse("new_pswd is coming soon")


def signup_user(request):
    return HttpResponse("signup_user is coming soon")
