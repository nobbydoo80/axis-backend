"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime
from collections import OrderedDict


class NeeaPrescriptive2015(ProgramBuilder):
    name = "NW ENERGY STAR® Version 3, natl Rev 8: Multifamily"
    slug = "neea-prescriptive-2015"
    owner = "neea"
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
    require_input_data = False
    require_rem_data = False
    require_model_file = False
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

    visibility_date = datetime.date(2015, 7, 1)
    start_date = datetime.date(2015, 7, 1)
    end_date = datetime.date(2017, 6, 30)

    comment = (
        """Northwest 2015 ENERGY STAR® Version 3, natl Rev 8: Multifamily (Prescriptive) Program"""
    )

    require_home_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": False,
    }
    measures = {
        "rater": {
            "default": [
                "estar-rater-plan-review",
                "estar-rater-field-inspection",
                "estar-hvac-design-report",
                "nwes-20-ptcs-info",
                "nwes-30-performancetest-ach50",
                "nwes-31-performancetest-net-caz",
                "nwes-32-performancetest-windy-conditions-no-te",
                "nwes-33-co-monitor-present",
                "nwes-34-performance-test-duct-leakage",
                "nwes-35-performancetest-conditioned-space-sqft",
                "nwes-41-inspection-notes-enter-notes-by-selectin",
            ],
        },
    }
    texts = {
        "rater": {
            "estar-rater-plan-review": "ESTAR 1.0 Completed Rater Plan Review Checklist?",
            "estar-rater-field-inspection": "ESTAR 2.0 Completed Rater Field Inspection Checklist?",
            "estar-hvac-design-report": "ESTAR 3.0 Collected HVAC System Design Report?",
            "nwes-20-ptcs-info": "NWES 2.0 Enter the name, ID, and credential type of the Provider approved performance tester (e.g. Bob Smith, 12345, PTCS) or “N/A” if not applicable.",
            "nwes-30-performancetest-ach50": "NWES 3.0 PerformanceTest - ACH50",
            "nwes-31-performancetest-net-caz": "NWES 3.1 PerformanceTest - Net CAZ",
            "nwes-32-performancetest-windy-conditions-no-te": "NWES 3.2 PerformanceTest - Windy conditions (No test required)",
            "nwes-33-co-monitor-present": "NWES 3.3 CO Monitor present?",
            "nwes-34-performance-test-duct-leakage": "NWES 3.4 Performance Test - Duct Leakage to Exterior",
            "nwes-35-performancetest-conditioned-space-sqft": "NWES 3.5 PerformanceTest - Conditioned Space (sqft)",
            "nwes-41-inspection-notes-enter-notes-by-selectin": 'NWES 4.1 Inspection Notes (enter notes by selecting the "Add Comment" button below)',
        },
    }
    descriptions = {
        "rater": {
            "estar-rater-plan-review": """Has the Rater Plan Review been completed""",
            "estar-rater-field-inspection": """Has the Rater Field Inspection been completed""",
            "estar-hvac-design-report": """Has the Rater collected the HVAC System Design Report?""",
            "nwes-20-ptcs-info": """Enter the name, ID, and credential type of the Provider approved performance tester (e.g. Bob Smith, 12345, PTCS) or “N/A” if not applicable.""",
            "nwes-33-co-monitor-present": """Select "N/A" for a residence with no combustion appliances within conditioned space.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
            ): [
                "estar-rater-plan-review",
                "estar-rater-field-inspection",
                "estar-hvac-design-report",
            ],
            (
                "No Windy Conditions",
                "Windy Conditions",
            ): [
                "nwes-32-performancetest-windy-conditions-no-te",
            ],
            (
                "Yes",
                "No",
                "N/A",
            ): [
                "nwes-33-co-monitor-present",
            ],
            (
                "As comment",
                "No notes",
            ): [
                "nwes-41-inspection-notes-enter-notes-by-selectin",
            ],
        },
    }
    instrument_types = {
        "float": [
            "nwes-30-performancetest-ach50",
            "nwes-35-performancetest-conditioned-space-sqft",
        ],
    }
    suggested_response_flags = {
        "rater": {
            "estar-rater-plan-review": {
                "No": {
                    "comment_required": True,
                },
            },
            "estar-rater-field-inspection": {
                "No": {
                    "comment_required": True,
                },
            },
            "estar-hvac-design-report": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-33-co-monitor-present": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-41-inspection-notes-enter-notes-by-selectin": {
                "As comment": {
                    "comment_required": True,
                },
            },
        },
    }
    annotations = OrderedDict(
        (
            (
                "bop",
                {
                    "name": "BOP",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "NW BOP 1 MF,NW BOP 2 MF,2011 ID/MT BOP 1,2011 ID/MT BOP 2,2011 WA BOP 1 - Ducts in Conditioned Space,2011 WA BOP 1 - Equipment Upgrade,2011 WA BOP 1 - Envelope Pathway,2011 WA BOP 2 - Zonal Electric; Propane and Oil,2012 OR BOP 1 - Ducts in Conditioned Space,2012 OR BOP 1 - Equipment Upgrade,2012 OR BOP 1 - Envelope Pathway,2012 OR BOP 2 - Zonal Electric; Propane and Oil,Oregon Premium Performance Home (OPPH)",
                    "is_required": "True",
                },
            ),
            (
                "clothes-washer-brand",
                {
                    "name": "Clothes Washer Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "clothes-washer",
                {
                    "name": "Clothes Washer Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "clothes-dryer-brand",
                {
                    "name": "Dryer Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "clothes-dryer",
                {
                    "name": "Dryer Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "house-fans-brand",
                {
                    "name": "House Fan(s) Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "house-fans",
                {
                    "name": "House Fan(s) Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "hrv-brand",
                {
                    "name": "HRV Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "hrv",
                {
                    "name": "HRV Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "hvac-brand",
                {
                    "name": "HVAC Combined / Heating Only Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "hvac",
                {
                    "name": "HVAC Combined / Heating Only Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "hvac-cooling-brand",
                {
                    "name": "HVAC Cooling-Only Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "hvac-cooling",
                {
                    "name": "HVAC Cooling-Only Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "other-brand",
                {
                    "name": "Other Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "other",
                {
                    "name": "Other Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "heat-source",
                {
                    "name": "Primary Heat Source",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Heat Pump,Heat Pump - Geothermal/Ground Source,Heat Pump - w/ Gas Backup,Heat Pump - Mini Split,Gas with AC,Gas No AC,Zonal Electric,Propane Oil or Wood",
                    "is_required": "True",
                },
            ),
            (
                "project-start",
                {
                    "name": "Project Start",
                    "data_type": "date",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "range-oven-brand",
                {
                    "name": "Range Oven Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "range-oven",
                {
                    "name": "Range Oven Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "refrigerator-brand",
                {
                    "name": "Refrigerator Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "refrigerator",
                {
                    "name": "Refrigerator Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "solar-brand",
                {
                    "name": "Solar / PV Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "solar",
                {
                    "name": "Solar / PV Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "ventilation-brand",
                {
                    "name": "Ventilation Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "ventilation",
                {
                    "name": "Ventilation Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "water-heater-brand",
                {
                    "name": "Water Heater Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "water-heater",
                {
                    "name": "Water Heater Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
        )
    )
