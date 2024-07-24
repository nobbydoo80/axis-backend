import logging
from collections import OrderedDict

from axis.eep_program.program_builder.base import ProgramBuilder

__author__ = "Steven Klass"
__date__ = "03/12/21 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuiltGreenKingSno(ProgramBuilder):
    CERTIFIER_SLUG = "provider-home-builders-association-of-tri-cities"

    name = "Built Green® King/Sno"
    slug = "built-green-king-sno"
    owner = CERTIFIER_SLUG
    simulation_type = None
    require_home_relationships = ["utility"]
    manual_transition_on_certify = False
    measures = {
        "rater": {},
    }
    texts = {}
    suggested_responses = {}
    conditions = {}

    annotations = OrderedDict(
        (
            (
                "built-green-enrollment-date",
                {
                    "name": "Built Green Enrollment Data",
                    "data_type": "date",
                    "is_required": True,
                },
            ),
            (
                "built-green-project-id",
                {
                    "name": "Built Green Project ID",
                    "data_type": "open",
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
                "unit-type",
                {
                    "name": "Unit Type",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Apartments,Condominiums,Detached Accessory Dwelling Unit (DADU),"
                    "Duplex,House,Mixed Use,Rowhouse,Small Efficiency Dwelling Units (SEDUs),"
                    "Townhouse,Triplex",
                    "is_required": True,
                },
            ),
            (
                "unit-count",
                {
                    "name": "Unit Count",
                    "data_type": "integer",
                    "is_required": True,
                },
            ),
            (
                "num-bedrooms",
                {
                    "name": "Bedroom Count",
                    "data_type": "integer",
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
                "total-built-green-points",
                {
                    "name": "Total Built Green Points",
                    "data_type": "integer",
                    "is_required": False,
                },
            ),
            (
                "built-green-certification-level",
                {
                    "name": "Built Green Certification Level",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "3-star,4-star,5-star",
                    "is_required": True,
                },
            ),
            (
                "built-green-nze-level",
                {
                    "name": "Built Green NZE Level",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": True,
                },
            ),
        )
    )
