import logging
from datetime import datetime

from django.shortcuts import redirect, render
from django.http import HttpResponse
from app_accounts.models import Member
from django.contrib import messages
from django.conf import settings

from icecream import ic
import environ

from app_housing.models import House
from app_housing.forms import UploadFileForm
from utils import utils
from app_housing.constants import (
    PICTURES_FRONT_OF_HOUSES_DIRECTORY,
    PICTURES_OF_BEDROOMS_DIRECTORY,
    OTHER_PICTURES_DIRECTORY,
)


def home(request):
    visitor = request.user
    if visitor.is_authenticated and visitor.is_host:
        return redirect('housing_host_home')
    return render(request, "app_housing/home.html")


def host_home(request):
    visitor = request.user
    if not (visitor.is_authenticated and visitor.is_host):
        return redirect('housing_home')

    # Removing a house if required
    if id_of_house_to_remove := request.POST.get('id_of_house_to_remove', ""):
        try:
            house_to_remove = visitor.list_of_houses.get(id=id_of_house_to_remove)
            house_to_remove.is_removed = True
            house_to_remove.save()
        except Exception as e:
            logging.error("Couldn't find house to remove from the houses of the visitor")
            messages.error(request, ("Une erreur inattendue est arrivée ! Contactez les développeurs."))

    houses = visitor.list_of_houses.all()
    houses = [house for house in houses if not house.is_removed and house.city]

    return render(request, "app_housing/host-home.html", context={"houses": houses})


def _get_or_create_house(request) -> "House":
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


def _add_pictures_to_house_if_house_exists(
        request,
        house_to_update,
        file_picture_front_of_house,
        file_picture_of_bedroom,
        file_other_picture):
    """Adding pictures to the existing or temporary house if required fields are filled"""

    are_required_fields_filled = False
    if (house_to_update.capacity
            and house_to_update.city
            and house_to_update.zip
            and house_to_update.nbr_n_street):

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


def create_or_update_house(request):
    list(messages.get_messages(request))  # Clear all system messages
    visitor = request.user
    if not (visitor.is_authenticated and visitor.is_host):
        return redirect('housing_home')

    house_to_update = _get_or_create_house(request)

    # Getting files (pictures) from the form
    form = UploadFileForm(request.POST, request.FILES)  # Get the django form (where is upload system)
    file_picture_front_of_house = request.FILES.get('file_picture_front_of_house')
    file_picture_of_bedroom = request.FILES.get('file_picture_of_bedroom')
    file_other_picture = request.FILES.get('file_other_picture')

    # Adding pictures to the existing or temporary house if required fields are filled
    _add_pictures_to_house_if_house_exists(
        request,
        house_to_update,
        file_picture_front_of_house,
        file_picture_of_bedroom,
        file_other_picture)

    # Getting data from request
    capacity = request.POST.get('capacity', "")
    city = request.POST.get('city', "")
    nbr_n_street = request.POST.get('nbr_n_street', "")
    zip = request.POST.get('zip', "")
    message_of_presentation_of_house = request.POST.get('message_of_presentation_of_house', "")
    is_available = request.POST.get('is_available', "")

    if is_available == "false":
        is_available = False
    elif is_available == "true":
        is_available = True

    try:
        capacity = int(capacity) if capacity else None

    except Exception as e:
        messages.error(request, "La capacité doit être un nombre entier !")
        return render(request,
                      "app_housing/create-or-update-house.html",
                      context={"house": house_to_update, "form": form})

    try:
        zip = int(zip) if zip else None

    except Exception as e:
        messages.error(request, "Le code postal doit être un nombre entier !")
        return render(request,
                      "app_housing/create-or-update-house.html",
                      context={"house": house_to_update, "form": form})

    # If the required fields are filled
    if (capacity
            and city
            and zip
            and nbr_n_street
            and house_to_update):  # If it's an update of the house

        # If the data of the house and the one from the form are NOT similar
        if not (house_to_update.capacity == capacity
                and house_to_update.city == city
                and house_to_update.zip == zip
                and house_to_update.nbr_n_street == nbr_n_street
                and house_to_update.message_of_presentation_of_house == (
                    message_of_presentation_of_house)
                and house_to_update.is_available == is_available):

            # Updating the house
            house_to_update.capacity = capacity
            house_to_update.city = city
            house_to_update.zip = zip
            house_to_update.nbr_n_street = nbr_n_street
            house_to_update.message_of_presentation_of_house = (
                    message_of_presentation_of_house)
            house_to_update.is_available = is_available

            house_to_update.save()

            messages.success(request, "Les nouvelles informations ont bien été enregistrées")
            return redirect('housing_home')

    return render(request, "app_housing/create-or-update-house.html", context={"house": house_to_update, "form": form})


def get_all_cities_with_available_rooms(request):
    return HttpResponse("get_all_cities_with_available_rooms is coming soon")


def add_to_contacts(request):
    return HttpResponse("add_to_contacts is coming soon")


def contact(request):
    return HttpResponse("contact is coming soon")


def details(request):
    return HttpResponse("details is coming soon")


def get_my_houses(request):
    return HttpResponse("get_my_houses is coming soon")


def get_my_contacts(request):
    return HttpResponse("get_my_contacts is coming soon")


def get_message(request):
    return HttpResponse("get_message is coming soon")


def get_origial_product(request):
    return HttpResponse("get_origial_product is coming soon")


def get_substitutes(request):
    return HttpResponse("get_substitutes is coming soon")


def legal_notice(request):
    return HttpResponse("legal_notice is coming soon")
