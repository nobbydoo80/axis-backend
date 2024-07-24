"""token.py: """

__author__ = "Artem Hruzd"
__date__ = "01/26/2021 22:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib.auth.tokens import PasswordResetTokenGenerator


class UnsubscribeEmailTokenGenerator(PasswordResetTokenGenerator):
    key_salt = "axis.core.messaging.tokens.UnsubscribeTokenGenerator"


unsubscribe_email_token = UnsubscribeEmailTokenGenerator()
