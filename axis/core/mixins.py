"""mixins.py: Standard Mixins for Views"""


from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class AuthenticationMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

    def get_permission_denied_message(self):
        try:
            user = self.request.user
            url = self.request.build_absolute_uri()
            msg = (
                f"Sorry {user} ({user.username}) does not have permission to "
                f"access this page {url}"
            )
            referer = self.request.META.get("HTTP_REFERER")
            if referer:
                msg += f" from {referer}"
            return msg
        except AttributeError:
            return super(AuthenticationMixin, self).get_permission_denied_message()

    def handle_no_permission(self):
        # Not authenticated users will be redirected to login page by default
        if not self.request.user.is_authenticated:
            self.raise_exception = False
        return super(AuthenticationMixin, self).handle_no_permission()
