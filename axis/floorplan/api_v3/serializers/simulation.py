"""serializers.py: """

__author__ = "Artem Hruzd"
__date__ = "08/27/2020 22:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.core.api_v3.serializers import UserInfoSerializer
from rest_framework import serializers
from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.geographic.api_v3.serializers import USStateSerializer, CitySerializer, CountySerializer
from axis.subdivision.api_v3.serializers import SubdivisionInfoSerializer

from simulation.enumerations import (
    AnalysisStatus,
    ERICalculationChoices,
    IECCCalculationChoices,
    ESTARCalculationChoices,
    ZERHCalculationChoices,
    DistributionSystemType,
)
from simulation.models import Project, Simulation
from simulation.enumerations import Location
from simulation.models.project import RaterUser


class RaterUserInfoSerializer(serializers.ModelSerializer):
    """
    Simulation Rater user info
    """

    user_info = UserInfoSerializer(source="user")

    class Meta:
        model = RaterUser
        fields = ("id", "user", "user_info", "rater_name", "rater_identification", "source_extra")
        read_only_fields = ("id", "created_date", "modified_date")


class SimulationProjectInfoSerializer(serializers.ModelSerializer):
    """
    Adopted detail serializer for AXIS
    """

    builder_info = CompanyInfoSerializer(source="builder", read_only=True)
    rater_organization_info = CompanyInfoSerializer(source="rater_organization", read_only=True)
    provider_organization_info = CompanyInfoSerializer(
        source="provider_organization", read_only=True
    )
    rater_of_record_info = RaterUserInfoSerializer(source="rater_of_record", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "model_name",
            "builder_name",
            "builder",
            "builder_info",
            "rater_organization_name",
            "rater_organization",
            "rater_organization_info",
            "rater_of_record",
            "rater_of_record_info",
            "provider_identification",
            "provider_organization",
            "provider_organization_info",
            "permit_identification",
            "permit_date",
            "construction_year",
            "rating_type",
            "sampleset_identification",
            "resnet_registry_identification",
            "resnet_registry_datetime",
            "eto_reference_home_type",
            "note",
            "source_extra",
        )
        read_only_fields = ("id", "created_date", "modified_date")


class LocationInfoSerializer(serializers.ModelSerializer):
    """
    Adopted detail serializer for AXIS
    """

    us_state_info = USStateSerializer(source="us_state")
    city_info = CitySerializer(source="city")
    county_info = CountySerializer(source="county")
    subdivision_info = SubdivisionInfoSerializer(source="subdivision")

    class Meta:
        model = Location
        fields = (
            "id",
            "lot_number",
            "street_line1",
            "street_line2",
            "zipcode",
            "is_multi_family",
            "city_name",
            "city",
            "city_info",
            "county_name",
            "county",
            "county_info",
            "us_state",
            "us_state_info",
            "weather_station",
            "subdivision_name",
            "subdivision",
            "subdivision_info",
            "elevation",
            "source_extra",
        )
        read_only_fields = ("id", "created_date", "modified_date")


class SimulationSerializer(serializers.ModelSerializer):
    """
    Adopted detail serializer for AXIS. Do not recommend it to use in list view, because of a lot of
    relation fields
    """

    company_info = CompanyInfoSerializer(source="company", read_only=True)
    project_info = SimulationProjectInfoSerializer(source="project", read_only=True)
    # location_info = LocationInfoSerializer(source="location", read_only=True)

    class Meta:
        model = Simulation
        fields = (
            "id",
            "source_type",
            "status",
            "company",
            "company_info",
            "version",
            "internal_version",
            "flavor",
            "name",
            "residence_type",
            "bedroom_count",
            "floors_on_or_above_grade",
            "conditioned_area",
            "conditioned_volume",
            "unit_count",
            "foundation_type",
            "crawl_space_type",
            "project",
            "project_info",
            "location",
            # "location_info",
        )
        read_only_fields = ("id", "created_date", "modified_date")


class SimulationListSerializer(serializers.ModelSerializer):
    """
    Special flattened serializer for list viewset
    """

    company__name = serializers.CharField(source="company.name", read_only=True)
    company__type = serializers.CharField(source="company.company_type", read_only=True)
    project__builder = serializers.CharField(source="project.builder", read_only=True)
    project__builder__name = serializers.CharField(source="project.builder.name", read_only=True)
    location__street_line1 = serializers.CharField(source="location.street_line1", read_only=True)
    location__street_line2 = serializers.CharField(source="location.street_line2", read_only=True)
    location__city__name = serializers.CharField(source="location.city.name", read_only=True)
    location__county__name = serializers.CharField(source="location.county.name", read_only=True)
    location__zipcode = serializers.CharField(source="location.zipcode", read_only=True)

    class Meta:
        model = Simulation
        fields = (
            "id",
            "source_type",
            "status",
            "company",
            "company__name",
            "company__type",
            "name",
            "bedroom_count",
            "project__builder",
            "project__builder__name",
            "location__street_line1",
            "location__street_line2",
            "location__city__name",
            "location__county__name",
            "location__zipcode",
            "modified_date",
            "created_date",
        )
        read_only_fields = ("id", "created_date", "modified_date")


class SimulationVersionsSerializer(serializers.Serializer):
    versions = serializers.ListField()


class SimulationFlatSerializer(serializers.ModelSerializer):
    """Limited fields to be used by Floorplan API"""

    source_type_display = serializers.CharField(source="get_source_type_display", read_only=True)

    class Meta:
        model = Simulation
        fields = (
            "id",
            "name",
            "source_type",
            "source_type_display",
            "version",
            "status",
        )


class SimulationHomeBuildingParameterSerializer(serializers.ModelSerializer):
    """This is used to seed the creation of a home from a simulation dataset"""

    class Meta:
        model = Simulation

    def to_representation(self, instance: Simulation) -> dict:
        rater_of_record = (
            instance.project.rater_of_record.user
            if instance.project.rater_of_record and instance.project.rater_of_record.user
            else None
        )

        rater = instance.company if instance.company.company_type == "rater" else None
        if rater is None:
            rater = (
                instance.project.rater_organization if instance.project.rater_organization else None
            )

        provider = instance.company if instance.company.company_type == "provider" else None
        if provider is None:
            provider = (
                instance.project.provider_organization
                if instance.project.provider_organization
                else None
            )

        return {
            "home": {
                "is_multi_family": instance.location.is_multi_family,
                "street_line1": instance.location.street_line1,
                "street_line2": instance.location.street_line2,
                "city_name": instance.location.city_name,
                "city": instance.location.city.pk if instance.location.city else None,
                "state": instance.location.us_state.abbr if instance.location.us_state else None,
                "zipcode": instance.location.zipcode,
                "subdivision": instance.location.subdivision.pk
                if instance.location.subdivision
                else None,
                "subdivision_name": instance.location.subdivision_name,
            },
            "home_relationships": {
                "builder": instance.project.builder.pk if instance.project.builder else None,
                "builder_name": str(instance.project.builder)
                if instance.project.builder
                else instance.project.builder_name,
                "rater": rater.id if rater else None,
                "rater_name": str(rater) if rater else instance.project.rater_organization_name,
                "provider": provider.id if provider else None,
                "provider_name": str(provider) if provider else None,
            },
            "home_status": {
                "rater_of_record": rater_of_record.pk if rater_of_record else None,
                "rater_of_record_name": rater_of_record.get_full_name()
                if rater_of_record
                else None,
            },
            "floorplan": {
                "name": instance.name,
                "square_footage": instance.conditioned_area,
                "number": instance.floorplan.number
                if instance.floorplan
                else instance.project.source_extra.get("rating_number"),
                "pk": instance.floorplan.pk if instance.floorplan else None,
                "simulation": instance.floorplan.simulation.id
                if instance.floorplan and instance.floorplan.simulation
                else None,
            },
        }


class SimulationOSERIAnalysisTypeSerializer(serializers.Serializer):
    ERICalculation = serializers.ChoiceField(
        choices=ERICalculationChoices.choices,
        default="2019AB",
        help_text="ERI Calculation Version",
        required=False,
    )

    IECCERICalculation = serializers.ChoiceField(
        choices=IECCCalculationChoices.choices,
        help_text="IECC Calculation Version",
        required=False,
    )

    EnergyStarCalculation = serializers.ChoiceField(
        choices=ESTARCalculationChoices.choices,
        help_text="ENERGY STAR Calculation Version",
        required=False,
    )
    ZERHCalculation = serializers.ChoiceField(
        choices=ZERHCalculationChoices.choices,
        help_text="ZERH Calculation Version",
        required=False,
    )


class SimulationTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="Simulation ID")
    analysis_ids = serializers.ListSerializer(
        child=serializers.IntegerField(), help_text="Analysis IDS"
    )
    status = serializers.ChoiceField(help_text="Simulation Status", choices=AnalysisStatus.choices)
    task_id = serializers.UUIDField(help_text="Task ID")


class NormalizedSimulationInputSerializer(serializers.ModelSerializer):
    """This is a legacy thing - it's used in the old Django templates and is simply used for the CBV's"""

    conditioned_area = serializers.IntegerField(source="imperial_conditioned_area")
    conditioned_volume = serializers.IntegerField(source="imperial_conditioned_volume")
    shell_area = serializers.SerializerMethodField()
    housing_type = serializers.CharField(source="get_residence_type_display")
    num_bedrooms = serializers.IntegerField(source="bedroom_count")
    num_stories = serializers.IntegerField(source="floors_on_or_above_grade")
    foundation_type = serializers.CharField(source="get_foundation_type_display")
    infiltration = serializers.FloatField(source="infiltration.get_ach50_infiltration_value")
    ceilings = serializers.SerializerMethodField()
    above_grade_wall = serializers.SerializerMethodField()
    floor = serializers.SerializerMethodField()
    windows = serializers.SerializerMethodField()
    total_duct_leakage = serializers.SerializerMethodField()
    duct_inside_percent = serializers.SerializerMethodField()
    installed_equipment = serializers.SerializerMethodField()
    ventilation = serializers.SerializerMethodField()
    solar = serializers.SerializerMethodField()
    dominant_equipment = serializers.SerializerMethodField()

    class Meta:
        """Meta options"""

        model = Simulation
        fields = (
            "conditioned_area",
            "conditioned_volume",
            "shell_area",
            "housing_type",
            "num_bedrooms",
            "num_stories",
            "foundation_type",
            "infiltration",
            "ceilings",
            "above_grade_wall",
            "floor",
            "windows",
            "total_duct_leakage",
            "duct_inside_percent",
            "installed_equipment",
            "ventilation",
            "solar",
            "dominant_equipment",
        )

    def get_shell_area(self, instance: Simulation) -> str | None:
        return ""

    def get_ceilings(self, instance: Simulation) -> dict:
        vaulted = instance.roofs.filter(interior_location=Location.VAULTED_ROOF)
        vaulted = [{"r_value": r.assembly_r_value} for r in vaulted]

        attic = instance.roofs.filter(
            interior_location__in=[Location.SEALED_ATTIC, Location.VENTED_ATTIC]
        )
        attic = [{"r_value": round(r.assembly_r_value, 2)} for r in attic]

        return {
            "vaulted": vaulted if vaulted else None,
            "attic": attic if attic else None,
        }

    def get_above_grade_wall(self, instance: Simulation) -> dict:
        return {"r_value": instance.above_grade_walls.all().get_dominant_wall_r_value()}

    def get_floor(self, instance: Simulation) -> dict:
        return {"r_value": instance.frame_floors.all().dominant_r_value}

    def get_windows(self, instance: Simulation) -> list:
        return [{"u_value": w.type.u_value} for w in instance.windows.all()]

    def get_total_duct_leakage(self, instance: Simulation) -> float | None:
        inst = instance.hvac_distribution_systems.filter(
            system_type=DistributionSystemType.FORCED_AIR
        ).first()
        return inst.total_leakage if inst else None

    def get_duct_inside_percent(self, instance: Simulation) -> float:
        return instance.hvac_distribution_systems.all().get_percent_ducts_in_conditioned_space()

    def get_installed_equipment(self, instance: Simulation) -> list:
        return [x.get_basic_type_display() for x in instance.mechanical_equipment.all()]

    def get_ventilation(self, instance: Simulation) -> str | None:
        return (
            str(instance.mechanical_ventilation_systems.first())
            if instance.mechanical_ventilation_systems
            else None
        )

    def get_solar(self, instance: Simulation) -> list | None:
        pv = instance.photovoltaics.all()
        return [str(p) for p in pv] if pv else None

    def get_dominant_equipment(self, instance: Simulation) -> dict:
        dominant_heating = instance.dominant_heating_equipment

        heating_capacity = None
        heating_efficiency = None
        heating_efficiency_unit = None
        heating_efficiency_unit_display = None
        if dominant_heating:
            if dominant_heating.heater:
                heating_capacity = dominant_heating.equipment.capacity
                heating_efficiency = dominant_heating.equipment.efficiency
                heating_efficiency_unit = dominant_heating.equipment.efficiency_unit
                heating_efficiency_unit_display = (
                    dominant_heating.equipment.get_efficiency_unit_display()
                )
            else:
                heating_capacity = dominant_heating.equipment.heating_capacity
                heating_efficiency = dominant_heating.equipment.heating_efficiency
                heating_efficiency_unit = dominant_heating.equipment.heating_efficiency_unit
                heating_efficiency_unit_display = (
                    dominant_heating.equipment.get_heating_efficiency_unit_display()
                )

        dominant_cooling = instance.dominant_cooling_equipment
        cooling_capacity = None
        cooling_efficiency = None
        cooling_efficiency_unit = None
        cooling_efficiency_unit_display = None
        if dominant_cooling:
            if dominant_cooling.air_conditioner:
                cooling_capacity = dominant_cooling.equipment.capacity
                cooling_efficiency = dominant_cooling.equipment.efficiency
                cooling_efficiency_unit = dominant_cooling.equipment.efficiency_unit
                cooling_efficiency_unit_display = (
                    dominant_cooling.equipment.get_efficiency_unit_display()
                )
            else:
                cooling_capacity = dominant_cooling.equipment.cooling_capacity
                cooling_efficiency = dominant_cooling.equipment.cooling_efficiency
                cooling_efficiency_unit = dominant_cooling.equipment.cooling_efficiency_unit
                cooling_efficiency_unit_display = (
                    dominant_cooling.equipment.get_cooling_efficiency_unit_display()
                )

        dominant_hot_water = instance.dominant_water_heating_equipment

        return {
            "dominant_heating": {
                "type_name_pretty": "Primary Heating",
                "load_served": 0
                if not dominant_heating
                else dominant_heating.heating_percent_served,
                "units": heating_efficiency_unit,
                "units_pretty": heating_efficiency_unit_display,
                "efficiency": heating_efficiency,
                "location": None
                if not dominant_heating
                else dominant_heating.get_location_display(),
                "qty": 0 if not dominant_heating else dominant_heating.qty_installed,
                "type": None if not dominant_heating else dominant_heating.system_type,
                "fuel": None
                if not dominant_heating
                else dominant_heating.equipment.get_fuel_display(),
                "capacity": heating_capacity,
                "capacity_units": None
                if not dominant_heating
                else dominant_heating.equipment.get_capacity_unit_display(),
                "backup_capacity": None,
                "backup_capacity_units": None,
            },
            "dominant_cooling": {
                "type_name_pretty": "Primary Cooling",
                "load_served": 0
                if not dominant_cooling
                else dominant_cooling.cooling_percent_served,
                "units": cooling_efficiency_unit,
                "units_pretty": cooling_efficiency_unit_display,
                "efficiency": cooling_efficiency,
                "location": None
                if not dominant_cooling
                else dominant_cooling.get_location_display(),
                "qty": 0 if not dominant_cooling else dominant_cooling.qty_installed,
                "type": None if not dominant_cooling else dominant_cooling.system_type,
                "fuel": None
                if not dominant_cooling
                else dominant_cooling.equipment.get_fuel_display(),
                "capacity": cooling_capacity,
                "capacity_units": None
                if not dominant_cooling
                else dominant_cooling.equipment.get_capacity_unit_display(),
            },
            "dominant_hot_water": {
                "type_name_pretty": "Primary Water Heating",
                "load_served": 0
                if not dominant_hot_water
                else dominant_hot_water.water_heater_percent_served,
                "tank_size": None
                if not dominant_hot_water
                else dominant_hot_water.equipment.imperial_tank_size,
                "location": None
                if not dominant_hot_water
                else dominant_hot_water.get_location_display(),
                "energy_factor": None
                if not dominant_hot_water
                else dominant_hot_water.equipment.efficiency,
                "qty": 0 if not dominant_hot_water else dominant_hot_water.qty_installed,
                "type": None
                if not dominant_hot_water
                else dominant_hot_water.equipment.get_style_display(),
                "fuel": None
                if not dominant_hot_water
                else dominant_hot_water.equipment.get_fuel_display(),
            },
        }
