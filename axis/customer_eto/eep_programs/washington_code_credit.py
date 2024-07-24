"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "8/5/21 13:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from collections import OrderedDict
from datetime import date
from enum import Enum

from django.apps import apps

from axis.core.tests.factories import provider_admin_factory
from axis.customer_eto.enumerations import YesNo, CaseInsensitiveEnumMeta
from axis.eep_program.program_builder import ProgramBuilder

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


class BuildingEnvelope(Enum):
    NONE = "None"
    OPTION_1p1 = "1.1: U-0.24 windows"
    OPTION_1p2 = "1.2: U-0.20 windows"
    OPTION_1p3a = "1.3.a: U-0.28 windows + R38 floor or R10 slabs"
    OPTION_1p3b = "1.3.b: 5% UA Reduction"
    OPTION_1p4a = "1.4.a: U-0.25 windows, R21+R4ci walls, R38 floor or R10 slabs"
    OPTION_1p4b = "1.4.b: 15% UA Reduction"
    OPTION_1p5a = (
        "1.5.a: U-0.22 windows, ceiling/vaults R-49, R21+R12ci walls, R38 floor or R10 slabs"
    )
    OPTION_1p5b = "1.5.b: 30% UA reduction"
    OPTION_1p6a = (
        "1.6.a: U0.18 windows, ceiling/vaults R60, R21+R16ci walls, R48 floor or R20 slabs"
    )
    OPTION_1p6b = "1.6.b: 40% UA reduction"
    OPTION_1p7 = "1.7: Adv Framing, U.28 windows, Full R49 ceiling"


class AirLeakageControl(Enum):
    NONE = "None"
    OPTION_2p1 = "2.1: 3 ACH Eff vent. fan, R402.4.1.2"
    OPTION_2p2 = "2.2: 2 ACH Eff, 65% HRV vent., R402.4.1.2"
    OPTION_2p3 = "2.3: 1.5 ACH Eff, 75% HRV vent., R402.4.1.2"
    OPTION_2p4 = "2.4: 0.6 ACH Eff, 80% HRV vent, R402.4.1.3"


class HighEfficiencyHVAC(Enum):
    NONE = "None"
    OPTION_3p1 = "3.1: REQUIRED - 95 AFUE"
    OPTION_3p2 = "3.2: INELIGIBLE SELECTION"
    OPTION_3p3 = "3.3: INELIGIBLE SELECTION"
    OPTION_3p4 = "3.4: INELIGIBLE SELECTION"
    OPTION_3p5 = "3.5: INELIGIBLE SELECTION"
    OPTION_3p6 = "3.6: INELIGIBLE SELECTION"


class HighEfficiencyHVACDistribution(Enum):
    NONE = "None"
    OPTION_4p1 = "4.1: Deeply Buried Ducts"
    OPTION_4p2 = "4.2: HVAC & Ducts In Conditioned Space"


class DWHR(Enum):
    NONE = "None"
    OPTION_5p1 = "5.1: Drain Water Heat Recovery"


class EfficientWaterHeating(Enum):
    NONE = "None"
    OPTION_5p2 = "5.2: INELIGIBLE SELECTION"
    OPTION_5p3 = "5.3: GAS - UEF 0.91 (REQUIRED FOR GAS DHW)"
    OPTION_5p4 = "5.4: ELEC - NEEA QPL Tier I"
    OPTION_5p5 = "5.5: ELEC - NEEA QPL Tier III"
    OPTION_5p6 = "5.6: ELEC - Split HP w/ UEF 2.9"


class RenewableEnergy(Enum):
    NONE = "None"
    OPTION_6p1a = "6.1: Renewable Generation - x1 - 1,200 - 2,399 kWh"
    OPTION_6p1b = "6.1: Renewable Generation - x2 - 2,400 - 3,599 kWh"
    OPTION_6p1c = "6.1: Renewable Generation - x3 - >3,600 kWh"


class Appliances(Enum):
    NONE = "None"
    OPTION_7p1 = "7.1: ENERGY STAR dishwasher, refrigerator, washer, ventless dryer CEF >5.2"


class WACCFuelType(Enum):
    GAS = "Gas"
    ELECTRIC = "Electric"


# Note this needs to be case insensitive
class ThermostatType(Enum, metaclass=CaseInsensitiveEnumMeta):
    PROGRAMABLE = "Programmable"
    PROGRAMABLE_WIFI = "Programmable + Wi-fi"
    BRYANT = "Bryant: Housewise Wi-Fi"
    CARRIER = "Carrier: Cor Wi-Fi"
    ECOBEE3 = "ecobee3 (Not ecobee 3 lite)"
    ECOBEE4 = "ecobee4"
    ECOBEE_VOICE = "ecobee: Smart Thermostat with Voice Control"
    NEST_LEARNING = "Nest: Learning Thermostat (all generations)"
    NEST = "Nest Thermostat"
    NEST_E = "Nest: Thermostat E"
    OTHER = "Smart, Other"


class FireplaceType(Enum):
    NONE = "None"
    FP_LT70 = "<70 FE"
    FP_70_75 = "70-75 FE"
    FP_GT75 = ">75 FE"


class FramingType(Enum):
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class VentilationType(Enum):
    EXHAUST_ONLY = "Exhaust Only"
    SUPPLY_ONLY = "Supply Only"
    BALANCED = "Balanced (no recovery)"
    HRV_ERV = "HRV/ERV"


class DuctLocation(Enum):
    UNCONDITIONED_SPACE = "Unconditioned Space"
    CONDITIONED_SPACE = "Conditioned Space"
    DEEPLY_BURIED = "Deeply Buried"


class FurnaceLocation(Enum):
    UNCONDITIONED_SPACE = "Unconditioned Space"
    CONDITIONED_SPACE = "Conditioned Space"


class WashingtonCodeCreditProgram(ProgramBuilder):
    """Program Specs for the Washington Code Credit"""

    name = "Energy Trust Washington Code Credits – 2021"
    comment = "Energy Trust Washington Code Credits – 2021 (Washington Only)"

    slug = "washington-code-credit"
    owner = app.CUSTOMER_SLUG

    viewable_by_company_type = "qa,provider,rater"

    certifiable_by = ["peci"]
    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    manual_transition_on_certify = True

    require_home_relationships = {
        "builder": True,
        "rater": True,
        "utility": True,
        "provider": True,
        "hvac": False,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
    }
    visibility_date = date(year=2021, month=11, day=1)
    start_date = date(year=2022, month=2, day=1)
    close_date = date(year=2024, month=11, day=1)
    submit_date = date(year=2024, month=11, day=15)
    end_date = date(year=2025, month=1, day=1)
    hers_range = [0, 500]

    measures = {
        "rater": [
            (
                "Home Data",
                [
                    "wcc-conditioned_floor_area",
                    "wcc-water_heating_fuel",
                    "wcc-thermostat_type",
                    "wcc-fireplace_efficiency",
                ],
            ),
            (
                "Efficient Building Envelope Options",
                [
                    "wcc-wall_cavity_r_value",
                    "wcc-wall_continuous_r_value",
                    "wcc-framing_type",
                    "wcc-window_u_value",
                    "wcc-window_shgc",
                    "wcc-floor_cavity_r_value",
                    "wcc-slab_perimeter_r_value",
                    "wcc-under_slab_r_value",
                    "wcc-ceiling_r_value",
                    "wcc-raised_heel",
                    "wcc-total_ua_alternative",
                ],
            ),
            (
                "Air Leakage Control & Efficient Ventilation Options",
                [
                    "wcc-air_leakage_ach",
                    "wcc-ventilation_type",
                    "wcc-ventilation_brand",
                    "wcc-ventilation_model",
                    "wcc-hrv_asre",
                ],
            ),
            (
                "High Efficiency HVAC Equipment Options",
                ["wcc-furnace_brand", "wcc-furnace_model", "wcc-furnace_afue"],
            ),
            (
                "High Efficiency HVAC Distribution System",
                [
                    "wcc-furnace_location",
                    "wcc-duct_location",
                    "wcc-duct_leakage",
                ],
            ),
            (
                "Efficient Water Heating",
                [
                    "wcc-dwhr_installed",
                    "wcc-water_heater_brand",
                    "wcc-water_heater_model",
                    "wcc-gas_water_heater_uef",
                    "wcc-electric_water_heater_uef",
                ],
            ),
        ]
    }
    texts = {
        "rater": {
            "wcc-conditioned_floor_area": "Conditioned Floor Area",
            "wcc-water_heating_fuel": "Water Heating Fuel",
            "wcc-thermostat_type": "Thermostat Type",
            "wcc-fireplace_efficiency": "Fireplace Efficiency",
            "wcc-wall_cavity_r_value": "Above Grade Wall Cavity R-Value",
            "wcc-wall_continuous_r_value": "Above Grade Wall Continuous R-Value",
            "wcc-framing_type": "Above Grade Wall Framing Type",
            "wcc-window_u_value": "Window U-Value",
            "wcc-window_shgc": "Window SHGC",
            "wcc-floor_cavity_r_value": "Floor-Cavity R-Value",
            "wcc-slab_perimeter_r_value": "Slab Perimeter R-Value",
            "wcc-under_slab_r_value": "Underslab R-Value",
            "wcc-ceiling_r_value": "Ceiling R-Value",
            "wcc-raised_heel": "Raised Heel?",
            "wcc-air_leakage_ach": "Air Leakage ACH50",
            "wcc-ventilation_type": "Ventilation Type",
            "wcc-ventilation_brand": "Ventilation Brand",
            "wcc-ventilation_model": "Ventilation Model",
            "wcc-hrv_asre": "HRV ASRE% (0-100)",
            "wcc-furnace_brand": "Furnace Brand",
            "wcc-furnace_model": "Furnace Model",
            "wcc-furnace_afue": "Furnace AFUE",
            "wcc-furnace_location": "Furnace Location",
            "wcc-duct_location": "Duct Location",
            "wcc-duct_leakage": "Duct Leakage CFM50",
            "wcc-dwhr_installed": "Drain Water Heat Recovery Installed",
            "wcc-water_heater_brand": "Water Heater Brand",
            "wcc-water_heater_model": "Water Heater Model",
            "wcc-gas_water_heater_uef": "Gas Water Heater UEF (0-1)",
            "wcc-electric_water_heater_uef": "Electric Water Heater UEF (0-5)",
            "wcc-total_ua_alternative": "Total UA Alternative",
        }
    }

    descriptions = {
        "default": {
            "wcc-floor_cavity_r_value": "If Slab enter 0",
            "wcc-slab_perimeter_r_value": "If no Slab enter 0",
            "wcc-under_slab_r_value": "If no Slab enter 0",
        }
    }

    suggested_responses = {
        # noqa
        "default": {
            tuple([i.value for i in YesNo]): ["wcc-raised_heel", "wcc-dwhr_installed"],
            tuple([i.value for i in WACCFuelType]): ["wcc-water_heating_fuel"],
            tuple([i.value for i in ThermostatType]): ["wcc-thermostat_type"],
            tuple([i.value for i in FireplaceType]): ["wcc-fireplace_efficiency"],
            tuple([i.value for i in FramingType]): ["wcc-framing_type"],
            tuple([i.value for i in VentilationType]): ["wcc-ventilation_type"],
            tuple([i.value for i in FurnaceLocation]): ["wcc-furnace_location"],
            tuple([i.value for i in DuctLocation]): ["wcc-duct_location"],
        }
    }

    instrument_types = {
        "integer": [
            "wcc-conditioned_floor_area",
            "wcc-wall_cavity_r_value",
            "wcc-wall_continuous_r_value",
            "wcc-floor_cavity_r_value",
            "wcc-slab_perimeter_r_value",
            "wcc-under_slab_r_value",
            "wcc-ceiling_r_value",
            "wcc-hrv_asre",
            "wcc-furnace_afue",
            "wcc-duct_leakage",
            "wcc-total_ua_alternative",
        ],
        "float": [
            "wcc-window_u_value",
            "wcc-window_shgc",
            "wcc-air_leakage_ach",
            "wcc-gas_water_heater_uef",
            "wcc-electric_water_heater_uef",
        ],
    }

    instrument_conditions = {
        "default": {},
        "rater": {
            "instrument": {
                "wcc-ventilation_type": {
                    ("one", (VentilationType.HRV_ERV.value,)): ["wcc-hrv_asre"],
                },
                "wcc-water_heating_fuel": {
                    ("one", (WACCFuelType.GAS.value,)): ["wcc-gas_water_heater_uef"],
                    ("one", (WACCFuelType.ELECTRIC.value,)): ["wcc-electric_water_heater_uef"],
                },
            }
        },
    }

    optional_measures = ["wcc-total_ua_alternative"]

    annotations = OrderedDict(
        (
            (
                "wcc-envelope-option",
                {
                    "name": "Efficiency Building Envelope Option",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [x.value for x in BuildingEnvelope],
                    "is_required": "True",
                },
            ),
            (
                "wcc-air-leakage-option",
                {
                    "name": "Air Leakage Control & Efficient Ventilation Options",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [x.value for x in AirLeakageControl],
                    "is_required": "True",
                },
            ),
            (
                "wcc-hvac-option",
                {
                    "name": "High efficiency HVAC option",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [x.value for x in HighEfficiencyHVAC],
                    "is_required": "True",
                },
            ),
            (
                "wcc-hvac-distribution-option",
                {
                    "name": "High efficiency HVAC distribution system option",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [
                        x.value for x in HighEfficiencyHVACDistribution
                    ],
                    "is_required": "True",
                },
            ),
            (
                "wcc-dwhr-option",
                {
                    "name": "Drain water heat recovery option",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [x.value for x in DWHR],
                    "is_required": "True",
                },
            ),
            (
                "wcc-water-heating-option",
                {
                    "name": "Efficient water heating option",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [x.value for x in EfficientWaterHeating],
                    "is_required": "True",
                },
            ),
            (
                "wcc-renewable-electric-option",
                {
                    "name": "Renewable electric energy option",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [x.value for x in RenewableEnergy],
                    "is_required": "True",
                },
            ),
            (
                "wcc-appliance-option",
                {
                    "name": "Appliance package option",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": [x.value for x in Appliances],
                    "is_required": "True",
                },
            ),
        )
    )

    def build_program(self):
        from axis.company.models import Company

        certifiable = Company.objects.filter(slug=self.certifiable_by[0]).first()
        if not certifiable:
            self.stdout.write("Adding certifying provider\n")
            from axis.company.models import SponsorPreferences
            from axis.relationship.models import Relationship

            eto = Company.objects.get(slug="eto")
            co_fields = [k.name for k in eto._meta.fields]
            exclude = ["id", "name", "slug", "group"]
            defaults = {"company__%s" % k: getattr(eto, k) for k in co_fields if k not in exclude}

            defaults["company__counties"] = eto.counties.all()
            defaults["company__is_eep_sponsor"] = False
            defaults["company__is_customer"] = False
            defaults["company__slug"] = self.certifiable_by[0]
            defaults["company__name"] = "WA Code Credit Provider"

            user_data = {
                "username": "wa-code-credit-provider",
                "first_name": "Matchstick",
                "last_name": "Marc",
                "email": "skip@wcc.com",
                "title": "Head Chief",
                "department": "Procurement",
                "is_approved": True,
            }
            defaults.update(**user_data)
            provider_user = provider_admin_factory(**defaults)
            provider = provider_user.company
            self.stdout.write(f"Created certifying provider {provider} with user {provider_user}")

            SponsorPreferences.objects.get_or_create(sponsor=eto, sponsored_company=provider)
            provider.save()  # Force a perms update

            companies = [eto, provider]
            Relationship.objects.create_mutual_relationships(*companies)

        return super(WashingtonCodeCreditProgram, self).build_program()
