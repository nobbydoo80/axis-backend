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


class NGBSMFNewConstruction2020(ProgramBuilder):
    name = "2020 MF New Construction"
    slug = "ngbs-mf-new-construction-2020-new"
    owner = "provider-home-innovation-research-labs"
    certifiable_by = ["provider-home-innovation-research-labs"]
    is_multi_family = True

    visibility_date = datetime.date(year=2019, month=11, day=1)
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
            slug = "energy-path-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Energy Path",
                "data_type": AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
                "valid_multiplechoice_values": "Performance path,Prescriptive Path,ERI Target,"
                "Alt. Bronze or Silver,Alt. Gold for Tropical",
                "is_required": False,
            }
            slug = "performance-path-percent-above-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Performance Path % Above",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "alternative-bronze-and-silver-level-compliance-{}-{}".format(
                self.slug, data_type
            )
            annotation_type_data[slug] = {
                "name": "Alternative Bronze and Silver Level Compliance",
                "data_type": AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
                "valid_multiplechoice_values": "Alt Bronze,Alt Silver",
                "is_required": False,
            }

            slug = "eri-score-percent-less-than-energy-star-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "ERI Score Percent Less than ENERGY STAR",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "epa-national-eri-target-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "EPA National ERI Target",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "eri-as-designed-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "ERI As Designed",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "water-path-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Water Path",
                "data_type": AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
                "valid_multiplechoice_values": "Performance Path,Prescriptive Path",
                "is_required": False,
            }

            slug = "wri-score-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "WRI Score (required when Performance Path is selected for water)",
                "data_type": AnnotationType.DATA_TYPE_INTEGER,
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
