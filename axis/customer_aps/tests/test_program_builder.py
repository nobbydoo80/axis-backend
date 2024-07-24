"""test_program_builder.py - axis"""

__author__ = "Steven K"
__date__ = "4/23/22 14:51"
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

    def _build_and_test(self, owner_slug: str, program_slug: str, has_qa: bool = False):
        company = general_organization_factory(slug=owner_slug)
        management.call_command("build_program", "-p", program_slug, stdout=DevNull())

        total = 2 if has_qa else 1
        self.assertEqual(EEPProgram.objects.count(), total)

        eep_program = EEPProgram.objects.get(is_qa_program=False)
        self.assertEqual(eep_program.owner.id, company.id)
        self.assertEqual(eep_program.required_checklists.count(), 0)
        self.assertIsNotNone(eep_program.collection_request)

        if has_qa:
            eep_program = EEPProgram.objects.get(is_qa_program=True)
            self.assertEqual(eep_program.owner.id, company.id)
            self.assertEqual(eep_program.required_checklists.count(), 0)
            self.assertIsNotNone(eep_program.collection_request)

    def test_aps_energy_star_v3(self):
        self._build_and_test("aps", "aps-energy-star-v3")

    def test_aps_energy_star_v3_hers_60(self):
        self._build_and_test("aps", "aps-energy-star-v3-hers-60")

    def test_aps_energy_star_v3_2014(self):
        self._build_and_test("aps", "aps-energy-star-v3-2014")

    def test_aps_2015_audit(self):
        self._build_and_test("aps", "aps-2015-audit")

    def test_aps_energy_star_v3_2018(self):
        self._build_and_test("aps", "aps-energy-star-v3-2018")

    def test_aps_energy_star_v3_hers_60_2018(self):
        self._build_and_test("aps", "aps-energy-star-v3-hers-60-2018")

    def test_srp_energy_star_homes(self):
        self._build_and_test("srp", "srp-energy-star-homes")

    def test_ed3_mock_energy_star_homes(self):
        self._build_and_test("electrical-district-3", "ed3-mock-energy-star-homes")

    def test_az_energy_star_v3_2017(self):
        self._build_and_test("az-doe", "az-energy-star-v3-2017")
