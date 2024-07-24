"""coi_document.py: """

__author__ = "Artem Hruzd"
__date__ = "04/16/2021 17:23"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.customer_hirl.models import COIDocument


class COIDocumentSerializer(serializers.ModelSerializer):
    company_info = CompanyInfoSerializer(source="company", read_only=True)

    class Meta:
        model = COIDocument
        fields = (
            "id",
            "company",
            "document",
            "policy_number",
            "start_date",
            "expiration_date",
            "last_update",
            "created_at",
            "filesize",
            "type",
            "description",
            # computed
            "company_info",
        )
        read_only_fields = ("company",)


class ClientCOIDocumentSerializer(COIDocumentSerializer):
    class Meta:
        model = COIDocument
        fields = (
            "id",
            "company",
            "document",
            "policy_number",
            "start_date",
            "expiration_date",
            "last_update",
            "created_at",
            "filesize",
            "type",
            "description",
            # computed
            "company_info",
        )
        read_only_fields = ("company", "policy_number", "start_date", "expiration_date")
