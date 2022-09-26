from django.test import Client

import pytest
from pytest_django.asserts import assertTemplateUsed

from utils import utils
from app_housing.models import House
from app_accounts.models import Member
from app_housing import views
from app_housing.views import (
    home,
)


client = Client()

# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

credentials = {
                "username": "toto@email.fr",
                "pseudo": "Latêtatoto",
                "first_name": "Toto",
                "last_name": "DUPONT",
                "email": "toto@email.fr",
                "password": "12345678",
                "is_submit_button_clicked": "yes"}


@pytest.fixture
def add_member_to_db():
    return Member.objects.create_user(
                pseudo=credentials["pseudo"],
                username=credentials["username"],
                first_name=credentials["first_name"],
                password=credentials["password"],
                email=credentials["username"])


@pytest.fixture
def add_host_to_db():
    return Member.objects.create_user(
                pseudo="Proprio",
                username="proprio@mail.fr",
                first_name="Vincent",
                password="12345678",
                email="proprio@mail.fr",
                is_host = True)


@pytest.fixture
def add_in_need_person_to_db():
    return Member.objects.create_user(
                pseudo="Help-Me",
                username="in@need.fr",
                first_name="Alain",
                last_name="RUE",
                password="12345678",
                email="in@need.fr",
                is_host = False)


@pytest.fixture
def add_1_house_to_db(add_host_to_db) -> tuple:
    """Create a house with its owner then return a tuple containing:
    host, house.
    The host is the owner of the house"""

    host = add_host_to_db  # Fixture. A house requires a host (owner)

    House.objects.get_or_create(
        owner=host,
        city="Paris",
        nbr_n_street="4 rue de Balades",
        message_of_presentation_of_house="",
        is_available=True)

    house = House.objects.get(owner=host)
    return host, house


@pytest.mark.integration_test
def test_home(add_in_need_person_to_db, add_host_to_db):

    # Create registered users using fixtures
    in_need_person = add_in_need_person_to_db
    host = add_host_to_db

    print("If the user is an in need person then he should be taken to the normal home-page.")
    client.force_login(in_need_person)  # Log the user in
    response = client.get('/')
    assertTemplateUsed(response, 'app_housing/home.html')
    client.logout()

    print("If the user is a host then he should be taken to then host-home-page")
    client.force_login(host)  # Log the user in
    response = client.get('/housing_home', follow=True)
    assert "Mes logements" in str(response.content)
    client.logout()


@pytest.mark.integration_test
def test_host_home(add_in_need_person_to_db, add_host_to_db, add_1_house_to_db):

    # Create registered users using fixtures
    in_need_person = add_in_need_person_to_db
    host = add_host_to_db

    print("If the user is not a host then he should be redirected to the normal home-page")
    client.force_login(in_need_person)  # Log the user in
    response = client.get('/housing_host-home', follow=True)
    assert "Je recherche un logement pour" in str(response.content)
    client.logout()

    print("If the user is a host then")
    print("     should display his list of houses")
    house = add_1_house_to_db  # Fixture. Create the user's house in Paris
    client.force_login(host)  # Log the user in
    response = client.get('/housing_host-home', follow=True)
    assert "Paris" in str(response.content)

    print("     should display the button 'Ajouter un logement'")
    assert "Ajouter un logement" in str(response.content)
    client.logout()


@pytest.mark.integration_test
def test_create_or_update_house(monkeypatch, add_1_house_to_db, add_host_to_db):

    class MockHouse():
        def get_or_create(request):
            _, house = add_1_house_to_db
            return house

        def add_pictures_to_house_if_house_exists(*args):
            return True

        def update(
                house_to_update,
                capacity,
                city,
                zip_code,
                nbr_n_street,
                message_of_presentation_of_house,
                is_available):
            house_to_update.capacity = capacity
            house_to_update.city = city
            house_to_update.zip_code = zip_code
            house_to_update.nbr_n_street = nbr_n_street
            house_to_update.message_of_presentation_of_house = message_of_presentation_of_house
            house_to_update.is_available = is_available
            house_to_update.save()
            return True

        def remove_house(*args):
            return True

    monkeypatch.setattr(views, "House", MockHouse)

    print("If the user is not logged then should redirect to the normal home-page.")
    response = client.get('/housing_create_or_update_house', follow=True)
    assert "Je recherche un logement pour" in str(response.content)

    print("if the user is a host then should display the page that allows to update "
          "or create a house")
    client.force_login(add_host_to_db)  # Log the user in
    response = client.get('/housing_create_or_update_house', follow=True)
    assertTemplateUsed(response, 'app_housing/create-or-update-house.html')

    print("If the zip code is not an integer or an integer into a string then "
          "should alert 'Le code postal doit être un nombre entier !'.")
    response = client.post('/housing_create_or_update_house',
                           {"zip_code":"should be an integer or an integer into a string"},
                           follow=True)
    assert ("Le code postal doit " in str(response.content)
            and "tre un nombre entier" in str(response.content))

    print("If the capacity is not an integer or an integer into a string then "
          "should alert 'La capacité doit être un nombre entier !'.")
    response = client.post('/housing_create_or_update_house',
                           {"capacity":"should be an integer or an integer into a string"},
                           follow=True)
    assert ("La capacit" in str(response.content)
            and " doit " in str(response.content)
            and "tre un nombre entier" in str(response.content))

    print("If all the required fields are set then should create the house.")
    response = client.post('/housing_create_or_update_house',
                           {"is_available":"true",
                            "capacity":2,
                            "city":"Lyon",
                            "zip_code":"45123",
                            "nbr_n_street":"18 rue Trop Cool",
                            "house_to_update":House.objects.get(id=1)},
                           follow=True)
    assert "Les nouvelles informations ont bien" in str(response.content)
    modified_house = House.objects.get(id=1)
    assert modified_house.is_available == True

    print("If is avialable is set to 'false' in the form then should turn the house "
          "to unavailable")
    response = client.post('/housing_create_or_update_house',
                           {"is_available":"false",
                            "capacity":2,
                            "city":"Lyon",
                            "zip_code":"45123",
                            "nbr_n_street":"18 rue Trop Cool",
                            "house_to_update":House.objects.get(id=1)},
                           follow=True)
    modified_house = House.objects.get(id=1)
    assert modified_house.is_available == False
    client.logout()


@pytest.mark.integration_test
def test_get_all_elements_with_available_rooms(monkeypatch, add_in_need_person_to_db):

    class MockHouse():
        def get_elements_by_capacity(
                capacity,
                from_id,
                what_to_find,
                total_nbr_of_elements,
                city):
            if what_to_find == "houses":
                return [(1, 2), (2, 2), (3, 4)], 3  # "2 personnes" x2 and "4 personnes" x1
            if what_to_find == "cities":
                return [(city, "Ma Ville sur Mer")], 2

    monkeypatch.setattr(views, "House", MockHouse)

    print("If a city and a capacity is defined in the form then should display a list "
          "of the corresponding houses")
    response = client.get('/housing_houses_or_cities',
                           {"what_to_find":"houses",
                            "city": "Paris",
                            "from_id":"0",
                            "capacity":"2",
                            "total_nbr_of_elements":"0"},
                           follow=True)

    assert ("4&nbsp;personnes" in str(response.content)
            and "2&nbsp;personnes" in str(response.content))

    print("If the user is not logged then should alert: "
          "'Vous devez être connecté pour en savoir plus'")
    assert ("Vous devez " in str(response.content)
            and "tre connect" in str(response.content)
            and " pour en savoir plus" in str(response.content))

    print("If the user is logged then should not alert: "
          "'Vous devez être connecté pour en savoir plus'")
    client.force_login(add_in_need_person_to_db)  # Log the user in
    response = client.get('/housing_houses_or_cities',
                           {"what_to_find":"houses",
                            "city": "Paris",
                            "from_id":"0",
                            "capacity":"2",
                            "total_nbr_of_elements":"0"},
                           follow=True)
    assert not ("Vous devez " in str(response.content)
            or "tre connect" in str(response.content))
    client.logout()


@pytest.mark.integration_test
def test_get_house_details(monkeypatch, add_1_house_to_db, add_in_need_person_to_db):

    registered_house = add_1_house_to_db  # Fixture

    def mock_send_email_to_owner_if_requested(request, Member):
        return True

    def mock_add_to_contacts_if_requested(request, Member):
        return True

    monkeypatch.setattr("utils.utils.send_email_to_owner_if_requested",
                        mock_send_email_to_owner_if_requested)
    monkeypatch.setattr("app_accounts.models.Member.add_to_contacts_if_requested",
                        mock_add_to_contacts_if_requested)

    print("If the user is not logged then should redirect to a 'Page not found'")
    response = client.get('/housing_house-details', {"id":"1"}, follow=True)
    assert "not found" in str(response.content).lower()

    print("If the id of the wanted house is in the request then should display the details of the house")
    client.force_login(add_in_need_person_to_db)  # Log the user in
    response = client.get('/housing_house-details', {"id":"1"}, follow=True)
    assert "Proprio" in str(response.content)


@pytest.mark.integration_test
def test_contact():

    print("If the user click on the contact link then should redirect to the contact page"
          "that displays a form to send a message to the administrator")
    response = client.get('/housing_contact')
    assertTemplateUsed(response, "app_housing/contact.html")


@pytest.mark.test_me
@pytest.mark.integration_test
def test_legal_notice():

    print("If the user click on the 'Mentions légales' link then should "
          "redirect to the legal-notice page")
    response = client.get('/housing_legal_notice')
    assertTemplateUsed(response, "app_housing/legal-notice.html")
