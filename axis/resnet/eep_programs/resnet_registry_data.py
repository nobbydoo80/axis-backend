__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import logging
from collections import OrderedDict

from axis.customer_neea.neea_data_report.models import NEEACertification
from axis.eep_program.program_builder.base import ProgramBuilder

log = logging.getLogger(__name__)


class ResnetRegistryData(ProgramBuilder):
    slug = "resnet-registry-data"
    name = "RESNET Registry Data"
    owner = "eep-resnet"

    require_input_data = True
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    measures = {
        "rater": {},
    }

    annotations = OrderedDict(
        [
            (
                type_slug,
                {
                    "is_unique": True,
                    "data_type": "open",
                    "is_required": False,
                },
            )
            for type_slug in NEEACertification.ANNOTATIONS
        ]
    )
