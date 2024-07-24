"""test_factories.py: Django """

import logging
import os

from django.test import TestCase

from .factories import simulation_factory

__author__ = "Steven Klass"
__date__ = "11/21/18 12:37 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

BLG_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "remrate", "tests/sources", "ALL_FIELDS_SET_15.7.blg"
    )
)


class FactoriesTests(TestCase):
    def test_16p1(self):
        sim = simulation_factory(
            version="16.1.1",
            dehumidifier_count=1,
            mechanical_ventilation_count=1,
            ground_source_heat_pump_count=1,
            shared_equipment_count=1,
            shared_equipment__type=3,
        )
        self.assertEqual(sim.ventilation_set.count(), 1)
        self.assertEqual(sim.dehumidifier_set.count(), 1)
        self.assertEqual(sim.groundsourceheatpump_set.count(), 1)
        self.assertEqual(sim.sharedequipment_set.count(), 1)
        self.assertEqual(sim.waterloopheatpump_set.count(), 1)
        self.assertIsNotNone(sim.lightsandappliance.dishwasher_gas_cost)
