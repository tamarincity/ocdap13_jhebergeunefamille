import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate

from icecream import ic

from utils import utils
from app_accounts.models import Member


# Get credentials sent via the form
def _get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


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


def profile(request):
    if not request.user.is_authenticated:
        ic()
        return redirect('housing_home')

    visitor = request.user
    username = visitor.username
    first_name = request.POST.get('first_name', "")
    last_name = request.POST.get('last_name', visitor.last_name)
    email = visitor.email
    is_submit_button_clicked = request.POST.get('is_submit_button_clicked', "")

    if first_name == "":
        first_name == visitor.first_name

    context = {"member": {
        "first_name": first_name,
        "last_name": last_name,
        "email": email}}

    print()
    print("visitor.first_name: ", visitor.first_name)
    print(type(visitor.first_name))
    print("first_name: ", first_name)
    print(type(first_name))
    print("last_name: ", last_name)
    print(type(last_name))
    print("email: ", email)
    print()
    try:
        ic()
        if is_submit_button_clicked and username:
            if not (first_name == visitor.first_name
                    and last_name == visitor.last_name):
                ic()
                (Member.objects.filter(username=username)
                    .update(first_name=first_name, last_name=last_name))
                ic()
                messages.success(request, ("Votre compte a bien été mis à jour"))

    except Exception as e:
        logging.error(f"Unable to update profile. Reason: {str(e)}")
        messages.success(request, (
            "Malheureusement une erreur du système est survenue. "
            "Les données n'ont pas pu être mises à jour. "
            "Merci de ré-essayez plus tard."))
    ic()
    return render(request, "app_accounts/profile.html", context=context)


def signup_user(request):
    return HttpResponse("signup_user is coming soon")
