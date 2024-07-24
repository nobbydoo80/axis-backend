__author__ = "Michael Jeffrey"
__date__ = "8/14/15 11:14 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

import datetime

from django.apps import apps

from rest_framework import serializers

from axis.filehandling.api import CustomerDocumentSerializer
from axis.home.tasks import update_home_states
from axis.qa.models import QARequirement
from axis.qa.state_machine import QAStateMachine

from .models import QAStatus, QANote, Observation, ObservationType
from . import strings

customer_hirl_app = apps.get_app_config("customer_hirl")


class ObservationSerializer(serializers.ModelSerializer):
    observation_type = serializers.ReadOnlyField(source="observation_type.name")

    class Meta:
        model = Observation
        fields = ("user", "created_on", "observation_type")


class ObservationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationType
        fields = "__all__"
        read_only_fields = ("company",)

    def validate(self, attrs):
        attrs["company"] = self.context["request"].company
        return attrs


class QARequirementSerializer(serializers.ModelSerializer):
    qa_company_name = serializers.CharField(source="qa_company.name", read_only=True)
    eep_program_name = serializers.CharField(source="eep_program.name", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = QARequirement
        fields = (
            # Fields
            "id",
            "qa_company",
            "coverage_pct",
            "gate_certification",
            "eep_program",
            "type",
            # Virtual Fields
            "qa_company_name",
            "eep_program_name",
            "type_display",
        )


class QANoteSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source="user.get_full_name", read_only=True)
    observation_set = ObservationSerializer(many=True, read_only=True)
    customer_documents = CustomerDocumentSerializer(many=True, read_only=True)
    requirement_eep_program_name = serializers.CharField(
        source="qa_status.requirement.eep_program.name", read_only=True
    )
    requirement_eep_program_slug = serializers.CharField(
        source="qa_status.requirement.eep_program.slug", read_only=True
    )
    last_update_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QANote
        fields = (
            "id",
            "qa_status",
            "note",
            "user",
            "content_type",
            "object_id",
            "observation_set",
            "last_update",
            "created_on",
            "customer_documents",
            # Virtual Fields
            "user_display",
            "requirement_eep_program_name",
            "requirement_eep_program_slug",
            "last_update_display",
        )

    def get_last_update_display(self, obj):
        return obj.last_update.replace(tzinfo=datetime.timezone.utc)


class QAStatusSerializer(serializers.ModelSerializer):
    requirement_eep_program_name = serializers.CharField(
        source="requirement.eep_program.name", read_only=True
    )
    requirement_eep_program_slug = serializers.CharField(
        source="requirement.eep_program.slug", read_only=True
    )
    requirement_qa_company_name = serializers.CharField(
        source="requirement.qa_company.name", read_only=True
    )
    requirement_gate_certification = serializers.BooleanField(
        source="requirement.gate_certification", read_only=True
    )
    requirement_type = serializers.CharField(source="requirement.type", read_only=True)
    requirement_type_display = serializers.CharField(
        source="requirement.get_type_display", read_only=True
    )
    qa_eep_program_id = serializers.SerializerMethodField(read_only=True)
    qa_designee_name = serializers.CharField(source="qa_designee.get_full_name", read_only=True)

    observations = serializers.SerializerMethodField(read_only=True)
    customer_documents = CustomerDocumentSerializer(many=True, read_only=True)

    state_display = serializers.CharField(source="get_state_display", read_only=True)
    result_display = serializers.CharField(source="get_result_display", read_only=True)
    new_state = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True
    )
    note = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=QANote._meta.get_field("note").max_length,
    )
    qanote_documents = serializers.JSONField(write_only=True, required=False, allow_null=True)
    rater_of_record = serializers.ReadOnlyField(source="home_status.rater_of_record.id")
    observation_types = serializers.ListField(
        write_only=True, required=False, allow_null=True, child=serializers.IntegerField()
    )
    hirl_verifier_points_reported = serializers.IntegerField(allow_null=True, required=False)
    hirl_verifier_points_awarded = serializers.IntegerField(allow_null=True, required=False)
    hirl_reviewer_wri_value_awarded = serializers.IntegerField(allow_null=True, required=False)
    hirl_commercial_space_confirmed = serializers.BooleanField(allow_null=True, default=False)
    hirl_water_sense_confirmed = serializers.BooleanField(allow_null=True, default=False)
    hirl_certification_level_awarded_display = serializers.SerializerMethodField()
    hirl_badges_awarded_display = serializers.SerializerMethodField()
    customer_hirl_verifier_display = serializers.SerializerMethodField()
    customer_hirl_project_green_energy_badges = serializers.SerializerMethodField()
    customer_hirl_project_is_require_water_sense_certification = serializers.CharField(
        source="home_status.customer_hirl_project.is_require_water_sense_certification",
        read_only=True,
    )
    customer_hirl_project_is_require_wri_certification = serializers.CharField(
        source="home_status.customer_hirl_project.is_require_wri_certification",
        read_only=True,
    )
    # using to access verifier for Inspection grades via region_dependency like:
    # machinery_summary['region_dependencies']['qa_status'] = [{
    #    'serialize_as': 'user_id',
    #    'field_name': 'hirl_verifier'
    # }]
    hirl_verifier = serializers.SerializerMethodField()

    class Meta:
        model = QAStatus
        fields = (
            "id",
            "correction_types",
            "created_on",
            "customer_documents",
            "has_failed",
            "has_observations",
            "last_update",
            "owner",
            "requirement",
            "state",
            "result",
            "qa_designee",
            "hirl_verifier_points_reported",
            "hirl_verifier_points_awarded",
            "hirl_certification_level_awarded",
            "hirl_certification_level_awarded_display",
            "hirl_badges_awarded",
            "hirl_badges_awarded_display",
            "hirl_commercial_space_confirmed",
            "hirl_reviewer_wri_value_awarded",
            "hirl_water_sense_confirmed",
            "customer_hirl_project_green_energy_badges",
            "customer_hirl_project_is_require_water_sense_certification",
            "customer_hirl_project_is_require_wri_certification",
            # Parent types
            "home_status",
            "subdivision",
            # Virtualized read-only/write-only fields
            "requirement_eep_program_name",
            "requirement_eep_program_slug",
            "requirement_qa_company_name",
            "requirement_gate_certification",
            "requirement_type",
            "requirement_type_display",
            "qa_eep_program_id",
            "observations",
            "state_display",
            "result_display",
            "new_state",
            "note",
            "observation_types",
            "qanote_documents",
            "qa_designee_name",
            "rater_of_record",
            "hirl_verifier",
            "customer_hirl_verifier_display",
        )

    def to_representation(self, instance):
        data = super(QAStatusSerializer, self).to_representation(instance)
        # convert boolean to string for frontend
        # select widget to display correct initial False value
        data["hirl_commercial_space_confirmed"] = (
            "true" if data["hirl_commercial_space_confirmed"] else "false"
        )
        data["hirl_water_sense_confirmed"] = (
            "true" if data["hirl_water_sense_confirmed"] else "false"
        )
        return data

    def to_internal_value(self, data):
        if data.get("hirl_verifier_points_reported", None) == "":
            data["hirl_verifier_points_reported"] = None
        if data.get("hirl_verifier_points_awarded", None) == "":
            data["hirl_verifier_points_awarded"] = None
        if data.get("hirl_reviewer_wri_value_awarded", None) == "":
            data["hirl_reviewer_wri_value_awarded"] = None
        return super(QAStatusSerializer, self).to_internal_value(data)

    def get_qa_eep_program_id(self, obj):
        if obj.pk:
            try:
                if obj.requirement.type == "field":
                    from axis.eep_program.models import EEPProgram

                    slug = obj.requirement.eep_program.slug + "-qa"
                    return EEPProgram.objects.get(slug=slug).id
            except AttributeError:
                # obj may not exist yet.
                pass
        return None

    def save(self, **kwargs):
        from axis.home.models import EEPProgramHomeStatus

        self.instance = super(QAStatusSerializer, self).save(**kwargs)

        # Initialize input-collection for qa
        qa_program = self.instance.home_status.eep_program.get_qa_program()
        if qa_program:
            qa_home_status = self.instance.home_status.home.homestatuses.filter(
                eep_program=qa_program
            ).first()
            if qa_home_status:
                uses_input_collection = qa_program.collection_request
                needs_initialization = not qa_home_status.collection_request
                if uses_input_collection and needs_initialization:
                    qa_home_status.set_collection_from_program()

        note = getattr(self.instance, "note", None)
        qa_note_documents = getattr(self.instance, "qanote_documents", None)

        if qa_note_documents and not note:
            raise serializers.ValidationError({"note": ["This field is required."]})

        if note is not None:
            from django.contrib.contenttypes.models import ContentType

            parent_obj = self.instance.get_parent()
            ct = ContentType.objects.get_for_model(parent_obj)
            qa_note = QANote.objects.create(
                qa_status_id=self.instance.id,
                note=note,
                user=self.context["request"].user,
                content_type=ct,
                object_id=parent_obj.id,
            )

            if qa_note_documents:
                for note_document in qa_note_documents:
                    from axis.filehandling.forms import CustomerDocumentForm

                    form = CustomerDocumentForm(data=note_document, raw_file_only=True)
                    if form.is_valid():
                        document = form.save(commit=False)
                        document.content_object = qa_note
                        document.type = "document"
                        document.filesize = form.cleaned_data["document"].size
                        document.company = self.context["request"].user.company
                        document.save()

            if hasattr(self.instance, "observation_types"):
                # self.instance.observation_types is assigned by the serializer save() super, due to it
                # being a writable serializer field.  It is not, however, a model field, but we will
                # inspect the model to find what value ended up on the object.  We trust them because
                # they are cleaned and validated, which is better than looking directly at request.data.

                # The instance attribute is checked via hasattr to make sure something was sent.

                self.record_observations(self.instance.observation_types, qa_note)

        new_state = getattr(self.instance, "new_state", None)

        if new_state:
            self.instance.make_transition(new_state)

            if new_state.endswith("complete"):
                # update_home_states used to be handled by the QAStatus post_save trigger.
                # The trigger would see if it could automatically transition to a complete state
                # and certify the home. In this case, it would transition the home to complete
                # 2 times, messing with the history of the instance. So now we
                # update_home_states manually.  Only when going to complete, because
                # update_home_states will try to certify a home, and we don't want that
                # happening in any other state.
                if self.instance.home_status:
                    home_statuses = [self.instance.home_status]
                elif self.instance.subdivision:
                    home_statuses = list(
                        EEPProgramHomeStatus.objects.filter(
                            home__subdivision=self.instance.subdivision
                        )
                    )
                update_home_states(
                    eepprogramhomestatus_ids=[x.id for x in home_statuses],
                    user_id=self.context["request"].user.id,
                )
                [x.validate_references() for x in home_statuses]

        return self.instance

    def validate(self, attrs):
        try:
            new_state = attrs["new_state"]
        except KeyError:
            pass
        else:
            note = attrs.get("note", None)
            result = attrs.get("result", None)
            self._validate_state_transition(new_state, attrs, note, result)

        return attrs

    def _validate_state_transition(self, new_state, attrs, note, result):
        notes_required_transitions = [
            "in_progress_to_correction_required",
            "correction_required_to_correction_received",
            "correction_received_to_correction_required",
        ]

        to_complete_transitions = ["correction_received_to_complete", "in_progress_to_complete"]

        if new_state in notes_required_transitions:
            if note in ["", None]:
                description = QAStateMachine.transitions[new_state].description
                raise serializers.ValidationError(
                    strings.MISSING_REQUIRED_NOTE.format(state_description=description)
                )

        if attrs.get("observation_types") and not note:
            raise serializers.ValidationError("New Observations require Note")

        if new_state in to_complete_transitions:
            if result in ["", None]:
                raise serializers.ValidationError(strings.MISSING_RESULT)

        if result not in ["", None]:
            if new_state not in to_complete_transitions:
                raise serializers.ValidationError(strings.INCORRECT_STATE_FOR_COMPLETE)

        if result == QAStatus.PASS_STATUS:
            if self.instance and getattr(self.instance, "home_status", None):
                home_status = self.instance.home_status
                customer_hirl_project = getattr(home_status, "customer_hirl_project", None)
                if customer_hirl_project:
                    if self.instance and getattr(self.instance, "requirement", None):
                        requirement_type = self.instance.requirement.type
                        eep_program = self.instance.requirement.eep_program

                        # Customer HIRL Programs require at least one Verification grade for PASS state
                        if requirement_type in [
                            QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
                            QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                            QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE,
                            QARequirement.ROUGH_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE,
                            QARequirement.FINAL_INSPECTION_VIRTUAL_AUDIT_REQUIREMENT_TYPE,
                        ]:
                            if (
                                not customer_hirl_project.is_accessory_structure
                                and not customer_hirl_project.commercial_space_type
                            ):
                                if (
                                    eep_program.slug
                                    in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
                                ):
                                    if not self.instance.inspectiongrade_set.count():
                                        raise serializers.ValidationError(
                                            "Please provide at least one Verification grade"
                                        )

                        if requirement_type == QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE:
                            if not self.instance.qanote_set.count():
                                raise serializers.ValidationError(
                                    "Please provide at least one Note"
                                )

                        if requirement_type == QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE:
                            desktop_audit_exists = home_status.qastatus_set.filter(
                                requirement__type=QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE
                            ).exists()

                            desktop_audit_qa_notes_count = QANote.objects.filter(
                                qa_status__home_status=home_status,
                                qa_status__requirement__type=QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE,
                            ).count()
                            if desktop_audit_exists and not desktop_audit_qa_notes_count:
                                raise serializers.ValidationError(
                                    "Please provide at least one Note for Desktop Audit QA"
                                )

                        if requirement_type == QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE:
                            from axis.customer_hirl.models import HIRLProject

                            if (
                                self.instance.requirement.eep_program.slug
                                in customer_hirl_app.WRI_PROGRAM_LIST
                            ):
                                required_fields = [
                                    "hirl_reviewer_wri_value_awarded",
                                ]
                            elif (
                                self.instance.home_status.customer_hirl_project.land_development_project_type
                                == HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT
                            ):
                                required_fields = [
                                    "hirl_certification_level_awarded",
                                ]
                            else:
                                required_fields = [
                                    "hirl_verifier_points_reported",
                                    "hirl_verifier_points_awarded",
                                    "hirl_certification_level_awarded",
                                ]

                            for field_name in required_fields:
                                if not attrs.get(field_name):
                                    raise serializers.ValidationError(
                                        {field_name: "This field is required"}
                                    )

                            incomplete_desktop_audit_exists = (
                                home_status.qastatus_set.filter(
                                    requirement__type=QARequirement.DESKTOP_AUDIT_REQUIREMENT_TYPE
                                )
                                .exclude(result=QAStatus.PASS_STATUS, state="complete")
                                .exists()
                            )
                            if incomplete_desktop_audit_exists:
                                raise serializers.ValidationError(
                                    "Please complete Desktop Audit QA"
                                )

                            if (
                                self.instance.requirement.eep_program.slug
                                not in customer_hirl_app.WRI_PROGRAM_LIST
                                and self.instance.home_status.customer_hirl_project.land_development_project_type
                                != HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT
                            ):
                                hirl_certification_level_awarded = attrs.get(
                                    "hirl_certification_level_awarded"
                                )
                                hirl_verifier_points_awarded = attrs.get(
                                    "hirl_verifier_points_awarded"
                                )

                                certification_level_choices_map = dict(
                                    QAStatus.HIRL_CERTIFICATION_LEVEL_AWARDED_CHOICES
                                )

                                per_level_validation_checks_map = [
                                    {
                                        "eep_program_slugs": [
                                            "ngbs-sf-whole-house-remodel-2020-new",
                                            "ngbs-mf-whole-house-remodel-2020-new",
                                            "ngbs-sf-whole-house-remodel-2015-new",
                                            "ngbs-mf-whole-house-remodel-2015-new",
                                            "ngbs-sf-whole-house-remodel-2012-new",
                                            "ngbs-mf-whole-house-remodel-2012-new",
                                        ],
                                        "min_points_awarded": 88,
                                        "levels": [
                                            {
                                                "level": QAStatus.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 125,
                                            },
                                            {
                                                "level": QAStatus.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 181,
                                            },
                                            {
                                                "level": QAStatus.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 225,
                                            },
                                        ],
                                    },
                                    {
                                        "eep_program_slugs": [
                                            "ngbs-sf-new-construction-2020-new",
                                            "ngbs-mf-new-construction-2020-new",
                                            "ngbs-sf-new-construction-2015-new",
                                            "ngbs-mf-new-construction-2015-new",
                                            "ngbs-sf-new-construction-2012-new",
                                            "ngbs-mf-new-construction-2012-new",
                                        ],
                                        "min_points_awarded": 231,
                                        "levels": [
                                            {
                                                "level": QAStatus.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 334,
                                            },
                                            {
                                                "level": QAStatus.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 489,
                                            },
                                            {
                                                "level": QAStatus.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 611,
                                            },
                                        ],
                                    },
                                    {
                                        "eep_program_slugs": [
                                            "ngbs-sf-new-construction-2012-new",
                                            "ngbs-mf-new-construction-2012-new",
                                        ],
                                        "min_points_awarded": 231,
                                        "levels": [
                                            {
                                                "level": QAStatus.SILVER_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 349,
                                            },
                                            {
                                                "level": QAStatus.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 509,
                                            },
                                            {
                                                "level": QAStatus.EMERALD_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 641,
                                            },
                                        ],
                                    },
                                    {
                                        "eep_program_slugs": [
                                            "ngbs-land-development-2020-new",
                                        ],
                                        "min_points_awarded": 95,
                                        "levels": [
                                            {
                                                "level": QAStatus.TWO_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 122,
                                            },
                                            {
                                                "level": QAStatus.THREE_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 149,
                                            },
                                            {
                                                "level": QAStatus.FOUR_STARS_HIRL_CERTIFICATION_LEVEL_AWARDED,
                                                "min_points_awarded": 176,
                                            },
                                        ],
                                    },
                                ]

                                for level_data in per_level_validation_checks_map:
                                    if eep_program.slug in level_data["eep_program_slugs"]:
                                        if (
                                            hirl_verifier_points_awarded
                                            < level_data["min_points_awarded"]
                                        ):
                                            raise serializers.ValidationError(
                                                "Not enough points for any level"
                                            )
                                        for level_check_data in level_data["levels"]:
                                            if (
                                                hirl_certification_level_awarded
                                                == level_check_data["level"]
                                                and hirl_verifier_points_awarded
                                                < level_check_data["min_points_awarded"]
                                            ):
                                                certification_level_display = (
                                                    certification_level_choices_map[
                                                        level_check_data["level"]
                                                    ]
                                                )
                                                raise serializers.ValidationError(
                                                    f"Not enough points for {certification_level_display}"
                                                )

    def record_observations(self, observation_type_ids, qa_note):
        user = self.context["request"].user
        queryset = ObservationType.objects.filter_by_user(user, id__in=observation_type_ids)
        for observation_type in queryset:
            self.instance.observation_set.create(
                **{
                    "observation_type": observation_type,
                    "user": user,
                    "qa_note": qa_note,
                }
            )
            self.instance.has_observations = True
            self.instance.save()

    def get_observations(self, obj):
        if obj.pk:
            return ObservationSerializer(
                instance=obj.observation_set.all(), many=True, read_only=True, required=False
            ).data
        return []

    def get_hirl_verifier(self, qa_status):
        verifier = qa_status.get_customer_hirl_grading_verifier()
        if verifier:
            return verifier.pk
        return None

    def get_customer_hirl_verifier_display(self, qa_status):
        verifier = qa_status.get_customer_hirl_grading_verifier()
        if verifier:
            return f"<a href='{verifier.get_absolute_url()}'>{verifier.get_full_name()}</a>"
        return ""

    def get_hirl_certification_level_awarded_display(self, obj):
        if not obj.pk:
            return ""
        return obj.get_hirl_certification_level_awarded_display()

    def get_hirl_badges_awarded_display(self, obj):
        if not obj.pk:
            return ""
        return ", ".join(obj.hirl_badges_awarded.all().values_list("name", flat=True))

    def get_customer_hirl_project_green_energy_badges(self, qa_status):
        if getattr(qa_status, "home_status", None):
            if getattr(qa_status.home_status, "customer_hirl_project", None):
                return qa_status.home_status.customer_hirl_project.green_energy_badges.values_list(
                    "id", flat=True
                )
        return []
