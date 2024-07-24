"""tests_core.py: Django RESO.tests"""


import logging
from django.test import TestCase

from axis.reso.RESO import RESOUnsupportedException
from axis.reso.RESO.data_models.input_model import InputModel
from axis.reso.RESO.reso import RESO

__author__ = "Steven Klass"
__date__ = "6/16/17 11:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FakeHomeStatus(object):
    @property
    def home(self):
        class Home(object):
            latitude = 1.123
            longitude = 2.321

        return Home


_hs = FakeHomeStatus()
DefaultDataDict = {
    "latitude": _hs.home.latitude,
    "longitude": _hs.home.longitude,
}


class RESOCoreTests(TestCase):
    def Xtest_supported_reso(self):
        """Normal configurations"""
        reso = RESO(home_status=FakeHomeStatus)
        self.assertEqual(reso.input_data.__class__.__name__, "HomeStatusModel")
        self.assertEqual(reso.data_model.__class__.__name__, "RESO1p4Json")
        reso = RESO(home_status=FakeHomeStatus, output_type="edmx")
        self.assertEqual(reso.input_data.__class__.__name__, "HomeStatusModel")
        self.assertEqual(reso.data_model.__class__.__name__, "RESO1p4EDMX")

        reso = RESO(home_status=DefaultDataDict)
        self.assertEqual(reso.input_data.__class__.__name__, "InputModel")
        self.assertEqual(reso.data_model.__class__.__name__, "RESO1p4Json")
        reso = RESO(home_status=DefaultDataDict, output_type="edmx")
        self.assertEqual(reso.input_data.__class__.__name__, "InputModel")
        self.assertEqual(reso.data_model.__class__.__name__, "RESO1p4EDMX")

    def Xtest_supported_rets(self):
        reso = RESO(home_status=FakeHomeStatus, data_flavor="rets", output_type="xml")
        self.assertEqual(reso.input_data.__class__.__name__, "HomeStatusModel")
        self.assertEqual(reso.data_model.__class__.__name__, "RETS1p8XML")
        reso = RESO(home_status=DefaultDataDict, data_flavor="rets", output_type="xml")
        self.assertEqual(reso.input_data.__class__.__name__, "InputModel")
        self.assertEqual(reso.data_model.__class__.__name__, "RETS1p8XML")

    def Xtest_unsupported_reso_version(self):
        self.assertRaises(
            RESOUnsupportedException, RESO, home_status=DefaultDataDict, reso_version="1.3333"
        )

    def Xtest_unsupported_rets_version(self):
        self.assertRaises(
            RESOUnsupportedException,
            RESO,
            home_status=DefaultDataDict,
            data_flavor="rets",
            rets_version="1.3333",
        )


class RESOCoreInputModelTests(TestCase):
    def test_supported_dict_model(self):
        InputModel(**DefaultDataDict)

    def test_supported_hs_model(self):
        InputModel(home_status=FakeHomeStatus)

    def test_attr_grabbing(self):
        model = InputModel(**DefaultDataDict)
        self.assertEqual(model.longitude, DefaultDataDict.get("longitude"))

    def test_attr_rounding(self):
        model = InputModel(**DefaultDataDict)
        self.assertEqual(model.round__longitude, round(DefaultDataDict.get("longitude"), 0))
        self.assertEqual(model.round1__longitude, round(DefaultDataDict.get("longitude"), 1))
        self.assertEqual(model.round2__longitude, round(DefaultDataDict.get("longitude"), 2))

    def test_attr_pct(self):
        model = InputModel(**DefaultDataDict)
        self.assertEqual(model.roundp__longitude, "232.100000%")

    def test_hs_override(self):
        model = InputModel(home_status=FakeHomeStatus, latitude=9.0)
        self.assertEqual(model.latitude, 9.0)


class RESOEDMXTests(TestCase):
    def Xtest_basic(self):
        reso = RESO(home_status=DefaultDataDict, output_type="edmx")
        reso.pprint()


class RESOListingTests(TestCase):
    pass
