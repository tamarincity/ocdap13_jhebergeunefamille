from django.urls import path

from app_accounts import fake_views as views

urlpatterns = [
    # route for the user to get his account info
    path('1', views.fake_1, name='fake_1'),
]
