import logging
import os
import sys
from collections import OrderedDict
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum

from axis.core.utils import values_to_dict, alias_valuesqueryset
from axis.messaging.tasks import queue_state_machine_message
from .state_messages import messages

ROOT = os.path.abspath(__file__ + "../../../../")
if ROOT not in sys.path:
    sys.path.append(ROOT)


__author__ = "Michael Jeffrey"
__date__ = "8/17/15 3:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


log = logging.getLogger(__name__)


def qa_state_change_handler(instance):
    # FIXME: This assumes contentobject is a homestatus (maybe fixed?)
    program = instance.requirement.eep_program.slug
    # program = instance.home_status.eep_program.slug
    state = instance.state
    state_id = getattr(instance.state_history.last(), "id", None)

    try:
        message_config = messages[program][(state, instance.requirement.type)]
    except KeyError:
        return
    else:
        content_type_id = ContentType.objects.get_for_model(instance._meta.model).id
        message_config["instance_url"] = instance.get_parent().get_absolute_url() + "#/tabs/qa"
        message_args = (state, state_id, instance.id, content_type_id, message_config)
        queue_state_machine_message.apply_async(
            args=message_args, countdown=message_config["countdown"]
        )


def _group_by_counter(
    queryset,
    counter,
    aliases,
    group_key_path,
    group_key,
    counter_name="n",
    pop=False,
    value_as_list=True,
):
    aliases[group_key_path] = group_key
    values_qs = queryset.values(counter, *aliases.keys()).annotate(**{counter_name: Count(counter)})
    values_qs = alias_valuesqueryset(values_qs, pop=pop, **aliases)
    breakdowns = values_to_dict(values_qs, key=group_key, value_as_list=value_as_list)
    return breakdowns


def _get_success_rates(
    qastatus_queryset,
    counter,
    aliases,
    group_key_path,
    group_key,
    counter_name="n",
    pop=False,
    value_as_list=True,
):
    breakdowns = _group_by_counter(
        qastatus_queryset,
        counter,
        aliases,
        group_key_path,
        group_key,
        pop=pop,
        value_as_list=value_as_list,
    )
    for group_value, data in breakdowns.items():
        if len(data) == 1:
            # All failures or all successes.  Need to generated a dummy entry for whatever's missing
            filler = dict(
                data[0],
                **{
                    counter_name: 0,  # none were found, so we're adding that info
                    "has_failed": not (data[0][counter]),
                },
            )
            data.append(filler)

        data.sort(key=lambda o: o[counter])

        success_data, failure_data = data
        total = success_data[counter_name] + failure_data[counter_name]
        success_data["percentage"] = round(100.0 * success_data[counter_name] / total, 2)

        # Extra success stats
        corrected = qastatus_queryset.filter(
            state__in=["correction_received", "complete"],
            has_failed=True,
            **{group_key_path: group_value},
        ).count()
        success_data["total"] = total
        success_data["corrected"] = corrected
        if failure_data[counter_name] > 0:
            relative_percentage = round(100.0 * corrected / failure_data[counter_name], 2)
        else:
            relative_percentage = 0.0
        success_data["relative_corrected_percentage"] = relative_percentage
        success_data["corrected_percentage"] = round(100.0 * corrected / total, 2) - 0.01  # css %
        failure_data["percentage"] = round(
            100.0 * (failure_data[counter_name] - corrected) / total, 2
        )

    breakdowns = sorted(breakdowns.values(), key=lambda o: o[0]["percentage"])
    return breakdowns


def get_program_summaries(
    homestatus_queryset,
    not_received_kwargs=None,
    ipp_payments_kwargs=None,
    energy_savings_kwargs=None,
):
    lookups = {
        "homestatus": "state",
        "qastatus": "qastatus__state",
        "incentivepaymentstatus": "incentivepaymentstatus__state",
    }
    filters = {"qastatus": {"qastatus__requirement__type": "file"}}

    result = OrderedDict()
    homestatus_queryset = homestatus_queryset.order_by("eep_program__name")
    for grouping_name, grouping_column in lookups.items():
        qs = homestatus_queryset.filter(**filters.get(grouping_name, {}))
        breakdown = _group_by_counter(
            qs,
            grouping_column,
            {
                "eep_program__name": "eep_program",
                "eep_program__builder_incentive_dollar_value": "builder_incentive",
                "eep_program__rater_incentive_dollar_value": "rater_incentive",
            },
            "eep_program__id",
            "eep_program_id",
            counter_name=grouping_name,
        )

        for program_id, data in breakdown.items():
            for item in data:
                composite_item = result.get(program_id, None)
                if composite_item is None:
                    composite_item = item
                    composite_item.setdefault(
                        "stats",
                        dict(
                            {
                                l: {"not_complete": 0, "outstanding_payment": Decimal(0.0)}
                                for l in lookups.keys()
                            }
                        ),
                    )
                    result[program_id] = composite_item

                grouped_value = item.pop(lookups[grouping_name])
                grouped_count = item.pop(grouping_name)
                composite_item["stats"][grouping_name][grouped_value] = grouped_count

                # Tally up the 'Not Certified' / 'Not Complete' / 'Not Paid'
                if grouped_value != "complete":
                    composite_item["stats"][grouping_name]["not_complete"] += grouped_count

                    # Payments due
                    outstanding = Decimal(0.0)
                    _company_type = None
                    if ipp_payments_kwargs is not None:
                        _company_type = ipp_payments_kwargs.get(
                            "ippitem__incentive_distribution__customer__company_type"
                        )
                    if _company_type is None or _company_type == "builder":
                        outstanding += grouped_count * item.get("builder_incentive", 0)
                    if _company_type is None or _company_type in ["rater", "provider"]:
                        outstanding += grouped_count * item.get("rater_incentive", 0)
                    composite_item["stats"][grouping_name]["outstanding_payment"] += outstanding

    # Amend results with extra calculation
    # "Not Received" IPP virtual state
    not_received_kwargs = not_received_kwargs or {}
    not_received_qs = homestatus_queryset.filter(
        incentivepaymentstatus__isnull=True, **not_received_kwargs
    )
    breakdown = _group_by_counter(
        not_received_qs,
        "eep_program__name",
        {},
        "eep_program__id",
        "eep_program_id",
        value_as_list=False,
    )
    for program_id, data in breakdown.items():
        result[program_id]["stats"]["incentivepaymentstatus"]["not_received"] = data["n"]

    # Count certifications
    values_qs = get_certification_metrics_by_program(homestatus_queryset)
    for item in values_qs:
        result[item["eep_program_id"]]["certifications"] = item["n"]

    # Aggregate sum of verified ipp payments
    ipp_payments_kwargs = ipp_payments_kwargs or {}
    breakdown = (
        homestatus_queryset.filter(
            ippitem__incentive_distribution__is_paid=True, **ipp_payments_kwargs
        )
        .values("eep_program__name", "eep_program__id")
        .annotate(n=Sum("ippitem__cost"))
    )
    for item in breakdown:
        result[item["eep_program__id"]]["incentives_paid"] = "{:,f}".format(item["n"])
        result[item["eep_program__id"]]["incentives_paid_raw"] = item["n"]

    # Aggregate sum of energy savings
    energy_savings_kwargs = energy_savings_kwargs or {}
    breakdown = (
        homestatus_queryset.filter(certification_date__isnull=False, **energy_savings_kwargs)
        .values("eep_program__name", "eep_program__id")
        .annotate(n=Sum("fasttracksubmission__mbtu_savings"))
    )
    for item in breakdown:
        n = item["n"] if item["n"] else 0
        result[item["eep_program__id"]]["energy_savings"] = "{:,f}".format(n)
        result[item["eep_program__id"]]["energy_savings_raw"] = n

    return list(result.values())


def get_success_rates_by_program(qastatus_queryset):
    return _get_success_rates(
        qastatus_queryset,
        "has_failed",
        {
            "home_status__eep_program__name": "eep_program",
        },
        "home_status__eep_program__id",
        "eep_program_id",
    )


def get_success_rates_by_rater_company(qastatus_queryset):
    return _get_success_rates(
        qastatus_queryset,
        "has_failed",
        {
            "home_status__company__name": "company",
        },
        "home_status__company__id",
        "company_id",
    )


def get_success_rates_by_rater_user(qastatus_queryset):
    return _get_success_rates(
        qastatus_queryset,
        "has_failed",
        {
            "home_status__rater_of_record__first_name": "ror_first_name",
            "home_status__rater_of_record__last_name": "ror_last_name",
        },
        "home_status__rater_of_record__id",
        "ror_id",
    )


def get_certification_metrics_by_program(homestatus_queryset):
    values_qs = (
        homestatus_queryset.exclude(certification_date=None)
        .values("eep_program__name", "eep_program_id")
        .annotate(n=Count("certification_date"))
    )
    values_qs = alias_valuesqueryset(
        values_qs,
        **{
            "eep_program__name": "eep_program",
        },
    )
    return values_qs


def get_frequent_observations(qastatus_queryset):
    # TODO: Narrow to date range?  Not sure if looking at active homestatuses is good enough.

    queryset = qastatus_queryset.exclude(
        qa_status__home_status__state__in=("complete", "abandoned")
    )

    # Generate a GROUPBY style query where we're counting the occurences of each type
    queryset = queryset.values("observation_type__name").annotate(
        frequency=Count("observation_type")
    )
    return queryset.order_by("-frequency")


def get_recent_observations(qastatus_queryset):
    return qastatus_queryset.order_by("-created_on")


def add_program_review_qa_to_programs():
    from axis.eep_program.models import EEPProgram
    from axis.company.models import Company
    from axis.qa.models import QARequirement

    company_slugs = (
        "provider-building-energy-inc",
        "provider-building-efficiency-resources",
        "efl",
        "provider-national-center-for-appropriate-technolog",
        "provider-wsu",
    )

    program_slugs = (
        "neea-energy-star-v3-performance",
        "neea-energy-star-v3",
        "neea-prescriptive-2015",
        "neea-performance-2015",
        "neea-efficient-homes",
    )

    companies = Company.objects.filter(slug__in=company_slugs)
    programs = EEPProgram.objects.filter(slug__in=program_slugs)
    defaults = {"gate_certification": True, "coverage_pct": 0}

    for program in programs:
        for company in companies:
            model, created = QARequirement.objects.get_or_create(
                qa_company=company, eep_program=program, type="program_review", defaults=defaults
            )
            if not created:
                save = False
                for k, v in defaults.items():
                    if not getattr(model, k) == v:
                        setattr(model, k, v)
                        save = True
                if save:
                    model.save()


def get_content_object_data_for_qa_messages(qastatus):
    if qastatus.home_status:
        obj_repr = qastatus.home_status.home.get_addr()
        obj_type = "home"  # users interact with homestatus as part of the home
        url = qastatus.home_status.home.get_absolute_url()
    elif qastatus.subdivision:
        obj_repr = "{}".format(qastatus.subdivision)
        obj_type = "subdivision"
        url = qastatus.subdivision.get_absolute_url()

    home_status = qastatus.get_home_status()
    return {
        "obj": qastatus.get_parent(),
        "obj_repr": obj_repr,
        "obj_type": obj_type,
        "provider": home_status.get_provider(),
        "rater": home_status.company,
        "company": home_status.company,
        "owner": qastatus.owner,
        "url": url,
    }


def get_qa_message_context(qa_status, qa_status_data):
    """
    :param qa_status: QAStatus instance
    :param qa_status_data: dict from get_content_object_data_for_qa_messages()
    :return: context dict
    """
    return {
        "qa_company": "{}".format(qa_status.owner),
        "company": qa_status_data["company"],
        "obj_type": qa_status_data["obj_type"],
        "obj_edit": qa_status_data["url"],
        "obj": qa_status_data["obj_repr"],
        "action_url": qa_status_data["url"] + "#/tabs/qa",
        "type": qa_status.requirement.type,
        "qa_notes": qa_status.qanote_set.all().order_by("-created_on"),
    }


def main(args):
    """Main Program -Create the NEEA 2015 programs

    :param args: argparse.Namespace
    """
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(filename)s] (%(name)s) %(message)s",
    )

    args.verbose = 4 if args.verbose > 4 else args.verbose
    loglevel = 50 - args.verbose * 10
    log.setLevel(loglevel)
    add_program_review_qa_to_programs()


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Add Program Review for companies")
    parser.add_argument(
        "-v",
        "--verbose",
        const=1,
        default=1,
        type=int,
        nargs="?",
        help="increase verbosity: 1=errors, 2=warnings, 3=info, 4=debug. "
        "No number means warning. Default is no verbosity.",
    )
    sys.exit(main(parser.parse_args()))
