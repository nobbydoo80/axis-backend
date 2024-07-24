"""factory.py: Django accreditation factories"""


import logging
import random

from django.utils import timezone

from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import provider_user_factory
from axis.core.utils import random_sequence
from axis.user_management.models import Accreditation

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def accreditation_factory(**kwargs):
    suffix = kwargs.pop("suffix", random_sequence(4))
    trainee = kwargs.pop("trainee", None)
    if not trainee:
        trainee = provider_user_factory()
    company = kwargs.pop("company", None)
    if not company:
        company = provider_organization_factory()
    approver = kwargs.pop("approver", None)
    if not approver:
        approver = provider_user_factory(company=company)
    kwrgs = {
        "name": random.choice(Accreditation.NAME_CHOICES)[0],
        "accreditation_id": "{}".format(suffix),
        "role": random.choice(Accreditation.ROLE_CHOICES)[0],
        "state": random.choice(Accreditation.STATE_CHOICES)[0],
        "state_changed_at": timezone.now(),
        "accreditation_cycle": random.choice(Accreditation.ACCREDITATION_CYCLE_CHOICES)[0],
        "date_initial": None,
        "date_last": None,
        "notes": "{}".format(suffix),
    }

    kwrgs.update(kwargs)

    accreditation = Accreditation.objects.create(trainee=trainee, approver=approver, **kwrgs)
    return accreditation
