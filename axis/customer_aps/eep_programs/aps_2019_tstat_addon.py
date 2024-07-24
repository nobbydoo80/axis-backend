"""aps_2019_tstat.py: Django """


import logging
from datetime import date
from decimal import Decimal

from axis.eep_program.program_builder.base import ProgramBuilder

__author__ = "Steven K"
__date__ = "07/22/2019 11:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Aps2019Addon(ProgramBuilder):
    """Program Builder for the 2019 Program addon smart thermostat program"""

    slug = "aps-energy-star-2019-tstat-addon"

    name = "APS 2019 Smart Thermostat ADD"
    comment = "APS 2019 Smart Thermostat Addon Program"
    owner = "aps"

    visibility_date = date(year=2019, month=8, day=1)
    start_date = date(year=2019, month=8, day=1)
    close_date = date(year=2019, month=11, day=1)
    submit_date = date(year=2019, month=11, day=15)
    end_date = date(year=2020, month=1, day=1)

    require_floorplan_approval = True

    require_input_data = True
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    require_home_relationships = ["builder", "utility", "provider"]
    require_provider_relationships = ["builder", "provider"]

    measures = {"rater": {}}
    instrument_types = {}
    suggested_responses = {}
    suggested_response_flags = {}
    builder_incentive_dollar_value = Decimal("30.00")
    rater_incentive_dollar_value = 0.0

    is_public = False
    viewable_by_company_type = "utility"


class Aps2019Tstat(ProgramBuilder):
    """Program Builder for the 2019 Program smart thermostat program"""

    slug = "aps-energy-star-2019-tstat"

    name = "APS 2019 + ST Program"
    comment = "APS 2019 Program + Smart Thermostat"
    owner = "aps"

    visibility_date = date(year=2019, month=8, day=1)
    start_date = date(year=2019, month=8, day=1)
    close_date = date(year=2019, month=11, day=1)
    submit_date = date(year=2019, month=11, day=15)
    end_date = date(year=2020, month=1, day=1)

    require_floorplan_approval = True

    require_input_data = True
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    require_home_relationships = ["builder", "utility", "provider"]
    require_provider_relationships = ["builder", "provider"]

    measures = {"rater": {}}
    builder_incentive_dollar_value = Decimal("200.00")
    rater_incentive_dollar_value = 0.0
    instrument_types = {}
    suggested_responses = {}
    suggested_response_flags = {}
