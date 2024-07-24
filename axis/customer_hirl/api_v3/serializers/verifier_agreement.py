"""verifier_agreement.py: """

__author__ = "Artem Hruzd"
__date__ = "03/23/2022 19:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from rest_framework import serializers

from axis.customer_hirl.models import BuilderAgreement

customer_hirl_app = apps.get_app_config("customer_hirl")


class VerifierAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuilderAgreement
        fields = ("id",)
