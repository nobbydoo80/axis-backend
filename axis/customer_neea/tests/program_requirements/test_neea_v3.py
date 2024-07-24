"""test_neea_v3.py - Axis"""

__author__ = "Steven K"
__date__ = "7/20/21 08:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
from unittest.mock import patch

from axis.checklist.tests.mixins import CollectedInputMixin
from axis.core.tests.testcases import AxisTestCase
from axis.home.models import EEPProgramHomeStatus
from ..mixins import NEEAV3ProgramTestMixin
from ...rtf_calculator.calculator import NEEAV3Calculator
from ...rtf_calculator.constants.neea_v3 import (
    REFRIGERATOR_BOTTOM_FREEZER_LABEL,
    CLOTHES_WASHER_SIDE_LABEL,
)
from ...strings import NEEA_BPA_2021_CHECKSUMS

log = logging.getLogger(__name__)


def get_completion_requirements(self):
    return [
        self.eep_program.get_std_protocol_percent_improvement_status,
        self.eep_program.get_neea_invalid_program_status,
        self.eep_program.get_simulation_flavor_status,
        self.eep_program.get_min_max_simulation_version,
        self.eep_program.get_water_heater_status,
        self.eep_program.get_duct_system_test_status,
        self.eep_program.get_ventilation_type_status,
        self.eep_program.get_neea_checklist_type_matches_remrate_status,
        self.eep_program.get_neea_checklist_water_heater_matches_remrate_status,
        self.eep_program.get_neea_v3_refrigerator_installed_status,
        self.eep_program.get_neea_v3_clothes_washer_installed_status,
        self.eep_program.get_neea_bpa_clothes_dryer_installed_status,
        self.eep_program.get_neea_bpa_dishwasher_installed_status,
        self.eep_program.get_neea_bpa_checklist_smart_thermostat_installed_status,
        self.eep_program.get_simulation_udrh_check,
        self.eep_program.get_neea_v3_availability_check,
        self.get_std_protocol_penn_power,
    ]


class NEEAV3ProgramChecksCounts(NEEAV3ProgramTestMixin, AxisTestCase):
    def test_completion_requirement_counts(self):
        """Make sure that we have counts that match"""
        self.home_status = EEPProgramHomeStatus.objects.get()
        self.assertEqual(self.home_status.eep_program.slug, "neea-bpa-v3")
        checks = self.home_status.get_progress_analysis()
        self.assertTrue(checks["status"])
        original = list(checks.get("requirements").keys())

        # Known to not need testing
        original = [
            test
            for test in original
            if test
            not in [
                "required_questions_remaining",
                "utility_required",
                "program_owner_attached",
                "required_annotations",
                "rater_required",
                "optional_questions_remaining",
                "multiple_utility_check",
                "model_data",
            ]
        ]

        method_to_patch = "axis.home.models.EEPProgramHomeStatus.get_completion_requirements"
        self.patcher = patch(method_to_patch, get_completion_requirements)
        self.patcher.start()
        self.home_status = EEPProgramHomeStatus.objects.get()
        checks = self.home_status.get_progress_analysis()
        self.assertTrue(checks["status"])
        patched_checks = checks.get("requirements").keys()
        self.patcher.stop()

        # Make sure we aren't missing anything here
        self.assertEqual(set(original), set(patched_checks))


class NEEAV3ProgramChecks(NEEAV3ProgramTestMixin, AxisTestCase, CollectedInputMixin):
    """These test out the big differences between V2/V3"""

    def setUp(self):
        method_to_patch = "axis.home.models.EEPProgramHomeStatus.get_completion_requirements"
        self.patcher = patch(method_to_patch, get_completion_requirements)
        self.mock_foo = self.patcher.start()
        self.addCleanup(self.patcher.stop)

        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        if missing_checks:
            print(
                "Failing Certification Eligibility Requirements:\n  - "
                + "\n  - ".join(missing_checks)
            )
        self.assertEqual(len(missing_checks), 0)
        self.simulation = self.home_status.floorplan.simulation
        self.rem_simulation = self.home_status.floorplan.remrate_target
        self.assertEqual(self.home_status.eep_program.slug, "neea-bpa-v3")

    def test_get_std_protocol_percent_improvement_status(self):
        """Verify we flag on a bad % improvement"""

        answer_data = dict(self.home_status.annotations.all().values_list("type__slug", "content"))
        answer_data = {k.replace("-", "_"): v for k, v in answer_data.items()}

        input_values = self.home_status.get_input_values(user_role="rater")
        input_answers = {
            measure.replace("neea-", ""): value for measure, value in input_values.items()
        }

        answer_data.update(input_answers)
        calculator = NEEAV3Calculator(home_status_id=self.home_status.id, **answer_data)
        calculator.result_data()

        self.assertEqual(self.home_status.standardprotocolcalculator_set.count(), 1)

        self.home_status.standardprotocolcalculator_set.update(revised_percent_improvement=0.09)
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Project total improvement must be at least 10%", missing_checks[0])

    def test_get_neea_invalid_program_status(self):
        """Verify multi-family"""
        home = self.home_status.home
        home.is_multi_family = True
        home.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("This program is available only for single-family", missing_checks[0])

    def test_get_simulation_flavor_status(self):
        """Verify the simulation flavor"""
        self.simulation.flavor = "FOO"
        self.simulation.save()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("only allows rating data from the following flavors", missing_checks[0])

    def test_get_simulation_version_status(self):
        """Verify the version of the simulation"""
        self.simulation.version = "15.7.3"
        self.simulation.save()
        self.home_status.refresh_from_db()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Simulation data must be REM == 16.0.6", missing_checks[0])

    def test_get_simulation_udrh_check_checksum(self):
        """Completely wrong checksum"""

        # Wrong checksum
        self.simulation.analyses.update(source_qualifier="FOOBAR")
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated", missing_checks[0])

    def test_get_simulation_udrh_check_filename(self):
        """Completely wrong Filename"""

        # Bad File
        self.simulation.analyses.update(source_name="FOOBAR")
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated", missing_checks[0])
        self.assertIn("verified via checksum", missing_checks[0])

    def test_get_simulation_udrh_check_combo(self):
        """Completely both legit just not aligned"""

        # General Mismatch
        self.simulation.analyses.update(
            source_qualifier=NEEA_BPA_2021_CHECKSUMS[0][0],
            source_name=NEEA_BPA_2021_CHECKSUMS[1][1],
        )
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH checksum associated with", missing_checks[0])

    def test_get_neea_v3_refrigerator_installed_status(self):
        """Test clothes washer required"""
        self.add_collected_input(
            self.home_status, "neea_refrigerators_installed", REFRIGERATOR_BOTTOM_FREEZER_LABEL
        )
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Brand & Model Number are required", missing_checks[0])

    def test_get_neea_v3_clothes_washer_installed_status(self):
        """Test clothes washer required"""
        self.add_collected_input(
            self.home_status, "neea_clothes_washer_installed", CLOTHES_WASHER_SIDE_LABEL
        )
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Brand & Model Number are required", missing_checks[0])
