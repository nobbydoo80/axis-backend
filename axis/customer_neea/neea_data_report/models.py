"""NGBS Certification and Candidate tracking for pairing to home.Home instances."""

import logging

from django.db import models
from django.urls import reverse

from axis.home.disambiguation.models import BaseCertification

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Candidate(models.Model):
    """ForeignKey link between Certification and a possible matching Home."""

    certification = models.ForeignKey("NEEACertification", on_delete=models.CASCADE)
    home = models.ForeignKey(
        "home.Home", related_name="%(app_label)s_candidates", on_delete=models.CASCADE
    )

    levenshtein_distance = models.PositiveIntegerField()
    profile_delta = models.IntegerField()

    class Meta:
        pass

    def __str__(self):
        return "Candidate: %r" % (
            "{}".format(
                self.home,
            )
        )


class NEEACertification(BaseCertification):
    """Model of csv data coming from a NEEA Data Report.
    The field names are normalized for snake_case, mapped via the `CertificationForm`.
    """

    PROGRAM_NAME = "RESNET Registry Data"
    PROGRAM_NAMES = {
        "RESNET Registry Data": "RESNET Registry Data",
    }

    FIELDS = {
        "RegistryID": "registry_id",
        "StreetAddress": "street_line1",
        "City": "city",
        "State": "state_abbreviation",
        "Zip": "zipcode",
        "DateRegistered": "certification_date",
        "DateRated": "certification_date",
        "HomeType": "home_type",
        "Software": "software",
        "SoftwareVersion": "software_version",
        "ConstructionYear": "construction_year",
        "ConditionedArea": "conditioned_area",
        "ConditionedVolume": "conditioned_volume",
        "ConditionedFloors": "conditioned_floors",
        "NumberBedrooms": "number_bedrooms",
        "HERSIndex": "hers_index",
        "RegistrationType": "registration_type",
        "TotalEnergyUse": "total_energy_use",
        "TotalEnergyCost": "total_energy_cost",
        "NumCoolingSystems": "num_cooling_systems",
        "NumHeatingSystems": "num_heating_systems",
        "CoolingEnergyUse": "cooling_energy_use",
        "CostCooling": "cost_cooling",
        "CoolingRatedOutput": "cooling_rated_output",
        "HeatingRatedOutput": "heating_rated_output",
        "NumHotWaterSystems": "num_hot_water_systems",
        "HotWaterEnergyUse": "hot_water_energy_use",
        "CostHotWater": "cost_hot_water",
        "LightingAppEnergyUse": "lighting_app_energy_use",
        "CostLighting": "cost_lighting",
        "On-site Generation": "on_site_generation",
        "OPP Net": "opp_net",
        "Purchased Energy Fraction": "purchased_energy_fraction",
        "AnnualElectricity": "annual_electricity",
        "AnnualGas": "annual_gas",
        "FoundationType": "foundation_type",
        "FoundationRigidInsulation": "foundation_rigid_insulation",
        "FoundationBattInsulation": "foundation_batt_insulation",
        "FoundationInsulationGrade": "foundation_insulation_grade",
        "FloorContinuousInsulation": "floor_continuous_insulation",
        "FloorCavityInsulation": "floor_cavity_insulation",
        "AGWWallConstructionType": "agw_wall_construction_type",
        "AGWallFramingFactor": "ag_wall_framing_factor",
        "AGWallContinuousInsulation": "ag_wall_continuous_insulation",
        "AGWallCavityInsulation": "ag_wall_cavity_insulation",
        "AGWallInsulationGrade": "ag_wall_insulation_grade",
        "AGWallInsulationType": "ag_wall_insulation_type",
        "CeilingInsulationDepth": "ceiling_insulation_depth",
        "CeilingCavityInsulation": "ceiling_cavity_insulation",
        "CeilingContinuousInsulation": "ceiling_continuous_insulation",
        "CeilingInsulationType": "ceiling_insulation_type",
        "RadiantBarrier": "radiant_barrier",
        "WindowUFactor": "window_u_factor",
        "WindowSHGC": "window_shgc",
        "ACH50": "ach50",
        "VentilationType": "ventilation_type",
        "VentilationRate": "ventilation_rate",
        "VentilationRunTime": "ventilation_run_time",
        "VentilationFanWattage": "ventilation_fan_wattage",
        "DuctLeakage": "duct_leakage",
        "DuctLeakageTotal": "duct_leakage_total",
        "DuctLeakageTightnessTest": "duct_leakage_tightness_test",
        "DuctLeakageUnits": "duct_leakage_units",
        "HighEfficiencyLightsPercent": "high_efficiency_lights_percent",
        "ACEfficiency": "ac_efficiency",
        "ACOutputCapacity": "ac_output_capacity",
        "HeatingSystemType": "heating_system_type",
        "HeatingEfficiency": "heating_efficiency",
        "HeatingEfficiencyUnits": "heating_efficiency_units",
        "FurnaceOutputCapacity": "furnace_output_capacity",
        "FurnaceFuel": "furnace_fuel",
        "WaterHeaterType": "water_heater_type",
        "WaterHeaterFuel": "water_heater_fuel",
        "WaterHeaterCapacity": "water_heater_capacity",
        "AGWallUo": "ag_wall_uo",
        "FoundationWallUo": "foundation_wall_uo",
        "CeilingUo": "ceiling_uo",
        "OverallEnclosureUA": "overall_enclosure_ua",
        "DuctsConditioned": "ducts_conditioned",
        "DishwasherKWhyr": "dishwasher_k_whyr",
        "RefrigeratorKWh": "refrigerator_k_wh",
        "DryerEnergyFactor": "dryer_energy_factor",
        "DryerEnergyFactorGas": "dryer_energy_factor_gas",
        "WasherLER": "washer_ler",
        "isZERH": "is_zerh",
        "EnergyStarVersion": "energy_star_version",
    }

    ANNOTATIONS = [
        "registry_id",
        "home_type",
        "software",
        "software_version",
        "construction_year",
        "conditioned_area",
        "conditioned_volume",
        "conditioned_floors",
        "number_bedrooms",
        "hers_index",
        "registration_type",
        "total_energy_use",
        "total_energy_cost",
        "num_cooling_systems",
        "num_heating_systems",
        "cooling_energy_use",
        "cost_cooling",
        "cooling_rated_output",
        "heating_rated_output",
        "num_hot_water_systems",
        "hot_water_energy_use",
        "cost_hot_water",
        "lighting_app_energy_use",
        "cost_lighting",
        "on_site_generation",
        "opp_net",
        "purchased_energy_fraction",
        "annual_electricity",
        "annual_gas",
        "foundation_type",
        "foundation_rigid_insulation",
        "foundation_batt_insulation",
        "foundation_insulation_grade",
        "floor_continuous_insulation",
        "floor_cavity_insulation",
        "agw_wall_construction_type",
        "ag_wall_framing_factor",
        "ag_wall_continuous_insulation",
        "ag_wall_cavity_insulation",
        "ag_wall_insulation_grade",
        "ag_wall_insulation_type",
        "ceiling_insulation_depth",
        "ceiling_cavity_insulation",
        "ceiling_continuous_insulation",
        "ceiling_insulation_type",
        "radiant_barrier",
        "window_u_factor",
        "window_shgc",
        "ach50",
        "ventilation_type",
        "ventilation_rate",
        "ventilation_run_time",
        "ventilation_fan_wattage",
        "duct_leakage",
        "duct_leakage_total",
        "duct_leakage_tightness_test",
        "duct_leakage_units",
        "high_efficiency_lights_percent",
        "ac_efficiency",
        "ac_output_capacity",
        "heating_system_type",
        "heating_efficiency",
        "heating_efficiency_units",
        "furnace_output_capacity",
        "furnace_fuel",
        "water_heater_type",
        "water_heater_fuel",
        "water_heater_capacity",
        "ag_wall_uo",
        "foundation_wall_uo",
        "ceiling_uo",
        "overall_enclosure_ua",
        "ducts_conditioned",
        "dishwasher_k_whyr",
        "refrigerator_k_wh",
        "dryer_energy_factor",
        "dryer_energy_factor_gas",
        "washer_ler",
        "is_zerh",
        "energy_star_version",
    ]

    candidates = models.ManyToManyField(
        "home.Home",
        through=Candidate,
        blank=True,
        related_name="neea_certification_candidates",
    )

    registry_id = models.CharField(max_length=100, blank=True)
    street_line1 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_abbreviation = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=100, blank=True)
    certification_date = models.DateField(blank=True, null=True)

    home_type = models.CharField(max_length=100, blank=True)
    software = models.CharField(max_length=100, blank=True)
    software_version = models.CharField(max_length=100, blank=True)
    construction_year = models.CharField(max_length=100, blank=True)
    conditioned_area = models.CharField(max_length=100, blank=True)
    conditioned_volume = models.CharField(max_length=100, blank=True)
    conditioned_floors = models.CharField(max_length=100, blank=True)
    number_bedrooms = models.CharField(max_length=100, blank=True)
    hers_index = models.CharField(max_length=100, blank=True)
    registration_type = models.CharField(max_length=100, blank=True)
    total_energy_use = models.CharField(max_length=100, blank=True)
    total_energy_cost = models.CharField(max_length=100, blank=True)
    num_cooling_systems = models.CharField(max_length=100, blank=True)
    num_heating_systems = models.CharField(max_length=100, blank=True)
    cooling_energy_use = models.CharField(max_length=100, blank=True)
    cost_cooling = models.CharField(max_length=100, blank=True)
    cooling_rated_output = models.CharField(max_length=100, blank=True)
    heating_rated_output = models.CharField(max_length=100, blank=True)
    num_hot_water_systems = models.CharField(max_length=100, blank=True)
    hot_water_energy_use = models.CharField(max_length=100, blank=True)
    cost_hot_water = models.CharField(max_length=100, blank=True)
    lighting_app_energy_use = models.CharField(max_length=100, blank=True)
    cost_lighting = models.CharField(max_length=100, blank=True)
    on_site_generation = models.CharField(max_length=100, blank=True)
    opp_net = models.CharField(max_length=100, blank=True)
    purchased_energy_fraction = models.CharField(max_length=100, blank=True)
    annual_electricity = models.CharField(max_length=100, blank=True)
    annual_gas = models.CharField(max_length=100, blank=True)
    foundation_type = models.CharField(max_length=100, blank=True)
    foundation_rigid_insulation = models.CharField(max_length=100, blank=True)
    foundation_batt_insulation = models.CharField(max_length=100, blank=True)
    foundation_insulation_grade = models.CharField(max_length=100, blank=True)
    floor_continuous_insulation = models.CharField(max_length=100, blank=True)
    floor_cavity_insulation = models.CharField(max_length=100, blank=True)
    agw_wall_construction_type = models.CharField(max_length=100, blank=True)
    ag_wall_framing_factor = models.CharField(max_length=100, blank=True)
    ag_wall_continuous_insulation = models.CharField(max_length=100, blank=True)
    ag_wall_cavity_insulation = models.CharField(max_length=100, blank=True)
    ag_wall_insulation_grade = models.CharField(max_length=100, blank=True)
    ag_wall_insulation_type = models.CharField(max_length=100, blank=True)
    ceiling_insulation_depth = models.CharField(max_length=100, blank=True)
    ceiling_cavity_insulation = models.CharField(max_length=100, blank=True)
    ceiling_continuous_insulation = models.CharField(max_length=100, blank=True)
    ceiling_insulation_type = models.CharField(max_length=100, blank=True)
    radiant_barrier = models.CharField(max_length=100, blank=True)
    window_u_factor = models.CharField(max_length=100, blank=True)
    window_shgc = models.CharField(max_length=100, blank=True)
    ach50 = models.CharField(max_length=100, blank=True)
    ventilation_type = models.CharField(max_length=100, blank=True)
    ventilation_rate = models.CharField(max_length=100, blank=True)
    ventilation_run_time = models.CharField(max_length=100, blank=True)
    ventilation_fan_wattage = models.CharField(max_length=100, blank=True)
    duct_leakage = models.CharField(max_length=100, blank=True)
    duct_leakage_total = models.CharField(max_length=100, blank=True)
    duct_leakage_tightness_test = models.CharField(max_length=100, blank=True)
    duct_leakage_units = models.CharField(max_length=100, blank=True)
    high_efficiency_lights_percent = models.CharField(max_length=100, blank=True)
    ac_efficiency = models.CharField(max_length=100, blank=True)
    ac_output_capacity = models.CharField(max_length=100, blank=True)
    heating_system_type = models.CharField(max_length=100, blank=True)
    heating_efficiency = models.CharField(max_length=100, blank=True)
    heating_efficiency_units = models.CharField(max_length=100, blank=True)
    furnace_output_capacity = models.CharField(max_length=100, blank=True)
    furnace_fuel = models.CharField(max_length=100, blank=True)
    water_heater_type = models.CharField(max_length=100, blank=True)
    water_heater_fuel = models.CharField(max_length=100, blank=True)
    water_heater_capacity = models.CharField(max_length=100, blank=True)
    ag_wall_uo = models.CharField(max_length=100, blank=True)
    foundation_wall_uo = models.CharField(max_length=100, blank=True)
    ceiling_uo = models.CharField(max_length=100, blank=True)
    overall_enclosure_ua = models.CharField(max_length=100, blank=True)
    ducts_conditioned = models.CharField(max_length=100, blank=True)
    dishwasher_k_whyr = models.CharField(max_length=100, blank=True)
    refrigerator_k_wh = models.CharField(max_length=100, blank=True)
    dryer_energy_factor = models.CharField(max_length=100, blank=True)
    dryer_energy_factor_gas = models.CharField(max_length=100, blank=True)
    washer_ler = models.CharField(max_length=100, blank=True)
    is_zerh = models.CharField(max_length=100, blank=True)
    energy_star_version = models.CharField(max_length=100, blank=True)

    @property
    def program(self):
        return "RESNET Registry Data"

    @property
    def county(self):
        return None

    def __str__(self):
        return self.street_line1

    def get_absolute_url(self):
        """Get raw certification view url."""

        return reverse("admin:customer_neea_neeacertification_change", kwargs={"pk": self.id})

    def can_be_edited(self, user):  # pylint: disable=unused-argument, no-self-use
        """Return False."""

        return False

    def can_be_deleted(self, user):  # pylint: disable=unused-argument, no-self-use
        """Return False."""

        return False

    def get_is_multifamily(self):
        return self.home_type != "Single-Family"
