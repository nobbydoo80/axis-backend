"""eto_2022.py - Axis"""

__author__ = "Steven K"
__date__ = "2/23/22 09:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import sys
from collections import OrderedDict
from enum import Enum

from simulation.enumerations import (
    CoolingSystemType,
    CoolingEfficiencyUnit,
    MechanicalSystemType,
)

from axis.customer_eto.eep_programs.fire_rebuild_2021 import FireResilienceBonus
from axis.customer_eto.enumerations import (
    YesNo,
    Fireplace2020,
    PrimaryHeatingEquipment2020,
    CaseInsensitiveEnum,
)
from axis.eep_program.program_builder import ProgramBuilder

log = logging.getLogger(__name__)


class AdditionalElements2022(Enum):
    NO = "No"
    SOLAR = "Solar elements"
    ELECTRIC_CAR = "Electric vehicle elements"
    SOLAR_AND_ELECTRIC_CAR = "Solar and electric vehicle elements"
    SOLAR_AND_STORAGE = "Solar and storage elements"
    ALL = "Solar, electric vehicle and storage elements"


class CobidQualification(Enum):
    NO = "No"
    AFFORDABLE = "Affordable (upload form to documents tab)"
    RURAL = "Rural"
    TRIBAL = "Tribal"
    AFFORDABLE_AND_RURAL = "Affordable (upload form to documents tab) and rural"
    AFFORDABLE_AND_TRIBAL = "Affordable (upload form to documents tab) and tribal"
    RURAL_AND_TRIBAL = "Rural and tribal"
    ALL = "Affordable (upload form to documents tab), rural and tribal"


class CobidRegistered(Enum):
    NO = "No"
    BUILDER = "Builder"
    VERIFIER = "Verifier"
    BOTH = "Builder and Verifier"


class SolarElements2022(Enum):
    SOLAR_READY = "Solar Ready"
    SOLAR_PV = "Energy Trust Solar PV"
    NET_ZERO = "Net zero (Energy Trust Solar PV installed and hosted solar EDA)"
    NON_ETO_SOLAR = "Non-Energy Trust Solar PV"


class ElectricCarElements2022(Enum):
    EV_READY = "Electric vehicle ready"
    EV_INSTALLED = "Electric vehicle charging equipment installed"


class StorageElements2022(Enum):
    STORAGE_READY = "Storage ready (either with solar ready or solar installed)"
    STORAGE_INSTALLED = "Storage installed (either with solar ready or solar installed)"


class SmartThermostatBrands2022(CaseInsensitiveEnum):
    NONE = "N/A"
    BRYANT = "Bryant Housewise WiFi model T6-WEM01-A"
    CARRIER = "Carrier Cor WiFi model T6-WEM01-A"
    ECOBEE3 = "Ecobee3 (not 'lite')"
    ECOBEE4 = "Ecobee4"
    ECOBEE_VOICE = "Ecobee w/ Voice Control"
    NEST = "NEST Thermostat"
    NEST_LEARNING = "NEST Learning Thermostat"
    NEST_E = "NEST Thermostat E"
    OTHER = "Other, add comment"


class MechanicalVentilationSystemTypes(Enum):
    BALANCED_NO_HR = "Balanced Ventilation without Heat Recovery"
    STAND_ALONE = "Stand-alone HRV or ERV"
    INTEGRATED_HRV_ERV = "Central air handler integrated HRV or ERV"
    SPOT = "Spot ERV"
    OTHER = "Other, add comment"
    WA_EXHAUST = "WA - Exhaust Only"
    WA_SUPPLY = "WA - Supply Only"


class BalancedVentilationTypes(Enum):
    INTERMITTENT = (
        "Intermittent central air handler integrated with fan-cycling "
        "controller (Air Cycler (CFIS) Ventilation Type)"
    )
    CONTINUOUS = "Continuously operating central air handler integrated"
    SECONDARY = "Secondary supply fan integrated with central air handler"
    STAND_ALONE = "Stand alone supply fan with exhaust fan"
    OTHER = "Other, add comment"


ETO_2022_FUEL_RATES = [
    ("portland-electric", "PGE-Jan2022"),
    ("pacific-power", "PAC-Jan2022"),
    ("central-electric", "CEC-Jan2022"),
    ("utility-city-of-ashland", "Ashland-Jan2022"),
    ("clark-pud", "ClarkPUD-Jan2022"),
    ("utility-umatilla-electric-co-op", "Umatilla-Jan2022"),
    ("utility-cowlitz-county-pud", "CowlitzPUD-Jan2022"),
    ("utility-columbia-basin-electric-co-op", "ColBasinCoop-Jan2022"),
    ("utility-columbia-river-pud", "ColRiverPUD-Jan2022"),
    ("utility-forest-grove-light-department", "ForestGrove-Jan2022"),
    ("utility-eugene-water-electric-board", "EWEB-Jan2022"),
    ("avista", "Avista-Jan2022"),
    ("nw-natural-gas", "NWN_OR-Jan2022"),
    ("cascade-gas", "Cascade-Jan2022"),
    ("utility-clatskanie-pud", "ClatskPUD-Jan2022"),
    ("utility-canby-utility-board", "CanbyPUD-Jan2022"),
    ("utility-columbia-power-co-op", "ColPowerCoop-Jan2022"),
    ("utility-klickitat-pud", "KlickitatPUD-Jan2022"),
    ("utility-midstate-electric-cooperative-inc", "MidStateElec-Jan2022"),
    ("utility-mcminnville-water-light", "MW&L-Jan2022"),
    ("utility-oregon-trail-electric-co-op", "OTEC-Jan2022"),
    ("utility-springfield-utility-board", "SUB-Jan2022"),
    ("utility-consumers-power-inc", "ConsumPwrInc-Jan2022"),
]
ETO_2022_FUEL_RATES_WA_OVERRIDE = [
    ("nw-natural-gas", "NWN_WA-Jan2022"),
]


ETO_2023_FUEL_RATES = [
    ("pacific-power", "PAC-Jan2023"),
    ("portland-electric", "PGE-Jan2023"),
    ("utility-city-of-ashland", "Ashland-Jan2023"),
    ("utility-canby-utility-board", "CanbyPUD-Jan2023"),
    ("central-electric", "CEC-Jan2023"),
    ("clark-pud", "ClarkPUD-Jan2023"),
    ("utility-clatskanie-pud", "ClatskPUD-Jan2023"),
    ("utility-columbia-basin-electric-co-op", "ColBasinCoop-Jan2023"),
    ("utility-columbia-river-pud", "ColRiverPUD-Jan2023"),
    ("utility-consumers-power-inc", "ConsumPwrInc-Jan2023"),
    ("utility-cowlitz-county-pud", "CowlitzPUD-Jan2023"),
    ("utility-eugene-water-electric-board", "EWEB-Jan2023"),
    ("utility-forest-grove-light-department", "ForestGrove-Jan2023"),
    ("utility-hermiston-energy-services", "Hermiston-Jan2023"),
    ("idaho-power", "IdahoPower-Jan2023"),
    ("utility-klickitat-pud", "KlickitatPUD-Jan2023"),
    ("utility-mcminnville-water-light", "McW&L-Jan2023"),
    ("utility-midstate-electric-cooperative-inc", "MidStateElec-Jan2023"),
    ("utility-oregon-trail-electric-co-op", "OTEC-Jan2023"),
    ("utility-springfield-utility-board", "SUB-Jan2023"),
    ("utility-umatilla-electric-co-op", "Umatilla-Jan2023"),
    ("avista", "Avista-Jan2023"),
    ("cascade-gas", "Cascade-Jan2023"),
    ("nw-natural-gas", "NWN_OR-Jan2023"),
]
ETO_2023_FUEL_RATES_WA_OVERRIDE = [
    ("nw-natural-gas", "NWN_WA-Jan2023"),
]


class Eto2022(ProgramBuilder):
    """Program Specs for the ETO-2022"""

    name = "Energy Trust Oregon - 2022"
    comment = "Energy Trust of Oregon 2022 Program"

    slug = "eto-2022"
    owner = "eto"

    viewable_by_company_type = None  # Leave this as None otherwise NEEA Can't see it.
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
    visibility_date = datetime.datetime(year=2022, month=2, day=1, tzinfo=datetime.timezone.utc)
    start_date = datetime.datetime(year=2022, month=2, day=1, tzinfo=datetime.timezone.utc)
    close_date = datetime.datetime(year=2023, month=11, day=1, tzinfo=datetime.timezone.utc)
    submit_date = datetime.datetime(year=2023, month=11, day=15, tzinfo=datetime.timezone.utc)
    end_date = datetime.datetime(year=2024, month=1, day=1, tzinfo=datetime.timezone.utc)
    hers_range = [0, 500]

    measures = {
        "rater": [
            (
                "EPS Information",
                [
                    "is-adu",
                    "builder-payment-redirected",
                    "payee-company",
                ],
            ),
            (
                "Fire Qualifications",
                [
                    "fire-rebuild-qualification",
                    "fire-resilience-bonus",
                    "building-fire-exterior-insulation-type",
                    "building-window-triple-pane-u-value",
                ],
            ),
            (
                "COBID Qualifications",
                [
                    "cobid-qualification",
                    "cobid-type",
                    "cobid-registered",
                ],
            ),
            (
                "Additional Incentives",
                [
                    # Additional Incentives
                    "eto-electric-elements",
                    "solar-elements",
                    "solar-company",
                    "ets-annual-etsa-kwh",
                    "non-ets-annual-pv-watts",
                    "non-ets-pv-panels-brand",
                    "non-ets-inverter-brand",
                    "non-ets-tsrf",
                    # EV
                    "electric-vehicle-type",
                    "electric-vehicle-estar-level-2",
                    "electric-vehicle-charging-brand",
                    "electric-vehicle-charging-model",
                    "electric-vehicle-charging-installer",
                    # Storage
                    "storage-type",
                    "storage-capacity",
                    "storage-brand",
                    "storage-model",
                    "storage-installer",
                    "storage-smart-panel",
                    "storage-smart-panel-brand",
                    "storage-smart-panel-model",
                    # Smart Tstat
                    "smart-thermostat-brand",
                    "has-gas-fireplace",
                ],
            ),
            (
                "HVAC Details",
                [
                    "primary-heating-equipment-type",
                    "equipment-furnace",
                    "equipment-heat-pump",
                    "mini-split-indoor-heads-quantity",
                    "equipment-dfhp-brand",
                    "equipment-dfhp-outdoor-model",
                    "equipment-dfhp-indoor-model",
                    "equipment-dfhp-furnace-model",
                    "equipment-heating-other-type",
                    "equipment-heating-other-brand",
                    "equipment-heating-other-model-number",
                    "equipment-furnace-2",
                    "equipment-heat-pump-2",
                    "equipment-dfhp-brand-2",
                    "equipment-dfhp-outdoor-model-2",
                    "equipment-dfhp-indoor-model-2",
                    "equipment-dfhp-furnace-model-2",
                    "equipment-heating-other-type-2",
                    "equipment-heating-other-brand-2",
                    "equipment-heating-other-model-number-2",
                    "equipment-air-conditioner-brand",
                    "equipment-air-conditioner-model-number-outdoor",
                    "equipment-air-conditioner-model-number-indoor",
                ],
            ),
            (
                "Water Heating",
                [
                    "equipment-water-heater",
                    "equipment-heat-pump-water-heater-serial-number",
                    "equipment-gas-tank-water-heater-serial-number",
                    "equipment-gas-tankless-water-heater-serial-number",
                ],
            ),
            (
                "Ventilation",
                [
                    "equipment-ventilation-system-type",
                    "equipment-balanced-ventilation-no-hr",
                    "equipment-ventilation-hrv-erv",
                    "equipment-ventilation-exhaust",
                    "equipment-ventilation-supply-brand",
                    "equipment-ventilation-supply-model",
                    "equipment-ventilation-spot-erv-count",
                ],
            ),
            (
                "Appliances",
                [
                    "equipment-refrigerator",
                    "equipment-dishwasher",
                    "equipment-clothes-washer",
                    "equipment-clothes-dryer",
                ],
            ),
            (
                "Notes",
                [
                    "inspection-notes",
                ],
            ),
        ],
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
                    # Additional Incentives
                    "eto-electric-elements",
                    "solar-elements",
                    "solar-company",
                    "ets-annual-etsa-kwh",
                    "non-ets-annual-pv-watts",
                    "non-ets-pv-panels-brand",
                    "non-ets-inverter-brand",
                    "non-ets-tsrf",
                    # EV
                    "electric-vehicle-type",
                    "electric-vehicle-estar-level-2",
                    "electric-vehicle-charging-brand",
                    "electric-vehicle-charging-model",
                    "electric-vehicle-charging-installer",
                    # Storage
                    "storage-type",
                    "storage-capacity",
                    "storage-brand",
                    "storage-model",
                    "storage-installer",
                    "storage-smart-panel",
                    "storage-smart-panel-brand",
                    "storage-smart-panel-model",
                    # Smart Tstat
                    "smart-thermostat-brand",
                    "has-gas-fireplace",
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
                    "equipment-dfhp-brand",
                    "equipment-dfhp-outdoor-model",
                    "equipment-dfhp-indoor-model",
                    "equipment-dfhp-furnace-model",
                    "equipment-heating-other-type",
                    "equipment-heating-other-brand",
                    "equipment-heating-other-model-number",
                    "equipment-furnace-2",
                    "equipment-heat-pump-2",
                    "equipment-dfhp-brand-2",
                    "equipment-dfhp-outdoor-model-2",
                    "equipment-dfhp-indoor-model-2",
                    "equipment-dfhp-furnace-model-2",
                    "equipment-heating-other-type-2",
                    "equipment-heating-other-brand-2",
                    "equipment-heating-other-model-number-2",
                    "heating-equipment-air-condition-installed",
                    "heating-equipment-air-condition-outdoor-model-number",
                    "heating-equipment-air-condition-indoor-model-number",
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
                    "ventilation-compliance",
                    "equipment-ventilation-hrv-erv",
                    "equipment-ventilation-system-type",
                    "equipment-ventilation-spot-erv-count",
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
        "default": {
            "is-adu": "Is this an Accessory Dwelling Unit (ADU)?",
            # Redirect
            "builder-payment-redirected": "Does the builder wish to re- direct its payment "
            "for the EPS Whole Home incentive?",
            "payee-company": "Enter the contact name or company name for the payee receiving the "
            "redirected payment.",
            # Fire
            "fire-rebuild-qualification": "Is this home on land where there had been a home "
            "that was destroyed by a wildfire?",
            "fire-resilience-bonus": "Does this home qualify for any fire resilience bonus?",
            "building-fire-exterior-insulation-type": "What type of ignition resistant continuous "
            "exterior rigid insulation is installed?",
            "building-window-triple-pane-u-value": "What is the average window U-value?",
            # COBID
            "cobid-qualification": "Does this home qualify as any of the following: affordable, "
            "rural, tribal, builder or verifier "
            "registered with Certification Office for Business Inclusion and Diversity (COBID)?",
            "cobid-type": "Does this home qualify as affordable, rural and/or tribal? ",
            "cobid-registered": "Is the builder or verifier registered with the COBID?",
            # Additional
            "eto-electric-elements": "Does this home have solar, electric vehicle, or "
            "storage elements?",
            # Solar
            "solar-elements": "What solar elements does this home have?",
            "solar-company": "What company installed the solar PV?",
            "ets-annual-etsa-kwh": "What is the annual kWh generation as per the Energy Trust "
            "solar application?",
            "non-ets-annual-pv-watts": "What is the annual kWh generation as per PV Watts?",
            "non-ets-pv-panels-brand": "What brand are the PV panels?",
            "non-ets-inverter-brand": "What brand is the inverter?",
            "non-ets-tsrf": "What is the Total Solar Resource Fraction (TSRF)?",
            # EV
            "electric-vehicle-type": "What electric vehicle elements does this home have?",
            "electric-vehicle-estar-level-2": "Is the electric vehicle charging equipment an "
            "ENERGY STAR Level 2 charger that is listed as Network Protocol Capable?",
            "electric-vehicle-charging-brand": "What is the brand of the EVSE?",
            "electric-vehicle-charging-model": "What is the model number of the EVSE?",
            "electric-vehicle-charging-installer": "What company installed the EVSE?",
            # Storage
            "storage-type": "What storage elements does this home have?",
            "storage-capacity": "What is the kWh capacity of the battery?",
            "storage-brand": "What is the brand of the battery?",
            "storage-model": "What is the model number of the battery?",
            "storage-installer": "What company installed the battery?",
            "storage-smart-panel": "Does this home have a smart electric panel or an Intelligent "
            "Load Control System (ILCS)?",
            "storage-smart-panel-brand": "What is the brand of the smart electric panel or ILCS?",
            "storage-smart-panel-model": "What is the model number is the smart electric panel "
            "or ILCS?",
            # Smart TSTAT
            "smart-thermostat-brand": "Does this home have a smart thermostat?",
            "has-gas-fireplace": "Does the home have a gas fireplace for secondary heating or "
            "decorative purposes?",
            # Heating
            "primary-heating-equipment-type": "Select the Primary Heating Equipment Type",
            "mini-split-indoor-heads-quantity": "Number of mini-split heat pump indoor heads",
            "equipment-furnace": "Select the furnace",
            "equipment-furnace-2": "Select the second furnace",
            "equipment-heat-pump": "Select the primary heat pump used for space conditioning",
            "equipment-heat-pump-2": "Select the secondary heat pump used for space conditioning",
            "equipment-dfhp-brand": "Select the primary Dual fuel heat pump brand",
            "equipment-dfhp-outdoor-model": "Select the primary Dual fuel heat pump outdoor model "
            "number",
            "equipment-dfhp-indoor-model": "Select the primary Dual fuel heat pump indoor model "
            "number",
            "equipment-dfhp-furnace-model": "Select the primary Dual fuel heat pump furnace model "
            "number",
            "equipment-dfhp-brand-2": "Select the secondary Dual fuel heat pump brand",
            "equipment-dfhp-outdoor-model-2": "Select the secondary Dual fuel heat pump outdoor "
            "model number",
            "equipment-dfhp-indoor-model-2": "Select the secondary Dual fuel heat pump indoor "
            "model number",
            "equipment-dfhp-furnace-model-2": "Select the secondary Dual fuel heat pump furnace "
            "model number",
            "equipment-heating-other-type": "Enter primary heating equipment type",
            "equipment-heating-other-brand": "Enter primary heating equipment brand",
            "equipment-heating-other-model-number": "Enter primary heating equipment model "
            "number(s)",
            "equipment-heating-other-type-2": "Enter secondary heating equipment type",
            "equipment-heating-other-brand-2": "Enter secondary heating equipment brand",
            "equipment-heating-other-model-number-2": "Enter secondary heating equipment model "
            "number(s)",
            "equipment-air-conditioner-brand": "Air conditioner brand",
            "equipment-air-conditioner-model-number-outdoor": "Air conditioner outdoor model "
            "number",
            "equipment-air-conditioner-model-number-indoor": "Air conditioner indoor model "
            "number",
            # Water heating
            "equipment-water-heater": "Select the water heater",
            "equipment-gas-tank-water-heater-serial-number": "Enter gas tank water heater "
            "serial number",
            "equipment-gas-tankless-water-heater-serial-number": "Enter gas tankless water heater "
            "serial number",
            "equipment-heat-pump-water-heater-serial-number": "Heat Pump Water Heater Serial "
            "number",
            # Ventilation
            "equipment-ventilation-system-type": "Select the ventilation system type",
            "equipment-balanced-ventilation-no-hr": "Select the balanced ventilation without "
            "heat recovery.",
            "equipment-ventilation-supply-brand": "Select the supply only ventilation brand",
            "equipment-ventilation-supply-model": "Select the supply only ventilation model",
            "equipment-ventilation-hrv-erv": "Select the HRV/ERV",
            "equipment-ventilation-spot-erv-count": "Number of Spot ERV units",
            "equipment-ventilation-exhaust": "Select the exhaust ventilation",
            # Appliances
            "equipment-refrigerator": "Select the Refrigerator",
            "equipment-dishwasher": "Select the Dishwasher",
            "equipment-clothes-washer": "Select the Clothes Washer",
            "equipment-clothes-dryer": "Select the Clothes Dryer",
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
            "eps-comments": "Comments",
            "heating-equipment-air-condition-installed": "Does this home have "
            "Air Conditioning installed?",
            "heating-equipment-air-condition-outdoor-model-number": "Air conditioner "
            "outdoor model number",
            "heating-equipment-air-condition-indoor-model-number": "Air conditioner "
            "indoor model number",
            "heating-equipment-comments": "Comments",
            "equipment-water-heater-serial-number": "Enter the water heater serial number",
            "equipment-water-heater-recirculation-pump": "Recirculation Pump",
            "equipment-water-heater-drain-water-heat-recovery": "Drain Water Heat Recovery",
            "equipment-water-heater-comments": "Comments",
            # Ventillation
            "zonal-pressure": "Zonal Pressure",
            "ventilation-compliance": "Ventilation Compliance",
            "equipment-ventilation-sone-spot-rating1": "Spot Ventilation 1",
            "equipment-ventilation-sone-spot-rating2": "Spot Ventilation 2",
            "equipment-ventilation-sone-spot-rating3": "Spot Ventilation 3",
            "equipment-ventilation-compliance": "Spot Ventilation Compliance",
            "mechanical-whole-house-exhaust-fan-flow-location": "Mechanical Whole House Exhaust "
            "Fan Flow Location",
            "mechanical-whole-house-exhaust-fan-flow-rate": "Mechanical Whole House Exhaust "
            "Fan Flow Rate",
            "mechanical-whole-house-exhaust-fan-sone-spot-rating": "Mechanical Whole House "
            "Exhaust Fan Sone Rating",
            "equipment-ventilation-comments": "Comments",
            # Envelope
            "insulation-grade-1-installation": "Grade 1 Insulation Installation",
            "thermal-enclosure-checklist": "Thermal Enclosure Checklist",
            "window-u-factor": "Window U-factor",
            "ceiling-insulation-type": "Ceiling Insulation Type",
            "intermediate-advanced-framing": "Intermediate/Advanced Framing",
            "above-grade-wall-insulation-type": "Above Grade Wall Insulation Type",
            "above-grade-wall-insulation-r-value": "Above Grade Wall Insulation R-value",
            "crawlspace-insulation-type": "Crawlspace Insulation Type",
            "crawlspace-insulation-r-value": "Crawlspace Insulation R-value",
            "rim-joist-insulation-r-value": "Rim Joist Insulation R-value",
            "envelope-comments": "Comments",
            # Ducts
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
            # Appliances
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
            "building-fire-exterior-insulation-type": "What type of ignition resistant continuous "
            "exterior rigid insulation is installed",
            "building-window-triple-pane-u-value": "What is the average window U-value?",
            "ets-annual-etsa-kwh": "If receiving solar incentive from Energy Trust, verify with "
            "builder/solar trade ally",
            "non-ets-annual-pv-watts": "If NOT receiving solar incentive from Energy Trust"
            " upload PV Watts report",
            "non-ets-pv-panels-brand": "If NOT receiving solar incentive from Energy Trust",
            "non-ets-inverter-brand": "If NOT receiving solar incentive from Energy Trust",
            "non-ets-tsrf": "If NOT receiving solar incentive from Energy Trust",
            "cobid-qualification": "See EPS Verifier Guide for definitions.  See help for links.",
            "cobid-type": "See EPS Verifier Guide for definitions.  See help for links.",
            "electric-vehicle-estar-level-2": "Check with builder/electrician. "
            "Network Protocol Capable Chargers are published "
            "here: <ul><li><a href='https://www.energystar.gov/productfinder/product/"
            "certified-evse/results' target=_blank>ENERGY STAR EVSE Qualified Product List</a>"
            "</li><li><a href='https://portlandgeneral.com/energy-choices/electric-vehicles-"
            "charging/charging-your-ev/ev-charging-pilot-program-home' target=_blank>PGE’s EVSE "
            "qualifying product list</a></li</ul>",
            "storage-capacity": "Check with builder/solar trade ally",
            "has-gas-fireplace": "Which efficiency bin does the fireplace reside?",
            "mini-split-indoor-heads-quantity": "If primary heating equipment is a mini-split",
            "equipment-heat-pump": "If primary heating model includes either a conventional "
            "heat pump or mini-splits",
            "equipment-heat-pump-2": "If secondary heating model includes either a conventional "
            "heat pump or mini-splits",
            "equipment-furnace": "Primary forced air heating",
            "equipment-furnace-2": "Secondary forced air heating",
            "equipment-heating-other-type": "If primary model includes a heating system apart "
            "from a heat pump/furnace",
            "equipment-heating-other-brand": "If primary model includes a heating system apart "
            "from a heat pump/furnace",
            "equipment-heating-other-model-number": "If primary model includes a heating system "
            "apart from a heat pump/furnace",
            "equipment-heat-pump-water-heater-serial-number": "If model includes heat pump water "
            "heater",
            "equipment-ventilation-exhaust": "If model is using balanced ventilation without "
            "heat recovery.",
            "equipment-ventilation-supply-brand": "Required if “Secondary supply fan "
            "integrated with central air handler” or “Stand alone supply with exhaust fan” "
            "are selected.",
            "equipment-ventilation-supply-model": "Required if “Secondary supply fan integrated "
            "with central air handler” or “Stand alone supply with exhaust fan” are selected.",
            "equipment-ventilation-hrv-erv": "If model includes HRV/ERV",
            "equipment-ventilation-system-type": "If the model includes ventilation",
            "equipment-ventilation-spot-erv-count": "Number of Spot ERV units",
            "equipment-refrigerator": "If refrigerator's consumption < 549 kWh/yr",
            "equipment-dishwasher": "If dishwasher's consumption < 302 kWh/yr, Place setting 12",
            "equipment-clothes-washer": "If clothes washer's iMEF > 2.155, LER 151 kWH/yr, "
            "Capacity > 3.31, Ele Rate > 0.1065, Gas Rate > 1.22, "
            "Ann Cost > 12.0",
            "equipment-clothes-dryer": "If clothes dryer's CEF > 2.8, with Moisture Sensing",
        },
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
            "duct-supply-in-conditioned-space": "Enter whole number",
            "duct-return-in-conditioned-space": "Enter whole number",
        },
    }
    help_text = {
        "default": {
            "electric-vehicle-estar-level-2": "Network Protocol Capable Chargers are published "
            "here: <ul><li><a href='https://www.energystar.gov/productfinder/product/"
            "certified-evse/results' target=_blank>ENERGY STAR EVSE Qualified Product List</a>"
            "</li><li><a href='https://portlandgeneral.com/energy-choices/electric-vehicles-"
            "charging/charging-your-ev/ev-charging-pilot-program-home' target=_blank>PGE’s EVSE "
            "qualifying product list</a></li</ul>",
            "cobid-qualification": "See <a href='https://epsverifier.com/resources/' "
            "target=_blank>EPS Verifier Guide</a> for definitions",
        }
    }
    suggested_responses = {
        "default": {
            CobidQualification: ["cobid-type"],
            CobidRegistered: ["cobid-registered"],
            AdditionalElements2022: ["eto-electric-elements"],
            SolarElements2022: ["solar-elements"],
            YesNo: [
                "is-adu",
                "fire-rebuild-qualification",
                "builder-payment-redirected",
                "cobid-qualification",
                "electric-vehicle-estar-level-2",
                "storage-smart-panel",
            ],
            Fireplace2020: [
                "has-gas-fireplace",
            ],
            PrimaryHeatingEquipment2020: [
                "primary-heating-equipment-type",
            ],
            (
                PrimaryHeatingEquipment2020.GAS_FIREPLACE,
                PrimaryHeatingEquipment2020.GAS_UNIT_HEATER,
                PrimaryHeatingEquipment2020.GAS_BOILER,
                PrimaryHeatingEquipment2020.GSHP,
                PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE,
                PrimaryHeatingEquipment2020.OTHER_GAS,
                PrimaryHeatingEquipment2020.OTHER_ELECTRIC,
                PrimaryHeatingEquipment2020.DFHP,
            ): [
                "equipment-heating-other-type",
            ],
            FireResilienceBonus: ["fire-resilience-bonus"],
            SmartThermostatBrands2022: ["smart-thermostat-brand"],
            ElectricCarElements2022: ["electric-vehicle-type"],
            StorageElements2022: ["storage-type"],
            MechanicalVentilationSystemTypes: ["equipment-ventilation-system-type"],
            BalancedVentilationTypes: ["equipment-balanced-ventilation-no-hr"],
        },
        "rater": {},
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
            ("Yes", "No", "N/A"): [
                "intermediate-advanced-framing",
                "air-handler-testing-installed",
            ],
            ("Yes", "No", "AC ready"): [
                "heating-equipment-air-condition-installed",
            ],
            (
                "Corrections Required",
                "Supply w/ Control",
                "Exhaust w/ Control",
                "HRV",
                "ERV",
            ): [
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
        },
    }
    instrument_types = {
        "integer": [
            "ets-annual-etsa-kwh",
            "non-ets-annual-pv-watts",
            "storage-capacity",
            "conditioned-space-area",
            "conditioned-space-volume",
            "equipment-ventilation-spot-erv-count",
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
        "float": [
            "building-window-triple-pane-u-value",
            "window-u-factor",
            "blower-door-ach-50pa",
        ],
        "cascading-select": [
            "equipment-furnace",
            "equipment-furnace-2",
            "equipment-heat-pump",
            "equipment-heat-pump-2",
            "equipment-water-heater",
            "equipment-ventilation-hrv-erv",  # Note this is balanced.
            "equipment-ventilation-exhaust",
            "equipment-refrigerator",
            "equipment-dishwasher",
            "equipment-clothes-washer",
            "equipment-clothes-dryer",
        ],
    }

    # Turn these into logical OR by default these are logical AND
    instrument_condition_types = {
        "default": {
            "solar-company": "one-pass",
            "equipment-ventilation-exhaust": "one-pass",
            "equipment-ventilation-hrv-erv": "one-pass",
        }
    }

    instrument_conditions = {
        "default": {},
        "rater": {
            "instrument": {
                "builder-payment-redirected": {
                    YesNo.YES: ["payee-company"],
                },
                "fire-rebuild-qualification": {
                    YesNo.YES: ["fire-resilience-bonus"],
                },
                "fire-resilience-bonus": {
                    (
                        "one",
                        (
                            FireResilienceBonus.TRIPLE_PANE,
                            FireResilienceBonus.TRIPLE_PANE_AND_SEALED_ATTIC,
                            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
                            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
                        ),
                    ): ["building-window-triple-pane-u-value"],
                    (
                        "one",
                        (
                            FireResilienceBonus.RIGID_INSULATION,
                            FireResilienceBonus.RIGID_INSULATION_AND_SEALED_ATTIC,
                            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION,
                            FireResilienceBonus.TRIPLE_PANE_AND_RIGID_INSULATION_AND_SEALED_ATTIC,
                        ),
                    ): ["building-fire-exterior-insulation-type"],
                },
                "cobid-qualification": {
                    YesNo.YES: ["cobid-type", "cobid-registered"],
                },
                "eto-electric-elements": {
                    (
                        "one",
                        (
                            AdditionalElements2022.SOLAR,
                            AdditionalElements2022.SOLAR_AND_STORAGE,
                            AdditionalElements2022.SOLAR_AND_ELECTRIC_CAR,
                            AdditionalElements2022.ALL,
                        ),
                    ): ["solar-elements"],
                    (
                        "one",
                        (
                            AdditionalElements2022.ELECTRIC_CAR,
                            AdditionalElements2022.SOLAR_AND_ELECTRIC_CAR,
                            AdditionalElements2022.ALL,
                        ),
                    ): ["electric-vehicle-type"],
                    (
                        "one",
                        (
                            AdditionalElements2022.SOLAR_AND_STORAGE,
                            AdditionalElements2022.ALL,
                        ),
                    ): ["storage-type"],
                },
                "solar-elements": {
                    # If “Solar PV” selected, then: 'ets-annual-etsa-kwh'
                    ("one", (SolarElements2022.SOLAR_PV, SolarElements2022.NET_ZERO)): [
                        "ets-annual-etsa-kwh",
                        "solar-company",
                    ],
                    # If “Non-Energy Trust Solar PV” selected, then:
                    SolarElements2022.NON_ETO_SOLAR: [
                        "non-ets-annual-pv-watts",
                        "non-ets-pv-panels-brand",
                        "non-ets-inverter-brand",
                        "non-ets-tsrf",
                        "solar-company",
                    ],
                },
                "electric-vehicle-type": {
                    ElectricCarElements2022.EV_INSTALLED: [
                        "electric-vehicle-estar-level-2",
                        "electric-vehicle-charging-brand",
                        "electric-vehicle-charging-model",
                        "electric-vehicle-charging-installer",
                    ],
                },
                "storage-type": {
                    StorageElements2022.STORAGE_INSTALLED: [
                        "storage-capacity",
                        "storage-brand",
                        "storage-model",
                        "storage-installer",
                        "storage-smart-panel",
                    ],
                },
                "storage-smart-panel": {
                    YesNo.YES: [
                        "storage-smart-panel-brand",
                        "storage-smart-panel-model",
                    ],
                },
                "primary-heating-equipment-type": {
                    (
                        "one",
                        (
                            PrimaryHeatingEquipment2020.MINI_SPLIT_NON_DUCTED,
                            PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED,
                            PrimaryHeatingEquipment2020.MINI_SPLIT_MIXED,
                        ),
                    ): [
                        "mini-split-indoor-heads-quantity",
                    ],
                },
                "equipment-ventilation-system-type": {
                    MechanicalVentilationSystemTypes.BALANCED_NO_HR: [
                        "equipment-balanced-ventilation-no-hr"
                    ],
                    (
                        "one",
                        (
                            MechanicalVentilationSystemTypes.STAND_ALONE,
                            MechanicalVentilationSystemTypes.INTEGRATED_HRV_ERV,
                        ),
                    ): [
                        "equipment-ventilation-hrv-erv",
                    ],
                    MechanicalVentilationSystemTypes.SPOT: [
                        "equipment-ventilation-spot-erv-count",
                        "equipment-ventilation-hrv-erv",
                    ],
                    MechanicalVentilationSystemTypes.WA_EXHAUST: [
                        "equipment-ventilation-exhaust",
                    ],
                },
                "equipment-balanced-ventilation-no-hr": {
                    (
                        "one",
                        (
                            BalancedVentilationTypes.INTERMITTENT,
                            BalancedVentilationTypes.CONTINUOUS,
                            BalancedVentilationTypes.STAND_ALONE,
                            BalancedVentilationTypes.SECONDARY,
                        ),
                    ): [
                        "equipment-ventilation-exhaust",
                    ],
                    (
                        "one",
                        (
                            BalancedVentilationTypes.STAND_ALONE,
                            BalancedVentilationTypes.SECONDARY,
                        ),
                    ): [
                        "equipment-ventilation-supply-brand",
                        "equipment-ventilation-supply-model",
                    ],
                },
            },
            "simulation": {
                # Water heaters.
                "floorplan.simulation.water_heaters.is_conventional_gas": {
                    ("one", True): ["equipment-gas-tank-water-heater-serial-number"],
                },
                "floorplan.simulation.water_heaters.is_tankless_gas": {
                    ("one", True): ["equipment-gas-tankless-water-heater-serial-number"],
                },
                "floorplan.simulation.water_heaters.is_heat_pump": {
                    ("one", True): [
                        "equipment-heat-pump-water-heater-serial-number",
                    ],
                },
                # Heating
                "floorplan.simulation.mechanical_equipment.primary_heating_equipment_system_type": {
                    MechanicalSystemType.FORCED_AIR_GAS_HEATER: [
                        "equipment-furnace",
                    ],
                    (
                        "one",
                        (
                            MechanicalSystemType.FORCED_AIR_ASHP,
                            MechanicalSystemType.DUCTLESS_ASHP,
                            MechanicalSystemType.HYRONIC_ASHP,
                            MechanicalSystemType.RADIANT_GSHP,
                            MechanicalSystemType.ASHP,
                        ),
                    ): [
                        "equipment-heat-pump",
                    ],
                    (
                        "one",
                        (
                            MechanicalSystemType.DFHP,
                            MechanicalSystemType.FORCED_AIR_DFHP,
                            MechanicalSystemType.DUCTLESS_DFHP,
                        ),
                    ): [
                        "equipment-dfhp-brand",
                        "equipment-dfhp-outdoor-model",
                        "equipment-dfhp-indoor-model",
                        "equipment-dfhp-furnace-model",
                    ],
                    (
                        "one",
                        (
                            MechanicalSystemType.GAS_HEATER,
                            MechanicalSystemType.DUCTLESS_GAS_HEATER,
                            MechanicalSystemType.RADIANT_GAS_HEATER,
                            MechanicalSystemType.HYRONIC_GAS_HEATER,
                            MechanicalSystemType.ELECTRIC_HEATER,
                            MechanicalSystemType.FORCED_AIR_ELECTRIC_HEATER,
                            MechanicalSystemType.DUCTLESS_ELECTRIC_HEATER,
                            MechanicalSystemType.RADIANT_ELECTRIC_HEATER,
                            MechanicalSystemType.HYRONIC_ELECTRIC_HEATER,
                            MechanicalSystemType.GSHP,
                            MechanicalSystemType.FORCED_AIR_GSHP,
                            MechanicalSystemType.RADIANT_GSHP,
                            MechanicalSystemType.HYRONIC_GSHP,
                        ),
                    ): [
                        "equipment-heating-other-type",
                        "equipment-heating-other-brand",
                        "equipment-heating-other-model-number",
                    ],
                },
                "floorplan.simulation.mechanical_equipment."
                "secondary_heating_equipment_system_type": {
                    MechanicalSystemType.FORCED_AIR_GAS_HEATER: [
                        "equipment-furnace-2",
                    ],
                    (
                        "one",
                        (
                            MechanicalSystemType.FORCED_AIR_ASHP,
                            MechanicalSystemType.DUCTLESS_ASHP,
                            MechanicalSystemType.HYRONIC_ASHP,
                            MechanicalSystemType.RADIANT_GSHP,
                            MechanicalSystemType.ASHP,
                        ),
                    ): [
                        "equipment-heat-pump-2",
                    ],
                    (
                        "one",
                        (
                            MechanicalSystemType.DFHP,
                            MechanicalSystemType.FORCED_AIR_DFHP,
                            MechanicalSystemType.DUCTLESS_DFHP,
                        ),
                    ): [
                        "equipment-dfhp-brand-2",
                        "equipment-dfhp-outdoor-model-2",
                        "equipment-dfhp-indoor-model-2",
                        "equipment-dfhp-furnace-model-2",
                    ],
                    (
                        "one",
                        (
                            MechanicalSystemType.GAS_HEATER,
                            MechanicalSystemType.DUCTLESS_GAS_HEATER,
                            MechanicalSystemType.RADIANT_GAS_HEATER,
                            MechanicalSystemType.HYRONIC_GAS_HEATER,
                            MechanicalSystemType.ELECTRIC_HEATER,
                            MechanicalSystemType.FORCED_AIR_ELECTRIC_HEATER,
                            MechanicalSystemType.DUCTLESS_ELECTRIC_HEATER,
                            MechanicalSystemType.RADIANT_ELECTRIC_HEATER,
                            MechanicalSystemType.HYRONIC_ELECTRIC_HEATER,
                            MechanicalSystemType.GSHP,
                            MechanicalSystemType.FORCED_AIR_GSHP,
                            MechanicalSystemType.RADIANT_GSHP,
                            MechanicalSystemType.HYRONIC_GSHP,
                        ),
                    ): [
                        "equipment-heating-other-type-2",
                        "equipment-heating-other-brand-2",
                        "equipment-heating-other-model-number-2",
                    ],
                },
                "floorplan.simulation.air_conditioners.system_type": {
                    CoolingSystemType.AIR_CONDITIONER: [
                        "equipment-air-conditioner-brand",
                        "equipment-air-conditioner-model-number-outdoor",
                        "equipment-air-conditioner-model-number-indoor",
                    ],
                },
                "floorplan.simulation.air_conditioners.efficiency_unit": {
                    CoolingEfficiencyUnit.SEER: [
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
        "default": {
            "smart-thermostat-brand": {
                SmartThermostatBrands2022.OTHER.value: {"comment_required": True},
            },
            "equipment-ventilation-system-type": {
                MechanicalVentilationSystemTypes.OTHER.value: {"comment_required": True},
            },
            "equipment-balanced-ventilation-no-hr": {
                BalancedVentilationTypes.OTHER.value: {"comment_required": True},
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
                {
                    "name": "Green Building Registry ID",
                    "data_type": "open",
                    "is_required": False,
                },
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
        import datetime
        from django.conf import settings
        from infrastructure.utils import get_user_input
        from axis.company.models import Company
        from axis.qa.models import QARequirement
        from axis.home.models import EEPProgramHomeStatus
        from axis.eep_program.models import EEPProgram

        # START DELETE ME
        if not hasattr(self, "wiped"):
            _date = datetime.datetime(2022, 3, 1, tzinfo=datetime.timezone.utc)
            wipe = "No"
            if "test" not in sys.argv:
                wipe = get_user_input(
                    f"Please confirm you wish to wipe the data on {settings.SERVER_TYPE} from "
                    f"{_date} forward",
                    choices=["Yes", "No"],
                    default="No",
                )
            if wipe == "Yes":
                slugs = [self.slug + "-qa", self.slug]
                EEPProgram.objects.filter(slug__in=slugs).update(collection_request=None)

                from django_input_collection.models import (
                    Measure,
                    CollectionRequest,
                    CollectionInstrument,
                    CollectionInstrumentType,
                    Case,
                    Condition,
                    CollectionGroup,
                    SuggestedResponse,
                )
                from axis.checklist.models import CollectedInput

                for ModelObject in [
                    Measure,
                    Case,
                    Condition,
                    CollectionGroup,
                    CollectionInstrumentType,
                    CollectionRequest,
                    CollectionInstrument,
                    SuggestedResponse,
                ]:
                    objects = ModelObject.objects.filter(date_created__gte=_date)
                    if objects.count():
                        self.stdout.write(
                            f"  * Removing {objects.count()} "
                            f"{ModelObject.__class__!r} objects\n"
                        )
                        objects.delete()

                stats = EEPProgramHomeStatus.objects.filter(eep_program__slug__in=slugs)
                stat_ids = list(stats.values_list("id", flat=True))
                objects = CollectedInput.objects.filter(home_status_id__in=stat_ids)
                if objects.count():
                    self.stdout.write(f"  * Removing {objects.count()} Answers\n")
                    objects.delete()
                if stats.count():
                    self.stdout.write(f"  * Resetting {stats.count()} collection requests\n")
                    stats.update(collection_request=None)
            else:
                if "test" not in sys.argv:
                    self.stdout.write("Skipping clearing db.\n")
            self.wiped = True
        # END DELETE ME

        _program = super(Eto2022, self).build_program()

        program = EEPProgram.objects.get(slug="eto-2022")
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
