from django.contrib import admin

from app_housing.models import House


class HouseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "capacity",
        "owner",
        "city",
        "nbr_n_street",
        "zip",
        "picture_front_of_house",
        "picture_of_bedroom",
        "other_picture",
        "message_of_presentation_of_house",
        "is_available",
        "is_removed")


# Usage
admin.site.register(House, HouseAdmin)
