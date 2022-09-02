from django.urls import path
from app_housing import views

urlpatterns = [
    path('', views.home, name='home'),
]
