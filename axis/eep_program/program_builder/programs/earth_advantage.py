__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import logging
import datetime
from collections import OrderedDict

from axis.eep_program.program_builder.base import ProgramBuilder

log = logging.getLogger(__name__)


class EarthAdvantageCertifiedHome(ProgramBuilder):
    name = "Earth Advantage Certified Home"
    slug = "earth-advantage-certified-home"
    owner = "earth-advantage-institute"
    is_qa_program = False
    opt_in = False
    workflow_default_settings = {}
    viewable_by_company_type = "builder eep rater"
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
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = False
    is_multi_family = False

    visibility_date = datetime.date(2019, 4, 22)
    start_date = datetime.date(2019, 4, 22)

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": True,
        "rater": True,
        "provider": False,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": False,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": False,
    }
    annotations = OrderedDict(
        (
            (
                "earth-advantage-certification-level",
                {
                    "name": "Earth Advantage Certification Level",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Silver,Gold,Platinum,Net Zero Ready,Net Zero",
                    "is_required": "True",
                },
            ),
        )
    )
