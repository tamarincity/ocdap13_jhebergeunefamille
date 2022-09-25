import pytest

from app_housing.models import House, ReceivedMessage
from app_accounts.models import Member


# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

Sut1 = ReceivedMessage
Sut2 = House

credentials = {
                "username": "toto@email.fr",
                "pseudo": "Latêtatoto",
                "first_name": "Toto",
                "last_name": "DUPONT",
                "email": "toto@email.fr",
                "password": "12345678",
                "is_submit_button_clicked": "yes"}


@pytest.fixture
def add_visitor_to_db():
    return Member.objects.create_user(
                pseudo="V-Lezard",
                username="visi@go.fr",
                first_name="Visigoth",
                password="12345678",
                email="visi@go.fr")


@pytest.fixture
def add_owner_to_db():
    return Member.objects.create_user(
                pseudo="GI Joe",
                username="gi@joe.com",
                first_name="Joe",
                password="12345678",
                email="gi@joe.com")


messages_from_django = ""


class Mock_Messages:  # messages.success(request, "blablabla")
        def add(cls, level, message, extra_tags):
            global messages_from_django
            messages_from_django = message
            return

class Mock_request:
    POST = {}
    GET = {}
    _messages = Mock_Messages()  # because of << messages.success(request, "blablabla")>>
    user: "Member" = None


def test_ReceivedMessage__str__():

    sut = ReceivedMessage()

    print("The __str__ method should return the email address of the sender")
    sut.email = "user@email.com"

    assert "user@email.com" in Sut1.__str__(sut)


def test_House__str__(add_owner_to_db):

    sut = House()

    print("The __str__ method ")
    print("     should return the pseudo of the owner")
    sut.owner = add_owner_to_db

    print("     should return the name of the city where the house is located")
    sut.city = "Béziers"

    assert "Béziers" in Sut2.__str__(sut)

@pytest.mark.test_me
def test_House_get_or_create(add_owner_to_db):

    sut = House()

    request = Mock_request()

    print("If the house doesn't exist, then")
    visitor = request.user = add_owner_to_db  # Fixture that create the web site visitor
    print("       this method creates it")
    house = sut.get_or_create(request)
    assert isinstance(house, House)

    print("     The owner of the house should be the current visitor")
    assert house.owner == visitor

    print("if the house already exists, then return it")
    request.POST["id_of_house_to_update"] = 1
    house = sut.get_or_create(request)
    assert isinstance(house, House)

    print("     The owner of the house should be the current visitor")
    assert house.owner == visitor

    print("if id of the house doesn't exist, then ")
    print("     should alert: 'Une erreur inattendue est arrivée ! Contactez les développeurs.'")
    request.POST["id_of_house_to_update"] = 100
    house = sut.get_or_create(request)
    global messages_from_django
    assert messages_from_django == (
        "Une erreur inattendue est arrivée ! Contactez les développeurs.")

    print("     should return None (No house created nor returned)")
    assert not isinstance(house, House)
    messages_from_django = ""