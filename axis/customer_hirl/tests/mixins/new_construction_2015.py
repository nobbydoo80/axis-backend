"""new_construction_2015.py: """

__author__ = "Artem Hruzd"
__date__ = "01/22/2021 22:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.customer_hirl.eep_programs import NGBSSFNewConstruction2015, NGBSMFNewConstruction2015
from axis.customer_hirl.tests.mixins.base_program import (
    HIRLScoringBaseTaskMixin,
)


class HIRLScoring2015NewConstructionTaskMixin(HIRLScoringBaseTaskMixin):
    program_builder_classes = [NGBSSFNewConstruction2015, NGBSMFNewConstruction2015]
