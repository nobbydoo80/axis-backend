"""tasks.py: Django home"""


from importlib import import_module

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings

from django.contrib.auth import get_user_model
from axis.relationship.utils import get_companies_by_path
from .models import Message
from .messages import MESSAGE_REGISTRY
from .utils import (
    send_alert,
    send_read_receipts,
    get_digest_report,
    get_digest_email_obj,
    get_user_message_preference,
)

__author__ = "Autumn Valenta"
__date__ = "4/21/15 2:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Naruhito Kaide",
]

logger = get_task_logger(__name__)
User = get_user_model()


@shared_task(default_retry_delay=15, max_retries=5, ignore_result=True)
def deliver_message_to_own_websocket(message_id, session_key):
    # The message was originally dispatched via send_alert(), but this time it will be from the
    # machine that owns the live websocket connection, so calling send_alert() again will result in
    # delivery (as opposed to ``requeue_message_for_destination()`` -> back to here)
    from .models import Message

    log = logger

    try:
        retry = deliver_message_to_own_websocket.request.retries
        max_retries = deliver_message_to_own_websocket.max_retries
    except:
        retry = 0
        max_retries = 5

    try:
        message = Message.objects.get(id=message_id)
        user_preference = get_user_message_preference(
            message.user, message_name=message.modern_message
        )
        if user_preference.receive_notification:
            send_alert(message, session_key=session_key, only_mine=True)
    except Message.DoesNotExist as exc:
        msg = (
            "Session: %(session)r -  Message ID %(message_id)r "
            "does not exist retry %(retry)d/%(max_retries)d"
        )
        msg_data = {
            "message_id": message_id,
            "session_key": session_key,
            "retry": retry,
            "max_retries": max_retries,
        }
        exc_info = True if retry > 3 else False
        log.error(msg, msg_data, exc_info=exc_info)
        return deliver_message_to_own_websocket.retry(exc=exc)


@shared_task(ignore_result=True)
def deliver_own_read_receipts(message_ids, session_key):
    id_list = list(Message.objects.filter(id__in=message_ids).values_list("id", flat=True))
    send_read_receipts(id_list, session_key=session_key)


@shared_task
def send_digest_email(**kwargs):
    """
    NOTE:  The crontab is set to run at 12:15 am.

    :param kwargs:
    :return:
    """
    log = kwargs.get("log", logger)

    user_reports, start, end = get_digest_report()

    if settings.SERVER_TYPE not in [
        settings.PRODUCTION_SERVER_TYPE,
        settings.LOCALHOST_SERVER_TYPE,
    ]:
        log.warning("Refusing to send digest email for SERVER_TYPE %s", settings.SERVER_TYPE)
        return

    for user_id in user_reports:
        report = user_reports[user_id]
        if (
            report.get("count", 0) == 0
            or report.get("threshold_display", "Unsubscribed") == "Unsubscribed"
        ):
            continue
        user = User.objects.get(id=user_id)
        email = get_digest_email_obj(user, report, start, end)
        email.send()


@shared_task(ignore_result=True)
def queue_state_machine_message(state, state_id, instance_id, content_type_id, message_config):
    from django.contrib.contenttypes.models import ContentType

    try:
        instance_type = ContentType.objects.get(id=content_type_id).model_class()
    except ContentType.DoesNotExist:
        return

    try:
        instance = instance_type.objects.get(id=instance_id)
    except instance_type.DoesNotExist:
        return

    if instance.state != state or (state_id and instance.state_history.last().id != state_id):
        return

    companies = get_companies_by_path(instance, message_config["recipients"])

    context = {
        "state": instance.get_state_display(),
        "instance_type": instance_type._meta.verbose_name,
        "instance": "{}".format(instance),
        "instance_url": message_config.get("instance_url", False) or instance.get_absolute_url(),
        "countdown": message_config["countdown_pretty"],
    }

    for company in companies:
        message_obj = MESSAGE_REGISTRY[message_config["message"]]()
        message_obj(url=instance.get_absolute_url()).send(context=context, company=company)

        if message_config.get("nag", False):
            message_args = (state, instance_id, instance._meta.model, message_config)
            queue_state_machine_message.apply_async(
                args=message_args, countdown=message_config["countdown"]
            )
