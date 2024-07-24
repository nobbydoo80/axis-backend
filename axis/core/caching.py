"""api_cache_response.py: Django core"""


import hashlib
import json
import logging
from functools import wraps

from django.conf import settings
from django.core.cache import cache

__author__ = "Steven Klass"
__date__ = "3/24/15 18:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def calculate_cache_key(primary, secondary, request, args, kwargs):
    key_dict = {
        "primary": "{}".format(primary.__class__.__name__),
        "secondary": "{}".format(secondary.__name__),
    }
    for k, v in request.GET.items():
        key_dict["get_{}".format(k)] = "{}".format(v)
    for k, v in request.POST.items():
        key_dict["post_{}".format(k)] = "{}".format(v)
    for k, v in request.query_params.items():
        key_dict["query_{}".format(k)] = "{}".format(v)
    for k, v in kwargs.items():
        key_dict["{}".format(k)] = "{}".format(v)
    _args = ["{}".format(x) for x in args]
    if len(_args):
        key_dict["args"] = _args

    _json_data = json.dumps(key_dict, sort_keys=True).encode("utf-8")
    hash = hashlib.sha256(_json_data).hexdigest()
    # log.debug("Hash: %s Key Data: %s " % (hash, _json_data))
    return hash


class DRFCacheResponse(object):
    """This will allow a Django Rest Framework Response object to be cached"""

    def __init__(self, timeout=None, cache_errors=None, key_func=None, **kwargs):
        if timeout is None:
            self.timeout = getattr(settings, "CACHE_RESPONSE_TIMEOUT", 60 * 5)
        else:
            self.timeout = timeout

        if cache_errors is None:
            self.cache_errors = getattr(settings, "CACHE_ERRORS", True)
        else:
            self.cache_errors = cache_errors

        if key_func is None:
            self.key_func = calculate_cache_key
        else:
            self.key_func = key_func

        self.by_user = kwargs.pop("by_user", False)
        self.by_company = kwargs.pop("by_company", False)

        self.cache = cache

    def __call__(self, func):
        this = self

        @wraps(func)
        def inner(self, request, *args, **kwargs):
            return this.process_cache_response(
                view_instance=self, view_method=func, request=request, args=args, kwargs=kwargs
            )

        return inner

    def process_cache_response(self, view_instance, view_method, request, args, kwargs):
        _key_kw = kwargs.copy()
        if self.by_user:
            try:
                _key_kw["_username"] = "{} - {}".format(request.user.id, request.user)
            except AttributeError:
                log.warning("Unable to cache by user - not is request")
        elif self.by_company:
            try:
                _key_kw["_company"] = "{} - {}".format(request.company.id, request.company)
            except AttributeError:
                try:
                    _key_kw["_company"] = "{} - {}".format(
                        request.user.company.id, request.user.company
                    )
                except AttributeError:
                    log.warning("Unable to cache by company - not is request")

        key = self.calculate_key(
            primary=view_instance, secondary=view_method, request=request, args=args, kwargs=_key_kw
        )

        response = self.cache.get(key)
        if not response:
            log.debug("No cached copy of %s", key[:24])
            response = view_method(view_instance, request, *args, **kwargs)
            response = view_instance.finalize_response(request, response, *args, **kwargs)
            response.render()  # should be rendered, before picklining while storing to cache

            if not response.status_code >= 400 or self.cache_errors:
                self.cache.set(key, response, self.timeout)
            else:
                if response.status_code >= 400:
                    log.error(
                        "Invalid Response code %s for primary:%s  secondary:%s",
                        "{}".format(response.status_code),
                        "{}".format(view_instance),
                        "{}".format(view_method),
                        request,
                    )

        if not hasattr(response, "_closable_objects"):
            response._closable_objects = []

        return response

    def calculate_key(self, primary, secondary, request, args, kwargs):
        if isinstance(self.key_func, str):
            key_func = getattr(primary, self.key_func)
        else:
            key_func = self.key_func
        return key_func(
            primary=primary, secondary=secondary, request=request, args=args, kwargs=kwargs
        )


cache_api_response = DRFCacheResponse
