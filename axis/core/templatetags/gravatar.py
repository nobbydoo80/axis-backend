"""gravatar.py: Django core"""

import hashlib
import json
import logging
from urllib import parse
from urllib.request import urlopen

from django import template
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import escape
from django.utils.safestring import mark_safe

__author__ = "Steven Klass"
__date__ = "4/24/13 7:56 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()

GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX", "https://www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(
    settings,
    "GRAVATAR_DEFAULT_IMAGE",
    "https://s3.amazonaws.com/assets.pivotalenergy.net/static/production/images/default_user_100x100.png",
)
GRAVATAR_DEFAULT_RATING = getattr(settings, "GRAVATAR_DEFAULT_RATING", "g")
GRAVATAR_DEFAULT_SIZE = getattr(settings, "GRAVATAR_DEFAULT_SIZE", 100)
GRAVATAR_IMG_CLASS = getattr(settings, "GRAVATAR_IMG_CLASS", "img-rounded")

register = template.Library()


def _imgclass_attr():
    if GRAVATAR_IMG_CLASS:
        return ' class="%s"' % (GRAVATAR_IMG_CLASS,)
    return ""


def _wrap_img_tag(url, info, size):
    return mark_safe(
        '<img src="%s"%s alt="Avatar for %s" height="%s" width="%s"/>'
        % (escape(url), _imgclass_attr(), info, size, size)
    )


def _get_user(user):
    if not isinstance(user, User):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist:
            raise Exception("Bad user for gravatar.")
    return user


def _get_gravatar_id(email):
    return hashlib.md5(email.encode("utf-8")).hexdigest()


@register.simple_tag
def gravatar_for_email(email, size=None, rating=None):
    """
    Generates a Gravatar URL for the given email address.

    Syntax::

        {% gravatar_for_email <email> [size] [rating] %}

    Example::

        {% gravatar_for_email someone@example.com 48 pg %}
    """
    gravatar_url = "%savatar/%s" % (
        GRAVATAR_URL_PREFIX,
        _get_gravatar_id(email),
    )  # nosec

    parameters = [
        p
        for p in (
            ("d", GRAVATAR_DEFAULT_IMAGE),
            ("s", size or GRAVATAR_DEFAULT_SIZE),
            ("r", rating or GRAVATAR_DEFAULT_RATING),
        )
        if p[1]
    ]

    if parameters:
        gravatar_url += "?" + parse.urlencode(parameters, doseq=True)

    return escape(gravatar_url)


@register.simple_tag
def gravatar_for_user(user, size=None, rating=None):
    """
    Generates a Gravatar URL for the given user object or username.

    Syntax::

        {% gravatar_for_user <user> [size] [rating] %}

    Example::

        {% gravatar_for_user request.user 48 pg %}
        {% gravatar_for_user 'jtauber' 48 pg %}
    """
    user = _get_user(user)
    return gravatar_for_email(user.email, size, rating)


@register.simple_tag
def gravatar_img_for_email(email, size=None, rating=None):
    """
    Generates a Gravatar img for the given email address.

    Syntax::

        {% gravatar_img_for_email <email> [size] [rating] %}

    Example::

        {% gravatar_img_for_email someone@example.com 48 pg %}
    """
    gravatar_url = gravatar_for_email(email, size, rating)
    return _wrap_img_tag(gravatar_url, email, size)


@register.simple_tag
def gravatar_img_for_user(user, size=None, rating=None):
    """
    Generates a Gravatar img for the given user object or username.

    Syntax::

        {% gravatar_img_for_user <user> [size] [rating] %}

    Example::

        {% gravatar_img_for_user request.user 48 pg %}
        {% gravatar_img_for_user 'jtauber' 48 pg %}
    """
    gravatar_url = gravatar_for_user(user, size, rating)
    return _wrap_img_tag(gravatar_url, user.username, size)


@register.simple_tag
def gravatar_profile_for_email(email):
    """
    Generates the gravatar profile in json format for the given email address.

    Syntax::

        {% gravatar_profile_for_email <email> %}

    Example::

        {% gravatar_profile_for_email someone@example.com %}
    """
    gravatar_url = "%s%s.json" % (GRAVATAR_URL_PREFIX, _get_gravatar_id(email))
    return json.load(urlopen(gravatar_url))  # nosec


@register.simple_tag
def gravatar_profile_for_user(user):
    """
    Generates the gravatar profile in json format for the given user object or
    username.

    Syntax::

        {% gravatar_profile_for_user <user> %}

    Example::

        {% gravatar_profile_for_user request.user %}
        {% gravatar_profile_for_user 'jtauber' %}
    """
    user = _get_user(user)
    return gravatar_profile_for_email(user.email)
