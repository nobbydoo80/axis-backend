"""project_tracker.py: Django Projects Tracker (aka FastTrack) Serializer"""


import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from axis.customer_eto import models

__author__ = "Steven K"
__date__ = "08/29/2019 11:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class FastTrackSubmissionSerializer(serializers.ModelSerializer):
    """FastTrack (Project Tracker)"""

    project_id = serializers.CharField()
    builder_account_number = serializers.SerializerMethodField(required=False, read_only=True)
    verifer_account_number = serializers.SerializerMethodField(required=False, read_only=True)

    # Submission-only bits
    project_ids = serializers.CharField(write_only=True)
    account_number = serializers.CharField(write_only=True)
    status = serializers.CharField(write_only=True)
    paid_date = serializers.CharField(write_only=True)
    check_number = serializers.CharField(write_only=True)

    class Meta:
        """Meta options"""

        model = models.FastTrackSubmission
        fields = (
            # Concrete fields
            "project_id",
            # Virtual fields
            "builder_account_number",
            "verifer_account_number",
            # Write-only
            "account_number",
            "project_id",
            "project_ids",
            "status",
            "paid_date",
            "check_number",
        )

        lookup_field = "project_id"

    def save(self, **kwargs):
        """Perform update via `customer_eto.utils.update_fasttracksubmission`"""

        from ..utils import update_fasttracksubmissions

        validated_data = [
            dict(list(attrs.items()) + list(kwargs.items())) for attrs in self.validated_data
        ]

        company = self.context["request"].company

        # Double check for other project_ids in addition to the one automatically resolved by the
        # url.
        if "project_ids" in validated_data:
            project_ids = validated_data["project_ids"]
        elif "project_id" in validated_data:
            project_ids = [validated_data["project_id"]]
        else:
            project_ids = [self.instance.project_id]

        objects = models.FastTrackSubmission.objects.filter(project_id__in=project_ids)

        try:
            update_fasttracksubmissions(self.instance, validated_data, objects, company=company)
        except models.ETOAccount.DoesNotExist as e:
            raise NotFound(str(e))

        return self.instance

    def get_builder_account_number(self, obj):
        """Return ETOAccount number if the company and number are available.

        Return None if no number can be found.
        """

        home_status = obj.home_status
        try:
            builder = home_status.home.get_builder()
            builder_number = builder.eto_account.account_number
        except ObjectDoesNotExist:
            builder_number = None
        return builder_number

    def get_verifer_account_number(self, obj):
        """Return ETOAccount number if the company and number are available.

        Return None if no number can be found.
        """

        home_status = obj.home_status
        try:
            verifier = home_status.get_provider()
            verifier_number = verifier.eto_account.account_number
        except ObjectDoesNotExist:
            verifier_number = None
        return verifier_number
