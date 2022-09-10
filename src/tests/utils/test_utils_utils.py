import pytest

from utils.utils import check_email

@pytest.mark.test_me
def test_check_email():
    print("If no email is provided, the test will fail.")
    print("If email is falsy then should return False.")

    assert check_email("") == False

    print("If email is not string then should return False.")
    assert check_email(123) == False

    print('If "@" not in email then should return False.')
    assert check_email("wrong.email") == False

    print('If "@." in email then should return False.')
    assert check_email("wrong@.email") == False

    print('If email ends with "." or "@", should return False.')
    assert check_email("wrong@.email") == False

    print("If email is well formed then should return True.")
    assert check_email("good@email.com") == True
