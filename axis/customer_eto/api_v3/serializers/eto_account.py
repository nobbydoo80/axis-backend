__author__ = "Artem Hruzd"
__date__ = "07/18/2022 20:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.customer_eto.models import ETOAccount


class ETOAccountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETOAccount
        fields = ("id", "company", "account_number", "ccb_number")


class ETOAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETOAccount
        fields = ("id", "company", "account_number", "ccb_number")
