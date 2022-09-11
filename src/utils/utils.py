import logging
from random import choice, randint
from datetime import datetime, timedelta
from typing import Any

from django.conf import settings
from django.core.mail import send_mail

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

    print("otp_end_datetime type: ", type(otp_end_datetime))

    return otp_code, otp_end_datetime


def add_in_global_dict(key: str, value: Any):
    if not isinstance(key, str):
        raise Exception("The key must be a string")

    if not key:
        raise Exception("The key must not be empty")

    if not value:
        raise Exception("The value must not be falsy")

    global_dict[key] = value


def test_remove_from_global_dict(key: str):
    if not isinstance(key, str):
        raise Exception("The key must be a string")

    if not key:
        raise Exception("The key must not be empty")

    try:
        del global_dict[key]
    except KeyError:
        raise Exception(f'The key "{key}" does not exist')


def send_email(email: str, message: str) -> bool:
    """Send OTP and its validity duration via email"""

    recipient = email

    subject = "Pur Beurre: Votre code OTP"

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
