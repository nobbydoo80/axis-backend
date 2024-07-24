__author__ = "Artem Hruzd"
__date__ = "04/11/2023 16:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.equipment.models import EquipmentSponsorStatus


class EquipmentSponsorStatusInfoSerializer(serializers.ModelSerializer):
    company_info = CompanyInfoSerializer(read_only=True, source="company")

    class Meta:
        model = EquipmentSponsorStatus
        fields = (
            "company",
            "company_info",
            "equipment",
            "state",
            "state_changed_at",
            "state_notes",
            "created_at",
        )
