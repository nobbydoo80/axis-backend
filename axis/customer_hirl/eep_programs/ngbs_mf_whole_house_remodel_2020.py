__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import datetime
import logging
from collections import OrderedDict

from axis.annotation.models import Type as AnnotationType
from axis.customer_hirl.scoring.base import BaseScoringExtraction
from axis.eep_program.program_builder.base import ProgramBuilder

log = logging.getLogger(__name__)


class NGBSMFWholeHouseRemodel2020(ProgramBuilder):
    name = "2020 MF Whole House Renovation"
    slug = "ngbs-mf-whole-house-remodel-2020-new"
    owner = "provider-home-innovation-research-labs"
    certifiable_by = ["provider-home-innovation-research-labs"]
    is_multi_family = True

    visibility_date = datetime.date(year=2020, month=11, day=1)
    start_date = datetime.date(year=2020, month=2, day=1)
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
            slug = "energy-compliance-path-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Energy Path",
                "data_type": AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
                "valid_multiplechoice_values": "Performance,Prescriptive",
                "is_required": False,
            }
            slug = "water-compliance-path-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Water Path",
                "data_type": AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
                "valid_multiplechoice_values": "Performance,Prescriptive",
                "is_required": False,
            }

            slug = "year-built-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Year Built",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "energy-baseline-year-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Energy Baseline Year",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "water-baseline-year-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Water Baseline Year",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "project-description-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Project Description",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "ach50-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "ACH50",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "elr50-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "ELR50",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "energy-percent-reduction-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Energy Percent Reduction",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "water-percent-reduction-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Water Percent Reduction",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "badge-resilience-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Badge: Resilience",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "badge-smart-home-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Badge: Smart Home",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "badge-universal-design-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Badge: Universal Design",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "badge-wellness-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Badge: Wellness",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "badge-zero-water-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Badge: Zero Water",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "duct-testing-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Duct Testing",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

        return annotation_type_data
