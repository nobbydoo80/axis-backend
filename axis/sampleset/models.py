"""models.py: Django sampleset"""


import logging

from django.conf import settings
from django.db import models, IntegrityError
from django.urls import reverse
from simple_history.models import HistoricalRecords

from axis.company.models import Company
from axis.core.fields import UUIDField
from axis.home.tasks import certify_single_home
from . import strings
from . import utils
from .managers import SampleSetManager, SampleSetHomeStatusManager, SamplingProviderApprovalManager

__author__ = "Autumn Valenta"
__date__ = "07/09/14  4:20 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SampleSet(models.Model):
    """

    owner = models.ForeignKey('company.Company', related_name="samplesets")
    home_statuses = models.ManyToManyField('home.EEPProgramHomeStatus', through='SampleHome',
    Tracks groups of homes placed in a common industry Sample Set.  "test" and "sampled" homes are
    tracked separately, where "test" homes are providing answers to the rest of the "sampled" homes.
    """

    objects = SampleSetManager()
    history = HistoricalRecords()

    uuid = UUIDField(unique=True, editable=False)
    alt_name = models.CharField(max_length=32, blank=True, null=True)  # EFL names
    owner = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, related_name="owned_samplesets"
    )

    # Accessing this field directly isn't a good idea.
    # Go through self.samplesethomestatus_set to get narrowed versions of this relationship.
    home_statuses = models.ManyToManyField(
        "home.EEPProgramHomeStatus", through="SampleSetHomeStatus"
    )

    # Housekeeping
    start_date = models.DateField(auto_now_add=True, editable=False)
    confirm_date = models.DateField(blank=True, null=True)
    revision = models.PositiveIntegerField(default=0)

    # Behavioral modifiers
    is_metro_sampled = models.BooleanField(
        default=False,
        help_text="""Tracks last known state of this flag
                                           as calculated by its member homestatuses.""",
    )

    class Meta:
        ordering = ("uuid",)

    def __str__(self):
        return self.alt_name or self.uuid[:8]

    def save(self, *args, **kwargs):
        if self.pk and self.samplesethomestatus_set.current().count() > settings.SAMPLING_MAX_SIZE:
            msg = strings.SAMPLESET_FULL
            raise IntegrityError(msg.format(max_size=settings.SAMPLING_MAX_SIZE))
        return super(SampleSet, self).save(*args, **kwargs)

    @classmethod
    def can_be_added(cls, user):
        """Whether object can be created by user"""
        return user.has_perm("sampleset.add_sampleset")

    def can_be_edited(self, user):
        """Whether object can be edited or not"""
        if not self.is_full():
            if self.owner.id == user.company.id or user.is_superuser:
                return True
        return False

    def can_be_advanced(self):
        # TODO: Double check that we aren't going to invalidate the 7 max shared answers.
        has_test_homes = self.samplesethomestatus_set.current().filter(is_test_home=True).exists()
        has_failures = self.get_current_source_answers().get_uncorrected_failures().exists()
        return has_test_homes and not has_failures

    def can_be_certified(self):
        can_be_advanced = self.can_be_advanced()
        has_uncertified_homes = self.samplesethomestatus_set.current().uncertified().exists()
        return can_be_advanced and has_uncertified_homes

    def get_absolute_url(self):
        return reverse("sampleset:view", kwargs={"uuid": self.uuid})

    def advance(self):
        """
        Copy answer references in the current setup to the Sampled homes, and advance the revision
        number.  This generates new membership SampleSetHomeStatus items, where the old existing
        ones carry the frozen answer data, and the new ones are empty with the new revision value.
        """
        items = self.samplesethomestatus_set.current()
        items_list = list(items)  # copy unaffected by update() change to queryset

        # Get the answers currently being offered by the current test homes for the current phase.
        test_answers = self.get_current_source_answers()
        num_answers = test_answers.count()

        new_revision = self.revision + 1

        # Take away active status on items that are now revision-1
        items.update(is_active=False)

        # As a precaution, make sure no existing items are found on the new revision, which is a
        # data integrity failure.
        _previous_partial_failures = self.samplesethomestatus_set.filter(revision=new_revision)
        if _previous_partial_failures.count():
            log.warning(
                "SampleSet %r (pk=%r) is advancing to revision=%d, but found %d existing "
                "items already there!  The orphaned items will be removed.",
                "{}".format(self),
                self.pk,
                new_revision,
                _previous_partial_failures.count(),
            )
            _previous_partial_failures.delete()

        # Create new entries to stand in place of the current ones.  These shadow copies will be
        # the objects that hold the Answers provided by the test homes.
        SampleSetHomeStatus.objects.bulk_create(
            [
                SampleSetHomeStatus(
                    **{
                        "sampleset": self,
                        "home_status": item.home_status,
                        "revision": new_revision,
                        "is_test_home": item.is_test_home,
                        "is_active": True,
                    }
                )
                for item in items_list
            ]
        )

        for item in items_list:
            item.answers.add(*item.find_new_test_answers())
            log.info(
                "Locked %s (Rev: %s) test answers to sampleset entry for %s.",
                num_answers,
                self.revision,
                item.home_status,
            )

        self.revision = new_revision
        self.save()

    def certify(self, user, date, return_report=False, validate_certified=True):
        """
        Calls advance() to guarantee all answers are pushed to sampled homes, and then asks the
        system to process any uncertified homes.
        """
        report = {
            "debug": [],
            "info": [],
            "warning": [],
            "error": [],
        }
        if not self.can_be_advanced():
            msg = strings.ADVANCE_NOT_AVAILABLE
            report["error"].append(msg.format(sampleset=self))
            if return_report:
                return report
            else:
                raise Exception(report["error"][0])
        if validate_certified and not self.can_be_certified():
            msg = strings.CERTIFICATION_NOT_AVAILABLE
            report["error"].append(msg.format(sampleset=self))
            if return_report:
                return report
            else:
                raise Exception(report["error"][0])

        self.advance()

        for item in self.samplesethomestatus_set.current().select_related("home_status__home"):
            self._certify_item(user, item, date, report)

        self.confirm_date = date

        if return_report:
            return report
        if report["error"]:
            raise Exception("\n".join(report["error"]))
        return True

    def _certify_item(self, user, item, date, report):
        """Broken-out work required to certify a single item in the sampleset."""
        # This exists on the sampleset model instead of the samplesethomestatus model because I
        # don't think it's wise to allow an individual item to know how to certify itself out of
        # context.

        # NOTE: This should be something that the home app provides, but the logic is all tied up
        # in two different places.  Adding a third would be spiteful.  The goal would be to be able
        # to run this function in a loop on all items, but instead the home task certifies the first
        # home one way, and then asks the sampleset to do all the rest in this other way.

        # NOTE: ``report`` will be modified in-place.
        report["error"] += certify_single_home(user, item.home_status, date, bypass_check=True)

    def is_full(self, revision=None):
        """
        Returns True if the sampleset is full for the given revision.  If no revision is given, the
        sampleset's own revision will be used.
        """
        if revision is None:
            revision = self.revision
        existing = self.samplesethomestatus_set.filter(revision=revision)
        return existing.count() >= settings.SAMPLING_MAX_SIZE

    def is_compatible(self, return_report=False, **kwargs):
        """
        Receives values for settings that should be compared to the sampleset's existing settings.
        If a setting is not provided, it will not be inspected at all, allowing for inspections of
        targetted values.

        Currently valid kwargs are ``subdivision`` and ``builder_org``.

        If the ``return_report`` flag is False, a simple boolean will be returned.
        If the flag is instead True, a 2-tuple is returned with the boolean result and the
        dictionary of findings.  This dictionary will have keys that match the input kwargs, and
        values that are sub-dicts of the analysis, a key for the 'is_compatible' check for that
        field, and a key for the sampleset's existing value that was used for comparison.

        Example return value when return_report is True:

            (False, {
                'subdivision': {
                    'is_compatible': True,
                    'value': good_subdivision,
                },
                'builder_org': {
                    'is_compatible': False,
                    'value': bad_builder_org,
                }
            })

        """

        checks = ["subdivision", "builder_org"]

        excess_checks = set(kwargs.keys()) - set(checks)
        if excess_checks:
            raise ValueError(
                "Unsupported compatibily checks requested: {}".format(str(excess_checks))
            )

        compatibility = {}
        for check in checks:
            callback = getattr(self, "is_compatible_{}".format(check))
            result = callback(kwargs[check], return_report=return_report)
            if return_report:
                # Turn the 2-tuple compatibilty value into a dict
                result = dict(zip(["is_compatible", "value"], result))
            compatibility[check] = result

        is_compatible = all(list(compatibility.values()))
        if return_report:
            return is_compatible, compatibility
        return is_compatible

    def is_compatible_subdivision(self, subdivision, return_report=False):
        """
        Returns a boolean for a valid subdivision, or, if return_report is True, a 2-tuple where
        the second value is the sampleset's own subdivision used in the check.
        """
        value = self.discover_subdivision()
        if value:
            # One subdivision, we can read the setting directly
            is_metro_sampled = value.use_metro_sampling
        else:
            # Multiple subdivisions, or none at all -- stay flexible
            is_metro_sampled = True

        log.debug(
            "Subdivision {} "
            "Metro Sampled: {} "
            "Discovered Subdivision: {}".format(subdivision, is_metro_sampled, value)
        )

        if value is None:
            # Nothing in sampleset, automatically allowed
            is_compatible = True
        elif value:
            if is_metro_sampled:
                if subdivision == value:
                    # Allows metro sampling, but not required for this subdivision to work
                    is_compatible = True
                else:
                    # Allows metro sampling, and using it
                    is_compatible = subdivision.metro == value.metro if subdivision else False
            else:
                # Not allowing metro sampling, subdivisions must match
                is_compatible = subdivision == value
        else:
            if is_metro_sampled:
                # Multiple subdivisions are in use, verify they are matching metros
                sampleset_metros = self.get_used_metros()
                is_compatible = (
                    {subdivision.metro} == set(sampleset_metros) if subdivision else False
                )
                value = sampleset_metros
            else:
                # Multiple subdivisions are in use, but metro sampling is not allowed, so automatic
                # failure to compatibility.
                is_compatible = False
                value = subdivision
        if return_report:
            return is_compatible, value
        return is_compatible

    def is_compatible_builder_org(self, builder_org, return_report=False):
        """
        Returns a boolean for a valid builder_org, or, if return_report is True, a 2-tuple where
        the second value is the sampleset's own builder_org used in the check.
        """
        this_builder_org = self.discover_builder_org()
        if this_builder_org is None:
            is_compatible = True
        elif this_builder_org:
            is_compatible = builder_org == this_builder_org
        else:
            is_compatible = False
        if return_report:
            return is_compatible, this_builder_org
        return is_compatible

    def add_home_status(self, home_status, **kwargs):
        """
        Attempts to put the EEPProgramHomeStatus object into the sampleset for the target revision.
        Any ``**kwargs`` given will be sent as values for the new SampleSetHomeStatus instance.
        """

        # Defaults for a successful no-args call
        kwargs.setdefault("is_test_home", False)
        kwargs.setdefault("revision", self.revision)

        # Not influenced by kwargs sent into method
        kwargs["is_active"] = kwargs["revision"] == self.revision

        kwargs["home_status"] = home_status
        existing = self.samplesethomestatus_set.filter(
            home_status=home_status, revision=kwargs["revision"]
        )
        if existing:
            item = existing[0]
            if item.is_test_home != kwargs["is_test_home"]:
                raise ValueError(
                    "Home is already in this sampleset with " "a different value for is_test_home"
                )
            return item

        # Constraints check
        if self.is_full(kwargs["revision"]):
            msg = strings.SAMPLESET_FULL
            raise Exception(msg.format(max_size=settings.SAMPLING_MAX_SIZE))

        return self.samplesethomestatus_set.create(**kwargs)

    def get_completion_percentage(self):
        """
        Return an aggregated percentage completion of the question/answer requirements in this
        sampleset.
        """
        from axis.home.models import EEPProgramHomeStatus
        from axis.checklist.models import Question

        # Find the question ids involved by the test homes (with multi-program support)
        homestatuses = EEPProgramHomeStatus.objects.filter(
            sampleset=self, samplesethomestatus__is_test_home=True
        ).select_related("eep_program")
        question_ids = set()
        programs = set()
        for homestatus in homestatuses:
            if homestatus.eep_program in programs:
                continue
            programs.add(homestatus.eep_program)
            program_questions = Question.objects.filter_by_home_status(homestatus)
            question_ids |= set(program_questions.values_list("id", flat=True))
        if programs and not question_ids:
            log.warning("No questions are provided by the programs in use: %r", programs)
            return 0

        # Find all answers that have ever been given to the sampleset, even by past test homes.
        answered_questions = set(self.get_test_answers().values_list("question__id", flat=True))
        try:
            return 100.0 * len(answered_questions) / len(question_ids)
        except ZeroDivisionError:
            return 0

    # Dynamic lookups about current items
    def discover_builder_org(self):
        """Returns the discovered builder for homes in the sampleset, or False if ambiguous."""
        return utils.discover_builder_org_for_homes(self.samplesethomestatus_set.all())

    def discover_subdivision(self):
        """
        Returns the discovered subdivision for homes in the sampleset, or False if ambiguous.
        """
        return utils.discover_subdivision_for_homes(self.samplesethomestatus_set.all())

    def discover_eep_program(self):
        return utils.discover_eep_program_for_homes(self.samplesethomestatus_set.current())

    def discover_is_metro_sampled(self):
        return utils.discover_is_metro_sampled(self.samplesethomestatus_set.current())

    def get_used_metros(self, **kwargs):
        """Getters for all used values (mostly used when discover() methods are returning False)"""
        return utils.get_used_metros(self.samplesethomestatus_set.current(), **kwargs)

    def get_current_source_answers(self):
        """
        Returns a queryset of current Answers
        being provided by the sampleset to sampled homes.
        """
        return self.samplesethomestatus_set.get_current_source_answers()

    def get_current_source_failing_answers(self, combined=False):
        """
        Returns a queryset of current
        failing Answers being provided by the sampleset to
        sampled homes.
        """
        if not combined:
            return self.get_current_source_answers().filter(is_considered_failure=True)

        data = {}
        for failure in self.get_current_source_answers().filter(is_considered_failure=True):
            if failure.question.id not in data:
                data[failure.question_id] = {
                    "question": failure.question,
                    "failure_count": 0,
                    "passing_count": 0,
                    "homes": [],
                    "corrected": False,
                }
            data[failure.question_id]["failure_count"] += 1
            if failure.failure_is_reviewed:
                data[failure.question_id]["passing_count"] += 1
            data[failure.question_id]["homes"].append(
                "<a href='{}'>{}</a><br />".format(
                    failure.home.get_absolute_url(), failure.home.get_addr()
                )
            )

        for item in data.values():
            item["homes"] = "<br />".join(item["homes"])
            item["corrected"] = item["passing_count"] >= item["failure_count"]

        return list(data.values())

    def get_previous_contributed_answers(self):
        """
        Returns all answers contributed to all sampleset items.  This provides information about
        questions that have been covered by past test homes no longer in the sampleset.
        """
        from axis.checklist.models import Answer

        return Answer.objects.filter(samplesethomestatus__sampleset=self).distinct()

    def get_test_answers(self):
        """
        Returns source answers and all past contributed answers, which together describe all test
        questions that have been in play on this sampleset, even if the contributing test home is no
        longer in the sampleset.
        """
        from axis.checklist.models import Answer

        current = set(self.get_current_source_answers().values_list("id", flat=True))
        previous = set(self.get_previous_contributed_answers().values_list("id", flat=True))
        return Answer.objects.filter(id__in=(current | previous))


class SampleSetHomeStatus(models.Model):
    """
    Tracks participation data about a homestatus in a sampleset.

    Answers provided by test homes in the sampleset will be "published" to the sampled homes via
    the ``answers`` m2m on this model.

    If the homestatus is tracked over multiple inspection phases, then a homestatus will get
    multiple instances of this model specific to each phase.  If a homestatus is removed from the
    sampleset, only the SampleSetHomeStatus matching the current inspection phase is deleted.
    Associations from past inspection phases will persist, holding answers the home gained from
    the sampleset back when it was associated with it under a different phase.
    """

    objects = SampleSetHomeStatusManager()

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    sampleset = models.ForeignKey("SampleSet", on_delete=models.CASCADE)
    home_status = models.ForeignKey("home.EEPProgramHomeStatus", on_delete=models.CASCADE)
    revision = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)
    is_test_home = models.BooleanField(
        default=False,
        help_text="""Indicates whether this home is
                                       providing answers or receiving them.""",
    )

    answers = models.ManyToManyField("checklist.Answer", blank=True)

    class Meta:
        unique_together = [("sampleset", "home_status", "revision")]
        verbose_name = "Sample Set Home Status"
        verbose_name_plural = "Sample Set Home Statuses"

    def __str__(self):
        active_label = "ACTIVE " if self.is_active else ""
        test_home_label = "Test" if self.is_test_home else "Sampled"

        desc = "{}{} homestatus [revision={}]".format(
            active_label,
            test_home_label,
            self.revision,
        )
        if self.is_test_home:
            desc += " ({} source answers)".format(self.home_status.home.answer_set.count())
        else:
            desc += " ({} received in revision={}, {} covered since revision=0)".format(
                self.answers.count(), self.revision, self.find_answered_questions().count()
            )
        return desc

    def get_questions(self):
        """
        Returns a queryset of the Questions being
        provided by the sampleset to sampled homes.
        """
        return self.home_status.get_all_questions()

    def get_source_answers(self, include_failures=True):
        """
        Returns answers that originated from
        this home as a Test home and can be shared.
        """
        return utils.get_homestatus_test_answers(
            [self.home_status], include_failures=include_failures
        ).distinct()

    def get_contributed_answers(self):
        """
        Returns all answers objects that have
        ever been shared to this home from any sampleset.
        """
        from axis.checklist.models import Answer

        return (
            Answer.objects.filter(samplesethomestatus__home_status=self.home_status)
            .get_passing_and_corrected()
            .distinct()
        )

    def get_failing_answers(self):
        """Returns answers which are considered uncorrected failures."""
        # Failures cannot be pushed to homes as contributed answers, so this is a Test Home
        # operation for source answers only.
        return self.get_source_answers(include_failures=True).get_uncorrected_failures()

    def find_existing_answers(self):
        """
        Returns an Answers queryset of all answers that are already given for this item, either by
        checklist/bulk, or by prior sampleset associations.
        """
        from axis.checklist.models import Answer

        source_answers = set(self.get_source_answers().values_list("id", flat=True))
        contributed_answers = set(self.get_contributed_answers().values_list("id", flat=True))
        return Answer.objects.filter(id__in=(source_answers | contributed_answers))

    def find_new_test_answers(self):
        """
        Returns an Answers queryset of current test answers minus what is already covered by this
        sampleset item.
        """
        answers = self.sampleset.get_current_source_answers()
        answer_ids = list(self.find_existing_answers().values_list("id", flat=True))

        # This use of distinct is to remain consistent with the other answer queryset getters on
        # this model, so that they can be combined without errors about mixing distinct and
        # non-distinct.
        return answers.exclude(id__in=answer_ids).distinct()

    def find_answered_questions(self):
        """
        Returns a Questions queryset for questions that have answers associated with them.
        """
        answer_ids = list(self.find_existing_answers().values_list("id", flat=True))
        return self.get_questions().filter(answer__id__in=answer_ids)

    def find_unanswered_questions(self):
        """
        Returns a Questions queryset for questions that have no answers associated with them.
        """
        # NOTE: This does not consider questions that WILL BE answered if the sampleset is put
        # through the required advance(), which would collect answers being offered by test homes.
        # For a look at completely uncovered questions, use find_uncovered_questions()
        answer_ids = list(self.find_existing_answers().values_list("id", flat=True))
        return self.get_questions().exclude(answer__id__in=answer_ids)

    def find_uncovered_questions(self, include_optional=False):
        """
        Returns a Questions queryset for questions that have no answers, but are also uncovered by
        answers tentatively offered by the test homes if advance() were to be called.
        """
        # NOTE: This is like peeking at what the question coverage would be if the sampleset were
        # put through the required advance().
        v1 = set(self.find_existing_answers().values_list("id", flat=True))
        v2 = set(self.find_new_test_answers().values_list("id", flat=True))
        queryset = self.get_questions()
        if not include_optional:
            queryset = queryset.filter(is_optional=False)
        return queryset.exclude(answer__id__in=(v1 | v2))


class SamplingProviderApproval(models.Model):
    provider = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="sampling_approver"
    )
    target = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="sampling_approved")
    sampling_approved = models.BooleanField("Approved", default=False)

    created_date = models.DateTimeField(auto_now_add=True)

    objects = SamplingProviderApprovalManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Provider Sampling Approvals"
