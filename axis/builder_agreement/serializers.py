import logging

from rest_framework import serializers

from axis.builder_agreement.models import BuilderAgreement
from axis.core.fields import ManyToManyNameField, ManyToManyUrlField
from axis.core.utils import make_safe_field
from axis.eep_program.models import EEPProgram

__author__ = "Michael Jeffrey"
__date__ = "5/13/15 1:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)


class BuilderAgreementSerializer(serializers.ModelSerializer):
    builder_org_name = make_safe_field(serializers.CharField)(
        source="builder_org.name", read_only=True
    )
    subdivision_name = make_safe_field(serializers.CharField)(
        source="subdivision.name", read_only=True
    )
    eep_programs = make_safe_field(serializers.PrimaryKeyRelatedField)(
        queryset=EEPProgram.objects.all(), many=True
    )
    eep_program_names = ManyToManyNameField(field_lookup="eep_programs")
    eep_program_urls = ManyToManyUrlField(
        field_lookup="eep_programs", reverse_lookup="eep_program:view"
    )
    expire_date = make_safe_field(serializers.CharField)(read_only=True)

    class Meta:
        model = BuilderAgreement
        fields = (
            "builder_org",
            "subdivision",
            "total_lots",
            "eep_programs",
            "start_date",
            "expire_date",
            "document",
            "comment",
            "lots_paid",
            "eep_program_names",
            "eep_program_urls",
            # Virtual read-only fields
            "builder_org_name",
            "subdivision_name",
        )

    def __init__(self, *args, **kwargs):
        super(BuilderAgreementSerializer, self).__init__(*args, **kwargs)
        self.configure_labels()

    def configure_labels(self):
        labels = [
            ("builder_org", "Builder"),
            ("eep_programs", "Programs covered"),
            ("document", "Primary Agreement"),
            ("expire_date", "End Date"),
        ]

        for field_name, label in labels:
            self.fields[field_name].label = label
