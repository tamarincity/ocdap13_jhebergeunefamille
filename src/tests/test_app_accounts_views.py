from datetime import datetime, timedelta
from functools import total_ordering

import pytest

from django.test import Client


from app_accounts.models import Member
from app_accounts.views import (
    _get_credentials,
    # _get_otp_n_pswd_from_request,
    # check_mail_validity,
    # create_otp,
)
from app_accounts.constants import OTP_VALIDITY_DURATION_IN_MINUTE


client = Client()

# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

credentials = {
                "username": "toto@email.fr",
                "first_name": "Toto",
                "last_name": "Toto",
                "email": "toto@email.fr",
                "password": "12345678",
                "is_submit_button_clicked": "yes"}

otp_n_pswd = {"otp": "Je 5u1s l3 c0de 0TP", "password": "new_password"}


def _mock_get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


class MockRequest:
    def __init__(self, method):
        self.method = method.upper()

        if self.method == 'POST_CREDENTIALS':
            self.POST: dict = credentials
        if self.method == 'POST_OTP_N_PSWD':
            self.POST: dict = otp_n_pswd


def test_get_credentials():

    request = MockRequest("POST_CREDENTIALS")

    print("Should get credentials of user from a form with POST method")
    assert _get_credentials(request) == ('toto@email.fr', '12345678')


@pytest.mark.integration_test
def test_login_user(monkeypatch):

    def mock_authenticate(username, password):
        if (username == credentials["username"]
                and password == credentials["password"]):
            return True
        return False

    def mock_login(request, user):
        pass

    monkeypatch.setattr("app_accounts.views.authenticate", mock_authenticate)
    monkeypatch.setattr("app_accounts.views.login", mock_login)

    print("If no username or no password is provided in login then should return "
            "'Tous les champs doivent être remplis' as message")
    response = client.post('/accounts_login', {"no_usernam": "", "no_password": ""})

    assert ("alert" in str(response.content)
            and "Tous les champs doivent" in str(response.content)
            and "remplis" in str(response.content))

    print("If username is not registered or password is incorrect then should return "
            "'Identifiants incorrects' as message")
    response = client.post(
        '/accounts_login', {"username": credentials["username"], "password": "XXX"})
    assert ("alert" in str(response.content)
            and "Identifiants incorrects" in str(response.content))

    print("If username and password are correct then should redirect to the home page")
    # follow=True allows to follow redirection
    response = client.post(
        '/accounts_login', {"username": credentials["username"],
                            "password": credentials["password"]}, follow=True)

    assert (response.redirect_chain[0][0] == "/")  # redirect_chain = [('/', 302)]