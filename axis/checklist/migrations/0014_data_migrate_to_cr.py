# Generated by Django 1.11.17 on 2019-04-15 13:31

from collections import defaultdict

from django.db import migrations
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist


from axis.checklist.collection.collectors import ChecklistCollector


# pylint: disable=invalid-name
def forward(apps, schema_editor):
    Answer = apps.get_model("checklist", "Answer")
    CollectedInput = apps.get_model("checklist", "CollectedInput")
    EEPProgram = apps.get_model("eep_program", "EEPProgram")

    convert = [
        "doe-zero-energy-ready-rev-05-performance-path",
        "earth-advantage-certified-home",
        "energy-star-version-31-rev-08",
        "energy-star-version-32-rev-08",
        "indoor-airplus-version-1-rev-03",
        "ngbs-sf-new-construction-2012",
        "neea-bpa",
        "eto-2018",
        "eto-2017",
        "eto-2016",
        "eto-2015",
        "eto",
    ]

    collectors_cache = {}
    bad_measures_cache = defaultdict(set)  # homestatus_id -> {measure_id}

    def get_collector(program_slug, home, measure, answer, **context):
        home_status = home.homestatuses.get(eep_program__slug=program_slug)

        if not home_status or measure in bad_measures_cache.get(home_status.id, ()):
            return None

        try:
            home_status.eep_program.collection_request.collectioninstrument_set.get(measure=measure)
        except ObjectDoesNotExist:
            bad_measures_cache.setdefault(home_status.id, set()).add(measure)
            return None

        collector = collectors_cache.get(home_status.id)
        if collector is None:
            collector = ChecklistCollector(
                home_status.collection_request, expand_context_companies=False, **context
            )

            # Monkeypatches for migration system
            collector.get_user_role = lambda user: "rater"
            collector.is_instrument_allowed = lambda instrument: True
            collectors_cache[home_status.id] = collector

        return collector

    num_programs = len(convert)
    for i, slug in enumerate(convert):
        program = EEPProgram.objects.get(slug=slug)
        assert program.collection_request, "Program appears uninitialized for input-collection"

        answers = Answer.objects.filter(home__homestatuses__eep_program__slug=slug).annotate(
            measure=F("question__slug")
        )
        total = answers.count()
        skipping = False
        for j, answer in enumerate(answers):
            context = {}
            collector = get_collector(slug, answer.home, answer.measure, answer, **context)
            if collector is None:
                if skipping is False:
                    skipping = True
                continue

            skipping = False
            if not hasattr(collector.collection_request, "eepprogramhomestatus"):
                continue

            home_status = collector.collection_request.eepprogramhomestatus
            instrument = collector.get_instrument(measure=answer.measure)
            CollectedInput.objects.create(
                **{
                    "date_created": answer.created_date,
                    "date_modified": answer.modified_date,
                    "data": {
                        "input": answer.answer,
                        "comment": answer.comment,
                        "hints": {
                            "SPECULATIVE": True,
                            "LEGACY": True,
                            "answer_id": answer.id,
                        },
                    },
                    "user_role": "rater",
                    "is_failure": answer.is_considered_failure,
                    "failure_is_reviewed": answer.failure_is_reviewed,
                    "collection_request": collector.collection_request,
                    "home": home_status.home,
                    "home_status": home_status,
                    "instrument": instrument,
                    "user": answer.user,
                }
            )
            # raise Exception('stop')
        # raise Exception('break')
    # raise Exception('finished')


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("checklist", "0013_fix_dupe_cases"),
        ("eep_program", "0008_shallow_migrate_to_cr"),
    ]

    operations = [migrations.RunPython(forward, backward)]
