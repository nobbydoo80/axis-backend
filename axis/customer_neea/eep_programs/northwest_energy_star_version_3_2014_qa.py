"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class NorthwestEnergyStarVersion32014Qa(ProgramBuilder):
    name = "Northwest ENERGY STAR Version 3: 2014 QA"
    slug = "northwest-energy-star-version-3-2014-qa"
    owner = "neea"
    is_qa_program = True
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
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = False
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = False
    is_multi_family = False

    visibility_date = datetime.date(2014, 4, 1)
    start_date = datetime.date(2014, 4, 1)
    role_settings = {}  # Dont swap names

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
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
        "qa": {
            "default": [
                "nwes-qa-10-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-11-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-12-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-13-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-14-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-15-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-16-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-17-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-18-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-19-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-110-rater-qa-checklist-hvac-system-qual",
                "nwes-qa-111-rater-qa-checklist-hvac-system-qual",
                "nwes-qa-20-data-entry-into-axis-did-the-rater-e",
                "nwes-qa-30-performance-tests-did-the-home-meet",
                "nwes-qa-40-remrate-if-this-is-a-single-family",
                "nwes-qa-41-remrate-does-the-home-meet-or-beat",
            ],
        },
    }
    texts = {
        "qa": {
            "nwes-qa-10-rater-qa-checklist-thermal-enclosure": "NWES-QA 1.0  Rater QA Checklist: Thermal Enclosure System – Section 1",
            "nwes-qa-11-rater-qa-checklist-thermal-enclosure": "NWES-QA 1.1  Rater QA Checklist: Thermal Enclosure System – Section 2",
            "nwes-qa-12-rater-qa-checklist-thermal-enclosure": "NWES-QA 1.2  Rater QA Checklist: Thermal Enclosure System – Section 3",
            "nwes-qa-13-rater-qa-checklist-thermal-enclosure": "NWES-QA 1.3  Rater QA Checklist: Thermal Enclosure System – Section 4",
            "nwes-qa-14-rater-qa-checklist-hvac-system-quali": "NWES-QA 1.4  Rater QA Checklist: HVAC System Quality Installation – Section 1",
            "nwes-qa-15-rater-qa-checklist-hvac-system-quali": "NWES-QA 1.5  Rater QA Checklist: HVAC System Quality Installation – Section 2",
            "nwes-qa-16-rater-qa-checklist-hvac-system-quali": "NWES-QA 1.6  Rater QA Checklist: HVAC System Quality Installation – Section 3",
            "nwes-qa-17-rater-qa-checklist-hvac-system-quali": "NWES-QA 1.7  Rater QA Checklist: HVAC System Quality Installation – Section 4",
            "nwes-qa-18-rater-qa-checklist-hvac-system-quali": "NWES-QA 1.8  Rater QA Checklist: HVAC System Quality Installation – Section 5",
            "nwes-qa-19-rater-qa-checklist-hvac-system-quali": "NWES-QA 1.9  Rater QA Checklist: HVAC System Quality Installation – Section 6",
            "nwes-qa-110-rater-qa-checklist-hvac-system-qual": "NWES-QA 1.10  Rater QA Checklist: HVAC System Quality Installation – Section 7",
            "nwes-qa-111-rater-qa-checklist-hvac-system-qual": "NWES-QA 1.11  Rater QA Checklist: HVAC System Quality Installation – Section 8",
            "nwes-qa-20-data-entry-into-axis-did-the-rater-e": "NWES-QA 2.0  Data Entry into Axis: Did the Rater enter all necessary home information accurately?  ",
            "nwes-qa-30-performance-tests-did-the-home-meet": "NWES-QA 3.0  Performance Tests:  Did the home meet building tightness and whole home ventilation requirements?",
            "nwes-qa-40-remrate-if-this-is-a-single-family": "NWES-QA 4.0  REM/Rate:  If this is a single family home, did the Rater complete the proper modeling of the home in the correct version of NW REM/Rate? ",
            "nwes-qa-41-remrate-does-the-home-meet-or-beat": "NWES-QA 4.1  REM/Rate:  Does the home meet or beat annual fuel usage? ",
        },
    }
    descriptions = {
        "qa": {},
    }
    suggested_responses = {
        "qa": {
            (
                "Passed",
                "Must Correct",
                "Not Visible",
                "N/A",
            ): [
                "nwes-qa-10-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-11-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-12-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-13-rater-qa-checklist-thermal-enclosure",
                "nwes-qa-14-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-15-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-16-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-17-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-18-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-19-rater-qa-checklist-hvac-system-quali",
                "nwes-qa-110-rater-qa-checklist-hvac-system-qual",
                "nwes-qa-111-rater-qa-checklist-hvac-system-qual",
            ],
            (
                "Yes",
                "No",
            ): [
                "nwes-qa-20-data-entry-into-axis-did-the-rater-e",
                "nwes-qa-30-performance-tests-did-the-home-meet",
            ],
            (
                "Yes",
                "No",
                "N/A",
            ): [
                "nwes-qa-40-remrate-if-this-is-a-single-family",
                "nwes-qa-41-remrate-does-the-home-meet-or-beat",
            ],
        },
    }
