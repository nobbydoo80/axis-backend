import logging

from django.core.cache import cache
from django.conf import settings as django_settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)
settings = getattr(django_settings, "FRONTEND", {})


class FrontendConfig(technology.TechnologyAppConfig):
    """Frontend technology configuration."""

    name = "axis.frontend"

    FRONTEND_HOST = settings["FRONTEND_HOST"]
    DEPLOY_URL = settings["FRONTEND_DEPLOY_URL"]

    def get_frontend_host(self, request):
        return self.FRONTEND_HOST.format(host=request.get_host())
