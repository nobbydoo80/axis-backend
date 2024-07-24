"""search.py: Django home"""


from appsearch.registry import ModelSearch, search
from .models import CheckList, Answer

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class ChecklistSearch(ModelSearch):
    display_fields = ("name",)

    search_fields = (
        "name",
        "description",
        {
            "questions": (
                ("Question", "question"),
                {
                    "answer": (
                        ("Answer", "answer"),
                        {"user": ({"company": (("Answered by company", "name"),)},)},
                    )
                },
            )
        },
    )


class AnswerSearch(ModelSearch):
    display_fields = (
        ("Question", "question__question"),
        "answer",
        ("Lot Number", "home__lot_number"),
        ("Street", "home__street_line1"),
        ("Subdivision", "home__subdivision"),
        ("Last Modified", "modified_date"),
    )

    search_fields = (
        "answer",
        "comment",
        ("Answered Date", "created_date"),
    )


search.register(CheckList, ChecklistSearch)
search.register(Answer, AnswerSearch)
