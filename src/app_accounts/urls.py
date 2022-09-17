from django.urls import path

from app_accounts import views

urlpatterns = [
    # route for the user to get his account info
    path('profile', views.profile, name='accounts_profile'),
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
    # route for the user to complete the registration
    path('complete_the_registration',
         views.complete_the_registration,
         name='accounts_complete_the_registration'),
]
