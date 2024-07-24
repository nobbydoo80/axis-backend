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


class NGBSSFNewConstruction2015(ProgramBuilder):
    name = "2015 SF New Construction"
    slug = "ngbs-sf-new-construction-2015-new"
    owner = "provider-home-innovation-research-labs"
    certifiable_by = ["provider-home-innovation-research-labs"]

    visibility_date = datetime.date(year=2015, month=11, day=1)
    start_date = datetime.date(year=2015, month=2, day=1)
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
            slug = "energy-path-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Energy Path",
                "data_type": AnnotationType.DATA_TYPE_MULTIPLE_CHOICE,
                "valid_multiplechoice_values": "Performance path,Prescriptive Path,"
                "HERS Index Target,"
                "Alt. Bronze or Silver",
                "is_required": False,
            }
            slug = "performance-path-percent-above-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Performance Path % Above",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }
            slug = "hers-index-percent-less-than-energy-star-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "HERS Index Percent less than ENERGY STAR",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

            slug = "energy-star-hers-index-target-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "ENERGY STAR HERS Index Target",
                "data_type": AnnotationType.DATA_TYPE_INTEGER,
                "is_required": False,
            }
            slug = "as-designed-home-hers-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "As Designed Home HERS",
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

        return annotation_type_data
