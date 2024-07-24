__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers

from axis.certification.utils import get_owner_swap_queryset
from axis.company.models import Company
from axis.core.utils import make_safe_field
from axis.customer_eto.serializers import PermitAndOccupancySettingsFieldsMixin
from axis.customer_hirl.api_v3.serializers.hirl_project import (
    HIRLProjectSerializerMixin,
    HIRLProjectMeta,
)
from axis.geographic.models import City
from axis.geographic.serializers import RawAddressPreferenceSerializerMixin
from axis.invoicing.models import InvoiceItemGroup, InvoiceItem, Invoice
from axis.qa.models import QAStatus, QARequirement
from axis.relationship.utils import modify_relationships
from axis.scheduling.models import ConstructionStage
from axis.subdivision.models import Subdivision
from .api_v3.serializers import HomeAddressIsUniqueRequestDataSerializer
from .messages import RaterAssociatedWithHomeStatMessage
from .models import EEPProgramHomeStatus, Home
from .utils import validate_compatible_program

log = logging.getLogger(__name__)


class HomeSerializer(
    RawAddressPreferenceSerializerMixin,
    PermitAndOccupancySettingsFieldsMixin,
    serializers.ModelSerializer,
):
    city = serializers.PrimaryKeyRelatedField(required=False, queryset=City.objects.all())
    subdivision = serializers.PrimaryKeyRelatedField(
        allow_null=True, required=False, queryset=Subdivision.objects.all()
    )
    county = serializers.PrimaryKeyRelatedField(read_only=True)
    metro = serializers.PrimaryKeyRelatedField(read_only=True)

    city_name = serializers.CharField(source="city.name", read_only=True)
    county_name = make_safe_field(serializers.CharField)(
        source="county.legal_statistical_area_description", read_only=True
    )
    metro_name = make_safe_field(serializers.CharField)(source="metro.as_string", read_only=True)
    country_name = serializers.CharField(source="city.country.name", read_only=True)

    subdivision_name = make_safe_field(serializers.CharField)(
        source="subdivision.name", read_only=True
    )
    subdivision_url = make_safe_field(serializers.CharField)(
        source="subdivision.get_absolute_url", read_only=True
    )
    community_name = make_safe_field(serializers.CharField)(
        source="subdivision.community.name", read_only=True
    )
    community_url = make_safe_field(serializers.CharField)(
        source="subdivision.community.get_absolute_url", read_only=True
    )
    gbr_id = serializers.CharField(source="gbr.gbr_id", read_only=True)
    gbr_status = serializers.CharField(source="gbr.get_status_display", read_only=True)
    gbr_external_url = serializers.CharField(source="gbr.external_url", read_only=True)

    # Virtual fields
    updated_construction_stage = serializers.SerializerMethodField("get_construction_stage")
    construction_stage_name = serializers.SerializerMethodField()
    construction_stage_start_date = serializers.SerializerMethodField()
    address_designator = serializers.CharField(source="get_address_designator", read_only=True)
    climate_zone = serializers.CharField(source="county.climate_zone", read_only=True)
    raw_address = serializers.CharField(
        source="geocode_response.geocode.raw_address", read_only=True
    )
    geocoded_address = serializers.SerializerMethodField()
    subdivision_is_multi_family = make_safe_field(serializers.BooleanField)(
        source="subdivision.is_multi_family", read_only=True
    )
    company_display_raw_addresses = serializers.SerializerMethodField()

    eto_region_name = serializers.SerializerMethodField()
    building_type_display = serializers.SerializerMethodField()

    # ETO Permit and Occupancy fields
    reeds_crossing_compliance_option = serializers.SerializerMethodField()
    rosedale_parks_compliance_option = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = (
            "lot_number",
            "street_line1",
            "street_line2",
            "is_multi_family",
            "city",
            "subdivision",
            "zipcode",
            "address_override",
            # Hidden
            "id",
            "geocode_response",
            "confirmed_address",
            "latitude",
            "longitude",
            # Virtual fields
            "city_name",
            "county_name",
            "metro_name",
            "country_name",
            "county",
            "metro",
            "state",
            "climate_zone",
            "address_designator",
            "subdivision_name",
            "subdivision_url",
            "raw_address",
            "geocoded_address",
            "community_name",
            "community_url",
            "updated_construction_stage",
            "construction_stage_name",
            "construction_stage_start_date",
            "subdivision_is_multi_family",
            "company_display_raw_addresses",
            "eto_region_name",
            "building_type_display",
            # ETO Permit and Occupancy fields
            "reeds_crossing_compliance_option",
            "rosedale_parks_compliance_option",
            # GBR
            "gbr_id",
            "gbr_status",
            "gbr_external_url",
        )
        read_only_fields = ("id", "confirmed_address", "latitude", "longitude")

    def get_fields(self):
        fields = super(HomeSerializer, self).get_fields()
        fields["street_line1"].required = True
        fields["zipcode"].required = True
        return fields

    def get_construction_stage(self, obj):
        # Virtual field value
        current_stage = None
        if self.context["request"] is not None:
            user = self.context["request"].user
            current_stage = obj.get_current_stage(user)
        if current_stage:
            return current_stage.stage_id

    def get_construction_stage_name(self, obj):
        # Virtual field value
        current_stage = None
        if self.context["request"] is not None:
            user = self.context["request"].user
            current_stage = obj.get_current_stage(user)
        if current_stage:
            return current_stage.stage.name

    def get_construction_stage_start_date(self, obj):
        # Virtual field value
        current_stage = None
        if self.context["request"] is not None:
            user = self.context["request"].user
            current_stage = obj.get_current_stage(user)
        if current_stage:
            return current_stage.start_date

    def get_geocoded_address(self, obj):
        if not obj.pk:
            return ""
        return obj.get_addr(include_city_state_zip=True)

    def get_eto_region_name(self, obj):
        if obj.pk and hasattr(self.context["request"], "user"):
            return obj.get_eto_region_name_for_zipcode(self.context["request"].user)

    def validate(self, attrs):
        if attrs.get("subdivision") and attrs["subdivision"].is_multi_family:
            if not attrs["is_multi_family"]:
                raise serializers.ValidationError(
                    {
                        "is_multi_family": "Multi-family subdivisions require the unit to be marked multi-family to match.",
                    }
                )

        is_unique, home = HomeAddressIsUniqueRequestDataSerializer().home_address_is_unique(
            instance=self.instance,
            street_line1=attrs["street_line1"],
            city=attrs["city"],
            zipcode=attrs["zipcode"],
            street_line2=attrs["street_line2"] or "",
            is_multi_family=attrs["is_multi_family"],
            geocode_response=attrs.get("geocode_response"),
        )

        log.info(
            "Validated {} address {}".format(
                "unique" if is_unique else "existing", home if home else ""
            )
        )

        if not is_unique:
            company = None
            if "request" in self.context:
                company = self.context["request"].company

            message = "<a target='_blank' href='{url}'>{text}</a> already exists in Axis. Please verify and/or correct the address before continuing."
            message = message.format(
                id=home.id, url=home.get_absolute_url(), text=home.get_addr(company=company)
            )
            raise serializers.ValidationError(message)

        return attrs

    def _save(self, obj: Home):
        """Trigger blank relationship save for new objects so that is_custom_home is set."""

        request = self.context["request"]

        try:
            construction_stage = int(request.data.get("updated_construction_stage"))
        except (ValueError, TypeError):
            construction_stage = None
        if construction_stage:
            construction_stage = ConstructionStage.objects.filter(is_public=True).get(
                id=construction_stage
            )
            obj.constructionstatus_set.create(
                stage=construction_stage, company=request.user.company, start_date=now()
            )

        relationship_data = obj.get_orgs()  # Use existing company breakdown
        modify_relationships(obj, relationship_data, request.user, request=request)
        obj.validate_references()

    def create(self, validated_data):
        # Avoid trusting the client to have sent an explicit None for geocode_response
        if validated_data.get("address_override"):
            validated_data["geocode_response"] = None

        instance = super(HomeSerializer, self).create(validated_data)
        self._save(instance)
        return instance

    def update(self, instance, validated_data):
        # Avoid trusting the client to have sent an explicit None for geocode_response
        if validated_data.get("address_override"):
            validated_data["geocode_response"] = None

        instance = super(HomeSerializer, self).update(instance, validated_data)
        self._save(instance)
        return instance

    def get_building_type_display(self, home: Home) -> str:
        if home.pk:
            home_status = home.homestatuses.filter(customer_hirl_project__isnull=False).first()
            if home_status:
                if home_status.customer_hirl_project.is_accessory_structure:
                    return "Accessory Structure"
                if home_status.customer_hirl_project.is_accessory_dwelling_unit:
                    return "Accessory Dwelling Unit"
                if home_status.customer_hirl_project.commercial_space_type:
                    return "Commercial Space"
        return "Building"


class HomeUsersSerializer(serializers.ModelSerializer):
    users = make_safe_field(serializers.PrimaryKeyRelatedField)(
        many=True, queryset=get_user_model().objects.all()
    )
    users_names = make_safe_field(serializers.SerializerMethodField)()
    users_urls = make_safe_field(serializers.SerializerMethodField)()

    class Meta:
        model = Home
        fields = ("id", "users", "users_names", "users_urls")

    def get_users_names(self, obj):
        return {user.pk: "{}".format(user) for user in obj.users.all()}

    def get_users_urls(self, obj):
        return {user.pk: user.get_absolute_url() for user in obj.users.all()}


class HomeStatusSerializer(serializers.ModelSerializer):
    """Read/write serializer for new and existing homes."""

    floorplan = serializers.PrimaryKeyRelatedField(read_only=True)
    floorplans = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    fastrack_enh_id = serializers.CharField(
        source="fasttracksubmission.get_project_id", read_only=True
    )

    fastrack_sle_id = serializers.CharField(
        source="fasttracksubmission.get_solar_project_id", read_only=True
    )
    fastrack_submit_status = serializers.CharField(
        source="fasttracksubmission.get_submit_status_display", read_only=True
    )
    fastrack_solar_submit_status = serializers.CharField(
        source="fasttracksubmission.get_solar_submit_status_display", read_only=True
    )

    # Virtual fields
    resnet_id = make_safe_field(serializers.CharField)(
        source="floorplan.remrate_target.building.project.resnet_registry_id", read_only=True
    )
    rater_of_record_display = make_safe_field(serializers.CharField)(
        source="rater_of_record.get_full_name", read_only=True
    )
    energy_modeler_display = make_safe_field(serializers.CharField)(
        source="energy_modeler.get_full_name", read_only=True
    )
    customer_hirl_rough_verifier_display = serializers.SerializerMethodField()
    customer_hirl_final_verifier_display = serializers.SerializerMethodField()
    customer_hirl_certification_level = serializers.SerializerMethodField()
    field_inspectors_display = serializers.SerializerMethodField()
    eep_program_name = make_safe_field(serializers.CharField)(
        source="eep_program.name", read_only=True
    )
    state_name = serializers.SerializerMethodField()
    company_type = make_safe_field(serializers.CharField)(
        source="company.get_company_type_display", read_only=True
    )
    company_name = make_safe_field(serializers.CharField)(source="company.name", read_only=True)
    company_url = make_safe_field(serializers.CharField)(
        source="company.get_absolute_url", read_only=True
    )
    rating_type = serializers.CharField(source="get_rating_type", read_only=True)
    status = serializers.SerializerMethodField("get_simplified_status")
    sampleset = serializers.SerializerMethodField("get_sampleset_id")
    sampleset_name = serializers.SerializerMethodField()
    sampleset_url = serializers.SerializerMethodField()
    progress_url = serializers.SerializerMethodField()
    has_ipp_payments = serializers.SerializerMethodField()

    class Meta:
        model = EEPProgramHomeStatus
        fields = (
            "id",
            "certification_date",
            "company",
            "created_date",
            "eep_program",
            "floorplan",
            "floorplans",
            "home",
            "is_billable",
            "pct_complete",
            "state",
            "rater_of_record",
            "energy_modeler",
            "field_inspectors",
            "customer_hirl_rough_verifier",
            "customer_hirl_final_verifier",
            # Virtual
            "eep_program_name",
            "state_name",
            "company_type",
            "company_name",
            "company_url",
            "rating_type",
            "sampleset",
            "sampleset_name",
            "sampleset_url",
            "status",
            "progress_url",
            "has_ipp_payments",
            "fastrack_enh_id",
            "fastrack_sle_id",
            "fastrack_submit_status",
            "fastrack_solar_submit_status",
            "rater_of_record_display",
            "energy_modeler_display",
            "field_inspectors_display",
            "resnet_id",
            "customer_hirl_rough_verifier_display",
            "customer_hirl_final_verifier_display",
            "customer_hirl_certification_level",
        )
        read_only_fields = ("id", "company", "state")

    def __init__(self, *args, **kwargs):
        super(HomeStatusSerializer, self).__init__(*args, **kwargs)
        user = self.context["request"].user
        if self.context["request"].data:
            if not (user.is_superuser or user.company.company_type in ["provider", "rater"]):
                del self.fields["rater_of_record"]

    def send_association_message(self, assigning_company, assigned_company, home):
        message_context = {
            "assigning_company_url": assigning_company.get_absolute_url(),
            "assigning_company": "{}".format(assigning_company),
            "assigned_company_url": assigned_company.get_absolute_url(),
            "assigned_company": "{}".format(assigned_company),
            "home_url": home.get_absolute_url(),
            "home": "{}".format(home),
        }

        RaterAssociatedWithHomeStatMessage(url=message_context["home_url"]).send(
            context=message_context,
            company=assigned_company,
        )

    def create(self, validated_data: dict) -> EEPProgramHomeStatus:
        validated_data["company"] = self.context["request"].company
        validate_compatible_program(
            validated_data["home"],
            validated_data["eep_program"],
        )

        # If company is somehow invalid, replace it with None so that it is automatically taken
        # from the active user.
        valid_company_queryset = get_owner_swap_queryset(
            self.context["request"].user, include_self=True
        )
        if valid_company_queryset:
            valid_company_choices = list(valid_company_queryset.values_list("id", flat=True))
            try:
                company_id = int(self.context["request"].data.get("company"))
            except (KeyError, ValueError, TypeError):
                company_id = None
            if company_id and company_id not in valid_company_choices:
                company_id = None

            if company_id is None:
                validated_data["company"] = self.context["request"].user.company
            else:
                validated_data["company"] = Company.objects.get(id=company_id)

        assigning_company = self.context["request"].company
        assigned_company = validated_data["company"]
        if assigned_company.id != assigning_company.id:
            self.send_association_message(
                assigning_company, assigned_company, validated_data["home"]
            )

        obj = super(HomeStatusSerializer, self).create(validated_data)

        if validated_data["eep_program"].collection_request:
            obj.set_collection_from_program()

        obj.validate_references()

        return obj

    def update(self, instance: EEPProgramHomeStatus, validated_data: dict) -> EEPProgramHomeStatus:
        validate_compatible_program(
            validated_data["home"],
            validated_data["eep_program"],
            created_date=validated_data.get("created_date"),
            state=validated_data.get("state"),
            instance_eep_program=instance.eep_program,
        )

        previous_eep_program = instance.eep_program

        # If company is somehow invalid, replace it with None so that it is automatically taken
        # from the active user.
        valid_company_queryset = get_owner_swap_queryset(
            self.context["request"].user, include_self=True
        )
        if valid_company_queryset:
            valid_company_choices = list(valid_company_queryset.values_list("id", flat=True))
            try:
                company_id = int(self.context["request"].data.get("company"))
            except (KeyError, ValueError, TypeError):
                company_id = None
            if company_id and company_id not in valid_company_choices:
                company_id = None

            if company_id is None:
                validated_data["company"] = self.context["request"].user.company
            else:
                validated_data["company"] = Company.objects.get(id=company_id)

        assigning_company = self.context["request"].company
        assigned_company = validated_data["company"]
        if (
            assigned_company.id != instance.company.id
            and assigned_company.id != assigning_company.id
        ):
            self.send_association_message(assigning_company, assigned_company, instance.home)

        self.update_qa_statuses(instance, validated_data)

        # Reset state machine if program changed
        if validated_data["eep_program"] != instance.eep_program:
            log.info("Program has been changed - we need to go back to inspected")
            instance.make_transition("program_change_transition", user=self.context["request"].user)
            instance = EEPProgramHomeStatus.objects.get(id=instance.id)

        super(HomeStatusSerializer, self).update(instance, validated_data)
        instance.save(update_stats=True)

        program_changed = previous_eep_program != instance.eep_program
        has_collection_request = validated_data["eep_program"].collection_request
        if has_collection_request and program_changed:
            instance.collection_request.delete()
            instance.collection_request = None  # Local instance retains a bad ref
            instance.set_collection_from_program()

        instance.validate_references()
        return instance

    def update_qa_statuses(self, instance, validated_data):
        """
        Look to see if the user is trying to switch the program.
        Look to see if QA is assigned.
        for each QA status:
            get the requirement matching (company, type, new_program)
            reassign the status to point at the new requirement.
        """
        if instance.qastatus_set.count() and instance.eep_program != validated_data["eep_program"]:
            from axis.qa.models import QARequirement

            company_hints = instance.home.relationships.all().get_orgs(ids_only=True)

            for qa_stat in instance.qastatus_set.all():
                old_requirement = qa_stat.requirement
                new_requirement = QARequirement.objects.filter_by_company(
                    company=old_requirement.qa_company,
                    type=old_requirement.type,
                    eep_program=validated_data["eep_program"],
                    company_hints=company_hints,
                ).first()
                qa_stat.requirement = new_requirement
                qa_stat.save()

    def get_state_name(self, obj):
        return obj.get_state_info().description

    def _get_sampleset(self, obj):
        if not hasattr(self, "_sampleset"):
            setattr(self, "_sampleset", obj.get_sampleset())
        return self._sampleset

    def get_sampleset_id(self, obj):
        sampleset = self._get_sampleset(obj)
        if sampleset:
            return sampleset.pk
        return None

    def get_sampleset_name(self, obj):
        sampleset = self._get_sampleset(obj)
        if sampleset:
            return "{}".format(sampleset)
        return None

    def get_sampleset_url(self, obj):
        sampleset = self._get_sampleset(obj)
        if sampleset:
            return sampleset.get_absolute_url()
        return None

    def get_simplified_status(self, obj):
        if obj.pk:
            return obj.get_simplified_status_for_user(self.context["request"].user)
        return None

    def get_progress_url(self, obj):
        if obj.pk:
            return reverse("apiv2:home_status-progress", kwargs={"pk": obj.pk})
        return None

    def get_has_ipp_payments(self, obj):
        if obj.pk:
            return obj.ippitem_set.exists()
        return False

    def get_field_inspectors_display(self, obj):
        if not obj.pk:
            return ""
        names = [
            '<a href="{}" target="_blank">{}</a>'.format(
                reverse("profile:detail", kwargs={"pk": user.pk}), user.get_full_name()
            )
            for user in obj.field_inspectors.all()
        ]
        return ", ".join(names)

    def get_customer_hirl_certification_level(self, obj):
        certification_level_annotation = ""
        if obj.pk:
            try:
                certification_level_annotation = obj.qastatus_set.get(
                    requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
                ).get_hirl_certification_level_awarded_display()
            except QAStatus.DoesNotExist:
                certification_level_annotation = ""

        return certification_level_annotation

    def get_customer_hirl_rough_verifier_display(self, obj):
        if not obj.pk:
            return ""
        if getattr(obj, "customer_hirl_rough_verifier", None):
            verifier = obj.customer_hirl_rough_verifier
            if verifier:
                return f"<a href='{verifier.get_absolute_url()}'>{verifier.get_full_name()}</a>"
        return ""

    def get_customer_hirl_final_verifier_display(self, obj):
        if not obj.pk:
            return ""
        if getattr(obj, "customer_hirl_final_verifier", None):
            verifier = obj.customer_hirl_final_verifier
            if verifier:
                return f"<a href='{verifier.get_absolute_url()}'>{verifier.get_full_name()}</a>"
        return ""


class HomeStatusAnnotationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EEPProgramHomeStatus
        fields = "__all__"

    def to_representation(self, obj):
        values = {
            t.slug: v.content if v else None for (t, v) in obj.get_annotations_breakdown().items()
        }
        values["id"] = obj.id
        return values


class HomeStatusFloorplansThroughSerializer(serializers.ModelSerializer):
    class Meta:
        model = EEPProgramHomeStatus.floorplans.through


class HomeStatusHIRLProjectSerializer(HIRLProjectSerializerMixin, serializers.ModelSerializer):
    registration_sampling_display = serializers.SerializerMethodField()
    green_energy_badges_display = serializers.SerializerMethodField()
    project_client_display = serializers.SerializerMethodField()
    entity_responsible_for_payment_display = serializers.SerializerMethodField()
    application_packet_completion_display = serializers.SerializerMethodField()
    party_named_on_certificate_display = serializers.SerializerMethodField()
    legacy_certification_id = serializers.SerializerMethodField()

    vr_batch_submission_parent_rough_home_address = serializers.SerializerMethodField()
    vr_batch_submission_parent_final_home_address = serializers.SerializerMethodField()

    vr_batch_submission_parent_childrens_rough = serializers.SerializerMethodField()
    vr_batch_submission_parent_childrens_final = serializers.SerializerMethodField()

    vr_batch_submission_rough_childrens = serializers.SerializerMethodField()
    vr_batch_submission_final_childrens = serializers.SerializerMethodField()

    commercial_space_parent = serializers.ReadOnlyField()

    class Meta(HIRLProjectMeta):
        fields = HIRLProjectMeta.fields + (
            "registration_sampling_display",
            "green_energy_badges_display",
            "project_client_display",
            "entity_responsible_for_payment_display",
            "application_packet_completion_display",
            "party_named_on_certificate_display",
            "legacy_certification_id",
            "vr_batch_submission_parent_rough_home_address",
            "vr_batch_submission_parent_final_home_address",
            "vr_batch_submission_parent_childrens_rough",
            "vr_batch_submission_parent_childrens_final",
            "vr_batch_submission_rough_childrens",
            "vr_batch_submission_final_childrens",
        )

    def get_legacy_certification_id(self, hirl_project):
        return " ".join(
            hirl_project.hirllegacycertification_set.values_list("hirl_project_id", flat=True)
        )

    def get_registration_sampling_display(self, hirl_project):
        return hirl_project.registration.get_sampling_display()

    def get_project_client_display(self, hirl_project):
        return hirl_project.registration.get_project_client_display()

    def get_green_energy_badges_display(self, hirl_project):
        return ", ".join(hirl_project.green_energy_badges.values_list("name", flat=True))

    def get_entity_responsible_for_payment_display(self, hirl_project):
        return hirl_project.registration.get_entity_responsible_for_payment_display()

    def get_application_packet_completion_display(self, hirl_project):
        return hirl_project.registration.get_application_packet_completion_display()

    def get_party_named_on_certificate_display(self, hirl_project):
        return hirl_project.registration.get_party_named_on_certificate_display()

    def get_vr_batch_submission_parent_rough_home_address(self, hirl_project):
        if hirl_project and hirl_project.pk and hirl_project.vr_batch_submission_parent_rough:
            home_status = hirl_project.vr_batch_submission_parent_rough.home_status
            return f'<a href="{home_status.get_absolute_url()}">{home_status}</a>'
        return ""

    def get_vr_batch_submission_parent_childrens_rough(self, hirl_project):
        if hirl_project and hirl_project.pk and hirl_project.vr_batch_submission_parent_rough:
            return self.get_vr_batch_submission_rough_childrens(
                hirl_project=hirl_project.vr_batch_submission_parent_rough
            )
        return []

    def get_vr_batch_submission_parent_final_home_address(self, hirl_project):
        if hirl_project and hirl_project.pk and hirl_project.vr_batch_submission_parent_final:
            home_status = hirl_project.vr_batch_submission_parent_final.home_status
            return f'<a href="{home_status.get_absolute_url()}">{home_status}</a>'
        return ""

    def get_vr_batch_submission_parent_childrens_final(self, hirl_project):
        if hirl_project and hirl_project.pk and hirl_project.vr_batch_submission_parent_final:
            return self.get_vr_batch_submission_final_childrens(
                hirl_project=hirl_project.vr_batch_submission_parent_final
            )
        return []

    def get_vr_batch_submission_rough_childrens(self, hirl_project):
        data = []
        if hirl_project and hirl_project.pk:
            childrens = (
                hirl_project.vr_batch_submission_rough_childrens.all()
                .select_related("home_status")
                .order_by("id")
            )
            for children in childrens:
                home_status = children.home_status

                data.append(
                    {
                        "id": children.id,
                        "home_status_id": home_status.id,
                        "home_status_url": home_status.get_absolute_url(),
                        "home_status_address": f'<a href="{home_status.get_absolute_url()}">'
                        f"{home_status}</a>",
                    }
                )

            return data
        return data

    def get_vr_batch_submission_final_childrens(self, hirl_project):
        data = []
        if hirl_project and hirl_project.pk:
            childrens = (
                hirl_project.vr_batch_submission_final_childrens.all()
                .select_related("home_status")
                .order_by("id")
            )
            for children in childrens:
                home_status = children.home_status
                data.append(
                    {
                        "id": children.id,
                        "home_status_id": home_status.id,
                        "home_status_url": home_status.get_absolute_url(),
                        "home_status_address": f'<a href="{home_status.get_absolute_url()}">'
                        f"{home_status}</a>",
                    }
                )

            return data
        return data


class HIRLInvoiceItemGroupSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(source_field="invoicing.InvoiceItemGroup.id", read_only=True)
    invoice = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field="invoicing.Invoice.id"),
        queryset=Invoice.objects.all(),
        allow_null=True,
    )
    invoice_state = serializers.ReadOnlyField(source="invoice.state")
    invoice_number = serializers.ReadOnlyField(source="invoice.invoice_number")
    total = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    current_balance = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItemGroup
        fields = (
            "id",
            "home_status",
            "invoice",
            "created_by",
            "updated_at",
            "created_at",
            # virtual fields
            "invoice_state",
            "invoice_number",
            "total",
            "total_paid",
            "current_balance",
        )
        read_only_fields = ("created_by",)

    def get_total(self, invoice_item_group):
        return getattr(invoice_item_group, "total", 0)

    def get_total_paid(self, invoice_item_group):
        return getattr(invoice_item_group, "total_paid", 0)

    def get_current_balance(self, invoice_item_group):
        return getattr(invoice_item_group, "current_balance", 0)

    def create(self, validated_data):
        request_user = self.context["request"].user
        validated_data["created_by"] = request_user
        return super(HIRLInvoiceItemGroupSerializer, self).create(validated_data)


class HIRLInvoiceItemSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(source_field="invoicing.InvoiceItem.id", read_only=True)
    group = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field="invoicing.InvoiceItemGroup.id"),
        queryset=InvoiceItemGroup.objects.all(),
    )

    class Meta:
        model = InvoiceItem
        fields = ("id", "name", "cost", "group", "created_by")
        read_only_fields = ("created_by",)

    def create(self, validated_data):
        request_user = self.context["request"].user
        validated_data["created_by"] = request_user
        return super(HIRLInvoiceItemSerializer, self).create(validated_data)
