import time
from datetime import datetime
import random
import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from icecream import ic

from app_accounts.models import Member
from utils import utils
from .constants import (
    LARA_FAKE_OTP,
    OTP_VALIDITY_DURATION_IN_MINUTE,
    USER_LARA_CROFT_HOMELESS,
    USER_LARA_CROFT_OWNER,
)


User = get_user_model()


# Get credentials sent via the form
def _get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


# Get OTP and password sent via the form
def _get_otp_n_pswd_from_request(request):
    otp_code = request.POST.get('otp', None)
    password = request.POST.get('password', None)
    return otp_code, password


def delete_fake_users(request):
    try:
        # user = Member.objects.get(username=USER_LARA_CROFT_HOMELESS["username"])
        Member.objects.filter(username=USER_LARA_CROFT_HOMELESS["username"]).delete()
    except Exception as e:
        print(str(e))

    try:
        # user = Member.objects.get(username=USER_LARA_CROFT_OWNER["username"])
        Member.objects.filter(username=USER_LARA_CROFT_OWNER["username"]).delete()
    except Exception as e:
        print(str(e))

    return redirect('housing_home')


def forgoten_pswd(request):
    list(messages.get_messages(request))  # Clear all system messages

    if request.method == 'POST':
        email, _ = _get_credentials(request)

        if not email:
            messages.error(request, ("Vous devez entrer votre adresse e-mail !"))
            return render(request, 'app_accounts/forgoten_pswd.html')

        if is_email_valid := utils.check_email_validity(email):

            try:
                # Check if member exists then update it
                member = Member.objects.get(username=email)

                otp_code, otp_validity_end_datetime = utils.create_otp()

                # Store OTP, email and OTP validity datetime in global_dict
                utils.add_in_global_dict(otp_code, [email, otp_validity_end_datetime])
                subject = "jhebergeunefamille: Votre code OTP"
                email_content = (
                    f"""
                    Bonjour, vous avez moins de {OTP_VALIDITY_DURATION_IN_MINUTE} """
                    f"""
                    minutes pour changer votre mot de passe.
                    Votre code (OTP) est : {otp_code}""")

                if is_email_sent := utils.send_email(email, subject, email_content):
                    return redirect('accounts_new_pswd')
                else:
                    messages.error(request, ("Une erreur inattendue est survenue !"))
                    return render(request, "app_accounts/forgoten_pswd.html")

            except ObjectDoesNotExist:
                return redirect('accounts_new_pswd')

    return render(request, "app_accounts/forgoten_pswd.html")


def login_user(request):
    """Login the user"""
    list(messages.get_messages(request))  # Clear all system messages

    # Get provenance of the user according of the value of the
    # param named "provenance" sent in a POST or GET request
    provenance = utils.get_provenance(request)

    if request.method == 'POST':
        username, password = _get_credentials(request)

        if not username or not password:
            messages.error(request, ("Tous les champs doivent ??tre remplis !"))
            return render(request, 'app_accounts/login.html')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, ("Bienvenue, vous ??tes connect?? !"))
            destination = provenance or 'housing_home'
            return redirect(destination)

        messages.error(request, ("Identifiants incorrects !"))

    return render(
        request,
        "app_accounts/login.html",
        context={"provenance": provenance} if provenance else None)


def logout_user(request):
    logout(request)
    return redirect('housing_home')


def new_pswd(request):
    list(messages.get_messages(request))  # Clear all system messages

    utils.remove_unvalid_otp_from_global_dict()

    if request.method == 'POST':
        otp_code, password = _get_otp_n_pswd_from_request(request)

        if not otp_code or not password:
            messages.error(request, ("Tous les champs doivent ??tre remplis !"))
            return render(request, 'app_accounts/new_pswd.html')

        # Get email is OTP valid
        email = utils.global_dict.get(otp_code, ["", ""])[0]  # [email, otp_validity][0]

        if not email:
            messages.error(request, ("Code OTP non valide !"))
            return render(request, "app_accounts/new_pswd.html")
        try:
            # Get the user corresponding to the OTP and OTP validity end datetime
            user = Member.objects.get(username=email)  # username and email are similar

            # Update the user's password
            user.set_password(password)
            user.save()

            # Connect the user
            login(request, user)
            messages.success(request, ("Votre mot de passe a bien ??t?? mis ?? jour. Vous ??tes connect??."))
            return redirect('housing_home')

        except ObjectDoesNotExist:
            logging.debug("No member found for this otp and valdity datetime")

        messages.error(request, ("Code OTP non valide !"))

    return render(request, "app_accounts/new_pswd.html")


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
                messages.success(request, ("Votre compte a bien ??t?? mis ?? jour"))

    except Exception as e:
        logging.error(f"Unable to update profile. Reason: {str(e)}")
        messages.error(request, (
            "Malheureusement une erreur du syst??me est survenue. "
            "Les donn??es n'ont pas pu ??tre mises ?? jour. "
            "Merci de r??-essayez plus tard."))
    ic()
    return render(request, "app_accounts/profile.html", context=context)


def signup_user(request):
    list(messages.get_messages(request))  # Clear all system messages

    # Get provenance of the user according of the value of the
    # param named "provenance" sent in a POST or GET request
    provenance = utils.get_provenance(request)

    if request.method == 'POST':  # Request via the form
        username, _ = _get_credentials(request)  # username = email

        if not username:
            messages.error(request, ("Le champ doit ??tre rempli !"))
            return render(request, 'app_accounts/signup.html')

        is_username_valid = utils.check_email_validity(username)  # because user email is used as username
        if not is_username_valid:
            messages.error(request, ("Email incorrect !"))
            return render(request, 'app_accounts/signup.html')

        if len(username) > 150:
            messages.error(request, ("Email trop long !"))
            return render(request, 'app_accounts/signup.html')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, ("Cet utilisateur est d??j?? enregistr?? !"))
            return render(request, "app_accounts/signup.html")

        # Create otp

        otp_code, otp_validity_end_datetime = utils.create_otp()
        # Store OTP, email and OTP validity datetime in global_dict
        # This part is to allows automatic functional testing
        if (username == USER_LARA_CROFT_HOMELESS["username"]
                or username == USER_LARA_CROFT_OWNER["username"]):
            otp_code = LARA_FAKE_OTP
        utils.add_in_global_dict(otp_code, [username, otp_validity_end_datetime])
        # Send OTP by email
        subject = "jhebergeunefamille: Votre code OTP"
        email_content = (f"Bonjour, vous avez {OTP_VALIDITY_DURATION_IN_MINUTE} minutes "
                            f"pour compl??ter votre enregistrement. Votre code OTP est: {otp_code}")
        is_email_sent = utils.send_email(username, subject, email_content)

        if not is_email_sent:
            time.sleep(random.randint(1, 5))

        messages.success(request, ("Un e-mail contenant votre code (OTP) vous a ??t?? envoy?? !"))
        return redirect(reverse('accounts_complete_the_registration') + f"?provenance={provenance}")

    return render(request, "app_accounts/signup.html", context={"provenance": provenance})


def complete_the_registration(request):
    """
    First the user fill the signup form then an OTP is sent to him.
    thereafter he is redirected to this function to complete the registration.
    This function displays and manages the registration form."""

    list(messages.get_messages(request))  # Clear all system messages

    # Get provenance of the user according of the value of the
    # param named "provenance" sent in a POST or GET request
    provenance = utils.get_provenance(request)

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
            messages.error(request, ("Code OTP non valide !"))
            return render(
                request, 'app_accounts/complete_the_registration.html', context=data_from_form)

        if not (
                data_from_form["pseudo"]
                and data_from_form["first_name"]
                and data_from_form["password"]
                and data_from_form["otp"]):

            messages.error(request, ("Un des champs requis n'est pas renseign??"))
            return render(
                request, 'app_accounts/complete_the_registration.html', context=data_from_form)

        if len(data_from_form["password"]) < 8:
            messages.error(request, ("Le mot de passe doit contenir au moins 8 caract??res"))
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
            messages.success(request, ("Bienvenue, vous ??tes connect?? !"))
            destination = provenance or 'housing_home'

            return redirect(destination)

        except Exception as e:
            logging.error("Unable to create the user or to log the user in.)")
            logging.error(str(e))

    return render(request, 'app_accounts/complete_the_registration.html', context=data_from_form)


@login_required
def get_my_contacts(request):
    """Get the list of contacts of the user in need of housing.
    Allows the in need person to send a message to the owner."""

    utils.send_email_to_owner_if_requested(request, Member)

    try:
        contacts = request.user.hosts.all()
    except Exception as e:
        logging.info("Unable to get the list of contacts")
        logging.info(str(e))
        contacts = None
    return render(
                request,
                "app_accounts/get-my-contacts.html",
                context={"contacts": contacts})
