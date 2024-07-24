__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import logging

from ..base import ProgramBuilder
import datetime

log = logging.getLogger(__name__)


class Phius(ProgramBuilder):
    name = "PHIUS+ New Construction"
    slug = "phius"
    owner = "eep-passive-house-institute-us-phius"
    is_qa_program = False
    opt_in = True
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
    manual_transition_on_certify = True
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = True
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2019, 11, 26)
    start_date = datetime.date(2019, 11, 26)

    comment = """<font size="2">

<p><h4>Passive House Institute U.S. New Construction</h4></p>

<ins><b>   Program Information</b></ins>
<p>    For more information about the Passive House Institute U.S. new construction program, <a href="http://www.phius.org/home-page" target="_blank">click here.</a></p>

<ins><b>   Certification Database</b></ins>
<p>    To view properties certified under the PHIUS+ program, <a href="http://www.phius.org/phius-certification-for-buildings-and-products/certified-projects-database" target="_blank">click here.</a>

</font>"""

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": True,
        "provider": True,
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
