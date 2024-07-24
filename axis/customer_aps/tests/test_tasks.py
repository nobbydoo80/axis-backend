"""test_tasks.py: """


from axis.core.tests.testcases import AxisTestCase
from axis.customer_aps.tests.factories import apshome_factory
from axis.home.models import Home, EEPProgramHomeStatus
from .mixins import CustomerAPS2019ModelTestMixin
from ..tasks import update_metersets_task


__author__ = "Artem Hruzd"
__date__ = "07/22/2019 18:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class APSTaskTests(CustomerAPS2019ModelTestMixin, AxisTestCase):
    def test_update_metersets_task(self):
        """Creating home and aps home with same address and match them with metersets task"""
        from axis.incentive_payment.tests.factories import (
            basic_incentive_payment_status_factory,
        )

        home = Home.objects.first()
        aps_home = apshome_factory(
            raw_street_line_1=home.geocode_response.geocode.raw_street_line1,
            raw_street_line_2=home.geocode_response.geocode.raw_street_line2,
            street_line1=home.street_line1,
            street_line2=home.street_line2,
            city=home.city,
            state=home.state,
            zipcode=home.zipcode,
        )
        eep_home_status = EEPProgramHomeStatus.objects.first()
        aps_home.geocode_response = home.geocode_response
        aps_home.save()
        basic_incentive_payment_status_factory(home_status=eep_home_status)

        update_metersets_task()
        aps_home.refresh_from_db()
        self.assertEqual(home, aps_home.home)
