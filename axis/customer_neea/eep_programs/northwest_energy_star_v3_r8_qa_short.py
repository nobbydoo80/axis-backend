"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class NorthwestEnergyStarV3R8QaShort(ProgramBuilder):
    name = "ENERGY STAR Version 3, Rev 8 QA Checklist – Short"
    slug = "northwest-energy-star-v3-r8-qa-short"
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
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = False
    is_multi_family = False

    visibility_date = datetime.date(2015, 8, 3)
    start_date = datetime.date(2015, 8, 3)

    comment = """This is the SHORT QA program for ENERGY STAR Version 3, Rev 8 """
    role_settings = {}  # Dont swap names

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
        "provider": False,
        "qa": False,
    }
    measures = {
        "qa": {
            "default": [
                "estar-qa-energy-star-action-itemssummary-of-qa-i-0",
                "estar-qa-rater-design-review-checklist-section-4",
                "estar-qa-rater-field-checklist-section-1-high-p",
                "estar-qa-rater-field-checklist-section-2-fully-",
                "estar-qa-rater-field-checklist-section-3-reduce",
                "estar-qa-rater-field-checklist-section-4-air-se",
                "estar-qa-rater-field-checklist-section-6-duct-q",
                "estar-qa-rater-field-checklist-section-7-whole-",
                "estar-qa-rater-field-checklist-section-8-local",
                "estar-qa-rater-field-checklist-section-9-filtra",
                "estar-qa-rater-field-checklist-section-10-combu",
                "estar-qa-misc-name-of-qa-designee-0",
                "estar-qa-misc-status-of-home-at-time-of-inspecti-0",
                "estar-qa-misc-date-of-inspection-0",
                "estar-qa-misc-additional-items-reviewed-0",
            ],
        },
    }
    texts = {
        "qa": {
            "estar-qa-energy-star-action-itemssummary-of-qa-i-0": 'ESTAR-QA Energy Star Action Items/Summary of QA: If any item marked "Must Correct", an action summary document shall be attached',
            "estar-qa-rater-design-review-checklist-section-4": "ESTAR-QA Rater Design Review Checklist - Section 4: Review of HVAC Design Report",
            "estar-qa-rater-field-checklist-section-1-high-p": "ESTAR-QA Rater Field Checklist - Section 1: High-Performance Fenestration & Insulation",
            "estar-qa-rater-field-checklist-section-2-fully-": "ESTAR-QA Rater Field Checklist - Section 2: Fully-Aligned Air Barriers",
            "estar-qa-rater-field-checklist-section-3-reduce": "ESTAR-QA Rater Field Checklist - Section 3: Reduced Thermal Bridging",
            "estar-qa-rater-field-checklist-section-4-air-se": "ESTAR-QA Rater Field Checklist - Section 4: Air Sealing",
            "estar-qa-rater-field-checklist-section-6-duct-q": "ESTAR-QA Rater Field Checklist - Section 6: Duct Quality Installation",
            "estar-qa-rater-field-checklist-section-7-whole-": "ESTAR-QA Rater Field Checklist - Section 7: Whole-House Mechanical Ventilation System",
            "estar-qa-rater-field-checklist-section-8-local": "ESTAR-QA Rater Field Checklist - Section 8: Local Mechanical Exhaust",
            "estar-qa-rater-field-checklist-section-9-filtra": "ESTAR-QA Rater Field Checklist - Section 9: Filtration",
            "estar-qa-rater-field-checklist-section-10-combu": "ESTAR-QA Rater Field Checklist - Section 10: Combustion Appliances",
            "estar-qa-misc-name-of-qa-designee-0": "ESTAR-QA MISC: Name of QA Designee",
            "estar-qa-misc-status-of-home-at-time-of-inspecti-0": "ESTAR-QA MISC: Status of Home at time of Inspection",
            "estar-qa-misc-date-of-inspection-0": "ESTAR-QA MISC: Date of Inspection",
            "estar-qa-misc-additional-items-reviewed-0": "ESTAR-QA MISC: Additional Items Reviewed",
        },
    }
    descriptions = {
        "qa": {},
    }
    suggested_responses = {
        "qa": {
            (
                "Yes",
                "No",
            ): [
                "estar-qa-energy-star-action-itemssummary-of-qa-i-0",
            ],
            (
                "Passed",
                "Must Correct",
                "N/A",
            ): [
                "estar-qa-rater-design-review-checklist-section-4",
            ],
            (
                "Passed",
                "Must Correct",
                "Not Visible",
                "N/A",
            ): [
                "estar-qa-rater-field-checklist-section-1-high-p",
                "estar-qa-rater-field-checklist-section-2-fully-",
                "estar-qa-rater-field-checklist-section-3-reduce",
                "estar-qa-rater-field-checklist-section-4-air-se",
                "estar-qa-rater-field-checklist-section-6-duct-q",
                "estar-qa-rater-field-checklist-section-7-whole-",
                "estar-qa-rater-field-checklist-section-8-local",
                "estar-qa-rater-field-checklist-section-9-filtra",
                "estar-qa-rater-field-checklist-section-10-combu",
            ],
            (
                "Yes; details entered as comment",
                "Yes; details uploaded as separate document",
                "No",
            ): [
                "estar-qa-misc-additional-items-reviewed-0",
            ],
        },
    }
    instrument_types = {
        "date": [
            "estar-qa-misc-date-of-inspection-0",
        ],
    }
    suggested_response_flags = {
        "qa": {
            "estar-qa-misc-additional-items-reviewed-0": {
                "Yes; details entered as comment": {
                    "comment_required": True,
                },
                "Yes; details uploaded as separate document": {
                    "document_required": True,
                },
            },
        },
    }
