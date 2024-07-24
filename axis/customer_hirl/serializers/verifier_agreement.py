"""verifier_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "02/14/2022 19:27"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.customer_hirl.models import VerifierAgreement


class VerifierAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifierAgreement
        fields = ("id", "state", "us_states", "provided_services")


class VerifierAgreementInfoSerializer(serializers.ModelSerializer):
    """
    Info serializer for nested usage
    """

    class Meta:
        model = VerifierAgreement
        fields = ("id", "state", "us_states", "provided_services")
