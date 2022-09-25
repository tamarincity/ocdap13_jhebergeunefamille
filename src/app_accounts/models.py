from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import messages


class Member(AbstractUser):

    pseudo = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    message_of_presentation = models.TextField()
    is_host = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)

    hosts = models.ManyToManyField('Member', related_name='contacts')

    def __str__(self):
        return f"{self.pseudo} ({self.first_name})"

    @classmethod
    def add_to_contacts_if_requested(
            cls,
            request,
            Member: "Member") -> None:
        """Add an owner to the contact list of the person in need of housing"""

        is_add_to_contact_requested = request.POST.get('add_to_contact', False)
        owner_id = request.POST.get('owner_id', "")
        in_need_email = request.POST.get('in_need_email', "")

        if is_add_to_contact_requested and owner_id and in_need_email:

            # Get the owner and the person_in_need
            owner = Member.objects.get(id=owner_id)
            in_need = request.user

            # Add the owner to the list of contacts of the in need person if he is not already in
            if owner in in_need.hosts.all():
                messages.error(request, ("Cette personne est déjà dans vos contacts"))
                return False

            in_need.hosts.add(owner)
            messages.success(request, "Cette personne a été ajoutée à vos contacts")
            return True
        return
