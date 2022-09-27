import random
import string

import pytest

from app_housing.models import House, ReceivedMessage
from app_accounts.models import Member


# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

messages_from_django = []


class Mock_Messages:  # messages.success(request, "blablabla")
        def add(cls, level, message, extra_tags):
            global messages_from_django
            messages_from_django.append(message)
            return

class Mock_request:
    POST = {}
    GET = {}
    _messages = Mock_Messages()  # because of << messages.success(request, "blablabla")>>
    user: "Member" = None


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


@pytest.fixture
def add_house_to_db(add_owner_to_db) -> tuple:
    """Create a house with its owner then return a tuple containing:
    request, visitor, house.
    The visitor is the owner of the house"""

    request = Mock_request()
    visitor = request.user = add_owner_to_db  # Because a house requires an owner

    House.objects.get_or_create(
        owner=visitor,
        city="".join(random.choice(string.ascii_letters) for _ in range(5)),
        nbr_n_street="",
        message_of_presentation_of_house="",
        is_available=True)

    house = House.objects.get(owner=visitor)
    return request, visitor, house


def test_ReceivedMessage__str__():

    sut = ReceivedMessage()

    print("The __str__ method should return the email address of the sender")
    sut.email = "user@email.com"

    assert "user@email.com" in ReceivedMessage.__str__(sut)


def test_House__str__(add_owner_to_db):

    sut = House()

    print("The __str__ method ")
    print("     should return the pseudo of the owner")
    sut.owner = add_owner_to_db

    print("     should return the name of the city where the house is located")
    sut.city = "Béziers"

    assert "Béziers" in House.__str__(sut)


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
    assert "Une erreur inattendue est arrivée ! Contactez les développeurs." in messages_from_django
    messages_from_django.remove("Une erreur inattendue est arrivée ! Contactez les développeurs.")

    print("     should return None (No house created nor returned)")
    assert not isinstance(house, House)


def test_add_pictures_to_house_if_house_exists(add_house_to_db):

    sut = House()

    request, _, house = add_house_to_db  # Fixture

    print("If more than one picture has been sent Then")
    print("     should update the house accordingly")
    assert sut.add_pictures_to_house_if_house_exists(
        request,
        house,
        "file_picture_front_of_house",
        "file_picture_of_bedroom",
        "file_other_picture",
        2,
        "Fort-de-France",
        97200,
        "1 rue Schoelcher") == True

    print("     should alert: 'Les nouvelles photos ont bien été enregistrées'")
    global messages_from_django
    assert "Les nouvelles photos ont bien été enregistrées" in messages_from_django
    messages_from_django.remove("Les nouvelles photos ont bien été enregistrées")

    print("If only one picture has been sent Then")
    print("     should alert: 'La nouvelle photo a bien été enregistrée'")
    sut.add_pictures_to_house_if_house_exists(
        request,
        house,
        "",
        "",
        "file_other_picture",
        2,
        "Fort-de-France",
        97200,
        "1 rue Schoelcher") == True

    assert "La nouvelle photo a bien été enregistrée" in messages_from_django
    messages_from_django.remove("La nouvelle photo a bien été enregistrée")


def test_update(add_house_to_db):

    sut = House()

    _, visitor, house = add_house_to_db  # Fixture

    print("If all the fields are the required type then should update the house accordingly")
    assert sut.update(
        house,
        1,
        "",
        74747,
        "",
        "",
        True) == True

    print(("If one of the args is not the good type then should raise an exception"))
    with pytest.raises(Exception):
        sut.update(
            house,
            "Should be an integer",  # <- This should raise an exception
            "",
            74747,
            "",
            "",
            True)


def test_remove_house(add_house_to_db):

    sut = House()
    request = Mock_request()

    # To remove a house, we need to create it first
    request, *_ = add_house_to_db  # Fixture. << *_ >> means the others are not important

    print("If the house to remove exists then ")
    print("     should remove it")
    request.POST = {"id_of_house_to_remove": "1"}
    assert sut.remove_house(request) == True

    print("     should alert: 'Le logement a été supprimé'")
    global messages_from_django
    assert "Le logement a été supprimé" in messages_from_django
    messages_from_django.remove("Le logement a été supprimé")

    print("If the house to remove has not been found then")
    request.POST = {"id_of_house_to_remove": "100"}
    print("     should return False")
    assert sut.remove_house(request) == False

    print("     should alert: 'Une erreur inattendue est arrivée ! Contactez les développeurs.'")
    assert "Une erreur inattendue est arrivée ! Contactez les développeurs." in messages_from_django
    messages_from_django.remove("Une erreur inattendue est arrivée ! Contactez les développeurs.")


def test_get_elements_by_capacity(add_owner_to_db):

    sut = House()
    request = Mock_request()

    # Creation of 5 houses with different capacities via the fixture 'add_house_to_db'    
    visitor = request.user = add_owner_to_db  # Because a house requires an owner
    city = "Paris"  # City where are located the houses
    wanted_capacity = 2  # Capacity of the wanted houses

    for capacity in range(1,6):
        House.objects.get_or_create(
            capacity=capacity,
            owner=visitor,
            city=city,
            zip_code="12345",
            nbr_n_street="1 rue Machin",
            message_of_presentation_of_house="",
            is_available=True)

    # Set the 3d house as unavailable
    house3 = House.objects.get(id=3)
    house3.is_available = False
    house3.save()

    # Set the 4th house as removed
    house4 = House.objects.get(id=3)
    house4.is_removed = True
    house4.save()

    print("5 houses has been created for this test.")
    assert House.objects.all().count() == 5

    print("     One is unavailable")
    assert House.objects.all().filter(is_available=False).count() == 1

    print("     and another is removed")
    assert House.objects.all().filter(is_removed=True).count() == 1

    print("If what are wanted are houses and if the capacity of the "
          "house and the city are in args then")
    elts, total_nbr_of_elements = sut.get_elements_by_capacity(
        capacity=wanted_capacity,
        from_id=0,
        what_to_find="houses",
        total_nbr_of_elements=0,
        city=city)

    print("     should return all the houses with a greater or equal capacity")
    assert total_nbr_of_elements == 3  # Total nbr of corresponding elements in the database
    assert len(elts) == 3  # Nbr of returned elements

    print(" should not return any elements with a less capacity")
    for elt in elts:
        assert elt[1] >= wanted_capacity  # elt[0] is the id, elt[1] is the capacity.

    print("If the index of the element in the total corresponding elements is "
          "greater than zero then should return only the element with a greater or "
          "equal index")
    elts, total_nbr_of_elements = sut.get_elements_by_capacity(
        capacity=wanted_capacity,
        from_id=2,
        what_to_find="houses",
        total_nbr_of_elements=0,
        city=city)

    print("     should return all the houses with a greater or equal capacity")
    assert total_nbr_of_elements == 3  # Total nbr of corresponding elements in the database
    assert len(elts) == 1  # Nbr of returned elements

    print("If what are wanted are cities then should return all the corresponding cities")
    elts, total_nbr_of_elements = sut.get_elements_by_capacity(
        capacity=wanted_capacity,
        from_id=0,
        what_to_find="cities",
        total_nbr_of_elements=0,
        city=city)
    assert len(elts) == 1
    assert elts[0]["city"] == "Paris"


def test_get_house_by_id(add_house_to_db):

    sut = House()
    add_house_to_db  # Fixture the create a house

    print("if the id corresponds to a house then should return the house")
    house = sut.get_house_by_id(1)
    assert house.id == 1

    print("If no house corresponds to the id then should return None")
    assert sut.get_house_by_id(100) == None
