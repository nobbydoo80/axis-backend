"""__init__.py: Django messaging app"""


from copy import copy

from django.contrib.messages import constants as messages_constants

__author__ = "Autumn Valenta"
__date__ = "4/1/15 8:35 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class Constants(object):
    def __init__(self):
        for k, v in messages_constants.__dict__.items():
            if not k.startswith("_"):
                setattr(self, k, copy(v))


constants = Constants()  # make an clone of contrib.messages.constants for our own use
constants.SYSTEM = 50  # Higher than 'ERROR'
constants.DEFAULT_TAGS[constants.SYSTEM] = "system"
constants.DEFAULT_LEVELS["SYSTEM"] = constants.SYSTEM
