"""Messaging settings context processors."""


from collections import defaultdict
import logging

from django.conf import settings

__author__ = "Autumn Valenta"
__date__ = "2015-03-04 2:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def websocket(request):
    port = settings.MESSAGING.get("PORT")
    return {
        "MESSAGING_HOST": "{host}{port}".format(
            host=settings.MESSAGING["HOST"].format(HTTP_HOST=request.META.get("HTTP_HOST")),
            port=":{port}".format(port=port) if port else "",
        ),
    }
