from datetime import datetime, timedelta
from functools import total_ordering
import copy
from pprint import pprint
import time

import pytest
from pytest_django.asserts import assertTemplateUsed

from django.test import Client

from utils import utils
from app_accounts.models import Member
from app_accounts.views import (
    _get_credentials,
    _get_otp_n_pswd_from_request,
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
    response = client.post('/accounts_signup', {"username": "t" * 141 + "@email.com"})
    assert ("alert" in str(response.content)
            and "Email trop long" in str(response.content))

    print("If the method of the request is not POST then "
            "should render the file 'app_accounts/signup.html' without doing anything")
    response = client.get('/accounts_signup', {"username": "tototati@email.com"})
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


@pytest.mark.integration_test
def test_complete_the_registration(monkeypatch):

    now = datetime.now()
    validity_ends_in_ten_minutes = now + timedelta(minutes=10)
    fake_email = "fake@email.com"

    initial_profile = {
        "otp": "0TP_c0D3",
        "pseudo": "tuti",
        "first_name": credentials["first_name"],
        "tel": "0123456789",
        "presentation": "Ceci est un message de présentation",
        "password": credentials["password"],
        "is_offering_accommodation": "true"}

    profile = copy.deepcopy(initial_profile)

    print("If the method of the request is not POST then should "
          "render the 'app_accounts/complete_the_registration.html' page "
          "without doing anything")
    response = client.get('/accounts_complete_the_registration')
    assertTemplateUsed(response, 'app_accounts/complete_the_registration.html')

    print("If the otp is not valid then should alert 'Code OTP non valide !'")
    response = client.post(
        '/accounts_complete_the_registration',
        {"otp": "1nvalid_0TP"})
    assert ("alert" in str(response.content)
            and "Code OTP non valide" in str(response.content))

    # Storing a valid OTP
    utils.global_dict[profile['otp']] = [fake_email, validity_ends_in_ten_minutes]

    print("If no pseudo is provided by the user then should alert "
          "'Un des champs requis n'est pas renseigné'")
    profile["pseudo"] = ""
    response = client.post(
        '/accounts_complete_the_registration',
        profile)
    assert ("alert" in str(response.content)
            and "Un des champs requis n"
            and "est pas renseign" in str(response.content))

    # Reset profile
    profile = copy.deepcopy(initial_profile)

    print("If no first_name is provided by the user then should alert "
          "'Un des champs requis n'est pas renseigné'")
    profile["first_name"] = ""
    response = client.post('/accounts_complete_the_registration', profile)
    assert ("alert" in str(response.content)
            and "Un des champs requis n"
            and "est pas renseign" in str(response.content))

    # Reset profile
    profile = copy.deepcopy(initial_profile)

    print("If no password is provided by the user then should alert "
          "'Un des champs requis n'est pas renseigné'")
    profile["password"] = ""
    response = client.post('/accounts_complete_the_registration', profile)
    assert ("alert" in str(response.content)
            and "Un des champs requis n"
            and "est pas renseign" in str(response.content))

    # Reset profile
    profile = copy.deepcopy(initial_profile)

    print("If the password contains less than 8 characters then should alert "
          "'Le mot de passe doit contenir au moins 8 caractères'")
    profile["password"] = "1234567"
    response = client.post('/accounts_complete_the_registration', profile)
    assert ("alert" in str(response.content)
            and "Le mot de passe doit contenir au moins 8 caract")

    # Reset profile
    profile = copy.deepcopy(initial_profile)

    print("Verifying that the OTP is stored in 'global_dict'...", end=" ")
    if profile["otp"] in utils.global_dict.keys():
        print("OK")
    else:
        print("ERROR!")
        raise Exception("Unable to find the OTP in 'global_dict'")

    print("If everything went well then")
    print("     should remove the otp from 'global_dict'")
    response = client.post('/accounts_complete_the_registration', profile, follow=True)

    time.sleep(3)
    assert profile["otp"] not in utils.global_dict.keys()
    print("     should store the new user to the database")
    try:
        new_user = Member.objects.get(username=fake_email)
    except Member.DoesNotExist:
        # username and email are similar
        raise Exception(f"No user with username '{fake_email}' "
                        "has been stored in the database")

    assert new_user.username == fake_email
    assert new_user.email == fake_email
    assert new_user.pseudo == profile["pseudo"]
    assert new_user.first_name == profile["first_name"]
    assert new_user.phone == profile["tel"]
    assert new_user.message_of_presentation == profile["presentation"]

    print("     should redirect to the home page")
    assert (response.redirect_chain[0][0] == "/")  # redirect_chain = [('/', 302)]

    print("     shoulde alert 'Bienvenue, vous êtes connecté !' "
          "because the user is now logged in")
    assert ("Bienvenue, vous " in str(response.content)
            and "tes connect" in str(response.content))


@pytest.mark.integration_test
def test_get_otp_n_pswd_from_request():

    request = MockRequest("POST_OTP_N_PSWD")

    print("Should get OTP and password sent by the user via a form with POST method")
    assert _get_otp_n_pswd_from_request(request) == ("Je 5u1s l3 c0de 0TP", "new_password")


@pytest.mark.integration_test
def test_forgoten_pswd(monkeypatch):

    now = datetime.now()
    otp_end_datetime = now + timedelta(minutes=OTP_VALIDITY_DURATION_IN_MINUTE)

    def mock_get_credentials(request):
        return _mock_get_credentials(request)

    def mock_check_mail_validity(email: str) -> bool:
        if (email
                and isinstance(email, str)
                and email.count("@") == 1):

            right_part = email.split("@")[-1]

            if "." in right_part:
                return True
        return False

    def mock_create_otp():
        return "I_4m_the_0TP", otp_end_datetime

    def mock_send_email(email: str, email_content: str) -> None:
        if "must_fail" in email:
            return False
        return True

    class MockMember():
        class objects():

            def get(username):
                class Toto():
                    def __init__(self, email):
                        self.username = email
                        self.password = credentials["password"]
                        self.otp = "Th3_old_0TP"
                        self.otp_validity_end_datetime = None

                    def save(self):
                        return
                if (username == credentials["username"]
                        or "must_fail" in username):
                    return Toto(username)

    monkeypatch.setattr("app_accounts.views._get_credentials", mock_get_credentials)
    monkeypatch.setattr("utils.utils.check_email_validity", mock_check_mail_validity)
    monkeypatch.setattr("utils.utils.create_otp", mock_create_otp)
    monkeypatch.setattr("utils.utils.send_email", mock_send_email)
    monkeypatch.setattr("app_accounts.views.Member", MockMember)

    print("No email provided should alert 'Vous devez entrer votre adresse e-mail !'")
    response = client.post(
        '/accounts_forgoten_pswd', {})
    assert "Vous devez entrer votre adresse e-mail" in str(response.content)

    print("If the email is malformed should display the page 'forgotten password' again")
    response = client.post(
        '/accounts_forgoten_pswd', {"username": "malformed@email"})
    assert "Mot de passe oubli" in str(response.content)

    print("If the email is not registered then "
            "should redirect to the page 'app_accounts/new_pswd.html'")
    print("     because for security reasons, the user must not know "
          "if this email is registered on the site.")
    response = client.post(
        '/accounts_forgoten_pswd',
        {"username": "unregistered@email.com"},
        follow=True)
    assertTemplateUsed(response, 'app_accounts/new_pswd.html')

    print("If the email is already registered but something went wrong "
            "while sending the email then")
    print("     should alert 'Une erreur inattendue est survenue'")
    response = client.post(
        '/accounts_forgoten_pswd', {"username": "sending.email@must_fail.com"})
    assert "Une erreur inattendue est survenue " in str(response.content)

    print("     should display the same form again")
    assert "Mot de passe oubli" in str(response.content)

    print("If the email is already registered and if an email has been sent "
            "then should redirect to the 'Enter your new password' page")
    response = client.post(
        '/accounts_forgoten_pswd',
        {"username": credentials["username"]},
        follow=True)  # To follow the redirection
    assert (response.redirect_chain[0][0] == "/accounts_new_pswd")  # Because follow=True


@pytest.mark.test_me
@pytest.mark.integration_test
def test_new_pswd(monkeypatch):

    now = datetime.now()
    otp_end_datetime = now + timedelta(minutes=OTP_VALIDITY_DURATION_IN_MINUTE)

    # Creation of a registered user so that we should be able to change his password
    Member.objects.get_or_create(
        username='calamity@jane.com',
        email='calamity@jane.com',
        password="old_p4SSw0rD",
        first_name="Jane",
        last_name="Calamity",)

    utils.global_dict["R1ght_0TP"] = ['calamity@jane.com', otp_end_datetime]

    def mock_get_otp_n_pswd_from_request(request):
        return request.POST.get('otp', None), request.POST.get('password', None)

    monkeypatch.setattr(
        "app_accounts.views._get_otp_n_pswd_from_request", mock_get_otp_n_pswd_from_request)

    print("If no OTP is provided from the form then should display the "
            "message: 'Tous les champs doivent être remplis'")
    response = client.post("/accounts_new_pswd", {"password": "new_PA55W0rd"})
    assert 'Tous les champs doivent ' in str(response.content)
    assert 'tre remplis' in str(response.content)

    print("If no password is provided from the form then should display the "
            "message: 'Tous les champs doivent être remplis'")
    response = client.post("/accounts_new_pswd", {"otp": "R1ght_0TP"})
    assert 'Tous les champs doivent ' in str(response.content)
    assert 'tre remplis' in str(response.content)

    print("If a wrong OTP is provided from the form then should display the "
            "message: 'Code OTP non valide'")
    response = client.post(
        "/accounts_new_pswd", {"otp": "Wr0ng_0TP", "password": "N3w_passw0rd"})
    assert 'Code OTP non valide ' in str(response.content)

    print("If the right OTP is provided from the form then")
    print("     should redirect to the home page")
    response = client.post(
        "/accounts_new_pswd",
        {"otp": "R1ght_0TP", "password": "N3w_passw0rd"},
        follow=True)  # To follow the redirection
    print("=======================================")
    print("response.content")
    print(response.content)
    print()
    assertTemplateUsed(response, 'app_housing/home.html')
    assert (response.redirect_chain[0][0] == "/")  # Because follow=True

    print("     should alert "
          "'Votre mot de passe a bien été mis à jour. Vous êtes connecté.' ")
    assert ("Votre mot de passe a bien " in str(response.content)
            and " mis " in str(response.content)
            and " jour. Vous " in str(response.content)
            and "tes connect" in str(response.content))

    print("     should display the link to logout because "
            "the user is automatically logged in")
    assert "logout" in str(response.content)
