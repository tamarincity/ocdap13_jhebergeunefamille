from datetime import datetime, timedelta

import pytest

from utils import utils
from utils.utils import (
    check_email_validity,
    create_otp,
    create_random_chars,
    global_dict,
    remove_unvalid_otp_from_global_dict,
    send_email,
)


def test_check_email_validity():
    print("If no email is provided, the test will fail.")
    print("If email is falsy then should return False.")

    assert check_email_validity("") == False

    print("If email is not string then should return False.")
    assert check_email_validity(123) == False

    print('If "@" not in email then should return False.')
    assert check_email_validity("wrong.email") == False

    print('If "@." in email then should return False.')
    assert check_email_validity("wrong@.email") == False

    print('If email ends with "." or "@", should return False.')
    assert check_email_validity("wrong@email.") == False

    print("If email is well formed then should return True.")
    assert check_email_validity("good@email.com") == True


def test_create_random_chars():

    print("Should return a random string")
    assert type(create_random_chars(7)) == str

    print("The returned length (7) must be equal to the integer entered as argument (7)")
    assert len(create_random_chars(7)) == 7

    print("Two returned strings of the same length must have a different content")
    assert create_random_chars(5) != create_random_chars(5)


def test_create_otp(monkeypatch):

    def mock_create_random_chars(int):
        return "gTdo3ik326GTsc1d24h0jfRRYJBKGN020gTdo3ik326GTsc1d24h0jfRRYJBKGN020"[:int]

    monkeypatch.setattr("utils.utils.create_random_chars", mock_create_random_chars)

    otp_n_validity = create_otp()

    print("Should return a tuple of two elements")
    assert len(otp_n_validity) == 2

    print("The first returned element (OTP) should be a string")
    assert type(otp_n_validity[0]) == str

    print("The first returned element (OTP) should have a length from 8 to 12 included")
    assert 8 <= len(otp_n_validity[0]) <= 12

    print("The second returned element (otp_end_datetime) should be a datetime")
    assert type(otp_n_validity[1]) == datetime


def test_send_email(monkeypatch):

    now = datetime.now()

    def mock_send_mail(
            subject,
            message,
            email_host_user,
            recipients,
            fail_silently):

        for recipient in recipients:
            if not (
                    "@" in recipient
                    and "." in recipient):
                raise Exception("Sending email failed")
        return True

    monkeypatch.setattr("utils.utils.send_mail", mock_send_mail)

    print("If the email of the recipient is malformed "
            "then should return False because no email can be sent")
    assert send_email("wrong@email", "the subject", "this_is_the_OTP_code") == False

    print("If the email of the recipient is properly formed "
            "then should return True because the email has been sent")
    assert send_email("good@email.com", "the subject", "this_is_the_OTP_code") == True


def test_add_in_global_dict():

    print("global_dict is a dictionary in which data such as the OTP is temporarily stored.")
    print("If the key is not a string then should raise an exception 'The key must be a string'")
    with pytest.raises(Exception):  # equiv to assert for exceptions
        utils.add_in_global_dict([1, 2, 3], "any value")

    print("If the key is empty then should raise an exception 'The key must not be empty'")
    with pytest.raises(Exception):  # equiv to assert for exceptions
        utils.add_in_global_dict("", "any value")

    print("If the value is falsy then should raise an exception 'The value must not be falsy'")
    with pytest.raises(Exception):  # equiv to assert for exceptions
        utils.add_in_global_dict("the_key", "")

    print("Add a key and a value should add them in the global_dict")
    utils.add_in_global_dict("the_key", "the value")
    assert utils.global_dict["the_key"] == "the value"

    # Remove the key we just added
    del utils.global_dict["the_key"]


def test_remove_unvalid_otp_from_global_dict():

    print("global_dict is a dictionary in which data such as the OTP is temporarily stored.")
    now = datetime.now()
    unvalid_datetime = now - timedelta(seconds=180)
    value = ["fake_email", unvalid_datetime, ]

    print("Adding a fake OTP with an expired validity datetime in the global_dict "
          "in order to test this function")
    global_dict["fake_otp"] = value
    assert global_dict["fake_otp"] == value
    assert "fake_otp" in global_dict.keys()

    print("This function should remove the otp from the global_dict")
    remove_unvalid_otp_from_global_dict()
    assert "fake_otp" not in global_dict.keys()
