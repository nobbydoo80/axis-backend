"""__init__.py: Django core.tests package container"""


import json
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage import default_storage
from django.test import Client

__author__ = "Steven Klass"
__date__ = "4/16/13 9:51 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BaseAxisClient(Client):
    """Baseline Client for Axis"""

    def __init__(self, **defaults):
        """Adds messages to the request"""
        super(BaseAxisClient, self).__init__(**defaults)
        if "django.contrib.messages" in settings.INSTALLED_APPS:
            self._messages = default_storage(self)

    def get(self, path, data={}, follow=False, ajax=False, **extra):
        """
        Adds simple ``ajax`` keyword argument for adding ``HTTP_X_REQUESTED_WITH='XMLHttpRequest'``
        to the ``**extra`` arguments.

        """
        if ajax:
            extra["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        return super(BaseAxisClient, self).get(path, data=data, follow=follow, **extra)

    def patch(self, *args, **kwargs):
        return self.generic("PATCH", *args, **kwargs)

    def get_json(self, path, data={}, follow=False, ajax=False, **extra):
        """
        Uses ``json`` module to deserialize the ``response.content`` and set a
        ``response.json_content`` value.

        """

        response = self.get(path, data, follow, ajax, **extra)
        response.json_content = json.loads(response.content)
        return response

    def login(self, **credentials):
        """This sets the user attibute for a logged in user"""
        if super(BaseAxisClient, self).login(**credentials):
            self.user = authenticate(**credentials)
            return True
        else:
            self.user = AnonymousUser()
        return False


class AxisClient(BaseAxisClient):
    pass
