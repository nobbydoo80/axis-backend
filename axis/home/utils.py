"""utils: Django axis.home"""


__author__ = "Steven Klass"
__date__ = "2/14/12 7:55 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging
import os
import time
from collections import namedtuple
from functools import partial
from io import BytesIO
from zipfile import ZipFile

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import serializers

from axis.customer_aps.strings import APS_PROGRAM_SLUGS
from axis.resnet.tasks import submit_home_status_to_registry
from . import strings

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


def validate_compatible_program(home, eep_program, raise_exception=True, pretty=False, **kwargs):
    """Validate comptible programs"""
    tests = []
    errors = []  # irrelevant if raise_exception=True

    tests.append(partial(validate_compatible_aps_program, home, eep_program, **kwargs))

    tests.append(
        partial(
            validate_compatible_multifamily_program,
            home.is_multi_family,
            eep_program,
            **kwargs,
        )
    )

    for test in tests:
        try:
            test()
        except serializers.ValidationError as e:
            if raise_exception:
                raise
            if pretty:
                if isinstance(e.detail, dict):
                    for k, v in e.detail.items():
                        err = "{}: {}"
                        if isinstance(v, list):
                            for _v in v:
                                errors.append(err.format(k, _v))
                        else:
                            errors.append(err.format(k, v))
                elif isinstance(e.detail, list):
                    for err in e.detail:
                        errors.append(err)
            else:
                errors.append(e.detail)
    return errors


def validate_compatible_aps_program(home, eep_program, instance_eep_program=None, **kwargs):
    """Raises ValidationError if home configuration does not allow the given eep_program."""

    ignore_program_ids = [eep_program.id]
    try:
        instance_eep_program_id = instance_eep_program.id
    except AttributeError:
        # If instance_eep_program is something we're coming
        # from an update an we need to allow program switching.
        pass
    else:
        ignore_program_ids.append(instance_eep_program_id)

    has_other_aps_programs = home.homestatuses.exclude(
        Q(eep_program__id__in=ignore_program_ids)
        | Q(eep_program__slug="aps-energy-star-2019-tstat")
    ).filter(eep_program__slug__contains="aps")

    if "aps" in eep_program.slug and has_other_aps_programs.count() > 1:
        raise serializers.ValidationError(
            {"eep_program": [strings.APS_MULTIPLE_PROGRAMS_NOT_ALLOWED]}
        )


def validate_compatible_multifamily_program(
    is_multi_family, eep_program, created_date=None, state=None, **kwargs
):
    """Raises ValidationError if home configuration does not allow the given eep_program."""

    # Presently this only checks the 'is_multi_family' flag.

    if created_date is None:
        created_date = now()

    if eep_program.slug == "neea-energy-star-v3":
        # Prescriptive
        if state == "complete":
            return
        if (
            created_date > datetime.datetime(2015, 7, 1).replace(tzinfo=datetime.timezone.utc)
            and state != "complete"
        ):
            raise serializers.ValidationError(
                {"eep_program": [strings.NEEA_INVALID_PROGRAM.format(program=eep_program)]}
            )
        if not is_multi_family:
            raise serializers.ValidationError(
                {"eep_program": [strings.PRESCRIPTIVE_REQUIRES_MULTIFAMILY]}
            )
    elif eep_program.slug in [
        "neea-energy-star-v3-performance",
        "neea-performance-2015",
    ]:
        # Performance
        if is_multi_family:
            raise serializers.ValidationError(
                {"eep_program": [strings.PERFORMANCE_REQUIRES_NON_MULTIFAMILY]}
            )
    elif eep_program.slug == "neea-prescriptive-2015" and not is_multi_family:
        raise serializers.ValidationError(
            {"eep_program": [strings.PRESCRIPTIVE_2015_REQUIRES_MULTIFAMILY]}
        )
    elif eep_program.slug == "utility-incentive-v1-multifamily" and not is_multi_family:
        raise serializers.ValidationError({"eep_program": [strings.GENERIC_REQUIRES_MULTIFAMILY]})


def get_inheritable_settings_form_info(
    company, obj, attr, form_class, settings_action_url, document_action_url
):
    """Returns a dict of helper data for the financial checklist modal UI."""

    # NOTE: The data['form'] key needs to survive examine machinery's self.serialize_form_spec()
    # in order to correctly be inspected in examine templates.

    from axis.company.models import Company
    from axis.subdivision.models import Subdivision
    from .models import EEPProgramHomeStatus, Home

    settings_model = getattr(obj, attr).model  # getattr() retrieves the reverse related manager

    valid_types = (Home, EEPProgramHomeStatus, Subdivision, Company)
    if not isinstance(obj, valid_types):
        raise ValueError("Unexpected object %r" % (obj,))

    form = form_class(company, instance=obj)
    data = {
        "form": form,
        "question_data": [],
    }

    # Break questions up into groups based on where headers should appear
    grouping = []
    header = None
    for f in settings_model._meta.local_fields:
        if f.remote_field or f.name == "id":
            continue

        if f.name not in form.fields:
            continue

        if f.name in settings_model.HEADERS:
            # Add the current collection to the question data
            data["question_data"].append(
                {
                    "header": header,
                    "items": grouping,
                }
            )

            # Reset values so we build a new list
            header = settings_model.HEADERS[f.name]
            grouping = []

        # Add question to current list
        grouping.append(
            {
                "name": f.name,
                "null_value": "unset" if getattr(f, "choices", None) else None,
                "show_label": bool(getattr(f, "choices", None)),
            }
        )

    # Append last set to the end
    data["question_data"].append(
        {
            "header": header,
            "items": grouping,
        }
    )

    pk = obj.pk or 0
    if isinstance(obj, EEPProgramHomeStatus):
        data.update(
            {
                "type": "home_status",
                "url": reverse(
                    "apiv2:home_status-{action_url}".format(action_url=settings_action_url),
                    kwargs={"pk": pk},
                ),
                "download_url": reverse(
                    "apiv2:home_status-{action_url}".format(action_url=document_action_url),
                    kwargs={"pk": pk},
                ),
                "parents": [
                    "subdivision",
                    "company",
                ],  # backwards on purpose, css reverses
                "company": {},
                "subdivision": {},
            }
        )
        settings_queryset = getattr(company, attr)
        tier_settings = settings_queryset.get_for_company(company)
        if tier_settings:
            data["company"] = tier_settings.as_dict(raw_values=True, display_values=True)
        if obj.home.subdivision:
            settings_queryset = getattr(obj.home.subdivision, attr)
            tier_settings = settings_queryset.get_for_company(company)
            if tier_settings:
                data["subdivision"] = tier_settings.as_dict(raw_values=True, display_values=True)

    elif isinstance(obj, Home):
        data.update(
            {
                "type": "home",
                "url": reverse(
                    "apiv2:home-{action_url}".format(action_url=settings_action_url),
                    kwargs={"pk": pk},
                ),
                "download_url": reverse(
                    "apiv2:home-{action_url}".format(action_url=document_action_url),
                    kwargs={"pk": pk},
                ),
                "parents": ["company", "subdivision"],
                "company": {},
                "subdivision": {},
            }
        )
        settings_queryset = getattr(company, attr)
        tier_settings = settings_queryset.get_for_company(company)
        if tier_settings:
            data["company"] = tier_settings.as_dict(raw_values=True, display_values=True)
        if obj.subdivision:
            settings_queryset = getattr(obj.subdivision, attr)
            tier_settings = settings_queryset.get_for_company(company)
            if tier_settings:
                data["subdivision"] = tier_settings.as_dict(raw_values=True, display_values=True)

    elif isinstance(obj, Subdivision):
        data.update(
            {
                "type": "subdivision",
                "url": reverse(
                    "apiv2:subdivision-{action_url}".format(action_url=settings_action_url),
                    kwargs={"pk": pk},
                ),
                "download_url": reverse(
                    "apiv2:subdivision-{action_url}".format(action_url=document_action_url),
                    kwargs={"pk": pk},
                ),
                "download_bulk_url": reverse(
                    "apiv2:subdivision-{action_url}".format(action_url=document_action_url),
                    kwargs={"pk": pk},
                ),
                "parents": ["company"],
                "company": {},
            }
        )
        settings_queryset = getattr(company, attr)
        tier_settings = settings_queryset.get_for_company(company)
        if tier_settings:
            data["company"] = tier_settings.as_dict(raw_values=True, display_values=True)

    elif isinstance(obj, Company):
        data.update(
            {
                "type": "company",
                "url": reverse(
                    "apiv2:company_new-{action_url}".format(action_url=settings_action_url),
                    kwargs={"pk": pk, "type": obj.company_type},
                ),
                "parents": [],
            }
        )

    return data


def flatten_inheritable_settings(company, manager_attr, sources, exclude=None):
    """Flatten out inheritable settings"""
    data = {}

    for obj in sources:
        if not obj:
            continue

        reverse_manager = getattr(obj, manager_attr)
        settings_obj = reverse_manager.get_for_company(company)
        if settings_obj:
            data.update(
                {
                    k: v
                    for k, v in settings_obj.as_dict().items()
                    if v is not None and (not exclude or k not in exclude)
                }
            )

    ct_fk_aliases = {
        "eepprogramhomestatus": "home_status",
    }

    # Keep object references instead of fk pks brought in by model_to_dict()
    for obj in sources:
        model_name = obj._meta.model_name
        model_name = ct_fk_aliases.get(model_name, model_name)
        if not exclude or model_name not in exclude:
            data[model_name] = obj

    return data


def get_required_annotations_form(instance, *args, **kwargs):
    """Takes a homestatus and returns the RequiredAnnotations form for its type requirements."""
    from axis.annotation.forms import RequiredAnnotationsForm

    annotations = instance.get_annotations_breakdown()
    return RequiredAnnotationsForm(
        annotations=annotations, instance=instance, prefix=None, *args, **kwargs
    )


def write_home_program_reports(user, queryset, filter_info=None, task=None, log=log):
    """Write the home program report"""

    def build_report(home_status, filestream):
        """Build the report"""
        report = HomeDetailReport(return_document=False, left_margin=0.4, right_margin=0.4)
        report.build(home_stat=home_status, response=filestream, user=user)
        log.info(
            'Report created for <a href="%s">%s</a>',
            home_status.home.get_absolute_url(),
            home_status,
        )

    def update_task_progress(state="STARTED", steps=None, step=0, current=1, total=1, **kwargs):
        """
        Update an asynchronous tasks state. Primarily used for send data to the client.
        :param state: string of custom state to set Task to.
        :param steps: list of processing steps
        :param step: int current step. 0 based
        :param current: int current progress point in total
        :param total: int total number of progress points
        """
        steps = steps or ["processing", "writing"]

        current_step = steps[step]

        meta = {}
        for s in steps:
            if s == current_step:
                meta[s] = {"current": current, "total": total}
            elif steps.index(s) > steps.index(current_step):
                # takes place after current step
                meta[s] = {"current": 0, "total": 1}
            else:
                # takes place before current step
                meta[s] = {"current": 1, "total": 1}
        meta.update(kwargs)
        if task is not None:
            task.update_state(state=state, meta=meta)

    from .reports import HomeDetailReport

    INDIVIDUAL_FILENAME = "Program Report - {street_line1} - {eep_program}.pdf"
    MULTI_HOMESTATUS_ZIPNAME = "Program_Reports.zip"

    filter_info = filter_info or []
    num_items = len(queryset)
    update_task = partial(update_task_progress, step=1, total=num_items)
    update_task()

    log.info("%s Filters have been used resulted in %s results", len(filter_info), num_items)
    for key, value in filter_info:
        log.info("&emsp;&emsp;{}&emsp;:&emsp;{}".format(key, value))

    filename, response_stream = "No Data.txt", BytesIO()
    if num_items > 1:
        zipfile = ZipFile(response_stream, "a")

        for i, home_status in enumerate(queryset):
            file_stream = BytesIO()
            build_report(home_status, file_stream)
            zipfile.writestr(
                INDIVIDUAL_FILENAME.format(
                    street_line1=home_status.home.street_line1,
                    eep_program=home_status.eep_program,
                ),
                file_stream.getvalue(),
            )
            update_task(current=i + 1)
            log.debug("Finished row %d / %d", i + 1, num_items)

        for f in zipfile.filelist:
            f.create_system = 0

        zipfile.close()
        filename = MULTI_HOMESTATUS_ZIPNAME
    elif num_items == 1:
        home_status = queryset[0]
        build_report(home_status, response_stream)
        filename = INDIVIDUAL_FILENAME.format(
            street_line1=home_status.home.street_line1,
            eep_program=home_status.eep_program,
        )
        update_task(current=1)
        log.debug("Finished single row %d / %d", 1, num_items)

    return filename, response_stream


def get_eps_data(home_status, recalculate=False, **kwargs):
    """Get the EPS Data"""

    eps_report_url = reverse("eto:download", kwargs={"home_status": home_status.id})
    # kwargs coming from homestatus examine api endpoint, not necessarily used
    if hasattr(home_status, "fasttracksubmission"):
        ft = home_status.fasttracksubmission
        if not ft.is_locked():
            recalculate = True

    if hasattr(home_status, "fasttracksubmission") and not recalculate:
        results = {}
        for k, v in home_status.fasttracksubmission.__dict__.items():
            if k.startswith("_"):
                continue
            if k == "id":
                k = "fasttracksubmission_id"
            results[k] = v
        results["eps_report_url"] = eps_report_url
        results["is_locked"] = home_status.fasttracksubmission.is_locked()
        return results

    from axis.customer_eto.reports.legacy_utils import get_legacy_calculation_data

    results = get_legacy_calculation_data(
        home_status, return_fastrack_data=True, return_errors=True
    )

    if "errors" not in results:
        results["fasttracksubmission_id"] = None
        results["eps_report_url"] = eps_report_url
        results["is_locked"] = False
    return results


def find_duplicates(comp_values=None, **kwargs):
    """Find duplicates"""
    from axis.home.models import Home

    compare_values = ["id"]
    compare_values += (
        comp_values
        if comp_values
        else ["street_line1", "street_line2", "city__name", "state", "zipcode"]
    )
    HomeData = namedtuple("HomeData", ["street_line1", "street_line2", "city", "state", "zipcode"])
    results, duplicates = {}, {}
    for _home in Home.objects.filter(**kwargs).values_list(*compare_values):
        idx, home = None, []
        for item in list(_home):
            if _home.index(item) == 0:
                idx = item
                continue
            if isinstance(item, str):
                item = item.strip().lower() if len(item.strip()) else None
            home.append(item)
        home_data = HomeData(*home)
        if home_data not in duplicates:
            duplicates[home_data] = []
        duplicates[home_data].append(idx)

    results = {}
    for home_d, data in duplicates.items():
        if len(data) <= 1:
            continue
        data.sort()
        is_multi = all(Home.objects.filter(id__in=data).values_list("is_multi_family", flat=True))
        if is_multi:
            print("Skipping {} Multi-Family {}, {}".format(len(data), home_d, data))
        else:
            results[home_d] = data
            print("{} entries found for {} {}".format(len(data), home_d, data))

    return results


class HomeCertificationMixin(object):
    """Home Certification Mixin"""

    href = "<a href='{}'>{}</a>"

    def __init__(self, user, stat, certification_date, **kwargs):
        from axis.checklist.models import Answer

        self.user = user
        self.stat = stat
        if certification_date:
            self.certification_date = certification_date
        self.answers = kwargs.get("answers", Answer.objects.none())
        self.kwargs = kwargs

        self.sampleset = self.stat.get_sampleset()

        self.home_href = self.href.format(self.stat.home.get_absolute_url(), self.stat.home)
        if self.sampleset:
            _href = self.href.format(self.sampleset.get_absolute_url(), self.sampleset)
            self.sampleset_href = _href

    @property
    def certification_date(self):
        """Certification Date"""
        if not hasattr(self, "_certification_date"):
            if self.stat.certification_date:
                self._certification_date = self.stat.certification_date

            if self.sampleset:
                ss_stats = (
                    self.sampleset.samplesethomestatus_set.current()
                    .certified()
                    .filter(is_test_home=True)
                )
                self._certification_date = ss_stats[0].home_status.certification_date

        return self._certification_date

    @certification_date.setter
    def certification_date(self, value):
        """Certification Date Settr"""

        if isinstance(value, datetime.datetime):
            value = value.date()

        if isinstance(value, str):
            value = datetime.datetime.strptime(date_string=value, format="%m/%d/%Y").date()
        self._certification_date = value

    def check_certification_date(self):
        """Certification Date Check"""

        if not self.certification_date:
            raise TypeError("No Certification Date")
        elif self.certification_date > (datetime.date.today() + datetime.timedelta(days=1)):
            raise ValueError("Homes may not certify more than 1 day in advance.")


class CheckHomeCanCertify(HomeCertificationMixin):
    """Can a home be certified"""

    unable_to_certify = "Unable to certify {type} home {home} - {err}"
    error_messages = {
        "check_already_certified": strings.EXISTING_PROGRAM_ALREADY_CERTIFIED,
        "gating_qa": strings.FAILED_GATING_QA_REQUIREMENT,
        "check_user": strings.FAILED_CERTIFICATION_NOT_ALLOWED_TO_CERTIFY,
        "get_certification_date": "No valid certification date.",
        "check_certification_date": "Must have a certification date.",
        "check_pct_complete": "Must be 100% complete only {:.2f}",
        "check_sampleset_eligibility": "Not all homes in the sampleset can be certified.",
        "check_document_questions": "Some answers require documents which "
        "have not been added for {home}",
        "check_photo_questions": "Some answers require photos which have not been added for {home}",
        "certification_date_in_future": "Homes may not certify more than 1 day in advance.",
        "not_a_certifying_org": "{company} is not an approved certifying organization for program.",
        "no_association": "{company} has no association to {home_status_company}.",
        "no_association_to_home": "{company} has no association to {home}.",
    }

    def __init__(self, user, stat, certification_date, fail_fast=True, **kwargs):
        super(CheckHomeCanCertify, self).__init__(user, stat, certification_date, **kwargs)
        self.fail_fast = fail_fast

        self.errors = []
        self.log = kwargs.get("log", log).getChild("HomeCanCertify")
        self.log.setLevel(kwargs.get("loglevel", logging.WARNING))
        self.log_errors = kwargs.get("log_errors", True)
        self.rating_type = self.stat.get_rating_type()

    @property
    def can_certify(self):
        """Can it be certified"""
        return len(self.errors) == 0

    @property
    def already_certified(self):
        """Is it already certified"""
        return (
            self.stat.certification_date
            and self.stat.state == "complete"
            and not self.answers.filter(confirmed=False).exists()
        )

    @property
    def verification_requirements(self):
        """Verification checks must be run prior to certification"""
        checks = [
            self.check_already_certified,
            self.check_gating_qa,
            self.check_user,
            self.check_eligibility,
            self.check_certification_date,
            self.check_pct_complete,
            self.check_sampleset_eligibility,
            self.check_document_questions,
            self.check_photo_questions,
            self.check_aps_program,
            self.check_certifiable_entity,
        ]

        try:
            company_slug = self.user.company.slug
        except AttributeError:
            company_slug = None

        if self.stat.eep_program.slug == "neea-efficient-homes" and company_slug in [
            "clearesult-qa",
            company_slug,
        ]:
            log.debug("Removing user check..")
            checks.pop(checks.index(self.check_user))
        return checks

    def get_unable_to_certify_message(self, error):
        """Unable to certify message"""
        return self.unable_to_certify.format(type=self.rating_type, home=self.home_href, err=error)

    def append_error(self, err, as_error=True):
        """Append an error"""
        if self.log_errors:
            if not as_error:
                self.log.info(f"Error: {err}")
            else:
                self.log.debug(f"Warning: {err}")
        self.errors.append(err)

    def verify(self):
        """Run the checks"""
        for check in self.verification_requirements:
            check()

            if self.fail_fast and not self.can_certify:
                break

    # CHECKS =====================
    def check_already_certified(self):
        if self.already_certified:
            self.append_error(
                self.error_messages["check_already_certified"].format(
                    url=self.stat.home.get_absolute_url(),
                    home=self.stat.home,
                    program=self.stat.eep_program,
                )
            )

    def check_gating_qa(self):
        if not self.stat.is_gating_qa_complete():
            self.append_error(self.error_messages["gating_qa"])

    def check_user(self):
        if not self.stat.can_user_certify(self.user, perform_eligiblity_check=False):
            self.append_error(self.error_messages["check_user"])

    def check_eligibility(self):
        progress = self.stat.get_progress_analysis(
            skip_certification_check=True, fail_fast=self.fail_fast
        )

        if not progress["status"]:
            self.append_error(
                strings.NOT_ELIGIBLE_FOR_CERTIFICATION.format(
                    url=self.stat.home.get_absolute_url(),
                    home=self.stat.home,
                    program=self.stat.eep_program,
                ),
                as_error=False,
            )

    def check_pct_complete(self):
        pct_complete = self.stat.pct_complete
        if self.sampleset:
            if pct_complete < 99.9 and not self.stat.get_samplesethomestatus().is_test_home:
                for item in self.sampleset.samplesethomestatus_set.current().filter(
                    is_test_home=True
                ):
                    _pct_complete = max(
                        item.home_status.home.homestatuses.all().values_list(
                            "pct_complete", flat=True
                        )
                    )
                    if _pct_complete > pct_complete:
                        pct_complete = _pct_complete

        if pct_complete < 99.9:
            self.append_error(
                self.error_messages["check_pct_complete"].format(self.stat.pct_complete)
            )

    def check_certification_date(self):
        if not self.certification_date:
            self.append_error(
                self.get_unable_to_certify_message(self.error_messages["check_certification_date"])
            )
        elif self.certification_date > (datetime.date.today() + datetime.timedelta(days=1)):
            self.append_error(
                self.get_unable_to_certify_message(
                    self.error_messages["certification_date_in_future"]
                )
            )

    def check_sampleset_eligibility(self):
        if self.sampleset and not self.sampleset.can_be_certified():
            self.append_error(
                self.get_unable_to_certify_message(
                    self.error_messages["check_sampleset_eligibility"]
                )
            )

    def check_document_questions(self):
        customer_document_q = Q(
            customer_documents__type="document", customer_documents__isnull=True
        )
        filter_kwargs = {"document_required": True}

        if self.answers.filter(customer_document_q, **filter_kwargs).count():
            self.append_error(
                self.error_messages["check_document_questions"].format(home=self.home_href)
            )

    def check_photo_questions(self):
        customer_document_q = Q(customer_documents__type="image", customer_documents__isnull=True)
        filter_kwargs = {"photo_required": True, "answerimage__isnull": True}

        if self.answers.filter(customer_document_q, **filter_kwargs).count():
            self.append_error(
                self.error_messages["check_photo_questions"].format(home=self.home_href)
            )

    def check_aps_program(self):
        if self.stat.eep_program.slug not in APS_PROGRAM_SLUGS[4:]:
            return

        from axis.customer_aps.aps_calculator import APSInputException
        from axis.customer_aps.aps_calculator.calculator import APSCalculator

        try:
            APSCalculator(home_status_id=self.stat.id)
        except APSInputException as issues:
            for item in issues[1:]:
                self.append_error(item)

    def check_certifiable_entity(self):
        """Are we a legit certifiable company"""
        if not self.stat.eep_program.certifiable_by.exists():
            return
        from axis.company.models import Company

        certifying_orgs = self.stat.eep_program.certifiable_by.values_list("slug", flat=True)
        if self.user.company.slug not in certifying_orgs:
            self.append_error(
                self.error_messages["not_a_certifying_org"].format(company=self.user.company)
            )

        status_orgs = Company.objects.filter_by_company(self.stat.company, mutual=True).values_list(
            "slug", flat=True
        )
        if self.user.company.slug not in status_orgs:
            if self.user.company.slug != self.stat.company.slug:
                self.append_error(
                    self.error_messages["not_a_certifying_org"].format(company=self.user.company)
                )

        stat_certification_orgs = list(set(certifying_orgs).intersection(set(status_orgs)))
        if self.user.company.slug not in stat_certification_orgs:
            if self.user.company.slug != self.stat.company.slug:
                self.append_error(
                    self.error_messages["no_association"].format(
                        company=self.user.company, home_status_company=self.stat.company
                    )
                )

        # Finally the list of orgs on that home
        home_orgs = self.stat.home.relationships.all().values_list("company__slug", flat=True)
        if self.user.company.slug not in home_orgs:
            self.append_error(
                self.error_messages["no_association_to_home"].format(
                    company=self.user.company, home=self.stat.home
                )
            )


class CertifyHome(HomeCertificationMixin):
    results = []

    def __init__(self, user, stat, certification_date=None, **kwargs):
        super(CertifyHome, self).__init__(user, stat, certification_date, **kwargs)

        self.log = kwargs["log"].getChild("HomeCertify")
        self.log.setLevel(kwargs.get("loglevel", logging.WARNING))

    def certify(self):
        start = time.time()
        self.check_certification_date()
        self.stat.certification_date = self.certification_date
        self.stat.save()

        self.confirm_answers()
        self.update_status_start_date()

        if self.stat.state != "complete":
            self.log.debug("Moving to completion - %s", self.stat)
            self.complete()

        self.submit_to_resnet()
        self.get_final_hes_score()
        self.customer_hirl_additional_actions()

        log.debug(
            "certify() home status %(home_status_id)s "
            "for %(eep_program_slug)s took %(submit_time).3f s",
            {
                "home_status_id": self.stat.pk,
                "eep_program_slug": self.stat.eep_program.slug,
                "submit_time": time.time() - start,
            },
        )

    def confirm_answers(self):
        """Iterate through all the unconfirmed questions and marked them as confirmed."""
        from axis.checklist.tasks import confirm_answers

        kwargs = {
            "user_id": self.user.id,
            "answer_ids": list(
                self.answers.filter(confirmed=False).distinct().values_list("id", flat=True)
            ),
            "home_href": self.home_href,
            "sampleset_href": getattr(self, "sampleset_href", ""),
        }
        confirm_answers.delay(**kwargs)

    def update_status_start_date(self):
        from axis.scheduling.models import ConstructionStage, ConstructionStatus

        try:
            stage = ConstructionStage.objects.get(name="Completed", is_public=True, order=100)
        except ConstructionStage.DoesNotExist:
            stage = ConstructionStage.objects.create(name="Completed", is_public=True, order=100)

        data = {"stage": stage, "home": self.stat.home, "company": self.stat.company}
        try:
            status, _ = ConstructionStatus.objects.get_or_create(**data)
        except ConstructionStatus.MultipleObjectsReturned:
            # FIXME: printing the home stat and the home id may be confusing for future debugging use.
            self.log.info(
                "Auto correcting multiple completed stages for home stat [%s] %s",
                self.stat.home.id,
                self.stat,
            )
            statuses = list(ConstructionStatus.objects.filter(**data))
            status = statuses.pop(0)
            [x.delete() for x in statuses]

        status.start_date = self.certification_date
        status.save()

    def submit_to_resnet(self):
        from axis.resnet.views import user_can_submit_to_resnet_registry

        can_upload = user_can_submit_to_resnet_registry(self.stat, self.user)
        upload = False

        if self.kwargs.get("bulk_upload") and self.kwargs.get("upload_to_registry"):
            if can_upload:
                upload = True
            else:
                self.log.warning("%s could not be submitted to the RESNET Registry", self.stat)
        elif can_upload and self.user.company.auto_submit_to_registry:
            upload = True

        if upload:
            self.log.info("%s is being submitted to the RESNET Registry", self.stat)
            submit_home_status_to_registry.delay(self.stat.id, self.user.id)

    def get_final_hes_score(self):
        """Obtain the final PDF for HES"""
        from axis.home.models import EEPProgramHomeStatus
        from axis.hes.tasks import create_or_update_hes_score
        from axis.hes.models import HESCredentials

        self.stat = EEPProgramHomeStatus.objects.get(id=self.stat.id)
        if not self.stat.hes_score_statuses.count():
            return

        hes_simulation_status = self.stat.hes_score_statuses.first()
        credential_company = hes_simulation_status.company
        try:
            credentials = HESCredentials.objects.filter(company=credential_company).first()
        except ObjectDoesNotExist:
            try:
                credentials = HESCredentials.objects.filter(company=self.user.company).first()
            except HESCredentials.DoesNotExist:
                log.error(
                    "No Credentials found.  Unable to get final HES Score for %(" "status_id)s",
                    {"status_id": self.stat.id},
                )
                return

        create_or_update_hes_score.delay(
            hes_sim_status_id=hes_simulation_status.pk,
            credential_id=credentials.pk,
            orientation=hes_simulation_status.worst_case_orientation,
        )

    def customer_hirl_additional_actions(self):
        from axis.customer_hirl.models import HIRLProject

        if self.stat.eep_program.slug not in customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS:
            return

        hirl_project = getattr(self.stat, "customer_hirl_project", None)

        if not hirl_project:
            return

        is_wri_program = self.stat.eep_program.slug in customer_hirl_app.WRI_PROGRAM_LIST

        if is_wri_program:
            last_project_qs = HIRLProject.objects.filter(
                registration__eep_program__slug__in=customer_hirl_app.WRI_PROGRAM_LIST
            )

            last_project = last_project_qs.order_by("wri_certification_counter").last()
            max_value = 0
            if last_project:
                max_value = last_project.wri_certification_counter

            HIRLProject.objects.filter(id=hirl_project.id).update(
                wri_certification_counter=max_value + 1
            )
        else:
            last_project_qs = HIRLProject.objects.exclude(
                registration__eep_program__slug__in=customer_hirl_app.WRI_PROGRAM_LIST
            )

            last_project = last_project_qs.order_by("certification_counter").last()
            max_value = 0
            if last_project:
                max_value = last_project.certification_counter

            HIRLProject.objects.filter(id=hirl_project.id).update(
                certification_counter=max(
                    max_value, customer_hirl_app.LEGACY_PROJECT_CERTIFICATION_COUNTER
                )
                + 1
            )

    def complete(self):
        from axis.home.models import EEPProgramHomeStatus
        from axis.home.tasks import update_home_states
        from axis.home.signals import eep_program_certified

        self.stat.save()
        update_home_states(eepprogramhomestatus_id=self.stat.id, user_id=self.user.id)

        self.stat = EEPProgramHomeStatus.objects.get(id=self.stat.id)

        if self.stat.state == "complete":
            self.results.append(
                "Certified {} on {}".format(self.home_href, self.certification_date)
            )
            self.log.debug("Certified {} on {}".format(self.home_href, self.certification_date))
            eep_program_certified.send(
                sender=EEPProgramHomeStatus, instance=self.stat, user=self.user
            )
        else:
            self.log.error(
                "%s is unable to transition this home %s to complete.", self.user, self.stat
            )


class HomeCertification(object):
    def __init__(self, user, stat, certification_date, **kwargs):
        self.user = user
        self.stat = stat
        self.certification_date = certification_date
        self.kwargs = kwargs

        from axis.checklist.models import Answer

        self.answers = Answer.objects.filter_by_home_status(stat)

        self.errors = []

    @property
    def already_certified(self):
        return self.stat.certification_date and self.stat.state == "complete"

    def verify(self, log_errors=True):
        check = CheckHomeCanCertify(
            self.user,
            self.stat,
            self.certification_date,
            answers=self.answers,
            log_errors=log_errors,
            **self.kwargs,
        )
        check.verify()
        self.errors = check.errors
        return check.can_certify

    def certify(self):
        start = time.time()
        certify = CertifyHome(
            self.user, self.stat, self.certification_date, answers=self.answers, **self.kwargs
        )
        self.stat.validate_references(freeze=True)
        certify.certify()
        stop = time.time()
        log.info(
            "Certification on status %(home_status_id)s by %(user_id)s "
            "for %(eep_program_slug)s took %(submit_time).3f s",
            {
                "home_status_id": self.stat.pk,
                "user_id": self.user.pk,
                "eep_program_slug": self.stat.eep_program.slug,
                "submit_time": stop - start,
            },
        )


def associate_companies_to_homestatus(obj, *companies):
    """
    Ensures an ``Association`` reference to the homestatus using the program owner as the source
    entity.
    """
    from axis.relationship.utils import associate_companies_to_obj

    associate_companies_to_obj(obj, obj.eep_program.owner, *companies)


def associate_companies_to_homestatuses(company_slugs, program_slugs):
    """
    Ensures an ``Association`` for every given company to every homestatus using the given programs.
    This relies on ``associate_companies_to_homestatus()`` to specify that the owner of the
    association is the program owner.
    """
    from axis.company.models import Company
    from axis.home.models import EEPProgramHomeStatus

    for company_slug in company_slugs:
        company = Company.objects.get(slug=company_slug)
        counties = company.counties.all()
        countries = company.countries.exclude(abbr="US")
        homestatuses = EEPProgramHomeStatus.objects.filter(
            Q(home__city__county__in=counties) | Q(home__city__country__in=countries),
            eep_program__slug__in=program_slugs,
        ).select_related("eep_program__owner")
        log.info(
            f"Associating {homestatuses.count()} home statuses from {counties.count()} counties "
            f"and {countries.count()} countries for {company_slug}"
        )
        for homestatus in homestatuses:
            associate_companies_to_homestatus(homestatus, company)


def associate_nightly_companies_to_homestatuses():
    """Runs associations for groupings of companies to homestatus programs."""

    # Note that these blocks are separate despite having some company overlap so that we can
    # hopefully keep the reasons for the associations clear.

    # NEEA & NCBPA see Energy Star stuff
    associate_companies_to_homestatuses(
        **{
            "company_slugs": [
                "neea",
                "buildingnc",
            ],
            "program_slugs": [
                "doe-zero-energy-ready-rev-05-performance-path",
                "doe-zero-energy-ready-rev-05-prescriptive-pat",
                "energy-star-version-3-rev-07",
                "energy-star-version-3-rev-08",
                "energy-star-version-31-rev-05",
                "energy-star-version-31-rev-08",
                "indoor-airplus-version-1-rev-03",
                "leed",
                "phius",
                "resnet-hers-certification",
            ],
        }
    )

    # NEEA sees Earth Advantage program
    associate_companies_to_homestatuses(
        **{
            "company_slugs": [
                "neea",
            ],
            "program_slugs": [
                "earth-advantage-certified-home",
            ],
        }
    )

    # NEEA sees Built Green
    associate_companies_to_homestatuses(
        **{
            "company_slugs": [
                "neea",
            ],
            "program_slugs": ["built-green-tri-cities", "built-green-king-sno"],
        }
    )

    # NEEA sees ETO
    associate_companies_to_homestatuses(
        **{
            "company_slugs": [
                "neea",
            ],
            "program_slugs": [
                "eto",
                "eto-2015",
                "eto-2016",
                "eto-2017",
                "eto-2018",
                "eto-2019",
                "eto-2020",
                "eto-2021",
                "eto-2022",
            ],
        }
    )

    # NEEA sees Home Innovation Research Labs provider
    associate_companies_to_homestatuses(
        **{
            "company_slugs": [
                "neea",
            ],
            "program_slugs": [
                # legacy programs
                "ngbs-basement-remodel-2012",
                "ngbs-bathroom-remodel-2012",
                "ngbs-green-subdivision-2012",
                "ngbs-kitchen-remodel-2012",
                "ngbs-mf-new-construction-2012",
                "ngbs-mf-remodel-building-2012",
                "ngbs-sf-new-construction-2012",
                "ngbs-sf-whole-house-remodel-2012",
                "ngbs-small-addition-2012",
                "ngbs-mf-new-construction-2015",
                "ngbs-sf-new-construction-2015",
                "ngbs-green-building-renovations-with-additions-75",
                "ngbs-green-remodel-renovations-with-additions-75",
                "ngbs-green-subdivision",
                "ngbs-multi-unit-green-building-renovation",
                "ngbs-multi-unit-green-remodel-renovation",
                "ngbs-multi-unit-new-construction",
                "ngbs-renovations-with-addition-75",
                "ngbs-single-family-additions-75-1",
                "ngbs-single-family-additions-75-2",
                "ngbs-single-family-green-building-renovation",
                "ngbs-single-family-green-remodel-renovation",
                "ngbs-single-family-new-construction",
                # new programs
                "ngbs-sf-new-construction-2020-new",
                "ngbs-mf-new-construction-2020-new",
                "ngbs-sf-whole-house-remodel-2020-new",
                "ngbs-mf-whole-house-remodel-2020-new",
                "ngbs-sf-certified-2020-new",
                "ngbs-sf-new-construction-2015-new",
                "ngbs-mf-new-construction-2015-new",
                "ngbs-sf-whole-house-remodel-2015-new",
                "ngbs-mf-whole-house-remodel-2015-new",
                "ngbs-sf-new-construction-2012-new",
                "ngbs-mf-new-construction-2012-new",
                "ngbs-sf-whole-house-remodel-2012-new",
                "ngbs-mf-whole-house-remodel-2012-new",
            ],
        }
    )

    # NEEA sees WSU
    associate_companies_to_homestatuses(
        **{
            "company_slugs": [
                "neea",
            ],
            "program_slugs": ["wsu-hers-2020"],
        }
    )

    # ETO sees NEEA
    associate_companies_to_homestatuses(
        **{
            "company_slugs": [
                "eto",
            ],
            "program_slugs": [
                "neea-efficient-homes",
                "neea-energy-star-v3-performance",
                "neea-energy-star-v3",
                "neea-prescriptive-2015",
                "neea-performance-2015",
                "utility-incentive-v1-multifamily",
                "utility-incentive-v1-single-family",
                "neea-bpa",
                "neea-bpa-v3",
            ],
        }
    )
