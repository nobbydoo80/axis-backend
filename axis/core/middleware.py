"""views.py: Django core views"""

__author__ = "Steven Klass"
__date__ = "2011/08/04 15:21:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["amit", "Steven Klass"]


import json
import logging
import sys

from django import http
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext_lazy as _
from django.views.debug import technical_500_response
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.models import Site

from axis.core.utils import get_user_perm_cache_key


log = logging.getLogger(__name__)
User = get_user_model()

AUTH_HEADER_TYPES = simplejwt_settings.AUTH_HEADER_TYPES

if not isinstance(simplejwt_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES = set(h.encode(HTTP_HEADER_ENCODING) for h in AUTH_HEADER_TYPES)


def get_cached_user_permissions(request, force=False):
    """A cached version of a company given a company_id"""

    if request.user.is_anonymous:
        return set()

    if not request.user.is_authenticated:
        return set()

    cache_key = get_user_perm_cache_key(user_id=request.user.pk)
    user_perms = None if force else cache.get(cache_key)
    if user_perms is None:
        user = User.objects.get(id=request.user.pk)
        user_perms = user.get_all_permissions()
        cache.set(cache_key, user_perms, settings.USER_PERMISSION_CACHE_DURATION)

    return user_perms


class UserPermissionsMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, "user"), (
            "The company middleware requires auth middleware to be "
            "installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )

        request.user_permissions = get_cached_user_permissions(request)
        return self.get_response(request)


class ExceptionUserInfoMiddleware(object):
    """Handle exceptions and let people know about them.  Add the ability for admins to look at
    the technical side of it"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        is_super_user = (
            hasattr(request, "user")
            and hasattr(request.user, "is_superuser")
            and request.user.is_superuser
        )

        # If we aren't in debug and we aren't running any tests
        if not settings.DEBUG and "test" not in sys.argv:
            # And this isn't a 404
            if not isinstance(exception, http.Http404):
                # And the user is a super or it's an internal IP then show the technical response
                msg = "Request Exception: %s"
                if "api" in request.path:
                    msg = "API Request Exception: %s"
                log.error(msg, request.path, extra={"request": request}, exc_info=True)
                if is_super_user or request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS:
                    return technical_500_response(request, *sys.exc_info())


class AxisSessionMiddleware(SessionMiddleware):
    """
    Adding jwt token to each request
    """

    def process_request(self, request):
        # disable CSRF check for local development
        # for case 3(Local App(localhost:4200) and Remote Django(e.g. demo))
        # Read more: https://github.com/pivotal-energy-solutions/axis/
        # wiki/How-authentication-and-impersonation-working-with-API-V3
        if settings.DEBUG:
            setattr(request, "_dont_enforce_csrf_checks", True)
        super(AxisSessionMiddleware, self).process_request(request)
        header = request.META.get("HTTP_AUTHORIZATION")

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        if header:
            raw_token = self.get_raw_token(header)
            if raw_token:
                token = self.get_validated_token(raw_token)
                if token:
                    request.jwt = token
                    return

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            data = {
                "error": "Authorization header must contain two space-delimited values",
                "code": "bad_authorization_header",
            }
            if parts[0] == b"Bearer":
                response = HttpResponse(
                    json.dumps(data),
                    content_type="application/json",
                    reason=data["error"],
                    status=401,
                )
                response["WWW-Authenticate"] = "Bearer"
                return response
            raise AuthenticationFailed(
                _(data["error"]),
                code=data["code"],
            )

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        for AuthToken in simplejwt_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError:
                pass

        return None


def get_user(validated_token):
    """
    Attempts to find and return a user using the given validated token.
    """
    user = None
    user_id = None

    try:
        user_id = validated_token[simplejwt_settings.USER_ID_CLAIM]
    except KeyError:
        # Token contained no recognizable user identification
        pass

    try:
        user = User.objects.get(**{simplejwt_settings.USER_ID_FIELD: user_id})
    except User.DoesNotExist:
        pass

    return user or AnonymousUser()


class AxisAuthenticationMiddleware(AuthenticationMiddleware):
    """
    Authenticate user prior to JWT request object
    """

    def process_request(self, request):
        if hasattr(request, "jwt"):
            request.user = SimpleLazyObject(lambda: get_user(request.jwt))
            if not request.session.get("_auth_user_id") and request.user.is_authenticated:
                login(request, request.user)
        else:
            super(AxisAuthenticationMiddleware, self).process_request(request)


class AxisAuthenticationCookieMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if not hasattr(request, "COOKIES") and not hasattr(response, "COOKIES"):
            return response
        if request.user.is_authenticated:
            refresh = RefreshToken.for_user(request.user)
            if (hasattr(request.user, "is_impersonate") and request.user.is_impersonate) or (
                hasattr(request.session, "_session")
                and request.session._session.get("_impersonate")
            ):
                refresh["impersonator"] = request.session._session.get("_auth_user_id")

            refresh_token = "%22{}%22".format(refresh)
            access_token = "%22{}%22".format(refresh.access_token)

            response.set_cookie("access", access_token, path="/")
            if refresh_token:
                response.set_cookie("refresh", refresh_token, path="/")
        else:
            response.delete_cookie("access")
            response.delete_cookie("refresh")
        return response


class DynamicSiteDomainMiddleware:
    """
    Helps to set SITE_ID based on domain
    that is allow us to detect and recognize Customer websites like NEEA or Home Innovation
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        try:
            current_site = Site.objects.get(domain=request.get_host())
        except Site.DoesNotExist:
            current_site = Site.objects.get(id=settings.SITE_ID)

        request.current_site = current_site
        settings.SITE_ID = current_site.id

        response = self.get_response(request)
        return response
