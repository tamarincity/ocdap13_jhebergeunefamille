from django.urls import path

from app_accounts import views

urlpatterns = [
    # route for the user to get his account info
    path('account', views.account, name='accounts_account'),
    # route to remove fake users from database
    path('delete_fake_users', views.delete_fake_users, name='delete_fake_users'),
    # route for the user to log in
    path('login', views.login_user, name='accounts_login'),
    # route for the user to declare that he has forgotten his password
    path('forgoten_pswd', views.forgoten_pswd, name='accounts_forgoten_pswd'),
    # route for the user to enter its new password
    path('new_pswd', views.new_pswd, name='accounts_new_pswd'),
    # route for the user to log out
    path('logout', views.logout_user, name='accounts_logout'),
    # route for the user to sign up
    path('signup', views.signup_user, name='accounts_signup'),
    # route for the user in need to get the list of cities that have available rooms
    path('cities', views.get_all_cities_with_available_rooms, name='accounts_cities'),
]
