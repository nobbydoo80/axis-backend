__author__ = "Steven Klass"
__date__ = "1/9/13 2:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import management
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django_celery_results.models import TaskResult
from simple_history import models as simple_history_models
from simple_history import utils as simple_history_utils
from simple_history.exceptions import NotHistoricalModelError

logger = get_task_logger(__name__)
User = get_user_model()


@shared_task(ignore_result=True, store_errors_even_if_ignored=True)
def update_user_groups(user_id) -> dict:
    """
    This updates a users groups to the groups of the company.
    :param user_id: axis.core.models.User id
    """
    log = logger
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return {"error": f"User with id {user_id} not found"}
    try:
        user.company
        group_ids = [user.company.group.id]
        if user.is_company_admin:
            group_ids.append(user.company.get_admin_group().id)
        expected_groups = Group.objects.filter(id__in=group_ids)
        current_groups = set(list(user.groups.values_list("id", flat=True)))
        if current_groups != set(list(expected_groups.values_list("id", flat=True))):
            log.debug(
                "Clearing perms for %s - adding %s fresh", user, expected_groups.all().count()
            )
            user.groups.clear()
            user.groups.add(*expected_groups)
        if len(user.get_all_permissions()) < 5:
            user.company.update_permissions()
    except (ObjectDoesNotExist, AttributeError):
        log.debug("Clearing perms - no company")
        user.groups.clear()
    return {"result": f"User {user} updated"}


@shared_task
def clear_expired_sessions() -> dict:
    """Crontab to clear expired sessions"""
    return {"result": management.call_command("clearsessions")}


@shared_task(time_limit=60 * 5)
def aggregate_metrics() -> dict:
    """Crontab to aggregate all metrics"""
    return {"result": management.call_command("metrics_aggregate")}


@shared_task
def cleanup_tasks() -> dict:
    """This cleans up old celery tasks"""
    expired = now() - datetime.timedelta(hours=24 * 180)
    expired_tasks = TaskResult.objects.filter(date_done__lt=expired)
    expired_tasks.delete()

    if expired_tasks:
        return {"result": f"Deleted {expired_tasks.count()} Tasks"}
    return {"result": "Nothing done"}


@shared_task(default_retry_delay=15, max_retries=5, time_limit=5)
def slack_message(url, data, headers, verify, timeout=60) -> dict:
    from infrastructure.utils.logging_utils.handlers.slack import dispatch_slack_message

    return {"result": dispatch_slack_message(url, data, headers, verify, timeout)}


@shared_task
def clean_all_duplicate_history_task():
    """
    Iterate over all registered models and run clean-duplicate-history management command as separate Celery task
    https://django-simple-history.readthedocs.io/en/latest/utils.html#clean-duplicate-history
    """
    for model in simple_history_models.registered_models.values():
        try:  # avoid issues with multi-table inheritance
            history_model = simple_history_utils.get_history_model_for_model(model)
        except NotHistoricalModelError:
            continue
        clean_duplicate_history_task.delay(
            model_from_natural_key=f"{model._meta.app_label}.{model._meta.object_name}"
        )


@shared_task(time_limit=60 * 5)
def clean_duplicate_history_task(model_from_natural_key: str):
    """
    Run clean-duplicate-history management command as Celery task
    :param model_from_natural_key: path for model in format "app_label.ModelName"
    """
    management.call_command(
        "clean_duplicate_history",
        model_from_natural_key,
        # common auto updated fields that we can ignore
        excluded_fields=["date_modified", "modified", "updated_at"],
    )
