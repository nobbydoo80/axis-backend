"""factory.py: Django annotation"""


import logging
import re

from django.contrib.contenttypes.models import ContentType
from django.db import models

from axis.annotation.models import Type, Annotation
from axis.core.utils import random_sequence

__author__ = "Autumn Valenta"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class DummyModel(models.Model):
    """
    Fills the role of a model that an Annotation will attach itself to.  Since it has no fields, it
    can easily be created without special treatment.

    """

    def __str__(self) -> str:
        return str(self.pk)


def type_factory(**kwargs) -> Type:
    """An annotation type factory"""
    applicable_content_types = kwargs.pop("applicable_content_types", None)
    if applicable_content_types:
        if not isinstance(applicable_content_types, list):
            applicable_content_types = [applicable_content_types]
    kwrgs = {
        "name": f"type_{random_sequence(4)}",
        "description": f"Description {random_sequence(4)}",
        "data_type": "open",
        "is_unique": False,
        "is_required": False,
        "valid_multiplechoice_values": "",
    }

    kwrgs.update(kwargs)

    annotation_type = Type.objects.create(**kwrgs)
    if applicable_content_types is None:
        content_type = ContentType.objects.get_for_model(DummyModel)
        annotation_type.applicable_content_types.add(content_type)
    return annotation_type


def multiple_choice_type_factory() -> Type:
    """An multiple_choice annotation type factory.  get_or_create based on the field 'name'."""
    data_type = "multiple-choice"
    valid_multiplechoice_values = "a,b,c,d"
    return type_factory(
        data_type=data_type,
        valid_multiplechoice_values=valid_multiplechoice_values,
    )


def annotation_factory(**kwargs) -> Annotation:
    """An annotation factory"""
    type = kwargs.pop("type", None)

    kwrgs = {
        "content": f"Content {random_sequence(4)}",
    }

    if type is None:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("type__"):
                c_kwrgs[re.sub(r"type__", "", k)] = kwargs.pop(k)
        kwargs["type"] = type_factory(**c_kwrgs)
    else:
        kwrgs["type"] = type

    kwrgs.update(kwargs)

    return Annotation.objects.create(**kwrgs)
