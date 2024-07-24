from django.urls import reverse
from rest_framework import serializers

from axis.annotation.serializers import AnnotationTypeSerializer
from axis.checklist.collection.examine.serializers import CollectionRequestSerializer
from axis.checklist.models import CheckList
from axis.checklist.serializers import CheckListSerializerNestedQuestions
from axis.core.utils import make_safe_field
from .models import EEPProgram

__author__ = "Michael Jeffrey"
__date__ = "3/3/16 11:28 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


class EEPProgramSerializer(serializers.ModelSerializer):
    owner_name = make_safe_field(serializers.CharField)(source="owner.name", read_only=True)
    owner_url = make_safe_field(serializers.CharField)(
        source="owner.get_absolute_url", read_only=True
    )
    workflow_name = make_safe_field(serializers.CharField)(
        source="workflow.get_config_name", read_only=True
    )
    bulk_checklist_download_url = serializers.SerializerMethodField()
    checklist_download_url = serializers.SerializerMethodField()
    required_checklists_names = serializers.SerializerMethodField()
    required_annotation_types_names = serializers.SerializerMethodField()
    subdivisions = serializers.SerializerMethodField()
    required_checklists = make_safe_field(serializers.PrimaryKeyRelatedField)(
        allow_empty=True, queryset=CheckList.objects.all(), many=True
    )
    collection_request = make_safe_field(CollectionRequestSerializer)(read_only=True)
    certifiable_by_details = serializers.SerializerMethodField()

    class Meta:
        model = EEPProgram
        fields = (
            "id",
            "name",
            "is_qa_program",
            "owner",
            "min_hers_score",
            "max_hers_score",
            "per_point_adder",
            "builder_incentive_dollar_value",
            "rater_incentive_dollar_value",
            "comment",
            "manual_transition_on_certify",
            "required_checklists",
            "opt_in",
            "workflow",
            "collection_request",
            "program_close_warning",
            "program_close_warning_date",
            "program_submit_warning",
            "program_submit_warning_date",
            # Requirements
            "require_input_data",
            "require_rem_data",
            "require_model_file",
            "require_ekotrope_data",
            "require_builder_relationship",
            "require_builder_assigned_to_home",
            "require_hvac_relationship",
            "require_hvac_assigned_to_home",
            "require_utility_relationship",
            "require_utility_assigned_to_home",
            "require_rater_relationship",
            "require_rater_assigned_to_home",
            "require_provider_relationship",
            "require_provider_assigned_to_home",
            "require_qa_relationship",
            "require_qa_assigned_to_home",
            "required_annotation_types",
            "require_rater_of_record",
            "require_energy_modeler",
            "require_field_inspector",
            "allow_sampling",
            "allow_metro_sampling",
            "require_resnet_sampling_provider",
            "is_legacy",
            "is_public",
            "program_visibility_date",
            "program_start_date",
            "program_close_date",
            "program_submit_date",
            "program_end_date",
            "is_active",
            "certifiable_by",
            # Virtual Fields
            "owner_name",
            "owner_url",
            "bulk_checklist_download_url",
            "checklist_download_url",
            "subdivisions",
            "required_checklists_names",
            "certifiable_by_details",
            "workflow_name",
            "required_annotation_types_names",
        )

    main_fieldset = (
        "name",
        "owner",
        "program_visibility_date",
        "program_start_date",
        "program_close_date",
        "program_submit_date",
        "program_end_date",
        "builder_incentive_dollar_value",
        "rater_incentive_dollar_value",
        "min_hers_score",
        "max_hers_score",
        "per_point_adder",
        "comment",
        "owner_name",
        "owner_url",
        "is_active",
        "bulk_checklist_download_url",
        "checklist_download_url",
        "workflow",
        "workflow_name",
        "program_submit_warning",
        "program_submit_warning_date",
        "program_close_warning",
        "program_close_warning_date",
    )

    requirements_fieldset = (
        "require_builder_assigned_to_home",
        "require_builder_relationship",
        "require_hvac_assigned_to_home",
        "require_hvac_relationship",
        "require_utility_assigned_to_home",
        "require_utility_relationship",
        "require_rater_assigned_to_home",
        "require_rater_relationship",
        "require_provider_assigned_to_home",
        "require_provider_relationship",
        "require_qa_assigned_to_home",
        "require_qa_relationship",
        "require_input_data",
        "require_rem_data",
        "require_model_file",
        "require_ekotrope_data",
        "require_resnet_epa_is_active",
        "require_rater_of_record",
        "require_energy_modeler",
        "require_field_inspector",
    )
    settings_fieldset = (
        "is_active",
        "manual_transition_on_certify",
        "allow_sampling",
        "allow_metro_sampling",
        "certifiable_by",  # 'viewable_by_company_type'
        "certifiable_by_details",
        "opt_in",
    )
    annotations_fieldset = (
        "required_annotation_types",
        "required_annotation_types_names",
    )
    checklist_fieldset = (
        "required_checklists",
        "required_checklists_names",
    )

    def __init__(self, *args, **kwargs):
        self.field_map = {
            "main": self.main_fieldset,
            "requirements": self.requirements_fieldset,
            "settings": self.settings_fieldset,
            "annotations": self.annotations_fieldset,
            "checklist": self.checklist_fieldset,
        }
        super(EEPProgramSerializer, self).__init__(*args, **kwargs)
        if "required_checklists" in self.fields:
            self.fields["required_checklists"].queryset = CheckList.objects.filter_by_user(
                self.context["request"].user
            )

    def validate(self, data):
        if data.get("program_visibility_date") and not data.get("program_start_date"):
            raise serializers.ValidationError(
                "You must have a start date with a program visibility date"
            )

        if data.get("program_visibility_date") and data.get("program_start_date"):
            if data["program_start_date"] < data["program_visibility_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program start before its visible date."
                )
        if data.get("program_visibility_date") and data.get("program_close_date"):
            if data["program_close_date"] < data["program_visibility_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program close before its visible date."
                )
        if data.get("program_visibility_date") and data.get("program_submit_date"):
            if data["program_submit_date"] < data["program_visibility_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program submit before its visible date."
                )
        if data.get("program_visibility_date") and data.get("program_end_date"):
            if data["program_end_date"] < data["program_visibility_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program end before its visible date."
                )

        if data.get("program_start_date") and data.get("program_visibility_date"):
            if data["program_start_date"] < data["program_visibility_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program start before its visible date."
                )
        if data.get("program_start_date") and data.get("program_close_date"):
            if data["program_close_date"] < data["program_start_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program close before its start date."
                )
        if data.get("program_start_date") and data.get("program_submit_date"):
            if data["program_submit_date"] < data["program_start_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program submit before its start date."
                )
        if data.get("program_start_date") and data.get("program_end_date"):
            if data["program_end_date"] < data["program_start_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program end before its start date."
                )

        if data.get("program_close_date") and data.get("program_visibility_date"):
            if data["program_close_date"] < data["program_visibility_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program close before its visible date."
                )
        if data.get("program_close_date") and data.get("program_start_date"):
            if data["program_close_date"] < data["program_start_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program close before its start date."
                )
        if data.get("program_close_date") and data.get("program_submit_date"):
            if data["program_submit_date"] < data["program_close_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program submit before its close date."
                )
        if data.get("program_close_date") and data.get("program_end_date"):
            if data["program_end_date"] < data["program_close_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program end before its close date."
                )

        if data.get("program_submit_date") and data.get("program_visibility_date"):
            if data["program_submit_date"] < data["program_visibility_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program submit before its visible date."
                )
        if data.get("program_submit_date") and data.get("program_start_date"):
            if data["program_submit_date"] < data["program_start_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program submit before its start date."
                )
        if data.get("program_submit_date") and data.get("program_close_date"):
            if data["program_submit_date"] < data["program_close_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program submit before its close date."
                )
        if data.get("program_submit_date") and data.get("program_end_date"):
            if data["program_end_date"] < data["program_submit_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program end before its submit date."
                )

        if data.get("program_close_warning") and not data.get("program_close_warning_date"):
            raise serializers.ValidationError(
                "You must specify a warning date to use a warning message."
            )
        if data.get("program_close_warning_date") and not data.get("program_close_warning"):
            raise serializers.ValidationError(
                "You must specify a warning message to use a warning date."
            )
        if data.get("program_close_date") and data.get("program_close_warning_date"):
            if data["program_close_date"] < data["program_close_warning_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program close before its warning period."
                )

        if data.get("program_submit_warning") and not data.get("program_submit_warning_date"):
            raise serializers.ValidationError(
                "You must specify a warning date to use a warning message."
            )
        if data.get("program_submit_warning_date") and not data.get("program_submit_warning"):
            raise serializers.ValidationError(
                "You must specify a warning message to use a warning date."
            )
        if data.get("program_submit_date") and data.get("program_submit_warning_date"):
            if data["program_submit_date"] < data["program_submit_warning_date"]:
                raise serializers.ValidationError(
                    "You cannot have a program submit before its warning period."
                )

        if data.get("min_hers_score") and data.get("max_hers_score"):
            if data["max_hers_score"] < data["min_hers_score"]:
                raise serializers.ValidationError(
                    "Max HERs  Score needs to be more than the Min HERs Score"
                )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        if not user.is_superuser:
            validated_data["owner"] = user.company

        return super(EEPProgramSerializer, self).create(validated_data)

    def get_fields(self):
        fields = super(EEPProgramSerializer, self).get_fields()

        try:
            fieldset = self.context["request"].query_params["fieldset"]
        except KeyError:
            pass
        else:
            if fieldset:
                allowed_fields = list(self.field_map[fieldset]) + ["id"]

                for key in list(fields.keys()):
                    if key not in allowed_fields:
                        del fields[key]

        return fields

    def get_required_checklists_names(self, instance):
        if instance.pk:
            checklists = instance.required_checklists.prefetch_related(
                "questions", "questions__question_choice"
            ).all()
            return CheckListSerializerNestedQuestions(instance=list(checklists), many=True).data

        return []

    def get_required_annotation_types_names(self, instance):
        if instance.pk:
            return AnnotationTypeSerializer(
                instance=list(instance.required_annotation_types.all()), many=True
            ).data

        return []

    def get_bulk_checklist_download_url(self, instance):
        if not instance.id:
            return None

        return reverse("checklist:bulk_checklist_download", kwargs={"pk": instance.id})

    def get_checklist_download_url(self, instance):
        if not instance.id:
            return None

        return reverse("home:download_single_program", kwargs={"eep_program": instance.id})

    def get_subdivisions(self, instance):
        from axis.subdivision.models import Subdivision

        return [
            {"url": sub.get_absolute_url(), "name": "{}".format(sub)}
            for sub in Subdivision.objects.filter(eep_programs=instance)
        ]

    def get_certifiable_by_details(self, instance):
        if instance.id:
            return {
                company.id: {"name": "{}".format(company), "url": company.get_absolute_url()}
                for company in instance.certifiable_by.all()
            }

        return {}
