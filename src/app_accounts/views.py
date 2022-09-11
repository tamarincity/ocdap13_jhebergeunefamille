import time
import random
import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate

from icecream import ic

from app_accounts.models import Member
from utils import utils
from .constants import (
    OTP_VALIDITY_DURATION_IN_MINUTE,
)


User = get_user_model()

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
    list(messages.get_messages(request))  # Clear all system messages

    if not request.user.is_authenticated:
        ic()
        return redirect('housing_home')

    visitor = request.user
    username = visitor.username
    pseudo = visitor.pseudo
    first_name = request.POST.get('first_name', visitor.first_name)
    last_name = request.POST.get('last_name', visitor.last_name)
    email = visitor.email
    is_submit_button_clicked = request.POST.get('is_submit_button_clicked', "")

    context = {"member": {
        "pseudo": pseudo,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "username": username}}

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
    list(messages.get_messages(request))  # Clear all system messages

    if request.method == 'POST':  # requête via formulaire
        username, password = _get_credentials(request)  # username = email

        if not username:
            messages.success(request, ("Le champ doit être rempli !"))
            return render(request, 'app_accounts/signup.html')

        is_username_valid = utils.check_email_validity(username)  # because user email is used as username
        if not is_username_valid:
            messages.success(request, ("Email incorrect !"))
            return render(request, 'app_accounts/signup.html')

        try:
            # Creation of the user if not exists else Exception
            user = User.objects.create_user(
                username=username[:150], password=password, email=username[:150])

            # Create otp
            otp_code, otp_validity_end_datetime = utils.create_otp()
            # Store OTP, email and OTP validity datetime in temporary dict
            utils.add_in_global_dict(otp_code, [username, otp_validity_end_datetime])
            # Send OTP by email
            email_content = (f"Bonjour, vous avez {OTP_VALIDITY_DURATION_IN_MINUTE} minutes "
                        f"pour compléter votre enregistrement. Votre code OTP est: {otp_code}")
            is_email_sent = utils.send_email(username, email_content)

            if not is_email_sent:
                time.sleep(random.randint(1, 5))

            return redirect('accounts_complete_the_registration')

        except Exception as e:
            print(str(e))
            if "exists" in str(e):
                messages.success(request, ("Cet utilisateur est déjà enregistré !"))

    return render(request, "app_accounts/signup.html")


def complete_the_registration(request):
    return HttpResponse("Completion of registration is coming soon")
