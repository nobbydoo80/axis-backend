"""test_mixins.py - Axis"""

__author__ = "Steven K"
__date__ = "8/9/21 08:57"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from enum import Enum

from django_input_collection.models import (
    CollectionInstrument,
    ResponsePolicy,
    Measure,
    CollectionInstrumentType,
    CollectionGroup,
)
from axis.checklist.models import CollectedInput

log = logging.getLogger(__name__)


class CollectionRequestMixin:
    @classmethod
    def build_answer(cls, value, comment=None):
        if isinstance(value, Enum):
            value = value.value

        data = value
        if isinstance(value, dict):
            if "input" not in value:
                comment = value.pop("comment", None)
                data = {"input": value}
                if comment:
                    data["comment"] = comment
        elif not isinstance(value, dict):
            data = {"input": value, "comment": comment or ""}

        if isinstance(data.get("input"), Enum):
            data["input"] = data["input"].value

        return data

    def add_collected_input(
        self,
        value,
        measure_id,
        user_role="rater",
        home_status=None,
        auto_create_instrument=False,
        **defaults,
    ):
        """This will fill an collection request for a measure"""

        if home_status is None:
            if not hasattr(self, "home_status"):
                msg = "We need to either be passed a home_status or set the attribute home_status"
                raise AttributeError(msg)
            home_status = self.home_status

        data = self.build_answer(value)

        if not home_status.collection_request:
            home_status.set_collection_from_program()
        try:
            instrument = home_status.collection_request.collectioninstrument_set.get(
                measure_id=measure_id
            )
        except CollectionInstrument.DoesNotExist:
            if not auto_create_instrument:
                print(f"Skipping measure {measure_id!r} not found!")
                return
            instrument = self.add_basic_instrument_based_on_data(
                measure_id, home_status.collection_request, data
            )
        user = defaults.get("user", home_status.company.users.first())
        if user is None:
            msg = f"We must have a user bound to {home_status.company} if we expect to get data.."
            raise TypeError(msg)

        answer, create = CollectedInput.objects.get_or_create(
            collection_request=home_status.collection_request,
            instrument=instrument,
            home_status=home_status,
            user_role=user_role,
            defaults=dict(
                user=user,
                home=home_status.home,
                data=data,
            ),
        )
        if not create:
            answer.data = data
            answer.home = home_status.home
            answer.user = defaults.get("user", home_status.company.users.first())
            answer.save()

    def add_bulk_answers(
        self, data, user_role="rater", home_status=None, auto_create_instrument=False, **defaults
    ):
        if not home_status.collection_request:
            home_status.set_collection_from_program()
            home_status = home_status.refresh_from_db()

        instruments = home_status.collection_request.collectioninstrument_set.all()
        instrument_dict = dict(instruments.values_list("measure_id", "pk"))
        remove_prior = defaults.pop("remove_prior", False)
        if remove_prior:
            CollectedInput.objects.filter(
                home_status=home_status,
                user_role=user_role,
                instrument__measure__in=instrument_dict.keys(),
            ).delete()

        user = defaults.get("user", home_status.company.users.first())
        answers = []
        errors = {}
        for measure_id, value in data.items():
            input_data = self.build_answer(value)
            try:
                instrument_id = instrument_dict[measure_id]
            except KeyError:
                if auto_create_instrument:
                    instrument = self.add_basic_instrument_based_on_data(
                        measure_id, home_status.collection_request, input_data
                    )
                    instrument_id = instrument.id
                else:
                    errors[measure_id] = input_data
                    continue

            answers.append(
                CollectedInput(
                    collection_request=home_status.collection_request,
                    instrument_id=instrument_id,
                    home_status=home_status,
                    home=home_status.home,
                    user_role=user_role,
                    user=user,
                    data=input_data,
                )
            )
        if errors:
            if not auto_create_instrument:
                raise KeyError(f"Unable to find measures {errors} in {instrument_dict.keys()}")

        CollectedInput.objects.bulk_create(answers)

    def add_basic_instrument_based_on_data(self, measure, collection_request, data):
        """This is used to hack in partial support for old stuff."""
        measure_, _ = Measure.objects.get_or_create(id=measure)
        group, _ = CollectionGroup.objects.get_or_create(id="default")
        segment, _ = CollectionGroup.objects.get_or_create(id="checklist")
        value = data.get("input")
        if isinstance(value, str):
            instrument_type, _ = CollectionInstrumentType.objects.get_or_create(id="open")
        elif isinstance(value, float):
            instrument_type, _ = CollectionInstrumentType.objects.get_or_create(id="float")
        elif isinstance(value, int):
            instrument_type, _ = CollectionInstrumentType.objects.get_or_create(id="integer")
        else:
            raise TypeError(f"No idea what to do with {value!r}")
        response_policy, _ = ResponsePolicy.objects.get_or_create(
            restrict=False, multiple=False, required=False, defaults={"nickname": "OPTIONAL Typed"}
        )

        return CollectionInstrument.objects.get_or_create(
            collection_request=collection_request,
            measure=measure_,
            type=instrument_type,
            text=measure.replace("_", " ").capitalize(),
            segment=segment,
            group=group,
            response_policy=response_policy,
        )[0]

    def remove_collected_input(
        self,
        measure_id,
        user_role="rater",
        home_status=None,
        raise_on_notfound=True,
        new_value=None,
    ):
        if home_status is None:
            if not hasattr(self, "home_status"):
                msg = "We need to either be passed a home_status or set the attribute home_status"
                raise AttributeError(msg)
            home_status = self.home_status

        try:
            instrument = home_status.collection_request.collectioninstrument_set.get(
                measure_id=measure_id
            )
        except CollectionInstrument.DoesNotExist:
            if raise_on_notfound:
                raise
            return
        try:
            answer = CollectedInput.objects.get(
                collection_request=home_status.collection_request,
                user_role=user_role,
                instrument=instrument,
                home_status=home_status,
            )
        except CollectedInput.DoesNotExist:
            if raise_on_notfound:
                raise
        else:
            if new_value is None:
                answer.delete()
                return
            answer.data = self.build_answer(new_value)
            answer.save()
            return answer

    def replace_collected_input(
        self,
        measure_id,
        value,
        user_role="rater",
        home_status=None,
        raise_on_notfound=True,
    ):
        self.remove_collected_input(
            measure_id=measure_id,
            user_role=user_role,
            home_status=home_status,
            raise_on_notfound=raise_on_notfound,
            new_value=self.build_answer(value),
        )

    def get_answered_questions(self, home_status=None):
        if home_status is None:
            if not hasattr(self, "home_status"):
                msg = "We need to either be passed a home_status or set the attribute home_status"
                raise AttributeError(msg)
            home_status = self.home_status

        return list(
            home_status.get_collector(user_role="rater")
            .get_inputs(cooperative_requests=True)
            .values_list("instrument__measure", flat=True)
            .distinct()
        )

    def get_unanswered_questions(self, home_status=None, measures_only=False):
        if home_status is None:
            if not hasattr(self, "home_status"):
                msg = "We need to either be passed a home_status or set the attribute home_status"
                raise AttributeError(msg)
            home_status = self.home_status
        if measures_only:
            return list(home_status.get_unanswered_questions().values_list("measure", flat=True))
        return home_status.get_unanswered_questions()
