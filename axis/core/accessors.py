import logging

from django.db import models

from axis.better_generics import BetterGenericAccessor
from .fields import UUIDField

__author__ = "Autumn Valenta"
__date__ = "1/14/14 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class RemoteIdentifiers(BetterGenericAccessor):
    model_name = "{source_model}RemoteIdentifier"
    attrs = {}  # We synthesize a Meta and put it here
    fields = {
        "id": (
            UUIDField,
            [],
            dict(
                primary_key=True,
                blank=False,
                help_text="""Represents an off-site ID of the given type.""",
            ),
        ),
        "type": (
            models.CharField,
            [],
            dict(
                max_length=20, choices=[], help_text="""A queryable label for an off-site type."""
            ),
        ),
    }

    def __init__(self, choices, **kwargs):
        """Dynamically insert 'choices' given during accessor init."""
        self.fields = self.fields.copy()
        self.fields["type"][2]["choices"] = choices
        self._choices = choices
        super(RemoteIdentifiers, self).__init__(**kwargs)

    def get_model_factory_kwargs(self, **kwargs):
        kwargs = super(RemoteIdentifiers, self).get_model_factory_kwargs(**kwargs)

        class Meta:
            # Only one remote id per type on a given model instance
            unique_together = [("type", kwargs["fk_name"])]

        kwargs["attrs"]["Meta"] = Meta

        return kwargs

    def finalize_model(self, sender, model, name):
        super(RemoteIdentifiers, self).finalize_model(sender, model, name)

        self.types = [item[0] for item in self._choices]

        sender.get_remote_identifiers = lambda self: get_remote_identifiers(self, name)
        sender.get_remote_identifier = lambda self, type: get_remote_identifier(self, name, type)
        sender.set_remote_identifier = lambda self, type, value: set_remote_identifier(
            self, name, type, value
        )


def get_remote_identifiers(instance, attr_name):
    related_manager = getattr(instance, attr_name)
    return dict(related_manager.values_list("type", "pk"))


def get_remote_identifier(instance, attr_name, type):
    related_manager = getattr(instance, attr_name)
    return related_manager.filter(type=type).values_list("id", flat=True).first()


def set_remote_identifier(instance, attr_name, type, value):
    related_manager = getattr(instance, attr_name)
    remote_identifier, _ = related_manager.get_or_create(type=type, defaults={"id": value})
    remote_identifier.pk = value
    remote_identifier.save()
