import logging
from typing import TypeVar

from django.db import models
from django.conf import settings
from django.contrib import messages

from app_accounts.models import Member


class House(models.Model):
    capacity = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(
        Member, related_name="list_of_houses", on_delete=models.CASCADE)

    city = models.CharField(max_length=100, null=True, blank=True)
    nbr_n_street = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.IntegerField(null=True, blank=True)
    picture_front_of_house = models.ImageField(
        upload_to=settings.PICTURES_FRONT_OF_HOUSES_DIRECTORY,
        blank=True,
        null=True,
        help_text="picture of the front of the house")

    picture_of_bedroom = models.ImageField(
        upload_to=settings.PICTURES_OF_BEDROOMS_DIRECTORY,
        blank=True,
        null=True,
        help_text="picture of the bedroom")

    other_picture = models.ImageField(
        upload_to=settings.OTHER_PICTURES_DIRECTORY,
        blank=True,
        null=True,
        help_text="other picture of the house")

    url_picture_front_of_house = models.TextField(default="", max_length=255, blank=True, null=True)
    url_picture_of_bedroom = models.TextField(default="", max_length=255, blank=True, null=True)
    url_other_picture = models.TextField(default="", max_length=255, blank=True, null=True)

    message_of_presentation_of_house = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "<< A house >>"
        verbose_name_plural = "list of houses"

    def __str__(self):
        return f"city: {self.city}, owner: {self.owner}"

    @classmethod
    def get_or_create(cls, request) -> "House":
        """Get or create a house.
        Return: house_to_update (instance of House)"""
        visitor = request.user

        # Get the id of the house to update from the request
        if id_of_house_to_update := request.POST.get('id_of_house_to_update', ""):
            print("id of house to update: ", id_of_house_to_update)
            try:
                # Get the involved house from the database
                house_to_update = visitor.list_of_houses.get(id=id_of_house_to_update)
            except Exception as e:
                logging.error("Couldn't find house to update from the houses of the visitor")
                logging.error(str(e))
                messages.error(request, ("Une erreur inattendue est arrivée ! Contactez les développeurs."))

        else:
            # Creation of a temporary house
            house_to_update = House.objects.get_or_create(
                owner=visitor,
                city="",
                nbr_n_street="",
                message_of_presentation_of_house="",
                is_available=True)

            house_to_update = visitor.list_of_houses.get(city="")
            id_of_house_to_update = house_to_update.id

        return house_to_update

    @classmethod
    def add_pictures_to_house_if_house_exists(
            cls,
            request,
            house_to_update,
            file_picture_front_of_house,
            file_picture_of_bedroom,
            file_other_picture,
            capacity,
            city,
            zip_code,
            nbr_n_street) -> True:
        """Adding pictures to the existing or temporary house if required fields are filled"""

        are_required_fields_filled = False
        if ((house_to_update.capacity
                and house_to_update.city
                and house_to_update.zip_code
                and house_to_update.nbr_n_street)
            or capacity
            or city
            or zip_code
            or nbr_n_street):

            are_required_fields_filled = True

        nbr_of_uploaded_pictures = 0
        if file_picture_front_of_house and are_required_fields_filled:
            house_to_update.picture_front_of_house = file_picture_front_of_house
            house_to_update.url_picture_front_of_house = (
                settings.AWS_DOMAIN_NAME
                + settings.PICTURES_FRONT_OF_HOUSES_DIRECTORY
                + str(file_picture_front_of_house))
            nbr_of_uploaded_pictures += 1
            print()
            print()
            print("Url de l'image principale: ", house_to_update.url_picture_front_of_house)
            print()

        if file_picture_of_bedroom and are_required_fields_filled:
            house_to_update.picture_of_bedroom = file_picture_of_bedroom
            house_to_update.url_picture_of_bedroom = (
                settings.AWS_DOMAIN_NAME
                + settings.PICTURES_OF_BEDROOMS_DIRECTORY
                + str(file_picture_of_bedroom))
            nbr_of_uploaded_pictures += 1

        if file_other_picture and are_required_fields_filled:
            house_to_update.other_picture = file_other_picture
            house_to_update.url_other_picture = (
                settings.AWS_DOMAIN_NAME
                + settings.OTHER_PICTURES_DIRECTORY
                + str(file_other_picture))
            nbr_of_uploaded_pictures += 1

        house_to_update.save()
        if nbr_of_uploaded_pictures == 1:
            messages.success(request, "La nouvelle photo a bien été enregistrée")
        if nbr_of_uploaded_pictures > 1:
            messages.success(request, "Les nouvelles photos ont bien été enregistrées")

        return True

    @classmethod
    def update(
            cls,
            house: "House",
            capacity: int,
            city: str,
            zip_code: int,
            nbr_n_street: str,
            message_of_presentation_of_house: str,
            is_available: bool) -> True:

        if not (isinstance(house, House)
                and isinstance(capacity, int)
                and isinstance(zip_code, int)
                and isinstance(is_available, bool)
                and isinstance(city, str)
                and isinstance(nbr_n_street, str)
                and isinstance(message_of_presentation_of_house, str)):

            raise Exception("Error: The type of one or more args in 'House.update()' is not correct!")

        house.capacity = capacity
        house.city = city
        house.zip_code = zip_code
        house.nbr_n_street = nbr_n_street
        house.message_of_presentation_of_house = (
                message_of_presentation_of_house)
        house.is_available = is_available

        house.save()
        return True

    @classmethod
    def remove_house(cls, house_id: int):
        return True

    @classmethod
    def get_cities_by_capacity(capacity: int):
        return True

    @classmethod
    def get_id_n_capacity_by_capacity_n_city(capacity_gte_than: int, city: str):
        return True
