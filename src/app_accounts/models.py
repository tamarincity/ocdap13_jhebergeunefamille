from django.db import models
from django.contrib.auth.models import AbstractUser


class Member(AbstractUser):

    pseudo = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    message_of_presentation = models.TextField()
    is_host = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)

    hosts = models.ManyToManyField('Member', related_name='contacts')


    def __str__(self):
        return f"{self.pseudo}, ({self.first_name})"

    def remove_member(email: str) -> bool:
        return True

    def update_or_create_member(member: dict) -> bool:
        return True

    def add_to_contacts(member) -> bool:
        return True

    def remove_from_contacts(member):
        return True
