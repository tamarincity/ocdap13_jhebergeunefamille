from django.contrib import admin

from app_accounts.models import Member


class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "id", "email", "pseudo", "phone", "message_of_presentation", "is_host", "is_removed")


# Usage
admin.site.register(Member, MemberAdmin)
