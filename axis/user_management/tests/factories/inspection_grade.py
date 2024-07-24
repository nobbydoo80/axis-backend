"""factory.py: Django inspecting grade factories"""


import logging
import random

from django.utils import timezone

from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import provider_user_factory
from axis.core.utils import random_sequence
from axis.user_management.models import InspectionGrade

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def inspection_grade_factory(**kwargs):
    suffix = kwargs.pop("suffix", random_sequence(4))
    user = kwargs.pop("user", provider_user_factory())
    company = kwargs.pop("company", provider_organization_factory())
    approver = kwargs.pop("approver", provider_user_factory(company=company))
    kwrgs = {
        "graded_date": timezone.now(),
        "letter_grade": random.choice(InspectionGrade.LETTER_GRADE_CHOICES)[0],
        "numeric_grade": random.randint(1, 99),
        "notes": "{}".format(suffix),
    }

    kwrgs.update(kwargs)

    accreditation = InspectionGrade.objects.create(user=user, approver=approver, **kwrgs)
    return accreditation
