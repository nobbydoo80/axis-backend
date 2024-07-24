"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "08/26/2021 18:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from collections import OrderedDict

from axis.eep_program.program_builder import ProgramBuilder
from axis.remrate_data import strings as rem_strings

import datetime


def val(rem_item_strings, label):
    return {v: k for k, v in rem_item_strings}[label]


class Eto2019(ProgramBuilder):
    name = "Energy Trust Oregon - 2019"
    slug = "eto-2019"
    owner = "eto"
    is_qa_program = False
    opt_in = False
    workflow_default_settings = {}
    min_hers_score = 0
    max_hers_score = 100
    per_point_adder = 0.0
    builder_incentive_dollar_value = 0.0
    rater_incentive_dollar_value = 0.0
    enable_standard_disclosure = False
    require_floorplan_approval = False
    require_input_data = True
    require_rem_data = True
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = True
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2018, 11, 1)
    start_date = datetime.date(2019, 1, 1)
    close_date = datetime.date(2020, 2, 9)
    submit_date = datetime.date(2020, 2, 9)
    end_date = datetime.date(2021, 1, 1)

    comment = """Energy Trust of Oregon 2019 Program"""

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": False,
    }

    measures = {
        "rater": {
            "default": [
                "is-affordable-housing",
                "is-adu",
                "builder-payment-redirected",
                # Solar
                "applicable-solar-incentive",
                "has-solar-pv",
                "ets-annual-etsa-kwh",
                "non-ets-annual-pv-watts",
                "non-ets-dc-capacity-installed",
                "non-ets-installer",
                "non-ets-pv-panels-brand",
                "non-ets-inverter-brand",
                "non-ets-tsrf",
                "smart-thermostat-brand",
                "has-battery-storage",
                "has-solar-water-heat",
                "has-bathroom-electric-resistance-heater",
                "ceiling-r-value",
                # Equipment
                "primary-heating-equipment-type",
                "mini-split-indoor-heads-quantity",
                "equipment-heat-pump",
                "equipment-furnace",
                "equipment-heating-other-type",
                "equipment-heating-other-brand",
                "equipment-heating-other-model-number",
                "equipment-air-conditioner-brand",
                "equipment-air-conditioner-model-number-outdoor",
                "equipment-air-conditioner-model-number-indoor",
                "equipment-water-heater",
                "equipment-heat-pump-water-heater-serial-number",
                "equipment-ventilation-balanced",
                "equipment-ventilation-exhaust",
                "equipment-refrigerator",
                "equipment-dishwasher",
                "equipment-clothes-washer",
                "equipment-clothes-dryer",
                # Notes
                "inspection-notes",
            ],
        },
        "qa": [
            (
                "QA Inspection Details",
                [
                    "inspection-inspector",
                    "inspection-date",
                    "inspection-confidence",
                    "insulation-company",
                ],
            ),
            (
                "General Information",
                [
                    "conditioned-space-area",
                    "conditioned-space-volume",
                    "bedrooms-quantity",
                    "floors-quantity",
                    "foundation-type",
                ],
            ),
            (
                "EPS Information",
                [
                    "is-adu",
                    "applicable-solar-incentive",
                    "has-solar-pv",
                    "has-battery-storage",
                    "has-solar-water-heat",
                    "smart-thermostat-brand",
                ],
            ),
            (
                "Heating Equipment",
                [
                    "primary-heating-equipment-type",
                    "equipment-heat-pump",
                    "equipment-furnace",
                    "equipment-heating-other-type",
                    "equipment-heating-other-brand",
                    "equipment-heating-other-model-number",
                    "ecm-present",
                ],
            ),
            (
                "Water Heating Equipment",
                [
                    "equipment-water-heater",
                    "equipment-water-heater-recirculation-pump",
                    "equipment-water-heater-drain-water-heat-recovery",
                ],
            ),
            (
                "Ventilation",
                [
                    "zonal-pressure",
                    "ventilation-whole-house-type",
                    "ventilation-compliance",
                    "equipment-ventilation-balanced",
                    "equipment-ventilation-exhaust",
                    "equipment-ventilation-sone-spot-rating1",
                    "equipment-ventilation-sone-spot-rating2",
                    "equipment-ventilation-sone-spot-rating3",
                    "mechanical-whole-house-exhaust-fan-flow-location",
                    "mechanical-whole-house-exhaust-fan-flow-rate",
                    "mechanical-whole-house-exhaust-fan-sone-spot-rating",
                ],
            ),
            (
                "Envelope/Insulation",
                [
                    "insulation-grade-1-installation",
                    "thermal-enclosure-checklist",
                    "window-u-factor",
                    "ceiling-insulation-type",
                    "ceiling-r-value",
                    "intermediate-advanced-framing",
                    "above-grade-wall-insulation-type",
                    "above-grade-wall-insulation-r-value",
                    "crawlspace-insulation-type",
                    "crawlspace-insulation-r-value",
                    "rim-joist-insulation-r-value",
                ],
            ),
            (
                "Duct/Air Leakage",
                [
                    "ducts-testing-protocol",
                    "ducts-sealed-mastic",
                    "ducts-fastened-nylon-draw-bands",
                    "duct-type-duct-r-value",
                    "duct-leakage-cfm50",
                    "ducts-percent-inside",
                    "air-handler-testing-installed",
                    "blower-door-cfm",
                    "blower-door-ach-50pa",
                ],
            ),
            (
                "Lighting & Appliances",
                [
                    "lighting-led-pct",
                    "refrigerator-annual-kwh",
                    "dishwasher-annual-kwh",
                    "clothes-washer-imef",
                    "dryer-cef",
                    "fireplace-model-number",
                    "fireplace-venting-type",
                ],
            ),
            (
                "QA Inspection Notes",
                [
                    "inspection-notes",
                ],
            ),
        ],
    }
    texts = {
        "rater": {
            "is-affordable-housing": "Is this affordable housing?",
            "is-adu": "Is this an Accessory Dwelling Unit (ADU)?",
            "builder-payment-redirected": "Does the builder wish to re-direct its payment for the EPS Whole Home "
            "incentive? If so, enter the contact name and payee company for the redirect.",
            "applicable-solar-incentive": "Does this home qualify as solar-ready?",
            "has-solar-pv": "Does the home have solar (PV)?",
            "ets-annual-etsa-kwh": "What is the annual kWh generation as per the Energy Trust Solar "
            "Application? (Check with builder/solar trade ally for 221R)",
            "non-ets-annual-pv-watts": "What is the annual kWh generation as per PV Watts? (Upload PV Watts report)",
            "non-ets-dc-capacity-installed": "What is the total installed kWdc capacity?",
            "non-ets-installer": "Who is the installer?",
            "non-ets-pv-panels-brand": "What brand are the PV panels?",
            "non-ets-inverter-brand": "What brand is the inverter?",
            "non-ets-tsrf": "What is the Total Solar Resource Fraction (TSRF)?",
            "smart-thermostat-brand": "Does this home have a smart thermostat?",
            "has-battery-storage": "Does this home have battery storage?",
            "has-solar-water-heat": "Does this home have Solar water heat?",
            "has-bathroom-electric-resistance-heater": "Does the bathroom have a dedicated electric resistance heater?",
            "ceiling-r-value": "Ceiling R-value",
            "primary-heating-equipment-type": "Select the Primary Heating Equipment Type",
            "mini-split-indoor-heads-quantity": "Number of mini-split heat pump indoor heads",
            "equipment-heat-pump": "Select the heat pump used for space conditioning",
            "equipment-furnace": "Select the furnace",
            "equipment-heating-other-type": "Enter heating equipment type",
            "equipment-heating-other-brand": "Enter heating equipment brand",
            "equipment-heating-other-model-number": "Enter heating equipment model number",
            "equipment-air-conditioner-brand": "Air conditioner brand",
            "equipment-air-conditioner-model-number-outdoor": "Air conditioner outdoor model number",
            "equipment-air-conditioner-model-number-indoor": "Air condition indoor model number",
            "equipment-water-heater": "Select the water heater",
            "equipment-heat-pump-water-heater-serial-number": "Heat Pump Water Heater Serial Number",
            "equipment-ventilation-balanced": "Select the Balanced Ventilation",
            "equipment-ventilation-exhaust": "Select the exhaust only ventilation",
            "equipment-refrigerator": "Select the Refrigerator",
            "equipment-dishwasher": "Select the Dishwasher",
            "equipment-clothes-washer": "Select the Clothes Washer",
            "equipment-clothes-dryer": "Select the Clothes Dryer",
            "inspection-notes": "Notes",
        },
        "qa": {
            "inspection-inspector": "QA Inspector",
            "inspection-date": "QA Inspection Date",
            "inspection-confidence": "Rough/Final",
            "insulation-company": "Insulation Company",
            "conditioned-space-area": "Area of Conditioned Space",
            "conditioned-space-volume": "Volume of Conditioned Space",
            "bedrooms-quantity": "Number of Bedrooms",
            "floors-quantity": "Number of Floors",
            "foundation-type": "Foundation Type",
            "is-adu": "Is this an accessory dwelling unit (ADU)?",
            "applicable-solar-incentive": "Does this home qualify as solar-ready?",
            "has-solar-pv": "Does the home have solar (PV)?",
            "has-battery-storage": "Does this home have battery storage?",
            "has-solar-water-heat": "Does this home have Solar water heat?",
            "smart-thermostat-brand": "Does this home have a smart thermostat?",
            "primary-heating-equipment-type": "Select the Primary Heating Equipment Type",
            "equipment-heat-pump": "Select the heat pump used for space conditioning ",
            "equipment-furnace": "Select the furnace",
            "equipment-heating-other-type": "Enter heating equipment type",
            "equipment-heating-other-brand": "Enter heating equipment brand",
            "equipment-heating-other-model-number": "Enter heating equipment model number",
            "ecm-present": "ECM present",
            "equipment-water-heater": "Select the water heater",
            "equipment-water-heater-recirculation-pump": "Recirculation Pump",
            "equipment-water-heater-drain-water-heat-recovery": "Drain Water Heat Recovery",
            "zonal-pressure": "Zonal Pressure",
            "ventilation-whole-house-type": "Whole House Ventilation Type",
            "ventilation-compliance": "Ventilation Compliance",
            "equipment-ventilation-balanced": "Select the balanced ventilation",
            "equipment-ventilation-exhaust": "Select the exhaust only ventilation",
            "equipment-ventilation-sone-spot-rating1": "Spot Ventilation Sone Rating",
            "equipment-ventilation-sone-spot-rating2": "Spot Ventilation Sone Rating",
            "equipment-ventilation-sone-spot-rating3": "Spot Ventilation Sone Rating",
            "mechanical-whole-house-exhaust-fan-flow-location": "Mechanical Whole House Exhaust Fan Flow Location",
            "mechanical-whole-house-exhaust-fan-flow-rate": "Mechanical Whole House Exhaust Fan Flow Rate",
            "mechanical-whole-house-exhaust-fan-sone-spot-rating": "Mechanical Whole House Exhaust Fan Sone Rating",
            "insulation-grade-1-installation": "Grade 1 Insulation Installation",
            "thermal-enclosure-checklist": "Thermal Enclosure Checklist",
            "window-u-factor": "Window U-factor",
            "ceiling-insulation-type": "Ceiling Insulation Type",
            "ceiling-r-value": "Ceiling Insulation R-value",
            "intermediate-advanced-framing": "Intermediate/Advanced Framing",
            "above-grade-wall-insulation-type": "Above Grade Wall Insulation Type",
            "above-grade-wall-insulation-r-value": "Above Grade Wall Insulation R-value",
            "crawlspace-insulation-type": "Crawlspace Insulation Type",
            "crawlspace-insulation-r-value": "Crawlspace Insulation R-value",
            "rim-joist-insulation-r-value": "Rim Joist Insulation R-value",
            "ducts-testing-protocol": "Ducts- Testing Protocol",
            "ducts-sealed-mastic": "Ducts- Sealed with Mastic",
            "ducts-fastened-nylon-draw-bands": "Ducts- Fastened w/ Nylon Draw-Bands",
            "duct-type-duct-r-value": "Duct Type and R-value",
            "duct-leakage-cfm50": "Duct Leakage @ CFM50",
            "ducts-percent-inside": "Ducts- Percent Inside",
            "air-handler-testing-installed": "Air Handler Installed at Testing",
            "blower-door-cfm": "Blower Door CFM",
            "blower-door-ach-50pa": "Blower Door ACH @ 50Pa",
            "lighting-led-pct": "Lighting % LED",
            "refrigerator-annual-kwh": "Refrigerator kWh/year",
            "dishwasher-annual-kwh": "Dishwasher kWh/year",
            "clothes-washer-imef": "Clothes Washer IMEF",
            "dryer-cef": "Dryer CEF",
            "fireplace-model-number": "Fireplace Model #",
            "fireplace-venting-type": "Fireplace Venting Type",
            "inspection-notes": "QA Inspection Notes",
        },
    }
    descriptions = {
        "default": {
            "ets-annual-etsa-kwh": "If receiving solar incentive from Energy Trust",
            "non-ets-annual-pv-watts": "If not receiving solar incentive from Energy Trust",
            "non-ets-dc-capacity-installed": "If not receiving solar incentive from Energy Trust",
            "non-ets-installer": "If not receiving solar incentive from Energy Trust",
            "non-ets-pv-panels-brand": "If not receiving solar incentive from Energy Trust",
            "non-ets-inverter-brand": "If not receiving solar incentive from Energy Trust",
            "non-ets-tsrf": "If not receiving solar incentive from Energy Trust",
            "mini-split-indoor-heads-quantity": "If primary heating equipment is a mini-split",
            "equipment-heat-pump": "If model includes either a conventional heat pump or mini-splits",
            "equipment-furnace": "If model includes forced air gas furnace",
            "equipment-heating-other-type": "If model includes a heating system apart from a heat pump/furnace",
            "equipment-heating-other-brand": "If model includes a heating system apart from a heat pump/furnace",
            "equipment-heating-other-model-number": "If model includes a heating system apart from a heat pump/furnace",
            "equipment-air-conditioner-brand": "If model includes air conditioner with SEER > 13",
            "equipment-air-conditioner-model-number-outdoor": "If model includes air conditioner with SEER > 13",
            "equipment-air-conditioner-model-number-indoor": "If model includes air conditioner with SEER > 13",
            "equipment-heat-pump-water-heater-serial-number": "If model includes heat pump water heater",
            "equipment-ventilation-balanced": "If model includes balanced ventilation",
            "equipment-ventilation-exhaust": "If model includes exhaust only ventilation",
            "equipment-refrigerator": "If refrigerator's consumption < 691 kWh/yr",
            "equipment-dishwasher": "If dishwasher's consumption < 270 kWh/yr",
            "equipment-clothes-washer": "If clothes washer's iMEF > .807",
            "equipment-clothes-dryer": "If clothes dryer's CEF > 2.62",
        },
        "qa": {},
    }
    suggested_responses = {
        # noqa
        "default": {
            ("Yes", "No"): [
                "is-affordable-housing",
                "is-adu",
                "builder-payment-redirected",
                "applicable-solar-incentive",
                "has-battery-storage",
                "has-solar-water-heat",
            ],
            ("Yes", "No", "N/A"): [
                "has-bathroom-electric-resistance-heater",
            ],
            ("Yes, Energy Trust Solar", "Yes, Non-Energy Trust Solar", "No Solar"): [
                "has-solar-pv",
            ],
            (
                "N/A",
                "Bryant Housewise WiFi model T6-WEM01-A",
                "Carrier Cor WiFi model T6-WEM01-A",
                "Ecobee3 (not 'lite')",
                "Ecobee4",
                "NEST Learning Thermostat",
                "NEST Thermostat E",
            ): [
                "smart-thermostat-brand",
            ],
            (
                "Gas Fireplace",
                "Gas Unit Heater",
                "Gas Furnace",
                "Gas Boiler",
                "Electric Heat Pump \u2013 Air Source Ducted",
                "Electric Heat Pump \u2013 Mini Split Non-Ducted",
                "Electric Heat Pump \u2013 Mini Split Ducted",
                "Electric Heat Pump \u2013 Mini Split Mixed Ducted and Non-Ducted",
                "Electric Heat Pump \u2013 Ground Source",
                "Electric Resistance",
                "Other Gas",
                "Other Electric",
                "Dual Fuel Heat Pump",
            ): [
                "primary-heating-equipment-type",
            ],
            (
                "Gas Fireplace",
                "Gas Unit Heater",
                "Gas Boiler",
                "Electric Heat Pump \u2013 Ground Source",
                "Electric Resistance",
                "Other Gas",
                "Other Electric",
            ): [
                "equipment-heating-other-type",
            ],
        },
        "qa": {
            ("Rough", "Final"): [
                "inspection-confidence",
            ],
            (
                "Slab",
                "Open crawl space/raised floor",
                "Enclosed crawl space",
                "Conditioned crawl space",
                "Conditioned basement",
                "Unconditioned basement",
                "More than one type",
                "Apartment above conditioned space",
                "None",
            ): [
                "foundation-type",
            ],
            ("Yes", "No"): [
                "ecm-present",
                "intermediate-advanced-framing",
                "air-handler-testing-installed",
            ],
            ("Supply", "Exhaust", "HRV", "ERV", "Other"): [
                "ventilation-whole-house-type",
            ],
            ("Supply w/ Control", "Exhause w/ Control", "HRV", "ERV"): [
                "ventilation-compliance",
            ],
            ("Bathroom", "Laundry Room", "Other"): [
                "mechanical-whole-house-exhaust-fan-flow-location",
            ],
            ("Pass", "Correction Required"): [
                "insulation-grade-1-installation",
                "thermal-enclosure-checklist",
                "ducts-sealed-mastic",
                "ducts-fastened-nylon-draw-bands",
                "zonal-pressure",
            ],
            ("Total Leakage to Outside", "Total Leakage"): [
                "ducts-testing-protocol",
            ],
        },
    }
    instrument_types = {
        "integer": [
            "ets-annual-etsa-kwh",
            "non-ets-annual-pv-watts",
            "conditioned-space-area",
            "conditioned-space-volume",
            "bedrooms-quantity",
            "floors-quantity",
            "above-grade-wall-insulation-r-value",
            "crawlspace-insulation-r-value",
            "rim-joist-insulation-r-value",
            "duct-leakage-cfm50",
            "ducts-percent-inside",
            "blower-door-cfm",
            "lighting-led-pct",
            "refrigerator-annual-kwh",
            "dishwasher-annual-kwh",
        ],
        "float": [
            "window-u-factor",
            "blower-door-ach-50pa",
            "clothes-washer-imef",
            "dryer-cef",
        ],
        "cascading-select": [
            "equipment-furnace",
            "equipment-heat-pump",
            "equipment-water-heater",
            "equipment-refrigerator",
            "equipment-dishwasher",
            "equipment-clothes-washer",
            "equipment-clothes-dryer",
            "equipment-ventilation-balanced",
            "equipment-ventilation-exhaust",
        ],
    }
    conditions = {
        "default": {
            "instrument": {
                "applicable-solar-incentive": {
                    "No": [
                        "has-solar-pv",
                    ],
                },
            },
        },
        "rater": {
            "instrument": {
                "has-solar-pv": {
                    "Yes, Energy Trust Solar": [
                        "ets-annual-etsa-kwh",
                    ],
                    "Yes, Non-Energy Trust Solar": [
                        "non-ets-annual-pv-watts",
                        "non-ets-dc-capacity-installed",
                        "non-ets-installer",
                        "non-ets-pv-panels-brand",
                        "non-ets-inverter-brand",
                        "non-ets-tsrf",
                    ],
                },
                "builder-payment-redirected": {
                    "Yes": {"comment": True},
                },
                "primary-heating-equipment-type": {
                    (
                        "one",
                        (
                            "Electric Heat Pump \u2013 Mini Split Non-Ducted",
                            "Electric Heat Pump \u2013 Mini Split Ducted",
                        ),
                    ): [
                        "mini-split-indoor-heads-quantity",
                    ],
                },
            },
            "rem": {
                "floorplan.remrate_target.hotwaterheater_set.type": {
                    val(rem_strings.H2O_HEATER_TYPES, "Heat pump"): [
                        "equipment-heat-pump-water-heater-serial-number",
                    ],
                },
                "floorplan.remrate_target.heater_set.fuel_type": {
                    val(rem_strings.FUEL_TYPES, "Natural gas"): [
                        "equipment-furnace",
                    ],
                },
                "floorplan.remrate_target.heater_set.type": {
                    val(rem_strings.HEATER_TYPES, "Fuel-fired air distribution"): [
                        "equipment-furnace",
                    ],
                },
                "floorplan.has_air_source_heat_pump": {
                    True: [
                        "equipment-heat-pump",
                    ],
                },
                "floorplan.has_non_air_source_heat_pump_heating": {
                    True: [
                        "equipment-heating-other-type",
                        "equipment-heating-other-brand",
                        "equipment-heating-other-model-number",
                    ],
                },
                "floorplan.remrate_target.airconditioner_set.type": {
                    val(rem_strings.COOLING_TYPES, "Air conditioner"): [
                        "equipment-air-conditioner-brand",
                        "equipment-air-conditioner-model-number-outdoor",
                        "equipment-air-conditioner-model-number-indoor",
                    ],
                },
                "floorplan.remrate_target.airconditioner_set.efficiency_unit": {
                    val(rem_strings.COOLING_EFF_UNITS, "SEER"): [
                        "equipment-air-conditioner-brand",
                        "equipment-air-conditioner-model-number-outdoor",
                        "equipment-air-conditioner-model-number-indoor",
                    ],
                },
                "floorplan.remrate_target.airconditioner_set.efficiency": {
                    (">", 13): [
                        "equipment-air-conditioner-brand",
                        "equipment-air-conditioner-model-number-outdoor",
                        "equipment-air-conditioner-model-number-indoor",
                    ],
                },
                "floorplan.remrate_target.infiltration.mechanical_vent_type": {
                    ("contains", val(rem_strings.INFILTRATION_TYPES, "Balanced")): [
                        "equipment-ventilation-balanced",
                    ],
                    ("contains", val(rem_strings.INFILTRATION_TYPES, "Exhaust Only")): [
                        "equipment-ventilation-exhaust",
                    ],
                },
                "floorplan.remrate_target.lightsandappliance.refrigerator_kw_yr": {
                    ("<", 691): [
                        "equipment-refrigerator",
                    ],
                },
                "floorplan.remrate_target.lightsandappliance.dishwasher_kw_yr": {
                    ("<", 270): [
                        "equipment-dishwasher",
                    ],
                },
                # This is a missing field from all REM/Rate version exports we know of
                # 'floorplan.remrate_target.lightsandappliance.clothes_washer_imef': {
                #     ('>', 0.807): [
                #         'equipment-clothes-washer',
                #     ],
                # },
                "floorplan.remrate_target.lightsandappliance.clothes_washer_label_energy_rating": {
                    ("<", 487): [
                        "equipment-clothes-washer",
                    ],
                },
                "floorplan.remrate_target.lightsandappliance.clothes_dryer_energy_factor": {
                    (">", 2.62): [
                        "equipment-clothes-dryer",
                    ],
                },
            },
        },
        "qa": {},
    }
    optional_measures = [
        "inspection-notes",
    ]

    annotations = OrderedDict(
        (
            (
                "hpxml_gbr_id",
                {"name": "Green Building Registry ID", "data_type": "open", "is_required": False},
            ),
            (
                "home-orientation",
                {
                    "name": "Home Orientation",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "north,northwest,south,southeast,"
                    "east,northeast,west,southwest",
                    "is_required": False,
                },
            ),
        )
    )
