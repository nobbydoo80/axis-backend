"""utils.py - Axis"""

__author__ = "Steven K"
__date__ = "10/27/21 15:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import typing

import dateutil.parser
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from axis.eep_program.models import EEPProgram

log = logging.getLogger(__name__)


def validate_annotation_type_content(annotation_type, value, log=None):
    """Verify an proposed value against an annotation type"""
    log = log if log else logging.getLogger(__name__)

    if annotation_type.data_type == "open":
        if isinstance(value, str) and len(value) > 500:
            log.error(
                f"Annotation {annotation_type} is restricted to a maximum length of 500 characters"
            )
            value = None
    elif annotation_type.data_type == "multiple-choice":
        if annotation_type.valid_multiplechoice_values:
            value = annotation_type.get_multiplechoice_value(value, app_log=log)
    elif annotation_type.data_type == "date":
        if isinstance(value, (datetime.datetime, datetime.date)):
            value = value.strftime("%m-%d-%Y")
        try:
            _date = dateutil.parser.parse(value)
        except dateutil.parser.ParserError:
            log.error(
                f"Annotation {annotation_type} cannot recognize {value} as a date",
            )
            value = None
        else:
            value = _date.strftime("%m-%d-%Y")

    elif annotation_type.data_type == "integer":
        try:
            if f"{value}".isnumeric and int(value) == float(value):
                value = f"{int(value)}"
            else:
                log.error(
                    f"Annotation {annotation_type} cannot recognize {value} as a whole number"
                )
                value = None
        except ValueError:
            log.error(f"Annotation {annotation_type} cannot recognize {value} as a whole number")
            value = None
    elif annotation_type.data_type == "float":
        try:
            float(value)
            value = f"{value}"
        except ValueError:
            log.error(
                f"Annotation {annotation_type} cannot recognize {value!r} as a decimal number"
            )
            value = None
    return {
        "type": annotation_type,
        "content": value,
    }


def validate_annotation_by_name(
    eep_program: EEPProgram,
    annotation_name: str,
    value: str,
    log: typing.Union[logging.Logger, None],
):
    try:
        annotation_type = eep_program.required_annotation_types.get(name__iexact=annotation_name)
    except ObjectDoesNotExist:
        log.error(f"Annotation {annotation_name!r} is not recognized for the program {eep_program}")
        return

    return validate_annotation_type_content(annotation_type, value, log)


def validate_annotations(
    eep_program: EEPProgram,
    annotations: typing.Union[list, None],
    log: typing.Union[logging.Logger, None],
) -> list:
    annotations = annotations if annotations is not None else []
    log = log if log else logging.getLogger(__name__)

    for item in annotations:
        if "type" not in item or "content" not in item:
            raise ValidationError(
                f"Expecting a list of `type` and `content` for annotations got {item!r}"
            )

    results = []
    valid_annotations = {x.slug: x for x in eep_program.required_annotation_types.all()}
    for proposed_annotation in annotations:
        if proposed_annotation["type"] not in valid_annotations:
            log.warning(
                f"Annotation provided ({proposed_annotation['type']}) "
                f"is not included in program {eep_program}"
            )
            continue
        result = validate_annotation_type_content(
            valid_annotations[proposed_annotation["type"]], proposed_annotation["content"], log
        )
        if result["content"] is not None:
            results.append(result)
    return results
