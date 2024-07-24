"""eep_program_home_status.py: """

__author__ = "Artem Hruzd"
__date__ = "06/26/2019 18:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import hashlib
import inspect
import logging
import sys
from collections import namedtuple

from django.apps import apps
from django.contrib.sites.shortcuts import get_current_site
from hashid_field import Hashid
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, F
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from axis.gbr.models import GbrStatus
from django_input_collection.models.utils import clone_collection_request
from django_states.models import StateModel
from simulation.enumerations import (
    FuelType,
    SourceType,
    AnalysisType,
)

from axis.certification.models import WorkflowStatusHomeStatusCompatMixin
from axis.certification.utils import (
    PassingStatusTuple,
    FailingStatusTuple,
    WarningStatusTuple,
    requirement_test,
)
from axis.checklist.models import Answer, Question
from axis.customer_aps.strings import APS_PROGRAM_SLUGS
from axis.customer_neea.utils import NEEA_BPA_SLUGS
from axis.hes.apps import HESConfig
from axis.home import strings
from axis.home.managers import (
    EEPProgramHomeStatusManager,
    EEPProgramHomeStatusHistoricalRecords,
)
from axis.home.state_machine import HomeStatusStateMachine
from axis.home.strings import (
    ERI_SCORE_TOO_HIGH,
    ERI_SCORE_TOO_LOW,
    MISSING_ERI_SCORE,
    MISSING_SIMULATION_DATA,
    MISSING_EKOTROPE_DATA,
    MISSING_REMRATE_DATA,
    MISSING_REMRATE_FILE,
)
from axis.home.utils import flatten_inheritable_settings
from axis.relationship.models import Relationship, Associations
from axis.relationship.utils import get_mutual_company_ids_including_self

User = get_user_model()
log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")

# Add legacy values that have been annoying to query when the punogram slug
# is the switch for correct measure names.
MEASURE_ALIASES = {
    "equipment-heat-pump-water-heater-serial-number": [
        "heat-pump-water-heater-serial-number",
    ],
    "primary-heating-equipment-type": [
        "equipment-primary-heating-type",
        "eto-primary_heat_type",
        "eto-primary_heat_type-2016",
    ],
    "showerheads15-quantity": [
        "eto-shower-head-1p5",
    ],
    "showerheads16-quantity": [
        "eto-shower-head-1p6",
    ],
    "showerheads175-quantity": [
        "eto-shower-head-1p75",
    ],
    "showerwands15-quantity": [
        "eto-shower-wand-1p5",
    ],
    # 'smart-thermostat-brand': '',
}


class EEPProgramHomeStatus(StateModel, WorkflowStatusHomeStatusCompatMixin):
    """This is where all the action takes place.  We can get the status
    of a Program to the house level. This is where completed homes get
    confirmed and sent for processing"""

    # state machine states to constants
    PENDING_INSPECTION_STATE = "pending_inspection"
    INSPECTION_STATE = "inspection"
    QA_PENDING_STATE = "qa_pending"
    CERTIFICATION_PENDING_STATE = "certification_pending"
    COMPLETE_STATE = "complete"
    FAILED_STATE = "failed"
    ABANDONED_STATE = "abandoned"

    # Customer HIRL states
    CUSTOMER_HIRL_PENDING_PROJECT_DATA = "customer_hirl_pending_project_data"
    CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE = "customer_hirl_pending_rough_qa"
    CUSTOMER_HIRL_PENDING_FINAL_QA_STATE = "customer_hirl_pending_final_qa"

    CUSTOMER_HIRL_STATE_CHOICES = (
        (CUSTOMER_HIRL_PENDING_PROJECT_DATA, "Pending Project Data"),
        (CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE, "Pending Rough QA"),
        (CUSTOMER_HIRL_PENDING_FINAL_QA_STATE, "Pending Final QA"),
        (CERTIFICATION_PENDING_STATE, "Inspected"),
        (COMPLETE_STATE, "Certified"),
        (FAILED_STATE, "Failed"),
        (ABANDONED_STATE, "Abandoned"),
    )

    STATE_CHOICES = (
        (PENDING_INSPECTION_STATE, "Pending"),
        (INSPECTION_STATE, "Active"),
        (QA_PENDING_STATE, "Pending QA"),
        (CERTIFICATION_PENDING_STATE, "Inspected"),
        (COMPLETE_STATE, "Certified"),
        (FAILED_STATE, "Failed"),
        (ABANDONED_STATE, "Abandoned"),
    )

    eep_program = models.ForeignKey(
        "eep_program.EEPProgram",
        on_delete=models.CASCADE,
        verbose_name="Program",
        related_name="homestatuses",
        help_text=strings.EEP_PROGRAM_HOME_STATUS_FORM_EEP_PROGRAM,
    )
    home = models.ForeignKey("Home", on_delete=models.CASCADE, related_name="homestatuses")

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    rater_of_record = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    energy_modeler = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="energy_modeler_epp_program_home_status_set",
    )
    field_inspectors = models.ManyToManyField(
        User, blank=True, related_name="field_inspector_epp_program_home_status_set"
    )

    # customer HIRL specific fields
    customer_hirl_rough_verifier = models.ForeignKey(
        User,
        verbose_name="Rough Verifier",
        related_name="rough_verifier_epp_program_home_statuses",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    customer_hirl_final_verifier = models.ForeignKey(
        User,
        verbose_name="Final Verifier",
        related_name="final_verifier_epp_program_home_statuses",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    floorplan = models.ForeignKey(
        "floorplan.Floorplan",
        on_delete=models.CASCADE,
        verbose_name="Active REM/Rate™ data",
        blank=True,
        null=True,
        related_name="active_for_homestatuses",
    )

    floorplans = models.ManyToManyField(
        "floorplan.Floorplan", blank=True, related_name="homestatuses"
    )

    certification_date = models.DateField(blank=True, null=True)

    # Accounting
    pct_complete = models.FloatField(default=0.0)
    is_billable = models.BooleanField(default=False)

    collection_request = models.OneToOneField(
        "django_input_collection.CollectionRequest",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    annotations = GenericRelation("annotation.Annotation")

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    objects = EEPProgramHomeStatusManager()
    history = EEPProgramHomeStatusHistoricalRecords()
    associations = Associations(related_name="homestatuses")
    Machine = HomeStatusStateMachine

    class Meta:
        """Non-Field options"""

        unique_together = (("home", "eep_program"),)
        verbose_name = "Project Status"
        verbose_name_plural = "Project Statuses"

    def __str__(self):
        try:
            floorplan = self.floorplan
        except (ObjectDoesNotExist, AttributeError):
            floorplan = None

        addr = builder = program = "-"
        try:
            addr = self.home.get_home_address_display()
            builder = self.home.get_builder()
        except ObjectDoesNotExist:
            pass

        try:
            program = "{}".format(self.eep_program)
        except ObjectDoesNotExist:
            pass

        return f"{addr} ({builder}) {f'[{floorplan}]' if floorplan else ''} - {program}"

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return reverse("home:view", kwargs={"pk": self.home.id})

    def save(self, *args, **kwargs):
        should_update_stats = kwargs.pop("update_stats", False)
        super(EEPProgramHomeStatus, self).save(*args, **kwargs)

        if should_update_stats:
            self.update_stats()

    @classmethod
    def can_be_added(cls, user):
        # This is probably a little open-ended, but doing this is only possible if they can edit
        # a given home.
        return True

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        # do not allow edit home for customer HIRL programs
        # they must use HIRL Registration page for correct sync
        if (
            self.eep_program.slug
            in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            + customer_hirl_app.HIRL_PROJECT_LEGACY_EEP_PROGRAM_SLUGS
        ):
            if user.is_customer_hirl_company_member():
                return True
            return False

        if user.company.id != self.company.id:
            return False

        is_aps_internal = self.eep_program.owner.slug == user.company.slug == "aps"

        # Allow APS leeway in removing programs that may have been added by mistake.
        if is_aps_internal and self.state in (
            "pending_inspection",
            "inspection",
            "certification_pending",
        ):
            return True

        perms = user.has_perm("checklist.change_answer") or user.has_perm("home.change_home")
        if not perms:
            return False
        if self.eep_program.owner.is_customer and self.certification_date:
            sampleset_membership = self.get_samplesethomestatus()
            if sampleset_membership and sampleset_membership.is_test_home:
                finished_siblings = (
                    sampleset_membership.sampleset.samplesethomestatus_set.current().filter(
                        home_status__incentivepaymentstatus__state__in=[
                            "payment_pending",
                            "complete",
                        ]
                    )
                )
                if finished_siblings.count():
                    return False
                return True
            else:
                try:
                    if self.incentivepaymentstatus.state not in [
                        "start",
                        "ipp_payment_failed_requirements",
                    ]:
                        return False
                except ObjectDoesNotExist:
                    return False

        # APS can ignore locked state mechanics, since their locks come from the incentive state.
        if is_aps_internal:
            return True

        locked_states = ["complete"]
        if self.eep_program.owner.slug == "eto":
            locked_states.append("certification_pending")

        return self.state not in locked_states

    def can_be_deleted(self, user):
        if (
            self.eep_program.slug
            in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            + customer_hirl_app.HIRL_PROJECT_LEGACY_EEP_PROGRAM_SLUGS
        ):
            return False
        if user.is_superuser:
            return True
        # Prevent deletion of old program from homes that have a QA
        return self.can_be_edited(user) and not self.qastatus_set.count()

    def get_state_display(self):
        return self.get_state_info().description

    def get_rating_type(self):
        """Legacy sampling helper."""
        if not hasattr(self, "eep_program"):
            return None
        if not self.eep_program.allow_sampling:
            return None
        total_memberships = self.samplesethomestatus_set.count()
        if total_memberships > 0:
            test_home = bool(self.samplesethomestatus_set.filter(is_test_home=True).count())
            if test_home:
                return "Sampled Test House"
            return "Sampled House"
        if self.eep_program is None or self.eep_program.slug in [
            "wa-code-study",
            "washington-code-credit",
        ]:
            return None
        return "Confirmed Rating"

    def get_certification_link(self, user_id_hash, current_site):
        hash_id = Hashid(self.id, salt=f"certificate{settings.HASHID_FIELD_SALT}")
        certificate_hash_id = hash_id.hashid
        hash_id = Hashid(
            user_id_hash,
            salt=f"user{settings.HASHID_FIELD_SALT}",
        )
        user_id = hash_id.hashid
        certification_link = reverse_lazy(
            "api_v3:home_status-certificate",
            args=(
                certificate_hash_id,
                user_id,
            ),
        )
        if "localhost" in current_site.domain:
            full_url = f"{current_site.domain}:8000{certification_link}"
        else:
            full_url = f"{current_site.domain}{certification_link}"
        return full_url

    def set_collection_from_program(self):
        """Internal utility for assigning the program checklist template to the homestatus."""
        if self.collection_request:
            raise ValueError("Homestatus pk=%r already has a collection request." % (self.pk,))
        collection_request = self.eep_program.collection_request
        cloned = clone_collection_request(collection_request)
        self.collection_request = cloned
        self.collection_request_id = cloned.id
        self.save()

    def get_collector(self, cls=None, **context):
        if self.collection_request is None:
            raise ValueError("No collection request set for homestatus.")
        if cls is None:
            from axis.checklist.collection.collectors import ChecklistCollector

            cls = ChecklistCollector
        return cls(self.collection_request, **context)

    def get_input_values(self, **context):
        if not self.collection_request:
            return dict(self.get_answers_for_home().values_list("question__slug", "answer"))

        collector = self.get_collector(**context)
        breakdown = (
            collector.get_inputs(cooperative_requests=True)
            .order_by("date_created")
            .get_breakdown("instrument__measure_id", last=True)
        )
        input_values = {
            measure: collected_input.data.get("input") if collected_input else None
            for measure, collected_input in breakdown.items()
        }

        def firstof(items):
            items = list(filter(bool, items))
            return items[0] if items else None

        input_values.update(
            {
                measure_id: firstof(map(input_values.get, [measure_id] + aliases))
                for measure_id, aliases in MEASURE_ALIASES.items()
            }
        )

        return input_values

    def full_transition(self, state, user, **kwargs):
        self.make_transition(state, user, **kwargs)

        if self.state != "complete":
            from ..tasks import update_home_states

            update_home_states(eepprogramhomestatus_id=self.id, user_id=user.id)

    def get_builder_incentive(self):
        """Get the real builder incentive"""
        if self.eep_program.owner.slug == "aps":
            from axis.customer_aps.incentives import get_builder_incentive

            return get_builder_incentive(self)
        elif self.eep_program.slug in NEEA_BPA_SLUGS:
            from axis.customer_neea.incentives import get_builder_incentive

            return get_builder_incentive(self)
        return self.eep_program.builder_incentive_dollar_value

    def get_rater_incentive(self):
        """Get the rater incentive"""
        if self.eep_program.owner.slug == "aps":
            from axis.customer_aps.incentives import get_rater_incentive

            return get_rater_incentive(self)
        elif self.eep_program.slug in NEEA_BPA_SLUGS:
            from axis.customer_neea.incentives import get_rater_incentive

            return get_rater_incentive(self)
        return self.eep_program.rater_incentive_dollar_value

    def get_total_incentive(self):
        """Get the total incentive"""
        if self.eep_program.owner.slug == "aps":
            from axis.customer_aps.incentives import get_total_incentive

            return get_total_incentive(self)
        elif self.eep_program.slug in NEEA_BPA_SLUGS:
            from axis.customer_neea.incentives import get_total_incentive

            return get_total_incentive(self)
        return self.get_rater_incentive() + self.get_builder_incentive()

    def is_missing_hes_score_annotations(self) -> bool:
        """Returns true if this EEPProgramHomeStatus is missing any annotations required for Home Energy Score"""
        annotation_slugs = [HESConfig.ORIENTATION_ANNOTATION_SLUG]
        if self.eep_program.slug in [
            "eto-2019",
            "eto-2020",
            "eto-2021",
            "eto-fire-2021",
            "eto-2022",
        ]:
            annotation_slugs.append("hpxml_gbr_id")
        count_annotations = self.annotations.filter(type__slug__in=annotation_slugs).count()
        return count_annotations != len(annotation_slugs)

    def has_orientation(self) -> bool:
        return self.annotations.filter(type__slug=HESConfig.ORIENTATION_ANNOTATION_SLUG).exists()

    def update_stats(self, audit=False, raise_exception=False, brief_audit=True):  # noqa: C901
        """Core function to update the stats of an Program attached to a home
        :param audit: Only audit it and if differences are found report them.
        :param raise_exception: Raise an exception if errors are found
        """
        if settings.DEBUG:
            try:
                frm = inspect.stack()[1]
                mod = inspect.getmodule(frm[0])
                log.debug("Updating Stats - Called from {}".format(mod.__name__))
            except AttributeError:
                pass

        from axis.checklist.models import Answer

        kwargs = dict(
            home=self.home,
            company=self.company,
            eep_program=self.eep_program,
            ignore_phase=True,
            include_unphased=True,
            skip_certified=audit,
        )
        all_questions = self.get_all_questions()
        kwargs.update(dict(questions=all_questions))
        sampleset_membership = self.get_samplesethomestatus()
        if sampleset_membership and not sampleset_membership.is_test_home:
            log.info("This is a sampled home")
            # log.debug("Questions: {}".format(len(questions)))
        all_unanswered_questions = self.get_unanswered_questions()

        # When dealing with pct complete we only care about non_optionals
        non_optional_questions = [q for q in all_questions if not q.is_optional]
        non_optional_unanswered = [q for q in all_unanswered_questions if not q.is_optional]
        non_optional_answered_questions = len(non_optional_questions) - len(non_optional_unanswered)

        if self.certification_date and audit is False:
            return
        try:
            pct_complete = (
                non_optional_answered_questions / float(len(non_optional_questions)) * 100
            )
            # Many acceptable passing answers
            if pct_complete > 100:
                pct_complete = 100
        except ZeroDivisionError:
            pct_complete = 0.0
            if len(
                non_optional_questions
            ):  # Is this even possible if it was a zero division error?
                pct_complete = 100
        if not len(non_optional_questions):
            pct_complete = 100.0
        if self.certification_date and 0 < pct_complete < 99.99:
            warn = (
                "{} Questions remain yet this home {} {} [{}] has been certified "
                "{}paid.".format(
                    len(non_optional_questions) - non_optional_answered_questions,
                    self,
                    self.company,
                    self.id,
                    "" if self.ippitem_set.count() else "un",
                )
            )
            log.warning(warn)

        if audit:
            # if self.sampleset is None:
            #     try:
            #         from axis.sampling.models import SampleSet
            #         hist = self.history.filter(sampleset__isnull=False)[0]
            #         ss = SampleSet.objects.get(id=hist.sampleset)
            #         print("Historical Rating Type: {} ({}) {}%".format(hist.rating_type, ss,
            #                                                                hist.pct_complete))
            #     except IndexError:
            #         pass
            eeps = list(set(self.history.values_list("eep_program", flat=True)))
            if len(eeps) > 1:
                log.info("Historical Program: {} vs {}".format(eeps[0], eeps[1]))
            opts = len(all_questions) - len(non_optional_questions)
            opts_comment = " ({} Optional)".format(opts) if opts else ""
            if pct_complete != self.pct_complete:
                log.info(
                    "Pct Complete: {}/{}{} {:.2f}% vs {:.2f}%".format(
                        non_optional_answered_questions,
                        len(non_optional_questions),
                        opts_comment,
                        pct_complete,
                        self.pct_complete,
                    )
                )
            else:
                log.info(
                    "Pct Complete: {}/{}{} {:.2f}%".format(
                        non_optional_answered_questions,
                        len(non_optional_questions),
                        opts_comment,
                        pct_complete,
                    )
                )

            if self.certification_date:
                log.info("Certified: {}".format(self.certification_date))
            if self.ippitem_set.count():
                ipp = self.ippitem_set.all()[0].incentive_distribution
                if ipp.paid_date:
                    log.info("Paid: {}".format(ipp.paid_date))
                else:
                    log.info("Check Requested: {}".format(ipp.check_requested_date))
            else:
                log.info("No payment status.")

            if (
                raise_exception
                and round(float(self.pct_complete), 0) != round(float(pct_complete), 0)
                and self.pct_complete > pct_complete
                and self.pct_complete > 99.9
                and self.certification_date
            ):
                raise ValueError("Home Stat differs")

            if brief_audit:
                return

            log.info("---{}---".format(self.id))
            answers = Answer.objects.filter_by_home_status(self)
            all_answers = list(
                answers.values(
                    "id",
                    "question",
                    "system_no",
                    "failure_is_reviewed",
                    "is_considered_failure",
                    "home",
                )
            )
            log.info(
                "idx {:<5} {:<20} {} {:<20} {:<20} {:<20}".format(
                    "Q.id", "Question", "O", "Answer.id's", "Answer.homes", "A.fails"
                )
            )
            log.info("=" * 80)
            for idx, question in enumerate(all_questions):
                q_id = question.id

                q = question.question
                if len(q) >= 20:
                    q = q[0:16] + "..."
                o = "*" if question.is_optional else " "
                qanswers = [x for x in all_answers if x["question"] == q_id]
                a = ", ".join([str(x["id"]) for x in qanswers])
                h = ", ".join([str(x["home"]) for x in qanswers])
                fail = "*" * len([x for x in qanswers if x["is_considered_failure"]])
                log.info(
                    "{:<3} {:<5} {:<20} {} {:<20} {:<20} {:<20}".format(
                        idx + 1, q_id, q, o, a, h, fail
                    )
                )
            return

        self.pct_complete = pct_complete
        self.save()

    def is_eligible_for_certification(self, skip_certification_check=False):
        """Returns a single boolean for the result of ``get_progress_analysis()``"""
        data = self.get_progress_analysis(
            skip_certification_check=skip_certification_check, fail_fast=True
        )
        return data["status"]

    def report_eligibility_for_certification(self, skip_certification_check=False):
        data = self.get_progress_analysis(
            skip_certification_check=skip_certification_check, fail_fast=False
        )
        return [req["message"] for req in data["requirements"].values() if req["status"] is False]

    def can_be_decertified(self, user, report=False):
        result = self.decertify(user, check_only=True, report=report)
        if report:
            return result[0]
        return result

    def decertify(self, user, check_only=True, report=True, force=False):  # noqa: C901
        """Expierimental - Removes certification from a program"""

        _report, _warnings = [], []

        # Checks
        if self.state != "complete" or self.certification_date is None:
            _warnings.append("This program is not yet certified.")

        if self.ippitem_set.all().count():
            _warnings.append("Incentives may exist as IPP items are on this.")

        # # If the owner is a rater and user is a provider friend
        if self.company.company_type == "rater" and self.eep_program.owner_id != user.company.id:
            providers = self.company.relationships.get_companies().filter(company_type="provider")
            if user.company not in providers and not user.is_superuser:
                _warnings.append("Only Certification Organizations allowed to decertify this")

        if self.eep_program.slug in customer_hirl_app.NGBS_PROGRAM_NAMES.values():
            _warnings.append("Imported programs cannot be decertified")

        if check_only:
            if report:
                return False if len(_warnings) else True, _warnings
            return False if len(_warnings) else True

        if len(_warnings):
            if not force:
                msg = "Decertify %s on %s failed: %s"
                log.warning(msg, self.eep_program, self.home, ", ".join(_warnings))
                msg = msg % (self.eep_program, self.home, ", ".join(_warnings))
                return msg if report else False
            else:
                log.warning(
                    "Decertify %s on %s forcing with issues: %s",
                    self.eep_program,
                    self.home,
                    ", ".join(_warnings),
                )

        save_required = False
        if self.certification_date:
            self.certification_date = None
            save_required = True
            _report.append("removed certification date")
        if self.state != "inspection":
            self.state = "inspection"
            save_required = True
            _report.append("reset state to active")
        try:
            self.incentivepaymentstatus.delete()
            _report.append("removed incentive status")
        except Exception:
            pass

        qa_statuses = self.qastatus_set.select_related("requirement")
        if len(qa_statuses):
            for qa_status in qa_statuses:
                qa_status.state = "received"
                qa_status.result = None
                qa_status.save()
                _report.append(
                    "{type} QA rolled back".format(type=qa_status.requirement.get_type_display())
                )

        try:
            ft = self.fasttracksubmission
            keep = ["id", "home_status", "project_id"]
            for fld in [f.name for f in ft._meta.fields if f.name not in keep]:
                setattr(ft, fld, None)
            ft.save()
            _report.append("ETO Project Tracker data cleared")
        except Exception:
            pass

        rollup = self.analytical_rollup
        if rollup is not None and rollup.status != "READY":
            rollup.status = "READY"
            rollup.save()
            self.validate_references()

        questions = self.eep_program.get_checklist_question_set()
        answers = Answer.objects.filter(home=self.home, question__in=questions)
        answers.update(confirmed=False)
        if answers.count():
            _report.append("unlocked {} answers".format(answers.count()))

        #
        from axis.filehandling.models import CustomerDocument

        public_docs = CustomerDocument.objects.filter(
            document__icontains="eps",
            content_type=ContentType.objects.get_for_model(self.home),
            object_id=self.home.pk,
            login_required=False,
        ).update(login_required=True, is_public=False)
        if public_docs:
            _report.append("Public EPS Documents reset")

        # GBR:
        from axis.gbr.models import GreenBuildingRegistry

        gbr = GreenBuildingRegistry.objects.filter(home=self.home).update(
            status=GbrStatus.NOT_STARTED
        )
        if gbr:
            _report.append("Green Building Registry reset")

        if len(_report) > 1:
            _report[-1] = "and {}.".format(_report[-1])
        if _report:
            _report[0] = _report[0].capitalize()
        _report = _report if len(_report) else ["Nothing needed to be done."]

        _report = "Decertified {} on {}; {}".format(self.eep_program, self.home, ", ".join(_report))

        if len(_warnings):
            _report += " Warnings: {}".format(", ".join(_warnings))

        if save_required:
            self.save()
        log.info(_report)
        return _report if report else True

    def reassign_user(self, user, include_samplesets=True):
        """
        Method will rassign the home_status company and all other associated collateral.
        This does not modify the answers as it's assumed the user will answer user is also moving
        """

        from axis.company.models import Company
        from axis.relationship.utils import create_or_update_spanning_relationships

        company = user.company
        former = Company.objects.get(id=self.company.id)

        self.home.relationships.filter(company=company).delete()

        relationship = self.home.relationships.get(company=former)
        relationship.company = company
        relationship.save()

        self.company = company
        try:
            self.save()
        except Exception as err:
            print("Issue with {}: {} - {}".format(self.id, self, err))

        for floorplan in list(self.floorplans.all()) + [self.floorplan]:
            if not floorplan:
                continue
            if floorplan.remrate_target:
                remrate = floorplan.remrate_target
                remrate.company = company
                remrate.save()

            floorplan.owner = company
            floorplan.save()

            floorplan.relationships.filter(company=company).delete()
            try:
                relationship = floorplan.relationships.get(company=former)
            except ObjectDoesNotExist:
                create_or_update_spanning_relationships(company, floorplan)
            else:
                relationship.company = company
                relationship.save()

        if include_samplesets:
            for ss in self.sampleset_set.all().distinct():
                ss.owner = company
                ss.save()

    def is_confirmed_rating(self):
        return self.samplesethomestatus_set.count() == 0

    def is_gating_qa_complete(self):
        """Looks up QA Completeness"""
        from axis.qa.models import QARequirement

        qa_requirements = QARequirement.objects.filter_for_home_status(self)

        if qa_requirements.count():
            log.debug("%s potential QA Requirements for %s", qa_requirements.count(), self)

        complete = True
        for requirement in qa_requirements:
            qastatuses = requirement.qastatus_set.filter(
                Q(home_status=self) | Q(subdivision__home__homestatuses=self)
            )

            if qastatuses:
                gating = qastatuses.filter(requirement__gate_certification=True).exclude(
                    state="complete"
                )
                if gating.exists():
                    log.debug("Gating Requirement for {} not met".format(requirement.qa_company))
                    complete = False
            else:
                # If there isn't a status and it must happen on every home
                if requirement.coverage_pct >= 1 and requirement.gate_certification:
                    log.debug(
                        "Gating 100%% Requirement for {} " "not met".format(requirement.qa_company)
                    )
                    complete = False

        return complete

    def is_allowed_by_projecttracker(self):
        is_eto_program = self.eep_program.slug.startswith("eto")
        is_qa_program = self.eep_program.is_qa_program

        return all(
            (
                is_eto_program,
                not is_qa_program,
                self.is_certified,
            )
        )

    @property
    def is_certified(self) -> bool:
        is_state_complete = self.state == self.COMPLETE_STATE
        has_cert_date = self.certification_date is not None

        # This should presumably never be possible and would indicate an error in the state machine, since it would
        # make no sense for an instance to have a cert date but not have the appropriate state, or to be certified
        # but not have a certification date.
        if is_state_complete != has_cert_date:
            raise Exception(
                f"EEPProgramHomeStatus {self.pk} has state {self.state}, but it has "
                f"{'no' if not has_cert_date else 'a'} certification date."
            )

        return is_state_complete

    def can_be_submitted_to_projecttracker(self):
        if hasattr(self, "fasttracksubmission") and self.fasttracksubmission:
            return self.fasttracksubmission.can_be_sent_to_fastrack()
        return False

    def get_certification_agent(self):
        """
        Returns the company who should possess the ability to certify if/when the homestatus object
        is ready for that step.
        """
        certification_agent = self.company

        has_certifying_agents = self.eep_program.certifiable_by.exists()
        if has_certifying_agents:
            # Determine which agent actually applies to this home, using the home's relationships
            # as context hints.
            candidate_agents = self.eep_program.certifiable_by.filter(
                **{
                    "id__in": self.home.relationships.values_list("company", flat=True),
                }
            )
            certification_agent = candidate_agents.first()

            # If there's more than one, we can't have confidence in which it is without specific
            # exceptions built into this method for certain program slugs, etc.
            if candidate_agents.count() > 1:
                company_info = list(candidate_agents.values("id", "name", "company_type"))
                log.warning(
                    "Ambiguous certification agent for home with relationships to these "
                    "'certifiable_by' companies: %r (Using '%r')",
                    company_info,
                    certification_agent.name,
                )

        return certification_agent

    def can_user_certify(self, user, perform_eligiblity_check=True):
        if perform_eligiblity_check and not self.is_eligible_for_certification():
            return False

        if self.get_sampleset():
            if self.eep_program.require_resnet_sampling_provider:
                if user.is_superuser:
                    return True
                try:
                    approved = user.company.resnet.is_sampling_provider
                    if not approved:
                        return False
                except ObjectDoesNotExist:
                    return False

        if not self.is_gating_qa_complete():
            return False

        if user.is_superuser:
            return True

        # Raters can only certify if it's for their programs and home status.
        if self.eep_program.owner == self.company == user.company:
            return True

        if self.company.id in get_mutual_company_ids_including_self(user.company):
            return self.eep_program.user_can_certify(user)

        log.warning(
            "Unexpected user for can_user_certify: user=%r; homestatus=%r",
            user.id,
            self.id,
        )
        return False

    def _can_user_edit(self, user):
        if user.is_superuser:
            return True
        if user.company.id != self.company.id:
            return False
        perms = user.has_perm("checklist.change_answer") and user.has_perm("home.change_home")
        if not perms:
            return False
        if self.eep_program.owner.is_customer and self.certification_date:
            try:
                if self.incentivepaymentstatus.state in ["payment_pending", "complete"]:
                    return False
            except ObjectDoesNotExist:
                return False
        return True

    def get_simplified_status_for_user(self, user):
        (
            can_view,
            can_edit,
            can_transition_to_certify,
        ) = (
            False,
            False,
            False,
        )
        can_certify, completed, has_checklist = False, False, False

        _is_eligible = self.is_eligible_for_certification()

        if self.state == "complete":
            completed = True
        elif _is_eligible and self.can_user_certify(user, perform_eligiblity_check=False):
            if (
                self.eep_program.manual_transition_on_certify
                and self.state != "certification_pending"
            ):
                can_certify = False
            else:
                can_certify = True
        if self.can_be_edited(user):
            can_edit = True
            if (
                _is_eligible
                and self.state == "inspection"
                and self.eep_program.manual_transition_on_certify
            ):
                if (
                    self.eep_program.program_submit_date
                    and self.eep_program.program_submit_date < now().date()
                ):
                    log.debug(
                        "Unable to transition to certify - submit date %s < %s today",
                        self.eep_program.program_submit_date,
                        now().date(),
                    )
                    can_transition_to_certify = False
                else:
                    can_transition_to_certify = True

        if self.state != "abandoned" and self.company == user.company:
            has_checklist = self.eep_program.required_checklists.exists()

        if EEPProgramHomeStatus.objects.filter_by_user(user, id=self.id).exists():
            can_view = True

        # allow permissions to trickle down
        can_edit = can_certify or can_edit
        can_view = can_certify or can_edit or can_view

        attrs = (
            "can_edit",
            "can_view",
            "can_transition_to_certify",
            "can_certify",
            "completed",
            "has_checklist",
        )
        HomeStatuses = namedtuple("SimplifiedStatus", attrs)
        return HomeStatuses(
            can_edit,
            can_view,
            can_transition_to_certify,
            can_certify,
            completed,
            has_checklist,
        )

    def get_answers_for_home(self):
        """Return answers for a home"""
        if not self.collection_request:
            from axis.checklist.models import Answer

            return Answer.objects.filter_by_home_status(self)

        collector = self.get_collector(user_role="rater")
        return collector.get_inputs(cooperative_requests=True)

    def get_qaanswers_for_home(self):
        """Return QA Answers for a home"""
        if not self.collection_request:
            from axis.checklist.models import QAAnswer

            return QAAnswer.objects.filter_by_home_status(self)

        collector = self.get_collector(user_role="qa")
        return collector.get_inputs(cooperative_requests=True)

    def get_next_state(self):
        """This returns the next state"""
        if self.state == "complete":
            return None
        elif self.state == "abandoned":
            return "abandoned_to_pending_transition"
        else:
            return "to_abandoned_transition"

    def get_provider(self):
        """Get the provider for this sucker"""
        from axis.company.models import Company

        if Company.objects.filter(
            id=self.company.id, company_type=Company.PROVIDER_COMPANY_TYPE
        ).count():
            return self.company
        providers = self.get_providers()
        if len(providers) > 1:
            log.warning("More than one provider attached to this home [%s]", self.home.id)
        return providers[0]

    def get_providers(self):
        """Returns all provider companies that are attached to the home."""
        rater_relations = self.company.relationships.get_companies(self.company)
        providers = self.home.relationships.get_provider_orgs()
        providers = list(set(rater_relations).intersection(set(providers)))
        if not len(providers):
            return [self.company]
        if len(providers) > 1:
            # PECI (EPS New Construction) is only used for eto
            if self.eep_program.owner.slug == "eto":
                return [x for x in providers if x.slug == "peci"]
            return [x for x in providers if x.slug != "peci"]
        return providers

    def get_electric_company(self, raise_errors=False):
        """Get the electric company"""
        return self.home.get_electric_company(raise_errors=raise_errors)

    def get_gas_company(self, raise_errors=False):
        """Get the gas company"""
        return self.home.get_gas_company(raise_errors=raise_errors)

    # def get_water_company(self, raise_errors=False):
    #     """Get the water company"""
    #     return self.home.get_water_company(raise_errors=raise_errors)

    def get_annotations_breakdown(self):
        """
        Returns a dict mapping annotation types to annotation instances, where the instance may be
        None for a type that is required by the program, but currently not filled out.
        """
        # This is a re-implementation of the Home.get_annotations_by_eep() method.

        required_annotations = {}

        required_types = self.eep_program.required_annotation_types.all()
        current_annotations = self.annotations.filter(type__in=required_types).select_related(
            "type"
        )
        annotations_lookup = {annotation.type: annotation for annotation in current_annotations}
        for annotation_type in required_types:
            required_annotations[annotation_type] = annotations_lookup.get(annotation_type, None)
        return required_annotations

    def get_missing_annotation_types(self):
        """
        Returns the queryset of annotation.Type objects that this program requires, but which are
        currently not filled out.
        """
        required_types = self.eep_program.required_annotation_types.filter(is_required=True)

        return required_types.exclude(pk__in=self.annotations.values_list("type"))

    def calculate_active_floorplan(self):
        from axis.floorplan.models import Floorplan

        # Select a floorplan to be the active one.
        try:
            final_floorplan = self.floorplans.get(type="final")
        except (Floorplan.DoesNotExist, Floorplan.MultipleObjectsReturned):
            try:
                ThroughModel = EEPProgramHomeStatus.floorplans.through
                final_floorplan = (
                    ThroughModel.objects.filter(eepprogramhomestatus=self)
                    .order_by("-id")[0]
                    .floorplan
                )
            except IndexError:
                final_floorplan = None
        return final_floorplan

    # Samplesets
    def get_sampleset(self):
        samplesethomestatus = self.get_samplesethomestatus()
        if samplesethomestatus:
            return samplesethomestatus.sampleset
        return None

    def get_samplesethomestatus(self):
        if not self.pk:
            from axis.sampleset.models import SampleSetHomeStatus

            return SampleSetHomeStatus.objects.none()

        queryset = self.samplesethomestatus_set.current().select_related("sampleset")
        try:
            return queryset.get()
        except queryset.model.MultipleObjectsReturned:
            log.error(
                "Multiple SampleSetHomeStatus for HomeStatus: {}".format(self.id),
                exc_info=1,
            )
            return queryset.first()

        except queryset.model.DoesNotExist:
            return None

    def remove_from_sampleset(self):
        """Removes this homestatus from its active sampleset."""
        # WARNING: Only do this if you're certain it is allowed (e.g., not certified, incentives)
        self.samplesethomestatus_set.current().delete()

    def get_current_sampleset_home_statuses(self):
        """Gets all stats in the current sampleset"""
        sampleset = self.get_sampleset()
        if sampleset:
            return EEPProgramHomeStatus.objects.in_sampleset(sampleset=sampleset)
        return EEPProgramHomeStatus.objects.none()

    def get_source_sampleset_answers(self, include_failures=False):
        """Returns a dictionary of question ids to their answer ids (or None if unanswered)."""
        from axis.sampleset.utils import get_homestatus_test_answers

        return get_homestatus_test_answers([self], include_failures=include_failures)

    def get_contributed_sampleset_answers(self):
        """Returns answers that have been given to this home via sampling."""
        return Answer.objects.filter(samplesethomestatus__home_status=self).distinct()

    def get_failing_sampleset_answers(self):
        return self.get_source_sampleset_answers(include_failures=True).filter(
            is_considered_failure=True
        )

    #
    # Status progress checking methods
    def get_completion_requirements(self, references=None):
        """
        Builds a list of requirements test callbacks for this home to be ready for certification.
        Test method names should follow the pattern "get_FOO_status()".

        The Program will be allowed to add/remove items from the default test list via a hook at
        ``eep_program.alter_certification_requirements(requirements_list)``.  This hook should
        return the final list of tests.

        Only test returned from this method will be run and their results displayed to the user.
        """

        requirement_tests = [
            # customer hirl checks
            self.get_customer_hirl_project_status,
            self.get_customer_hirl_project_fees_status,
            self.get_customer_hirl_project_verifier_status,
            self.get_customer_hirl_project_builder_agreement_status,
            self.get_customer_hirl_project_coi_status,
            self.get_customer_hirl_project_builder_is_water_sense_partner,
            self.get_already_certified_status,
            self.get_sampled_house_status,
            self.get_required_questions_remaining_status,
            self.get_optional_questions_remaining_status,
            self.get_uncovered_questions_status,
            self.get_model_file_status,
            self.get_model_data_status,
            self.get_required_annotations_status,
            self.get_program_owner_attached_status,
            self.get_builder_required_status,
            self.get_provider_required_status,
            self.get_rater_required_status,
            self.get_utility_required_status,
            self.get_hvac_required_status,
            self.get_qa_required_status,
            self.get_architect_required_status,
            self.get_developer_required_status,
            self.get_communityowner_required_status,
            self.get_multiple_utility_check_status,
            self.get_remrate_flavor_support,
            self.get_floorplan_subdivision_matches_home_subdivision_status,
            self.get_std_protocol_penn_power,
            # self.get_gating_qa_requirement,
            # Add warnings last, since they can't trigger failfast anyway.
            # We don't want to spend time running them when failfast in enabled.
            self.get_floorplan_remrate_data_error_status,
            self.get_floorplan_remrate_data_warning_status,
            self.get_floorplan_simulation_error_status,
            self.get_floorplan_simulation_warning_status,
            self.get_rater_of_record_status,
            self.get_energy_modeler_status,
            self.get_field_inspectors_status,
            self.get_simulation_gas_utility_status,
            self.get_simulation_electric_utility_status,
        ]

        # Allow the Program to modify the certification requirements list.
        requirement_tests = self.eep_program.alter_certification_requirements(
            requirement_tests, references
        )

        if references is None:
            return requirement_tests

        # TODO - Update this to support references.

        return requirement_tests

    def get_completion_test_kwargs(self, user=None, **kwargs):
        """Returns dict of kwargs for certification tests, including Home-specific stuff."""

        kwargs = super(EEPProgramHomeStatus, self).get_completion_test_kwargs(user, **kwargs)

        sampleset_homestatus = self.get_samplesethomestatus()

        collector = None
        if self.collection_request:
            answerer_role = "rater"
            if self.collection_request.eepprogramhomestatus.eep_program.is_qa_program:
                answerer_role = "qa"

            context = {
                "user_role": answerer_role,  # not user's role
            }
            collector = self.get_collector(**context)
            inputs = (
                collector.get_inputs(cooperative_requests=True)
                .order_by("date_created")
                .select_related("instrument__response_policy")
                .get_breakdown("instrument__measure_id")
            )
        else:
            answers = self.get_answers_for_home()
            inputs = {
                answer._measure: answer
                for answer in answers.annotate(
                    **{
                        "_measure": F("question__slug"),
                    }
                )
            }

        ann_edit_url = "#instruction-edit:home_status_annotations-home_status_annotations_{}"
        co_edit_url = "#instruction-edit:home_relationships-home_relationships_{}"
        kwargs.update(
            {
                "collector": collector,
                # Alias things from WorkflowStatus super()
                "home": kwargs["certifiable_object"],
                "home_status": kwargs["workflow_status"],
                # Crunched data
                "builder": self.home.get_builder(),
                "eep_companies": self.eep_program.owner.relationships.get_companies(),
                "accepted_companies": self.home.relationships.get_accepted_companies(),
                "unaccepted_companies": self.home.relationships.get_unaccepted_companies(),
                "samplesethomestatus": sampleset_homestatus,
                "sampleset": (sampleset_homestatus.sampleset if sampleset_homestatus else None),
                "inputs": inputs,
                "input_values": self.get_input_values(),
                # URLs
                "annotations_edit_url": ann_edit_url.format(self.pk),
                "home_edit_url": "#instruction-edit:home-home_{}".format(self.home.pk),
                "companies_edit_url": co_edit_url.format(self.home.pk),
                "checklist_url": "#/tabs/checklist",
            }
        )

        return kwargs

    def get_already_certified_status(self, skip_certification_check, **kwargs):
        """Returns a good status if the home is still awaiting certification."""
        # Returning None will omit the test entirely from the results list
        if skip_certification_check or not self.certification_date:
            return None

        msg = strings.ALREADY_CERTIFIED
        return FailingStatusTuple(data=self.certification_date, message=msg, url=None)

    def get_unanswered_questions(self, collector=None, **kwargs):
        """Powers status checking for ``get_unanswered_questions_status()``"""
        sshs = self.get_samplesethomestatus()
        if sshs:
            return sshs.find_uncovered_questions()

        if collector is None and self.collection_request:
            context = {
                "user_role": "rater" if not self.eep_program.is_qa_program else "qa",
            }
            collector = self.get_collector(**context)

        if collector:
            answered_measure_pks = list(
                collector.get_inputs(cooperative_requests=True)
                .values_list("instrument__measure", flat=True)
                .distinct()
            )
            instruments = collector.get_instruments(active=True).exclude(
                measure__in=answered_measure_pks
            )
            for instrument in instruments:
                instrument.is_optional = not instrument.response_policy.required
            # inst_values = instruments.values_list('measure', flat=True)
            # print({"Answered": answered_measure_pks, "Remaining": inst_values})
            return instruments
        else:
            if self.eep_program.is_qa_program:
                answers = self.get_qaanswers_for_home().values_list("id", flat=True)
            else:
                answers = self.get_answers_for_home().values_list("id", flat=True)
            return (
                self.get_all_questions()
                .exclude(answer__id__in=list(answers))
                .exclude(qaanswer__id__in=list(answers))
            )

    def get_all_questions(self, collector=None, **kwargs):
        from axis.checklist.models import Question

        if collector:
            return collector.get_active_instruments()
        else:
            return Question.objects.filter_by_home_status(self)

    def get_questions_edit_permission_for_user(self, user):
        if user.company == self.company:
            log.debug("User owns the home stat [%s]. -- has edit permissions", self.id)
            return "edit"
        elif self.company.relationships.get_companies().filter(id=user.company_id).exists():
            log.debug(
                "User has relationship with home stat [%s] owner. -- has readonly permissions",
                self.id,
            )
            return "readonly"
        elif self.associations.filter(company=user.company, is_active=True).exists():
            log.debug(
                "Associations exist on the home stat [%s]. -- has readonly permissions",
                self.id,
            )
            return "readonly"
        elif user.is_superuser:
            log.debug("User is super. -- has readonly permissions")
            return "readonly"
        log.debug(
            "User [%s] has no affiliation with the stat [%s] attached to this home.",
            user.id,
            self.id,
        )
        return None

    def get_questions_and_permission_for_user(self, user):
        """
        Get the questions associated with this stat along with the users ability to edit them.
        :param user: User
        :return: Question Queryset, permission string
        """

        # add the questions from the EEP
        questions = self.eep_program.get_checklist_question_set()
        permission = self.get_questions_edit_permission_for_user(user)
        questions = questions.distinct()

        if permission:
            return questions, permission

        return Question.objects.none(), None

    def get_required_questions_remaining_status(self, checklist_url, **kwargs):
        """Returns a good status if the number of unanswered required questions is 0."""

        if kwargs["sampleset"]:
            # This will be checked with alternate logic in "get_uncovered_questions_status()"
            return None

        instruments = self.get_unanswered_questions(**kwargs)

        collector = kwargs.get("collector")
        if collector:
            instruments = instruments.filter(response_policy__required=True)
            if instruments.exists():
                msg = "There are %d required checklist questions remaining." % instruments.count()
                return FailingStatusTuple(data=True, message=msg, url=checklist_url)
            return PassingStatusTuple(data=0)

        # Legacy
        questions = instruments
        required_unanswered_count = len([q for q in questions if not q.is_optional])

        kwargs = {"n": required_unanswered_count}
        if required_unanswered_count:
            msg = strings.HAS_UNANSWERED_REQUIRED_QUESTIONS
            if required_unanswered_count > 1:
                msg = strings.HAS_UNANSWERED_REQUIRED_QUESTIONS_PLURAL

            return FailingStatusTuple(
                data=required_unanswered_count,
                message=msg.format(**kwargs),
                url=checklist_url,
            )

        return PassingStatusTuple(data=required_unanswered_count)

    def get_optional_questions_remaining_status(self, checklist_url, **kwargs):
        """Returns a good status if the number of unanswered optional questions is 0."""

        if kwargs["sampleset"]:
            # This will be checked with alternate logic in "get_uncovered_questions_status()"
            return None

        optional_unanswered_count = len(
            [q for q in self.get_unanswered_questions(**kwargs) if q.is_optional]
        )

        kwargs = {"n": optional_unanswered_count}
        if optional_unanswered_count:
            msg = strings.HAS_UNANSWERED_OPTIONAL_QUESTIONS
            if optional_unanswered_count > 1:
                msg = strings.HAS_UNANSWERED_OPTIONAL_QUESTIONS_PLURAL

            return WarningStatusTuple(
                data=optional_unanswered_count,
                message=msg.format(**kwargs),
                url=checklist_url,
            )

        return PassingStatusTuple(data=None)

    def get_uncovered_questions_status(self, samplesethomestatus, **kwargs):
        if samplesethomestatus is None:
            return None

        num_uncovered = samplesethomestatus.find_uncovered_questions().count()
        if num_uncovered:
            if num_uncovered == 1:
                msg = strings.HAS_UNCOVERED_QUESTIONS
            else:
                msg = strings.HAS_UNCOVERED_QUESTIONS_PLURAL
            return FailingStatusTuple(
                data=num_uncovered, message=msg.format(n=num_uncovered), url=None
            )
        return PassingStatusTuple(data=None)

    def get_sampled_house_status(self, sampleset, samplesethomestatus, **kwargs):
        """Returns a good status only if the home isn't a sampled one (rating_type != 3)"""
        if not sampleset:
            # Skip sampleset integrity check
            return None

        current_test_homes = sampleset.samplesethomestatus_set.filter(revision=sampleset.revision)
        if not current_test_homes.filter(is_test_home=True).exists():
            msg = strings.MISSING_TEST_HOME.format(rating_type="Sampled House")
            return FailingStatusTuple(data=sampleset, message=msg, url=None)
        return PassingStatusTuple(data=None)

    def get_model_file_status(self, edit_url, **kwargs):
        """Returns a good status if no model file is required, or else is required and set."""
        if not self.eep_program.require_model_file:
            return None
        if self.floorplan is not None:
            if not bool(self.floorplan.remrate_data_file):
                msg = strings.MISSING_REMRATE_FILE
                return FailingStatusTuple(
                    data=self.floorplan.remrate_data_file, message=msg, url=edit_url
                )
            else:
                return PassingStatusTuple(data=self.floorplan.remrate_data_file)
        else:
            msg = strings.MISSING_FLOORPLAN_FILE
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

    def get_model_data_status(self, edit_url, **kwargs):  # noqa: C901
        """
        Returns a good status if no data is required, or else is required and set properly.
        """

        qualifiers = any(
            [
                self.eep_program.require_input_data,
                self.eep_program.require_rem_data,
                self.eep_program.require_model_file,
                self.eep_program.require_ekotrope_data,
            ]
        )

        if self.certification_date or not qualifiers:
            return None

        sim = None
        if self.floorplan:
            try:
                sim = self.floorplan.simulation
            except ObjectDoesNotExist:
                sim = None
            if sim is None:
                # We should have this but why don't we..
                from axis.floorplan.models import Floorplan
                from axis.floorplan.signals import floorplan_simulation_sync

                floorplan_simulation_sync(None, self.floorplan, False, False)
                self.floorplan = Floorplan.objects.get(id=self.floorplan.id)
                sim = self.floorplan.simulation

        if self.floorplan is None or sim is None:
            errors = [MISSING_SIMULATION_DATA]
            if self.eep_program.require_rem_data:
                errors = [MISSING_REMRATE_DATA]
            elif self.eep_program.require_ekotrope_data:
                errors = [MISSING_EKOTROPE_DATA]

            if self.floorplan:
                if self.floorplan.remrate_target:
                    errors += self.floorplan.remrate_target.get_validation_errors()
                elif self.floorplan.ekotrope_houseplan:
                    errors += self.floorplan.ekotrope_houseplan.get_validation_errors()
            return FailingStatusTuple(data=None, message=", ".join(errors), url=edit_url)

        # Be aware -- At this point require_input_data is now satisfied.  But is it the right stuff?

        if self.eep_program.require_model_file and not self.floorplan.remrate_data_file:
            return FailingStatusTuple(data=None, message=MISSING_REMRATE_FILE, url=edit_url)

        if self.eep_program.require_rem_data and sim.source_type != SourceType.REMRATE_SQL:
            msg = "Only REM/Rate data is allowed"
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

        elif self.eep_program.require_ekotrope_data and sim.source_type != SourceType.EKOTROPE:
            msg = "Only Ekotrope data is allowed"
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

        eri = sim.get_default_eri_score()
        min_eri_value = self.eep_program.min_hers_score
        max_eri_value = self.eep_program.max_hers_score
        if min_eri_value > 0.0 or max_eri_value < 100.0:
            if eri is None:
                return FailingStatusTuple(data=eri, message=MISSING_ERI_SCORE, url=edit_url)

            if min_eri_value > 0.0 and eri < min_eri_value:
                return FailingStatusTuple(
                    data=eri, message=ERI_SCORE_TOO_LOW.format(eri=eri), url=edit_url
                )
            if max_eri_value < 100.0 and eri > max_eri_value:
                return FailingStatusTuple(
                    data=eri, message=ERI_SCORE_TOO_HIGH.format(eri=eri), url=edit_url
                )

        return PassingStatusTuple(data=eri)

    @requirement_test("Verify REMRate Flavor", eep_program=["neea-efficient-homes"])
    def get_remrate_flavor_support(self, edit_url, **kwargs):
        """
        Returns a good status if the home is single family.
        """
        try:
            flavor = self.floorplan.remrate_target.flavor.strip()
        except AttributeError:
            flavor = "Unknown"

        if flavor.lower() not in ["northwest", "washington"]:
            msg = strings.INVALID_REMRATE_FLAVOR.format(flavor=flavor, required_flavor="Northwest")
            return FailingStatusTuple(data=self.floorplan, message=msg, url=edit_url)

        return PassingStatusTuple(data=None)

    def get_required_annotations_status(self, annotations_edit_url, **kwargs):
        num_required = self.eep_program.required_annotation_types.filter(is_required=True).count()

        if num_required == 0:
            return None

        missing_types = list(self.get_missing_annotation_types().values_list("name", flat=True))
        num_missing = len(missing_types)

        if num_missing and not self.certification_date:
            missing_list = "<ul><li>%s</li></ul>" % ("</li><li>".join(missing_types),)
            msg = strings.MISSING_REQUIRED_ANNOTATIONS
            return FailingStatusTuple(
                message=msg.format(n=num_missing),
                url=annotations_edit_url,
                weight=(num_required - num_missing),
                total_weight=num_required,
                data=missing_list,
                show_data=True,
            )
        return PassingStatusTuple(data=None)

    def get_program_owner_attached_status(self, accepted_companies, **kwargs):
        """Returns a good status if there are incentives and the program owner is attached."""
        program = self.eep_program
        incentives = program.rater_incentive_dollar_value + program.builder_incentive_dollar_value

        if incentives > 0 and not accepted_companies.filter(id=program.owner.id).exists():
            msg = strings.PROGRAM_OWNER_NOT_ATTACHED
            return FailingStatusTuple(
                data=incentives, message=msg.format(owner=program.owner), url=None
            )
        return PassingStatusTuple(data=incentives)

    def _get_company_required_status(
        self,
        company_type,
        eep_companies,
        accepted_companies,
        unaccepted_companies,
        companies_edit_url,
        **kwargs,
    ):
        """Common logic for the various company_type relationship checking variants."""
        COMPANY_TYPE = company_type.upper()
        program = self.eep_program

        require_assigned_to_home = getattr(program, "require_%s_assigned_to_home" % company_type)
        require_relationship = getattr(program, "require_%s_relationship" % company_type)
        companies = list(
            accepted_companies.filter(company_type=company_type).values_list("id", flat=True)
        )
        builder = kwargs.get("builder")
        if company_type == "builder" and builder and builder.id not in companies:
            companies.append(builder.id)

        unaccepted_companies = unaccepted_companies.filter(company_type=company_type)
        unaccepted_companies = list(unaccepted_companies.values_list("id", flat=True))

        if require_assigned_to_home and not companies:
            if not unaccepted_companies:
                msg = getattr(strings, "MISSING_%s" % COMPANY_TYPE)
                return FailingStatusTuple(
                    data=len(companies),
                    message=msg.format(program=program),
                    url=companies_edit_url,
                )
            # If you are here, the company has been assigned but has not yet accepted a
            # relationship to the 'home'. Why should a program owner care if a company doesn't
            # approve the relationship to the home?  If the home_status.company added the company
            # is that good enough?  We may want to revisit this later and require the relationship
            # be accepted via a separate requirement.
        if require_relationship and companies and not eep_companies.filter(id__in=companies):
            msg = getattr(strings, "MISSING_%s_RELATIONSHIP" % COMPANY_TYPE)
            return FailingStatusTuple(
                data=0,
                message=msg.format(program=program, owner=program.owner),
                url=companies_edit_url,
            )

        if require_relationship:
            return PassingStatusTuple(data=None)
        else:
            return None

    def get_builder_required_status(self, **kwargs):
        """Returns a good status if the builder company is required and has a relationship."""
        return self._get_company_required_status("builder", **kwargs)

    def get_provider_required_status(self, **kwargs):
        """Returns a good status if the provider company is required and has a relationship."""
        return self._get_company_required_status("provider", **kwargs)

    def get_rater_required_status(self, **kwargs):
        """Returns a good status if the rater company is required and has a relationship."""
        return self._get_company_required_status("rater", **kwargs)

    def get_utility_required_status(self, **kwargs):
        """Returns a good status if the utility company is required and has a relationship."""
        return self._get_company_required_status("utility", **kwargs)

    def get_hvac_required_status(self, **kwargs):
        """Returns a good status if the hvac company is required and has a relationship."""
        return self._get_company_required_status("hvac", **kwargs)

    def get_qa_required_status(self, **kwargs):
        """Returns a good status if the qa company is required and has a relationship."""
        return self._get_company_required_status("qa", **kwargs)

    def get_architect_required_status(self, **kwargs):
        """Returns a good status if the architect company is required and has a relationship."""
        return self._get_company_required_status("architect", **kwargs)

    def get_developer_required_status(self, **kwargs):
        """Returns a good status if the developer company is required and has a relationship."""
        return self._get_company_required_status("developer", **kwargs)

    def get_communityowner_required_status(self, **kwargs):
        """
        Returns a good status if the communityowner company is required and has a relationship.
        """
        return self._get_company_required_status("communityowner", **kwargs)

    def get_multiple_utility_check_status(self, home_edit_url, **kwargs):
        """
        Returns a good status if the type of company can
        be easily obtained and doesn't conflict
        """
        try:
            self.get_electric_company(raise_errors=True)
        except Relationship.MultipleObjectsReturned:
            err = strings.MULTIPLE_SPECIFIC_UTILITY.format(utility_type="Electric Provider")
            return FailingStatusTuple(data=0, message=err, url=home_edit_url)
        try:
            self.get_gas_company(raise_errors=True)
        except Relationship.MultipleObjectsReturned:
            err = strings.MULTIPLE_SPECIFIC_UTILITY.format(utility_type="Gas Provider")
            return FailingStatusTuple(data=0, message=err, url=home_edit_url)
        # try:
        #     self.get_water_company(raise_errors=True)
        # except MultipleObjectsReturned:
        #     err = strings.MULTIPLE_SPECIFIC_UTILITY.format(utility_type="Water Provider")
        #     return FailingStatusTuple(data=0, message=str(err), url=home_edit_url)
        return PassingStatusTuple(data=None)

    def get_floorplan_remrate_data_error_status(self, **kwargs):
        # TODO: Deprecate this after conversion
        # This gets handled by simulation error
        if self.eep_program.slug in ["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"]:
            return

        if not self.floorplan or not self.floorplan.remrate_target:
            return None

        issues = self.floorplan.remrate_target.compare_to_home_status(self)

        msg = "REM/Rate Data mismatch:<span class='progress-list'><ul>"
        for issue in issues.get("error", []):
            msg += "<li>{}</li>".format(issue)
        msg += "</ul></span>"
        if len(issues.get("error", [])):
            return FailingStatusTuple(data=None, url=None, message=mark_safe(msg))

        return PassingStatusTuple(data=None)

    def get_floorplan_remrate_data_warning_status(self, **kwargs):
        # TODO: Deprecate this after conversion
        # This gets handled by simulation warning

        if self.eep_program.slug in ["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"]:
            return

        if not self.floorplan or not self.floorplan.remrate_target:
            return None

        issues = self.floorplan.remrate_target.compare_to_home_status(self)

        msg = "REM/Rate Data mismatch:<span class='progress-list'><ul>"
        for issue in issues.get("warning", []):
            msg += "<li>{}</li>".format(issue)
        msg += "</ul></span>"
        if issues.get("warning", []):
            return WarningStatusTuple(data=None, url=None, message=mark_safe(msg))

    def get_simulation_cache_key(self):
        """Returns a cache key for simulation"""

        dates = [
            self.modified_date,
            self.floorplan.modified_date,
            self.floorplan.simulation.modified_date,
        ]

        last_answer = self.collectedinput_set.order_by("date_modified").last()
        if last_answer:
            dates.append(last_answer.date_modified)

        last_modified = max(dates).strftime("%d-%b-%Y %H:%M:%S")

        key = (
            f"sim-{self.id}-{self.floorplan.id}-" f"{self.floorplan.simulation.id}-{last_modified}"
        )
        cache_key = hashlib.sha1(key.encode("utf-8")).hexdigest()
        return cache_key

    def get_floorplan_simulation_status(self, level="errors", **kwargs):
        """Compare elements against expected values for a given program"""
        # TODO: Open completely after conversion

        from axis.customer_eto.validations import (
            get_eto_2020_simulation_validations,
            get_eto_2021_simulation_validations,
            get_eto_2022_simulation_validations,
        )

        validation_map = {
            "eto-2020": get_eto_2020_simulation_validations,
            "eto-2021": get_eto_2021_simulation_validations,
            "eto-fire-2021": get_eto_2021_simulation_validations,
            "eto-2022": get_eto_2022_simulation_validations,
        }

        if self.eep_program.slug not in validation_map:
            return None

        if self.floorplan is None or self.floorplan.simulation is None:
            return None

        cache_key = self.get_simulation_cache_key()
        result = cache.get(cache_key)
        if result and level in result:
            leveled_result = result.get(level, [])
        else:
            validation = validation_map.get(self.eep_program.slug)
            result = validation(self, self.floorplan.simulation)
            cache.set(cache_key, result, 60 * 30)
            leveled_result = result.get(level, [])

        message = True
        if len(leveled_result):
            message = "Simulation data mismatch:<span class='progress-list'><ul>"
            for issue in leveled_result:
                message += "<li>{}</li>".format(issue)
            message += "</ul></span>"
        return message

    @requirement_test(
        "Verify Simulation data meets expectations",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"],
    )
    def get_floorplan_simulation_error_status(self, **kwargs):
        """Compare elements against expected values for a given program"""
        message = self.get_floorplan_simulation_status()
        if message is None:  # Does not apply
            return
        if message is True:
            return PassingStatusTuple(data=None)
        return FailingStatusTuple(data=None, url=None, message=mark_safe(message))

    @requirement_test(
        "Verify Simulation data meets expectations (warnings)",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"],
    )
    def get_floorplan_simulation_warning_status(self, **kwargs):
        """Compare elements against expected values for a given program"""
        message = self.get_floorplan_simulation_status("warnings")
        if message is None:  # Does not apply
            return
        if message is True:
            return PassingStatusTuple(data=None)
        return WarningStatusTuple(data=None, url=None, message=mark_safe(message))

    def get_rater_of_record_status(self, user, edit_url, **kwargs):
        if not self.eep_program.require_rater_of_record:
            return None

        url = None
        if user and user.company.company_type in ("provider", "rater"):
            url = edit_url
        if self.rater_of_record is None:
            return FailingStatusTuple(data=None, url=url, message=strings.MISSING_RATER_OF_RECORD)
        return None

    def get_energy_modeler_status(self, user, edit_url, **kwargs):
        if not self.eep_program.require_energy_modeler:
            return None

        url = None
        if user and user.company.company_type in ("provider", "rater"):
            url = edit_url
        if self.energy_modeler is None:
            return FailingStatusTuple(data=None, url=url, message=strings.MISSING_ENERGY_MODELER)
        return None

    def get_field_inspectors_status(self, user, edit_url, **kwargs):
        if not self.eep_program.require_field_inspector:
            return None

        url = None
        if user and user.company.company_type in ("provider", "rater"):
            url = edit_url
        if not self.field_inspectors.count():
            return FailingStatusTuple(data=None, url=url, message=strings.MISSING_FIELD_INSPECTOR)
        return None

    @requirement_test("Verify Floorplan matches Subdivision", eep_program=APS_PROGRAM_SLUGS)
    def get_floorplan_subdivision_matches_home_subdivision_status(self, home_edit_url, **kwargs):
        if not self.floorplan:
            return None

        home_subdivision = self.home.subdivision
        home_floorplan_url = self.floorplan.get_absolute_url()
        floorplan_subdivision = self.floorplan.subdivision_set.first()

        if floorplan_subdivision:
            if home_subdivision:
                if floorplan_subdivision == home_subdivision:
                    return None  # Matches, no warning
                return FailingStatusTuple(
                    data=None,
                    url=home_floorplan_url,
                    message="Correct Floorplan Subdivision Association",
                )
            else:
                return FailingStatusTuple(
                    data=None,
                    url=home_edit_url,
                    message="Home must have Subdivision Association",
                )
        else:
            if home_subdivision:
                return FailingStatusTuple(
                    data=None,
                    url=home_floorplan_url,
                    message="Floorplan must have Subdivision Association",
                )

    @requirement_test(
        "Verify Gas utility if simulation equipment uses natural gas",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"],
    )
    def get_simulation_gas_utility_status(self, companies_edit_url, **_kwargs):
        """If the simulation uses gas fuel then we need a gas utility"""
        if self.floorplan is None or self.floorplan.simulation is None:
            return

        fuels_used = self.floorplan.simulation.get_fuels_used()
        if FuelType.NATURAL_GAS not in fuels_used:
            return
        if self.get_gas_company() is not None:
            return PassingStatusTuple(data=None)
        return FailingStatusTuple(
            data=None,
            url=companies_edit_url,
            message="Simulation data uses natural gas but gas utility not specified",
        )

    @requirement_test(
        "Verify Electric utility if simulation equipment uses electricity",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"],
    )
    def get_simulation_electric_utility_status(self, companies_edit_url, **_kwargs):
        """If the simulation uses electric fuel then we need a electric utility"""
        if self.floorplan is None or self.floorplan.simulation is None:
            return

        fuels_used = self.floorplan.simulation.get_fuels_used()
        if FuelType.ELECTRIC not in fuels_used:
            return
        if self.get_electric_company() is not None:
            return PassingStatusTuple(data=None)
        return FailingStatusTuple(
            data=None,
            url=companies_edit_url,
            message="Simulation data uses electricity but electric utility not specified",
        )

    @requirement_test("Verify Peninsula Power Meter Requirements", eep_program=NEEA_BPA_SLUGS)
    def get_std_protocol_penn_power(self, home_status, checklist_url, input_values, **kwargs):
        """If the electric utility is Penn Power (utility-peninsula-power-light) there is a
        requirement for an electric meter number"""

        try:
            utility = self.get_electric_company(raise_errors=True)
        except Relationship.MultipleObjectsReturned:
            return None

        if utility and utility.slug != "utility-peninsula-power-light":
            return None

        errors = []
        meter_number = input_values.get("neea-electric_meter_number")
        if not meter_number:
            errors.append("Electric Meter number is required")

        if not len(errors):
            return PassingStatusTuple(data=None)

        msg = "Peninsula Power requires multiple additional questions:" + ", ".join(errors)
        if len(errors) == 1:
            msg = "Peninsula Power requires optional question: " + errors[0]
        return FailingStatusTuple(data=None, url=checklist_url, message=msg)

    @requirement_test(
        "Verify that Project is in Active State",
        eep_program=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS,
    )
    def get_customer_hirl_project_status(self, home_status, **kwargs):
        from axis.customer_hirl.models import HIRLProjectRegistration

        hirl_project = getattr(home_status, "customer_hirl_project", None)
        if hirl_project:
            if hirl_project.registration.state == HIRLProjectRegistration.ACTIVE_STATE:
                return PassingStatusTuple(data=None)
            return FailingStatusTuple(
                data=None,
                url=hirl_project.get_absolute_url(),
                message=f"NGBS MF Registration is incomplete. "
                f"Click <a href='{hirl_project.registration.get_absolute_url()}'>here</a> "
                f"to finalize registration",
            )
        return FailingStatusTuple(data=None, url="", message="Project does not exist")

    @requirement_test(
        "Verify that Project fees have been paid",
        eep_program=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS,
    )
    def get_customer_hirl_project_fees_status(self, home_status, **kwargs):
        from axis.customer_hirl.models import HIRLProject

        hirl_project = getattr(home_status, "customer_hirl_project", None)
        if hirl_project:
            # annotate fee balance
            hirl_project = (
                HIRLProject.objects.filter(id=hirl_project.id)
                .annotate_fee_balance()
                .select_related("home_status", "registration")
                .first()
            )
            if hirl_project.fee_current_balance > 0:
                return WarningStatusTuple(
                    data=None,
                    url="#/tabs/invoicing",
                    message="Check outstanding balance of certification fees",
                )
            return PassingStatusTuple(data=None)

        return FailingStatusTuple(data=None, url="", message="Project does not exist")

    @requirement_test(
        "Verifier status",
        eep_program=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS,
    )
    def get_customer_hirl_project_verifier_status(self, home_status, **kwargs):
        from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates

        verifiers = [
            getattr(home_status, "customer_hirl_rough_verifier", None),
            getattr(home_status, "customer_hirl_final_verifier", None),
        ]

        for verifier in verifiers:
            if verifier:
                if not verifier.company:
                    return FailingStatusTuple(
                        data=None,
                        url=verifier.get_absolute_url(),
                        message=f"Verifier {verifier} does not belong to any Company",
                    )

                accreditation_exists = (
                    home_status.eep_program.hirl_program_have_accreditation_for_user(user=verifier)
                )

                if not accreditation_exists:
                    return WarningStatusTuple(
                        data=None,
                        url=verifier.get_absolute_url(),
                        message=f"Verifier {verifier.get_full_name()} "
                        f"must have an active accreditation",
                    )

                # Verifier must have active Verifier Agreement
                verifier_agreement_exists = (
                    verifier.customer_hirl_enrolled_verifier_agreements.filter(
                        state__in=[
                            VerifierAgreementStates.VERIFIED,
                            VerifierAgreementStates.COUNTERSIGNED,
                        ]
                    ).exists()
                )

                if not verifier_agreement_exists:
                    return WarningStatusTuple(
                        data=None,
                        url=reverse("hirl:verifier_agreements:list"),
                        message=f"Verifier {verifier.get_full_name()} "
                        f"does not have any active Verifier Agreement",
                    )

                #  Check expiration date of verifier COI’s
                active_cois_exists = verifier.company.coi_documents.active().exists()
                if not active_cois_exists:
                    return WarningStatusTuple(
                        data=None,
                        url=verifier.get_absolute_url(),
                        message=f"Verifier {verifier.get_full_name()} "
                        f"does not have any active Certificate of Insurance",
                    )

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Client Agreement status",
        eep_program=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS,
    )
    def get_customer_hirl_project_builder_agreement_status(self, home_status, **kwargs):
        from axis.customer_hirl.models import BuilderAgreement

        hirl_project = getattr(home_status, "customer_hirl_project", None)
        if not hirl_project:
            return PassingStatusTuple(data=None)

        try:
            project_client_company = hirl_project.registration.get_project_client_company()
        except ObjectDoesNotExist:
            return FailingStatusTuple(
                data=None,
                url=hirl_project.get_absolute_url(),
                message="Project Client is not set. ",
            )

        client_agreement = project_client_company.customer_hirl_enrolled_agreements.filter(
            state__in=[BuilderAgreement.VERIFIED, BuilderAgreement.COUNTERSIGNED]
        ).first()

        if not client_agreement:
            return WarningStatusTuple(
                data=None,
                url=reverse("hirl:agreements:list"),
                message=f"No Client Agreement found for {project_client_company}. ",
            )

        if (
            hirl_project.registration.eep_program.slug in customer_hirl_app.WRI_PROGRAM_LIST
            or hirl_project.is_require_water_sense_certification
            or hirl_project.is_require_wri_certification
        ):
            version = client_agreement.get_ca_version_to_sign()
            if version == 1:
                return WarningStatusTuple(
                    data=None,
                    url=client_agreement.get_absolute_url(),
                    message=f"Client Agreement must be updated for certification "
                    f"of a WRI or WaterSense project for {project_client_company} ",
                )

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Certificate of Insurance status",
        eep_program=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS,
    )
    def get_customer_hirl_project_coi_status(self, home_status, **kwargs):
        hirl_project = getattr(home_status, "customer_hirl_project", None)
        if not hirl_project:
            return PassingStatusTuple(data=None)

        try:
            project_client_company = hirl_project.registration.get_project_client_company()
        except ObjectDoesNotExist:
            return FailingStatusTuple(
                data=None,
                url=hirl_project.get_absolute_url(),
                message="Project Client is not set",
            )

        coi_document_count = project_client_company.coi_documents.count()

        if coi_document_count:
            client_agreements = project_client_company.customer_hirl_enrolled_agreements
            client_agreements = client_agreements.annotate_company_coi_info()
            active_coi_exists = client_agreements.filter(active_coi_document_count__gt=0).exists()
            if not active_coi_exists:
                return WarningStatusTuple(
                    data=None,
                    url=f"{project_client_company.get_absolute_url()}#/tabs/coi",
                    message=f"Certificate of Insurance is "
                    f"expired for {project_client_company}. "
                    f"Click here to update COI.",
                )
        else:
            return WarningStatusTuple(
                data=None,
                url=f"{project_client_company.get_absolute_url()}#/tabs/coi",
                message=f"Certificate of Insurance is missing "
                f"for {project_client_company}. "
                f"Click here to update COI.",
            )
        return PassingStatusTuple(data=None)

    @requirement_test(
        "Water Sense partner status",
        eep_program=customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS,
    )
    def get_customer_hirl_project_builder_is_water_sense_partner(self, home_status, **kwargs):
        hirl_project = getattr(home_status, "customer_hirl_project", None)
        if not hirl_project:
            return PassingStatusTuple(data=None)

        if not hirl_project.is_require_water_sense_certification:
            return PassingStatusTuple(data=None)

        is_water_sense_partner = (
            hirl_project.registration.builder_organization.is_water_sense_partner()
        )

        if not is_water_sense_partner:
            return WarningStatusTuple(
                data=None,
                url="https://www.epa.gov/watersense/watersense-partnership-agreement",
                message=f"According to the EPA WaterSense website, the "
                f"{hirl_project.registration.builder_organization} builder "
                f"is not currently a Water Sense partner. "
                f"Click here to complete the online partnership agreement.",
            )
        return PassingStatusTuple(data=None)

    def get_standard_disclosure_settings(self, company):
        return flatten_inheritable_settings(
            company,
            manager_attr="standarddisclosuresettings_set",
            sources=[company, self.home.subdivision, self],
        )

    @property
    def analytical_rollup(self):
        AnalyticRollup = apps.get_model(app_label="analytics", model_name="AnalyticRollup")
        content_type = ContentType.objects.get_for_model(self)
        try:
            analytics = AnalyticRollup.objects.get(
                content_type__pk=content_type.pk, object_id=self.id
            )
        except ObjectDoesNotExist:
            return None
        return analytics

    def get_references(self):
        associations = set(
            list(self.home.relationships.values_list("company__pk", flat=True)) + [self.company.pk]
        )

        try:
            qa_status = EEPProgramHomeStatus.objects.get(
                home=self.home,
                eep_program__is_qa_program=True,
                eep_program__slug__icontains=self.eep_program.slug,
            )
            qa_collection_request = qa_status.collection_request_id
        except EEPProgramHomeStatus.DoesNotExist:
            qa_collection_request = None
        except Exception as err:
            log.error(err)
            qa_collection_request = None

        analysis_type_hints = None
        analysis_type = AnalysisType.DEFAULT
        if self.eep_program.slug in ["eto-2022"]:
            analysis_type_hints = Q(
                type__contains=2023, simulation__source_type=SourceType.REMRATE_SQL
            ) | Q(type__contains=2022, simulation__source_type=SourceType.EKOTROPE)
            if self.home.state == "WA":
                analysis_type_hints = Q(type__contains=2021)
        if self.eep_program.slug in ["eto-2021", "eto-fire-2021"]:
            analysis_type_hints = {"type__contains": 2021}
        if self.eep_program.slug == "eto-2020":
            analysis_type_hints = {"type__contains": 2020}
        if self.eep_program.slug == "eto-2019":
            analysis_type_hints = {"type__contains": 2019}
        if analysis_type_hints:
            try:
                analysis = self.floorplan.simulation.logical_as_designed_analyses(
                    type_hints=analysis_type_hints
                )
                analysis_type = analysis.get().type
            except (AttributeError, ObjectDoesNotExist):
                pass

        if self.floorplan and self.floorplan.simulation is None and self.floorplan.remrate_target:
            log.warning("Home %s is missing simulation but Rem data exists" % self.home_id)

        rater_collection_last_update = None
        try:
            dm = self.collection_request.collectedinput_set.all().order_by("date_modified").last()
            rater_collection_last_update = dm.date_modified if dm else None
        except AttributeError:
            pass

        annotation_last_update = None
        try:
            am = self.annotations.order_by("last_update").last()
            annotation_last_update = am.last_update if am else None
        except AttributeError:
            pass

        return {
            "home_id": self.home.pk if self.home else None,
            "home_status_id": self.pk,
            "eep_program_id": self.eep_program_id,
            "rating_company_id": self.company_id,
            "rater_of_record_id": self.rater_of_record_id,
            "rater_collection_request_id": self.collection_request_id,
            "rater_collection_last_update": rater_collection_last_update,
            "qa_collection_request_id": qa_collection_request,
            "annotation_last_update": annotation_last_update,
            "associated_company_ids": list(associations),
            "floorplan_id": self.floorplan_id,
            "remrate_simulation_id": self.floorplan.remrate_target_id if self.floorplan else None,
            "simulation_id": self.floorplan.simulation_id if self.floorplan else None,
            "city_id": self.home.city_id if self.home else None,
            "county_id": self.home.county_id if self.home else None,
            "us_state": self.home.county.state if self.home and self.home.county_id else None,
            "addresss_long": self.home.get_addr(include_city_state_zip=True, raw=True)
            if self.home
            else None,
            "climate_zone_id": self.home.county.climate_zone_id
            if self.home and self.home.county
            else None,
            "state": self.state,
            "analysis_type": analysis_type,
        }

    def _validate_references(
        self,
        force: bool = False,
        immediate: bool = False,
        freeze: bool = False,
        override_complete: bool = False,
        freeze_post_run: bool = False,
    ):
        from analytics.models import AnalyticRollup
        from analytics.tasks import update_rollup_analytics

        if self.state == "complete" and not override_complete:
            if not freeze:
                return
        if self.state == "abandoned" and not force:
            return

        program_metrics = self.eep_program.metrics.all()
        if not program_metrics.count():
            return

        rollup, create = AnalyticRollup.objects.create_from_model(self)
        msg = f"Metrics ({rollup.id}) are in state {rollup.status} -> %(next)s"
        if not rollup.should_be_updated(create=create, force=force):
            log.debug(msg % {"next": "skipping"})
            return

        msg = f"Metrics ({rollup.id}) are in state {rollup.status} -> %(next)s"
        rollup.set_metrics(reference_metrics=program_metrics)
        rollup.status = "FROZEN" if freeze else "REQUIRES_UPDATE"
        rollup.save()

        if freeze:
            log.debug(msg % {"next": "freezing"})
            return

        log.debug(msg % {"next": "processing"})
        if settings.CELERY_TASK_ALWAYS_EAGER or immediate:
            update_rollup_analytics(rollup.pk, freeze=freeze_post_run, force=force)
        else:
            args = [rollup.pk]
            kwargs = {"freeze": freeze_post_run, "force": force}
            task = update_rollup_analytics.apply_async(countdown=5, args=args, kwargs=kwargs)
            log.info(
                f"Deployed `update_rollup_analytics` with task {task}"
                f"{' and freeze' if freeze_post_run else ''} for {rollup.pk}"
            )
        return AnalyticRollup.objects.get(id=rollup.id)

    def validate_references(self, force=False, immediate=False, freeze=False, **kwargs):
        # Call it on both QA changes and Rater Changes.
        if not self.eep_program.is_qa_program:
            return self._validate_references(
                force=force, immediate=immediate, freeze=freeze, **kwargs
            )
        stat = EEPProgramHomeStatus.objects.filter(
            home=self.home.id, eep_program=self.eep_program.get_rater_program()
        ).first()
        if stat:
            return stat.validate_references(
                force=force, immediate=immediate, freeze=freeze, **kwargs
            )
        return
