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


class NeeaEfficientHomes(ProgramBuilder):
    name = "NEEA Efficient Homes Pilot"
    slug = "neea-efficient-homes"
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
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2015, 9, 20)
    start_date = datetime.date(2015, 9, 20)
    close_date = datetime.date(2018, 5, 1)
    end_date = datetime.date(2020, 10, 30)

    comment = """NEEA Efficient Homes Pilot (Single Family)"""

    require_home_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": False,
        "qa": True,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": False,
        "qa": True,
    }
    measures = {
        "rater": {
            "default": [
                "neea-pilot-phase-1-or-2-rough-inspection-checkl",
                "neea-pilot-phase-1-or-2-final-commissioning-che",
                "neea-pilot-phase-3-combined-roughfinal-checkli",
                "neea-pilot-phase-3-nw-remrate-performance-summ",
                "neea-pilot-data-logger-or-metering-equipment-inst",
                "neea-pilot-compliance-calculators-ie-kitchen-r",
                "neea-pilot-builder-agreement",
                "neea-pilot-rater-agreement",
                "neea-pilot-other-documents-or-notes",
            ],
        },
    }
    texts = {
        "rater": {
            "neea-pilot-phase-1-or-2-rough-inspection-checkl": "NEEA-Pilot: Phase 1 or 2 – Rough Inspection Checklist",
            "neea-pilot-phase-1-or-2-final-commissioning-che": "NEEA-Pilot: Phase 1 or 2 – Final Commissioning Checklist",
            "neea-pilot-phase-3-combined-roughfinal-checkli": "NEEA-Pilot: Phase 3 – Combined Rough/Final Checklist",
            "neea-pilot-phase-3-nw-remrate-performance-summ": "NEEA-Pilot: Phase 3 – NW REM/Rate Performance Summary Report",
            "neea-pilot-data-logger-or-metering-equipment-inst": "NEEA-Pilot: Data logger or metering equipment installed?",
            "neea-pilot-compliance-calculators-ie-kitchen-r": "NEEA-Pilot: Compliance Calculators (i.e. Kitchen Range Exhaust)",
            "neea-pilot-builder-agreement": "NEEA-Pilot: Builder Agreement",
            "neea-pilot-rater-agreement": "NEEA-Pilot: Rater Agreement",
            "neea-pilot-other-documents-or-notes": "NEEA-Pilot: Other Documents or Notes",
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
                "N/A",
            ): [
                "neea-pilot-phase-1-or-2-rough-inspection-checkl",
                "neea-pilot-phase-1-or-2-final-commissioning-che",
                "neea-pilot-phase-3-combined-roughfinal-checkli",
                "neea-pilot-phase-3-nw-remrate-performance-summ",
                "neea-pilot-data-logger-or-metering-equipment-inst",
                "neea-pilot-compliance-calculators-ie-kitchen-r",
                "neea-pilot-builder-agreement",
                "neea-pilot-rater-agreement",
                "neea-pilot-other-documents-or-notes",
            ],
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
                "certified-doe-zero-ready",
                {
                    "name": "DOE Zero Energy Ready Home™",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
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
                "move-in-date-nr",
                {
                    "name": "Home owner Move In",
                    "data_type": "date",
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
                "certified-leed",
                {
                    "name": "LEED",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Silver,Gold,Platinum",
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
                "other-brand",
                {
                    "name": "Other Brand",
                    "data_type": "open",
                    "valid_multiplechoice_values": "",
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
                "other",
                {
                    "name": "Other Model",
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
                "neea-pilot-specification",
                {
                    "name": "Pilot Specification",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Phase 1,Phase 2,Phase 3 - Minimum Spec,Phase 3 - Reach Spec",
                    "is_required": "True",
                },
            ),
            (
                "heat-source-nr",
                {
                    "name": "Primary Heat Source",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Heat Pump,Heat Pump - Geothermal/Ground Source,Heat Pump - w/ Gas Backup,Heat Pump - Mini Split,Gas with AC,Gas No AC,Zonal Electric,Propane Oil or Wood,Hydronic Radiant",
                    "is_required": "True",
                },
            ),
            (
                "project-end-nr",
                {
                    "name": "Project End",
                    "data_type": "date",
                    "valid_multiplechoice_values": "",
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
