import time
from datetime import datetime
import random
import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from icecream import ic

from app_accounts.models import Member
from utils import utils
from .constants import (
    OTP_VALIDITY_DURATION_IN_MINUTE,
    USER_LARA_CROFT,
)


User = get_user_model()

def fake_1(request):
    try:
        in_need = Member.objects.get(username="mimi@yopmail.com")
        print()
        print("Mimi contacts: ")
        print(in_need.hosts.all())
        print()
    except Exception as e:
        print(str(e))
    return HttpResponse("OK")
