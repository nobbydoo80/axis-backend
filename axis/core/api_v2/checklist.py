from axis.checklist import api
from axis.filehandling.api import customerdocument_viewset_factory
from .router import api_router

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


# Modern
api_router.register(
    r"checklist/documents",
    customerdocument_viewset_factory("checklist.CollectedInput"),
    "collectedinput_documents",
)

# Legacy
api_router.register(
    r"answer/documents", customerdocument_viewset_factory("checklist.answer"), "answer_documents"
)
api_router.register(
    r"qaanswer/documents",
    customerdocument_viewset_factory("checklist.qaanswer"),
    "qaanswer_documents",
)
api_router.register(r"answer", api.AnswerViewSet, "answer")
api_router.register(r"qaanswer", api.QAAnswerViewSet, "qaanswer")
api_router.register(r"checklists", api.CheckListViewSet, "checklists")
api_router.register(r"section", api.SectionViewSet, "section")
api_router.register(r"questions", api.QuestionViewSet, "questions")
api_router.register(r"question_choices", api.QuestionChoiceViewSet, "question_choices")
