"""signals.py: Django checklist"""


import logging
from .models import Answer

from django.db.models.signals import post_save

__author__ = "Steven Klass"
__date__ = "10/18/18 10:28 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")
    post_save.connect(conflicting_answer_check, sender=Answer)


def conflicting_answer_check(sender, instance, raw=False, **kwargs):
    # Failing answers require no scrutiny.  Let it through.
    if raw or instance.is_considered_failure:
        return

    conflicting_instances = Answer.objects.filter(
        home=instance.home,
        system_no=instance.system_no,
        question=instance.question,
        user__company=instance.user.company,
        is_considered_failure=False,
    ).exclude(pk=instance.pk)

    if conflicting_instances.count():
        conflicting_ids = list(conflicting_instances.values_list("pk", flat=True))
        for aid in conflicting_ids:
            a = conflicting_instances.get(pk=aid)
            if "{}".format(a.answer) != "{}".format(instance.answer):
                log.info(
                    "Removing prior answer %s [%s] for updated %s - %s",
                    a.answer,
                    aid,
                    instance.answer,
                    kwargs,
                )
        try:
            conflicting_instances.delete()
        except Answer.DoesNotExist:
            log.exception("Unable to delete %d conflicting answers" % conflicting_instances.count())
