"""test_models.py: Django customer_aps"""


import logging
import datetime
from axis.core.tests.testcases import AxisTestCase
from axis.customer_aps.models import APSHome
from axis.customer_aps.tests.factories import apshome_factory
from axis.customer_aps.tests.mixins import CustomerAPSModelTestMixin
from axis.home.strings import NOT_ELIGIBLE_FOR_CERTIFICATION
from axis.messaging.models import Message
from axis.eep_program.models import EEPProgram
from axis.home.forms import HomeCertifyForm
from axis.home.models import EEPProgramHomeStatus

__author__ = "Steven Klass"
__date__ = "4/14/14 2:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CustomerAPSIncentiveModelTests(CustomerAPSModelTestMixin, AxisTestCase):
    def test_meterset_match_no_update_program(self):
        """Test that the EEP Program updates and messages are sent"""
        stat = EEPProgramHomeStatus.objects.get()

        self.assertEqual(stat.eep_program.slug, "aps-energy-star-v3-2018")
        self.assertEqual(APSHome.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 0)
        aps_home = apshome_factory(
            **{
                "premise_id": "138521283",
                "meterset_date": datetime.datetime(2016, 1, 1),
                "raw_lot_number": None,
                "raw_street_number": "124",
                "raw_prefix": "E",
                "raw_street_name": "OLIVE",
                "raw_suffix": "AVE",
                "raw_street_line_2": None,
                "raw_city": "GILBERT",
                "raw_state": "AZ",
                "raw_zip": "85234",
                "geocode": True,
            }
        )

        self.assertEqual(aps_home.confirmed_address, True)
        self.assertEqual(APSHome.objects.count(), 1)
        self.assertIsNone(aps_home.home)

        stat.home.save()

        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertIsNotNone(stat.home.apshome)
        self.assertEqual(APSHome.objects.count(), 1)
        self.assertEqual(stat.eep_program.slug, "aps-energy-star-v3-2018")

    def test_certification_check_fail_program_on_cert_form(self):
        stat = EEPProgramHomeStatus.objects.get()
        stat.eep_program = EEPProgram.objects.get(slug="aps-energy-star-v3-hers-60-2018")
        stat.save()

        user = self.user_model.objects.get(company__slug=stat.company.slug)
        data = {"certification_date": datetime.date(2017, 12, 1)}
        form = HomeCertifyForm(user=user, data=data, instance=stat)
        self.assertEqual(form.is_valid(), False)

        msg = NOT_ELIGIBLE_FOR_CERTIFICATION.format(
            url=stat.home.get_absolute_url(), home=stat.home, program=stat.eep_program
        )
        self.assertIn(msg, form.errors["__all__"][0])
