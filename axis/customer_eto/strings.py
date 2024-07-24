"""strings.py: Django customer_eto"""


import logging
from textwrap import dedent
from typing import List, Tuple

from axis.remrate_data.strings import (
    HOME_TYPES,
    FOUNDATION_TYPES,
    FOUNDATION_WALL_LOCATIONS,
)

__author__ = "Steven Klass"
__date__ = "12/10/13 2:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)

ETO_PROGRAM_SLUGS = [
    "eto",
    "eto-2015",
    "eto-2016",
    "eto-2017",
    "eto-2018",
    "eto-2019",
    "eto-2020",
]

NEW_ETO_ACCOUNT_NOTIFICATION = (
    "Builder {company} has been associated with an Energy Trust "
    "program home at <a href='{home_url}'>{home}</a> and does not "
    "have an ETO Account Number.  Please "
    "<a href='{add_relationship}'>add an association</a> to this "
    "builder and <a href='{edit_url}'>add</a> an ETO Account Number to "
    "the builder's profile to prevent delays in home certification."
)
QA_REMAINING = (
    'QA is gating certification on <a href="{home_url}">{home}</a>.  Please click '
    '<a href="{home_url}">here</a> to complete QA on this home.'
)

ETO_ACCOUNT_NUMBER_ADDED_BASE = """ETO Account Number for {company} has been added."""
ETO_ACCOUNT_NUMBER_ADDED_NOTIFICATION_SINGLE = (
    "   The home <a href='{home_url}'>{home}</a> which is associated with an "
    "Energy Trust program can now proceed."
)
ETO_ACCOUNT_NUMBER_ADDED_NOTIFICATION_MULTS = (
    "   The {count} homes that are associated with an Energy Trust program and "
    "{company} can now proceed."
)

ETO_FASTTRACK_SUBMISSION_SUCCESS = (
    "Project Tracker {project_type} Project ID is {project_id} "
    "for <a href='{home_url}'>{home}</a> has been successfully submitted."
)

ETO_FASTTRACK_SUBMISSION_FAILED = (
    "Project Tracker {project_type} for <a href='{home_url}'>{home}</a> "
    "has failed attempt {attempt}.  Error presented: {exc}."
)

HOME_REACHED_INSPECTED_STATUS = (
    'Home <a href="{home_url}">{home}</a> has advanced to inspected status.'
)

EPS_CALCULATOR_NOT_VALID = (
    """EPS Calculator data is not valid yet for <a href='{url}'>{home_stat}</a>."""
)

ETO_SUPPLEMENTARY_QUESTIONS = [
    {
        "section": "companies",
        "slug": "hvac_company",
        "text": "HVAC Company",
        "type": "text",
    },
    {
        "section": "companies",
        "slug": "insulation_company",
        "text": "Insulation Company",
        "type": "text",
    },
    {
        "section": "building",
        "slug": "conditioned_area",
        "text": "Area of Conditioned Space",
        "type": "float",
        "min_value": 200,
        "max_value": 10000,
    },
    {
        "section": "building",
        "slug": "conditioned_volume",
        "text": "Volume of Conditioned Space",
        "type": "float",
        "min_value": 1000,
        "max_value": 100000,
    },
    {
        "section": "building",
        "slug": "housing_type",
        "text": "Housing Type",
        "type": "choice",
        "choices": dict(HOME_TYPES).values(),
    },
    {
        "section": "building",
        "slug": "floors_above_grade",
        "text": "Number of Floors Above Grade",
        "type": "int",
        "min_value": 1,
        "max_value": 5,
    },
    {
        "section": "building",
        "slug": "bedrooms_count",
        "text": "Number of Bedrooms",
        "type": "int",
        "min_value": 1,
        "max_value": 15,
    },
    {
        "section": "building",
        "slug": "foundation_type",
        "text": "Foundation Type",
        "type": "choice",
        "choices": dict(FOUNDATION_TYPES).values(),
    },
    {
        "section": "foundation walls",
        "slug": "foundation_location",
        "text": "Location",
        "type": "choice",
        "choices": dict(FOUNDATION_WALL_LOCATIONS).values(),
    },
    {
        "section": "foundation walls",
        "slug": "foundation_length",
        "text": "Length (ft)",
        "type": "float",
        "min_value": 1,
        "max_value": 10000,
    },
    {
        "section": "foundation walls",
        "slug": "foundation_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 1,
        "max_value": 50,
    },
    {
        "section": "foundation walls",
        "slug": "foundation_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "slab",
        "slug": "slab_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "slab",
        "slug": "slab_under_r_value",
        "text": "Under R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "slab",
        "slug": "slab_under_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "slab",
        "slug": "slab_perimeter_r_value",
        "text": "Perimeter R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "slab",
        "slug": "slab_perimeter_insulation_type",
        "text": "Perimeter Insulation Type",
        "type": "text",
    },
    {
        "section": "floor 1",
        "slug": "floor1_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "floor 1",
        "slug": "floor1_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "floor 1",
        "slug": "floor1_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "floor 1",
        "slug": "floor1_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "floor 2",
        "slug": "floor2_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "floor 2",
        "slug": "floor2_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "floor 2",
        "slug": "floor2_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "floor 2",
        "slug": "floor2_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "rim joist 1",
        "slug": "rim_joist1_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "rim joist 1",
        "slug": "rim_joist1_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "rim joist 1",
        "slug": "rim_joist1_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "rim joist 1",
        "slug": "rim_joist1_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "rim joist 2",
        "slug": "rim_joist2_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "rim joist 2",
        "slug": "rim_joist2_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "rim joist 2",
        "slug": "rim_joist2_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "rim joist 2",
        "slug": "rim_joist2_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "Above Grade Wall 1",
        "slug": "agw1_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "Above Grade Wall 1",
        "slug": "agw1_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Above Grade Wall 1",
        "slug": "agw1_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Above Grade Wall 1",
        "slug": "agw1_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "Above Grade Wall 2",
        "slug": "agw2_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "Above Grade Wall 2",
        "slug": "agw2_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Above Grade Wall 2",
        "slug": "agw2_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Above Grade Wall 2",
        "slug": "agw2_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "Window 1",
        "slug": "window1_orientiation",
        "text": "Orientation",
        "type": "text",
    },
    {
        "section": "Window 1",
        "slug": "window1_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 1",
        "slug": "window1_u_value",
        "text": "U-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 1",
        "slug": "window1_shgc",
        "text": "SHGC",
        "type": "float",
        "min_value": 0,
        "max_value": 1,
    },
    {
        "section": "Window 2",
        "slug": "window2_orientiation",
        "text": "Orientation",
        "type": "text",
    },
    {
        "section": "Window 2",
        "slug": "window2_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 2",
        "slug": "window2_u_value",
        "text": "U-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 2",
        "slug": "window2_shgc",
        "text": "SHGC",
        "type": "float",
        "min_value": 0,
        "max_value": 1,
    },
    {
        "section": "Window 3",
        "slug": "window3_orientiation",
        "text": "Orientation",
        "type": "text",
    },
    {
        "section": "Window 3",
        "slug": "window3_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 3",
        "slug": "window3_u_value",
        "text": "U-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 3",
        "slug": "window3_shgc",
        "text": "SHGC",
        "type": "float",
        "min_value": 0,
        "max_value": 1,
    },
    {
        "section": "Window 4",
        "slug": "window4_orientiation",
        "text": "Orientation",
        "type": "text",
    },
    {
        "section": "Window 4",
        "slug": "window4_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 4",
        "slug": "window4_u_value",
        "text": "U-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 4",
        "slug": "window4_shgc",
        "text": "SHGC",
        "type": "float",
        "min_value": 0,
        "max_value": 1,
    },
    {
        "section": "Window 5",
        "slug": "window5_orientiation",
        "text": "Orientation",
        "type": "text",
    },
    {
        "section": "Window 5",
        "slug": "window5_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 5",
        "slug": "window5_u_value",
        "text": "U-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Window 5",
        "slug": "window5_shgc",
        "text": "SHGC",
        "type": "float",
        "min_value": 0,
        "max_value": 1,
    },
    {
        "section": "Door 1",
        "slug": "door1_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Door 1",
        "slug": "door1_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Door 2",
        "slug": "door2_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Door 2",
        "slug": "door2_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Flat Ceiling",
        "slug": "flat_ceiling_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Flat Ceiling",
        "slug": "flat_ceiling_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Flat Ceiling",
        "slug": "flat_ceiling_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "Vault Ceiling",
        "slug": "vault_ceiling_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Vault Ceiling",
        "slug": "vault_ceiling_r_value",
        "text": "R-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Vault Ceiling",
        "slug": "vault_ceiling_insulation_type",
        "text": "Insulation Type",
        "type": "text",
    },
    {
        "section": "Skylight",
        "slug": "skylight_orientiation",
        "text": "Orientation",
        "type": "text",
    },
    {
        "section": "Skylight",
        "slug": "skylight_area",
        "text": "Area",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Skylight",
        "slug": "skylight_u_value",
        "text": "U-Value",
        "type": "float",
        "min_value": 0,
    },
    {
        "section": "Skylight",
        "slug": "skylight_shgc",
        "text": "SHGC",
        "type": "float",
        "min_value": 0,
        "max_value": 1,
    },
    {
        "section": "Space Heating",
        "slug": "heating_type",
        "text": "Type",
        "type": "text",
    },
    {
        "section": "Space Heating",
        "slug": "heating_fuel",
        "text": "Fuel",
        "type": "text",
    },
    # {'section': 'Space Heating', 'slug': 'heating_brand', 'text': 'Brand', 'type': 'text'},
    # {'section': 'Space Heating', 'slug': 'heating_model', 'text': 'Model Number', 'type': 'text'},
    {
        "section": "Space Heating",
        "slug": "heating_afue",
        "text": "AFUE",
        "type": "float",
    },
    {"section": "Space Heating", "slug": "heating_ecm", "text": "ECM", "type": "text"},
    {
        "section": "Space Heating",
        "slug": "heating_hspf",
        "text": "HSPF",
        "type": "float",
    },
    {"section": "Space Heating", "slug": "heating_cop", "text": "COP", "type": "float"},
    {
        "section": "Space Heating",
        "slug": "heating_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "Space Heating",
        "slug": "heating_qty",
        "text": "Number of Systems",
        "type": "int",
    },
    {"section": "Water Heating", "slug": "dhw_type", "text": "Type", "type": "text"},
    {"section": "Water Heating", "slug": "dhw_fuel", "text": "Fuel", "type": "text"},
    # {'section': 'Water Heating', 'slug': 'dhw_brand', 'text': 'Brand', 'type': 'text'},
    # {'section': 'Water Heating', 'slug': 'dhw_model', 'text': 'Model Number', 'type': 'text'},
    {
        "section": "Water Heating",
        "slug": "dhw_efficiency",
        "text": "Efficiency",
        "type": "float",
    },
    {
        "section": "Water Heating",
        "slug": "dhw_location",
        "text": "Location",
        "type": "text",
    },
    {
        "section": "Water Heating",
        "slug": "dhw_qty",
        "text": "Number of Systems",
        "type": "int",
    },
    {"section": "Cooling", "slug": "cooling_type", "text": "Type", "type": "text"},
    {"section": "Cooling", "slug": "cooling_brand", "text": "Brand", "type": "text"},
    {
        "section": "Cooling",
        "slug": "cooling_model",
        "text": "Model Number",
        "type": "text",
    },
    {
        "section": "Cooling",
        "slug": "cooling_efficiency",
        "text": "Efficiency",
        "type": "float",
    },
    {"section": "Ducts", "slug": "ducts_type", "text": "Type", "type": "text"},
    {
        "section": "Ducts",
        "slug": "ducts_leakage",
        "text": "Leakage CFM @50",
        "type": "float",
    },
    {
        "section": "Ducts",
        "slug": "ducts_pct_inside",
        "text": "Percent Inside",
        "type": "float",
    },
    {"section": "Ducts", "slug": "ducts_r_value", "text": "R-Value", "type": "float"},
    {
        "section": "Refrigerator",
        "slug": "refigerator_brand",
        "text": "Brand",
        "type": "text",
    },
    {
        "section": "Refrigerator",
        "slug": "refigerator_model",
        "text": "Model Number",
        "type": "text",
    },
    {
        "section": "Refrigerator",
        "slug": "refigerator_consumption",
        "text": "Consumption",
        "type": "float",
    },
    {
        "section": "Dishwasher",
        "slug": "dishwasher_brand",
        "text": "Brand",
        "type": "text",
    },
    {
        "section": "Dishwasher",
        "slug": "dishwasher_model",
        "text": "Model Number",
        "type": "text",
    },
    {
        "section": "Dishwasher",
        "slug": "dishwasher_consumption",
        "text": "Consumption",
        "type": "float",
    },
    {"section": "Range/Oven", "slug": "range_brand", "text": "Brand", "type": "text"},
    {
        "section": "Range/Oven",
        "slug": "range_model",
        "text": "Model Number",
        "type": "text",
    },
    {"section": "Washer", "slug": "washer_brand", "text": "Brand", "type": "text"},
    {
        "section": "Washer",
        "slug": "washer_model",
        "text": "Model Number",
        "type": "text",
    },
    {"section": "Dryer", "slug": "dryer_brand", "text": "Brand", "type": "text"},
    {"section": "Dryer", "slug": "dryer_model", "text": "Model Number", "type": "text"},
    {"section": "Lighting", "slug": "cfl_count", "text": "CFL Count", "type": "int"},
    {"section": "Lighting", "slug": "led_count", "text": "LED Count", "type": "int"},
    {
        "section": "Lighting",
        "slug": "lighting_efficiency",
        "text": "Percent Efficient",
        "type": "float",
    },
    {
        "section": "Solar PV",
        "slug": "solar_generation",
        "text": "Solar Generation",
        "type": "text",
    },
    {
        "section": "Solar PV",
        "slug": "solar_installer",
        "text": "Installation Company",
        "type": "text",
    },
    {
        "section": "Solar PV",
        "slug": "solar_eto_verified",
        "text": "ETO Verified",
        "type": "text",
    },
    {"section": "Recording", "slug": "notes", "text": "Notes", "type": "text"},
]

ETO_2019_CHECKSUMS = [
    ("5FA1D9E5", "OR Central 2019-Final.udr"),
    ("3A9D8804", "OR Perf Zonal 2019-Final.udr"),
    ("3B4E8CBB", "2019-SWWA EPS-REMv15.7-Final.udr"),
]

ETO_2020_CHECKSUMS = [
    ("2E07EEEA", "OR Perf Path Central 2020-Final.udr"),
    ("7EFE1FE0", "OR Perf Path Zonal 2020-Final.udr"),
    ("E10EE32D", "2020-SWWA EPS-REMv15.7-Final.udr"),
]

ETO_2021_CHECKSUMS: List[Tuple[str, str]] = [
    ("555A4B54", "OR Perf Path Central 2021-Final.udr"),
    ("5336B197", "OR Perf Path Zonal 2021-Final.udr"),
    ("BF6A0805", "WAPerfPath-GasCentral-GasDHW-Small_2021-Final.udr"),
    ("54A9C108", "WAPerfPath-GasCentral-GasDHW-Medium_2021-Final.udr"),
    ("BB85F2F1", "WAPerfPath-GasCentral-ElecDHW-Small_2021-Final.udr"),
    ("C8A062FC", "WAPerfPath-GasCentral-ElecDHW-Medium_2021-Final.udr"),
]

ETO_2022_CHECKSUMS: List[Tuple[str, str]] = [
    ("A7AF23BC", "OR Perf Path Central 2022-FINAL.udr"),
    ("0DE1953D", "OR Perf Path Central 2022 V2-FINAL.udr"),
    ("D6520E37", "OR Perf Path Zonal 2022-FINAL.udr"),
    ("BF6A0805", "WAPerfPath-GasCentral-GasDHW-Small_2021-Final.udr"),
    ("54A9C108", "WAPerfPath-GasCentral-GasDHW-Medium_2021-Final.udr"),
    ("BB85F2F1", "WAPerfPath-GasCentral-ElecDHW-Small_2021-Final.udr"),
    ("C8A062FC", "WAPerfPath-GasCentral-ElecDHW-Medium_2021-Final.udr"),
]

ETO_2023_CHECKSUMS: List[Tuple[str, str]] = [
    ("BC699BAE", "OR Perf Path Central 2023-FINAL.udr"),
    ("2B34EC7A", "OR Perf Path Zonal 2023-FINAL.udr"),
    ("BF6A0805", "WAPerfPath-GasCentral-GasDHW-Small_2021-Final.udr"),
    ("54A9C108", "WAPerfPath-GasCentral-GasDHW-Medium_2021-Final.udr"),
    ("BB85F2F1", "WAPerfPath-GasCentral-ElecDHW-Small_2021-Final.udr"),
    ("C8A062FC", "WAPerfPath-GasCentral-ElecDHW-Medium_2021-Final.udr"),
]

COMPLIANCE_LONGFORM_CHOICES = {
    k: dedent(v)
    for k, v in {
        "eps_20": """
        Energy Performance Score (EPS) “20%” with Specific Elements
            a. Earth Advantage Silver and EPS 20% Certification
            b. Energy Trust Solar Ready
                • An approvable implementation is a roof top solar ready installation that includes a
                  junction box placed on an attic truss on a southern or western exposure with a metal
                  conduit path terminating in a junction box installed next to the main service panel.
                  Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                  in the service panel for a solar installation. The junction box is grounded. Details for
                  the installation are provided by Energy Trust of Oregon and included in each permitted
                  plan set.
            c. Advanced Energy Storage dedicated circuit
                • Labeled panel space for a double 40A/240V breaker
            d. Electric Vehicle Charger Ready
            e. Smart (demand response capable) electric water heater or tankless water heater
                (EPS prerequisite)
            f.  Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program
    """,
        "eps_30": """
        Energy Performance Score (EPS) “30%” with Specific Elements
            a. EPS 30% Certification
            b. Energy Trust Solar Ready:
                • An approvable implementation is a roof top solar ready installation that includes a
                  junction box placed on an attic truss on a southern or western exposure with a metal
                  conduit path terminating in a junction box installed next to the main service panel.
                  Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                  in the service panel for a solar installation. The junction box is grounded. Details for
                  the installation are provided by Energy Trust of Oregon and included in each permitted
                  plan set.
            c. Smart (demand response capable) electric water heater or tankless water heater (EPS
                prerequisite)
            d. Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program
            e. A minimum of 3 additional labeled breakers that are either:
                • One (1) EV + Double 40A/240V minimum Energy Storage circuits, with 72" clear wall space
                  labeled for future solar + energy storage + EV charging; or
                • Dedicated labeled subpanel, with 72" clear wall space labeled for future solar + energy
                  storage + EV charging
    """,
        "eps_40": """
        Energy Performance Score (EPS) “40%” with Specific Elements
            a. EPS 40% Certification
            b. Smart (demand response capable) electric water heater or tankless water heater (EPS
                prerequisite)
            c. Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program
            d. A minimum of 5 labeled breakers that are either:
                • Double 40A/240V minimum Solar + one (1) EV + Double 40A/240V minimum Energy Storage
                  circuits, with 72" clear wall space labeled for future solar + energy storage + EV
                  charging; or
                • Dedicated labeled subpanel, with 72" clear wall space labeled for future solar +
                  energy storage + EV charging
    """,
        "ea_silver": """
        Earth Advantage Silver with Specific Elements
            a. Earth Advantage Silver Certification
            b. Energy Trust Solar Ready:
                • An approvable implementation is a roof top solar ready installation that includes a
                  junction box placed on an attic truss on a southern or western exposure with a metal
                  conduit path terminating in a junction box installed next to the main service panel.
                  Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                  in the service panel for a solar installation. The junction box is grounded. Details for
                  the installation are provided by Energy Trust of Oregon and included in each permitted
                  plan set.
            c. Advanced Energy Storage dedicated circuit: Labeled panel space for a double 40A/240V
                breaker with 72" clear wall space labeled for future solar + energy storage + EV charging
            d. Electric Vehicle Charger Ready
            e. Smart (demand response capable) electric water heater or tankless water heater (EPS
                prerequisite)
            f.  Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program
    """,
        "ngbs_standard": """
        National Green Building Standard (NGBS) with Specific Elements
            a. NGBS Silver Certification
            b. Energy Trust Solar Ready
                • An approvable implementation is a roof top solar ready installation that includes a
                  junction box placed on an attic truss on a southern or western exposure with a metal
                  conduit path terminating in a junction box installed next to the main service panel.
                  Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                  in the service panel for a solar installation. The junction box is grounded. Details for
                  the installation are provided by Energy Trust of Oregon and included in each permitted
                  plan set.
            c. Advanced Energy Storage dedicated circuit: Labeled panel space for a double 40A/240V
            breaker
                • An approvable implementation is a main service electrical panel that has breaker
                  spaces reserved and labeled for an electric vehicle outlet, roof top solar, and a critical
                  load panel for an energy storage device.
            d. Electric Vehicle Charger Ready
                • An approvable implementation is installation of a conduit from the main electrical
                  panel to a blank plate outlet on the garage wall that will allow the customer to install
                  the appropriate plug for their electric vehicle. Also included in the electrical panel
                  is space for a 40 amp, minimum amperage, breaker that is labeled and reserved in the
                  main panel for this feature.
            e. Smart (demand response capable) electric water heater or tankless water heater (EPS
            prerequisite)
                • Such as a Rinnai tankless water heater, Model Number RUCS75iN that is Wi-Fi compatible
            f.  Wi-Fi Smart “Learning” Thermostat per PGE Demand Response (DR) thermostat program
                • Such as a Honeywell Lyric Round Programmable Thermostat, Part Number H8732WFH5002
    """,
        "ea": """
        Earth Advantage
            a. Earth Advantage Silver Certification
            b. Pre-Plumbed for Solar
    """,
        "ngbs": """
        National Green Building Standard (NGBS)
            a. NGBS Silver Certification
            b. Pre-Plumbed for Solar
    """,
        "eps": """
        EPS
            a. 20% above code
            b. Pre-Plumbed for Solar
    """,
    }.items()
}

COMPLIANCE_LONGFORM_HTML_CHOICES = {
    "eps_20": """
        Energy Performance Score (EPS) “20%” with Specific Elements
        <ul>
            <li>Earth Advantage Silver and EPS 20% Certification</li>
            <li>Energy Trust Solar Ready
                <ul>
                    <li>An approvable implementation is a roof top solar ready installation that includes a
                    junction box placed on an attic truss on a southern or western exposure with a metal
                    conduit path terminating in a junction box installed next to the main service panel.
                    Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                    in the service panel for a solar installation. The junction box is grounded. Details for
                    the installation are provided by Energy Trust of Oregon and included in each permitted
                    plan set.</li>
                </ul></li>
            <li>Advanced Energy Storage dedicated circuit
                <ul><li>Labeled panel space for a double 40A/240V breaker</li></ul></li>
            <li>Electric Vehicle Charger Ready</li>
            <li>Smart (demand response capable) electric water heater or tankless water heater
                (EPS prerequisite)</li>
            <li>Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program</li>
        </ul>
    """,
    "eps_30": """
        Energy Performance Score (EPS) “30%” with Specific Elements
        <ul>
            <li>EPS 30% Certification</li>
            <li>Energy Trust Solar Ready:
                <ul>
                    <li>An approvable implementation is a roof top solar ready installation that includes a
                    junction box placed on an attic truss on a southern or western exposure with a metal
                    conduit path terminating in a junction box installed next to the main service panel.
                    Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                    in the service panel for a solar installation. The junction box is grounded. Details for
                    the installation are provided by Energy Trust of Oregon and included in each permitted
                    plan set.</li>
                </ul></li>
            <li>Smart (demand response capable) electric water heater or tankless water heater (EPS
                prerequisite)</li>
            <li>Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program</li>
            <li>A minimum of 3 additional labeled breakers that are either:
                <ul>
                    <li>One (1) EV + Double 40A/240V minimum Energy Storage circuits, with 72" clear wall space
                    labeled for future solar + energy storage + EV charging; or
                    <li>Dedicated labeled subpanel, with 72" clear wall space labeled for future solar + energy
                    storage + EV charging</li>
                </ul></li>
        </ul>
    """,
    "eps_40": """
        Energy Performance Score (EPS) “40%” with Specific Elements
        <ul>
            <li>EPS 40% Certification</li>
            <li>Smart (demand response capable) electric water heater or tankless water heater (EPS
            prerequisite)</li>
            <li>Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program</li>
            <li>A minimum of 5 labeled breakers that are either:
                <ul>
                    <li>Double 40A/240V minimum Solar + one (1) EV + Double 40A/240V minimum Energy Storage
                    circuits, with 72" clear wall space labeled for future solar + energy storage + EV
                    charging; or</li>
                    <li>Dedicated labeled subpanel, with 72" clear wall space labeled for future solar +
                    energy storage + EV charging</li>
                </ul></li>
        </ul>
    """,
    "ea_silver": """
        Earth Advantage Silver with Specific Elements
        <ul>
            <li>Earth Advantage Silver Certification</li>
            <li>Energy Trust Solar Ready:
                <ul>
                    <li>An approvable implementation is a roof top solar ready installation that includes a
                    junction box placed on an attic truss on a southern or western exposure with a metal
                    conduit path terminating in a junction box installed next to the main service panel.
                    Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                    in the service panel for a solar installation. The junction box is grounded. Details for
                    the installation are provided by Energy Trust of Oregon and included in each permitted
                    plan set.</li>
                </ul></li>
            <li>Advanced Energy Storage dedicated circuit: Labeled panel space for a double 40A/240V
            breaker with 72" clear wall space labeled for future solar + energy storage + EV charging</li>
            <li>Electric Vehicle Charger Ready</li>
            <li>Smart (demand response capable) electric water heater or tankless water heater (EPS
            prerequisite)</li>
            <li>Wi-Fi Smart “Learning” Thermostat per PGE Demand Response thermostat program</li>
        </ul>
    """,
    "ngbs_standard": """
        National Green Building Standard (NGBS) with Specific Elements
        <ul>
            <li>NGBS Silver Certification</li>
            <li>Energy Trust Solar Ready</li>
                <ul>
                    <li>An approvable implementation is a roof top solar ready installation that includes a
                    junction box placed on an attic truss on a southern or western exposure with a metal
                    conduit path terminating in a junction box installed next to the main service panel.
                    Space for two 40 amp, minimum amperage, breaker locations that are reserved and labeled
                    in the service panel for a solar installation. The junction box is grounded. Details for
                    the installation are provided by Energy Trust of Oregon and included in each permitted
                    plan set.</li>
                </ul></li>
            <li>Advanced Energy Storage dedicated circuit: Labeled panel space for a double 40A/240V
            breaker
                <ul>
                    <li>An approvable implementation is a main service electrical panel that has breaker
                    spaces reserved and labeled for an electric vehicle outlet, roof top solar, and a critical
                    load panel for an energy storage device.</li>
                </ul></li>
            <li>Electric Vehicle Charger Ready
                <ul>
                    <li>An approvable implementation is installation of a conduit from the main electrical
                    panel to a blank plate outlet on the garage wall that will allow the customer to install
                    the appropriate plug for their electric vehicle. Also included in the electrical panel
                    is space for a 40 amp, minimum amperage, breaker that is labeled and reserved in the
                    main panel for this feature.</li>
                </ul></li>
            <li>Smart (demand response capable) electric water heater or tankless water heater (EPS
            prerequisite)
                <ul>
                    <li>Such as a Rinnai tankless water heater, Model Number RUCS75iN that is Wi-Fi compatible</li>
                </ul></li>
            <li>Wi-Fi Smart “Learning” Thermostat per PGE Demand Response (DR) thermostat program
                <ul>
                    <li>Such as a Honeywell Lyric Round Programmable Thermostat, Part Number H8732WFH5002</li>
                </ul></li>
        </ul>
    """,
    "ea": """
        Earth Advantage
        <ul>
            <li>Earth Advantage Silver Certification</li>
            <li>Pre-Plumbed for Solar</li>
        </ul>
    """,
    "ngbs": """
        National Green Building Standard (NGBS)
        <ul>
            <li>NGBS Silver Certification</li>
            <li>Pre-Plumbed for Solar</li>
        </ul>
    """,
    "eps": """
        EPS
        <ul>
            <li>20% above code</li>
            <li>Pre-Plumbed for Solar</li>
        </ul>
    """,
}

COMPLIANCE_SHORTFORM_CHOICES = {
    k: dedent(v)
    for k, v in {
        "eps_20": """
        Energy Performance Score (EPS) “20%” with Specific Elements
            a. Earth Advantage Silver and EPS 20% Certification
            b. Energy Trust Solar Ready
            c. Advanced Energy Storage dedicated circuit
                • Labeled panel space for a double 40A/240V breaker
            d. Electric Vehicle Charger Ready
            e. Smart (demand response capable) electric water heater or tankless
                water heater (EPS prerequisite)
            f. Wi-Fi Smart “Learning” Thermostat per PGE Demand Response
                thermostat program
    """,
        "eps_30": """
        Energy Performance Score (EPS) “30%” with Specific Elements
            a. EPS 30% Certification
            b. Energy Trust Solar Ready:
            c. Smart (demand response capable) electric water heater or tankless
                water heater (EPS prerequisite)
            d. Wi-Fi Smart “Learning” Thermostat per PGE Demand Response
                thermostat program
            e. A minimum of 3 additional labeled breakers that are either:
                • One (1) EV + Double 40A/240V minimum Energy Storage circuits,
                  with 72" clear wall space labeled for future solar + energy storage
                  + EV charging; or
                • Dedicated labeled subpanel, with 72" clear wall space labeled for
                  future solar + energy storage + EV charging
    """,
        "eps_40": """
        Energy Performance Score (EPS) “40%” with Specific Elements
            a. EPS 40% Certification
            b. Smart (demand response capable) electric water heater or tankless
                water heater (EPS prerequisite)
            c. Wi-Fi Smart “Learning” Thermostat per PGE Demand Response
                thermostat program
            d. A minimum of 5 labeled breakers that are either:
                • Double 40A/240V minimum Solar + one (1) EV + Double 40A/240V
                  minimum Energy Storage circuits, with 72" clear wall space labeled
                  for future solar + energy storage + EV charging; or
                • Dedicated labeled subpanel, with 72" clear wall space labeled for
                  future solar + energy storage + EV charging
    """,
        "ea_silver": """
        Earth Advantage Silver with Specific Elements
            a. Earth Advantage Silver Certification
            b. Energy Trust Solar Ready:
            c. Advanced Energy Storage dedicated circuit: Labeled panel space for a
                double 40A/240V breaker with 72" clear wall space labeled for future
                solar + energy storage + EV charging
            d. Electric Vehicle Charger Ready
            e. Smart (demand response capable) electric water heater or tankless
               water heater (EPS prerequisite)
            f. Wi-Fi Smart “Learning” Thermostat per PGE Demand Response
                thermostat program
    """,
        "ngbs_standard": """
        National Green Building Standard (NGBS) with Specific Elements
            a. NGBS Silver Certification
            b. Energy Trust Solar Ready
            c. Advanced Energy Storage dedicated circuit: Labeled panel space for a
                double 40A/240V breaker
            d. Electric Vehicle Charger Ready
            e. Smart (demand response capable) electric water heater or tankless
                water heater (EPS prerequisite)
            f. Wi-Fi Smart “Learning” Thermostat per PGE Demand Response (DR)
                thermostat program
    """,
        "ea": """
    Earth Advantage
        a. Earth Advantage Silver Certification
        b. Pre-Plumbed for Solar
    """,
        "ngbs": """
    National Green Building Standard (NGBS)
        a. NGBS Silver Certification
        b. Pre-Plumbed for Solar
    """,
        "eps": """
    EPS
        a. 20% above code
        b. Pre-Plumbed for Solar
    """,
    }.items()
}

REEDS_CROSSING_COMPLIANCE_CHOICES = (
    ("eps_20", "Energy Performance Score (EPS) “20%” with Specific Elements"),
    ("eps_30", "Energy Performance Score (EPS) “30%” with Specific Elements"),
    ("eps_40", "Energy Performance Score (EPS) “40%” with Specific Elements"),
    ("ea_silver", "Earth Advantage Silver with Specific Elements"),
    ("ngbs_standard", "National Green Building Standard (NGBS) with Specific Elements"),
)
ROSEDALE_PARKS_COMPLIANCE_CHOICES = (
    ("ea", "Earth Advantage"),
    ("ngbs", "National Green Building Standard (NGBS)"),
    ("eps", "EPS"),
)
REEDS_CROSSING_COMPLIANCE_OPTIONS = dict(REEDS_CROSSING_COMPLIANCE_CHOICES)
ROSEDALE_PARKS_COMPLIANCE_OPTIONS = dict(ROSEDALE_PARKS_COMPLIANCE_CHOICES)
ETO_FIRE_2021_CHECKSUMS: List[Tuple[str, str]] = [
    ("A7AF23BC", "OR Perf Path Central 2022-FINAL.udr"),
    ("D6520E37", "OR Perf Path Zonal 2022-FINAL.udr"),
]
