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
            messages.success(request, ("Bienvenue, vous êtes connecté !"))
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

    visitor = Member.objects.get(username=request.user.username)
    username = visitor.username
    pseudo = visitor.pseudo
    first_name = request.POST.get('first_name', visitor.first_name)
    last_name = request.POST.get('last_name', visitor.last_name)
    phone = request.POST.get('tel', visitor.phone)
    presentation = request.POST.get('presentation', visitor.message_of_presentation)
    email = visitor.email
    is_submit_button_clicked = request.POST.get('is_submit_button_clicked', "")

    context = {"member": {
        "pseudo": pseudo,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "message_of_presentation": presentation,
        "username": username}}

    try:
        ic()
        if is_submit_button_clicked and username:
            if not (first_name == visitor.first_name
                    and last_name == visitor.last_name
                    and phone == visitor.phone
                    and presentation == visitor.message_of_presentation):
                ic()
                (Member.objects.filter(username=username)
                    .update(
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        message_of_presentation=presentation))
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

    if request.method == 'POST':  # Request via the form
        username, _ = _get_credentials(request)  # username = email

        if not username:
            messages.success(request, ("Le champ doit être rempli !"))
            return render(request, 'app_accounts/signup.html')

        is_username_valid = utils.check_email_validity(username)  # because user email is used as username
        if not is_username_valid:
            messages.success(request, ("Email incorrect !"))
            return render(request, 'app_accounts/signup.html')

        if len(username) > 150:
            messages.success(request, ("Email trop long !"))
            return render(request, 'app_accounts/signup.html')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.success(request, ("Cet utilisateur est déjà enregistré !"))
            return render(request, "app_accounts/signup.html")

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

        messages.success(request, ("Un e-mail contenant votre code (OTP) vous a été envoyé !"))
        return redirect('accounts_complete_the_registration')

    return render(request, "app_accounts/signup.html")


def complete_the_registration(request):
    """
    First the user fill the signup form then an OTP is sent to him.
    thereafter he is redirected to this function to complete the registration.
    This function displays and manages the registration form."""

    list(messages.get_messages(request))  # Clear all system messages

    data_from_form = {
        "otp": request.POST.get('otp', ''),
        "pseudo": request.POST.get('pseudo', ''),
        "first_name": request.POST.get('first_name', ''),
        "tel": request.POST.get('tel', ''),
        "presentation": request.POST.get('presentation', ''),
        "password": request.POST.get('password', ''),
        "is_offering_accommodation": request.POST.get('is_offering_accommodation', '')}

    data_from_form["is_offering_accommodation"] = (
        True if data_from_form["is_offering_accommodation"] == "true"
        else False)

    utils.remove_unvalid_otp_from_global_dict()

    if data_from_form["otp"]:
        # Get email from global_dict thanks to the otp. {"any otp": ["an email", "validity datetime"]}
        email = utils.global_dict.get(data_from_form["otp"], ["", ""])[0]
        if not email:
            messages.success(request, ("Code OTP non valide !"))
            return render(
                request, 'app_accounts/complete_the_registration.html', context=data_from_form)

        if not (
                data_from_form["pseudo"]
                and data_from_form["first_name"]
                and data_from_form["password"]
                and data_from_form["otp"]):
            messages.success(request, ("Un des champs requis n'est pas renseigné"))
            return render(
                request, 'app_accounts/complete_the_registration.html', context=data_from_form)

        if len(data_from_form["password"]) < 8:
            messages.success(request, ("Le mot de passe doit contenir au moins 8 caractères"))
            return render(
                request, 'app_accounts/complete_the_registration.html', context=data_from_form)

        # Remove OTP from global_dict
        try:
            del utils.global_dict[data_from_form["otp"]]
        except Exception as e:
            logging.error("Unable to remove OTP from global_dict via the key")

        try:
            # Creation of the user
            user = Member.objects.create_user(
                username=email,
                email=email,
                pseudo=data_from_form["pseudo"],
                first_name=data_from_form["first_name"],
                phone=data_from_form["tel"],
                message_of_presentation=data_from_form["presentation"],
                password=data_from_form["password"],
                is_host=data_from_form["is_offering_accommodation"])

            # User connection
            login(request, user)

            messages.success(request, ("Bienvenue, vous êtes connecté !"))
            return redirect('housing_home')

        except Exception as e:
            logging.error("Unable to create the user or to log the user in.)")
            logging.error(str(e))

    return render(request, 'app_accounts/complete_the_registration.html', context=data_from_form)
