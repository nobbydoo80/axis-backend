"""eto_2021.py - Axis"""

__author__ = "Steven K"
__date__ = "9/8/21 12:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from collections import OrderedDict
from datetime import date

from simulation.enumerations import (
    CoolingSystemType,
    CoolingEfficiencyUnit,
    MechanicalVentilationType,
)

from axis.eep_program.program_builder import ProgramBuilder

from ..enumerations import (
    Fireplace2020,
    PrimaryHeatingEquipment2020,
    GridHarmonization2020,
    SmartThermostatBrands2020,
    AdditionalIncentives2020,
    SolarElements2020,
)

log = logging.getLogger(__name__)

ETO_2021_FUEL_RATES = [
    ("portland-electric", "PGE-Jan2021"),
    ("pacific-power", "PAC-Jan2021"),
    ("central-electric", "CEC-Jan2021"),
    ("utility-city-of-ashland", "Ashland-Jan2021"),
    ("clark-pud", "ClarkPUD-Jan2021"),
    ("utility-umatilla-electric-co-op", "Umatilla-Jan2021"),
    ("utility-cowlitz-county-pud", "CowlitzPUD-Jan2021"),
    ("utility-columbia-basin-electric-co-op", "ColBasinCoop-Jan2021"),
    ("utility-columbia-river-pud", "ColRiverPUD-Jan2021"),
    ("utility-forest-grove-light-department", "ForestGrove-Jan2021"),
    ("utility-eugene-water-electric-board", "EWEB-Jan2021"),
    ("avista", "Avista-Jan2021"),
    ("nw-natural-gas", "NWN_OR-Jan2021"),
    ("cascade-gas", "Cascade-Jan2021"),
    ("utility-clatskanie-pud", "ClatskPUD-Jan2021"),
    ("utility-canby-utility-board", "CanbyPUD-Jan2021"),
    ("utility-columbia-power-co-op", "ColPowerCoop-Jan2021"),
    ("utility-oregon-trail-electric-co-op", "OTEC-Jan2021"),
    ("utility-mcminnville-water-light", "MW&L-Jan2021"),
    ("utility-springfield-utility-board", "SUB-Jan2021"),
    ("utility-klickitat-pud", "KlickitatPUD-Jan2021"),
    ("utility-midstate-electric-cooperative-inc", "MidStateElec-Jan2021"),
]
ETO_2021_FUEL_RATES_WA_OVERRIDE = [
    ("nw-natural-gas", "NWN_WA-Jan2021"),
]


class Eto2021(ProgramBuilder):
    """Program Specs for the ETO-2021"""

    name = "Energy Trust Oregon - 2021"
    comment = "Energy Trust of Oregon 2021 Program"

    slug = "eto-2021"
    owner = "eto"

    viewable_by_company_type = "qa,provider,rater"
    qa_viewable_by_company_type = "qa,provider"

    require_input_data = True
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
    visibility_date = date(year=2020, month=11, day=1)
    start_date = date(year=2021, month=2, day=1)
    close_date = date(year=2022, month=11, day=1)
    submit_date = date(year=2022, month=11, day=15)
    end_date = date(year=2023, month=1, day=1)
    hers_range = [0, 500]

    measures = {
        "rater": {
            "default": [
                "is-adu",
                "builder-payment-redirected",
                "eto-additional-incentives",
                "grid-harmonization-elements",
                # Solar
                "solar-elements",
                "ets-annual-etsa-kwh",
                "non-ets-annual-pv-watts",
                "non-ets-dc-capacity-installed",
                "non-ets-installer",
                "non-ets-pv-panels-brand",
                "non-ets-inverter-brand",
                "non-ets-tsrf",
                "smart-thermostat-brand",
                "has-gas-fireplace",
                "has-battery-storage",
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
                "equipment-gas-tank-water-heater-serial-number",
                "equipment-gas-tankless-water-heater-serial-number",
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
                    "insulation-company",
                    "inspection-inspector",
                    "inspection-date",
                    "inspection-confidence",
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
                    "general-information-comments",
                ],
            ),
            (
                "EPS Information",
                [
                    "is-adu",
                    "has-battery-storage",
                    "electric-vehicle-charger",
                    "smart-thermostat-brand",
                    "eps-additional-incentives",
                    "eps-solar-elements",
                    "grid-harmonization-elements",
                    "eps-comments",
                ],
            ),
            (
                "Heating Equipment",
                [
                    "primary-heating-equipment-type",
                    "equipment-furnace",
                    "equipment-heat-pump",
                    "mini-split-indoor-heads-quantity",
                    "heating-equipment-air-condition-installed",
                    "heating-equipment-air-condition-outdoor-model-number",
                    "heating-equipment-air-condition-indoor-model-number",
                    "equipment-heating-other-type",
                    "equipment-heating-other-brand",
                    "equipment-heating-other-model-number",
                    "heating-equipment-comments",
                ],
            ),
            (
                "Water Heating Equipment",
                [
                    "equipment-water-heater",
                    "equipment-water-heater-serial-number",
                    "equipment-water-heater-recirculation-pump",
                    "equipment-water-heater-drain-water-heat-recovery",
                    "equipment-water-heater-comments",
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
                    "equipment-ventilation-compliance",
                    "mechanical-whole-house-exhaust-fan-flow-location",
                    "mechanical-whole-house-exhaust-fan-flow-rate",
                    "mechanical-whole-house-exhaust-fan-sone-spot-rating",
                    "equipment-ventilation-comments",
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
                    "envelope-comments",
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
                    "duct-supply-in-conditioned-space",
                    "duct-return-in-conditioned-space",
                    "air-handler-testing-installed",
                    "blower-door-cfm",
                    "blower-door-ach-50pa",
                    "duct-comments",
                ],
            ),
            (
                "Lighting & Appliances",
                [
                    "lighting-led-pct",
                    "refrigerator-model-number",
                    "clothes-diswasher-model-number",
                    "clothes-washer-model-number",
                    "clothes-dryer-model-number",
                    "fireplace-model-number",
                    "fireplace-venting-type",
                    "lighting-comments",
                ],
            ),
            (
                "QA Observations/General Notes",
                [
                    "inspection-notes",
                ],
            ),
        ],
    }
    texts = {
        "rater": {
            "is-adu": "Is this an Accessory Dwelling Unit (ADU)?",
            "builder-payment-redirected": "Does the builder wish to re-direct its payment for the EPS Whole Home incentive? "
            "If so, enter the contact name and payee company for the redirect.",
            "eto-additional-incentives": "Does this home qualify for any of the following "
            "additional incentives?",
            "grid-harmonization-elements": "What energy smart homes elements does this home have?",
            "solar-elements": "What solar elements does this home have?",
            "ets-annual-etsa-kwh": "What is the annual kWh generation as per the Energy Trust solar application? "
            "(Check with builder/solar trade ally)",
            "non-ets-annual-pv-watts": "What is the annual kWh generation as per PV Watts? (Upload PV Watts report)",
            "non-ets-dc-capacity-installed": "What is the total installed kWdc capacity?",
            "non-ets-installer": "Who is the installer?",
            "non-ets-pv-panels-brand": "What brand are the PV panels?",
            "non-ets-inverter-brand": "What brand is the inverter?",
            "non-ets-tsrf": "What is the Total Solar Resource Fraction (TSRF)?",
            "smart-thermostat-brand": "Does this home have a smart thermostat?",
            "has-gas-fireplace": "Does the home have a gas fireplace for secondary heating or "
            "decorative purposes, if yes, which efficiency bin?",
            "has-battery-storage": "Does this home have battery storage?",
            "ceiling-r-value": "Ceiling R-value",
            "primary-heating-equipment-type": "Select the Primary Heating Equipment Type",
            "mini-split-indoor-heads-quantity": "Number of mini-split heat pump indoor heads",
            "equipment-heat-pump": "Select the heat pump used for space conditioning",
            "equipment-furnace": "Select the furnace",
            "equipment-heating-other-type": "Enter heating equipment type",
            "equipment-heating-other-brand": "Enter heating equipment brand",
            "equipment-heating-other-model-number": "Enter heating equipment model number(s)",
            "equipment-air-conditioner-brand": "Air conditioner brand",
            "equipment-air-conditioner-model-number-outdoor": "Air conditioner outdoor model number",
            "equipment-air-conditioner-model-number-indoor": "Air conditioner indoor model number",
            "equipment-water-heater": "Select the water heater",
            "equipment-heat-pump-water-heater-serial-number": "Heat Pump Water Heater Serial Number",
            "equipment-ventilation-balanced": "Select the Balanced Ventilation",
            "equipment-ventilation-exhaust": "Select the exhaust only ventilation",
            "equipment-refrigerator": "Select the Refrigerator",
            "equipment-dishwasher": "Select the Dishwasher",
            "equipment-clothes-washer": "Select the Clothes Washer",
            "equipment-clothes-dryer": "Select the Clothes Dryer",
            "equipment-gas-tank-water-heater-serial-number": "Enter gas tank water heater serial number",
            "equipment-gas-tankless-water-heater-serial-number": "Enter gas tankless water heater serial number",
            "inspection-notes": "Notes",
        },
        "qa": {
            "insulation-company": "Insulation Company",
            "inspection-inspector": "QA Inspector",
            "inspection-date": "QA Inspection Date",
            "inspection-confidence": "Rough/Final",
            "conditioned-space-area": "Area of Conditioned Space",
            "conditioned-space-volume": "Volume of Conditioned Space",
            "bedrooms-quantity": "Number of Bedrooms",
            "floors-quantity": "Number of Floors",
            "foundation-type": "Foundation Type",
            "general-information-comments": "Comments",
            "is-adu": "Is this an accessory dwelling unit (ADU)?",
            "has-battery-storage": "Does this home have battery storage?",
            "electric-vehicle-charger": "Does this home have an electric vehicle charger?",
            "smart-thermostat-brand": "Does this home have a smart thermostat?",
            "eps-additional-incentives": "Does this home qualify for any "
            "of the following additional incentives?",
            "eps-solar-elements": "What solar elements does this home have?",
            "grid-harmonization-elements": "What energy smart homes "
            "elements does this home have ?",
            "eps-comments": "Comments",
            "primary-heating-equipment-type": "Select the Primary Heating Equipment Type",
            "equipment-heat-pump": "Select the heat pump used for space conditioning",
            "equipment-furnace": "Select the furnace",
            "mini-split-indoor-heads-quantity": "Number of mini-split heat pump indoor heads",
            "heating-equipment-air-condition-installed": "Does this home have "
            "Air Conditioning installed?",
            "heating-equipment-air-condition-outdoor-model-number": "Air conditioner "
            "outdoor model number",
            "heating-equipment-air-condition-indoor-model-number": "Air conditioner "
            "indoor model number",
            "equipment-heating-other-type": "Enter heating equipment type",
            "equipment-heating-other-brand": "Enter heating equipment brand",
            "equipment-heating-other-model-number": "Enter heating equipment model number(s)",
            "heating-equipment-comments": "Comments",
            "equipment-water-heater": "Select the water heater",
            "equipment-water-heater-serial-number": "Enter the water heater serial number",
            "equipment-water-heater-recirculation-pump": "Recirculation Pump",
            "equipment-water-heater-drain-water-heat-recovery": "Drain Water Heat Recovery",
            "equipment-water-heater-comments": "Comments",
            "zonal-pressure": "Zonal Pressure",
            "ventilation-whole-house-type": "Whole House Ventilation Type",
            "ventilation-compliance": "Ventilation Compliance",
            "equipment-ventilation-balanced": "Select the balanced ventilation",
            "equipment-ventilation-exhaust": "Select the exhaust only ventilation",
            "equipment-ventilation-sone-spot-rating1": "Spot Ventilation 1",
            "equipment-ventilation-sone-spot-rating2": "Spot Ventilation 2",
            "equipment-ventilation-sone-spot-rating3": "Spot Ventilation 3",
            "equipment-ventilation-compliance": "Spot Ventilation Compliance",
            "mechanical-whole-house-exhaust-fan-flow-location": "Mechanical Whole House Exhaust Fan Flow Location",
            "mechanical-whole-house-exhaust-fan-flow-rate": "Mechanical Whole House Exhaust Fan Flow Rate",
            "mechanical-whole-house-exhaust-fan-sone-spot-rating": "Mechanical Whole House Exhaust Fan Sone Rating",
            "equipment-ventilation-comments": "Comments",
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
            "envelope-comments": "Comments",
            "ducts-testing-protocol": "Ducts- Testing Protocol",
            "ducts-sealed-mastic": "Ducts- Sealed with Mastic",
            "ducts-fastened-nylon-draw-bands": "Ducts- Fastened w/ Nylon Draw-Bands",
            "duct-type-duct-r-value": "Duct Type and R-value",
            "duct-leakage-cfm50": "Duct Leakage @ CFM50",
            "duct-supply-in-conditioned-space": "Ducts- % of Supply in Conditioned Space",
            "duct-return-in-conditioned-space": "Ducts- % of Return in Conditioned Space",
            "air-handler-testing-installed": "Air Handler Installed at Testing",
            "blower-door-cfm": "Blower Door CFM",
            "blower-door-ach-50pa": "Blower Door ACH @ 50Pa",
            "duct-comments": "Comments",
            "lighting-led-pct": "Lighting % LED",
            "refrigerator-model-number": "Enter refrigerator model number",
            "clothes-diswasher-model-number": "Enter dishwasher model number",
            "clothes-washer-model-number": "Enter clothes washer model number",
            "clothes-dryer-model-number": "Enter clothes dryer model number",
            "fireplace-model-number": "Fireplace Brand/Model #",
            "fireplace-venting-type": "Fireplace Venting Type",
            "lighting-comments": "Comments",
            "inspection-notes": "Additional Comments",
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
            "equipment-refrigerator": "If refrigerator's consumption < 549 kWh/yr",
            "equipment-dishwasher": "If dishwasher's consumption < 302 kWh/yr, Place setting 12",
            "equipment-clothes-washer": "If clothes washer's iMEF > 2.155, LER 151 kWH/yr, "
            "Capacity > 3.31, Ele Rate > 0.1065, Gas Rate > 1.22, "
            "Ann Cost > 12.0",
            "equipment-clothes-dryer": "If clothes dryer's CEF > 2.8, with Moisture Sensing",
            "duct-supply-in-conditioned-space": "Enter whole number",
            "duct-return-in-conditioned-space": "Enter whole number",
        },
        # 'rater': {},
        "qa": {
            "general-information-comments": "Enter General Information section comments",
            "eps-comments": "Enter EPS Information section comments",
            "mini-split-indoor-heads-quantity": "If primary heating equipment is a mini-split",
            "heating-equipment-air-condition-outdoor-model-number": "Required entry "
            "if AC installed",
            "heating-equipment-air-condition-indoor-model-number": "Required entry if AC installed",
            "heating-equipment-comments": "Enter Heating & Cooling section comments",
            "equipment-water-heater-serial-number": "Required Entry if water heater is installed",
            "equipment-water-heater-comments": "Enter Water Heating Equipment section comments",
            "equipment-ventilation-sone-spot-rating1": "Enter Location, Tested CFM and Sone rating",
            "equipment-ventilation-sone-spot-rating2": "Enter Location, Tested CFM and Sone rating",
            "equipment-ventilation-sone-spot-rating3": "Enter Location, Tested CFM and Sone rating",
            "equipment-ventilation-compliance": "Required Entry",
            "equipment-ventilation-comments": "Enter Ventilation section comments",
            "window-u-factor": "Enter weighted average of inspected/observed window package",
            "ceiling-r-value": "Enter whole number",
            "above-grade-wall-insulation-r-value": "Enter whole number",
            "crawlspace-insulation-r-value": "Enter whole number",
            "rim-joist-insulation-r-value": "Enter whole number",
            "envelope-comments": "Enter Envelope/Insulation section comments",
            "duct-leakage-cfm50": "Enter whole number",
            "blower-door-cfm": "Enter whole number",
            "duct-comments": "Enter Duct/Air Leakage section comments",
            "lighting-led-pct": "Enter whole number",
            "lighting-comments": "Enter Lighting & Appliances section comments",
            "inspection-notes": "Enter observations and discoveries outside of EPS requirements",
        },
    }
    suggested_responses = {
        "default": {
            tuple([x.value for x in AdditionalIncentives2020]): ["eto-additional-incentives"],
            tuple([x.value for x in SolarElements2020]): ["solar-elements"],
            ("Yes", "No"): [
                "is-adu",
                "builder-payment-redirected",
                "has-battery-storage",
            ],
            tuple([x.value for x in Fireplace2020]): [
                "has-gas-fireplace",
            ],
            tuple([x.value for x in PrimaryHeatingEquipment2020]): [
                "primary-heating-equipment-type",
            ],
            (
                PrimaryHeatingEquipment2020.GAS_FIREPLACE.value,
                PrimaryHeatingEquipment2020.GAS_UNIT_HEATER.value,
                PrimaryHeatingEquipment2020.GAS_BOILER.value,
                PrimaryHeatingEquipment2020.GSHP.value,
                PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE.value,
                PrimaryHeatingEquipment2020.OTHER_GAS.value,
                PrimaryHeatingEquipment2020.OTHER_ELECTRIC.value,
                PrimaryHeatingEquipment2020.DFHP.value,
            ): [
                "equipment-heating-other-type",
            ],
        },
        "rater": {
            tuple([x.value for x in SmartThermostatBrands2020]): [
                "smart-thermostat-brand",
            ],
            tuple([x.value for x in GridHarmonization2020]): [
                "grid-harmonization-elements",
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
            (
                "Bryant Housewise WiFi model T6-WEM01-A",
                "Carrier Cor WiFi model T6-WEM01-A",
                "Ecobee3 (not 'lite')",
                "Ecobee4",
                "Ecobee w/ Voice Control",
                "NEST Learning Thermostat",
                "NEST Thermostat E",
                "N/A",
                "Other, add comment",
            ): [
                "smart-thermostat-brand",
            ],
            ("Yes", "No"): [
                "electric-vehicle-charger",
            ],
            ("Yes", "No", "N/A"): [
                "intermediate-advanced-framing",
                "air-handler-testing-installed",
            ],
            ("Yes", "No", "AC ready"): [
                "heating-equipment-air-condition-installed",
            ],
            ("None", "Supply", "Exhaust", "HRV", "ERV", "Other"): [
                "ventilation-whole-house-type",
            ],
            ("Corrections Required", "Supply w/ Control", "Exhaust w/ Control", "HRV", "ERV"): [
                "ventilation-compliance",
            ],
            ("Bathroom", "Laundry Room", "Other"): [
                "mechanical-whole-house-exhaust-fan-flow-location",
            ],
            ("Pass", "Correction Required"): [
                "insulation-grade-1-installation",
                "thermal-enclosure-checklist",
                "zonal-pressure",
                "equipment-ventilation-compliance",
            ],
            ("N/A", "Pass", "Correction Required"): [
                "ducts-sealed-mastic",
                "ducts-fastened-nylon-draw-bands",
            ],
            ("Leakage to Outside", "Total Leakage"): [
                "ducts-testing-protocol",
            ],
            (
                "No",
                "Affordable housing (upload 610L to documents tab)",
                "Solar elements",
                "Energy smart homes (upload solar exemption to documents tab)",
                "Affordable housing and solar elements",
                "Affordable housing and energy smart homes (upload solar exemption to documents tab)",
                "Solar elements and energy smart homes",
                "Affordable housing, energy smart homes and solar elements",
            ): ["eps-additional-incentives"],
            ("Solar Ready", "Solar PV", "None"): ["eps-solar-elements"],
            (
                "Energy smart homes – Base package",
                "Energy smart homes – Base package + storage ready",
                "Energy smart homes – Base package + advanced wiring",
                "Energy smart homes – Base package + storage ready + advanced wiring",
                "None",
            ): [
                "grid-harmonization-elements",
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
            "blower-door-cfm",
            "lighting-led-pct",
            "duct-supply-in-conditioned-space",
            "duct-return-in-conditioned-space",
        ],
        "float": ["window-u-factor", "blower-door-ach-50pa"],
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
    instrument_conditions = {
        "default": {},
        "rater": {
            "instrument": {
                "eto-additional-incentives": {
                    (
                        "one",
                        (
                            "Solar elements",
                            "Affordable housing and solar elements",
                            "Solar elements and energy smart homes",
                            "Affordable housing, energy smart homes and solar elements",
                        ),
                    ): ["solar-elements"],
                    (
                        "one",
                        (
                            "Energy smart homes (upload solar exemption to documents tab)",
                            "Affordable housing and energy smart homes "
                            "(upload solar exemption to documents tab)",
                            "Solar elements and energy smart homes",
                            "Affordable housing, energy smart homes and solar elements",
                        ),
                    ): ["grid-harmonization-elements"],
                },
                "solar-elements": {
                    # If “Solar PV” selected, then: 'ets-annual-etsa-kwh'
                    ("one", ("Solar PV",)): ["ets-annual-etsa-kwh"],
                    # If “Non-Energy Trust Solar PV” selected, then:
                    ("one", ("Non-Energy Trust Solar PV",)): [
                        "non-ets-annual-pv-watts",
                        "non-ets-dc-capacity-installed",
                        "non-ets-installer",
                        "non-ets-pv-panels-brand",
                        "non-ets-inverter-brand",
                        "non-ets-tsrf",
                    ],
                },
                "primary-heating-equipment-type": {
                    (
                        "one",
                        (
                            "Electric Heat Pump \u2013 Mini Split Non-Ducted",
                            "Electric Heat Pump \u2013 Mini Split Ducted",
                            "Electric Heat Pump \u2013 Mini Split Mixed Ducted and Non-Ducted",
                        ),
                    ): [
                        "mini-split-indoor-heads-quantity",
                    ],
                },
            },
            "simulation": {
                "floorplan.simulation.water_heaters.is_heat_pump": {
                    ("one", True): [
                        "equipment-heat-pump-water-heater-serial-number",
                    ],
                },
                "floorplan.simulation.has_gas_forced_air_heating": {
                    ("one", True): [
                        "equipment-furnace",
                    ],
                },
                "floorplan.simulation.water_heaters.is_conventional_gas": {
                    ("one", True): ["equipment-gas-tank-water-heater-serial-number"],
                },
                "floorplan.simulation.water_heaters.is_tankless_gas": {
                    ("one", True): ["equipment-gas-tankless-water-heater-serial-number"],
                },
                "floorplan.simulation.air_source_heat_pumps": {
                    ("any", None): [
                        "equipment-heat-pump",
                    ],
                },
                "floorplan.simulation.non_air_source_heat_pump_heating": {
                    ("any", None): [
                        "equipment-heating-other-type",
                        "equipment-heating-other-brand",
                        "equipment-heating-other-model-number",
                    ],
                },
                "floorplan.simulation.air_conditioners.system_type": {
                    ("one", (CoolingSystemType.AIR_CONDITIONER,)): [
                        "equipment-air-conditioner-brand",
                        "equipment-air-conditioner-model-number-outdoor",
                        "equipment-air-conditioner-model-number-indoor",
                    ],
                },
                "floorplan.simulation.air_conditioners.efficiency_unit": {
                    ("one", CoolingEfficiencyUnit.SEER): [
                        "equipment-air-conditioner-brand",
                        "equipment-air-conditioner-model-number-outdoor",
                        "equipment-air-conditioner-model-number-indoor",
                    ],
                },
                "floorplan.simulation.air_conditioners.efficiency": {
                    (">", 13): [
                        "equipment-air-conditioner-brand",
                        "equipment-air-conditioner-model-number-outdoor",
                        "equipment-air-conditioner-model-number-indoor",
                    ],
                },
                "floorplan.simulation.mechanical_ventilation_systems.type": {
                    (
                        "one",
                        (
                            MechanicalVentilationType.BALANCED,
                            MechanicalVentilationType.HRV,
                            MechanicalVentilationType.ERV,
                        ),
                    ): [
                        "equipment-ventilation-balanced",
                    ],
                    ("one", MechanicalVentilationType.EXHAUST_ONLY): [
                        "equipment-ventilation-exhaust",
                    ],
                },
                "floorplan.simulation.appliances.refrigerator_consumption": {
                    ("<", 549): [
                        "equipment-refrigerator",
                    ],
                },
                "floorplan.simulation.appliances.dishwasher_consumption": {
                    ("<", 302): [
                        "equipment-dishwasher",
                    ],
                },
                "floorplan.simulation.appliances.clothes_washer_efficiency": {
                    (">", 2.155): [
                        "equipment-clothes-washer",
                    ],
                },
                "floorplan.simulation.appliances.clothes_washer_label_electric_consumption": {
                    ("<", 151): [
                        "equipment-clothes-washer",
                    ],
                },
                "floorplan.simulation.appliances.clothes_dryer_efficiency": {
                    (">", 2.8): [
                        "equipment-clothes-dryer",
                    ],
                },
            },
        },
        "qa": {},
    }

    suggested_response_flags = {
        "rater": {
            "builder-payment-redirected": {
                "Yes": {"comment_required": True},
            },
        },
        "default": {
            "smart-thermostat-brand": {
                "Other, add comment": {"comment_required": True},
            },
        },
    }

    optional_measures = [
        "general-information-comments",
        "eps-comments",
        "heating-equipment-comments",
        "equipment-ventilation-comments",
        "envelope-comments",
        "duct-comments",
        "lighting-comments",
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

    def build_program(self):
        """Build out our program"""
        from axis.eep_program.models import EEPProgram
        from axis.company.models import Company
        from axis.qa.models import QARequirement

        # START DELETE ME
        # if not hasattr(self, 'wiped'):
        #     import datetime
        #     from axis.eep_program.models import EEPProgram
        #     slugs = [self.slug + '-qa', self.slug]
        #     EEPProgram.objects.filter(slug__in=slugs).update(collection_request=None)
        #
        #     _date = datetime.date(2020, 2, 25)
        #     from django_input_collection.models import Measure, CollectionRequest, \
        #         CollectionInstrument, CollectionInstrumentType, Case, Condition, CollectionGroup
        #     Measure.objects.filter(date_created__gte=_date).delete()
        #     Case.objects.filter(date_created__gte=_date).delete()
        #     Condition.objects.filter(date_created__gte=_date).delete()
        #     CollectionGroup.objects.filter(date_created__gte=_date).delete()
        #     CollectionInstrumentType.objects.filter(date_created__gte=_date).delete()
        #     CollectionRequest.objects.filter(date_created__gte=_date).delete()
        #     CollectionInstrument.objects.filter(date_created__gte=_date).delete()
        #
        #     from axis.home.models import EEPProgramHomeStatus
        #     EEPProgramHomeStatus.objects.filter(eep_program__slug__in=slugs).delete()
        #     self.wiped = True

        # END DELETE ME

        _program = super(Eto2021, self).build_program()

        program = EEPProgram.objects.get(slug="eto-2021")
        qa_company = Company.objects.get(slug="peci")

        qa_requirement, _ = QARequirement.objects.get_or_create(
            qa_company=qa_company, eep_program=program, type="file"
        )
        qa_requirement.coverage_pct = 100
        qa_requirement.gate_certification = True
        qa_requirement.save()

        qa_requirement, _ = QARequirement.objects.get_or_create(
            qa_company=qa_company, eep_program=program, type="field"
        )
        qa_requirement.coverage_pct = 0
        qa_requirement.gate_certification = True
        qa_requirement.save()

        return _program
