from django.urls import path
from app_housing import views

urlpatterns = [
    # Home page
    path('home', views.home, name='housing_home'),
    # Home page
    path('host-home', views.host_home, name='housing_host_home'),
    # Route for the user to create or update his house
    path('create_or_update_house',
         views.create_or_update_house,
         name='housing_create_or_update_house'),

    # Route for the user to send a message
    path('contact', views.contact, name='housing_contact'),
    # Route to receive the message from the contact page
    path('get-message-to-developer', views.get_message_to_developer, name='housing_get_message_to_developer'),
    # Route to go to the page of the legal notice
    path('legal_notice', views.legal_notice, name='housing_legal_notice'),
    # Home page
    path('', views.home, name='housing_home'),
    # Route for the user to get the list of cities that have available rooms
    path('houses_or_cities', views.get_all_elements_with_available_rooms, name='housing_houses_or_cities'),
    # Route for the user to get the details of an accommodation
    path('house-details', views.get_house_details, name='housing_house-details'),
]
