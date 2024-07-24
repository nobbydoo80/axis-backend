# -*- coding: utf-8 -*-
"""verification_report_upload.py: """

__author__ = "Artem Hruzd"
__date__ = "11/08/2022 14:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from rest_framework import serializers

from axis.customer_hirl.scoring import scoring_registry, BaseScoringExtraction
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.customer_hirl.tasks import scoring_upload_task


User = get_user_model()


class VerificationReportUploadSerializer(serializers.Serializer):
    scoring_path = serializers.ChoiceField(
        choices=scoring_registry.as_choices(), label="NGBS Standard Version/Scoring Path"
    )
    report_type = serializers.ChoiceField(
        choices=(
            (BaseScoringExtraction.ROUGH_DATA_TYPE, "Rough Verification Report"),
            (BaseScoringExtraction.FINAL_DATA_TYPE, "Final Verification Report"),
        ),
        label="Verification Report Type",
    )
    verifier = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    report_file = serializers.FileField(required=True, help_text="")

    def create(self, validated_data):
        user = self.context["request"].user

        async_document = AsynchronousProcessedDocument.objects.create(
            company=user.company,
            document=validated_data["report_file"],
            task_name=scoring_upload_task.name,
            task_id="",
            download=True,
        )

        result = scoring_upload_task.delay(
            user_id=user.id,
            result_object_id=async_document.id,
            template_type=validated_data["scoring_path"],
            data_type=validated_data["report_type"],
            verifier_id=validated_data["verifier"].id,
        )

        async_document.task_id = result.task_id
        async_document.save()

        return async_document

    def update(self, instance, validated_data):
        raise NotImplementedError
