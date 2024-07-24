"""test_program_builder.py - axis"""

__author__ = "Steven K"
__date__ = "4/23/22 15:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.core import management

from axis.company.tests.factories import (
    general_organization_factory,
)
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.core.tests.client import AxisClient
from axis.eep_program.models import EEPProgram

log = logging.getLogger(__name__)


class LegacyProgramBuilder(AxisTestCase):
    """Verify that we can build out these legacy programs."""

    client_class = AxisClient

    def _build_and_test(self, owner_slug: str, program_slug: str, is_qa: bool = False):
        company = general_organization_factory(slug=owner_slug)

        management.call_command(
            "build_program", "-p", program_slug, "-r", "qa" if is_qa else "rater", stdout=DevNull()
        )

        self.assertEqual(EEPProgram.objects.count(), 1)

        eep_program = EEPProgram.objects.get(is_qa_program=is_qa)
        self.assertEqual(eep_program.owner.id, company.id)
        self.assertEqual(eep_program.required_checklists.count(), 0)
        self.assertIsNotNone(eep_program.collection_request)

    def test_neea_energy_star_v3(self):
        self._build_and_test("neea", "neea-energy-star-v3")

    def test_neea_energy_star_v3_qa(self):
        self._build_and_test("neea", "neea-energy-star-v3-qa")

    def test_neea_energy_star_v3_performance(self):
        self._build_and_test("neea", "neea-energy-star-v3-performance")

    def test_neea_prescriptive_2015(self):
        self._build_and_test("neea", "neea-prescriptive-2015")

    def test_neea_performance_2015(self):
        self._build_and_test("neea", "neea-performance-2015")

    def test_neea_efficient_homes(self):
        self._build_and_test("neea", "neea-efficient-homes")

    def test_northwest_energy_star_v3_r8_qa_short(self):
        self._build_and_test("neea", "northwest-energy-star-v3-r8-qa-short", True)

    def test_northwest_energy_star_v3_r8_qa_long(self):
        self._build_and_test("neea", "northwest-energy-star-v3-r8-qa-long", True)

    def test_northwest_energy_star_version_3_2014_qa(self):
        self._build_and_test("neea", "northwest-energy-star-version-3-2014-qa", True)

    def test_northwest_energy_star_version_3_2014_full_qa(self):
        self._build_and_test("neea", "northwest-energy-star-version-3-2014-full-qa", True)

    def test_utility_incentive_v1_single_family(self):
        self._build_and_test("neea", "utility-incentive-v1-single-family")

    def test_utility_incentive_v1_multi_family(self):
        self._build_and_test("neea", "utility-incentive-v1-multifamily")
