from django.shortcuts import redirect, render
from django.http import HttpResponse

from utils import utils


def home(request):
    visitor = request.user
    if visitor.is_authenticated and visitor.is_host:
        return redirect('housing_host_home')
    return render(request, "app_housing/home.html")

def get_all_cities_with_available_rooms(request):
    return HttpResponse("get_all_cities_with_available_rooms is coming soon")

def host_home(request):
    visitor = request.user
    if not (visitor.is_authenticated and visitor.is_host):
        return redirect('housing_home')
    return render(request, "app_housing/host-home.html")


def add_to_favorites(request):
    return HttpResponse("host_home is coming soon")


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
