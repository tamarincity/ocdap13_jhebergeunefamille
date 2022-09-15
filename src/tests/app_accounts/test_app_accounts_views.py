from datetime import datetime, timedelta
from functools import total_ordering
from pprint import pprint
import time

import pytest
from pytest_django.asserts import assertTemplateUsed

from django.test import Client


from app_accounts.models import Member
from app_accounts.views import (
    _get_credentials,
    # _get_otp_n_pswd_from_request,
    # check_email_validity,
    # create_otp,
)
from app_accounts.constants import OTP_VALIDITY_DURATION_IN_MINUTE


client = Client()

# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

credentials = {
                "username": "toto@email.fr",
                "first_name": "Toto",
                "last_name": "DUPONT",
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


@pytest.fixture
def add_member_to_db():
    return Member.objects.create_user(
                username=credentials["username"],
                first_name=credentials["first_name"],
                password=credentials["password"],
                email=credentials["username"])


@pytest.fixture
def get_user_credentials():
    return {"username": credentials["username"],
            "password": credentials["password"],
            "email": credentials["username"]}


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


@pytest.mark.integration_test
def test_logout_user(monkeypatch):

    def mock_logout(request):
        pass

    monkeypatch.setattr("app_accounts.views.logout", mock_logout)

    print("If logout is clicked then ")
    print("     should redirect to the home page")
    # follow=True allows to follow redirection
    response = client.get('/accounts_logout', follow=True)
    assert (response.redirect_chain[0][0] == "/")  # redirect_chain = [('/', 302)]

    print("     should display the link 'Connexion'")
    assert "Connexion" in str(response.content)


@pytest.mark.integration_test
def test_profile(add_member_to_db):

    unregistered_user = {"first_name": "Jane", "is_submit_button_clicked": True}

    print("If the user is not registered, should redirect to the home page")
    response = client.post('/accounts_profile',
                           unregistered_user,
                           follow=True)
    assert "Je recherche un logement pour" in str(response.content)

    # Create a registered user
    user = add_member_to_db  # Fixture

    print("If the registered user modify his account via the form then")
    print("     should alert 'Votre compte a bien été mis à jour'")
    data_from_form = {"first_name": "Jhon",
                        "is_submit_button_clicked": True}
    client.force_login(user)  # Log the user in
    response = client.post('/accounts_profile', data_from_form)
    assert ("alert" in str(response.content)
                and "Votre compte a bien " in str(response.content)
                and "mis " in str(response.content)
                and "jour" in str(response.content))

    print("     should update the user account in the database")
    member = Member.objects.get(username=credentials["username"])
    assert member.first_name == data_from_form["first_name"]


@pytest.mark.test_me
@pytest.mark.integration_test
def test_signup_user(monkeypatch, add_member_to_db):

    def mock_get_credentials(request):
        return _mock_get_credentials(request)

    def mock_check_email_validity(email: str) -> bool:
        if (email
                and isinstance(email, str)
                and email.count("@") == 1):

            right_part = email.split("@")[-1]

            if "." in right_part:
                return True
        return False

    def mock_utils_send_email(email, email_content):
        if email == "email@failed.com":
            return False
        return True

    monkeypatch.setattr("app_accounts.views._get_credentials", mock_get_credentials)
    monkeypatch.setattr("utils.utils.check_email_validity", mock_check_email_validity)
    monkeypatch.setattr("utils.utils.send_email", mock_utils_send_email)

    print("If username (email) is missing then "
            "should alert 'Le champ doit être rempli !'")
    response = client.post('/accounts_signup', {"username": ""})

    assert ("alert" in str(response.content)
            and "Le champ doit" in str(response.content)
            and "tre rempli" in str(response.content))

    print("If username (email) is malformed then "
            "should alert 'Email incorrect !'")
    response = client.post('/accounts_signup', {"username": "toto@email"})
    assert ("alert" in str(response.content)
            and "Email incorrect" in str(response.content))

    print("If username (email) contains more than 150 characters then "
            "should alert 'Email trop long !'")
    response = client.post('/accounts_signup', {"username": "t" *141 + "@email.com"})
    assert ("alert" in str(response.content)
            and "Email trop long" in str(response.content))

    print("If the method of the request is not POST then "
            "should render the file 'app_accounts/signup.html' without doing anything")
    response = client.get('/accounts_signup', {"username": "t" *141 + "@email.com"})
    assertTemplateUsed(response, 'app_accounts/signup.html')

    print("If user is already registered then "
            "should alert 'Cet utilisateur est déjà enregistré !'")
    user = add_member_to_db  # Fixture
    response = client.post('/accounts_signup', {"username": user.username})
    assert ("alert" in str(response.content)
            and "Cet utilisateur est d" in str(response.content)
            and "enregistr" in str(response.content))

    print("If the email that contains the OTP has not been sent then "
            "should wait a while before "
            "redirecting to the 'complete_the_registration' page")
    response = client.post(
        '/accounts_signup',
        {"username": "email@failed.com"},
        follow=True)
    assert (response.redirect_chain[0][0] == "/accounts_complete_the_registration")

    print("If user is not already registered then "
            "should redirect to the 'complete_the_registration' page")
    response = client.post(
        '/accounts_signup',
        {"username": "new@user.fr"},
        follow=True)
    assert (response.redirect_chain[0][0] == "/accounts_complete_the_registration")
    