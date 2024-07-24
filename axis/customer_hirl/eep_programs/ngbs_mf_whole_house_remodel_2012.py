import datetime
import logging

from collections import OrderedDict

from axis.annotation.models import Type as AnnotationType

from axis.customer_hirl.scoring import BaseScoringExtraction
from axis.eep_program.program_builder.base import ProgramBuilder

__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class NGBSMFWholeHouseRemodel2012(ProgramBuilder):
    name = "2012 MF Whole House Renovation"
    slug = "ngbs-mf-whole-house-remodel-2012-new"
    owner = "provider-home-innovation-research-labs"
    certifiable_by = ["provider-home-innovation-research-labs"]

    is_multi_family = True

    visibility_date = datetime.date(year=2012, month=11, day=1)
    start_date = datetime.date(year=2012, month=2, day=1)
    close_date = datetime.date(year=2023, month=1, day=1)
    submit_date = datetime.date(year=2023, month=1, day=1)
    end_date = datetime.date(year=2023, month=1, day=1)

    simulation_type = None
    manual_transition_on_certify = True
    require_home_relationships = {
        "builder": True,
        "rater": True,
        "utility": False,
        "provider": True,
        "hvac": False,
        "qa": False,
        "architect": True,
        "developer": True,
        "communityowner": True,
    }
    require_provider_relationships = {
        "builder": True,
        "rater": True,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
        "architect": True,
        "developer": True,
        "communityowner": True,
    }

    measures = {"rater": {}}

    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    require_rater_of_record = False

    allow_sampling = False

    @property
    def annotations(self):
        annotation_type_data = OrderedDict()
        for data_type in BaseScoringExtraction.AVAILABLE_DATA_TYPES:
            slug = "energy-percent-reduction-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Energy % Reduction",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }
            slug = "water-percent-reduction-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Water % Reduction",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

        return annotation_type_data
