"""contact.py: """

__author__ = "Artem Hruzd"
__date__ = "07/19/2022 18:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

from django.apps import apps
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from axis.company import strings
from axis.company.managers import (
    ContactQuerySet,
)
from axis.core.accessors import RemoteIdentifiers
from axis.geographic.placedmodels import AddressedPlacedModel

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class Contact(AddressedPlacedModel):
    objects = ContactQuerySet.as_manager()
    identifiers = RemoteIdentifiers(
        choices=[
            ("trc", "TRC UUID"),
        ]
    )

    company = models.ForeignKey("Company", on_delete=models.CASCADE)

    type = models.CharField(
        max_length=10,
        default="person",
        choices=[
            ("person", "Person"),
            ("company", "Company"),
        ],
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=200, blank=True)
    phone = PhoneNumberField(null=True, help_text=strings.SUBDIVISION_HELP_TEXT_OFFICE_PHONE)
    email = models.EmailField(
        blank=True, null=True, help_text=strings.SUBDIVISION_HELP_TEXT_DEFAULT_EMAIL
    )

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        description = self.description if (self.type == "person") else None
        return "{name}{description_area}".format(
            **{
                "name": (" ".join((self.first_name, self.last_name)).strip()),
                "description_area": (" ({})".format(description) if description else ""),
            }
        )

    def can_be_edited(self, user):
        if user.is_superuser:
            return True
        return user.company_id == self.company_id

    def can_be_deleted(self, user):
        return False  # Can't enforce data integrity in JSON blobs if we delete

    def get_json_info_repr(self):
        from axis.company.serializers import ContactSerializer

        return ContactSerializer(self).data

    def get_address(self):
        return "\n".join(
            filter(
                None,
                [
                    self.street_line1 or "",
                    self.street_line2 or "",
                    "{city} {state} {zipcode}".format(
                        **{
                            "city": self.city.name if self.city else "",
                            "state": self.state or "",
                            "zipcode": self.zipcode or "",
                        }
                    ).strip(),
                ],
            )
        )
