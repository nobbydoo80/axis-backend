from axis.checklist.api import AnswerViewSet
from axis.checklist.models import Answer
from axis.examine.machinery import ReadonlyMachineryMixin, PanelMachinery

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeAnswerDocumentExamineMachinery(ReadonlyMachineryMixin, PanelMachinery):
    model = Answer
    type_name = "answer"
    api_provider = AnswerViewSet

    regionset_template = "examine/home/answer_with_document_regionset.html"
    region_template = "examine/home/answer_with_document_region.html"
    detail_template = "examine/home/answer_with_document_detail.html"

    can_add_new = False
