""" Floorplan model serializers """


import json
import logging
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.timezone import now
from rest_framework import serializers
from simulation.models import get_or_import_rem_simulation, get_or_import_ekotrope_simulation
from simulation.serializers.rem.blg import get_blg_simulation_from_floorplan
from simulation.serializers.simulation.base import SimulationSerializer
from simulation.serializers.simulation.examine import FloorplanSimulationReadOnlySerializer

from axis.company.models import Company
from axis.core.utils import make_safe_field
from axis.ekotrope.models import HousePlan
from axis.relationship.utils import (
    create_or_update_spanning_relationships,
    _create_or_update_spanning_relationship_for_obj,
)
from axis.remrate_data.models import InstalledEquipment, PhotoVoltaic
from axis.subdivision.models import Subdivision, FloorplanApproval, THERMOSTAT_CHOICES
from .models import Floorplan

__author__ = "Autumn Valenta"
__date__ = "09-30-14  3:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

User = get_user_model()


class PhotoVoltaicSerializer(serializers.ModelSerializer):
    """Photo voltaic serializer"""

    unicode = serializers.CharField(source="as_string")

    class Meta:
        """Meta options"""

        model = PhotoVoltaic
        fields = ("unicode",)


class EquipmentSerializer(serializers.ModelSerializer):
    """Equipment serializer"""

    system_type_name = make_safe_field(serializers.CharField)(
        source="get_system_type_display", required=False
    )
    quantity = make_safe_field(serializers.CharField)(source="qty_installed", required=False)
    type_name = serializers.SerializerMethodField()
    fuel_type_name = make_safe_field(serializers.CharField)(
        source="equipment.get_fuel_type_display", required=False
    )
    output_capacity = serializers.SerializerMethodField()
    efficiency = serializers.SerializerMethodField()
    efficiency_unit = serializers.SerializerMethodField()
    tank_size = serializers.SerializerMethodField()
    energy_factor = serializers.SerializerMethodField()

    class Meta:
        """Meta options"""

        model = InstalledEquipment
        fields = (
            "system_type_name",
            "quantity",
            "type_name",
            "fuel_type_name",
            "output_capacity",
            "efficiency",
            "efficiency_unit",
            "tank_size",
            "energy_factor",
        )

    def get_type_name(self, obj):
        """Type name"""
        if hasattr(obj.equipment, "get_type_display"):
            return obj.equipment.get_type_display()
        return obj.equipment.name

    def get_output_capacity(self, obj):
        """Output Capacity"""
        if hasattr(obj.equipment, "output_capacity"):
            return obj.equipment.output_capacity
        return None

    def get_efficiency(self, obj):
        """Output Efficiency"""
        if hasattr(obj.equipment, "efficiency"):
            return obj.equipment.efficiency
        return None

    def get_efficiency_unit(self, obj):
        """Efficiency Unit"""
        if hasattr(obj.equipment, "efficiency_unit"):
            return obj.equipment.get_efficiency_unit_display()
        return None

    def get_tank_size(self, obj):
        """Hot Water Tank Size"""
        if hasattr(obj.equipment, "tank_size"):
            return obj.equipment.tank_size
        return None

    def get_energy_factor(self, obj):
        """Energy Factor"""
        if hasattr(obj.equipment, "energy_factor"):
            return obj.equipment.energy_factor
        return None


class ApprovalSerializer(serializers.ModelSerializer):
    """
    Displays Subdivisions for a Floorplan via the FloorplanApproval through-model.
    """

    name = serializers.ReadOnlyField(source="subdivision.name")
    url = serializers.ReadOnlyField(source="subdivision.get_absolute_url")
    community_name = serializers.ReadOnlyField(source="subdivision.community.name")
    community_url = serializers.ReadOnlyField(source="subdivision.community.get_absolute_url")

    class Meta:
        """Meta options"""

        model = FloorplanApproval
        fields = ("name", "url", "community_name", "community_url", "is_approved")


class FloorplanSerializer(serializers.ModelSerializer):
    """Floorplan Serializer"""

    owner = serializers.ReadOnlyField(source="owner_id")
    name = serializers.CharField()

    subdivisions = serializers.SerializerMethodField()

    # Virtual fields
    owner_name = serializers.ReadOnlyField(source="owner.name")
    owner_url = serializers.ReadOnlyField(source="owner.get_absolute_url")

    remrate_target_name = serializers.ReadOnlyField(source="remrate_target.as_string")
    remrate_target_url = serializers.ReadOnlyField(source="remrate_target.get_absolute_url")
    remrate_target_required = serializers.SerializerMethodField()
    remrate_housing_type = serializers.ReadOnlyField(
        source="remrate_target.buildinginfo.get_type_display"
    )
    ekotrope_houseplan_name = serializers.ReadOnlyField(source="ekotrope_houseplan.as_string")
    ekotrope_houseplan_url = serializers.ReadOnlyField(source="ekotrope_houseplan.get_absolute_url")
    ekotrope_project_required = serializers.SerializerMethodField()

    # This is implicitly available when the Examine floorplan allows edit mode, but a readonly
    # machinery won't have that access.  We're publishing it here to streamline that value.
    remrate_data_file_name = serializers.SerializerMethodField()
    remrate_data_file_url = serializers.SerializerMethodField()
    remrate_data_file_required = serializers.SerializerMethodField()

    remrate_data_blg_xml_url = serializers.ReadOnlyField()
    remrate_data_sim_xml_url = serializers.ReadOnlyField()

    # Inputs
    normalized_input_data = serializers.ReadOnlyField(source="get_normalized_input_data")

    # Outputs
    normalized_remrate_result_data = serializers.SerializerMethodField()
    normalized_ekotrope_result_data = serializers.SerializerMethodField()
    normalized_hes_result_data = serializers.SerializerMethodField()
    normalized_open_studio_eri_result_data = serializers.SerializerMethodField()

    # Write-only fields - Helper field for "add existing" workflow
    existing_floorplan = serializers.IntegerField(required=False, write_only=True)
    ekotrope_houseplan = serializers.PrimaryKeyRelatedField(
        queryset=HousePlan.objects.all(), required=False, allow_null=True, write_only=True
    )

    companies = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), required=False, write_only=True, many=True
    )
    subdivision = serializers.PrimaryKeyRelatedField(
        queryset=Subdivision.objects.all(), required=False, write_only=True
    )

    simulation = FloorplanSimulationReadOnlySerializer(read_only=True)

    class Meta:
        """Meta options"""

        model = Floorplan
        fields = (
            "owner",
            "remrate_target",
            "remrate_data_file",
            "ekotrope_houseplan",
            "name",
            "number",
            "square_footage",
            "comment",
            "subdivisions",
            "simulation",
            # Hidden
            "id",
            # Virtual fields
            "existing_floorplan",
            "remrate_data_file_name",
            "remrate_data_file_url",
            "remrate_target_name",
            "remrate_target_url",
            "owner_name",
            "owner_url",
            "companies",
            "subdivision",
            "remrate_data_file_required",
            "remrate_housing_type",
            "ekotrope_houseplan_url",
            "ekotrope_houseplan_name",
            "remrate_target_required",
            "ekotrope_project_required",
            "remrate_data_blg_xml_url",
            "remrate_data_sim_xml_url",
            # Input data
            "normalized_input_data",
            # Output
            "normalized_ekotrope_result_data",
            "normalized_remrate_result_data",
            "normalized_hes_result_data",
            "normalized_open_studio_eri_result_data",
        )

        read_only_fields = (
            "id",
            "modified_date",
            "slug",
            "remrate_data_file",
            "remrate_data_blg_xml_url",
            "remrate_data_sim_xml_url",
        )

    def __init__(self, instance=None, **kwargs):
        from rest_framework.fields import empty

        self.object_overridden = False
        data = kwargs.pop("data", empty)
        if data is not empty and data.get("existing_floorplan"):
            self.object_overridden = True
            floorplan_id = data.get("existing_floorplan")
            try:
                floorplan = kwargs["context"]["view"].get_queryset().get(id=floorplan_id)
            except (Floorplan.DoesNotExist, ValueError):
                pass
            else:
                instance = floorplan
            data = FloorplanSerializer(instance=instance, **kwargs).data

        super(FloorplanSerializer, self).__init__(instance, data=data, **kwargs)

    def get_subdivisions(self, obj: Floorplan):
        if obj.pk:
            serializer = ApprovalSerializer(
                instance=obj.floorplanapproval_set.all(), many=True, read_only=True
            )
            return serializer.data
        return []

    def get_remrate_data_file_name(self, obj: Floorplan):
        """Get the REM/Rat Blg file name"""
        if obj.remrate_data_file:
            return obj.remrate_data_filename()
        return None

    def get_remrate_data_file_url(self, obj: Floorplan):
        if obj.remrate_data_file:
            return obj.remrate_data_file.url
        return None

    def _get_input_data_required(self, obj: Floorplan):
        """Input Required?"""
        return any(obj.homestatuses.values_list("eep_program__require_input_data", flat=True))

    def get_remrate_target_required(self, obj: Floorplan):
        """RemRate target required"""
        if not obj.id:
            return False
        return any(obj.homestatuses.values_list("eep_program__require_rem_data", flat=True))

    def get_remrate_data_file_required(self, obj: Floorplan):
        """RemRate BLG required"""
        if not obj.id:
            return False
        return any(obj.homestatuses.values_list("eep_program__require_model_file", flat=True))

    def get_ekotrope_project_required(self, obj: Floorplan):
        """Ekotrope required"""
        if not obj.id:
            return False
        return any(obj.homestatuses.values_list("eep_program__require_ekotrope_data", flat=True))

    def get_normalized_remrate_result_data(self, obj: Floorplan):
        return obj.get_normalized_remrate_result_data()

    def get_normalized_ekotrope_result_data(self, obj: Floorplan):
        return obj.get_normalized_ekotrope_result_data()

    # TODO: Remove this function and related functionality that is not in use any longer
    def normalized_hes_result_data(self, obj: Floorplan):
        return obj.normalized_hes_result_data()

    def get_normalized_open_studio_eri_result_data(self, obj: Floorplan) -> dict:
        return obj.normalized_open_studio_eri_result_data()

    def _handle_relationships(self, obj, requesting_company, validated_data_companies):
        """Update relationships"""
        from axis.relationship.models import Relationship

        # Old relationships were purged during possible call to update()

        Relationship.objects.validate_or_create_relations_to_entity(
            entity=obj,
            direct_relation=requesting_company,
            implied_relations=validated_data_companies,
        )

        companies = [requesting_company] + [x for x in validated_data_companies]
        create_or_update_spanning_relationships(companies, obj)

    def update(self, instance, validated_data):
        instance = super(FloorplanSerializer, self).update(instance, validated_data)

        # Remove old relationships
        for relationship in instance.relationships.all():
            is_friend = relationship.company in self._companies
            if relationship.company == instance.owner or is_friend:
                continue
            relationship.delete()

        return instance

    def save(self, *args, **kwargs):
        home_status = kwargs.pop("home_status")
        self._companies = self.validated_data.pop("companies", [])
        subdivision = self.validated_data.pop("subdivision", None)

        user = self.context["request"].user
        company = self.context["request"].company

        instance = super(FloorplanSerializer, self).save(*args, **kwargs)

        # Handle special write-only fields
        if subdivision:
            if home_status:
                _val = home_status.eep_program.requires_manual_floorplan_approval(company)
                manual_approval = _val
            else:
                manual_approval = company.guess_manual_floorplan_approval_requirement(subdivision)
            instance.floorplanapproval_set.exclude(subdivision=subdivision).delete()
            instance.floorplanapproval_set.get_or_create(
                subdivision=subdivision,
                defaults={
                    "is_approved": (not manual_approval),
                    "approved_by": user,
                },
            )

        self._handle_relationships(instance, company, self._companies)

        if subdivision is None:
            self.Meta.model.objects.filter(id=instance.id).update(is_custom_home=True)
            instance.refresh_from_db()

        if home_status:
            home_status_rels = home_status.home.relationships.values_list(
                "company__slug", flat=True
            )
            owner_rels = instance.owner.relationships.get_companies().values_list("slug", flat=True)
            slugs = list(set(home_status_rels).intersection(set(owner_rels)))
            companies = Company.objects.filter(slug__in=slugs + [instance.owner.slug])
            _create_or_update_spanning_relationship_for_obj(companies, instance, skip_implied=True)
        return instance

    def validate_simulation_data(self, **kwargs):
        """Validate our simulation to REM / EKO Data"""

        simulation = kwargs.get("simulation")
        remrate_target = kwargs.get("remrate_target")
        ekotrope_houseplan = kwargs.get("ekotrope_houseplan")

        if simulation:
            log.debug("Have Sim")
            if remrate_target and not remrate_target.simulation_seeds.exists():
                simulation = kwargs["simulation"] = None
            elif ekotrope_houseplan and not ekotrope_houseplan.project.simulation_seeds.exists():
                simulation = kwargs["simulation"] = None
        if simulation is None:
            if remrate_target:
                log.debug("No Sim REM")
                if remrate_target.simulation_seeds.exists():
                    log.debug("Assigning Sim REM")
                    try:
                        simulation = remrate_target.simulation_seeds.last().simulation
                        kwargs["simulation"] = simulation
                    except ObjectDoesNotExist:
                        log.debug("REM Still processing")
                else:
                    log.debug("REM Convert")
                    simulation = get_or_import_rem_simulation(remrate_target.id, use_tasks=False)
                    if simulation is None:
                        log.error("Unable to convert REM %s" % remrate_target.id)
                    kwargs["simulation"] = simulation
            elif ekotrope_houseplan:
                log.debug("No Sim EKO")
                project = ekotrope_houseplan.project
                if project.simulation_seeds.exists():
                    log.debug("Assigning Sim ELP")
                    try:
                        simulation = project.simulation_seeds.last().simulation
                        kwargs["simulation"] = simulation
                    except ObjectDoesNotExist:
                        log.debug("Still processing")
                else:
                    log.debug("EKO Convert")
                    simulation = get_or_import_ekotrope_simulation(
                        project_id=project.id, use_tasks=False
                    )
                    kwargs["simulation"] = simulation
        return kwargs

    def validate(self, data):
        """Validate"""
        cleaned_data = super(FloorplanSerializer, self).validate(data)

        cleaned_data = self.validate_simulation_data(**cleaned_data)

        # When a floorplan is 'copied' directly from an existing program, we can take it as-is.
        # Note that update logic after this will no longer contain an 'existing_id' request, so
        # validations will resume after this request.
        if self.object_overridden:
            return cleaned_data

        existing_floorplans = Floorplan.objects.filter_for_uniqueness(
            name=cleaned_data["name"],
            owner=cleaned_data.get("owner"),
            remrate_target=cleaned_data.get("remrate_target"),
            ekotrope_houseplan=cleaned_data.get("ekotrope_houseplan"),
            simulation=cleaned_data.get("simulation"),
            id=cleaned_data.get("id", self.initial_data.get("id")),
        )
        if existing_floorplans.exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        f"Floorplan with name '{cleaned_data['name']}' already exists."
                    ]
                }
            )

        if self.instance and self.instance.is_restricted:
            errors = []
            for key in ["name", "number", "remrate_target", "simulation", "ekotrope_houseplan"]:
                if self.initial_data.get(key) != cleaned_data.get(key):
                    errors.append(key)
            if errors:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            f"Floorplan is restricted - unable to edit fields {', '.join(errors)}"
                        ]
                    }
                )

        return cleaned_data

    def _get_user(self) -> User | None:
        if "request" in self.context:
            return self.context["request"].user
        return None


class FloorplanRemrateSerializer(serializers.ModelSerializer):
    """Floorplan REM/Rate Serializer"""

    remrate_target_name = make_safe_field(serializers.ReadOnlyField)(
        source="remrate_target.as_string"
    )
    remrate_target_url = make_safe_field(serializers.ReadOnlyField)(
        source="remrate_target.get_absolute_url"
    )

    remrate_data_file_name = make_safe_field(serializers.ReadOnlyField)(
        source="remrate_data_filename"
    )
    remrate_data_file_url = make_safe_field(serializers.ReadOnlyField)(
        source="remrate_data_file.url"
    )

    remrate_data_blg_xml_url = make_safe_field(serializers.ReadOnlyField)
    remrate_data_sim_xml_url = make_safe_field(serializers.ReadOnlyField)

    blg_data = make_safe_field(serializers.SerializerMethodField)()

    simulation = FloorplanSimulationReadOnlySerializer(read_only=True)

    class Meta:
        model = Floorplan
        fields = (
            "id",
            "remrate_data_file",
            "remrate_data_file_name",
            "remrate_data_file_url",
            "remrate_target",
            "remrate_target_name",
            "remrate_target_url",
            "blg_data",
            "remrate_data_blg_xml_url",
            "remrate_data_sim_xml_url",
            "simulation",
        )
        read_only_fields = (
            "id",
            "remrate_target_name",
            "remrate_target_url",
            "remrate_data_file",
            "remrate_data_file_name",
            "remrate_data_file_url",
            "blg_data",
            "remrate_data_blg_xml_url",
            "remrate_data_sim_xml_url",
            "simulation",
        )

    def get_blg_data(self, obj):
        """Get the BLG FIle and data"""
        if obj.id:
            try:
                blg_instance = get_blg_simulation_from_floorplan(obj)
                simulation_serializer = SimulationSerializer(instance=blg_instance)
                return simulation_serializer.data
            except (ValidationError, ValueError, IOError, OSError) as err:
                return {"error": f"Associated Floorplan or BLG File does not exist - {err}"}
        return None


class FloorplanEkotropeSerializer(serializers.ModelSerializer):
    """Floorplan Ekotrope Serializer"""

    ekotrope_houseplan_name = make_safe_field(serializers.ReadOnlyField)(
        source="ekotrope_houseplan.as_string"
    )
    ekotrope_houseplan_url = make_safe_field(serializers.ReadOnlyField)(
        source="ekotrope_houseplan.get_absolute_url"
    )
    ekotrope_houseplan_data = serializers.SerializerMethodField()

    data = serializers.SerializerMethodField()
    import_failed = make_safe_field(serializers.ReadOnlyField)(
        source="ekotrope_houseplan.project.import_failed"
    )
    import_error = make_safe_field(serializers.ReadOnlyField)(
        source="ekotrope_houseplan.project.import_error"
    )

    simulation = FloorplanSimulationReadOnlySerializer(read_only=True)

    class Meta:
        """Meta options"""

        model = Floorplan
        fields = (
            "id",
            "ekotrope_houseplan",
            "ekotrope_houseplan_name",
            "ekotrope_houseplan_url",
            "ekotrope_houseplan_data",
            "data",
            "import_failed",
            "import_error",
            "simulation",
        )

    def get_data(self, obj):
        """Get the data"""
        if obj.id and obj.ekotrope_houseplan:
            return obj.ekotrope_houseplan.project.data
        return None

    def get_ekotrope_houseplan_data(self, obj):
        """Get the houseplan data"""
        if obj.id and obj.ekotrope_houseplan:
            return obj.ekotrope_houseplan.data
        return None


class FloorplanApprovalSerializer(serializers.ModelSerializer):
    """Floorplan approval - for APS to approve floorplans."""

    # This field is split into two parts because DRF can't handle a writeable field that gets its
    # original value from a serializer method.
    is_active = serializers.BooleanField(
        label="Is Active", source="get_approved_status.is_approved", read_only=True
    )
    thermostat_num = serializers.IntegerField(
        label="Thermostat Qty", source="get_approved_status.thermostat_qty", read_only=True
    )

    thermostat_qty = serializers.ChoiceField(choices=THERMOSTAT_CHOICES, write_only=True)
    is_approved = serializers.BooleanField(write_only=True)

    approved_by = serializers.CharField(source="get_approved_status.user_name", read_only=True)
    approved_date = serializers.DateField(
        source="get_approved_status.date_modified", read_only=True
    )

    class Meta:
        """Meta options"""

        model = Floorplan
        fields = (
            "id",
            "is_active",
            "is_approved",
            "approved_by",
            "approved_date",
            "thermostat_num",
            "thermostat_qty",
        )

    def validate(self, attrs):
        attrs.setdefault("is_approved", False)
        attrs.setdefault("thermostat_qty", 0)
        return attrs

    def update(self, instance, validated_data):
        """Update our data"""
        request = self.context["request"]

        user = request.user
        is_approval_entity = request.company.is_floorplan_approval_entity()

        if is_approval_entity or user.is_superuser:
            # Updates affect all approvals on this object due to UI constraints
            if not instance.floorplanapproval_set.exists():
                instance.floorplanapproval_set.create(
                    subdivision=self.instance.subdivision, approved_by=user, **validated_data
                )
            else:
                instance.floorplanapproval_set.update(
                    date_modified=now(),  # Update date in a bulk operation
                    approved_by=user,
                    **validated_data,
                )

        return instance
