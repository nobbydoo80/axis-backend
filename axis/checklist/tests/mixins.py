"""fixturecompilers: Django checklist"""

import logging
import random

from django_input_collection.models import CollectionRequest

log = logging.getLogger(__name__)

__author__ = "Steven Klass"
__date__ = "3/19/14 4:12 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CollectedInputMixin:
    @classmethod
    def add_collected_input(cls, home_status, measure_id, value, **defaults):
        if not home_status.collection_request:
            home_status.set_collection_from_program()
            home_status.refresh_from_db()

        defaults["user"] = defaults.pop("user", home_status.company.users.first())

        collection_request = home_status.collection_request
        collector = home_status.get_collector(cls=defaults.pop("collector_cls", None))

        instrument = collection_request.collectioninstrument_set.get(measure_id=measure_id)
        payload = collector.make_payload(instrument, value, **defaults)
        existing = collector.get_inputs(instrument).first()
        if existing:
            log.debug(f"Removing {existing=}")
            collector.remove(instrument, existing)
        return collector.store(**collector.clean_payload(payload))

    @classmethod
    def remove_collected_input(cls, home_status, measure_id=None):
        collection_request = home_status.collection_request
        collector = home_status.get_collector()

        # Get the instrument
        if measure_id != "__all__":
            instrument = collection_request.collectioninstrument_set.get(measure_id=measure_id)

            existing = collector.get_inputs(instrument).first()
            if existing:
                collector.remove(instrument, existing)

        else:
            collection_request = home_status.collection_request.id
            from axis.home.models import EEPProgramHomeStatus

            EEPProgramHomeStatus.objects.filter(id=home_status.id).update(collection_request=None)
            CollectionRequest.objects.filter(id=collection_request).delete()
            home_status.refresh_from_db()

    @classmethod
    def get_unanswered_measures(cls, home_status):
        return list(
            home_status.get_unanswered_questions().values_list("measure", flat=True).distinct()
        )

    @classmethod
    def get_answered_questions(cls, home_status, context=None):
        if context is None:
            context = {
                "user_role": "rater" if not home_status.eep_program.is_qa_program else "qa",
            }

        try:
            return list(
                home_status.get_collector(**context)
                .get_inputs(cooperative_requests=True)
                .values_list("instrument__measure", flat=True)
                .distinct()
            )
        except ValueError:
            home_status.set_collection_from_program()
        return []

    def satisfy_measure(self, measure_id, home_status, user):
        instrument = home_status.collection_request.collectioninstrument_set.get(
            measure_id=measure_id
        )

        if instrument.type_id == "float":
            answer = round(random.uniform(1, 100), 4)
        elif instrument.type_id == "integer":
            answer = random.randrange(1, 100)
        elif instrument.type_id == "float":
            answer = random.randrange(1, 100)
        elif instrument.type_id == "open":
            answer = "Answered"
        elif instrument.type_id == "multiple-choice":
            # Pick an easy answer
            choices = instrument.bound_suggested_responses.filter(
                photo_required=False,
                document_required=False,
                is_considered_failure=False,
                comment_required=False,
            )
            choices = choices.values_list("suggested_response__data", flat=True)
            answer = random.choice(list(choices))
        elif instrument.type_id == "cascading-select":
            collector = home_status.get_collector()
            data = collector.get_method(instrument).structure_source()
            brand = random.choice(list(data.keys()))
            model = random.choice(list(data[brand].keys()))
            chars = random.choice(data[brand][model])
            answer = {"brand_name": brand, "model_number": model}
            answer.update(chars)
        else:
            raise TypeError(
                "Unable to satisfy instrument type of %r for measure %r"
                % (instrument.type_id, measure_id)
            )
        self.add_collected_input(
            value=answer, home_status=home_status, measure_id=measure_id, user=user
        )

    def satisfy_collection_request(self, home_status, user=None, pct=100):
        user = user if user else home_status.company.users.first()

        context = {
            "user_role": "rater" if not home_status.eep_program.is_qa_program else "qa",
        }

        while True:
            answered_questions = self.get_answered_questions(home_status, context)
            remaining_questions = home_status.get_unanswered_questions()
            total = len(answered_questions) + remaining_questions.count()

            try:
                actual_pct = len(answered_questions) / float(total) * 100.0
            except ZeroDivisionError:
                actual_pct = 100

            log.debug(
                f"{len(answered_questions) / float(total):.2%}  "
                f"({len(answered_questions)}/{total}) complete for "
                f"{home_status.eep_program.slug} on {home_status.home}",
            )

            if actual_pct >= pct:
                break

            self.satisfy_measure(remaining_questions.first().measure, home_status, user)
