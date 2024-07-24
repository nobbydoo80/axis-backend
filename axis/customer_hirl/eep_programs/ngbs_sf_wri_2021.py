"""ngbs_sf_wri_2021.py: """

__author__ = "Artem Hruzd"
__date__ = "03/24/2022 11:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import datetime
from collections import OrderedDict

from django.apps import apps

from axis.annotation.models import Type as AnnotationType
from axis.customer_hirl.scoring.base import BaseScoringExtraction
from axis.eep_program.program_builder.base import ProgramBuilder

customer_hirl_app = apps.get_app_config("customer_hirl")


class NGBSSFWRI2021(ProgramBuilder):
    name = "2020 Stand-Alone WRI – SF"
    slug = "ngbs-sf-wri-2021"
    owner = customer_hirl_app.CUSTOMER_SLUG
    certifiable_by = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    visibility_date = datetime.date(year=2022, month=5, day=1)
    start_date = datetime.date(year=2022, month=5, day=1)
    close_date = datetime.date(year=2025, month=5, day=1)
    submit_date = datetime.date(year=2025, month=5, day=1)
    end_date = datetime.date(year=2025, month=5, day=1)

    simulation_type = None
    manual_transition_on_certify = True
    require_home_relationships = {
        "builder": True,
        "rater": True,
        "utility": False,
        "provider": True,
        "hvac": False,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "rater": True,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
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
            slug = "baseline-units-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Baseline Units",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "baseline-common-areas-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Baseline Common Areas",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "baseline-indoor-total-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Baseline Indoor Total",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "baseline-outdoor-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Baseline Outdoor",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "designed-units-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Designed Units",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "designed-common-areas-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Designed Common Areas",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "designed-less-indoor-credit-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Designed Less Indoor Credit",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "designed-indoor-total-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Designed Indoor Total",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "designed-outdoor-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Designed Outdoor",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "designed-less-outdoor-credit-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Designed Less Outdoor Credit",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "designed-outdoor-total-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Designed Outdoor Total",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "gallons-saved-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Gallons Saved",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "wri-rating-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "WRI Rating",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

        return annotation_type_data
