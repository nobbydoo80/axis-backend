__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import datetime
import logging
from collections import OrderedDict

from axis.eep_program.program_builder.base import ProgramBuilder

log = logging.getLogger(__name__)


class NeeaBpa(ProgramBuilder):
    name = "Utility Incentive V2 – Single Family Performance Path"
    slug = "neea-bpa"
    owner = "neea"

    is_qa_program = False
    opt_in = False

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

    manual_transition_on_certify = True

    require_rater_of_record = False
    require_energy_modeler = False
    require_field_inspector = False

    allow_sampling = False
    allow_metro_sampling = False

    require_resnet_sampling_provider = False

    is_legacy = False
    is_public = False

    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2019, 4, 21)
    start_date = datetime.date(2019, 4, 21)

    require_home_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": False,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": False,
        "hvac": False,
        "utility": True,
        "rater": True,
        "provider": False,
        "qa": False,
    }
    measures = {
        "rater": {
            "default": [
                "neea-heating_system_config",
                "neea-heating_source",
                "neea-water_heater_tier",
                "estar_std_refrigerators_installed",
                "estar_dishwasher_installed",
                "estar_front_load_clothes_washer_installed",
                "neea-clothes_dryer_tier",
                "cfl_installed",
                "led_installed",
                "total_installed_lamps",
                "smart_thermostat_installed",
                "qty_shower_head_1p5",
                "qty_shower_head_1p75",
                "neea-major-load-equipment",
                "bpa_upload_docs",
                "hvac-combo",
                "hvac-cooling-combo",
                "water-heater-combo",
                "ventilation-combo",
                "refrigerator-combo",
                "clothes-washer-combo",
                "clothes-dryer-combo",
                "dishwasher-combo",
                "range-oven-combo",
                "solar-combo",
                "house-fans-combo",
                "hrv-combo",
                "heat-pump-water-heater-serial-number",
                "heat-pump-heater-serial-number",
                "smart-thermostat-combo",
                "other-combo",
                "neea-electric_meter_number",
                "neea-gas_meter_number",
                "neea-program_redirected",
                "neea-hvac-distributor",
                "neea-hpwh-contractor",
                "neea-hpwh-distributor",
            ],
        },
    }
    texts = {
        "rater": {
            "neea-heating_system_config": "Heating System Configuration",
            "neea-heating_source": "Primary Heat Source",
            "neea-water_heater_tier": "Water Heater Tier",
            "estar_std_refrigerators_installed": "ENERGY STAR® Refrigerator Installed.  If yes, enter brand & model number "
            "using optional checklist question",
            "estar_dishwasher_installed": "ENERGY STAR® Dishwasher Installed.  If yes, enter brand & model number "
            "using optional checklist question",
            "estar_front_load_clothes_washer_installed": "ENERGY STAR® Clothes Washer Installed.  If yes, enter brand & model number "
            "using optional checklist question",
            "neea-clothes_dryer_tier": "Clothes Dryer Tier.  If ENERGY STAR®, Tier 2, or Tier 3, enter brand & model "
            "number using optional checklist question",
            "cfl_installed": "Qty CFL Lamps",
            "led_installed": "Qty LED Lamps",
            "total_installed_lamps": "Qty Total Lamps",
            "smart_thermostat_installed": "Smart Thermostat Installed.  If yes, enter brand & model number "
            "using optional checklist question",
            "qty_shower_head_1p5": "Qty 1.5 gpm Showerheads",
            "qty_shower_head_1p75": "Qty 1.75 gpm Showerheads",
            "neea-major-load-equipment": "Major Load Consuming Equipment",
            "bpa_upload_docs": "Upload documents and/or field checklists required by program",
            "hvac-combo": "HVAC Combined or Heating-only Brand and Model Number",
            "hvac-cooling-combo": "HVAC Cooling-Only Brand and Model",
            "water-heater-combo": "Water Heater Brand and Model Number",
            "ventilation-combo": "Ventilation Brand and Model Number",
            "refrigerator-combo": "Refrigerator Brand and Model Number",
            "clothes-washer-combo": "Clothes Washer Brand and Model Number",
            "clothes-dryer-combo": "Dryer Brand and Model Number",
            "dishwasher-combo": "Dishwasher Brand and Model Number",
            "range-oven-combo": "Range Oven Brand and Model Number",
            "solar-combo": "Solar / PV Brand and Model Number",
            "house-fans-combo": "House Fan(s) Brand and Model Number",
            "hrv-combo": "HRV Brand and Model Number",
            "heat-pump-water-heater-serial-number": "Heat Pump Water Heater Serial Number",
            "smart-thermostat-combo": "Smart Thermostat Brand and Model Number",
            "other-combo": "Other Brand and Model Number",
            "neea-electric_meter_number": "Electric Meter Number (must be permanent meter number).",
            "neea-gas_meter_number": "Gas Meter Number (must be permanent meter number).",
            "heat-pump-heater-serial-number": "Space Heating Heat Pump Serial Number",
            "neea-program_redirected": "Utility Incentive Payment Redirected",
            "neea-hvac-distributor": "HVAC Distributor",
            "neea-hpwh-contractor": "Heat Pump Water Heater Contractor",
            "neea-hpwh-distributor": "Heat Pump Water Heater Distributor",
        },
    }
    descriptions = {
        "rater": {
            "neea-water_heater_tier": "Refer to <a href='http://neea.org/docs/default-source/"
            "advanced-water-heater-specification/qualified-products-list.pdfmore'>"
            "this</a> for more information",
            "neea-clothes_dryer_tier": "Refer to <a href='https://conduitnw.org/Pages/File.aspx?rid=2844'>this</a> "
            "and <a href='https://conduitnw.org/_layouts/Conduit/FileHandler.ashx?RID=2844'>"
            "this</a> for more information",
            "hvac-combo": "Please enter the model / serial numbers",
            "hvac-cooling-combo": "Please enter the model / serial numbers",
            "water-heater-combo": "Please enter the model / serial numbers",
            "ventilation-combo": "Please enter the model / serial numbers",
            "refrigerator-combo": "Please enter the model / serial numbers",
            "clothes-washer-combo": "Please enter the model / serial numbers",
            "clothes-dryer-combo": "Please enter the model / serial numbers",
            "dishwasher-combo": "Please enter the model / serial numbers",
            "range-oven-combo": "Please enter the model / serial numbers",
            "solar-combo": "Please enter the model / serial numbers",
            "house-fans-combo": "Please enter the model / serial numbers",
            "hrv-combo": "Please enter the model / serial numbers",
            "heat-pump-water-heater-serial-number": "Please enter the model / serial numbers",
            "smart-thermostat-combo": "Please enter the model / serial numbers",
            "other-combo": "Please enter the model / serial numbers",
            "neea-hvac-distributor": "HVAC Distributor",
            "neea-hpwh-contractor": "HPWH Contractor (Required by PSE)",
            "neea-hpwh-distributor": "HPWH Distributor",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Central",
                "Zonal",
                "All",
            ): [
                "neea-heating_system_config",
            ],
            (
                "Heat Pump",
                "Heat Pump - Geothermal/Ground Source",
                "Heat Pump - w/ Gas Backup",
                "Heat Pump - Mini Split",
                "Gas with AC",
                "Gas No AC",
                "Zonal Electric",
                "Propane Oil or Wood",
                "Hydronic Radiant Electric Boiler",
                "Hydronic Radiant Gas Boiler",
                "Hydronic Radiant Heat Pump",
            ): [
                "neea-heating_source",
            ],
            (
                "Electric Resistance",
                "HPWH Tier 1",
                "HPWH Tier 2",
                "HPWH Tier 3",
                "Gas Conventional EF < 0.67",
                "Gas Conventional EF ≥ 0.67",
                "Gas Conventional EF ≥ 0.70",
                "Gas Tankless EF ≥ 0.82",
                "Gas Tankless EF ≥ 0.90",
                "Propane Tank",
                "Propane Tankless",
            ): [
                "neea-water_heater_tier",
            ],
            (
                "Yes",
                "No",
            ): [
                "estar_std_refrigerators_installed",
                "estar_dishwasher_installed",
                "estar_front_load_clothes_washer_installed",
                "smart_thermostat_installed",
                "bpa_upload_docs",
                "neea-program_redirected",
            ],
            (
                "ENERGY STAR®",
                "Tier 2",
                "Tier 3",
                "None",
            ): [
                "neea-clothes_dryer_tier",
            ],
            (
                "No",
                "Yes",
            ): [
                "neea-major-load-equipment",
            ],
        },
    }
    instrument_types = {
        "integer": [
            "cfl_installed",
            "led_installed",
            "total_installed_lamps",
            "qty_shower_head_1p5",
            "qty_shower_head_1p75",
        ],
    }
    optional_measures = [
        "bpa_upload_docs",
        "range-oven-combo",
        "solar-combo",
        "house-fans-combo",
        "hrv-combo",
        "heat-pump-water-heater-serial-number",
        "heat-pump-heater-serial-number",
        "other-combo",
        "neea-electric_meter_number",
        "neea-gas_meter_number",
        "neea-hvac-distributor",
        "neea-hpwh-contractor",
        "neea-hpwh-distributor",
    ]
    suggested_response_flags = {
        "rater": {
            "neea-major-load-equipment": {
                "Yes": {
                    "comment_required": True,
                },
            },
            "bpa_upload_docs": {
                "Yes": {
                    "comment_required": True,
                },
            },
        },
    }

    instrument_conditions = {
        "default": {},
        "rater": {
            "instrument": {
                "estar_std_refrigerators_installed": {
                    ("one", ("Yes",)): ["refrigerator-combo"],
                },
                "estar_dishwasher_installed": {
                    ("one", ("Yes",)): ["dishwasher-combo"],
                },
                "estar_front_load_clothes_washer_installed": {
                    ("one", ("Yes",)): ["clothes-washer-combo"],
                },
                "neea-clothes_dryer_tier": {
                    (
                        "one",
                        (
                            "ENERGY STAR®",
                            "Tier 2",
                            "Tier 3",
                        ),
                    ): ["clothes-dryer-combo"],
                },
                "smart_thermostat_installed": {
                    ("one", ("Yes",)): ["smart-thermostat-combo"],
                },
            },
            "simulation": {
                "floorplan.remrate_target.has_heat_pumps": {
                    ("one", True): [
                        "heat-pump-heater-serial-number",
                    ]
                },
                "floorplan.remrate_target.has_heat_pump_water_heaters": {
                    ("one", True): [
                        "heat-pump-water-heater-serial-number",
                        "neea-hpwh-contractor",
                        "neea-hpwh-distributor",
                    ]
                },
            },
        },
    }

    annotations = OrderedDict(
        (
            (
                "certified-builtgreen",
                {
                    "name": "BuiltGreen",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "3-star,4-star,5-star",
                    "is_required": "False",
                },
            ),
            (
                "certified-doe-zero-ready",
                {
                    "name": "DOE Zero Energy Ready Home™",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "certified-earth-advantage",
                {
                    "name": "Earth Advantage Certified Home",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Silver,Gold,Platinum,Net Zero Ready,Net Zero",
                    "is_required": "False",
                },
            ),
            (
                "certified-eto-eps",
                {
                    "name": "Energy Trust of Oregon",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "certified-efl",
                {
                    "name": "Environments for Living",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Gold,Platinum,Certified Green,Diamond",
                    "is_required": "False",
                },
            ),
            (
                "certified-estar",
                {
                    "name": "EPA ENERGY STAR®",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "certified-hers",
                {
                    "name": "HERS",
                    "data_type": "integer",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "certified-leed",
                {
                    "name": "LEED",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Silver,Gold,Platinum",
                    "is_required": "False",
                },
            ),
            (
                "certified-mthouse",
                {
                    "name": "Montana House",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "certified-nat-gbs",
                {
                    "name": "National Green Building Standard",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Bronze,Silver,Gold,Emerald",
                    "is_required": "False",
                },
            ),
            (
                "certified-other",
                {
                    "name": "Other Certifications",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "certified-phius",
                {
                    "name": "PHIUS+ Certified",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "project-start-nr",
                {
                    "name": "Project Start",
                    "data_type": "date",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
        )
    )
