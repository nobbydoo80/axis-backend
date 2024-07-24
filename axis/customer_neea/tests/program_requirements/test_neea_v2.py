"""test_neea_v2.py - Axis"""

__author__ = "Steven K"
__date__ = "7/20/21 08:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from datetime import date
from unittest import mock
from unittest.mock import patch

from axis.checklist.tests.mixins import CollectedInputMixin
from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from axis.customer_neea.strings import NEEA_BPA_2019_CHECKSUMS
from axis.home.models import EEPProgramHomeStatus
from axis.remrate_data.tests.factories.air_source_heat_pump import air_source_heat_pump_factory
from ..mixins import NEEAV2ProgramTestMixin

log = logging.getLogger(__name__)


def get_completion_requirements(self):
    return [
        self.eep_program.get_std_protocol_percent_improvement_status,
        self.eep_program.get_neea_invalid_program_status,
        self.eep_program.get_remrate_flavor_status,
        self.eep_program.get_neea_bpa_remrate_version_status,
        self.eep_program.get_water_heater_status,
        self.eep_program.get_duct_system_test_status,
        self.eep_program.get_ventilation_type_status,
        self.eep_program.get_neea_checklist_type_matches_remrate_status,
        self.eep_program.get_neea_checklist_water_heater_matches_remrate_status,
        self.eep_program.get_neea_bpa_refrigerator_installed_status,
        self.eep_program.get_neea_bpa_clothes_washer_installed_status,
        self.eep_program.get_neea_bpa_clothes_dryer_installed_status,
        self.eep_program.get_neea_bpa_dishwasher_installed_status,
        self.eep_program.get_neea_bpa_checklist_smart_thermostat_installed_status,
        self.eep_program.get_remrate_udhr_check,
        self.get_std_protocol_penn_power,
    ]


class FakeDate(date):
    "A manipulable date replacement"

    def __new__(cls, *args, **kwargs):
        return date.__new__(date, *args, **kwargs)


class NEEAV2ProgramChecks(NEEAV2ProgramTestMixin, AxisTestCase, CollectedInputMixin):
    def setUp(self):
        method_to_patch = "axis.home.models.EEPProgramHomeStatus.get_completion_requirements"
        self.patcher = patch(method_to_patch, get_completion_requirements)
        self.mock_foo = self.patcher.start()
        self.addCleanup(self.patcher.stop)  # add this line
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        # if missing_checks:
        #     print("Failing Certification Eligibility Requirements:\n  - " + "\n  - ".join(missing_checks))
        # self.assertEqual(len(missing_checks), 0)
        self.simulation = self.home_status.floorplan.remrate_target

    @mock.patch("datetime.date", FakeDate)
    def test_get_neaa_bpa_min_program_version_15p7p1(self):
        self.simulation.version = "15.7.1"
        self.simulation.udrh_checksum = NEEA_BPA_2019_CHECKSUMS[0][0]
        self.simulation.udrh_filename = NEEA_BPA_2019_CHECKSUMS[0][1]

        FakeDate.today = classmethod(lambda cls: date(2019, 10, 2))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        FakeDate.today = classmethod(lambda cls: date(2019, 3, 1))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        FakeDate.today = classmethod(lambda cls: date(2019, 2, 28))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("rating data from REM/Rate\u2122 versions 15.3.", missing_checks[0])

    @mock.patch("datetime.date", FakeDate)
    def test_get_neaa_bpa_min_program_version_15p3(self):
        self.simulation.version = "15.3"

        FakeDate.today = classmethod(lambda cls: date(2019, 2, 1))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        FakeDate.today = classmethod(lambda cls: date(2019, 5, 1))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        FakeDate.today = classmethod(lambda cls: date(2019, 10, 2))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("rating data from REM/Rate\u2122 versions 15.7.1.", missing_checks[0])

    @mock.patch("datetime.date", FakeDate)
    def test_get_neaa_bpa_min_program_version_15p6(self):
        self.simulation.version = "15.6"

        FakeDate.today = classmethod(lambda cls: date(2019, 2, 1))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("rating data from REM/Rate\u2122 versions 15.3.", missing_checks[0])

        FakeDate.today = classmethod(lambda cls: date(2019, 5, 1))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn(
            "rating data from REM/Rate\u2122 versions 15.3 or 15.7.1.",
            missing_checks[0],
        )

        FakeDate.today = classmethod(lambda cls: date(2019, 10, 2))
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("rating data from REM/Rate\u2122 versions 15.7.1.", missing_checks[0])

    @mock.patch("datetime.date", FakeDate)
    def test_get_neaa_bpa_rem_udhr_check(self):
        self.simulation.version = "15.7.1"
        FakeDate.today = classmethod(lambda cls: date(2019, 3, 1))
        self.simulation.udrh_checksum = NEEA_BPA_2019_CHECKSUMS[0][0]
        self.simulation.udrh_filename = NEEA_BPA_2019_CHECKSUMS[0][1]

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

        self.simulation.udrh_filename = "FOOBAR"
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH File used", missing_checks[0])

        self.simulation.udrh_filename = NEEA_BPA_2019_CHECKSUMS[0][1]
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.simulation.udrh_checksum = "FOO"
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated with as built home", missing_checks[0])

    @mock.patch("datetime.date", FakeDate)
    def test_get_state_cerification_check(self):
        """Verify that we can certify a home ater the dates."""
        FakeDate.today = classmethod(lambda cls: date(2019, 3, 1))

        self.assertEqual(self.home_status.state, "inspection")
        self.assertEqual(self.simulation.version, "15.7.1")

        self.simulation.version = "15.3"
        self.simulation.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1, missing_checks)
        self.assertIn("rating data from REM/Rate\u2122 versions 15.7.1.", missing_checks[0])

        self.home_status.state = "certification_pending"
        self.assertEqual(self.home_status.state, "certification_pending")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    def test_get_std_protocol_pse_hp_water_heater_status(self):
        """Verify PSE Required checks all in when ready"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

        self.assertFalse(self.home_status.floorplan.remrate_target.has_heat_pump_water_heaters())

        utility = Company.objects.get(slug="pacific-power")
        utility.slug = "puget-sound-energy"
        utility.save()

        relations = self.home_status.home.relationships.values_list("company", flat=True)
        self.assertIn(utility.id, list(relations))

        simulation = self.home_status.floorplan.remrate_target
        simulation.hotwaterheater_set.update(type=4)

        self.home_status = EEPProgramHomeStatus.objects.get(pk=self.home_status.id)
        self.assertEqual(self.home_status.get_electric_company().slug, "puget-sound-energy")
        self.assertTrue(self.home_status.floorplan.remrate_target.has_heat_pump_water_heaters())

        self.add_collected_input(self.home_status, "neea-hpwh-contractor", "X")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1, missing_checks)
        self.assertIn("does not align with checklist answer", " ".join(missing_checks))

        simulation.hotwaterheater_set.update(type=4, fuel_type=4)
        self.add_collected_input(self.home_status, "neea-water_heater_tier", "HPWH Tier 2")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    def test_get_std_protocol_pse_gas_fails_status(self):
        """Verify PSE Required checks all in when ready"""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

        self.assertFalse(self.home_status.floorplan.remrate_target.has_heat_pump_water_heaters())

        utility = Company.objects.get(slug="nw-natural-gas")
        utility.slug = "puget-sound-energy"
        utility.save()

        relations = self.home_status.home.relationships.values_list("company", flat=True)
        self.assertIn(utility.id, list(relations))

        simulation = self.home_status.floorplan.remrate_target
        # Replace heater with and ASHP
        ashp = air_source_heat_pump_factory(simulation=simulation, _result_number=123)
        simulation.installedequipment_set.filter(heater__isnull=False).update(
            heater=None,
            _heater_number=None,
            air_source_heat_pump=ashp,
            _air_source_heat_pump_number=123,
            system_type=4,
        )

        self.home_status = EEPProgramHomeStatus.objects.get(pk=self.home_status.id)
        self.assertNotEqual(self.home_status.get_electric_company().slug, "puget-sound-energy")
        self.assertEqual(self.home_status.get_gas_company().slug, "puget-sound-energy")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

    def test_get_std_protocol_penn_power(self):
        """Test out the Penn Power requirement that a meter is attached."""
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)

        self.remove_collected_input(self.home_status, "neea-electric_meter_number")
        utility = Company.objects.get(slug="pacific-power")
        utility.slug = "utility-peninsula-power-light"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1, missing_checks)
        self.assertIn("Electric Meter number is required", " ".join(missing_checks))

        self.add_collected_input(self.home_status, "neea-electric_meter_number", "FOOBar")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0, missing_checks)
