from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType

from axis.relationship.models import Relationship
from axis.checklist.models import Answer
from axis.checklist.utils import build_questionanswer_dict
from axis.home.models import Home, EEPProgramHomeStatus
from .models import SampleSet, SampleSetHomeStatus
from . import utils

__author__ = "Autumn Valenta"
__date__ = "8/1/14 10:02 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class SampleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleSet
        fields = "__all__"
        read_only_fields = ("id",)


class SampleSetHomeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleSetHomeStatus
        fields = "__all__"
        read_only_fields = ("id",)


class SampleSetSummarySerializer(serializers.Serializer):
    """Converts a SampleSet object to a collection of summary fields for the UI to use."""

    id = serializers.CharField()
    name = serializers.CharField(source="uuid")
    alt_name = serializers.CharField()
    test_homes = serializers.SerializerMethodField()
    sampled_homes = serializers.SerializerMethodField()
    builder_id = serializers.SerializerMethodField()
    builder_name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SampleSetSummarySerializer, self).__init__(*args, **kwargs)
        self._preload(self.instance)

    def _preload(self, obj):
        """Pre-load the required field data so we keep queries down during serialization."""

        from axis.core.utils import values_to_dict

        self._preloaded = {}

        field_names = {
            "id": "id",
            "is_test_home": "is_test_home",
            "home_status": "home_status_id",
            "home_status__eep_program": "eep_program_id",
            "home_status__eep_program__name": "eep_program",
            "home_status__home__street_line1": "street_line1",
            "home_status__home__street_line2": "street_line2",
            "home_status__home_id": "home_id",
            "home_status__home__subdivision_id": "subdivision_id",
            "home_status__home__subdivision__name": "subdivision",
            "home_status__home__metro_id": "metro_id",
            "home_status__home__metro__name": "metro",
            "home_status__incentivepaymentstatus__state": "payment_state",
        }
        question_field_names = {
            "question__id": "question_id",
            "question__question": "question",
            "id": "answer_id",
            "answer": "answer",
        }

        test_homes = []
        sampled_homes = []
        _homes = {
            True: test_homes,
            False: sampled_homes,
        }

        items = obj.samplesethomestatus_set.current()
        results = items.values(*field_names.keys())

        _home_content_type = ContentType.objects.get_for_model(Home)
        _builders = set()
        _question_cache = {}
        for result in results:
            # Transform the orm query paths to friendlier names as given above
            item = {field_names.get(k, k): v for k, v in result.items()}

            item["name"] = " ".join(
                filter(None, [item.pop("street_line1"), item.pop("street_line2")])
            )

            # Determine the builder info
            builder_rels = Relationship.objects.filter(
                object_id=item["home_id"],
                content_type=_home_content_type,
                company__company_type="builder",
            )
            try:
                builder = builder_rels.get().company
                item["builder"] = builder.name
                item["builder_id"] = builder.id
            except (Relationship.DoesNotExist, Relationship.MultipleObjectsReturned):
                # Can't really handle garbage input, just don't want to blow up with a 500
                item["builder"] = False
                item["builder_id"] = False

            # This is not a saved object, it just has an id from the database we know to be correct.
            # We can use it to execute instance methods on the model class that only need the id.
            # This probably is evidence of the fact that we need to move model logic into utilities.
            sshomestatus_standin = SampleSetHomeStatus(id=item["id"])
            sshomestatus_standin.home_status_id = item["home_status_id"]

            questions = _question_cache.setdefault(
                sshomestatus_standin.home_status.eep_program.pk, None
            )
            if questions is None:
                questions = sshomestatus_standin.get_questions()
                _question_cache[sshomestatus_standin.home_status.eep_program.pk] = questions

            # Get the answers that are give for this home first-hand (i.e., not collected via past
            # sampling associations).  These can be shared forward if the home is a test home.
            answers = sshomestatus_standin.get_source_answers(include_failures=False)
            item["source_answers"] = build_questionanswer_dict(questions, answers)

            # Get answers that have been collected by this home via past sampling associations.
            # These answers represent "pre-existing" answers on a home from before the sampleset
            # it's currently in (or, potentially, a previous revision of the current sampleset).
            answers = sshomestatus_standin.get_contributed_answers()
            item["contributed_answers"] = build_questionanswer_dict(questions, answers)

            # Answers that are currently considered to be in a failing state, which haven't yet been
            # corrected.
            answers = sshomestatus_standin.get_failing_answers()
            item["failing_answers"] = build_questionanswer_dict(questions, answers)

            # Certification flag
            item["is_certified"] = bool(sshomestatus_standin.home_status.certification_date)

            # Provide the absolute url to the home
            item["detail_url"] = Home(id=item["home_id"]).get_absolute_url()

            # Payment state preventing modifications.  These will likely be True in bulk in a
            # sampleset, but new items added to such a sampleset could have False here.
            item["is_locked"] = False
            if item["payment_state"]:
                if item["payment_state"] not in ["start", "ipp_payment_failed_requirements"]:
                    item["is_locked"] = True
            elif item["is_certified"]:
                item["is_locked"] = True

            target_home_group = _homes[item["is_test_home"]]
            target_home_group.append(item)
            _builders.add((item["builder"], item["builder_id"]))

        self._preloaded["test_homes"] = test_homes
        self._preloaded["sampled_homes"] = sampled_homes

        if len(_builders) == 1:
            builder_name, builder_id = list(_builders)[0]
            self._preloaded["builder_id"] = builder_id
            self._preloaded["builder"] = builder_name
        else:
            self._preloaded["builder_id"] = False
            self._preloaded["builder"] = False

    def _get_item_answers(self, id):
        from axis.core.utils import values_to_dict

        answer_results = Answer.objects.filter(samplesethomestatus__id=id).values(
            "question__id", "question__question", "id", "answer"
        )
        return values_to_dict(answer_results, "question__id")

    ## Field data suppliers
    def get_test_homes(self, obj):
        return self._preloaded["test_homes"]

    def get_sampled_homes(self, obj):
        return self._preloaded["sampled_homes"]

    def get_builder_id(self, obj):
        return self._preloaded["builder_id"]

    def get_builder_name(self, obj):
        return self._preloaded["builder"]
