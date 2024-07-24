"""auth.py: """

from django.core import mail
from django.urls import reverse_lazy
from django.utils.encoding import force_str

from axis.core.tests.mixins import ImpersonateTestMixin
from axis.core.tests.testcases import ApiV3Tests

__author__ = "Artem Hruzd"
__date__ = "08/25/2020 17:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TestAuthAPIViews(ImpersonateTestMixin, ApiV3Tests):
    def _generate_uid_and_token(self, user):
        result = {}
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode

        result["uid"] = urlsafe_base64_encode(force_bytes(user.pk))
        result["token"] = default_token_generator.make_token(user)
        return result

    def test_password_reset(self):
        user = self.nonadmin_user
        new_password = "Test@Password123"

        password_reset_url = reverse_lazy("api_v3:password_reset")
        rest_password_reset_confirm_url = reverse_lazy("api_v3:password_reset_confirm")

        # call password reset
        mail_count = len(mail.outbox)
        payload = {"email": user.email}
        response = self.client.post(password_reset_url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), mail_count + 1)

        url_kwargs = self._generate_uid_and_token(user)

        # wrong token
        data = {
            "new_password1": new_password,
            "new_password2": new_password,
            "uid": force_str(url_kwargs["uid"]),
            "token": "-wrong-token-",
        }
        response = self.client.post(rest_password_reset_confirm_url, data=data)
        self.assertEqual(response.status_code, 400)

        # wrong uid
        data = {
            "new_password1": new_password,
            "new_password2": new_password,
            "uid": "-wrong-uid-",
            "token": url_kwargs["token"],
        }
        response = self.client.post(rest_password_reset_confirm_url, data=data)
        self.assertEqual(response.status_code, 400)

        # wrong token and uid
        data = {
            "new_password1": new_password,
            "new_password2": new_password,
            "uid": "-wrong-uid-",
            "token": "-wrong-token-",
        }
        response = self.client.post(rest_password_reset_confirm_url, data=data)
        self.assertEqual(response.status_code, 400)

        # valid payload
        data = {
            "new_password1": new_password,
            "new_password2": new_password,
            "uid": force_str(url_kwargs["uid"]),
            "token": url_kwargs["token"],
        }
        response = self.client.post(rest_password_reset_confirm_url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_password_reset_with_email_in_different_case(self):
        user = self.nonadmin_user
        password_reset_url = reverse_lazy("api_v3:password_reset")

        # call password reset in upper case
        mail_count = len(mail.outbox)
        payload = {"email": user.email.upper()}
        response = self.client.post(password_reset_url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), mail_count + 1)

    def test_password_reset_with_invalid_email(self):
        """
        Invalid email should not raise error, as this would leak users
        """
        user = self.nonadmin_user
        password_reset_url = reverse_lazy("api_v3:password_reset")

        # call password reset
        mail_count = len(mail.outbox)
        payload = {"email": "nonexisting@email.com"}
        response = self.client.post(password_reset_url, data=payload, status_code=200)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), mail_count)
