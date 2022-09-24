import logging
from datetime import datetime

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from icecream import ic
import environ

from app_accounts.models import Member
from app_housing.models import House, ReceivedMessage
from app_housing.forms import UploadFileForm
from utils import utils
from app_housing.constants import (
    NBR_MAX_OF_ELEMENTS_TO_DISPLAY,
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

    # Removing a house if button remove has been pressed
    House.remove_house(request)

    houses = visitor.list_of_houses.all()
    houses = [house for house in houses if not house.is_removed and house.city]

    return render(request, "app_housing/host-home.html", context={"houses": houses})


def create_or_update_house(request):
    list(messages.get_messages(request))  # Clear all system messages
    visitor = request.user
    if not (visitor.is_authenticated and visitor.is_host):
        return redirect('housing_home')

    house_to_update = House.get_or_create(request)

    # Getting files (pictures) from the form
    form = UploadFileForm(request.POST, request.FILES)  # Get the django form (where is upload system)
    file_picture_front_of_house = request.FILES.get('file_picture_front_of_house')
    file_picture_of_bedroom = request.FILES.get('file_picture_of_bedroom')
    file_other_picture = request.FILES.get('file_other_picture')

    # Getting data from request
    capacity = request.POST.get('capacity', "")
    city = request.POST.get('city', "")
    nbr_n_street = request.POST.get('nbr_n_street', "")
    zip_code = request.POST.get('zip_code', "")
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
        zip_code = int(zip_code) if zip_code else None

    except Exception as e:
        messages.error(request, "Le code postal doit être un nombre entier !")
        return render(request,
                      "app_housing/create-or-update-house.html",
                      context={"house": house_to_update, "form": form})

    # Adding pictures to the existing or temporary house if required fields are filled
    House.add_pictures_to_house_if_house_exists(
        request,
        house_to_update,
        file_picture_front_of_house,
        file_picture_of_bedroom,
        file_other_picture,
        capacity,
        city,
        zip_code,
        nbr_n_street)

    # If the required fields are filled
    if (capacity
            and city
            and zip_code
            and nbr_n_street
            and house_to_update):  # If it's an update of the house

        # If the data of the house and the one from the form are NOT similar
        if not (house_to_update.capacity == capacity
                and house_to_update.city == city
                and house_to_update.zip_code == zip_code
                and house_to_update.nbr_n_street == nbr_n_street
                and house_to_update.message_of_presentation_of_house == (
                    message_of_presentation_of_house)
                and house_to_update.is_available == is_available):

            # Updating the house
            House.update(
                house_to_update,
                capacity,
                city,
                zip_code,
                nbr_n_street,
                message_of_presentation_of_house,
                is_available)

            messages.success(request, "Les nouvelles informations ont bien été enregistrées")
            return redirect('housing_home')

    return render(
        request,
        "app_housing/create-or-update-house.html",
        context={"house": house_to_update, "form": form})


def get_all_elements_with_available_rooms(request):
    """Get the cities where there are available hosts that has a capacity
    equals or greater than the one in argument."""

    what_to_find = request.GET.get('what_to_find', "")
    city = request.GET.get('city', None)

    try:
        from_id = int(request.GET.get('from_id', 0))
        capacity = int(request.GET.get('capacity', 0))
        total_nbr_of_elements = int(request.GET.get('total_nbr_of_elements', 0))
    except Exception as e:
        logging.error(
            "Error: each of 'from_id', 'capacity' and 'total_nbr_of_elements' "
            "must be an integer into a string!")

    if capacity and what_to_find in ["cities", "houses"]:
        elts, total_nbr_of_elements = House.get_elements_by_capacity(
            capacity,
            from_id,
            what_to_find,
            total_nbr_of_elements,
            city)

        previous_id = from_id - NBR_MAX_OF_ELEMENTS_TO_DISPLAY
        if previous_id < 1:
            previous_id = 0

        from_id = from_id + NBR_MAX_OF_ELEMENTS_TO_DISPLAY
        is_next = False  # Display of the button "Suivant"
        is_previous = False  # Display of the button "Précédent"

        if from_id < total_nbr_of_elements:
            is_next = True

        if from_id - NBR_MAX_OF_ELEMENTS_TO_DISPLAY > 0:
            is_previous = True

        return render(
            request,
            f"app_housing/{what_to_find}.html",
            context={"elts": elts,
                        "from_id": from_id,
                        "previous_id": previous_id,
                        "capacity": capacity,
                        "is_previous": is_previous,
                        "is_next": is_next,
                        "total_nbr_of_elements": total_nbr_of_elements,
                        "city": city})

    return redirect('housing_home')


@login_required
def get_house_details(request):
    """Get details of a house
    and allows the person in need to send an email to the owner of the house"""

    utils.send_email_to_owner_if_requested(request, Member)
    Member.add_to_contacts_if_requested(request, Member)

    if house_id := request.GET.get('id', ""):

        if house := House.get_house_by_id(house_id):
            return render(
                request,
                "app_housing/house-details.html",
                context={"house": house})

    return redirect(request.META.get('HTTP_REFERER', '/'))


def contact(request):
    return render(request, "app_housing/contact.html")


def get_message_to_developer(request):
    """Get message to developer from form to database."""

    list(messages.get_messages(request))  # Clear all system messages

    firstname = request.POST.get("firstname", "")
    lastname = request.POST.get("lastname", "")
    email = request.POST.get("email", "")
    phone_number = request.POST.get("phone_number", "")
    message = request.POST.get("message", "")

    context = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "phone_number": phone_number,
        "message": message,
    }

    is_email_well_formed = utils.check_email_validity(email)
    if not is_email_well_formed:
        messages.success(request, ("Le champ email est incorrect !"))
        return render(request, "app_housing/contact.html", context)

    if not (
        firstname
        and lastname
        and email
        and phone_number
        and message
        and isinstance(firstname, str)
        and isinstance(lastname, str)
        and isinstance(email, str)
        and isinstance(phone_number, str)
        and isinstance(message, str)
    ):

        messages.success(request, ("Tous les champs doivent être remplis !"))
        return render(request, "app_housing/contact.html", context)

    try:
        ReceivedMessage.objects.create(
            firstname=firstname,
            lastname=lastname,
            email=email,
            phone_number=phone_number,
            message=message,
        )

        messages.success(
            request,
            (
                "Votre message a bien été reçu. :)"
            ),
        )
    except Exception as e:
        logging.error(f"Unable to add the customer. Reason: {str(e)}")
        messages.error(
            request,
            (
                "Malheureusement, une erreur du système est survenue. "
                "Le message n'a pas pu être reçu !"
                " Veuillez ré-essayer plus tard. Merci"
            ),
        )

    return render(request, "app_housing/message-received.html")


def legal_notice(request):
    return render(request, "app_housing/legal-notice.html")
