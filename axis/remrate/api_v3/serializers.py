"""serializers.py: """


from django.http import request
from rest_framework import serializers
import logging
import re

from axis.remrate.models import RemRateUser, RESERVED_PASSWORDS, RESERVED_USERNAMES

__author__ = "Rajesh Pethe"
__date__ = "07/10/2020 20:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Rajesh Pethe",
]


log = logging.getLogger(__name__)

errors = {
    "reserved_username": "Sorry you cannot use that reserved username",
    "user_exists": "Sorry the user {username} already exists",
    "password_mismatch": "The two passwords do not match.",
    "reserved_password": "Password is too obvious - please trye something else.",
    "weak_password": "Password is too weak - please try something else.",
}


class BaseRemrateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemRateUser
        fields = ("id", "username", "password", "company", "is_active", "last_used")

    def validate_password(self, password):
        confirm_password = self.context["request"].data["confirm_password"]
        if password != confirm_password:
            raise serializers.ValidationError(errors["password_mismatch"])
        if password in RESERVED_PASSWORDS:
            raise serializers.ValidationError(errors["reserved_password"])
        if not bool(re.match(r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6})", password)):
            raise serializers.ValidationError(errors["weak_password"])
        return password


class RemrateUserSerializer(BaseRemrateUserSerializer):
    def validate_username(self, username):
        if username in RESERVED_USERNAMES:
            raise serializers.ValidationError(errors["reserved_username"])
        return username


class NestedRemrateUserSerializer(BaseRemrateUserSerializer):
    def validate_username(self, username):
        if username in RESERVED_USERNAMES:
            raise serializers.ValidationError(errors["reserved_username"])

        if RemRateUser.objects.filter(username=username).count():
            raise serializers.ValidationError(errors["user_exists"], username)
        return username
