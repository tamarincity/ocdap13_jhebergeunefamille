import time

import pytest
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from app_accounts.constants import (
        LARA_CITY,
        LARA_FAKE_OTP,
        LARA_NBR_N_STREET,
        LARA_ZIP_CODE,
        USER_LARA_CROFT_HOMELESS,
        USER_LARA_CROFT_OWNER,
)
from src.utils import utils


PRODUCTION_DOMAIN_NAME = "http://128.199.39.96/"
PORT = "5550"
DEV_DOMAIN_NAME = "http://localhost:" + PORT

DOMAIN_NAME = DEV_DOMAIN_NAME
# DOMAIN_NAME = "https://yopmail.com/fr/wm"


@pytest.mark.functional_test
@pytest.mark.usefixtures("init_driver")  # From conftest.py - Select and initialyze the driver
class TestApplication:
    def test_signup(self):
        global DOMAIN_NAME
        if DOMAIN_NAME == PRODUCTION_DOMAIN_NAME:
            SPECIAL_COLOR = "\033[1;33;41m"
            NORMAL_COLOR = "\033[0;0;0m"
            print()
            print(SPECIAL_COLOR + "------------!!! THE TESTED DOMAINE NAME IS "
                    "THE ONE FOR PRODUCTION !!!-------------", end="")
            print(NORMAL_COLOR)
        try:
            driver = self.driver
            find = driver.find_element_by_xpath

            # Remove fake users from database
            driver.get(DOMAIN_NAME + "/accounts_delete_fake_users")

            # Go to home page
            print("No characters after the domain name should take the user to the home page")
            driver.get(DOMAIN_NAME)
            time.sleep(2)
            h1_content = find("//h1").text
            assert "famille" in h1_content

            # Owner ==============================

            # Click on the signup link
            print("Clicking on the signup link should redirect to the signup page ")
            find("//a[@id='signup']").click()
            time.sleep(2)
            h2_content = find("//h2").text
            assert "S'inscrire" in h2_content

            # Enter a malformed email address to signup
            print("Entering a malformed email address in the field and submit")
            field_enter_email = find("//input[@id='username']")
            field_enter_email.send_keys("wrong@email")
            print("     should let the user on the same page")
            # Click on the submit btn
            find("//button[@id='submitButton']").click()
            h2_content = find("//h2").text
            assert "S'inscrire" in h2_content

            # Enter an wellformed email address to signup
            print("Entering a wellformed email address in the field")
            field_enter_email = find("//input[@id='username']")
            field_enter_email.send_keys(USER_LARA_CROFT_OWNER["username"])
            print("then click on the submit button shoud redirect to the form "
                  "to continue registration")
            # Click on the submit btn
            find("//button[@id='submitButton']").click()
            time.sleep(2)
            assert "Terminer l'inscription" in driver.page_source

            print("Filling the form as a owner and submit "
                  "should take the user to his host-home page’")
            # Fill the form
            field_otp = find("//input[@id='otp']")
            field_otp.send_keys(LARA_FAKE_OTP)
            field_pseudo = find("//input[@id='pseudo']")
            field_pseudo.send_keys(USER_LARA_CROFT_OWNER["pseudo"])
            field_first_name = find("//input[@id='first_name']")
            field_first_name.send_keys(USER_LARA_CROFT_OWNER["first_name"])
            field_password = find("//input[@id='password']")
            field_password.send_keys(USER_LARA_CROFT_OWNER["password"])
            option_is_host = Select(driver.find_element_by_id('is_offering_accommodation'))
            option_is_host.select_by_visible_text('Je propose un logement gratuitement')

            # Scroll down and valid the form
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            find("//button[@type='submit']").send_keys(Keys.ENTER)
            time.sleep(2)
            assert "Ajouter un logement" in driver.page_source

            print("Clicking on the ‘add house’ button "
                  "should take the user to the ‘add info of house page’")

            find("//a[@href='housing_create_or_update_house']").click()
            time.sleep(2)
            assert "Modification de logement" in driver.page_source

            print("Filling the required fields properly and validate the form "
                  "should take the user to his host-home page with the new house "
                  "added on his list of houses")

            # Fill the form
            field_capacity = find("//input[@id='capacity-input']")
            field_capacity.send_keys("3")
            field_city = find("//input[@id='city']")
            field_city.send_keys(LARA_CITY)
            field_zip_code = find("//input[@id='zip_code']")
            field_zip_code.send_keys(LARA_ZIP_CODE)
            field_nbr_n_street = find("//input[@id='nbr_n_street']")
            field_nbr_n_street.send_keys(LARA_NBR_N_STREET)

            # Scroll down and valid the form
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            find("//button[@id='submitButton']").send_keys(Keys.ENTER)
            time.sleep(2)

            print("Clicking on the logout icon "
                  "should take to the normal home page as a not logged user")

            find("//a[@id='logout']").click()
            assert "Je recherche un logement pour" in driver.page_source
            assert "login" in driver.page_source

            # Person in need of housing ==============================

            # Click on the signup link
            print("Clicking on the signup link should redirect to the signup page ")
            find("//a[@id='signup']").click()
            time.sleep(2)
            h2_content = find("//h2").text
            assert "S'inscrire" in h2_content

            # Enter an wellformed email address to signup
            print("Entering a wellformed email address in the field")
            field_enter_email = find("//input[@id='username']")
            field_enter_email.send_keys(USER_LARA_CROFT_HOMELESS["username"])
            print("then click on the submit button shoud redirect to the form "
                  "to continue registration")
            # Click on the submit btn
            find("//button[@id='submitButton']").click()
            time.sleep(2)
            assert "Terminer l'inscription" in driver.page_source

            print("Filling the form as a person in need of house and submit "
                  "should take the user to the normal home page as a logged member")
            # Fill the form
            field_otp = find("//input[@id='otp']")
            field_otp.send_keys(LARA_FAKE_OTP)
            field_pseudo = find("//input[@id='pseudo']")
            field_pseudo.send_keys(USER_LARA_CROFT_HOMELESS["pseudo"])
            field_first_name = find("//input[@id='first_name']")
            field_first_name.send_keys(USER_LARA_CROFT_HOMELESS["first_name"])
            field_password = find("//input[@id='password']")
            field_password.send_keys(USER_LARA_CROFT_HOMELESS["password"])
            option_is_host = Select(driver.find_element_by_id('is_offering_accommodation'))
            option_is_host.select_by_visible_text("Je suis à la recherche d'un logement")

            # Scroll down and valid the form
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            find("//button[@type='submit']").send_keys(Keys.ENTER)
            time.sleep(2)
            assert "logout" in driver.page_source

            print("Entering un number in the search bar")
            print("     should take the user to the list of cities that have houses "
                  "corresponding to the capacity asked for.")

            field_capacity = find("//input[@id='search-nbr']")
            field_capacity.send_keys("2")
            find("//button[@id='magnifier']").send_keys(Keys.ENTER)
            time.sleep(2)
            assert "Villes" in driver.page_source

            print("Clicking on a city should take the user to the list of "
                  "corresponding houses in the selected city")

            find("//a[contains(@href,'housing_houses_or_cities')]").click()
            time.sleep(2)
            assert "Peut accueillir" in driver.page_source

            print("Clicking on a house "
                  "should display the details and the owner of the house")

            find("//a[contains(@href,'housing_house-details')]").click()
            time.sleep(2)
            assert "Peut accueillir" in driver.page_source
            assert "Pseudo" in driver.page_source

            print("Entering a message and submitting it ")
            print("     should let the user on the same page "
                  "and display the alert : ‘Le message a bien été envoyé’")

            textarea = find("//textarea[@id='text-area-send-message-to-host']")
            textarea.send_keys("J'ai été envoyé automatiquement via un test fonctionnelle")
            find("//button[text()='Envoyer un message']").send_keys(Keys.ENTER)
            time.sleep(3)
            assert "Le message a bien été envoyé" in driver.page_source

            print("Clicking on the logout icon "
                  "should take to the normal home page as a not logged user")

            find("//a[@id='logout']").click()
            assert "Je recherche un logement pour" in driver.page_source
            assert "login" in driver.page_source

            driver.get(DOMAIN_NAME + "/accounts_delete_fake_users")

        except Exception as e:
            driver.save_screenshot("screenshot_of fail.png")
            print("TEST FAILED! Reason: ", str(e))
            if "connection" in str(e).lower():
                assert "Functional test failed! Maybe the server is not running." in str(e)
            else:
                assert "Functional test failed!" in ""
