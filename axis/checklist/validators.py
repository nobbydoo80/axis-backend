"""validators.py: Validators for the various types of checklist question types. """


import logging

from django.forms import ValidationError

import dateutil
import datetime

from . import strings

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Answer validators get wrapped in a functools.partial by the Question.get_validator_for_type()
# method, which provides the "question" variable.
# Each possible question type should be represented here, to build a full mapping of types to
# validators.
def validate_open_answer(question, answer_value, **kwargs):
    return answer_value


def validate_multiple_choice_answer(question, answer_value, **kwargs):
    from .models import QuestionChoice

    override_comment_requirement = kwargs.get("override_comment_requirement", False)
    comment = kwargs.get("comment", None)
    try:
        question_choice = question.question_choice.get(choice__iexact=answer_value)
    except QuestionChoice.DoesNotExist:
        msg = strings.INVALID_QUESTION_CHOICE
        raise ValidationError(
            msg % ", ".join(list(question.question_choice.values_list("choice", flat=True)))
        )
    if question_choice.comment_required and not comment and not override_comment_requirement:
        msg = strings.QUESTION_CHOICE_REQUIRES_COMMENT
        raise ValidationError(msg)
    return question_choice.choice


def validate_datetime_answer(question, answer_value, **kwargs):
    if isinstance(answer_value, datetime.date):
        return datetime.datetime.fromordinal(answer_value.toordinal())

    if isinstance(answer_value, datetime.datetime):
        return answer_value

    try:
        answer_value = dateutil.parser.parse(answer_value, yearfirst=True)
    except:
        msg = strings.UNKNOWN_DATETIME_FORMAT
        raise ValidationError(msg)
    return answer_value


def validate_date_answer(question, answer_value, **kwargs):
    if isinstance(answer_value, datetime.date):
        return answer_value

    if isinstance(answer_value, datetime.datetime):
        return answer_value.date()

    try:
        answer_value = dateutil.parser.parse(answer_value, yearfirst=True)
        return answer_value.date()
    except:
        msg = strings.UNKNOWN_DATE_FORMAT
        raise ValidationError(msg)


def validate_integer_answer(question, answer_value, **kwargs):
    """Adds a check for min/max values based on the source question's configuration."""
    try:
        answer_value = int(answer_value)
    except (ValueError, TypeError):
        msg = strings.VALUE_NOT_AN_INTEGER
        raise ValidationError(msg)
    if question.minimum_value and answer_value < question.minimum_value:
        msg = strings.VALUE_TOO_SMALL
        raise ValidationError(msg.format(minimum=int(question.minimum_value)))
    if question.maximum_value and answer_value > question.maximum_value:
        msg = strings.VALUE_TOO_LARGE
        raise ValidationError(msg.format(maximum=int(question.maximum_value)))
    return answer_value


def validate_int_answer(question, answer_value, **kwargs):
    return validate_integer_answer(question, answer_value, **kwargs)


def validate_float_answer(question, answer_value, **kwargs):
    """Adds a check for min/max values based on the source question's configuration."""
    try:
        answer_value = float(answer_value)
    except (ValueError, TypeError):
        msg = strings.VALUE_NOT_A_FLOAT
        raise ValidationError(msg)
    if question.minimum_value and answer_value < question.minimum_value:
        msg = strings.VALUE_TOO_SMALL
        raise ValidationError(msg.format(minimum=question.minimum_value))
    if question.maximum_value and answer_value > question.maximum_value:
        msg = strings.VALUE_TOO_LARGE
        raise ValidationError(msg.format(maximum=question.maximum_value))
    return answer_value


def validate_csv_answer(question, answer_value, **kwargs):
    try:
        answer_value = ",".join([bit.strip() for bit in answer_value.split(",")])
    except:
        # FIXME: I think this is only an exception if we're not handling unicode correctly
        msg = strings.VALUE_NOT_A_CSV_LIST
        raise ValidationError(msg)
    return answer_value


def validate_kvfloatcsv_answer(question, answer_value, **kwargs):
    final = []

    log = kwargs.get("log", logging.getLogger(__name__))

    # Filter away blanks between commas
    items = filter(None, map(unicode.strip, "{}".format(answer_value).split(",")))

    for i, item in enumerate(items):
        data = filter(None, item.split(":"))

        # There might be more than 2 parts if the key had a space in it (e.g., "Foo Bar: Value")
        if len(data) < 2:
            data = filter(None, item.split(" "))
            if len(data) < 2:
                # log.info("Only one component found (%r)", data)
                continue

        key = " ".join(data[:-1]).rstrip(":")
        try:
            value = float(data[-1])
        except ValueError:
            msg = strings.UNKNOWN_KVFLOATCSV_VALUE
            raise ValidationError(msg.format(i=i + 1, key=data[-1]))
        final.append("{}:{}".format(key, value))

    if not len(final):
        msg = strings.VALUE_NOT_A_KVFLOATCSV_LIST
        raise ValidationError(msg)

    return ",".join(final)
