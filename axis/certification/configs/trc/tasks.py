from celery import shared_task
from celery.utils.log import get_task_logger

__author__ = "Autumn Valenta"
__date__ = "12/12/17 4:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = get_task_logger(__name__)


@shared_task(time_limit=60 * 5)
def issue_reminder_notifications():
    from .utils import issue_reminder_notifications

    issue_reminder_notifications()
