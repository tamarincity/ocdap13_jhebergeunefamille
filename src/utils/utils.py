import logging
from random import choice, randint
from datetime import datetime, timedelta
from typing import Any

from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages

from .constants import (
    ALPHABET_N_NUMBERS,
)

from app_accounts.constants import OTP_VALIDITY_DURATION_IN_MINUTE


global_dict = {}


def check_email_validity(email: str) -> bool:
    if email and isinstance(email, str) and email.count("@") == 1:

        if "@." in email:
            return False

        if email.endswith(".") or email.endswith("@"):
            return False

        right_part = email.split("@")[-1]

        if "." in right_part:
            return True

    return False


def create_random_chars(nbr_of_chars):
    return (
        "".join(choice(ALPHABET_N_NUMBERS) for i in range(nbr_of_chars)))


def create_otp() -> tuple[str, "datetime.datetime"]:
    """Create OTP (One Time Password) with a datetime validity"""

    # Create OTP_code
    otp_code = create_random_chars(randint(8, 12))

    # Create end datetime of otp_code
    now = datetime.now()
    otp_end_datetime = now + timedelta(minutes=OTP_VALIDITY_DURATION_IN_MINUTE)

    return otp_code, otp_end_datetime


def add_in_global_dict(key: str, value: Any):
    if not isinstance(key, str):
        raise Exception("The key must be a string")

    if not key:
        raise Exception("The key must not be empty")

    if not value:
        raise Exception("The value must not be falsy")

    global_dict[key] = value


def remove_unvalid_otp_from_global_dict():

    now = datetime.now()
    list_of_unvalid_keys = [key for key, value in global_dict.items() if value[1] < now]

    for key in list_of_unvalid_keys:
        del global_dict[key]


def send_email(email: str, subject: str, message: str) -> bool:
    """Send email"""

    recipient = email

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient],
            fail_silently=False)

    except Exception as e:
        logging.error(f"ERROR, unable to send email! Reason: {e}")
        return False

    return True


def send_email_to_owner_if_requested(request, Member) -> None:
    """Allows the person in need to send an email to the owner of an accomodation
    if some args are provided"""

    message_to_owner = request.POST.get('message_to_owner', "")
    owner_id = request.POST.get('owner_id', "")
    in_need_email = request.POST.get('in_need_email', "")

    if message_to_owner and owner_id and in_need_email:

        # Get the recipient
        owner = Member.objects.get(id=owner_id)

        # Create the email
        subject = "jhebergeunefamille: Une personne dans le besoin vous contacte"
        header_message = f"""
        Bonjour {owner.first_name} ({owner.pseudo}),

        Cet email vous a été envoyé par {in_need_email} via l'application jhebergeunefamille.app.

        """

        email_content = header_message + message_to_owner
        if not send_email(owner.email, subject, email_content):
            messages.error(request, "Une erreur est survenue lors de l'envoi de l'email")
        else:
            messages.success(request, "Le message a bien été envoyé")

    return


def get_provenance(request) -> str:
    """Return (as a string) the provenance of the user if it has been sent via GET or POST request
    The parameter name in the request must be "provenance".
    Ex: provenance = "my-uri?param1=yes&param2=black&param3=fast" """

    uri_n_first_param = (
        request.GET.get('provenance', "")
        or request.POST.get('provenance', "?=").split("?"))

    provenance = (
        str(uri_n_first_param)
        + "".join(f"&{key}={value}" for key, value in request.GET.items() if not key == "provenance"))

    if provenance in ["['', '=']", "['']"]:
        provenance = ""

    return provenance
