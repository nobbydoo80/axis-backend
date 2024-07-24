"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "08/04/2021 23:45"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime

from axis.eep_program.program_builder import ProgramBuilder


class Eto(ProgramBuilder):
    name = "Energy Trust Oregon - 2014"
    slug = "eto"
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
    require_model_file = True
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = False
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = False
    is_multi_family = False

    visibility_date = datetime.date(2014, 1, 1)
    start_date = datetime.date(2014, 1, 1)
    end_date = datetime.date(2015, 1, 1)

    comment = """Energy Trust of Oregon 640S Program"""

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": True,
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
                "eto-contact_name",
                "eto-technician_name",
                "eto-payment_redirected",
                "eto-eto_pathway",
                "eto-low_income_incentive",
                "eto-solar_ready_builder_incentive",
                "eto-solar_ready_verifier_incentive",
                "eto-conditioned_area",
                "eto-building_type",
                "eto-num_stories",
                "eto-num_bedrooms",
                "eto-basement_type",
                "eto-solar_installed",
                "eto-solar_installer",
                "eto-water_heater_fuel",
                "eto-electric_meter_number",
                "eto-gas_meter_number",
                "eto-floor_type",
                "eto-floor_insulation_type",
                "eto-floor_r_value",
                "eto-framing_type",
                "eto-wall_type",
                "eto-wall_insulation_type",
                "eto-wall_r_value",
                "eto-window_u_value",
                "eto-window_shgc_value",
                "eto-window_area_glazing_pct",
                "eto-total_window_area",
                "eto-door_r_value",
                "eto-ceiling_type",
                "eto-ceiling_insulation_type",
                "eto-ceiling_r_value",
                "eto-skylights_u_value",
                "eto-skylights_shgc_value",
                "eto-primary_heat_type",
                "eto-primary_heat_afue",
                "eto-primary_heat_hspf",
                "eto-primary_heat_seer",
                "eto-primary_heat_cop",
                "eto-primary_heat_brand",
                "eto-primary_heat_model_no",
                "eto-primary_heat_serial_no",
                "eto-primary_heat_location",
                "eto-primary_heat_ecm",
                "eto-primary_heat_outdoor_unit_model_no",
                "eto-primary_heat_outdoor_unit_serial_no",
                "eto-air_conditioner_seer",
                "eto-air_conditioner_btu_hr",
                "eto-water_heater_heat_type",
                "eto-water_heater_gallons",
                "eto-water_heater_ef",
                "eto-water_heater_location",
                "eto-water_heater_brand",
                "eto-water_heater_model_no",
                "eto-water_heater_serial_no",
                "eto-ducts_inside",
                "eto-ducts_inside_pct",
                "eto-ducts_r_value",
                "eto-ducts_seal_with_mastic",
                "eto-duct_inspection_type",
                "eto-meets_mechanical_vent_req",
                "eto-hrv_erv_model_no",
                "eto-estar_dishwasher",
                "eto-dishwasher_ef",
                "eto-dishwasher_model_no",
                "eto-lighting_pct",
                "eto-num_fixtures",
                "eto-num_estar_fixtures_and_cfls",
                "eto-ventilation_type",
                "eto-home_volume",
                "eto-duct_leakage_cfm50",
                "eto-duct_leakage_ach50",
                "eto-notes",
                "eto-refrigerator-ef",
                "eto-refrigerator_model_no",
                "eto-flat_ceiling_r_value",
                "eto-flat_ceiling_insulation_type",
                "eto-vaulted_ceiling_r_value",
                "eto-vaulted_ceiling_insulation_type",
                "eto-scissor_truss_r_value",
                "eto-scissor_truss_insulation_type",
                "eto-above_grade_walls_r_value",
                "eto-above_grade_walls_insulation_type",
                "eto-below_grade_walls_r_value",
                "eto-below_grade_walls_insulation_type",
                "eto-floor_over_underheated_r_value",
                "eto-floor_over_underheated_insulation_type",
                "eto-over_garage_r_value",
                "eto-over_garage_insulation_type",
                "eto-rim_joist_r_value",
                "eto-rim_joist_insulation_type",
                "eto-washer-ef",
                "eto-washer-model",
                "eto-dryer-ef",
                "eto-dryer-model",
            ],
        },
    }
    texts = {
        "rater": {
            "eto-contact_name": "ETO-640S 1.04 Contact Name",
            "eto-technician_name": "ETO-640S 1.06 Technician Name",
            "eto-payment_redirected": "ETO-640S 1.02 Is this payment redirected?",
            "eto-eto_pathway": "ETO-640S 1.07 Energy Trust Pathway",
            "eto-low_income_incentive": "ETO-640S 1.08 Low Income Incentive",
            "eto-solar_ready_builder_incentive": "ETO-640S 1.09 Solar Ready Builder Incentive",
            "eto-solar_ready_verifier_incentive": "ETO-640S 1.10 Solar Ready Verifier Incentive",
            "eto-conditioned_area": "ETO-640S 2.05 Total Conditioned Area",
            "eto-building_type": "ETO-640S 2.07 Building Type",
            "eto-num_stories": "ETO-640S 2.08 Number of Stories",
            "eto-num_bedrooms": "ETO-640S 2.10 Number of Bedrooms",
            "eto-basement_type": "ETO-640S 2.11 Foundation Type",
            "eto-solar_installed": "ETO-640S 2.15 Solar Installed",
            "eto-solar_installer": "ETO-640S 2.16 Solar Installer Name/Company",
            "eto-water_heater_fuel": "ETO-640S 2.12 Water Heater Fuel",
            "eto-electric_meter_number": 'ETO-640S 2.17 Electric Meter Number (must be permanent meter number).  Enter "N/A" if not applicable.',
            "eto-gas_meter_number": 'ETO-640S 2.18 Gas Meter Number (must be permanent meter number).  Enter "N/A" if not applicable.',
            "eto-floor_type": "ETO-640S 3.08 Floor Type",
            "eto-floor_insulation_type": "ETO-640S 3.09 Floor Insulation Type",
            "eto-floor_r_value": "ETO-640S 3.10 Floor Insulation R-value",
            "eto-framing_type": "ETO-640S 3.01 Framing Type",
            "eto-wall_type": "ETO-640S 3.05 Wall Type",
            "eto-wall_insulation_type": "ETO-640S 3.06 Wall Insulation Type",
            "eto-wall_r_value": "ETO-640S 3.07 Wall Insulation R-value",
            "eto-window_u_value": "ETO-640S 3.12 Window U-value",
            "eto-window_shgc_value": "ETO-640S 3.13 Window SHGC",
            "eto-window_area_glazing_pct": "ETO-640S 3.16  Window Area (Glazing) Percentage",
            "eto-total_window_area": "ETO-640S 3.17 Window Area Total",
            "eto-door_r_value": "ETO-640S 3.11 Door R-value",
            "eto-ceiling_type": "ETO-640S 3.02 Ceiling Type",
            "eto-ceiling_insulation_type": "ETO-640S 3.03 Ceiling Insulation Type",
            "eto-ceiling_r_value": "ETO-640S 3.04 Ceiling Insulation R-value",
            "eto-skylights_u_value": "ETO-640S 3.14 Skylight U-value",
            "eto-skylights_shgc_value": "ETO-640S 3.15 Skylight SHGC",
            "eto-primary_heat_type": "ETO-640S 3.27 Primary Heating Equipment",
            "eto-primary_heat_afue": "ETO-640S 3.28 Primary Heating Equipment AFUE",
            "eto-primary_heat_hspf": "ETO-640S 3.29 Primary Heating Equipment HSPF",
            "eto-primary_heat_seer": "ETO-640S 3.30 Primary Heating Equipment SEER",
            "eto-primary_heat_cop": "ETO-640S 3.31 Primary Heating Equipment COP",
            "eto-primary_heat_brand": "ETO-640S 3.32 Primary Heating Equipment Brand",
            "eto-primary_heat_model_no": "ETO-640S 3.33 Primary Heating Equipment Model Number",
            "eto-primary_heat_serial_no": "ETO-640S 3.34 Primary Heating Equipment Serial Number",
            "eto-primary_heat_location": "ETO-640S 3.35 Primary Heating Equipment Location",
            "eto-primary_heat_ecm": "ETO-640S 3.36 Primary Heating Equipment ECM",
            "eto-primary_heat_outdoor_unit_model_no": "ETO-640S 3.37 Heat Pump Outdoor Unit Model Number",
            "eto-primary_heat_outdoor_unit_serial_no": "ETO-640S 3.38 Heat Pump Outdoor Unit Serial Number",
            "eto-air_conditioner_seer": "ETO-640S 3.24 Air Conditioning SEER",
            "eto-air_conditioner_btu_hr": "ETO-640S 3.25 Air Conditioning BTU/Hr",
            "eto-water_heater_heat_type": "ETO-640S 3.40 Water Heater Type",
            "eto-water_heater_gallons": "ETO-640S 3.41 Water Heater Gallons",
            "eto-water_heater_ef": "ETO-640S 3.42 Water Heater EF",
            "eto-water_heater_location": "ETO-640S 3.43 Water Heater Location",
            "eto-water_heater_brand": "ETO-640S 3.44 Water Heater Brand",
            "eto-water_heater_model_no": "ETO-640S 3.45 Water Heater Model Number",
            "eto-water_heater_serial_no": "ETO-640S 3.46 Water Heater Serial Number",
            "eto-ducts_inside": "ETO-640S 3.50 Ducts Inside",
            "eto-ducts_inside_pct": "ETO-640S 3.51 Ducts Inside Percentage",
            "eto-ducts_r_value": "ETO-640S 3.52 Duct Insulation R-value",
            "eto-ducts_seal_with_mastic": "ETO-640S 3.53 Duct Seal with Mastic",
            "eto-duct_inspection_type": "ETO-640S 3.54 If claiming incentive for ducts inside, select one of the following",
            "eto-meets_mechanical_vent_req": "ETO-640S 3.48 Meets Energy Trust Mechanical Ventilation Requirements?",
            "eto-hrv_erv_model_no": "ETO-640S 3.49 Ventilation System HRV/ERV Model Number",
            "eto-estar_dishwasher": "ETO-640S 3.21 ENERGY STAR® Dishwasher?",
            "eto-dishwasher_ef": "ETO-640S 3.22 Dishwasher EF",
            "eto-dishwasher_model_no": "ETO-640S 7.05 Appliances: Dishwasher Model Number",
            "eto-lighting_pct": "ETO-640S 3.18 Lighting Indoor and Outdoor Percentage",
            "eto-num_fixtures": "ETO-640S 3.19 Number of Lighting Fixtures",
            "eto-num_estar_fixtures_and_cfls": "ETO-640S 3.20 Number of ENERGY STAR® fixtures or CFLs",
            "eto-ventilation_type": "ETO-640S 3.47 Ventilation System Type",
            "eto-home_volume": "ETO-640S 2.06 House Volume",
            "eto-duct_leakage_cfm50": "ETO-640S 4.01 Duct Leakage (CFM)",
            "eto-duct_leakage_ach50": "ETO-640S 4.02 Whole House Leakage Air Changes per Hour (ACH)",
            "eto-notes": "ETO-640S 5.01 Notes",
            "eto-refrigerator-ef": "ETO-640S 7.03 Appliances: Refrigerator EF",
            "eto-refrigerator_model_no": "ETO-640S 7.04 Appliances: Refrigerator Model #",
            "eto-flat_ceiling_r_value": "ETO-640S 6.01 Insulation Details: Flat Ceiling R-Value",
            "eto-flat_ceiling_insulation_type": "ETO-640S 6.02 Insulation Details: Flat Ceiling Insulation Type",
            "eto-vaulted_ceiling_r_value": "ETO-640S 6.03 Insulation Details: Vaulted Ceiling R-Value",
            "eto-vaulted_ceiling_insulation_type": "ETO-640S 6.04 Insulation Details: Vaulted Ceiling Insulation Type",
            "eto-scissor_truss_r_value": "ETO-640S 6.05 Insulation Details: Scissor Truss R-Value",
            "eto-scissor_truss_insulation_type": "ETO-640S 6.06 Insulation Details: Scissor Truss Insulation Type",
            "eto-above_grade_walls_r_value": "ETO-640S 6.07 Insulation Details: Above Grade Walls R-Value",
            "eto-above_grade_walls_insulation_type": "ETO-640S 6.08 Insulation Details: Above Grade Walls Insulation Type",
            "eto-below_grade_walls_r_value": "ETO-640S 6.09 Insulation Details: Below Grade Walls R-Value",
            "eto-below_grade_walls_insulation_type": "ETO-640S 6.10 Insulation Details: Below Grade Walls Insulation Type",
            "eto-floor_over_underheated_r_value": "ETO-640S 6.11 Insulation Details: Floor Over Unheated Space R-Value",
            "eto-floor_over_underheated_insulation_type": "ETO-640S 6.12 Insulation Details: Floor Over Unheated Space Insulation Type",
            "eto-over_garage_r_value": "ETO-640S 6.13 Insulation Details: Floor Over Garage R-Value",
            "eto-over_garage_insulation_type": "ETO-640S 6.14 Insulation Details: Floor Over Garage Insulation Type",
            "eto-rim_joist_r_value": "ETO-640S 6.15 Insulation Details: Rim Joist R-Value",
            "eto-rim_joist_insulation_type": "ETO-640S 6.16 Insulation Details: Rim Joist Insulation Type",
            "eto-washer-ef": "ETO-640S 7.05 Appliances: Clothes Washer EF",
            "eto-washer-model": "ETO-640S 7.06 Appliances: Clothes Washer Model #",
            "eto-dryer-ef": "ETO-640S 7.07 Appliances: Dryer EF",
            "eto-dryer-model": "ETO-640S 7.08 Appliances: Dryer Model #",
        },
    }
    descriptions = {
        "rater": {},
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
            ): [
                "eto-payment_redirected",
                "eto-primary_heat_ecm",
                "eto-ducts_inside",
                "eto-ducts_seal_with_mastic",
                "eto-estar_dishwasher",
            ],
            (
                "Pathway 1",
                "Pathway 2",
                "Pathway 3",
                "Pathway 4",
                "Pathway 5",
                "Percent Improvement",
            ): [
                "eto-eto_pathway",
            ],
            (
                "Yes qualifies verifier for $250 incentive",
                "No doesn't meet Low Income requirements",
            ): [
                "eto-low_income_incentive",
            ],
            (
                "$200 Solar Ready Electric (SRPV)",
                "$200 Solar Ready Water Heating (SRWH)",
                "Both",
                "None",
            ): [
                "eto-solar_ready_builder_incentive",
            ],
            (
                "$50 Solar Ready Electric (SRPV)",
                "$50 Solar Ready Water Heating (SRWH)",
                "Both",
                "None",
            ): [
                "eto-solar_ready_verifier_incentive",
            ],
            (
                "Unattached",
                "Attached",
            ): [
                "eto-building_type",
            ],
            (
                "Full Basement",
                "Half Basement",
                "Crawlspace",
                "Slab Floor",
                "Other/More Than One (add comment)",
            ): [
                "eto-basement_type",
            ],
            (
                "Solar Electric (PV)",
                "Solar Water Heating (SWH)",
                "Both",
                "None",
            ): [
                "eto-solar_installed",
            ],
            (
                "Gas",
                "Electric",
                "Other Electric (add comment)",
            ): [
                "eto-water_heater_fuel",
            ],
            (
                "Slab",
                "Perimeter Slab",
                "Frame",
            ): [
                "eto-floor_type",
            ],
            (
                "Batts",
                "Blown-in",
                "Rigid foam board",
                "Spray foam",
                "Other/Combination",
            ): [
                "eto-floor_insulation_type",
                "eto-wall_insulation_type",
                "eto-ceiling_insulation_type",
            ],
            (
                "Standard",
                "Intermediate",
                "Advanced",
            ): [
                "eto-framing_type",
            ],
            (
                "Above Grade Wall",
                "Below Grade Wall",
            ): [
                "eto-wall_type",
            ],
            (
                "Flat Ceiling",
                "Scissor Truss",
            ): [
                "eto-ceiling_type",
            ],
            (
                "Gas Fireplace",
                "Gas Unit Heater",
                "Gas Furnace",
                "Gas Boiler",
                "Electric Heat Pump - Air Source Ducted",
                "Electric Heat Pump - Mini Split Non-Ducted",
                "Electric Heat Pump - Mini Split Ducted",
                "Electric Heat Pump - Ground Source",
                "Other Gas (add comment)",
                "Other Electric (add comment)",
            ): [
                "eto-primary_heat_type",
            ],
            (
                "Storage",
                "Tankless",
            ): [
                "eto-water_heater_heat_type",
            ],
            (
                "Ducts Tested",
                "Visual Inspection per RTF Specs",
            ): [
                "eto-duct_inspection_type",
            ],
            (
                "Yes",
                "Untestable",
            ): [
                "eto-meets_mechanical_vent_req",
            ],
            (
                "Exhaust",
                "Supply",
                "Air Cycler",
                "HRV/ERV",
            ): [
                "eto-ventilation_type",
            ],
        },
    }
    instrument_types = {
        "float": [
            "eto-conditioned_area",
            "eto-floor_r_value",
            "eto-wall_r_value",
            "eto-window_u_value",
            "eto-window_shgc_value",
            "eto-window_area_glazing_pct",
            "eto-total_window_area",
            "eto-door_r_value",
            "eto-ceiling_r_value",
            "eto-skylights_u_value",
            "eto-skylights_shgc_value",
            "eto-primary_heat_afue",
            "eto-primary_heat_hspf",
            "eto-primary_heat_seer",
            "eto-primary_heat_cop",
            "eto-air_conditioner_seer",
            "eto-air_conditioner_btu_hr",
            "eto-water_heater_gallons",
            "eto-water_heater_ef",
            "eto-ducts_inside_pct",
            "eto-ducts_r_value",
            "eto-dishwasher_ef",
            "eto-lighting_pct",
            "eto-home_volume",
            "eto-duct_leakage_cfm50",
            "eto-duct_leakage_ach50",
        ],
        "integer": [
            "eto-num_stories",
            "eto-num_bedrooms",
            "eto-num_fixtures",
            "eto-num_estar_fixtures_and_cfls",
        ],
    }
    optional_measures = [
        "eto-contact_name",
        "eto-technician_name",
        "eto-low_income_incentive",
        "eto-solar_ready_builder_incentive",
        "eto-solar_ready_verifier_incentive",
        "eto-building_type",
        "eto-solar_installed",
        "eto-solar_installer",
        "eto-floor_type",
        "eto-floor_insulation_type",
        "eto-framing_type",
        "eto-wall_type",
        "eto-wall_insulation_type",
        "eto-window_area_glazing_pct",
        "eto-total_window_area",
        "eto-door_r_value",
        "eto-ceiling_type",
        "eto-ceiling_insulation_type",
        "eto-skylights_u_value",
        "eto-skylights_shgc_value",
        "eto-primary_heat_afue",
        "eto-primary_heat_hspf",
        "eto-primary_heat_seer",
        "eto-primary_heat_cop",
        "eto-primary_heat_brand",
        "eto-primary_heat_model_no",
        "eto-primary_heat_location",
        "eto-primary_heat_ecm",
        "eto-primary_heat_outdoor_unit_model_no",
        "eto-primary_heat_outdoor_unit_serial_no",
        "eto-air_conditioner_seer",
        "eto-air_conditioner_btu_hr",
        "eto-water_heater_gallons",
        "eto-water_heater_location",
        "eto-water_heater_brand",
        "eto-water_heater_model_no",
        "eto-ducts_r_value",
        "eto-ducts_seal_with_mastic",
        "eto-duct_inspection_type",
        "eto-meets_mechanical_vent_req",
        "eto-hrv_erv_model_no",
        "eto-estar_dishwasher",
        "eto-dishwasher_ef",
        "eto-dishwasher_model_no",
        "eto-num_fixtures",
        "eto-num_estar_fixtures_and_cfls",
        "eto-ventilation_type",
        "eto-duct_leakage_cfm50",
        "eto-notes",
        "eto-refrigerator-ef",
        "eto-refrigerator_model_no",
        "eto-flat_ceiling_r_value",
        "eto-flat_ceiling_insulation_type",
        "eto-vaulted_ceiling_r_value",
        "eto-vaulted_ceiling_insulation_type",
        "eto-scissor_truss_r_value",
        "eto-scissor_truss_insulation_type",
        "eto-above_grade_walls_r_value",
        "eto-above_grade_walls_insulation_type",
        "eto-below_grade_walls_r_value",
        "eto-below_grade_walls_insulation_type",
        "eto-floor_over_underheated_r_value",
        "eto-floor_over_underheated_insulation_type",
        "eto-over_garage_r_value",
        "eto-over_garage_insulation_type",
        "eto-rim_joist_r_value",
        "eto-rim_joist_insulation_type",
        "eto-washer-ef",
        "eto-washer-model",
        "eto-dryer-ef",
        "eto-dryer-model",
    ]
    suggested_response_flags = {
        "rater": {
            "eto-basement_type": {
                "Other/More Than One (add comment)": {
                    "comment_required": True,
                },
            },
            "eto-water_heater_fuel": {
                "Other Electric (add comment)": {
                    "comment_required": True,
                },
            },
            "eto-floor_insulation_type": {
                "Other/Combination": {
                    "comment_required": True,
                },
            },
            "eto-wall_insulation_type": {
                "Other/Combination": {
                    "comment_required": True,
                },
            },
            "eto-ceiling_insulation_type": {
                "Other/Combination": {
                    "comment_required": True,
                },
            },
            "eto-primary_heat_type": {
                "Other Gas (add comment)": {
                    "comment_required": True,
                },
                "Other Electric (add comment)": {
                    "comment_required": True,
                },
            },
        },
    }
