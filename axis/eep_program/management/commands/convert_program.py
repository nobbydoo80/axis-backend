"""convert_program.py - Axis"""

__author__ = "Steven K"
__date__ = "8/5/21 08:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.db.models import F

from django_input_collection.collection import Collector

from axis.checklist.collection.collectors import ChecklistCollector
from axis.checklist.models import Answer, CollectedInput, QAAnswer
from axis.eep_program.models import EEPProgram

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Converts a legacy program to a collection."

    def add_arguments(self, parser):
        """Add arguments"""
        parser.add_argument(
            "-p",
            "--eep_program",
            action="store",
            dest="program",
            type=str,
            required=True,
            help="Program slug",
        )
        parser.add_argument(
            "-H",
            "--home_id",
            action="store",
            dest="home_id",
            type=int,
            required=False,
            help="Home ID",
        )

        parser.add_argument(
            "--verify",
            action="store_true",
            dest="verify_only",
            help="Only verify conversion",
        )

    collectors_cache = {}
    bad_measures_cache = defaultdict(set)

    def get_collector(self, program_slug, home, measure, **context):
        home_status = home.homestatuses.get(eep_program__slug=program_slug)
        if not home_status.collection_request:
            if not home_status.eep_program.collection_request:
                print(
                    "This program has not even started the conversion! To do this "
                    "perform the following:"
                )
                print(f"-  ./manage.py write_program -p {program_slug}")
                print("-  Review and add the program to legacy")
                print("-  Add the program to eep_program.apps")
                print(f"-  ./manage.py build_program -p {program_slug}")
                print(
                    "-  Add a test in axis.eep_program.tests.program_builder.test_program_builder.LegacyProgramBuilder"
                )
                print(f"-  ./manage.py convert_program -p {program_slug}")
                raise IOError("This program has not been created / built")
            home_status.set_collection_from_program()

        if not home_status or measure in self.bad_measures_cache.get(home_status.id, ()):
            return None

        try:
            home_status.eep_program.collection_request.collectioninstrument_set.get(measure=measure)
        except ObjectDoesNotExist:
            # This is OK - The measure
            self.stderr.write(f"Missing measure {measure} on program {program_slug}?")
            self.bad_measures_cache.setdefault(home_status.id, set()).add(measure)
            return None

        collector = self.collectors_cache.get(home_status.id)
        if collector is None:
            collector = ChecklistCollector(
                home_status.collection_request, expand_context_companies=False, **context
            )

            # Monkeypatches for migration system
            role = "qa" if home_status.eep_program.is_qa_program else "rater"
            collector.get_user_role = lambda user: context.get("user_role", role)
            collector.is_instrument_allowed = lambda instrument: True
            self.collectors_cache[home_status.id] = collector

        return collector

    def get_answers_for_program(self, program, home_id=None):
        question_slugs = list(
            program.get_checklist_question_set().all().values_list("slug", flat=True)
        )
        kwargs = dict(home__homestatuses__eep_program=program, question__slug__in=question_slugs)
        if home_id:
            kwargs["home_id"] = home_id
        if program.is_qa_program:
            answers = QAAnswer.objects.filter(**kwargs).annotate(measure=F("question__slug"))
            if answers.count():
                return answers
        return Answer.objects.filter(**kwargs).annotate(measure=F("question__slug"))

    def convert_program(self, program, home_id=None, max_count=None):
        """This will convert a program over to collection request"""

        answers = self.get_answers_for_program(program, home_id)
        max_count = max_count if max_count else answers.count()
        created = 0

        considered_answers = list(answers)[:max_count]
        self.stdout.write(
            f"Reviewing/Creating {len(considered_answers)}/{answers.count()} on program {program!r}"
        )
        for idx, answer in enumerate(considered_answers):
            if idx and idx % 500 == 0:
                self.stdout.write(f"{idx / len(considered_answers):.1%} Complete - {idx}")
            context = {"user_role": "qa" if program.is_qa_program else "rater"}
            collector = self.get_collector(program.slug, answer.home, answer.measure, **context)
            if collector is None:
                raise IOError("This should not happen")

            home_status = collector.collection_request.eepprogramhomestatus
            instrument = collector.get_instrument(measure=answer.measure)

            package = dict(
                instrument=instrument,
                data={
                    "input": answer.answer,
                    "comment": answer.comment,
                    "hints": {
                        "SPECULATIVE": True,
                        "LEGACY": True,
                        "answer_id": answer.id,
                    },
                },
                collection_request=collector.collection_request,
                user=answer.user,
                user_role=context["user_role"],
                is_failure=answer.is_considered_failure,
                failure_is_reviewed=answer.failure_is_reviewed,
                home=home_status.home,
                home_status=home_status,
            )

            if CollectedInput.objects.filter(**package).count():
                continue

            package.update(
                dict(
                    defaults={
                        "collector_class": "axis.checklist.collection.collectors.ChecklistCollector",
                        "collector_id": collector.get_identifier(),
                        "collector_version": ".".join(
                            ["{}".format(x) for x in collector.__version__]
                        ),
                        "version": ".".join(["{}".format(x) for x in Collector.__version__]),
                        "date_created": answer.created_date,
                        "date_modified": answer.modified_date,
                    }
                )
            )

            _obj, _created = CollectedInput.objects.get_or_create(**package)
            if _created:
                created += 1
        self.stdout.write(
            f"Program {program} has been converted {created} new collection responses!"
        )

    def verify_program_conversion(self, program, home_id=None, max_count=None):
        """This will verify that a program has been effectively cut over"""
        if not program.collection_request:
            raise CommandError(f"Unable to verify {program!r} as it hasn't been converted yet.")

        answers = self.get_answers_for_program(program, home_id)
        max_count = max_count if max_count else answers.count()
        errors = 0

        considered_answers = list(answers)[:max_count]
        self.stdout.write(
            f"Reviewing {len(considered_answers)}/{answers.count()} on program {program!r}"
        )
        for idx, answer in enumerate(considered_answers):
            if idx and idx % 500 == 0:
                self.stdout.write(f"{idx / len(considered_answers):.1%} Complete - {idx}")
            context = {"user_role": "qa" if program.is_qa_program else "rater"}
            collector = self.get_collector(program.slug, answer.home, answer.measure, **context)
            if collector is None:
                raise IOError("This should not happen")

            home_status = collector.collection_request.eepprogramhomestatus
            instrument = collector.get_instrument(measure=answer.measure)

            collected_input = CollectedInput.objects.filter(
                user_role=context["user_role"],
                is_failure=answer.is_considered_failure,
                failure_is_reviewed=answer.failure_is_reviewed,
                home=home_status.home,
                home_status=home_status,
                instrument=instrument,
                user=answer.user,
            )
            if collected_input.count() == 0:
                self.stderr.write(f"Missing Input for {answer.measure} on home {home_status.home}")
                errors += 1
                continue
            elif collected_input.count() > 1:
                last = collected_input.last()
                removed_data = collected_input.exclude(id=last.id)
                self.stderr.write(
                    f"Warning: Multiple Inputs for {answer.measure} on home {home_status.home} - "
                    f"Removing {removed_data.count()} inputs"
                )
                removed_data.delete()
                collected_input = last

            else:
                collected_input = collected_input.get()

            if collected_input.data["input"] != answer.answer:
                errors += 1
                self.stderr.write(
                    f"Answer mis-alignment {answer.measure} {collected_input.data['input']} "
                    f"on home {home_status.home}"
                )

        try:
            converted = (len(considered_answers) - errors) / len(considered_answers)
        except ZeroDivisionError:
            converted = 0

        if errors:
            self.stderr.write(
                f"Program {program} has has {errors} errors {converted:.2%} converted!"
            )
        else:
            self.stdout.write(f"Program {program} has been {converted:.2%} validated!")

    def handle(self, *app_labels, **options):
        """Does the lifting"""
        max_count = None

        eep_program = EEPProgram.objects.filter(slug=options["program"]).first()
        if eep_program is None or eep_program.get_checklist_question_set().count() is None:
            raise CommandError(
                f"Program {options['program']!r} not found or program has no questions to convert!"
            )

        if options["verify_only"]:
            self.verify_program_conversion(
                eep_program, home_id=options["home_id"], max_count=max_count
            )
        else:
            self.convert_program(eep_program, home_id=options["home_id"], max_count=max_count)
