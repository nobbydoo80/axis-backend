from axis.examine.machinery import ReadonlyMachineryMixin, PanelMachinery
from axis.qa.api import QANoteViewSet
from axis.qa.models import QANote


__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeQANoteDocumentExamineMachinery(ReadonlyMachineryMixin, PanelMachinery):
    model = QANote
    type_name = "qa_note"
    api_provider = QANoteViewSet

    regionset_template = "examine/home/qanote_with_document_regionset.html"
    region_template = "examine/home/qanote_with_document_region.html"
    detail_template = "examine/home/qanote_with_document_detail.html"
