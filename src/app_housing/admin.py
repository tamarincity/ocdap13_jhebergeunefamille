from django.contrib import admin

from app_housing.models import House, ReceivedMessage


class ReceivedMessageAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in ReceivedMessage._meta.fields if field.name != "is_already_read"]
    list_filter = ('is_already_read', 'datetime')


class HouseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "capacity",
        "owner",
        "city",
        "nbr_n_street",
        "zip_code",
        "picture_front_of_house",
        "picture_of_bedroom",
        "other_picture",
        "message_of_presentation_of_house",
        "is_available",
        "is_removed")


# Usage
admin.site.register(ReceivedMessage, ReceivedMessageAdmin)
admin.site.register(House, HouseAdmin)
