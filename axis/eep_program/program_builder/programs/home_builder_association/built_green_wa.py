import logging
from collections import OrderedDict

from axis.eep_program.program_builder.base import ProgramBuilder

__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class BuiltGreenWAPrescriptive(ProgramBuilder):
    CERTIFIER_SLUG = "provider-home-builders-association-of-tri-cities"

    name = "Built Green® WA Prescriptive"
    slug = "built-green-wa-prescriptive"
    qa_name = "Built Green® WA Prescriptive QA"
    qa_slug = "built-green-wa-prescriptive-qa"
    owner = CERTIFIER_SLUG
    simulation_type = None
    require_home_relationships = ["utility"]
    manual_transition_on_certify = True
    measures = {
        "rater": {
            "default": [
                "built-green-inspection-checklist",
            ],
        },
        "qa": {},
    }
    texts = {
        "rater": {
            "built-green-inspection-checklist": "Upload a completed Built Green Inspection Checklist for this home.",
        },
    }
    suggested_responses = {
        "rater": {
            ("Not Applicable (comment required)", "Upload Document(s)"): [
                "built-green-inspection-checklist",
            ],
        },
    }
    conditions = {
        "rater": {
            "instrument": {
                "built-green-inspection-checklist": {
                    "Not Applicable (comment required)": {"comment": True},
                },
            },
        },
    }

    annotations = OrderedDict(
        (
            (
                "num-bedrooms",
                {
                    "name": "Number of Bedrooms",
                    "data_type": "integer",
                    "is_required": True,
                },
            ),
            (
                "unit-size-sqft",
                {
                    "name": "Unit Size in Square Feet",
                    "data_type": "integer",
                    "is_required": True,
                },
            ),
            (
                "built-green-house-size-multiplier",
                {
                    "name": "Built Green House Size Multiplier",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "pct-improvement-over-code",
                {
                    "name": "Percent Improvement Over Code",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-certification-level",
                {
                    "name": "Built Green Certification Level",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "1-star,2-star,3-star,4-star,5-star",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-1",
                {
                    "name": "Built Green Points: Section 1",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-2",
                {
                    "name": "Built Green Points: Section 2",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-3",
                {
                    "name": "Built Green Points: Section 3",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-4",
                {
                    "name": "Built Green Points: Section 4",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-5",
                {
                    "name": "Built Green Points: Section 5",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-6",
                {
                    "name": "Built Green Points: Section 6",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-7",
                {
                    "name": "Built Green Points: Section 7",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "total-built-green-points",
                {
                    "name": "Total Built Green Points",
                    "data_type": "float",
                    "is_required": False,  # Keep computed field False so api doesn't block it for missing
                },
            ),
        )
    )

    def build_program(self):
        from axis.company.models import Company
        from axis.qa.models import QARequirement

        program = super(BuiltGreenWAPrescriptive, self).build_program()
        certifier = Company.objects.get(slug=self.CERTIFIER_SLUG)
        program.certifiable_by.clear()
        program.certifiable_by.add(certifier)
        qa_requirement, _ = QARequirement.objects.get_or_create(
            qa_company=certifier, eep_program=program, type="program_review"
        )
        qa_requirement.coverage_pct = 0
        qa_requirement.gate_certification = False
        qa_requirement.save()
        return program


class BuiltGreenWAPerformance(ProgramBuilder):
    CERTIFIER_SLUG = "provider-home-builders-association-of-tri-cities"

    name = "Built Green® WA Performance"
    slug = "built-green-wa-performance"
    qa_name = "Built Green® WA Performance QA"
    qa_slug = "built-green-wa-performance-qa"
    owner = CERTIFIER_SLUG

    require_input_data = True
    require_rem_data = True
    require_model_file = False
    require_ekotrope_data = False

    require_home_relationships = ["utility"]
    manual_transition_on_certify = True
    measures = {
        "rater": {
            "default": [
                "built-green-inspection-checklist",
            ],
        },
        "qa": {},
    }
    texts = {
        "rater": {
            "built-green-inspection-checklist": "Upload a completed Built Green Inspection Checklist for this home.",
        },
    }
    suggested_responses = {
        "rater": {
            ("Not Applicable (comment required)", "Upload Document(s)"): [
                "built-green-inspection-checklist",
            ],
        },
    }
    conditions = {
        "rater": {
            "instrument": {
                "built-green-inspection-checklist": {
                    "Not Applicable (comment required)": {"comment": True},
                },
            },
        },
    }

    annotations = OrderedDict(
        (
            (
                "num-bedrooms",
                {
                    "name": "Number of Bedrooms",
                    "data_type": "integer",
                    "is_required": True,
                },
            ),
            (
                "unit-size-sqft",
                {
                    "name": "Unit Size in Square Feet",
                    "data_type": "integer",
                    "is_required": True,
                },
            ),
            (
                "built-green-house-size-multiplier",
                {
                    "name": "Built Green House Size Multiplier",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "pct-improvement-over-code",
                {
                    "name": "Percent Improvement Over Code",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-certification-level",
                {
                    "name": "Built Green Certification Level",
                    "data_type": "multiple-choice",
                    "is_required": True,
                    "valid_multiplechoice_values": "1-star,2-star,3-star,4-star,5-star",
                },
            ),
            (
                "built-green-points-section-1",
                {
                    "name": "Built Green Points: Section 1",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-2",
                {
                    "name": "Built Green Points: Section 2",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-3",
                {
                    "name": "Built Green Points: Section 3",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-4",
                {
                    "name": "Built Green Points: Section 4",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-5",
                {
                    "name": "Built Green Points: Section 5",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-6",
                {
                    "name": "Built Green Points: Section 6",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "built-green-points-section-7",
                {
                    "name": "Built Green Points: Section 7",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
            (
                "total-built-green-points",
                {
                    "name": "Total Built Green Points",
                    "data_type": "float",
                    "is_required": True,
                },
            ),
        )
    )

    def build_program(self):
        from axis.company.models import Company
        from axis.qa.models import QARequirement

        program = super(BuiltGreenWAPerformance, self).build_program()
        certifier = Company.objects.get(slug=self.CERTIFIER_SLUG)
        program.certifiable_by.clear()
        program.certifiable_by.add(certifier)
        qa_requirement, _ = QARequirement.objects.get_or_create(
            qa_company=certifier, eep_program=program, type="program_review"
        )
        qa_requirement.coverage_pct = 0
        qa_requirement.gate_certification = False
        qa_requirement.save()
        return program
