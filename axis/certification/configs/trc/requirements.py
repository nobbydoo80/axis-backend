import logging
from datetime import datetime, timedelta, timezone

from django.utils.timezone import now

from ...utils import requirement_test, PassingStatusTuple, FailingStatusTuple, WarningStatusTuple
from . import utils


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


tests_list = []


# Decorator for automatic appending of functions to the master list.  No runtime proxying.
def register(f):
    tests_list.append(f)
    return f


# Filter function for 'requirement_test' decorations
def is_state(state):
    """
    Returns True when the kwargs to be sent to a requirement test function match a specific state.
    """

    def filter(workflow_status, **kwargs):
        return state == workflow_status.state

    return filter


# Utility for generating a link to a region form field that will route directly to editing that
# field.
def link_to_field(instance, name, label):
    link_template = """<a href="#{name}" ng-click="progressCtrl.routeRequirementLink('{routable_link}')">{label}</a>"""
    routable_link = "#instruction-edit:#panel_workflowstatus_{pk} [name=\\'{name}\\']".format(
        pk=instance.pk, name=name
    )
    return link_template.format(routable_link=routable_link, name=name, label=label)


# Common logic for obtaining a status readout on a list of interesting data names
def _get_notable_field_test_status(
    field_names, workflow, workflow_status, certifiable_object, edit_url, **kwargs
):
    config = workflow.get_config()

    # Gather available data
    data = workflow_status.get_data(fields=field_names)
    settings = workflow_status.get_settings()
    all_data = dict(data, **settings)

    # Gather relevant data specs
    # 'settings' already contains the object_type kwarg
    data_specs = config.get_data_specs(**settings)
    settings_specs = config.get_settings_specs(**settings)
    all_specs = dict(data_specs, **settings_specs)

    # Get names list for fields from field_names that are missing real values
    required_spec_names = set(field_names) & set(all_specs.keys())
    provided_data_names = set(k for k, v in all_data.items() if v is not None)
    missing_data_names = required_spec_names - provided_data_names

    total_weight = len(required_spec_names)
    completion_weight = total_weight - len(missing_data_names)
    if missing_data_names:
        missing_data_info = sorted(
            [(name, all_specs[name]["label"]) for name in missing_data_names],
            key=lambda data: field_names.index(data[0]),
        )
        missing_data_labels = [link_to_field(workflow_status, *info) for info in missing_data_info]
        msg = """{number} field{plural_s} remaining:"""
        msg = msg.format(
            **{
                "number": len(missing_data_labels),
                "plural_s": "s" if len(missing_data_labels) != 1 else "",
            }
        )
        data = """<ul><li>{}</li></ul>""".format("</li><li>".join(missing_data_labels))
        return FailingStatusTuple(
            message=msg,
            url=edit_url,
            data=data,
            show_data=True,
            weight=completion_weight,
            total_weight=total_weight,
        )
    return PassingStatusTuple([], weight=completion_weight, total_weight=total_weight)


@register
@requirement_test("Horizons")
def has_approaching_horizons(workflow_status, **kwargs):
    """
    Uses the same logic as ``utils.issue_reminder_notifications()`` to decide whether a date needs
    to be shown or not.
    """

    # FIXME: This sort of logic probably shouldn't repeat just for the display.  The utils over in
    # the determination of the nightly task notifications should be adjusted so that they can also
    # reveal "time until" information.

    today = now()

    def make_timer_line(label, delta):
        return """{label}: {days} day{plural_s}""".format(
            **{
                "label": label,
                "days": delta.days,
                "plural_s": "s" if delta.days != 1 else "",
            }
        )

    state = workflow_status.state
    data = workflow_status.data

    horizons = []

    def str_to_datetime(s):
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

    def str_to_date(s):
        return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    if data.get("escalated"):
        escalated_date = str_to_datetime(data["escalated"])
        thresholds = [2, 5]
        for threshold in thresholds:
            target_date = escalated_date + timedelta(days=threshold)
            if target_date >= today:
                delta = (target_date - today) + timedelta(days=1)
                horizons.append(make_timer_line("Escalated", delta))
                break

    if state == "application" and not data.get("application_form_received"):
        target_date = utils.get_date_of_state_entry(workflow_status, "application") + timedelta(
            days=2
        )
        if target_date >= today:
            # FIXME: Businessdays!
            delta = (target_date - today) + timedelta(days=1)
            horizons.append(make_timer_line("Application Notification", delta))
    elif state == "incentive_reserved":
        start_date = data.get("expected_construction_start_date")
        if start_date:
            thresholds = [14, 30]
            for threshold in thresholds:
                target_date = str_to_date(start_date) + timedelta(days=threshold)
                if target_date >= today:
                    delta = (target_date - today) + timedelta(days=1)
                    horizons.append(make_timer_line("Construction Start Reminder", delta))
                    break

        completion_date = data.get("expected_construction_completion_date")
        if completion_date:
            thresholds = [30, 60, 90]
            for threshold in thresholds:
                target_date = str_to_date(completion_date) + timedelta(days=threshold)
                if target_date >= today:
                    delta = (target_date - today) + timedelta(days=1)
                    horizons.append(make_timer_line("Construction Completion (monthly)", delta))
                    break

    if horizons:
        msg = "<ul><li>%s</li></ul>" % ("</li><li>".join(horizons),)
        return WarningStatusTuple(
            message="Scheduled reminders:",
            url=None,
            data=msg,
            show_data=True,
            weight=len(horizons),
            total_weight=len(horizons),
        )
    return None


@register
@requirement_test("{state_name} Requirements", filter=is_state("pre_qual"))
def test_notable_fields_for_pre_qual(**kwargs):
    return _get_notable_field_test_status(
        [
            # CertifiableObject.settings
            "project_name",
            "project_number",
            "project_street1",
            "project_city",
            "project_county",
            "project_state",
            "project_zipcode",
            # WorkflowStatus.data
            "pre_qual_start_date",
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("application"))
def test_notable_fields_for_application(**kwargs):
    return _get_notable_field_test_status(
        [
            "application_form_received",
            "application_package_complete_date",
            "number_of_buildings",
            "number_of_units",
            "expected_construction_start_date",
            "expected_construction_completion_date",
            "property_class",
            "rise_type",
            "year_built",
            "utility_electric",
            "payee_company",
            "payee_contact",
            "customer_company",
            "customer_contact",
            "application_package_coordinator",
            "incentive_type",  # Labeled as "Program Pathway"
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("technical_assistance"))
def test_notable_fields_for_technical_assistance(**kwargs):
    return _get_notable_field_test_status(
        [
            "energy_advisor",
            "assessment_report_received",
            "water_heater_fuel_type",
            "space_heat_fuel_type",
            "date_reservation_sent",
            "date_review_started",
            "date_comments_sent",
            "date_review_complete",
            "kwh_savings",  # 'enrolled' version, not 'installed'
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("incentive_reserved"))
def test_notable_fields_for_incentive_reserved(**kwargs):
    return _get_notable_field_test_status(
        [
            "date_reserved",
            "expected_construction_start_date",
            "expected_construction_completion_date",
            "total_incentive",  # 'enrolled' version, not 'installed'
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("verification"))
def test_notable_fields_for_verification(**kwargs):
    return _get_notable_field_test_status(
        [
            "trc_verifier",
            "verification_type",
            "verification_documents_received",
            "verification_performed",
            "verification_scheduled",
            "verification_complete",
            "kwh_savings_installed",
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("incentive_requested"))
def test_notable_fields_for_incentive_requested(**kwargs):
    return _get_notable_field_test_status(
        [
            "total_incentive_installed",
            "incentive_request_date",
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("complete"))
def test_notable_fields_for_complete(**kwargs):
    return _get_notable_field_test_status(
        [
            "incentive_delivered_date",
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("project_maintenance"))
def test_notable_fields_for_project_maintenance(**kwargs):
    return _get_notable_field_test_status([], **kwargs)


@register
@requirement_test("{state_name} Requirements", filter=is_state("dropped"))
def test_notable_fields_for_dropped(**kwargs):
    return _get_notable_field_test_status(
        [
            "dropped_date",
            "dropped_reason",
        ],
        **kwargs,
    )


@register
@requirement_test("{state_name} Requirements", filter=is_state("waitlist"))
def test_notable_fields_for_waitlist(**kwargs):
    return _get_notable_field_test_status(
        [
            "waitlist_date",
        ],
        **kwargs,
    )
