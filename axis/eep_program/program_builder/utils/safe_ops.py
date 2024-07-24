"""Program checklist utils"""


import logging

from django_input_collection import models as collection_models

from axis.checklist.models import AxisBoundSuggestedResponse
from . import unsafe_ops


__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


# NOTE: All functions in this module should allow back-to-back executions without creating duplicate
# objects.


def convert_checklist_to_collection(eep_program, exclude=[]):
    """
    Generates a CollectionRequest on the given program identical to the existing required_checklists
    questions.
    """

    collection_request = derive_collection_request(to=eep_program)
    eep_program.collection_request = collection_request
    eep_program.save()

    queryset = eep_program.get_checklist_question_set()
    if exclude:
        queryset = queryset.exclude(slug__in=exclude)

    for i, question in enumerate(queryset):
        # Supporting pieces
        group_info = {
            "id": "checklist",
        }
        measure_info = {
            "id": question.slug,
        }
        type_info = {
            "type": question.type,
            "unit": question.unit,
        }
        response_policy_info = {
            "nickname": None,
            "restrict": question.question_choice.exists(),
            "multiple": False,  # Unsupported in legacy checklists
            "required": not question.is_optional,
        }

        # Get hard references
        group = derive_group(**group_info)
        measure = derive_measure(**measure_info)
        type = derive_type(**type_info)
        response_policy = derive_response_policy(**response_policy_info)
        # condition = derive_condition(**condition_info)

        # Build instrument
        instrument_info = {
            "order": i * 10,  # Tracks with question.priority because queryset is ordered
            "text": question.question,
            "description": question.description or "",
            "help": question.help_url or "",
            # References
            "group": group,
            "measure": measure,
            "type": type,
            "response_policy": response_policy,
            "collection_request": collection_request,
        }
        instrument = derive_instrument(**instrument_info)

        # Add choices
        choices_info = question.question_choice.values()
        for choice_info in choices_info:
            suggested_response = derive_suggested_response(data=choice_info["choice"])
            for k in [
                "id",
                "choice",
                "choice_order",
                "created_date",
                "display_as_failure",
                "display_flag",
                "email_required",
                "modified_date",
            ]:
                del choice_info[k]
            derive_bound_suggested_response(
                collection_instrument=instrument,
                suggested_response=suggested_response,
                **choice_info,
            )

        collection_request.collectioninstrument_set.add(instrument)


def _update_or_create(model, defaults={}, **lookup_kwargs):
    obj, _ = model.objects.update_or_create(defaults=defaults, **lookup_kwargs)
    return obj


def derive_collection_request(to, **kwargs):
    collection_request, _ = collection_models.CollectionRequest.objects.get_or_create(
        id=to.collection_request_id
    )
    re_fetch_qs = collection_models.CollectionRequest.objects.filter(id=collection_request.id)
    re_fetch_qs.update(**kwargs)

    collection_request = re_fetch_qs.get()
    to.collection_request = collection_request
    to.save()

    return collection_request


def derive_group(id):
    return _update_or_create(collection_models.CollectionGroup, id=id)


def derive_measure(id):
    return _update_or_create(collection_models.Measure, id=id)


def derive_type(type, unit=None):
    if unit:
        type = "{}-{}".format(type, unit)
    return _update_or_create(collection_models.CollectionInstrumentType, id=type)


def derive_response_policy(**attrs):
    return _update_or_create(collection_models.ResponsePolicy, **attrs)


def derive_suggested_response(choice=None, **kwargs):
    kwargs = {
        "data": choice or kwargs["data"],
    }
    return _update_or_create(collection_models.SuggestedResponse, **kwargs)


def derive_bound_suggested_response(suggested_response, collection_instrument, **kwargs):
    return _update_or_create(
        AxisBoundSuggestedResponse,
        **{
            "collection_instrument": collection_instrument,
            "suggested_response": suggested_response,
            "defaults": kwargs,
        },
    )


def derive_instrument(measure, collection_request, **kwargs):
    return _update_or_create(
        collection_models.CollectionInstrument,
        **{
            "collection_request": collection_request,
            "measure": measure,
            "defaults": kwargs,
        },
    )


def derive_condition(instrument, data_getter, condition_group):
    return _update_or_create(
        collection_models.Condition,
        **{
            "instrument": instrument,
            "data_getter": data_getter,
            "condition_group": condition_group,
        },
    )


def derive_condition_group(nickname=None, **attrs):
    if nickname is None:
        kwargs = attrs
    else:
        kwargs = {
            "nickname": nickname,
            "defaults": attrs,
        }
    return _update_or_create(collection_models.ConditionGroup, **kwargs)


def derive_case(nickname=None, **attrs):
    if nickname is None:
        kwargs = attrs
    else:
        kwargs = {
            "nickname": nickname,
            "defaults": attrs,
        }
    return _update_or_create(collection_models.Case, **kwargs)


def derive_program(slug, **kwargs):
    attrs = {
        "slug": slug,
    }
    from axis.eep_program.models import EEPProgram

    return _update_or_create(EEPProgram, defaults=kwargs, **attrs)
