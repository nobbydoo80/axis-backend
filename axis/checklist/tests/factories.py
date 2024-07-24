"""factory.py: Django checklist"""

from django.utils.timezone import now

from axis.core.utils import random_sequence, random_digits
from ..models import Question, QuestionChoice, Answer, CheckList, Section

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


def question_choice_factory(**kwargs):
    """A basic choice factory.  get_or_create based on the field 'choice'."""
    kwrgs = {
        "choice": f"choice_{random_sequence(4)}_{random_sequence(3)}",
        "photo_required": False,
        "document_required": False,
        "email_required": False,
        "comment_required": False,
        "is_considered_failure": False,
        "display_as_failure": False,
        "choice_order": 1,
        "display_flag": True,
    }

    kwrgs.update(kwargs)
    choice = kwrgs.pop("choice")
    choice, create = QuestionChoice.objects.get_or_create(choice=choice, defaults=kwrgs)
    return choice


def question_factory(**kwargs):
    """A basic question factory.  get_or_create based on the field 'question'."""
    question_type = kwargs.pop("type", "open")

    question_choices = kwargs.pop("question_choices", [])
    if len(question_choices):
        question_type = "multiple-choice"

    kwrgs = {
        "priority": random_digits(3),
        "question": f"An {question_type.capitalize()} question {random_sequence(4)}",
        "type": question_type,
        "description": f"Description {random_sequence(4)}",
        "help_url": "http://question.org",
        "climate_zone": None,
        "unit": None,
        "allow_bulk_fill": False,
        "minimum_value": None,
        "maximum_value": None,
        "display_flag": True,
        "is_optional": False,
    }

    kwrgs.update(kwargs)
    question_txt = kwrgs.pop("question")

    question, create = Question.objects.get_or_create(question=question_txt, defaults=kwrgs)
    if create:
        if len(question_choices):
            if isinstance(question_choices[0], str):
                question_choices = [
                    question_choice_factory(choice=choice) for choice in question_choices
                ]
            question.question_choice.add(*question_choices)
    return question


def multiple_choice_question_factory(**kwargs):
    """A basic multiple-choice question factory.  get_or_create based on the field 'question'."""
    question_choices = kwargs.pop("question_choice", [])
    question_choice_count = kwargs.pop("question_choice_count", 3)
    if not len(question_choices):
        while len(question_choices) < question_choice_count:
            choice_name = f"Choice_{len(question_choices) + 1}_{random_sequence(4)}"
            choice = question_choice_factory(choice=choice_name)
            question_choices.append(choice)
    kwargs["type"] = "multiple-choice"
    kwargs["question_choice"] = question_choices
    return question_factory(**kwargs)


def answer_factory(question, home, user, **kwargs):
    """A basic answer question factory.  get_or_create based on the field 'answer', 'user', 'home."""
    in_bulk = kwargs.pop("in_bulk", False)

    kwrgs = {
        "answer": f"Answer_{random_sequence(4)}",
        "comment": f"Comment {random_sequence(4)}",
        "system_no": None,
        "type": "open",
        "photo_required": False,
        "document_required": False,
        "email_required": False,
        "email_sent": False,
        "is_considered_failure": False,
        "display_as_failure": False,
        "failure_is_reviewed": False,
        "confirmed": False,
        "display_flag": False,
        "bulk_uploaded": False,
    }

    kwrgs.update(kwargs)
    answer = kwrgs.get("answer")

    if question.type == "multiple_choice":
        assert answer in question.question_choice.all.values_list("choice", flat=True), "Bad answer"
        choice = question.question_choice.get(choice=answer)
        mc_dict = {
            "type": "open",
            "photo_required": choice.photo_required,
            "document_required": choice.document_required,
            "email_required": choice.email_required,
            "is_considered_failure": choice.is_considered_failure,
        }
        kwrgs.update(mc_dict)

    if in_bulk:
        kwrgs.update({"created_date": now(), "modified_date": now()})
        answer = Answer(home=home, question=question, user=user, **kwrgs)
    else:
        answer, create = Answer.objects.get_or_create(
            answer=answer, home=home, question=question, user=user, defaults=kwrgs
        )

    return answer


def checklist_factory(**kwargs):
    """A basic checklist factory.  get_or_create based on the field 'name'."""
    add_section = kwargs.pop("add_section", False)
    questions = kwargs.pop("questions", [])
    question_count = kwargs.pop("question_count", 2)
    question_count = question_count if question_count else 2
    question_prefix = kwargs.pop("question_prefix", "")
    kwrgs = {
        "name": f"Checklist {random_sequence(4)}",
        "public": False,
        "description": f"Description {random_sequence(4)}",
        "display_flag": True,
    }

    if not len(questions):
        while len(questions) < question_count:
            txt = f"{question_prefix}Q{len(questions) + 1} Question {random_sequence(4)}"
            questions.append(question_factory(question=txt))

    kwrgs.update(kwargs)
    name = kwrgs.pop("name")

    checklist, create = CheckList.objects.get_or_create(name=name, defaults=kwrgs)
    if create:
        checklist.questions.add(*questions)
        checklist.save()

    if add_section:
        name = f"Section {random_sequence(4)}"
        kwrgs = {
            "checklist": checklist,
            "description": f"Description {random_sequence(4)}",
            "display_flag": True,
        }
        section, create = Section.objects.get_or_create(name=name, **kwrgs)
        if create:
            section.questions.add(*questions)
            section.save()

    return checklist
