"""new_construction_2020.py: """

__author__ = "Artem Hruzd"
__date__ = "01/22/2021 22:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.customer_hirl.tests.mixins.base_program import (
    HIRLScoringBaseTaskMixin,
)
from axis.customer_hirl.eep_programs import NGBSSFWRI2021, NGBSMFWRI2021


class HIRLScoringWRI2021TaskMixin(HIRLScoringBaseTaskMixin):
    program_builder_classes = [NGBSSFWRI2021, NGBSMFWRI2021]
