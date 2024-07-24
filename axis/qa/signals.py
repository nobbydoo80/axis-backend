"""signals.py: Django qa"""


import logging

from django.conf import settings
from django.db.models.signals import post_save

from .models import QAStatus

__author__ = "Steven Klass"
__date__ = "1/17/17 10:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""
    # log.debug("Registering late signals.")

    post_save.connect(QAStatusStateUpdate, sender=QAStatus)

    from axis.home.models import EEPProgramHomeStatus

    post_save.connect(QANotifyOpportunities, sender=EEPProgramHomeStatus)
    post_save.connect(QAStatusStateUpdateFromEEPProgramHomeStatus, sender=EEPProgramHomeStatus)


def QANotifyOpportunities(sender, **kwargs):
    """This will send notification to any companies which need QA to happen"""
    from .tasks import update_notify_opportunities
    from .models import QARequirement

    home_status = kwargs.get("instance")
    if kwargs.get("raw", False):
        return
    qa_requirements = QARequirement.objects.filter_for_home_status(home_status)
    if qa_requirements.count():
        update_notify_opportunities.delay(home_status_id=home_status.id)


def QAStatusStateUpdate(sender, **kwargs):
    """Attempt to move the state of QA forward"""
    from .tasks import update_qa_states
    from axis.home.tasks import update_home_states

    qa_status = kwargs.get("instance")
    if kwargs.get("raw", False):
        return
    update_qa_states.delay(qa_status_id=qa_status.id)

    if getattr(qa_status, "home_status"):
        update_home_states(eepprogramhomestatus_id=qa_status.home_status.id)


def QAStatusStateUpdateFromEEPProgramHomeStatus(sender, **kwargs):
    """Attempt to move the state of QA forward based on a change in EEPProgramHomeStatus"""
    from .tasks import update_qa_states

    home_status = kwargs.get("instance")
    if kwargs.get("raw", False):
        return
    idx, task = 0, None
    for idx, qa_id in enumerate(list(home_status.qastatus_set.values_list("id", flat=True))):
        task = update_qa_states.delay(qa_status_id=qa_id)
    if idx:
        log.debug(
            "Called QAStatusStateUpdateFromEEPProgramHomeStatus updated %(count)d task " "%(task)s",
            {"count": idx, "task": task},
        )
