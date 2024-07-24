__author__ = "Artem Hruzd"
__date__ = "10/14/2022 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]

import datetime
import logging
from django.apps import apps
from collections import OrderedDict

from axis.annotation.models import Type as AnnotationType
from axis.customer_hirl.scoring.base import BaseScoringExtraction
from axis.eep_program.program_builder.base import ProgramBuilder


customer_hirl_app = apps.get_app_config("customer_hirl")


log = logging.getLogger(__name__)


class NGBSLandDevelopment2020(ProgramBuilder):
    name = "2020 NGBS Land Development"
    slug = "ngbs-land-development-2020-new"
    owner = customer_hirl_app.CUSTOMER_SLUG
    certifiable_by = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    visibility_date = datetime.date(year=2019, month=11, day=1)
    start_date = datetime.date(year=2020, month=2, day=1)
    close_date = datetime.date(year=2023, month=1, day=1)
    submit_date = datetime.date(year=2023, month=1, day=1)
    end_date = datetime.date(year=2023, month=1, day=1)

    simulation_type = None
    manual_transition_on_certify = True
    require_home_relationships = {
        "builder": False,
        "rater": True,
        "utility": False,
        "provider": True,
        "hvac": False,
        "qa": False,
        "developer": True,
    }
    require_provider_relationships = {
        "builder": False,
        "rater": True,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
        "developer": True,
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
            slug = "loa-points-awarded-by-verifier-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Total Points Awarded by Verifier",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "loa-rating-level-archived-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Rating Level Achieved",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "points-awarded-by-verifier-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Total Points Awarded by Verifier",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "rating-level-archived-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Rating Level Achieved",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }
        return annotation_type_data
