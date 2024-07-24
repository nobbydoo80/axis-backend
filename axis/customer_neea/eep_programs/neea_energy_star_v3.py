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


class NeeaEnergyStarV3(ProgramBuilder):
    name = "Northwest ENERGY STAR Version 3: Prescriptive"
    slug = "neea-energy-star-v3"
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

    visibility_date = datetime.date(2013, 3, 1)
    start_date = datetime.date(2013, 3, 1)
    end_date = datetime.date(2017, 6, 30)

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
                "nwes-10-house-size-adjustment-factor-needed-ple",
                "nwes-11-completed-thermal-enclosure-checklist",
                "nwes-12-completed-hvac-contractor-checklist",
                "nwes-13-completed-hvac-verifier-checklist",
                "nwes-14-completed-water-management-or-indoor-airp",
                "nwes-20-is-performance-tester-ptcs-certified",
                "nwes-21-enter-name-of-ptcs-contrator-or-na-if",
                "nwes-22-enter-ptcs-id-number-or-na-if-not-ap",
                "nwes-30-performancetest-ach50",
                "nwes-31-performancetest-net-caz",
                "nwes-32-performancetest-windy-conditions-no-te",
                "nwes-33-co-monitor-present",
                "nwes-34-performance-test-duct-leakage",
                "nwes-35-performancetest-conditioned-space-sqft",
                "nwes-41-inspection-notes-enter-notes-by-selectin",
                "nwes-50-home-inspection-meets-or-exceeds-all-mini",
            ],
        },
    }
    texts = {
        "rater": {
            "nwes-10-house-size-adjustment-factor-needed-ple": 'NWES 1.0 House Size Adjustment Factor Needed?  Please answer "Size Adjustment Factor Required" if House Size Adjustment Factor has been used for this residence.  Enter the details by selecting the "Add Comment" button below.',
            "nwes-11-completed-thermal-enclosure-checklist": "NWES 1.1 Completed Thermal Enclosure Checklist?",
            "nwes-12-completed-hvac-contractor-checklist": "NWES 1.2 Completed HVAC Contractor Checklist?",
            "nwes-13-completed-hvac-verifier-checklist": "NWES 1.3 Completed HVAC Verifier Checklist?",
            "nwes-14-completed-water-management-or-indoor-airp": "NWES 1.4 Completed Water Management OR Indoor airPLUS Checklist?",
            "nwes-20-is-performance-tester-ptcs-certified": "NWES 2.0 Is Performance Tester PTCS Certified?",
            "nwes-21-enter-name-of-ptcs-contrator-or-na-if": 'NWES 2.1 Enter Name of PTCS Contractor (or "N/A" if not applicable) ',
            "nwes-22-enter-ptcs-id-number-or-na-if-not-ap": 'NWES 2.2 Enter PTCS ID Number (or ("N/A" if not applicable).  Click on this text for help in finding PTCS ID\'s.',
            "nwes-30-performancetest-ach50": "NWES 3.0 PerformanceTest - ACH50",
            "nwes-31-performancetest-net-caz": "NWES 3.1 PerformanceTest - Net CAZ",
            "nwes-32-performancetest-windy-conditions-no-te": "NWES 3.2 PerformanceTest - Windy conditions (No test required)",
            "nwes-33-co-monitor-present": "NWES 3.3 CO Monitor present?",
            "nwes-34-performance-test-duct-leakage": "NWES 3.4 Performance Test - Duct Leakage to Exterior",
            "nwes-35-performancetest-conditioned-space-sqft": "NWES 3.5 PerformanceTest - Conditioned Space (sqft)",
            "nwes-41-inspection-notes-enter-notes-by-selectin": 'NWES 4.1 Inspection Notes (enter notes by selecting the "Add Comment" button below)',
            "nwes-50-home-inspection-meets-or-exceeds-all-mini": "NWES 5.0 Home Inspection meets or exceeds all minimum values",
        },
    }
    descriptions = {
        "rater": {
            "nwes-11-completed-thermal-enclosure-checklist": """<a href="http://northwestenergystar.com/partners/verifiersraters?tid=166" target="_blank">Click here</a> to download the Northwest ENERGY STAR Thermal Enclosure inspection checklist.""",
            "nwes-12-completed-hvac-contractor-checklist": """<a href="http://northwestenergystar.com/partners/verifiersraters?tid=166" target="_blank">Click here</a> to download the Northwest ENERGY STAR HVAC Contractor inspection checklist.""",
            "nwes-13-completed-hvac-verifier-checklist": """<a href="http://northwestenergystar.com/partners/verifiersraters?tid=166" target="_blank">Click here</a> to download the Northwest ENERGY STAR HVAC Verifier inspection checklist.""",
            "nwes-14-completed-water-management-or-indoor-airp": """<a href="http://northwestenergystar.com/partners/verifiersraters?tid=166" target="_blank">Click here</a> to download the Northwest ENERGY STAR Water Management inspection checklist.  <a href="http://epa.gov/iaplus01/pdfs/verification_checklist.pdf" target="_blank">Click here</a> to view the U.S. EPA ENERGY STAR Indoor airPLUS inspection checklist.""",
            "nwes-20-is-performance-tester-ptcs-certified": """Performance tester or installing technician.""",
            "nwes-22-enter-ptcs-id-number-or-na-if-not-ap": """For a list of Bonneville Power Administration PTCS Certified Technicians <a href=" http://www.bpa.gov/energy/n/residential/ptcs/index.cfm" target="_blank">click here.</a>""",
            "nwes-33-co-monitor-present": """Select "N/A" for a residence with no combustion appliances within conditioned space.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Size Adjustment Factor Required",
                "No Size Adjustment Factor Required",
            ): [
                "nwes-10-house-size-adjustment-factor-needed-ple",
            ],
            (
                "Yes",
                "No",
            ): [
                "nwes-11-completed-thermal-enclosure-checklist",
                "nwes-12-completed-hvac-contractor-checklist",
                "nwes-13-completed-hvac-verifier-checklist",
                "nwes-50-home-inspection-meets-or-exceeds-all-mini",
            ],
            (
                "Water Management Checklist",
                "Indoor airPLUS Checklist",
                "Neither",
            ): [
                "nwes-14-completed-water-management-or-indoor-airp",
            ],
            (
                "Yes",
                "No",
                "N/A",
            ): [
                "nwes-20-is-performance-tester-ptcs-certified",
                "nwes-33-co-monitor-present",
            ],
            (
                "No Windy Conditions",
                "Windy Conditions",
            ): [
                "nwes-32-performancetest-windy-conditions-no-te",
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
            "nwes-10-house-size-adjustment-factor-needed-ple": {
                "Size Adjustment Factor Required": {
                    "comment_required": True,
                },
            },
            "nwes-11-completed-thermal-enclosure-checklist": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-12-completed-hvac-contractor-checklist": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-13-completed-hvac-verifier-checklist": {
                "No": {
                    "comment_required": True,
                },
            },
            "nwes-14-completed-water-management-or-indoor-airp": {
                "Neither": {
                    "comment_required": True,
                },
            },
            "nwes-20-is-performance-tester-ptcs-certified": {
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
            "nwes-50-home-inspection-meets-or-exceeds-all-mini": {
                "No": {
                    "comment_required": True,
                },
            },
        },
    }
    annotations = OrderedDict(
        (
            (
                "advanced-lighting-package",
                {
                    "name": "Advanced Lighting Package",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
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
                "builder-owner",
                {
                    "name": "Builder Owner",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
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
                "ducts",
                {
                    "name": "Ducts",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "electric-utility-account-number",
                {
                    "name": "Electric Utility Account Number",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "eto",
                {
                    "name": "ETO",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "faucet-aerators",
                {
                    "name": "Faucet Aerators",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "gas-utility-account-number",
                {
                    "name": "Gas Utility Account Number",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "home-type",
                {
                    "name": "Home Type",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Standard,Reference,Sampled",
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
                "hvac",
                {
                    "name": "HVAC Combined / Heating Only Model",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "light-bulbs",
                {
                    "name": "Light Bulbs",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "lighting-fixtures",
                {
                    "name": "Lighting Fixtures",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "low-flow-showerheads",
                {
                    "name": "Low-flow Showerheads",
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
                "reference-home-site-id",
                {
                    "name": "Reference Home Site ID",
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
                "residence-description",
                {
                    "name": "Residence Description",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
            (
                "tco-options",
                {
                    "name": "TCO Options",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": 'N/A,Hybrid "Ductless Split" Heat Pump/Electric Resistance Zonal Heating,Natural Gas Fired Hydronic Heating Systems,Un-vented Crawlspaces,Mechanically Exhausted,Sealed Crawlspaces,Tankless Water Heater Alternative(s)',
                    "is_required": "True",
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
