from typing import TypeVar

from django.db import models

from app_accounts.models import Member

class House(models.Model):
    capacity = models.IntegerField(default=1)
    owner = models.ForeignKey(
        Member, related_name="list_of_houses", on_delete=models.CASCADE)

    city = models.CharField(max_length=100, null=True, blank=True)
    nbr_n_street = models.CharField(max_length=100, null=True, blank=True)
    zip = models.IntegerField()
    picture_front_of_house = models.ImageField(
        upload_to="pictures_front_of_house/",
        blank=True,
        null=True,
        help_text="picture of the front of the house")

    picture_of_bedroom = models.ImageField(
        upload_to="pictures_of_bedroom/",
        blank=True,
        null=True,
        help_text="picture of the bedroom")

    other_picture = models.ImageField(
        upload_to="other_pictures/",
        blank=True,
        null=True,
        help_text="other picture of the house")

    message_of_presentation_of_house = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "<< A house >>"
        verbose_name_plural = "list of houses"

    def __str__(self):
        return f"city: {self.city}, owner: {self.owner}"

    @classmethod
    def remove_house(cls, house_id: int):
        return True

    @classmethod
    def get_cities_by_capacity(capacity: int):
        return True

    @classmethod
    def get_id_n_capacity_by_capacity_n_city(capacity_gte_than: int, city: str):
        return True
