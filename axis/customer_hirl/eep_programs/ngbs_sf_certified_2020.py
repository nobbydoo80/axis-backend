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


class NGBSSFCertified2020(ProgramBuilder):
    name = "2020 SF Certified"
    slug = "ngbs-sf-certified-2020-new"
    owner = "provider-home-innovation-research-labs"
    certifiable_by = ["provider-home-innovation-research-labs"]

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
                "valid_multiplechoice_values": "Performance path,Prescriptive Path," "ERI Path,",
                "is_required": False,
            }
            slug = "total-reference-annual-energy-{}-{}".format(self.slug, data_type)
            annotation_type_data[slug] = {
                "name": "Total Reference Annual Energy",
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
                "valid_multiplechoice_values": "Prescriptive Path, Alt. Compliance Path",
                "is_required": False,
            }

            slug = "wri-score-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "WRI Score",
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

            slug = "total-leakage-{}-{}".format(self.slug, data_type)

            annotation_type_data[slug] = {
                "name": "Total Leakage",
                "data_type": AnnotationType.DATA_TYPE_OPEN,
                "is_required": False,
            }

        return annotation_type_data
