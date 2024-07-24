"""accreditation.py: """


from dateutil.relativedelta import relativedelta
from django.utils import timezone

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.user_management.models import Accreditation
from ..mixins import AccreditationTestMixin

__author__ = "Artem Hruzd"
__date__ = "12/25/2019 18:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationModelTest(AccreditationTestMixin, AxisTestCase):
    client_class = AxisClient

    def test_is_expired(self):
        accreditation = Accreditation.objects.first()
        accreditation.date_last = None
        accreditation.accreditation_cycle = Accreditation.ANNUAL_ACCREDITATION_CYCLE
        accreditation.save()

        self.assertFalse(accreditation.is_expired())

        accreditation.date_last = timezone.now().date()
        accreditation.save()

        self.assertFalse(accreditation.is_expired())

        accreditation.date_last = timezone.now().date() - relativedelta(years=2)
        accreditation.save()

        self.assertTrue(accreditation.is_expired())

        with self.subTest("With manual override accreditation"):
            accreditation.manual_expiration_date = timezone.now().date() + timezone.timedelta(
                days=5
            )
            accreditation.save()

            self.assertFalse(accreditation.is_expired())

            accreditation.manual_expiration_date = timezone.now().date() - timezone.timedelta(
                days=5
            )

            self.assertTrue(accreditation.is_expired())
