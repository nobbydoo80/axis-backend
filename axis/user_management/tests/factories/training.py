"""factory.py: Django training factories"""


import logging
import random

from django.utils import timezone

from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import provider_user_factory
from axis.core.utils import random_sequence
from axis.user_management.models import Training, TrainingStatus
from axis.user_management.states import TrainingStatusStates

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def training_factory(**kwargs):
    suffix = kwargs.pop("suffix", random_sequence(4))
    trainee = kwargs.pop("trainee", provider_user_factory())
    kwrgs = {
        "name": "{}".format(suffix),
        "address": "{}".format(suffix),
        "training_date": timezone.now().date(),
        "training_type": random.choice(Training.TRAINING_TYPE_CHOICES)[0],
        "attendance_type": random.choice(Training.ATTENDANCE_TYPE_CHOICES)[0],
        "credit_hours": random.randint(0, 10),
        "notes": "{}".format(suffix),
    }

    kwrgs.update(kwargs)

    training = Training.objects.create(trainee=trainee, **kwrgs)
    return training


def training_status_factory(**kwargs):
    training = kwargs.pop("training")
    company = kwargs.pop("company", provider_organization_factory())
    approver = kwargs.pop("approver", provider_user_factory(company=company))
    kwrgs = {"state_changed_at": timezone.now(), "state": TrainingStatusStates.NEW}

    kwrgs.update(kwargs)
    training_status = TrainingStatus.objects.create(
        training=training, company=company, approver=approver, **kwrgs
    )
    return training_status
