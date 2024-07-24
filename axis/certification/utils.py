import datetime
import logging
import operator
import os
import re
from collections import namedtuple
from functools import reduce

import dateutil.parser
from django.forms.models import modelform_factory

from axis.home import strings  # FIXME: Home requirements names need to be given explicitly

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


CONFIGS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "configs"))
TEST_CODENAME_RE = re.compile(r"^get_(.*?)_status$")


# This is an outdated strategy but
# Data structures for streamlined certification status reporting
StatusTuple = namedtuple(
    "StatusTuple", ["status", "data", "message", "url", "weight", "total_weight", "show_data"]
)
PassingStatusTuple = (
    lambda data, message=None, url=None, weight=1, total_weight=1, show_data=False: StatusTuple(
        status=True,
        data=data,
        message=message,
        url=url,
        weight=weight,
        total_weight=total_weight,
        show_data=show_data,
    )
)
FailingStatusTuple = lambda weight=0, total_weight=1, show_data=False, **kwargs: StatusTuple(
    status=False, weight=weight, total_weight=total_weight, show_data=show_data, **kwargs
)
WarningStatusTuple = lambda weight=0, total_weight=0, show_data=False, **kwargs: StatusTuple(
    status=None, weight=weight, total_weight=total_weight, show_data=show_data, **kwargs
)


def requirement_test(name, filter=None, eep_program=None, ignore_before=None):
    """Convenience decorator for requirement test methods that declare an explicit name."""

    def decorator(m):
        m._test_name = name
        m._test_filter = filter
        m._eep_program_slug_hint = eep_program
        m._ignore_before = ignore_before
        return m

    return decorator


def get_progress_analysis(
    workflow_status, user=None, skip_certification_check=False, as_list=False, fail_fast=False
):
    """
    Returns a report of status indicators concerning progress status.

    If ``as_list`` is True, the requirement statuses are returned as an ordered list of
    dictionaries, rather than one large unordered dictionary of test names mapping to results.

    If a ``user`` is provided, the urls can be modified to fit the user's context.
    """

    from axis.eep_program.models import EEPProgram

    _program_hint_cache = {}

    def applicable_program(test):
        slug_hint = getattr(test, "_eep_program_slug_hint", None)
        if not slug_hint:
            return True

        if isinstance(slug_hint, str):
            slug_hint = (slug_hint,)
        else:
            slug_hint = tuple(slug_hint)

        if slug_hint not in _program_hint_cache:
            # Store whether the program in use matches the slug hint
            _program_hint_cache[slug_hint] = EEPProgram.objects.filter(
                **{
                    "id": workflow_status.eep_program_id,
                    "slug__in": slug_hint,
                }
            ).exists()
        return _program_hint_cache[slug_hint]

    def applicable_date(test):
        date_hint = getattr(test, "_ignore_before", None)
        if not date_hint:
            return True

        # Do NOT catch this exception if it's raised, because the date is declarative and should
        # never be silenced if it can't be parsed.
        target_date = dateutil.parser.parse(date_hint).replace(tzinfo=datetime.timezone.utc).date()

        # Return False if the last meaningful transition into qa took place after the target date,
        # a sign that the requirement should be ignored in order to preserve the QA process of
        # seemingly completed items.
        if workflow_status.state != "inspection":
            qa_pending_transition = (
                workflow_status.state_history.filter(to_state="qa_pending")
                .order_by("start_time")
                .last()
            )
            if qa_pending_transition:
                transition_date = qa_pending_transition.start_time.date()
                if transition_date and transition_date < target_date:
                    return False
        return True

    def _pre_filter(test):
        filters = [applicable_program, applicable_date]
        for filt in filters:
            if filt(test) is False:
                return False
        return True

    # This gets directly serialized by our API.  Be careful what you put in the final data dict.

    # Prune items that declare unmet prerequisites
    test_list = workflow_status.get_completion_requirements()
    requirements = list(filter(_pre_filter, test_list))

    # All test functions will receive these kwargs
    kwargs = workflow_status.get_completion_test_kwargs(
        user, skip_certification_check=skip_certification_check
    )

    # Build a mapping of test names to their results.
    codenames = {f: TEST_CODENAME_RE.sub(r"\1", f.__name__) for f in requirements}
    results = []
    for test in requirements:
        # Skip running the test if the requirement filter function is present and fails
        if hasattr(test, "_test_filter") and test._test_filter:
            if not test._test_filter(**kwargs):
                continue

        # Run the test
        result = test(**kwargs)
        if result is None:
            # Test result is omitted if the value is explicitly not a StatusTuple
            continue

        codename = codenames[test]

        # Obtain a user-facing name
        if hasattr(test, "_test_name"):
            name = test._test_name
        else:
            name = getattr(strings, "REQUIREMENT_NAME_" + codename.upper(), None)
            assert name is not None, "Decorate {codename} with {module}{name}".format(
                **{
                    "codename": codename,
                    "module": requirement_test.__module__,
                    "name": requirement_test.__name__,
                }
            )

        name = name.format(**kwargs)

        results.append([codename, dict(result._asdict(), name=name, codename=codename)])
        if fail_fast and result.status is False:
            break

    # Pack the results in the appropriate format.
    # as_list helps keep the results in the same order as initially requested
    if as_list:
        data = [v for k, v in results]
    else:
        data = dict(results)

    non_warning_results = [(k, v) for k, v in results if v["status"] is not None]

    # Count only True/False items in progress analysis.
    num_passing_tests = len([k for k, v in non_warning_results if v["status"]])
    completed_items = sum([v["weight"] for k, v in non_warning_results if v["weight"]])
    total_items = sum([v["total_weight"] for k, v in non_warning_results])

    completion_percent = 100
    if total_items > 0:
        completion_percent = 100.0 * completed_items / total_items

    # Final data structure, later encoded to JSON in most cases
    return {
        # True only if everything passes
        # Note that None status is a passive warning, so combinations of {None, True} are okay
        "status": all(v["status"] is not False for k, v in results),
        # Individual status items
        "requirements": data,
        "fail_fast": fail_fast,
        # Helpful stats
        "completed_tests": num_passing_tests,
        "completed_requirements": completed_items,
        "total_requirements": total_items,
        "completion": completion_percent,
    }


def update_computed_fields(workflowstatus):
    """Updates object data related to this workflowstatus."""

    # Get root parent object
    parent = workflowstatus.certifiable_object
    while parent.parent is not None:
        parent = parent.parent
    root_parent = parent

    # Accumulate all WorkflowStatus instances in this tree
    related_objects = _get_workflow_statuses(root_parent)

    # Crunch values for any computed field with a value function for the appropriate object_type.
    # Value functions that apply only to other types are typically the sources of the computation,
    # and should not be "updated".
    for workflowstatus in related_objects:
        config = workflowstatus.workflow.get_config()
        settings = workflowstatus.get_settings()  # already includes object_type
        computed_specs = config.get_computed_data_specs(**settings)

        context = {"object_type": settings["object_type"]}
        for field_name, item_spec in computed_specs.items():
            value_getter = item_spec["value"]
            if isinstance(value_getter, dict):
                value_getter = value_getter.get(context["object_type"])
            if value_getter:
                value = value_getter(
                    **{
                        "instance": workflowstatus,
                        "field_name": field_name,
                        "item_spec": item_spec,
                        "context": context,
                    }
                )
                workflowstatus.data[field_name] = value

        workflowstatus.save()


def _get_workflow_statuses(certifiable_object):
    """Recursively gets all WorkflowStatus instances for this CertifiableObject tree."""
    workflowstatuses = list(certifiable_object.workflowstatus_set.all())
    children_workflowstatuses = reduce(
        operator.add,
        [_get_workflow_statuses(child) for child in certifiable_object.children.all()],
        [],
    )
    return workflowstatuses + children_workflowstatuses


def refresh_values_sheet(values_sheet, data):
    form_class = modelform_factory(values_sheet)
    form = form_class(data)
    if not form.is_valid():
        raise ValueError("ValuesSheet data not valid: %r" % (form.errors,))

    form.save()


def get_owner_swap_queryset(user, include_self=False):
    """
    Returns a queryset of candidates for changing a homestatus company to something else, based on
    who the altering ``company`` is.
    """

    from axis.company.models import Company

    company = user.company

    if user.is_superuser:
        return Company.objects.filter(company_type__in=["rater", "provider"])

    queryset = Company.objects.filter_by_company(company, include_self=include_self)
    if company.company_type == "rater":
        queryset = queryset.filter(company_type="rater")
    elif company.company_type in ["provider", "qa"]:
        queryset = queryset.filter(company_type__in=["rater", "provider"])
    else:
        queryset = None

    return queryset


def get_available_eep_program_queryset_for_certifiable_object(certifiable_object_id, user):
    """Returns the queryset of EEPPrograms available for adding to a CertifiableObject."""

    from axis.eep_program.models import EEPProgram
    from .models import CertifiableObject, WorkflowStatus

    if isinstance(certifiable_object_id, CertifiableObject):
        certifiable_object_id = certifiable_object_id.id

    workflow_statuses = WorkflowStatus.objects.filter_by_user(user).filter(
        certifiable_object_id=certifiable_object_id
    )
    exclude_program_ids = set(workflow_statuses.values_list("eep_program_id", flat=True))

    queryset = (
        EEPProgram.objects.filter(owner_id=user.company_id)
        .filter(workflow__isnull=False)
        .exclude(id__in=exclude_program_ids)
    )
    return queryset


def get_available_eep_program_queryset_for_workflow_status(
    workflow_status_id, user, include_self=True
):
    """Returns the queryset of EEPPrograms available for selection on this WorkflowStatus."""

    from axis.eep_program.models import EEPProgram
    from .models import CertifiableObject, WorkflowStatus

    if isinstance(workflow_status_id, WorkflowStatus):
        workflow_status_id = workflow_status_id.id

    certifiable_object = CertifiableObject.objects.get(workflowstatus__id=workflow_status_id)
    workflow_statuses = certifiable_object.workflowstatus_set.filter_by_user(user)

    if include_self:
        # Including self means to ignore self's program in this queryset so that it can still show
        # up later in the last query.
        workflow_statuses = workflow_statuses.exclude(id=workflow_status_id)

    exclude_program_ids = set(workflow_statuses.values_list("eep_program_id", flat=True))

    queryset = (
        EEPProgram.objects.filter(owner_id=user.company_id)
        .filter(workflow__isnull=False)
        .exclude(id__in=exclude_program_ids)
    )
    return queryset
