"""credentials.py: """


from ..models import HESCredentials
from rest_framework import serializers
from ..hes import DOEInterface, DOEAuthenticationError

__author__ = "Artem Hruzd"
__date__ = "12/20/2019 18:40"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class HESCredentialsSerializer(serializers.ModelSerializer):
    """HES Credentials"""

    class Meta:
        model = HESCredentials
        exclude = ("updated_at", "created_at")
        extra_kwargs = {"username": {"allow_blank": True}, "password": {"allow_blank": True}}

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        if bool(username) != bool(password):
            raise serializers.ValidationError(
                f"DOE {'username' if username else 'password'} was provided, but {'password' if username else 'username'} was not"
            )
        if username and password:
            try:
                doe = DOEInterface(username=username, password=password)
                doe.get_session_token()
            except DOEAuthenticationError:
                raise serializers.ValidationError(
                    "We could not log you in with the provided DOE HES username and password, please check that they are correct"
                )
        return attrs
