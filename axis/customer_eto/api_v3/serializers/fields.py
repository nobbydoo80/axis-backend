"""fields.py - Axis"""

__author__ = "Steven K"
__date__ = "8/10/21 08:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import enum
import logging

from rest_framework import fields

log = logging.getLogger(__name__)


class EnumField(fields.ChoiceField):
    def __init__(
        self,
        choices=None,
        to_choice=lambda x: (x.name, x.value),
        to_repr=lambda x: x.name,
        **kwargs,
    ) -> object:
        self.enum_class = choices
        self.to_repr = to_repr
        self.to_choice = to_choice
        kwargs["choices"] = [to_choice(e) for e in self.enum_class]
        kwargs.pop("max_length", None)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        # Default values
        if isinstance(data, enum.Enum):
            if data in self.enum_class:
                return data

        try:
            return self.enum_class[data]
        except (KeyError, ValueError):
            pass

        try:
            return self.enum_class(data)
        except (KeyError, ValueError):
            pass

        self.fail("invalid_choice", input=data)

    def to_representation(self, value):
        if not value:
            return None
