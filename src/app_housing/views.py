import logging

from django.shortcuts import redirect, render
from django.http import HttpResponse
from app_accounts.models import Member
from django.contrib import messages

from icecream import ic

from utils import utils


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
    houses = [house for house in houses if not house.is_removed]

    return render(request, "app_housing/host-home.html", context={"houses": houses})


def create_or_update_house(request):
    visitor = request.user
    if not (visitor.is_authenticated and visitor.is_host):
        return redirect('housing_home')

    capacity = request.POST.get('capacity', "")
    city = request.POST.get('city', "")
    nbr_n_street = request.POST.get('city', "")
    zip = request.POST.get('city', "")
    picture_front_of_house = request.POST.get('picture_front_of_house', "")
    picture_of_bedroom = request.POST.get('picture_of_bedroom', "")
    other_picture = request.POST.get('other_picture', "")
    other_picture = request.POST.get('other_picture', "")
    message_of_presentation_of_house = request.POST.get('message_of_presentation_of_house', "")
    is_available = request.POST.get('is_available', "")

    house_to_update = None

    if id_of_house_to_update := request.POST.get('id_of_house_to_update', ""):
        try:
            house_to_update = visitor.list_of_houses.get(id=id_of_house_to_update)
            house_to_update.capacity = capacity or house_to_update.capacity
            house_to_update.city = city or house_to_update.city
            house_to_update.nbr_n_street = nbr_n_street or house_to_update.nbr_n_street
            house_to_update.zip = zip or house_to_update.zip
            house_to_update.picture_of_bedroom = (
                picture_of_bedroom
                or house_to_update.picture_of_bedroom)

            house_to_update.other_picture = other_picture or house_to_update.other_picture
            house_to_update.message_of_presentation_of_house = (
                message_of_presentation_of_house
                or house_to_update.message_of_presentation_of_house)

            house_to_update.is_available = (
                is_available
                or house_to_update.is_available)

            house_to_update.picture_front_of_house = (
                picture_front_of_house
                or house_to_update.picture_front_of_house)

            house_to_update.save()
            print()
            print()
            print("HOUSE IN ", house_to_update.city)
            print()
            print()
        except Exception as e:
            logging.error("Couldn't find house to update from the houses of the visitor")
            messages.error(request, ("Une erreur inattendue est arrivée ! Contactez les développeurs."))

    return render(request, "app_housing/create-or-update-house.html", context={"house": house_to_update})


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
