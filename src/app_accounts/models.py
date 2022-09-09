from django.db import models
from django.contrib.auth.models import AbstractUser


class Member(AbstractUser):

    pseudo = models.CharField(max_length=150)
    firstname = models.CharField(max_length=150, blank=False, null=False)
    lastname = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    message_of_presentation = models.TextField()
    is_host = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstname} ({self.username})"

    def remove_member(email: str) -> bool:
        return True

    def update_or_create_member(member: dict) -> bool:
        return True

    def add_to_contacts(member) -> bool:
        return True

    def remove_from_contacts(member):
        return True
