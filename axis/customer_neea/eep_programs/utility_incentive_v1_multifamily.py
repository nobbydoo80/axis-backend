"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/27/2022 19:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime
from collections import OrderedDict


class UtilityIncentiveV1Multifamily(ProgramBuilder):
    name = "Utility Incentive V1 - Multifamily"
    slug = "utility-incentive-v1-multifamily"
    owner = "neea"
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
    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = True
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2017, 1, 31)
    start_date = datetime.date(2017, 1, 31)
    close_date = datetime.date(2019, 1, 27)
    submit_date = datetime.date(2019, 1, 27)
    end_date = datetime.date(2019, 1, 27)

    comment = (
        """Version 1 of the NEEA Utility Incentive program for Multifamily new construction."""
    )

    require_home_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": True,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": True,
        "utility": False,
        "rater": True,
        "provider": True,
        "qa": True,
    }
    measures = {"rater": {}}
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
                "heat-source",
                {
                    "name": "Primary Heat Source",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Heat Pump,Heat Pump - Geothermal/Ground Source,Heat Pump - w/ Gas Backup,Heat Pump - Mini Split,Gas with AC,Gas No AC,Zonal Electric,Propane Oil or Wood",
                    "is_required": "True",
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
        )
    )
