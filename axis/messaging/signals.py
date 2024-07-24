import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_in


__author__ = "Autumn Valenta"
__date__ = "5/7/15 11:51 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")

    user_logged_in.connect(user_logged_in_handler)

    from impersonate.signals import session_begin, session_end

    session_begin.connect(session_begin_handler)
    session_end.connect(session_end_handler)


def user_logged_in_handler(sender, request, user, **kwargs):
    from .models import UserSession

    request.session.save()
    UserSession.objects.get_or_create(user=user, session_id=request.session.session_key)


def session_begin_handler(sender, request, impersonator, impersonating, **kwargs):
    from .models import UserSession

    UserSession.objects.get_or_create(user=impersonating, session_id=request.session.session_key)


def session_end_handler(sender, request, impersonator, impersonating, **kwargs):
    from .models import UserSession

    UserSession.objects.filter(user=impersonating, session_id=request.session.session_key).delete()
