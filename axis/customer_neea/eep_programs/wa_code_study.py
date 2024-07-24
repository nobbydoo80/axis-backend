"""wa_code_study.py: Django WA Code Study"""

__author__ = "Steven K"
__date__ = "09/24/2019 11:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


import logging
from collections import OrderedDict
from axis.eep_program.program_builder.base import ProgramBuilder

from ..strings import (
    WA_CODE_DWELLING_TYPES,
    WA_CODE_BUILDING_ENVELOPE_TYPES,
    WA_CODE_AIR_LEAKAGE,
    WA_CODE_BUILDING_HVAC,
    WA_CODE_BUILDING_HVAC_DISTRIBUTION,
    WA_CODE_QTY_RENEWABLE_ENERGY,
    WA_CODE_BUILDING_WATER_HEATING_5A,
    WA_CODE_BUILDING_WATER_HEATING_5BC,
    WA_CODE_BUILDING_WATER_HEATING_5D,
)


log = logging.getLogger(__name__)


class WACodeStudy(ProgramBuilder):
    """Program Specs for the Washington Code Study"""

    CERTIFIER_SLUG = "neea"

    name = "Washington State 2015 Energy Code Compliance Study"
    slug = "wa-code-study"

    owner = CERTIFIER_SLUG

    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    require_home_relationships = []
    manual_transition_on_certify = True
    measures = {
        "rater": {
            "default": [
                "inspection-stage",
                "inspection-date",
                "code-jurisdiction",
                "permit-docs-available",
                "permit-date",
                "home-size",
                "home-volume",
                "home-type",
                "home-qty-floors-above-grade",
                "home-qty-bedrooms",
                "home-qty-bathrooms",
                "home-foundation-type",
                "home-foundation-r-value",
                "home-foundation-slab-depth",
                "home-below-grade-walls-observed",
                "home-below-grade-walls-ext-r-value",
                "home-below-grade-walls-int-r-value",
                "home-below-grade-walls-cavity-r-value",
                "home-below-grade-insulation-grade",
                "meets-wa-code-qty-below-grade-wall",
                "home-floors-observed",
                "home-floor-r-value",
                "home-floor-joist-depth",
                "home-above-grade-walls-observed",
                "home-above-grade-walls-continuous-ins-r-value",
                "home-above-grade-walls-cavity-r-value",
                "home-above-grade-walls-insulation-grade",
                "meets-wa-code-above-grade-wall-requirements",
                "home-windows-observed",
                "home-window-u-value",
                "home-window-shgc",
                "home-skylight-u-value",
                "home-ceiling-observed",
                "home-ceiling-type",
                "home-ceiling-r-value",
                "home-ceiling-framing-details",
                "meets-wa-code-ceiling-requirements",
                "home-infiltration-builder-test",
                "home-infiltration-observed",
                "home-infiltration-cfm",
                "home-infiltration-ach",
                "home-lighting-observed",
                "home-lighting-meets-efficacy",
                "home-recessed-lighting",
                "home-recessed-lighting-rated",
                "home-bathroom-fan-observed",
                "home-bathroom-fan-cfm",
                "home-bathroom-fan-efficacy",
                "home-primary-heating",
                "home-ashp-lock-out-temp",
                "home-ashp-hspf",
                "home-ashp-expected-capacity",
                "home-ashp-installed-capacity",
                "home-primary-heating-has-ecm",
                "home-furnace-afue",
                "home-boiler-afue",
                "home-gshp-cop",
                "home-ductless-hp-hspf",
                "home-ductless-hp-expected-capacity",
                "home-ductless-hp-installed-capacity",
                "home-ductless-hp-qty-heads",
                "home-ductless-hp-ele-resistance-watts",
                "home-ductless-hp-ele-resistance-serving-largest-zone",
                "home-duct-primary-location",
                "home-duct-r-value",
                "home-duct-builder-test",
                "home-duct-leakage-with-air-handler",
                "home-duct-leakage-without-air-handler",
                "meets-wa-code-duct-requirements",
                "home-primary-heating-brand",
                "home-primary-cooling",
                "home-primary-cooling-seer",
                "home-primary-cooling-brand",
                "home-thermostat-type",
                "home-ventilation-type",
                "home-ventilation-fan-rating",
                "home-ventilation-fan-wired-damper",
                "home-ventilation-exhaust-brand",
                "home-ventilation-sensible-heat-recovery-rating",
                "home-ventilation-hrv-brand",
                "home-ventilation-radon-brand",
                "home-primary-hot-water-type",
                "home-primary-hot-water-tank-size",
                "home-primary-hot-water-location",
                "home-primary-hot-water-r10-board",
                "home-primary-hot-water-pipe-r-value",
                "home-primary-hot-water-gas-ef",
                "meets-wa-code-solar-water-requirements",
                "home-primary-hot-water-hp-ef",
                "home-primary-hot-water-ele-ef",
                "meets-neea-hp-requirements",
                "home-primary-hot-water-brand",
                "meets-wa-code-shower-head-requirements",
                "showerhead-flow-rate",
                "kitchen-faucet-flow-rate",
                "bathroom-faucet-flow-rate",
                "hot-water-recirculation-pump",
                "hot-water-recirculation-pump-type",
                "drain-water-heat-recovery-system",
                "meets-wa-code-drain-water-requirements",
                "renewable-energy-system",
                "meets-wa-code-energy-credit-option",
                "ev-charging",
                "energy-storage",
                "above-code-participation",
            ],
        },
        "qa": {},
    }
    texts = {
        "rater": {
            "inspection-stage": "Inspection Stage",
            "inspection-date": "Inspection Date",
            "code-jurisdiction": "Code Jurisdiction",
            "permit-docs-available": "Permit/Code documents available",
            "permit-date": "Permit Date",
            "home-size": "Home Size (sq. ft)",
            "home-volume": "Home Volume (cu. ft)",
            "home-type": "Home Type",
            "home-qty-floors-above-grade": "Number of floors above grade",
            "home-qty-bedrooms": "Number of bedrooms",
            "home-qty-bathrooms": "Number of bathrooms",
            "home-foundation-type": "Foundation Type",
            "home-foundation-r-value": "Slab R-Value",
            "home-foundation-slab-depth": "Slab Depth (ft)",
            "home-below-grade-walls-observed": "Below Grade walls Insulation",
            "home-below-grade-walls-ext-r-value": "Exterior Continuous Insulation R-Value",
            "home-below-grade-walls-int-r-value": "Interior Continuous Insulation R-Value",
            "home-below-grade-walls-cavity-r-value": "Cavity Insulation Insulation R-Value",
            "home-below-grade-insulation-grade": "Below Grade Walls Insulation Grading (RESNET)",
            "meets-wa-code-qty-below-grade-wall": "Do below grade walls meet requirements of 1B or 1C",
            "home-floors-observed": "Floors",
            "home-floor-r-value": "Floor R-Value",
            "home-floor-joist-depth": "Floor Joist Depth (inches)",
            "home-above-grade-walls-observed": "Above Grade Walls Insulation",
            "home-above-grade-walls-continuous-ins-r-value": "Above Grade Walls Continuous Insulation R-value",
            "home-above-grade-walls-cavity-r-value": "Above Grade Walls Cavity Insulation R-value",
            "home-above-grade-walls-insulation-grade": "Above Grade Walls Insulation Grade (RESNET)",
            "meets-wa-code-above-grade-wall-requirements": "If Energy Credit Option 1B or 1C selected, then Do Above Grade Walls meet "
            "requirements of energy credit 1B or 1C?",
            "home-windows-observed": "Windows",
            "home-window-u-value": "Window U-value (Verticle Fenestration, area weighted average)",
            "home-window-shgc": "Window SHGC",
            "home-skylight-u-value": "Skylight U-value",
            "home-ceiling-observed": "Ceilings",
            "home-ceiling-type": "Type of Ceiling",
            "home-ceiling-r-value": "Ceiling R-Value",
            "home-ceiling-framing-details": "Ceiling Framing Details",
            "meets-wa-code-ceiling-requirements": "If Energy Credit Option 1C selected, then Do ceilings meet the requirements of "
            "energy credit option 1C?",
            "home-infiltration-builder-test": "Builder Reported Infiltration Test",
            "home-infiltration-observed": "Infiltration Test",
            "home-infiltration-cfm": "Infiltration Value CFM@50 Pascals",
            "home-infiltration-ach": "Infiltration Value ACH@50 Pascals",
            "home-lighting-observed": "Lighting",
            "home-lighting-meets-efficacy": "Is 75% of lighting high efficacy?",
            "home-recessed-lighting": "Recessed Lighting?",
            "home-recessed-lighting-rated": "Is recessed lighting ASTM rated and gasketed?",
            "home-bathroom-fan-observed": "Bathroom Fan",
            "home-bathroom-fan-cfm": "Bathroom Fan Air Flow Rate (CFM)",
            "home-bathroom-fan-efficacy": "Bathroom Fan Efficacy (CFM/Watt)",
            "home-primary-heating": "Primary Space Heating Equipment Type",
            "home-ashp-lock-out-temp": "Air Source Heat Pump Aux Heat Lock Out temp °F",
            "home-ashp-hspf": "Air Source Heat Pump HSPF",
            "home-ashp-expected-capacity": "Expected Heat Pump Capacity per Sizing Calculations (btu/h)",
            "home-ashp-installed-capacity": "Installed Heat Pump Capacity (btu/h)",
            "home-primary-heating-has-ecm": "Is there an ECM?",
            "home-furnace-afue": "Furnace AFUE",
            "home-boiler-afue": "Boiler AFUE",
            "home-gshp-cop": "Ground Source Heat Pump COP",
            "home-ductless-hp-hspf": "Ductless Heat Pump HSPF",
            "home-ductless-hp-expected-capacity": "Expected Ductless Heat Pump Capacity per Sizing Calculations (btu/h) ",
            "home-ductless-hp-installed-capacity": "Installed Ductless Heat Pump Capacity (btu/h)",
            "home-ductless-hp-qty-heads": "Number of Ductless Heat Pump Indoor Heads",
            "home-ductless-hp-ele-resistance-watts": "Electric Resistance Watts",
            "home-ductless-hp-ele-resistance-serving-largest-zone": "Is Ductless Heat Pump servicing the largest zone?",
            "home-duct-primary-location": "Duct Primary Location",
            "home-duct-r-value": "Duct Insulation R-value",
            "home-duct-builder-test": "Builder Reported Duct Leakage Test",
            "home-duct-leakage-with-air-handler": "Duct Leakage Test with Air Handler CFM @ 25",
            "home-duct-leakage-without-air-handler": "Duct Leakage Test without Air Handler CFM @ 25",
            "meets-wa-code-duct-requirements": "Do all duct components meet the requirements of energy credit option 4?",
            "home-primary-heating-brand": "Primary Space Heating Equipment Brand and Model",
            "home-primary-cooling": "Primary Space Cooling Equipment Type",
            "home-primary-cooling-seer": "Cooling Equipment SEER value",
            "home-primary-cooling-brand": "Cooling Equipment Brand and Model",
            "home-thermostat-type": "Type of Thermostat",
            "home-ventilation-type": "Type of Ventilation",
            "home-ventilation-fan-rating": "Ventilation Fan Rating (watts/cfm)",
            "home-ventilation-fan-wired-damper": "Is Mechanical Damper Wired to Control? ",
            "home-ventilation-exhaust-brand": "Brand and Model of system",
            "home-ventilation-sensible-heat-recovery-rating": "HRV Sensible Heat Recovery Efficiency Rating",
            "home-ventilation-hrv-brand": "HRV Brand and Model of system",
            "home-ventilation-radon-brand": "Radon Ventilation System",
            "home-primary-hot-water-type": "Primary Water Heating Equipment Type",
            "home-primary-hot-water-tank-size": "Primary Water Heating Equipment Tank Size (gallons)",
            "home-primary-hot-water-location": "Primary Water Heating Equipment Location",
            "home-primary-hot-water-r10-board": "Is there R-10 insulation board installed with the water heater?",
            "home-primary-hot-water-pipe-r-value": "Primary Water Heating Pipe Insluation R-Value",
            "home-primary-hot-water-gas-ef": "Gas/Propane Water Heater EF or UEF Value",
            "meets-wa-code-solar-water-requirements": "Does the solar water heating equipment meet the requirements of "
            "energy credit option 5C? ",
            "home-primary-hot-water-hp-ef": "Heat Pump Water Heater EF or UEF Value",
            "home-primary-hot-water-ele-ef": "Electric Water Heater EF or UEF Value",
            "meets-neea-hp-requirements": "Does the Heat Pump Water Heater meet NEEA's Northern Climate Specifications?",
            "home-primary-hot-water-brand": "Primary Water Heating Equipment Brand and Model",
            "meets-wa-code-shower-head-requirements": "Do the kitchen, bathroom, and showerheads meet the requirements of energy "
            "credit option 5A?",
            "showerhead-flow-rate": "Showerhead flow rate GPM",
            "kitchen-faucet-flow-rate": "Kithen Faucet flow rate GPM",
            "bathroom-faucet-flow-rate": "Bathroom Faucet flow rate GPM",
            "hot-water-recirculation-pump": "Hot water recirculation pump?",
            "hot-water-recirculation-pump-type": "Type of Recirculation Pump controls",
            "drain-water-heat-recovery-system": "Drain Water Heat Recovery System",
            "meets-wa-code-drain-water-requirements": "Does the drain water heat recovery system meet the requirements of "
            "energy credit option 5D? ",
            "renewable-energy-system": "Renewable Energy System",
            "meets-wa-code-energy-credit-option": "Does the renewable energy system meeting the requirements of "
            "energy credit option 6?",
            "ev-charging": "EV Charging",
            "energy-storage": "Energy Storage",
            "above-code-participation": "Above-Code Certification Participation",
        },
    }
    descriptions = {
        "default": {
            "inspection-date": "What is the date of inspection",
        }
    }
    instrument_types = {
        "integer": [
            "home-size",
            "home-volume",
            "home-foundation-r-value",
            "home-foundation-slab-depth",
            "home-below-grade-walls-ext-r-value",
            "home-below-grade-walls-int-r-value",
            "home-below-grade-walls-cavity-r-value",
            "home-above-grade-walls-continuous-ins-r-value",
            "home-floor-r-value",
            "home-qty-bedrooms",
            "home-bathroom-fan-cfm",
            "home-ceiling-r-value",
            "home-infiltration-cfm",
            "home-furnace-afue",
            "home-boiler-afue",
            "home-ashp-expected-capacity",
            "home-ashp-installed-capacity",
            "home-ashp-lock-out-temp",
            "home-ductless-hp-expected-capacity",
            "home-ductless-hp-installed-capacity",
            "home-ductless-hp-qty-heads",
            "home-ductless-hp-ele-resistance-watts",
            "home-duct-r-value",
            "home-primary-hot-water-tank-size",
            "home-primary-hot-water-pipe-r-value",
        ],
        "float": [
            "home-qty-bathrooms",
            "home-qty-floors-above-grade",
            "home-window-u-value",
            "home-window-shgc",
            "home-skylight-u-value",
            "home-bathroom-fan-efficacy",
            "home-ashp-hspf",
            "home-gshp-cop",
            "home-ductless-hp-hspf",
            "home-infiltration-ach",
            "home-ventilation-fan-rating",
            "home-ventilation-sensible-heat-recovery-rating",
            "home-primary-cooling-seer",
            "home-primary-hot-water-gas-ef",
            "home-primary-hot-water-hp-ef",
            "home-primary-hot-water-ele-ef",
        ],
        "date": ["inspection-date", "permit-date"],
    }

    suggested_responses = {
        "rater": {
            ("Rough", "Final"): ["inspection-stage"],
            (
                "Auburn",
                "Battle Ground",
                "Bellevue",
                "Benton County Unincorporated Area",
                "Bremerton",
                "Camas",
                "Chelan County Unincorporated Area",
                "Clark County Unincorporated Area",
                "Douglas County Unincorporated Area",
                "Ferndale",
                "Island County Unincorporated Area",
                "Jefferson County Unincorporated Area",
                "Kennewick",
                "King County Unincorporated Area",
                "Kirkland",
                "Kitsap County Unincorporated Area",
                "Kittitas County Unincorporated Area",
                "Lake Stevens",
                "Mason County Unincorporated Area",
                "Ocean Shores",
                "Okanogan County Unincorporated Area",
                "Pasco",
                "Pierce County Unincorporated Area",
                "Port Townsend",
                "Poulsbo",
                "Richland",
                "Ridgefield",
                "Seattle",
                "Skagit County Unincorporated Area",
                "Snohomish County Unincorporated Area",
                "Spokane",
                "Spokane County Unincorporated Area",
                "Stevens County Unincorporated Area",
                "Thurston County Unincorporated Area",
                "Vancouver",
                "Wenatchee",
                "West Richland",
                "Other",
            ): ["code-jurisdiction"],
            ("Yes", "No"): [
                "permit-docs-available",
                "home-lighting-meets-efficacy",
                "home-recessed-lighting",
                "home-recessed-lighting-rated",
                "home-primary-heating-has-ecm",
                "home-ductless-hp-ele-resistance-serving-largest-zone",
                "home-primary-hot-water-r10-board",
                "meets-wa-code-solar-water-requirements",
                "meets-neea-hp-requirements",
                "meets-wa-code-duct-requirements",
                "hot-water-recirculation-pump",
                "drain-water-heat-recovery-system",
                "meets-wa-code-energy-credit-option",
                "energy-storage",
            ],
            ("Yes", "Not Observable"): [
                "home-floors-observed",
                "home-above-grade-walls-observed",
                "home-windows-observed",
                "home-ceiling-observed",
                "home-infiltration-observed",
                "home-lighting-observed",
                "home-bathroom-fan-observed",
            ],
            ("Yes", "No", "Not Observable"): [
                "home-below-grade-walls-observed",
                "home-ventilation-fan-wired-damper",
            ],
            ("Yes", "No", "Not Applicable"): [
                "meets-wa-code-qty-below-grade-wall",
                "meets-wa-code-above-grade-wall-requirements",
                "meets-wa-code-ceiling-requirements",
                "meets-wa-code-drain-water-requirements",
                "meets-wa-code-shower-head-requirements",
            ],
            ("Single Family Detached", "Duplex", "Single family attached/townhome"): ["home-type"],
            (
                "Slab on Grade",
                "Below Grade Slab",
                "Vented Crawl Space",
                "Unvented Crawl Space",
                "Conditioned Basement",
                "Unconditioned Basement",
                "Other",
            ): ["home-foundation-type"],
            ("1", "2", "3"): [
                "home-below-grade-insulation-grade",
                "home-above-grade-walls-insulation-grade",
            ],
            ("Flat", "Vaulted"): ["home-ceiling-type"],
            (
                "Air Source Heat Pump",
                "Gas Furnace",
                "Gas Boiler",
                "Ductless Heat Pump",
                "Ductless Heat Pump with Electric Resistance",
                "Ground Source Heat Pump",
                "Propane Furnace",
                "Propane Boiler",
                "Other",
                "Not Observable",
            ): ["home-primary-heating"],
            ("Conditioned Space", "Attic", "Crawlspace", "Not Observable"): [
                "home-duct-primary-location"
            ],
            (
                "Air Conditioner",
                "Air Source Heat Pump",
                "Ductless Heat Pump",
                "None",
                "Not Observable",
            ): ["home-primary-cooling"],
            ("Programmable", "Smart", "None", "Not Observable"): ["home-thermostat-type"],
            ("High Efficiency Fan", "HRV", "Supply", "Exhaust", "Balanced", "Not Observable"): [
                "home-ventilation-type"
            ],
            (
                "Electric conventional",
                "Gas conventional",
                "Heat Pump Water Heater",
                "Gas Tankless",
                "Ground Source Heat Pump",
                "Propane conventional",
                "Propane Tankless",
                "Solar",
                "Other",
                "Not Observable",
            ): ["home-primary-hot-water-type"],
            ("Conditioned Space", "Unconditioned Space"): ["home-primary-hot-water-location"],
            ("2.0", "1.8", "1.75", "1.5", "1.0", "Other"): [
                "showerhead-flow-rate",
                "kitchen-faucet-flow-rate",
                "bathroom-faucet-flow-rate",
            ],
            ("Solar PV", "Wind", "Renewable-ready", "None", "Not Observable"): [
                "renewable-energy-system"
            ],
            ("Level 1", "Level 2", "Level 3 DC Fast Charge", "EV-ready", "None"): ["ev-charging"],
            (
                "RESNET HERS",
                "ENERGY STAR",
                "DOE ZERH",
                "NGBS",
                "PHIUS",
                "LEED",
                "Indoor AirPlus",
                "Built Green",
                "Utility Performance Path",
                "Energy Trust EPS",
                "Other",
            ): ["above-code-participation"],
        },
    }

    suggested_response_flags = {
        "default": {},
        "rater": {
            "home-foundation-type": {
                "Other": {"comment_required": True},
            },
            "home-primary-heating": {
                "Other": {"comment_required": True},
                "Not Observable": {"comment_required": True},
            },
            "meets-wa-code-qty-below-grade-wall": {
                "No": {"comment_required": True},
            },
            "meets-wa-code-above-grade-wall-requirements": {
                "No": {"comment_required": True},
            },
            "meets-wa-code-ceiling-requirements": {
                "No": {"comment_required": True},
            },
            "home-lighting-meets-efficacy": {
                "No": {"comment_required": True},
            },
            "home-recessed-lighting-rated": {
                "No": {"comment_required": True},
            },
            "home-ductless-hp-ele-resistance-serving-largest-zone": {
                "No": {"comment_required": True},
            },
            "meets-wa-code-duct-requirements": {
                "No": {"comment_required": True},
            },
            "home-ventilation-fan-wired-damper": {
                "Not Observable": {"comment_required": True},
                "No": {"comment_required": True},
            },
            "home-primary-hot-water-r10-board": {
                "No": {"comment_required": True},
            },
            "meets-wa-code-solar-water-requirements": {
                "No": {"comment_required": True},
            },
            "meets-neea-hp-requirements": {
                "No": {"comment_required": True},
            },
            "meets-wa-code-shower-head-requirements": {
                "No": {"comment_required": True},
            },
            "meets-wa-code-drain-water-requirements": {
                "No": {"comment_required": True},
            },
            "meets-wa-code-energy-credit-option": {
                "No": {"comment_required": True},
            },
            "home-below-grade-walls-observed": {
                "No": {"comment_required": True},
                "Not Observable": {"comment_required": True},
            },
            "home-floors-observed": {
                "Not Observable": {"comment_required": True},
            },
            "home-above-grade-walls-observed": {
                "Not Observable": {"comment_required": True},
            },
            "home-windows-observed": {
                "Not Observable": {"comment_required": True},
            },
            "home-ceiling-observed": {
                "Not Observable": {"comment_required": True},
            },
            "home-infiltration-observed": {
                "Not Observable": {"comment_required": True},
            },
            "home-lighting-observed": {
                "Not Observable": {"comment_required": True},
            },
            "home-bathroom-fan-observed": {
                "Not Observable": {"comment_required": True},
            },
            "home-duct-primary-location": {
                "Not Observable": {"comment_required": True},
            },
            "home-primary-cooling": {
                "Not Observable": {"comment_required": True},
            },
            "home-thermostat-type": {
                "Not Observable": {"comment_required": True},
            },
            "home-ventilation-type": {
                "Not Observable": {"comment_required": True},
            },
            "home-primary-hot-water-type": {
                "Other": {"comment_required": True},
                "Not Observable": {"comment_required": True},
            },
            "renewable-energy-system": {
                "Not Observable": {"comment_required": True},
            },
            "above-code-participation": {
                "Other": {"comment_required": True},
            },
        },
    }

    instrument_conditions = {
        "default": {
            "instrument": {
                "permit-docs-available": {
                    "Yes": [
                        "permit-date",
                    ]
                },
                "home-foundation-type": {
                    ("one", ("Slab on Grade", "Below Grade Slab")): [
                        "home-foundation-r-value",
                    ],
                    "Slab on Grade": ["home-foundation-slab-depth"],
                },
                "home-floors-observed": {
                    "Yes": ["home-floor-r-value", "home-floor-joist-depth"],
                },
                "home-below-grade-walls-observed": {
                    "Yes": [
                        "home-below-grade-walls-ext-r-value",
                        "home-below-grade-walls-int-r-value",
                        "home-below-grade-walls-cavity-r-value",
                        "meets-wa-code-qty-below-grade-wall",
                        "home-below-grade-insulation-grade",
                    ]
                },
                "home-above-grade-walls-observed": {
                    "Yes": [
                        "home-above-grade-walls-continuous-ins-r-value",
                        "home-above-grade-walls-cavity-r-value",
                        "home-above-grade-walls-insulation-grade",
                        "meets-wa-code-above-grade-wall-requirements",
                    ]
                },
                "home-windows-observed": {
                    "Yes": [
                        "home-window-u-value",
                        "home-window-shgc",
                    ]
                },
                "home-ceiling-observed": {
                    "Yes": [
                        "home-ceiling-type",
                        "home-ceiling-r-value",
                        "home-ceiling-framing-details",
                        "meets-wa-code-ceiling-requirements",
                    ]
                },
                "home-infiltration-observed": {
                    "Yes": ["home-infiltration-cfm", "home-infiltration-ach"]
                },
                "home-lighting-observed": {
                    "Yes": [
                        "home-lighting-meets-efficacy",
                        "home-recessed-lighting",
                    ]
                },
                "home-recessed-lighting": {"Yes": ["home-recessed-lighting-rated"]},
                "home-bathroom-fan-observed": {
                    "Yes": ["home-bathroom-fan-cfm", "home-bathroom-fan-efficacy"]
                },
                "home-primary-heating": {
                    ("one", ("Air Source Heat Pump", "Gas Furnace")): [
                        "home-primary-heating-has-ecm",
                        "home-duct-primary-location",
                    ],
                    (
                        "one",
                        ("Ductless Heat Pump", "Ductless Heat Pump with Electric Resistance"),
                    ): [
                        "home-ductless-hp-hspf",
                        "home-ductless-hp-expected-capacity",
                        "home-ductless-hp-installed-capacity",
                        "home-ductless-hp-qty-heads",
                    ],
                    "Air Source Heat Pump": [
                        "home-ashp-lock-out-temp",
                        "home-ashp-hspf",
                        "home-ashp-expected-capacity",
                        "home-ashp-installed-capacity",
                    ],
                    "Gas Furnace": [
                        "home-furnace-afue",
                    ],
                    "Gas Boiler": [
                        "home-boiler-afue",
                    ],
                    "Ground Source Heat Pump": [
                        "home-gshp-cop",
                    ],
                    "Ductless Heat Pump with Electric Resistance": [
                        "home-ductless-hp-ele-resistance-watts",
                        "home-ductless-hp-ele-resistance-serving-largest-zone",
                    ],
                },
                "home-duct-primary-location": {
                    ("one", ("Conditioned Space", "Attic", "Crawlspace")): [
                        "home-duct-r-value",
                        "home-duct-leakage-with-air-handler",
                        "home-duct-leakage-without-air-handler",
                        "home-duct-builder-test",
                    ],
                    "Conditioned Space": [
                        "meets-wa-code-duct-requirements",
                    ],
                },
                "home-primary-cooling": {
                    ("one", ("Air Conditioner", "Air Source Heat Pump", "Ductless Heat Pump")): [
                        "home-primary-cooling-seer",
                        "home-primary-cooling-brand",
                    ],
                },
                "home-ventilation-type": {
                    "High Efficiency Fan": [
                        "home-ventilation-fan-rating",
                    ],
                    "HRV": [
                        "home-ventilation-sensible-heat-recovery-rating",
                        "home-ventilation-hrv-brand",
                    ],
                    "Supply": [
                        "home-ventilation-fan-wired-damper",
                    ],
                    "Exhaust": [
                        "home-ventilation-exhaust-brand",
                    ],
                },
                "home-primary-hot-water-type": {
                    (
                        "one",
                        (
                            "Electric conventional",
                            "Gas conventional",
                            "Heat Pump Water Heater",
                            "Gas Tankless",
                            "Ground Source Heat Pump",
                            "Propane conventional",
                            "Propane Tankless",
                            "Solar",
                        ),
                    ): [
                        "home-primary-hot-water-pipe-r-value",
                        "home-primary-hot-water-location",
                    ],
                    (
                        "one",
                        (
                            "Gas conventional",
                            "Propane conventional",
                            "Propane Tankless",
                            "Gas Tankless",
                        ),
                    ): [
                        "home-primary-hot-water-gas-ef",
                    ],
                    ("one", ("Electric conventional", "Heat Pump Water Heater")): [
                        "home-primary-hot-water-r10-board",
                    ],
                    (
                        "one",
                        (
                            "Electric conventional",
                            "Gas conventional",
                            "Heat Pump Water Heater",
                            "Propane conventional",
                            "Solar",
                        ),
                    ): [
                        "home-primary-hot-water-tank-size",
                    ],
                    "Heat Pump Water Heater": [
                        "home-primary-hot-water-hp-ef",
                        "meets-neea-hp-requirements",
                    ],
                    "Electric conventional": ["home-primary-hot-water-ele-ef"],
                    "Solar": [
                        "meets-wa-code-solar-water-requirements",
                    ],
                },
                "home-primary-hot-water-location": {
                    "Unconditioned Space": [
                        "home-primary-hot-water-r10-board",
                    ]
                },
                "hot-water-recirculation-pump": {
                    "Yes": [
                        "hot-water-recirculation-pump-type",
                    ]
                },
                "drain-water-heat-recovery-system": {
                    "Yes": [
                        "meets-wa-code-drain-water-requirements",
                    ]
                },
                "renewable-energy-system": {
                    "Solar PV": ["meets-wa-code-energy-credit-option"],
                    "Wind": ["meets-wa-code-energy-credit-option"],
                },
            },
        },
    }

    optional_measures = [
        "home-skylight-u-value",
        "showerhead-flow-rate",
        "kitchen-faucet-flow-rate",
        "bathroom-faucet-flow-rate",
        "hot-water-recirculation-pump",
        "hot-water-recirculation-pump-type",
        "drain-water-heat-recovery-system",
        "meets-wa-code-drain-water-requirements",
        "ev-charging",
        "energy-storage",
        "above-code-participation",
    ]

    annotations = OrderedDict(
        (
            (
                "dwelling-type",
                {
                    "name": "Dwelling Type",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_DWELLING_TYPES),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-envelope",
                {
                    "name": "1. Building Envelope Type",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_BUILDING_ENVELOPE_TYPES),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-air-leakage",
                {
                    "name": "2. Air Leakage Control & Efficient Ventilation",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_AIR_LEAKAGE),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-hvac",
                {
                    "name": "3. High Efficiency HVAC",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_BUILDING_HVAC),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-hvac-distribution",
                {
                    "name": "4. High Efficiency HVAC Distribution",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_BUILDING_HVAC_DISTRIBUTION),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-water-heating-5a",
                {
                    "name": "5a.  Efficient Water Heating 5a",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_BUILDING_WATER_HEATING_5A),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-water-heating-5bc",
                {
                    "name": "5b/c.  Efficient Water Heating",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_BUILDING_WATER_HEATING_5BC),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-water-heating-5d",
                {
                    "name": "5d.  Efficient Water Heating",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_BUILDING_WATER_HEATING_5D),
                    "is_required": True,
                },
            ),
            (
                "efficient-building-renewable-energy",
                {
                    "name": "6. Renewable Electric Energy",
                    "description": "Enter the number of 1200 kWh systems",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": ",".join(WA_CODE_QTY_RENEWABLE_ENERGY),
                    "is_required": True,
                },
            ),
            (
                "wa-code-study-score",
                {
                    "name": "WA Code Study Score",
                    "data_type": "float",
                    "is_required": False,
                },
            ),
        )
    )

    def build_program(self):
        """Build out our program"""
        from axis.company.models import Company
        from axis.qa.models import QARequirement
        from axis.relationship.models import Relationship
        from axis.company.models import SponsorPreferences
        from axis.core.tests.factories import rater_admin_factory, qa_admin_factory

        neea = Company.objects.get(slug="neea")
        co_fields = [k.name for k in neea._meta.fields]
        exclude = ["id", "name", "slug", "group"]
        defaults = {"company__%s" % k: getattr(neea, k) for k in co_fields if k not in exclude}
        defaults["company__counties"] = neea.counties.all()
        defaults["company__is_eep_sponsor"] = False
        defaults["company__is_customer"] = False

        user_data = {
            "username": "wa-code-study-rater",
            "first_name": "Skittish",
            "last_name": "Skip",
            "email": "skip@neea.com",
            "title": "Head Chief",
            "department": "Facilities",
            "is_approved": True,
        }

        build_rels = False
        if not Company.objects.filter(slug="wa-code-study-rater").exists():
            neea_rater = defaults.copy()
            neea_rater["company__slug"] = "wa-code-study-rater"
            neea_rater["company__name"] = "WA Code Study Rater"
            neea_rater.update(**user_data)
            rater_admin_factory(**neea_rater)
            build_rels = True
        rater_company = Company.objects.get(slug="wa-code-study-rater")

        if not Company.objects.filter(slug="wa-code-study-qa").exists():
            neea_qa = defaults.copy()
            neea_qa["company__slug"] = "wa-code-study-qa"
            neea_qa["company__name"] = "WA Code Study QA"
            neea_qa.update(**user_data)
            neea_qa["username"] = "wa-code-study-qa"
            neea_qa["first_name"] = "Buckaroo"
            neea_qa["last_name"] = "Burke"
            neea_qa["email"] = "Buckaroo@neea.com"
            qa_admin_factory(**neea_qa)
            build_rels = True
        qa_company = Company.objects.get(slug="wa-code-study-qa")

        if build_rels:
            SponsorPreferences.objects.get_or_create(sponsor=neea, sponsored_company=rater_company)
            SponsorPreferences.objects.get_or_create(sponsor=neea, sponsored_company=qa_company)

            rater_company.save()  # Force a perms update
            qa_company.save()  # Force a perms update

            companies = [neea, rater_company, qa_company]
            Relationship.objects.create_mutual_relationships(*companies)
            # for c_type in ['builder', 'hvac', 'utility']:
            #     companies = Company.objects.filter_by_company(neea).filter(company_type=c_type)
            #     for indirect_company in companies:
            #         if indirect_company.company_type != rater_company.company_type:
            #             Relationship.objects.validate_or_create_relations_to_entity(
            #                 indirect_company, rater_company)
            #         if indirect_company.company_type != qa_company.company_type:
            #             Relationship.objects.validate_or_create_relations_to_entity(
            #                 indirect_company, qa_company)
        else:
            # Wipe the relationships per 25068
            # from axis.home.models import EEPProgramHomeStatus
            # from django.contrib.contenttypes.models import ContentType
            #
            # used_companies = []
            # stats = EEPProgramHomeStatus.objects.filter(eep_program__slug='wa-code-study')
            # for stat in stats:
            #     _stats = stat.home.relationships.values_list('company_id', flat=True)
            #     used_companies += list(_stats)
            # ctype = ContentType.objects.get_for_model(Company)
            # Relationship.objects.filter(company=rater_company, content_type=ctype).exclude(
            #     object_id__in=list(set(used_companies))).delete()

            rater_company.save()  # Force a perms update
            qa_company.save()  # Force a perms update
            for company in [qa_company, rater_company]:
                user = company.users.first()
                user.is_company_admin = True
                user.save()

        program = super(WACodeStudy, self).build_program()
        certifier = Company.objects.get(slug=self.CERTIFIER_SLUG)
        program.certifiable_by.clear()
        program.certifiable_by.add(certifier)
        qa_requirement, _ = QARequirement.objects.get_or_create(
            qa_company=qa_company, eep_program=program, type="file"
        )
        qa_requirement.coverage_pct = 100
        qa_requirement.gate_certification = True
        qa_requirement.save()

        # print('./manage.py set_permissions -c %s' % rater_company.id)
        # print('./manage.py set_permissions -c %s' % qa_company.id)

        return program
