import pytest

from app_accounts.models import Member


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


def test_Member_add_to_contacts_if_requested(add_owner_to_db, add_visitor_to_db):

    Sut = Member

    # Create a owner to get added to the contacts of the visitor
    owner = add_owner_to_db

    class Mock_Messages:
        def add(cls, level, message, extra_tags):
            return

    class Mock_request:
        POST = {"add_to_contact": "true",
                "owner_id": "1",
                "in_need_email": "visi@go.fr"}
        _messages = Mock_Messages()  # because of << messages.success(request, "blablabla")>>
        user = add_visitor_to_db  # Fixture that creates the visitor

    request = Mock_request()

    print("If 'add_to_contact', 'owner_id' and 'in_need_email' have been sent via POST method, then ")
    print("     the owner should be added to the contact list of the visitor. The method returns True")
    assert Sut.add_to_contacts_if_requested(request, Member) == True

    print("If the owner is already in the contacts of the visitor, then ")
    print("     the owner should NOT be added to the contact list one more time. The method returns False")
    assert Sut.add_to_contacts_if_requested(request, Member) == False

    print("If 'add_to_contact', 'owner_id' or 'in_need_email' is falsy, then "
          "should return None")
    request.POST['add_to_contact'] = ""
    assert Sut.add_to_contacts_if_requested(request, Member) == None
