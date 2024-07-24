"""checklist_analysis.py - Axis"""


import logging

__author__ = "Steven K"
__date__ = "5/18/20 09:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import re

from django.core.management import BaseCommand, CommandError
from django_input_collection.models.utils import lazy_clone

from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Base command to run program builder"""

    help = "Runs Program Builder for a Program"
    requires_system_checks = []

    errors = []

    def add_arguments(self, parser):
        """Add arguments"""
        parser.add_argument(
            "--home-status", action="store", dest="home_status", type=int, help="Project ID"
        )
        parser.add_argument("--home", action="store", dest="home", type=int, help="Home ID")
        parser.add_argument("--eep", action="store", dest="eep_program", help="Program Slug")
        parser.add_argument(
            "--measure", action="store", dest="measure", help="Measure", required=False
        )
        parser.add_argument(
            "--align", action="store_true", dest="align", help="Align them", default=False
        )

    def analyze_response_policy(self, instrument, master_instrument, align=False):
        """Verifies the response policy"""
        if instrument.response_policy.pk != master_instrument.response_policy.pk:
            if align:
                msg = "  Aligning reponse policay from %r to %r"
                instrument.response_policy = master_instrument.response_policy
                instrument.save()
            else:
                msg = "  WARNING: Instrument response policy has changed from %r to %r"
                self.errors.append(
                    msg % (instrument.response_policy, master_instrument.response_policy)
                )
            print(msg % (instrument.response_policy, master_instrument.response_policy))
        else:
            msg = (
                "    Validated Response Policy (%(id)s) Required: %(required)s, "
                "Restrict: %(restrict)s"
            )
            print(msg % instrument.response_policy.__dict__)

    def analyze_choices(self, instrument, master_instrument, align=False):
        """Verifies the choice options"""
        choices = instrument.get_choices()
        master_choices = master_instrument.get_choices()
        if set(choices) != set(master_choices):
            if align:
                msg = "  Aligning choices from %r to %r"
                instrument.suggested_responses.clear()
                for suggested_response in master_instrument.suggested_responses.all():
                    instrument.suggested_responses.add(suggested_response)
            else:
                msg = "  WARNING: Choices has changed from %r to %r"
                self.errors.append(msg % (choices, master_choices))
            print(msg % (choices, master_choices))
        else:
            if choices:
                print("    Validated %d choice responses" % len(choices))
                for choice in choices:
                    print("      * %r" % choice)

    def analyze_cases(self, condition_group, master_condition_group, align=False):
        """Align cases"""
        errors = False
        for master_case in master_condition_group.cases.all():
            if not condition_group.cases.filter(
                nickname=master_case.nickname,
                match_type=master_case.match_type,
                match_data=master_case.match_data,
            ).count():
                if align:
                    common_excludes = ["date_created", "date_modified"]
                    condition_group.cases.add(lazy_clone(master_case, exclude=common_excludes))
                    msg = "      Adding case %r to %r"
                else:
                    msg = "      WARNING case %r not found for %r"
                    self.errors.append(msg % (master_case, condition_group))
                print(msg % (master_case, condition_group))
                errors = True
            else:
                print("       Validated case %r" % master_case.describe().decode("utf8"))
        for case in condition_group.cases.all():
            if not master_condition_group.cases.filter(
                nickname=case.nickname, match_type=case.match_type, match_data=case.match_data
            ).count():
                if align:
                    condition_group.remove(case)
                    msg = "      Removing case %r from %r"
                else:
                    msg = "      WARNING Extra case %r found for %r"
                    self.errors.append(msg % (case, condition_group))
                print(msg % (case, condition_group))
                errors = True
        if not errors and condition_group.cases.count() > 1:
            print("      Validated %d cases" % condition_group.cases.count())

    def analyze_conditions(self, instrument, master_instrument, align=False):
        """Verifies conditions are the same.

        Conditions are copied and so they are unique.
        """
        conditions = instrument.conditions.all()
        master_conditions = master_instrument.conditions.all()
        if conditions.count() or master_conditions.count():
            print("    Inspecting %d conditions" % master_conditions.count())

        if conditions.count() != master_conditions.count():
            if align:
                msg = "     Condition counts do not align - We need to identify missing.."
            else:
                msg = "     WARNING: Condition counts do not align!!"
                self.errors.append(msg)
            print(msg)

        # According to `clone_collection_request` the conditions will have roughly the same
        # data_getter except the instrument:\d+ stuff .
        match_pairs, current_existing = [], []
        for master_condition in master_conditions:
            data_getter = re.sub(
                r"^instrument:\d+$", "instrument:%d" % instrument.id, master_condition.data_getter
            )

            existing = conditions.filter(data_getter=data_getter)
            match_pairs.append((master_condition, existing.first()))
            current_existing.append(existing.first())

        for condition in conditions:
            if condition in current_existing:
                continue
            data_getter = re.sub(
                r"^instrument:\d+$", "instrument:%d" % master_instrument.id, condition.data_getter
            )
            master_existing = master_conditions.filter(data_getter=data_getter)
            if (master_existing.first(), condition) not in match_pairs:
                if align:
                    msg = "     Existing condition %r not found on master - removing"
                    condition.delete()
                else:
                    msg = "     WARNING: Existing condition %r not found on master"
                    self.errors.append(msg % condition)
                print(msg % condition)

        # Now add any missing.
        for master_condition, current_condition in match_pairs:
            if current_condition is None:
                if align:
                    msg = "     Condition with data_getter %r is missing adding"
                    common_excludes = ["date_created", "date_modified"]
                    current_condition = lazy_clone(
                        master_condition,
                        exclude=common_excludes,
                        **{
                            "instrument_id": instrument.id,
                            "data_getter": re.sub(
                                r"^instrument:\d+$",
                                "instrument:%d" % instrument.id,
                                master_condition.data_getter,
                            ),
                        },
                    )
                else:
                    msg = "     WARNING: Condition with data_getter %r is missing!"
                    self.errors.append(msg % master_condition.data_getter)
                print(msg % master_condition.data_getter)
            if current_condition:
                if current_condition.condition_group != master_condition.condition_group:
                    if align:
                        msg = "     Existing condition group %r does not match master - Aligning %r"
                        print(
                            msg
                            % (current_condition.condition_group, master_condition.condition_group)
                        )
                        current_condition.condition_group = master_condition.condition_group
                        current_condition.save()

                    else:
                        msg = "     WARNING: Existing condition group %r does not match master %r"
                        print(
                            msg
                            % (current_condition.condition_group, master_condition.condition_group)
                        )
                        self.errors.append(
                            msg
                            % (current_condition.condition_group, master_condition.condition_group)
                        )
                else:
                    msg = "     Existing condition group %r validated"
                    print(msg % current_condition.condition_group.nickname)

                from django_input_collection.models import ConditionGroup

                condition_group = ConditionGroup.objects.get(
                    pk=current_condition.condition_group.pk
                )
                self.analyze_cases(condition_group, master_condition.condition_group, align)

    def analyze_instrument(self, instrument, master_instrument, align=False):
        """Analyzes an instrument"""
        _kw = {"text": instrument.text, "inst_id": instrument.pk, "measure": instrument.measure}
        print("  %(text)r - Instrument (%(inst_id)s) [%(measure)s]" % _kw)
        if instrument.text != master_instrument.text:
            if align:
                msg = "  Aligning instrument text from %r to %r"
                instrument.text = master_instrument.text
                instrument.save()
            else:
                msg = "  WARNING: Instrument text has changed from %r to %r"
                self.errors.append(msg % (instrument.text, master_instrument))
            print(msg % (instrument.text, master_instrument))
        self.analyze_response_policy(instrument, master_instrument, align)
        self.analyze_choices(instrument, master_instrument, align)
        self.analyze_conditions(instrument, master_instrument, align)
        if not master_instrument.conditions.all():
            print("    Unrestricted - No conditions required for this to show")
        answers = instrument.collectedinput_set
        if answers.count():
            print("    %d answers provided:" % answers.count())
            for answer in answers.all():
                print(
                    "      - %s (%s) answered with %r on %s"
                    % (answer.user, answer.user_role, answer.data, answer.date_created)
                )
        else:
            print("    No answer input provided")
        print("\n")

    def analyze_collection_request(
        self, collection_request, master=None, measure=None, align=False
    ):
        """Display out a collection request"""

        instruments = collection_request.collectioninstrument_set.all()
        if master:
            master_instruments = master.collectioninstrument_set.all()

        if measure:
            instruments = instruments.filter(measure_id=measure)
            if master:
                master_instruments = master_instruments.filter(measure_id=measure)

        msg = "Reviewing %d instrument(s)" % instruments.count()
        if master:
            msg += " against %d master instrument(s)" % instruments.count()
            if instruments.count() != master_instruments.count():
                print(" WARNING: Instrument count mismatch!")
                self.errors.append(" WARNING: Instrument count mismatch!")

        for instrument in instruments.all():
            master_instrument = instrument
            if master:
                master_instrument = master_instruments.get(measure_id=instrument.measure_id)
            self.analyze_instrument(instrument, master_instrument, align)

        measures = list(instruments.values_list("measure", flat=True))
        master_measures = list(master_instruments.values_list("measure", flat=True))
        if set(measures) != set(master_measures):
            for measure in list(set(master_measures) - set(measures)):
                if align:
                    instrument = master_instruments.get(measure_id=measure)
                    common_excludes = ["date_created", "date_modified"]
                    cloned_instrument = lazy_clone(
                        instrument,
                        exclude=common_excludes,
                        **{
                            "collection_request_id": collection_request.id,
                        },
                    )
                    for condition in instrument.conditions.all():
                        lazy_clone(
                            condition,
                            exclude=common_excludes,
                            **{
                                "instrument_id": cloned_instrument.id,
                                "data_getter": re.sub(
                                    r"^instrument:\d+$",
                                    "instrument:%d" % cloned_instrument.id,
                                    condition.data_getter,
                                ),
                            },
                        )
                    for bound_response in instrument.bound_suggested_responses.all():
                        lazy_clone(bound_response, collection_instrument_id=cloned_instrument.id)
                else:
                    print("Error: Measure %r is missing" % measure)
                    self.errors.append("Error: Measure %r is missing" % measure)

            for measure in list(set(measures) - set(master_measures)):
                print("Error: Measure %r is extra from master" % measure)
                self.errors.append("Error: Measure %r is extra from master" % measure)

    def handle(self, *args, **options):
        """Do the work"""
        align = options.get("align", False)

        base_object = None
        master_collection_request = None
        if options.get("home_status"):
            base_object = EEPProgramHomeStatus.objects.get(id=options.get("home_status"))
            master_collection_request = base_object.eep_program.collection_request
        elif options.get("home"):
            _kw = {"home_id": options.get("home")}
            if options.get("eep_program"):
                _kw["eep_program__slug"] = options.get("eep_program")
            try:
                base_object = EEPProgramHomeStatus.objects.get(**_kw)
            except EEPProgramHomeStatus.MultipleObjectsReturned:
                print("Multiple Program found for home.  Add the program slug to the kwargs")
                raise
            master_collection_request = base_object.eep_program.collection_request
        elif options.get("eep_program"):
            base_object = EEPProgram.objects.get(slug=options.get("eep_program"))
            align = False
        if base_object is None:
            msg = "You must provide at least a home id, home status id or program slug"
            raise CommandError(msg)

        collection_request = base_object.collection_request

        _kw = {
            "url": base_object.get_absolute_url(),
            "align": align,
            "object": base_object.__class__.__name__,
        }
        msg = "Analyzing on %(object)s %(url)s"
        if options.get("measure"):
            msg += " Measure %r" % options.get("measure")
        msg += " - (Align - %(align)s)"
        print(msg % _kw)

        self.analyze_collection_request(
            collection_request, master_collection_request, options.get("measure"), align
        )

        if not align and self.errors:
            print("Errors:")
            for error in self.errors:
                print(error)
            print("%d Errors found" % len(self.errors))

        if not align and not self.errors:
            print("Aligned and looking good!")
