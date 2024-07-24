"""home_qa_inspection_grade.py: """

__author__ = "Artem Hruzd"
__date__ = "04/01/2020 21:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from axis.core.views.machineries.inspection_grade import UserInspectionGradeExamineMachinery
from axis.examine import REGIONSET_PANEL_TEMPLATE


class HomeQAInspectionGradeExamineMachinery(UserInspectionGradeExamineMachinery):
    regionset_template = REGIONSET_PANEL_TEMPLATE

    def get_region_dependencies(self):
        return {"qastatus": [{"field_name": "id", "serialize_as": "qa_status"}]}

    def get_max_regions(self):
        return 1
