from django.urls import path
from app_housing import views

urlpatterns = [
    # Home page
    path('home', views.home, name='housing_home'),
    # Home page
    path('host-home', views.host_home, name='housing_host_home'),
    # Route to store the original product and its substitute to the database
    path('add_to_favorites', views.add_to_favorites, name='housing_add_to_favorites'),
    # Route for the user to send a message
    path('contact', views.contact, name='housing_contact'),
    # Route to get the details of a substitute product
    path('details', views.details, name='housing_details'),
    # Route for a host to get all his registered houses
    path('my-houses', views.get_my_houses, name='housing_my_houses'),
    # Route for a host to get all his registered houses
    path('my-contacts', views.get_my_contacts, name='housing_my_contacts'),
    # Route to receive the message from the contact page
    path('get-message', views.get_message, name='housing_get_message'),
    # Route to get the original product after submitting the form
    path('get-origial-product', views.get_origial_product, name='housing_get_origial_product'),
    # Route to get a list of substitute housing for an original product
    path('get-substitutes', views.get_substitutes, name='housing_get_substitutes'),
    # Route to go to the page of the legal notice
    path('legal_notice', views.legal_notice, name='housing_legal_notice'),
    # Home page
    path('', views.home, name='housing_home'),
]
