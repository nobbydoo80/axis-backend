"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/20/2022 16:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from ..base import ProgramBuilder
import datetime


class MassCodeTesting(ProgramBuilder):
    name = "Mass Code Testing"
    slug = "mass-code-testing"
    owner = "advanced-building-analysis"
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
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2012, 1, 1)
    start_date = datetime.date(2012, 1, 1)
    end_date = datetime.date(2012, 12, 31)

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
        "rater": {
            "default": [
                "customer-10-raterbuilder-agreement-signed",
            ],
        },
    }
    texts = {
        "rater": {
            "customer-10-raterbuilder-agreement-signed": "Customer 1.0 Rater/Builder Agreement signed",
        },
    }
    descriptions = {
        "rater": {
            "customer-10-raterbuilder-agreement-signed": """Agreement between Rater and Builder describing the services provided and payment""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Pass",
                "Fail",
            ): [
                "customer-10-raterbuilder-agreement-signed",
            ],
        },
    }
    suggested_response_flags = {
        "rater": {
            "customer-10-raterbuilder-agreement-signed": {
                "Fail": {
                    "comment_required": True,
                },
            },
        },
    }
