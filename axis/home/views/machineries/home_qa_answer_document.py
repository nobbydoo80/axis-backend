from axis.examine.machinery import ReadonlyMachineryMixin, PanelMachinery
from axis.checklist.api import QAAnswerViewSet
from axis.checklist.models import QAAnswer

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeQAAnswerDocumentExamineMachinery(ReadonlyMachineryMixin, PanelMachinery):
    model = QAAnswer
    type_name = "qaanswer"
    api_provider = QAAnswerViewSet

    regionset_template = "examine/home/qaanswer_with_document_regionset.html"
    region_template = "examine/home/answer_with_document_region.html"
    detail_template = "examine/home/answer_with_document_detail.html"

    can_add_new = False
