"""neea.py: Django eep_program program checks tests"""


__author__ = "Johnny Fang"
__date__ = "16/7/19 3:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]

import datetime
import logging
import random
from datetime import timedelta, date

from django.contrib.contenttypes.models import ContentType

from axis.annotation.models import Type, Annotation
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_neea.utils import NEEA_PROGRAM_SLUGS
from axis.eep_program.models import EEPProgram

from axis.eep_program.tests.mixins import EEPProgramHomeStatusTestMixin
from axis.floorplan.tests.factories import floorplan_with_remrate_factory
from axis.home import strings as home_strings
from axis.home.models import EEPProgramHomeStatus, Home

log = logging.getLogger(__name__)


class EEPProgramNEEAprogramChecksTests(EEPProgramHomeStatusTestMixin, AxisTestCase):
    """Test for NEEA eep_program"""

    client_class = AxisClient

    def test_get_neea_utilities_satisfied_status_slug_neea_heat_not_provided(self):
        """
        Test for get_neea_utilities_satisfied_status() case when home_status annotations has no type
        heat-source. expected result is a failing status
        """
        slug = NEEA_PROGRAM_SLUGS[random.randint(0, len(NEEA_PROGRAM_SLUGS) - 1)]
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = dict()
        annotations_url = "annotations_edit_url"
        result = eep_program.get_neea_utilities_satisfied_status(
            home_status, "", "", annotations_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertIn("Heat Source has not yet been provided.", result.message)
        self.assertEqual(annotations_url, result.url)

    def test_get_neea_utilities_satisfied_status_slug_unknown_heat_source(self):
        """
        Test for get_neea_utilities_satisfied_status() case when heat-source is unknown i.e.
        the value passed does NOT match anything in the app. Expected result is a failing status
        """
        slug = NEEA_PROGRAM_SLUGS[random.randint(0, len(NEEA_PROGRAM_SLUGS) - 1)]
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = dict({"neea-heating_source": "Primary Heating Type"})
        annotations_url = "annotations_edit_url"
        result = eep_program.get_neea_utilities_satisfied_status(
            home_status, "", "", annotations_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertIn("Unknown heat source", result.message)
        self.assertEqual(annotations_url, result.url)

    def test_get_neea_utilities_satisfied_status_neea_all_utilities_required(self):
        """
        Test for get_neea_utilities_satisfied_status() case when heat-source requires that both an
        electric and gas utility be assigned.. Expected result is a failing status
        """
        slug = NEEA_PROGRAM_SLUGS[random.randint(0, len(NEEA_PROGRAM_SLUGS) - 1)]
        EEPProgram.objects.filter(owner__name="EEP4").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = dict({"neea-heating_source": "Heat Pump - w/ Gas Backup"})
        annotations_url = "annotations_edit_url"
        co_url = "companies_edit_url"
        result = eep_program.get_neea_utilities_satisfied_status(
            home_status, "", co_url, annotations_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertIn("requires that both an electric and gas utility be assigned", result.message)
        self.assertEqual(co_url, result.url)
        self.assertEqual(input_values["neea-heating_source"], result.data)

    def test_get_neea_utilities_satisfied_status_neea_electric_utility_required(self):
        """
        Test for get_neea_utilities_satisfied_status() case when heat-source requires
        electric utility be assigned.. Expected result is a failing status
        """
        slug = NEEA_PROGRAM_SLUGS[random.randint(0, len(NEEA_PROGRAM_SLUGS) - 1)]
        EEPProgram.objects.filter(owner__name="EEP4").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = dict({"neea-heating_source": "Hydronic Radiant Heat Pump"})
        annotations_url = "annotations_edit_url"
        co_url = "companies_edit_url"
        result = eep_program.get_neea_utilities_satisfied_status(
            home_status, "", co_url, annotations_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertIn("requires that an electric utility be assigned", result.message)
        self.assertEqual(co_url, result.url)
        self.assertEqual(input_values["neea-heating_source"], result.data)

    def test_get_neea_utilities_satisfied_status_neea_gas_utility_required(self):
        """
        Test for get_neea_utilities_satisfied_status() case when heat-source requires a
        gas utility be assigned.. Expected result is a failing status
        """
        slug = NEEA_PROGRAM_SLUGS[random.randint(0, len(NEEA_PROGRAM_SLUGS) - 1)]
        EEPProgram.objects.filter(owner__name="EEP4").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = dict({"neea-heating_source": "Hydronic Radiant Gas Boiler"})
        annotations_url = "annotations_edit_url"
        co_url = "companies_edit_url"
        result = eep_program.get_neea_utilities_satisfied_status(
            home_status, "", co_url, annotations_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertIn("requires that a gas utility be assigned", result.message)
        self.assertEqual(co_url, result.url)
        self.assertEqual(input_values["neea-heating_source"], result.data)

    def test_get_neea_utilities_satisfied_status_neea_passing(self):
        """
        Test for get_neea_utilities_satisfied_status() case when heat-source requires that both an
        electric and gas utility be assigned. Expected result is a passing status
        """
        slug = NEEA_PROGRAM_SLUGS[random.randint(0, len(NEEA_PROGRAM_SLUGS) - 1)]
        EEPProgram.objects.filter(owner__name="EEP3").update(slug=slug)
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        input_values = dict({"neea-heating_source": "Heat Pump - w/ Gas Backup"})
        heat_source_type = Type.objects.create(
            name="heat source type", data_type="open", slug="heat-source"
        )
        Annotation.objects.create(
            type=heat_source_type,
            content="Gas with AC",
            content_type=ContentType.objects.get_for_model(home_status),
            object_id=home_status.id,
        )
        annotations_url = "annotations_edit_url"
        co_url = "companies_edit_url"
        result = eep_program.get_neea_utilities_satisfied_status(
            home_status, "", co_url, annotations_url, input_values
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_get_hquito_accrediation_status_for_non_neea_program(self):
        """
        Test for get_hquito_accrediation_status() for a non NEEA eep_program. response should be
        None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_hquito_accrediation_status(
            home_status, "home_edit_url", "companies_edit_url"
        )
        self.assertIsNone(result)

    def test_get_hquito_accrediation_status_non_2015_program(self):
        """
        Test for get_hquito_accrediation_status() for a NEEA eep_program that does NOT contain 2015
        in its name. check NEEA_PROGRAM_SLUGS for a complete list of program slugs. For this tests
        I will use 'neea-energy-star-v3-performance'
        response should be None
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-energy-star-v3-performance")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_hquito_accrediation_status(
            home_status, "home_edit_url", "companies_edit_url"
        )
        self.assertIsNone(result)

    def test_get_hquito_accrediation_status_non_hvac_company(self):
        """
        Test for get_hquito_accrediation_status() case home_status home company is not hvac.
        response should be None
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-performance-2015")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_hquito_accrediation_status(
            home_status, "home_edit_url", "companies_edit_url"
        )
        self.assertIsNone(result)

    def test_get_hquito_accrediation_status_hquito_status_none(self):
        """
        Test for get_hquito_accrediation_status()  case hvac company hquito status is None.
        response should be Failing status
        """
        from axis.company.models import Company

        Company.objects.filter(name="EEP4").update(slug="neea")
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-performance-2015")
        # I need to make this happen eep_program__owner__slug="neea" for EEP4
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_hquito_accrediation_status(
            home_status, "home_edit_url", "companies_edit_url"
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn(
            "Projects must have an H-QUITO accredited contractor for certification", result.message
        )

    def test_get_hquito_accrediation_status_hquito_status_false(self):
        """
        Test for get_hquito_accrediation_status() case hvac company hquito status is False.
        response should be failing status
        """
        from axis.company.models import Company

        Company.objects.filter(name="EEP4").update(slug="neea")
        Company.objects.filter(name="HVAC1").update(hquito_accredited=False)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-performance-2015")
        # I need to make this happen eep_program__owner__slug="neea" for EEP4
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_hquito_accrediation_status(
            home_status, "home_edit_url", "companies_edit_url"
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn(
            "Projects must have an H-QUITO accredited contractor for certification", result.message
        )

    def test_get_hquito_accrediation_status_hquito_status_true(self):
        """
        Test for get_hquito_accrediation_status() case hvac company hquito status is True.
        response should be passing status
        """
        from axis.company.models import Company, HvacOrganization

        Company.objects.filter(name="EEP4").update(slug="neea")
        Company.objects.filter(name="HVAC1").update(hquito_accredited=True)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-performance-2015")
        # I need to make this happen eep_program__owner__slug="neea" for EEP4
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_hquito_accrediation_status(
            home_status, "home_edit_url", "companies_edit_url"
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_neea_invalid_program_status_home_status_complete(self):
        """Test for get_neea_invalid_program_status() home_status state 'complete"""
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-energy-star-v3")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(state="complete")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_invalid_program_status(home_status, "home_edit_utl", "")

        self.assertIsNone(result)

    def test_get_neea_invalid_program_status_neea_invalid_program(self):
        """
        Test for get_neea_invalid_program_status() home_status NOT multifamily and
        created_date after  2015, 7, 1
        state not complete 'complete
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-energy-star-v3")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            created_date=datetime.datetime(2015, 8, 1, tzinfo=datetime.timezone.utc)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_invalid_program_status(home_status, "home_edit_utl", "")

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertIn(
            "was closed on July 1 2015.  Please change this to the NEEA 2015 ENERGY STAR Program.",
            result.message,
        )

    def test_get_neea_invalid_program_status_prescriptive_requires_multifamily(self):
        """
        Test for get_neea_invalid_program_status() home_status NOT multifamily and
        created_date before than 2015, 7, 1
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-energy-star-v3")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            created_date=datetime.datetime(2015, 6, 1, tzinfo=datetime.timezone.utc)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_invalid_program_status(home_status, "home_edit_utl", "")

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(home_strings.PRESCRIPTIVE_REQUIRES_MULTIFAMILY, result.message)

    def test_get_neea_invalid_program_status_performance_passing(self):
        """Test for get_neea_invalid_program_status() home_status home is NOT multifamily and
        program slug is neea-energy-star-v3-performance (performance)
        """
        EEPProgram.objects.filter(owner__name="EEP3").update(slug="neea-energy-star-v3-performance")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_invalid_program_status(home_status, "home_edit_utl", "")

        self.assertIsNotNone(result)
        self.assertTrue(result.status)

    def test_get_neea_invalid_program_status_performance_requires_non_multifamily(self):
        """
        Test for get_neea_invalid_program_status() home_status home is multifamily and
        program slug is neea-energy-star-v3-performance (performance)
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-energy-star-v3-performance")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")

        home_slug = EEPProgramHomeStatus.objects.get(eep_program=eep_program).home.slug
        Home.objects.filter(slug=home_slug).update(is_multi_family=True)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_invalid_program_status(home_status, "home_edit_utl", "")

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(home_strings.PERFORMANCE_REQUIRES_NON_MULTIFAMILY, result.message)

    def test_get_neea_invalid_program_status_generic_requires_non_multifamily(self):
        """
        Test for get_neea_invalid_program_status() home_status home is NOT multifamily and
        its program slug is utility-incentive-v1-multifamily
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        EEPProgram.objects.filter(owner__name="EEP3").update(
            slug="utility-incentive-v1-multifamily"
        )
        eep_program4 = EEPProgram.objects.get(owner__name="EEP4")
        eep_program = EEPProgram.objects.get(owner__name="EEP3")

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program4.get_neea_invalid_program_status(home_status, "home_edit_utl", "")

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(home_strings.GENERIC_REQUIRES_MULTIFAMILY, result.message)

    def test_get_neea_invalid_program_status_generic_requires_singlefamily(self):
        """
        Test for get_neea_invalid_program_status() home_status home is multifamily and
        its program slug is neea-bpa. expected failing status
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")

        home_slug = EEPProgramHomeStatus.objects.get(eep_program=eep_program).home.slug
        Home.objects.filter(slug=home_slug).update(is_multi_family=True)

        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_invalid_program_status(home_status, "home_edit_utl", "")

        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(home_strings.GENERIC_REQUIRES_SINGLEFAMILY, result.message)

    def test_get_neea_bpa_remrate_version_status_no_floorplan(self):
        """Test get_neea_bpa_remrate_version_status. eep_program home_status has no floorplan"""
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.floorplan)
        result = eep_program.get_neea_bpa_remrate_version_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_neea_bpa_remrate_version_status_no_remrate_target(self):
        """
        Test get_neea_bpa_remrate_version_status. eep_program home_status' floorplan has NO
        remrate target
        """
        from axis.floorplan.tests.factories import floorplan_factory

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_bpa_remrate_version_status(home_status, "edit_url")
        self.assertIsNone(result)

    def test_get_neea_bpa_remrate_version_status_invalid(self):
        """
        Test for get_neea_bpa_remrate_version_status. NO passing_version and
        home_status_state NOT in  ['certification_pending', 'complete']
        using default start and end dates:
        start_transition_date == datetime.date(2019, 3, 1) ;  end_transition_date == (2019, 10, 1)
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwargs = {"remrate_target__version": "14.7.0"}
        neea_kwargs = {"end_transition_date": date.today() + timedelta(days=1)}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.numerical_version, (14, 7, 0))

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            floorplan=floorplan, state="inspection"
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_bpa_remrate_version_status(
            home_status, "edit_url", **neea_kwargs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Program {program} only allows rating data from REM/Rate™ versions {versions}".format(
            program=home_status.eep_program, versions="15.3 or 15.7.1"
        )
        self.assertIn(msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual("edit_url", result.url)

    def test_get_neea_bpa_remrate_version_status_invalid_2(self):
        """
        Test for get_neea_bpa_remrate_version_status. NO passing_version and
        home_status_state NOT in  ['certification_pending', 'complete']
        start_transition_date is today + 10 days
        end_transition_date is start_transition_date + 7 days
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwargs = {"remrate_target__version": "14.7.0"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.numerical_version, (14, 7, 0))

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            floorplan=floorplan, state="inspection"
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        start_transition_date = datetime.date.today() + datetime.timedelta(days=10)
        end_transition_date = datetime.date.today() + datetime.timedelta(days=17)
        kwargs = {
            "start_transition_date": start_transition_date,
            "end_transition_date": end_transition_date,
        }
        result = eep_program.get_neea_bpa_remrate_version_status(home_status, "edit_url", **kwargs)
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Program {program} only allows rating data from REM/Rate™ versions {versions}".format(
            program=home_status.eep_program, versions="15.3"
        )
        self.assertIn(msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual("edit_url", result.url)

    def test_get_neea_bpa_remrate_version_status_passing_status(self):
        """
        Test for get_neea_bpa_remrate_version_status. NO passing_version and
        home_status_state in  ['certification_pending', 'complete']
        start_transition_date is today + 10 days
        end_transition_date is start_transition_date + 7 days
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwargs = {"remrate_target__version": "14.7.0"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.numerical_version, (14, 7, 0))

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        start_transition_date = datetime.date.today() + datetime.timedelta(days=10)
        end_transition_date = datetime.date.today() + datetime.timedelta(days=17)
        kwargs = {
            "start_transition_date": start_transition_date,
            "end_transition_date": end_transition_date,
        }
        result = eep_program.get_neea_bpa_remrate_version_status(home_status, "edit_url", **kwargs)
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNotNone(result.data)

    def test_get_neea_bpa_remrate_version_status_passing_status_passing_version(self):
        """
        Test for get_neea_bpa_remrate_version_status. passing_version and
        home_status_state not in  ['certification_pending', 'complete']
        start_transition_date is today + 10 days
        end_transition_date is start_transition_date + 7 days
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwargs = {"remrate_target__version": "15.3.0"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 3, 0))

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            floorplan=floorplan, state="inspection"
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)

        start_transition_date = datetime.date.today() + datetime.timedelta(days=10)
        end_transition_date = datetime.date.today() + datetime.timedelta(days=17)
        kwargs = {
            "start_transition_date": start_transition_date,
            "end_transition_date": end_transition_date,
        }
        result = eep_program.get_neea_bpa_remrate_version_status(home_status, "edit_url", **kwargs)
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNotNone(result.data)

    def test_get_neea_bpa_remrate_version_status_passing(self):
        """
        Test for get_neea_bpa_remrate_version_status. passing_version and
        home_status_state NOT in  ['certification_pending', 'complete']
        using default start and end dates:
        start_transition_date == datetime.date(2019, 3, 1) ;  end_transition_date == (2019, 10, 1)
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP3")
        kwargs = {"remrate_target__version": "15.7.1"}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        self.assertEqual(floorplan.remrate_target.numerical_version, (15, 7, 1))

        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            floorplan=floorplan, state="inspection"
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_bpa_remrate_version_status(home_status, "edit_url")
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNotNone(result.data)

    def test_gnctmts_heat_source_non_neea_bpa_program(self):
        """Test for get_neea_checklist_type_matches_remrate_status. eep_program is not neea-bpa"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertNotEqual(eep_program.slug, "neea-bpa")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_gnctmts_heat_source_with_certification_date(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status. home_status has a
        certification_date
        """
        import datetime

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            certification_date=datetime.date(2018, 1, 1)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.certification_date)
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_gnctmts_heat_source_no_floorplan(self):
        """Test for get_neea_checklist_type_matches_remrate_status. home_status has NO floorplan"""
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_gnctmts_heat_source_no_heat_source(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status. input_values has no key
        neea-heating_source
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values
        )
        self.assertIsNone(result)

    def test_gnctmts_heat_source_no_remrate(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status. home_status floorplan has NO
        remrate
        """
        from axis.floorplan.tests.factories import floorplan_factory

        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertIsNone(home_status.floorplan.remrate_target)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": ""}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values
        )
        self.assertIsNone(result)

    def test_gnctmts_heat_source_passing_status(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status. for this case since our
        'neea-heating_source' will not match any of the heat_sources it will return a Passing Status
        """
        floorplan = floorplan_with_remrate_factory()
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "some"}
        heat_sources = [
            "Heat Pump",
            "Heat Pump - Geothermal",
            "Heat Pump - Geothermal/Ground Source",
            "Heat Pump - w/ Gas Backup",
            "Heat Pump - Mini Split",
            "Gas with AC",
            "Gas No AC",
            "Zonal Electric",
            "Propane, Oil, or Wood",
            "Hydronic Radiant Electric Boiler",
            "Hydronic Radiant Gas Boiler",
            "Hydronic Radiant Heat Pump",
        ]
        self.assertNotIn(input_values["neea-heating_source"], heat_sources)
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)
        self.assertIsNone(result.message)

    def test_gnctmts_heat_source_heat_pump_type_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Heat Pump'  AND dominant_heating type does NOT contain 'Heat Pump' nor 'air'
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Heat Pump"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("heat pump", dominant["dominant_heating"]["type"].lower())
        self.assertNotIn("air", dominant["dominant_heating"]["type"].lower())
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_heat_pump_passing_1(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Heat Pump'  AND dominant_heating type does contain 'Heat Pump'
        simulation heating type = 7 i.e. 'Ground-source heat pump'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 7}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Heat Pump"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn("heat pump", dominant["dominant_heating"]["type"].lower())
        self.assertNotIn("air", dominant["dominant_heating"]["type"].lower())
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_heat_pump_passing_2(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Heat Pump'  AND dominant_heating type does contain 'Heat Pump' or 'air'
        simulation heating type = 6 i.e. 'Air-source heat pump'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 6}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Heat Pump"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn("heat pump", dominant["dominant_heating"]["type"].lower())
        self.assertIn("air", dominant["dominant_heating"]["type"].lower())
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_geothermal_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is ['Heat Pump - Geothermal', 'Heat Pump - Geothermal/Ground Source']
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        kwrgs = {"checklist_url": "url"}

        heat_sources = ["Heat Pump - Geothermal", "Heat Pump - Geothermal/Ground Source"]
        for heat_source in heat_sources:
            input_values = {"neea-heating_source": heat_source}
            self.assertNotIn(
                "Ground-source heat pump".lower(), dominant["dominant_heating"]["type"].lower()
            )
            result = eep_program.get_neea_checklist_type_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            msg = (
                "Primary heating type '{}' in REM/Rate does not align with "
                "checklist answer of '{}'"
            )
            fail_msg = msg.format(
                dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
            )
            self.assertEqual(fail_msg, result.message)
            self.assertIsNone(result.data)
            self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_geothermal_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is ['Heat Pump - Geothermal', 'Heat Pump - Geothermal/Ground Source']
        simulation heating type = 7 i.e. 'Ground-source heat pump'
        expected back Passing status
        """
        kwargs = {"remrate_target__heating__type": 7}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        kwrgs = {"checklist_url": "url"}

        heat_sources = ["Heat Pump - Geothermal", "Heat Pump - Geothermal/Ground Source"]
        for heat_source in heat_sources:
            input_values = {"neea-heating_source": heat_source}
            self.assertIn(
                "Ground-source heat pump".lower(), dominant["dominant_heating"]["type"].lower()
            )
            result = eep_program.get_neea_checklist_type_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)

    def test_gnctmts_heat_source_heat_pump_with_gas_backup_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Heat Pump - w/ Gas Backup'  AND
        dominant_heating type != 'Dual Fuel heat Pump'
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Heat Pump - w/ Gas Backup"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotEqual(
            "Dual Fuel heat Pump".lower(), dominant["dominant_heating"]["type"].lower()
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_heat_pump_mini_split_type_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Heat Pump - Mini Split'  AND
        dominant_heating type does  NOT contain 'heat pump'
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Heat Pump - Mini Split"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("heat pump".lower(), dominant["dominant_heating"]["type"].lower())
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_heat_pump_mini_split_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Heat Pump - Mini Split'  AND
        dominant_heating type does  contain 'heat pump'
        simulation heating type = 6 i.e. 'Air-source heat pump'
        expected back Passing status
        """
        kwargs = {"remrate_target__heating__type": 6}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Heat Pump - Mini Split"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn("heat pump".lower(), dominant["dominant_heating"]["type"].lower())
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_gas_with_ac_mismatch_heat_source(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas with AC'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas with AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("Gas with AC".lower(), dominant["dominant_heating"]["type"].lower())
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_sources_gas_with_ac_fuel_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas with AC'  AND
        dominant_heating type in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Propane'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 1, "remrate_target__heating__fuel_type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas with AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired air distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertIsNotNone(dominant["dominant_heating"]["fuel"])
        self.assertNotIn("gas", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_gas_with_ac_no_cooling_type(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas with AC'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        simulation cooling type is None
        expected back Failing status
        """
        kwargs = {
            "remrate_target__heating__type": 1,
            "remrate_target__heating__fuel_type": 1,
            "remrate_target__air_conditioning_count": 0,
            "remrate_target__air_source_heat_pump_count": 0,
            "remrate_target__ground_source_heat_pump_count": 0,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas with AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired air distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertIn("gas", dominant["dominant_heating"]["fuel"])
        self.assertIsNone(dominant["dominant_cooling"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Air Conditioner is not present in REM/Rate but checklist answer indicates {}"
        fail_msg = msg.format(input_values["neea-heating_source"])
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_gas_with_ac_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas with AC'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        simulation cooling type = 1
        expected back Passing status
        """
        kwargs = {
            "remrate_target__heating__type": 1,
            "remrate_target__heating__fuel_type": 1,
            "remrate_target__air_conditioning__type": 1,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas with AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired air distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertIn("gas", dominant["dominant_heating"]["fuel"])
        self.assertIsNotNone(dominant["dominant_cooling"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_gas_no_ac_mismatch_heat_source(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas with AC'  AND
        dominant_heating type not == 'Fuel-fired air distribution'
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas No AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn(
            "Fuel-fired air distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_gas_no_ac_fuel_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas with AC'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        simulation heating fuel type = 2 i.e. 'Propane'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 1, "remrate_target__heating__fuel_type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas No AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired air distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertIsNotNone(dominant["dominant_heating"]["fuel"])
        self.assertNotIn("gas", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_gas_no_ac_with_cooling_type(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas No AC'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        simulation cooling type = 1
        expected back Failing status
        """
        kwargs = {
            "remrate_target__heating__type": 1,
            "remrate_target__heating__fuel_type": 1,
            "remrate_target__air_conditioning__type": 1,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas No AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired air distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertIn("gas", dominant["dominant_heating"]["fuel"])
        self.assertIsNotNone(dominant["dominant_cooling"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Air Conditioner is present in REM/Rate but checklist answer indicates {}"
        fail_msg = msg.format(input_values["neea-heating_source"])
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_gas_no_ac_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Gas No AC'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        simulation cooling type = 1
        expected back Passing status
        """
        kwargs = {
            "remrate_target__heating__type": 1,
            "remrate_target__heating__fuel_type": 1,
            "remrate_target__air_conditioning_count": 0,
            "remrate_target__air_source_heat_pump_count": 0,
            "remrate_target__ground_source_heat_pump_count": 0,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Gas No AC"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired air distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertIn("gas", dominant["dominant_heating"]["fuel"])
        self.assertIsNone(dominant["dominant_cooling"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_zonal_electric_type_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Zonal Electric'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 1, "remrate_target__heating__fuel_type": 2}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Zonal Electric"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn(
            "Electric baseboard or radiant".lower(), dominant["dominant_heating"]["type"].lower()
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_zonal_electric_fuel_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Zonal Electric'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 4 i.e. 'Electric baseboard or radiant'
        simulation heating fuel type is not 'Electric'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 4, "remrate_target__heating__fuel_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Zonal Electric"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Electric baseboard or radiant".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertNotEqual("Electric", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_zonal_electric_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Zonal Electric'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 4 i.e. 'Electric baseboard or radiant'
        simulation heating fuel type = 4 i.e. 'Electric'
        expected back Passing status
        """
        kwargs = {"remrate_target__heating__type": 4, "remrate_target__heating__fuel_type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Zonal Electric"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Electric baseboard or radiant".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertEqual("Electric", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_propane_oil_wood_type_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Propane, Oil, or Wood'
        AND
        dominant_heating type not in ['Electric baseboard or radiant',
        'Fuel-fired unvented unit heater']
        AND
        simulation heating type = 6 i.e. 'Air-source heat pump'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 6, "remrate_target__heating__fuel_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Propane, Oil, or Wood"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn(
            dominant["dominant_heating"]["type"].lower(),
            ["Electric baseboard or radiant".lower(), "Fuel-fired unvented unit heater".lower()],
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_propane_oil_wood_fuel_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Propane, Oil, or Wood'
        AND
        dominant_heating type in  ['Fuel-fired unit heater',
         'Fuel-fired unvented unit heater']
        simulation heating type in [3, 9]
        simulation heating fuel not in ['Propane', 'Fuel Oil', 'Wood']
        expected back Failing status
        """
        # 3 = 'Fuel-fired unit heater', 9 = 'Fuel-fired unvented unit heater'
        heating_types = [3, 9]
        for heating_type in heating_types:
            kwargs = {
                "remrate_target__heating__type": heating_type,
                "remrate_target__heating__fuel_type": 1,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)
            input_values = {"neea-heating_source": "Propane, Oil, or Wood"}
            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertIn(
                dominant["dominant_heating"]["type"].lower(),
                ["Fuel-fired unit heater".lower(), "Fuel-fired unvented unit heater".lower()],
            )
            self.assertNotIn(
                dominant["dominant_heating"]["fuel"].lower(), ["Propane", "Fuel Oil", "Wood"]
            )
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_type_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            msg = (
                "Primary heating type '{}' in REM/Rate does not align with "
                "checklist answer of '{}'"
            )
            fail_msg = msg.format(
                dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
            )
            self.assertEqual(fail_msg, result.message)
            self.assertIsNone(result.data)
            self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_propane_oil_wood_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Propane, Oil, or Wood'
        AND
        dominant_heating type in  ['Fuel-fired unit heater',
         'Fuel-fired unvented unit heater']
        simulation heating type in [3, 9]
        expected back Passing status
        """
        # 3 = 'Fuel-fired unit heater', 9 = 'Fuel-fired unvented unit heater'
        # 2 = 'Propane', 3 = 'Fuel oil', 6 = 'Wood'
        types = [(3, 2), (3, 3), (3, 6), (9, 2), (9, 3), (9, 6)]
        for heating_type, fuel_type in types:
            kwargs = {
                "remrate_target__heating__type": heating_type,
                "remrate_target__heating__fuel_type": fuel_type,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)
            input_values = {"neea-heating_source": "Propane, Oil, or Wood"}
            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertIn(
                dominant["dominant_heating"]["type"].lower(),
                ["Fuel-fired unit heater".lower(), "Fuel-fired unvented unit heater".lower()],
            )
            self.assertIn(dominant["dominant_heating"]["fuel"], ["Propane", "Fuel oil", "Wood"])
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_type_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)
            self.assertIsNone(result.data)

    def test_gnctmts_heat_source_electric_boiler_type_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Hydronic Radiant Electric Boiler'
        AND
        dominant_heating type NOT in ['Hydronic Ground-source heat pump',
         'Electric hydronic distribution'.lower()]
         AND
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 1, "remrate_target__heating__fuel_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Electric Boiler"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn(
            dominant["dominant_heating"]["type"].lower(),
            ["Hydronic Ground-source heat pump".lower(), "Electric hydronic distribution".lower()],
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_electric_boiler_fuel_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Hydronic Radiant Electric Boiler'  AND
        dominant_heating type = 'Electric hydronic distribution'
        simulation heating type = 8 i.e. 'Electric hydronic distribution'
        simulation heating fuel type NOT 'Electric'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 8, "remrate_target__heating__fuel_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Electric Boiler"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Electric hydronic distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertNotEqual("Electric", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_electric_boiler_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Hydronic Radiant Electric Boiler'  AND
        dominant_heating type = 'Electric hydronic distribution'
        simulation heating type = 8 i.e. 'Electric hydronic distribution'
        simulation heating fuel type = 'Electric'
        expected back Passing status
        """
        kwargs = {"remrate_target__heating__type": 8, "remrate_target__heating__fuel_type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Electric Boiler"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Electric hydronic distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertEqual("Electric", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_gas_boiler_type_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Zonal Electric'
        AND
        dominant_heating type not in ['Hydronic Ground-source heat pump',
        'Fuel-fired hydronic distribution']
        AND
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 1, "remrate_target__heating__fuel_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Gas Boiler"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn(
            dominant["dominant_heating"]["type"].lower(),
            [
                "Hydronic Ground-source heat pump".lower(),
                "Fuel-fired hydronic distribution".lower(),
            ],
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_gas_boiler_fuel_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Hydronic Radiant Gas Boiler'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        simulation heating fuel type = 3 i.e. 'Fuel oil'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 2, "remrate_target__heating__fuel_type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Gas Boiler"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired hydronic distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertNotEqual("Electric", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_gas_boiler_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Hydronic Radiant Gas Boiler'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 2 i.e. 'Fuel-fired hydronic distribution'
        simulation heating fuel type = 1 i.e. 'Natural gas'
        expected back Passing status
        """
        kwargs = {"remrate_target__heating__type": 2, "remrate_target__heating__fuel_type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Gas Boiler"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            "Fuel-fired hydronic distribution".lower(), dominant["dominant_heating"]["type"].lower()
        )
        self.assertEqual("Natural gas", dominant["dominant_heating"]["fuel"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gnctmts_heat_source_hydronic_heat_pump_type_mismatch(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Zonal Electric'  AND
        dominant_heating type not in 'Fuel-fired air distribution'
        simulation heating type = 1 i.e. 'Fuel-fired air distribution'
        expected back Failing status
        """
        kwargs = {"remrate_target__heating__type": 1}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Heat Pump"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn(
            dominant["dominant_heating"]["type"].lower(),
            ["Hydronic Ground-source heat pump".lower(), "Electric baseboard or radiant".lower()],
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_heating"]["type"], input_values["neea-heating_source"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gnctmts_heat_source_hydronic_heat_pump_passing(self):
        """
        Test for get_neea_checklist_type_matches_remrate_status.
        heat_source is 'Zonal Electric'
        AND
        dominant_heating type in
        ['Hydronic Ground-source heat pump', 'Electric baseboard or radiant]
        AND
        simulation heating type = 4 i.e. 'Electric baseboard or radiant'
        expected back Passing status
        """
        kwargs = {"remrate_target__heating__type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Heat Pump"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIn(
            dominant["dominant_heating"]["type"].lower(),
            ["Hydronic Ground-source heat pump".lower(), "Electric baseboard or radiant".lower()],
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_type_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gncwhmrs_non_neea_bpa(self):
        """Test for get_neea_checklist_water_heater_matches_remrate_status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertNotEqual(eep_program.slug, "neea-bpa")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_gncwhmrs_heat_source_with_certification_date(self):
        """
        Test get_neea_checklist_water_heater_matches_remrate_status. home_status
        has certification_date
        """
        import datetime

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            certification_date=datetime.date(2018, 1, 1)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.certification_date)
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_gncwhmrs_no_water_heater(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status.
        input_values has no key 'neea-water_heater_tier'
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values
        )

        self.assertIsNone(result)

    def test_gncwhmrs_no_floorplan(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status.
        eep_program has NO floorplan
        """
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=None)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-water_heater_tier": "value"}
        kwargs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwargs
        )

        self.assertIsNone(result)

    def test_gncwhmrs_no_simulation(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. home_status floorplan has
        NO remrate (simulation)
        """
        from axis.floorplan.tests.factories import floorplan_factory

        floorplan = floorplan_factory()
        self.assertIsNone(floorplan.remrate_target)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertIsNone(home_status.floorplan.remrate_target)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-water_heater_tier": "value"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )

        self.assertIsNone(result)

    def test_gncwhmrs_water_heater_equipment_type_none(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for 'dominant_hot_water' is none
        """

        floorplan = floorplan_with_remrate_factory()

        # Ugly Hack should not be used
        from axis.remrate_data.models import HotWaterHeater

        HotWaterHeater.objects.filter(simulation=floorplan.remrate_target).update(type=None)

        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-water_heater_tier": "Heat Pump"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertIsNone(dominant["dominant_hot_water"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary water heater '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_electric_resistance_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water='Electric Resistance' is NOT 'conventional',
        but 'Instant water heater'
        """
        # 3 = 'Instant water heater'
        kwargs = {"remrate_target__hot_water__type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-water_heater_tier": "Electric Resistance"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotEqual(dominant["dominant_hot_water"]["type"], "Conventional")
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary water heater '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_electric_resistance_fuel_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water='Electric Resistance' is NOT 'conventional',
        but 'Instant water heater'
        """
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {"remrate_target__hot_water__type": 1, "remrate_target__hot_water__fuel_type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-water_heater_tier": "Electric Resistance"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual(dominant["dominant_hot_water"]["type"], "Conventional")
        self.assertNotEqual(dominant["dominant_hot_water"]["fuel"], "Electric")
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = "Primary water heater '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_electric_resistance_passing_status(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        meets all requirements to get a Passing status
        installed equipment
        type for dominant_hot_water='Electric Resistance' is 'conventional',
        fuel type is 'Electric
        """
        # 1 = 'Conventional' h2O_heater_type
        # 4 = 'Electric' fuel type
        kwargs = {"remrate_target__hot_water__type": 1, "remrate_target__hot_water__fuel_type": 4}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-water_heater_tier": "Electric Resistance"}
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual(dominant["dominant_hot_water"]["type"], "Conventional")
        self.assertEqual(dominant["dominant_hot_water"]["fuel"], "Electric")
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gncwhmrs_water_heater_hpwh_tiers_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water of types: 'HPWH Tier 1', 'HPWH Tier 2',
        'HPWH Tier 3' is NOT 'Heat pump',
        """
        water_heaters = ["HPWH Tier 1", "HPWH Tier 2", "HPWH Tier 3"]
        for water_heater in water_heaters:
            input_values = {"neea-water_heater_tier": water_heater}
            # 1 = 'Conventional' h2O_heater_type
            kwargs = {"remrate_target__hot_water__type": 1}
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertNotIn("heat pump", dominant["dominant_hot_water"]["type"])
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            msg = (
                "Primary water heater '{}' in REM/Rate does not align with checklist "
                "answer of '{}'"
            )
            fail_msg = msg.format(
                dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
            )
            self.assertEqual(fail_msg, result.message)
            self.assertIsNone(result.data)
            self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_hpwh_tiers_fuel_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status.
        simulation's installed equipment for dominant_hot_water of types:
        'HPWH Tier 1', 'HPWH Tier 2', 'HPWH Tier 3' fuel_type is NOT 'Electric',
        """
        water_heaters = ["HPWH Tier 1", "HPWH Tier 2", "HPWH Tier 3"]
        for water_heater in water_heaters:
            input_values = {"neea-water_heater_tier": water_heater}
            # 4 = 'Heat pump' h2O_heater_type
            # 3 = 'Fuel oil' fuel type
            kwargs = {
                "remrate_target__hot_water__type": 4,
                "remrate_target__hot_water__fuel_type": 3,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertIn("heat pump", dominant["dominant_hot_water"]["type"].lower())
            self.assertNotEqual(dominant["dominant_hot_water"]["fuel"], "Electric")
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            msg = (
                "Primary water heater '{}' in REM/Rate does not align with checklist "
                "answer of '{}'"
            )
            fail_msg = msg.format(
                dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
            )
            self.assertEqual(fail_msg, result.message)
            self.assertIsNone(result.data)
            self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_hpwh_tiers_passing_status(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status.
        simulation's installed equipment for dominant_hot_water of types:
        'HPWH Tier 1', 'HPWH Tier 2', 'HPWH Tier 3' fuel_type is  'Electric',
        """
        water_heaters = ["HPWH Tier 1", "HPWH Tier 2", "HPWH Tier 3"]
        for water_heater in water_heaters:
            input_values = {"neea-water_heater_tier": water_heater}
            # 4 = 'Heat pump' h2O_heater_type
            # 4 = 'Electric' fuel type
            kwargs = {
                "remrate_target__hot_water__type": 4,
                "remrate_target__hot_water__fuel_type": 4,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertIn("heat pump", dominant["dominant_hot_water"]["type"].lower())
            self.assertEqual(dominant["dominant_hot_water"]["fuel"], "Electric")
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)
            self.assertIsNone(result.data)

    def test_gncwhmrs_water_heater_gas_conventional_lt_067_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water of type 'Gas Conventional EF < 0.67'
        is NOT 'Conventional',
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF < 0.67"}
        # 21 = 'Integrated' h2O_heater_type
        kwargs = {"remrate_target__hot_water__type": 21}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("Conventional", dominant["dominant_hot_water"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_lt_067_fuel_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment fuel type for dominant_hot_water of type 'Gas Conventional EF < 0.67'
        is NOT in ['Natural gas', 'Propane']
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF < 0.67"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {"remrate_target__hot_water__type": 1, "remrate_target__hot_water__fuel_type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
        self.assertNotIn(
            dominant["dominant_hot_water"]["fuel"], ["Natural gas".lower(), "Propane".lower()]
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_lt_067_insufficient_energy_factor(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Conventional EF < 0.67'
        energy factor >= 0.6
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF < 0.67"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Natural gas' fuel type
        energy_factors = [0.67, 0.7]
        for energy_factor in energy_factors:
            kwargs = {
                "remrate_target__hot_water__type": 1,
                "remrate_target__hot_water__fuel_type": 1,
                "remrate_target__hot_water__energy_factor": energy_factor,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
            self.assertIn(
                dominant["dominant_hot_water"]["fuel"].lower(),
                ["Natural gas".lower(), "Propane".lower()],
            )
            self.assertGreaterEqual(dominant["dominant_hot_water"]["energy_factor"], 0.67)
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            msg = (
                "Primary water heater '{}' in REM/Rate does not align with checklist "
                "answer of '{}'"
            )
            fail_msg = msg.format(
                dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
            )
            self.assertEqual(fail_msg, result.message)
            self.assertIsNone(result.data)
            self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_lt_067_passing_status(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Conventional EF < 0.67'
        energy factor = 0.66
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF < 0.67"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Natural gas' fuel type
        energy_factor = 0.66

        kwargs = {
            "remrate_target__hot_water__type": 1,
            "remrate_target__hot_water__fuel_type": 1,
            "remrate_target__hot_water__energy_factor": energy_factor,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
        self.assertIn(
            dominant["dominant_hot_water"]["fuel"].lower(),
            ["Natural gas".lower(), "Propane".lower()],
        )
        self.assertLess(dominant["dominant_hot_water"]["energy_factor"], 0.67)
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertIsNone(result.data)

    def test_gncwhmrs_water_heater_gas_conventional_gte_067_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water of type 'Gas Conventional EF ≥ 0.67'
        is NOT 'Conventional',
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.67"}
        # 21 = 'Integrated' h2O_heater_type
        kwargs = {"remrate_target__hot_water__type": 21}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("Conventional", dominant["dominant_hot_water"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_gte_067_fuel_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment fuel type for dominant_hot_water of type 'Gas Conventional EF ≥ 0.67'
        is NOT in ['Natural gas', 'Propane']
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.67"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {"remrate_target__hot_water__type": 1, "remrate_target__hot_water__fuel_type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
        self.assertNotIn(
            dominant["dominant_hot_water"]["fuel"], ["Natural gas".lower(), "Propane".lower()]
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_gte_067_insufficient_energy_factor(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Conventional EF ≥ 0.67'
        energy factor >= 0.67
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.67"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Natural gas' fuel type
        energy_factors = [0.66]
        for energy_factor in energy_factors:
            kwargs = {
                "remrate_target__hot_water__type": 1,
                "remrate_target__hot_water__fuel_type": 1,
                "remrate_target__hot_water__energy_factor": energy_factor,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
            self.assertIn(
                dominant["dominant_hot_water"]["fuel"].lower(),
                ["Natural gas".lower(), "Propane".lower()],
            )
            self.assertLess(dominant["dominant_hot_water"]["energy_factor"], 0.70)
            self.assertLess(dominant["dominant_hot_water"]["energy_factor"], 0.67)
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            msg = (
                "Primary water heater '{}' in REM/Rate does not align with checklist "
                "answer of '{}'"
            )
            fail_msg = msg.format(
                dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
            )
            self.assertEqual(fail_msg, result.message)
            self.assertIsNone(result.data)
            self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_gte_067_passing_status(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Conventional EF ≥ 0.67'
        energy factor >= 0.67
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.67"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Natural gas' fuel type
        energy_factors = [0.67, 0.69]
        for energy_factor in energy_factors:
            kwargs = {
                "remrate_target__hot_water__type": 1,
                "remrate_target__hot_water__fuel_type": 1,
                "remrate_target__hot_water__energy_factor": energy_factor,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
            self.assertIn(
                dominant["dominant_hot_water"]["fuel"].lower(),
                ["Natural gas".lower(), "Propane".lower()],
            )
            self.assertGreaterEqual(dominant["dominant_hot_water"]["energy_factor"], 0.67)
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)
            self.assertIsNone(result.data)

    def test_gncwhmrs_water_heater_gas_conventional_gte_070_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water of type 'Gas Conventional EF ≥ 0.70'
        is NOT 'Conventional',
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.70"}
        # 21 = 'Integrated' h2O_heater_type
        kwargs = {"remrate_target__hot_water__type": 21}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("Conventional", dominant["dominant_hot_water"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_gte_070_fuel_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment fuel type for dominant_hot_water of type 'Gas Conventional EF ≥ 0.70'
        is NOT in ['Natural gas', 'Propane']
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.70"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {"remrate_target__hot_water__type": 1, "remrate_target__hot_water__fuel_type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
        self.assertNotIn(
            dominant["dominant_hot_water"]["fuel"], ["Natural gas".lower(), "Propane".lower()]
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_gte_070_insufficient_energy_factor(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Conventional EF ≥ 0.70'
        energy factor >= 0.67
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.70"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Natural gas' fuel type
        energy_factors = [0.69]
        for energy_factor in energy_factors:
            kwargs = {
                "remrate_target__hot_water__type": 1,
                "remrate_target__hot_water__fuel_type": 1,
                "remrate_target__hot_water__energy_factor": energy_factor,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
            self.assertIn(
                dominant["dominant_hot_water"]["fuel"].lower(),
                ["Natural gas".lower(), "Propane".lower()],
            )
            self.assertLess(dominant["dominant_hot_water"]["energy_factor"], 0.70)
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertFalse(result.status)
            msg = (
                "Primary water heater '{}' in REM/Rate does not align with checklist "
                "answer of '{}'"
            )
            fail_msg = msg.format(
                dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
            )
            self.assertEqual(fail_msg, result.message)
            self.assertIsNone(result.data)
            self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_conventional_gte_070_passing_status(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Conventional EF ≥ 0.70'
        energy factor >= 0.70
        """
        input_values = {"neea-water_heater_tier": "Gas Conventional EF ≥ 0.70"}
        # 1 = 'Conventional' h2O_heater_type
        # 3 = 'Natural gas' fuel type
        energy_factors = [0.70, 0.75]
        for energy_factor in energy_factors:
            kwargs = {
                "remrate_target__hot_water__type": 1,
                "remrate_target__hot_water__fuel_type": 1,
                "remrate_target__hot_water__energy_factor": energy_factor,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertEqual("Conventional", dominant["dominant_hot_water"]["type"])
            self.assertIn(
                dominant["dominant_hot_water"]["fuel"].lower(),
                ["Natural gas".lower(), "Propane".lower()],
            )
            self.assertGreaterEqual(dominant["dominant_hot_water"]["energy_factor"], 0.70)
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)
            self.assertIsNone(result.data)

    def test_gncwhmrs_water_heater_gas_tankless_gte_082_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water of type 'Gas Tankless EF ≥ 0.82'
        is NOT 'Instant water heater',
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.82"}
        # 21 = 'Integrated' h2O_heater_type
        kwargs = {"remrate_target__hot_water__type": 21}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("Conventional", dominant["dominant_hot_water"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_tankless_gte_082_fuel_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment fuel type for dominant_hot_water of type 'Gas Tankless EF ≥ 0.82'
        is NOT in ['Natural gas', 'Propane']
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.82"}
        # 1 = 'Instant water heater' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {"remrate_target__hot_water__type": 3, "remrate_target__hot_water__fuel_type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Instant water heater", dominant["dominant_hot_water"]["type"])
        self.assertNotIn(
            dominant["dominant_hot_water"]["fuel"], ["Natural gas".lower(), "Propane".lower()]
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_tankless_gte_082_insufficient_energy_factor(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Tankless EF ≥ 0.82'
        energy factor >= 0.67
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.82"}
        # 1 = 'Instant water heater' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {
            "remrate_target__hot_water__type": 3,
            "remrate_target__hot_water__fuel_type": 1,
            "remrate_target__hot_water__energy_factor": 0.81,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Instant water heater", dominant["dominant_hot_water"]["type"])
        self.assertIn(
            dominant["dominant_hot_water"]["fuel"].lower(),
            ["Natural gas".lower(), "Propane".lower()],
        )
        self.assertLess(dominant["dominant_hot_water"]["energy_factor"], 0.82)
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_tankless_gte_082_passing_status(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Tankless EF ≥ 0.82'
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.82"}
        # 1 = 'Instant water heater' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        energy_factors = [0.82, 0.89]
        for energy_factor in energy_factors:
            kwargs = {
                "remrate_target__hot_water__type": 3,
                "remrate_target__hot_water__fuel_type": 1,
                "remrate_target__hot_water__energy_factor": energy_factor,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertEqual("Instant water heater", dominant["dominant_hot_water"]["type"])
            self.assertIn(
                dominant["dominant_hot_water"]["fuel"].lower(),
                ["Natural gas".lower(), "Propane".lower()],
            )
            self.assertGreaterEqual(dominant["dominant_hot_water"]["energy_factor"], 0.82)
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)
            self.assertIsNone(result.data)

    def test_gncwhmrs_water_heater_gas_tankless_gte_090_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment type for dominant_hot_water of type 'Gas Tankless EF ≥ 0.90'
        is NOT 'Instant water heater',
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.90"}
        # 21 = 'Integrated' h2O_heater_type
        kwargs = {"remrate_target__hot_water__type": 21}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)
        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertNotIn("Conventional", dominant["dominant_hot_water"]["type"])
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_tankless_gte_090_fuel_type_mismatch(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment fuel type for dominant_hot_water of type 'Gas Tankless EF ≥ 0.90'
        is NOT in ['Natural gas', 'Propane']
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.90"}
        # 1 = 'Instant water heater' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {"remrate_target__hot_water__type": 3, "remrate_target__hot_water__fuel_type": 3}
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Instant water heater", dominant["dominant_hot_water"]["type"])
        self.assertNotIn(
            dominant["dominant_hot_water"]["fuel"], ["Natural gas".lower(), "Propane".lower()]
        )
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_tankless_gte_090_insufficient_energy_factor(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Tankless EF ≥ 0.90'
        energy factor >= 0.67
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.90"}
        # 1 = 'Instant water heater' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        kwargs = {
            "remrate_target__hot_water__type": 3,
            "remrate_target__hot_water__fuel_type": 1,
            "remrate_target__hot_water__energy_factor": 0.89,
        }
        floorplan = floorplan_with_remrate_factory(**kwargs)
        EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        self.assertEqual(eep_program.slug, "neea-bpa")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertIsNotNone(home_status.floorplan)
        self.assertFalse(home_status.certification_date)

        sim = floorplan.remrate_target
        dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
        self.assertEqual("Instant water heater", dominant["dominant_hot_water"]["type"])
        self.assertIn(
            dominant["dominant_hot_water"]["fuel"].lower(),
            ["Natural gas".lower(), "Propane".lower()],
        )
        self.assertLess(dominant["dominant_hot_water"]["energy_factor"], 0.90)
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        msg = (
            "Primary water heater '{}' in REM/Rate does not align with checklist " "answer of '{}'"
        )
        fail_msg = msg.format(
            dominant["dominant_hot_water"]["type"], input_values["neea-water_heater_tier"]
        )
        self.assertEqual(fail_msg, result.message)
        self.assertIsNone(result.data)
        self.assertEqual(result.url, kwrgs["checklist_url"])

    def test_gncwhmrs_water_heater_gas_tankless_gte_090_passing_status(self):
        """
        Test for get_neea_checklist_water_heater_matches_remrate_status. simulation's
        installed equipment for dominant_hot_water of type 'Gas Tankless EF ≥ 0.90'
        """
        input_values = {"neea-water_heater_tier": "Gas Tankless EF ≥ 0.90"}
        # 1 = 'Instant water heater' h2O_heater_type
        # 3 = 'Fuel oil' fuel type
        energy_factors = [0.90, 0.99]
        for energy_factor in energy_factors:
            kwargs = {
                "remrate_target__hot_water__type": 3,
                "remrate_target__hot_water__fuel_type": 1,
                "remrate_target__hot_water__energy_factor": energy_factor,
            }
            floorplan = floorplan_with_remrate_factory(**kwargs)
            EEPProgram.objects.filter(owner__name="EEP4").update(slug="neea-bpa")
            eep_program = EEPProgram.objects.get(owner__name="EEP4")
            self.assertEqual(eep_program.slug, "neea-bpa")
            EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(floorplan=floorplan)
            home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
            self.assertIsNotNone(home_status.floorplan)
            self.assertFalse(home_status.certification_date)

            sim = floorplan.remrate_target
            dominant = sim.installedequipment_set.get_dominant_values(sim.id)[sim.id]
            self.assertEqual("Instant water heater", dominant["dominant_hot_water"]["type"])
            self.assertIn(
                dominant["dominant_hot_water"]["fuel"].lower(),
                ["Natural gas".lower(), "Propane".lower()],
            )
            self.assertGreaterEqual(dominant["dominant_hot_water"]["energy_factor"], 0.90)
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_checklist_water_heater_matches_remrate_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)
            self.assertIsNone(result.data)

    def test_nbris_with_certification_date(self):
        """
        Test for get_neea_bpa_refrigerator_installed_status. home status has a certification_date.
        expected back None.
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            certification_date=datetime.date(2018, 1, 1)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.certification_date)
        result = eep_program.get_neea_bpa_refrigerator_installed_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_nbris_wrong_source_question_slug(self):
        """Test for get_neea_bpa_refrigerator_installed_status."""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Heat Pump"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_refrigerator_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbris_no_required_slug_supplied(self):
        """
        Test for get_neea_bpa_refrigerator_installed_status.
        required_question_slug = 'refrigerator-combo' is not included in input_values causing
        a Failing Status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_std_refrigerators_installed": "Yes"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_refrigerator_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.status)
        self.assertEqual(
            result.message,
            "Brand & Model Number are required if an ENERGY STAR refrigerator " "is installed.",
        )
        self.assertEqual(kwrgs["checklist_url"], result.url)

    def test_nbris_passing_status(self):
        """Test for get_neea_bpa_refrigerator_installed_status.  Passing Status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_std_refrigerators_installed": "Yes", "refrigerator-combo": "val"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_refrigerator_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertEqual(input_values["refrigerator-combo"], result.data)

    def test_nbcwis_with_certification_date(self):
        """
        Test for get_neea_bpa_clothes_washer_installed_status. home status has a certification_date.
        expected back None.
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            certification_date=datetime.date(2018, 1, 1)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.certification_date)
        result = eep_program.get_neea_bpa_clothes_washer_installed_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_nbcwis_wrong_source_question_slug(self):
        """
        Test for get_neea_bpa_clothes_washer_installed_status.
        'estar_front_load_clothes_washer_installed' key not in input values.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Heat Pump"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_clothes_washer_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbcwis__wrong_source_question_value(self):
        """
        Test for get_neea_bpa_clothes_washer_installed_status.
        'estar_front_load_clothes_washer_installed' value is not 'Yes'.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_front_load_clothes_washer_installed": "N/A"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_clothes_washer_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbcwis_wrong_required_question_slug(self):
        """
        Test for get_neea_bpa_clothes_washer_installed_status.
        'clothes-washer-combo' key is not in input_values.
        expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_front_load_clothes_washer_installed": "Yes"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_clothes_washer_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        self.assertEqual(
            result.message,
            "Brand & Model Number are required if an ENERGY STAR clothes washer is " "installed.",
        )
        self.assertEqual(kwrgs["checklist_url"], result.url)

    def test_nbcwis_passing_status(self):
        """Test for get_neea_bpa_clothes_washer_installed_status. expected back Passing status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {
            "estar_front_load_clothes_washer_installed": "Yes",
            "clothes-washer-combo": "value",
        }
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_clothes_washer_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertEqual(input_values["clothes-washer-combo"], result.data)

    def test_nbcdis_with_certification_date(self):
        """
        Test for get_neea_bpa_clothes_dryer_installed_status. home status has a certification_date.
        expected back None.
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            certification_date=datetime.date(2018, 1, 1)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.certification_date)
        result = eep_program.get_neea_bpa_clothes_dryer_installed_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_nbcdis_wrong_source_question_slug(self):
        """
        Test for get_neea_bpa_clothes_dryer_installed_status.
        'neea-clothes_dryer_tier' key not in input values.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-heating_source": "Hydronic Radiant Heat Pump"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_clothes_dryer_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbcdis_wrong_source_question_value(self):
        """
        Test for get_neea_bpa_clothes_dryer_installed_status.
        'neea-clothes_dryer_tier' value is not 'Yes'.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"neea-clothes_dryer_tier": "N/A"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_clothes_dryer_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbcdis_wrong_required_question_slug(self):
        """
        Test for get_neea_bpa_clothes_dryer_installed_status.
        'clothes-dryer-combo' key is not in input_values.
        expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        source_question_values = ["ENERGY STAR®", "Tier 2", "Tier 3"]
        for value in source_question_values:
            input_values = {"neea-clothes_dryer_tier": value}
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_bpa_clothes_dryer_installed_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertIsNone(result.data)
            self.assertEqual(
                result.message,
                "Brand & Model Number are required if clothes dryer is one of: "
                "ENERGY STAR®, Tier2, or Tier 3.",
            )
            self.assertEqual(kwrgs["checklist_url"], result.url)

    def test_nbcdis_passing_status(self):
        """Test for get_neea_bpa_clothes_dryer_installed_status. expected back Passing status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        source_question_values = ["ENERGY STAR®", "Tier 2", "Tier 3"]
        for value in source_question_values:
            input_values = {"neea-clothes_dryer_tier": value, "clothes-dryer-combo": "value"}
            kwrgs = {"checklist_url": "url"}
            result = eep_program.get_neea_bpa_clothes_dryer_installed_status(
                home_status.home, home_status, input_values, **kwrgs
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.status)
            self.assertEqual(input_values["clothes-dryer-combo"], result.data)

    def test_nbdis_with_certification_date(self):
        """
        Test for get_neea_bpa_dishwasher_installed_status. home status has a certification_date.
        expected back None.
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            certification_date=datetime.date(2018, 1, 1)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.certification_date)
        result = eep_program.get_neea_bpa_dishwasher_installed_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_nbdis_wrong_source_question_slug(self):
        """
        Test for get_neea_bpa_dishwasher_installed_status.
        'estar_dishwasher_installed' key not in input values.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_front_load_clothes_washer_installed": "Hydronic Radiant Heat Pump"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_dishwasher_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbdis_wrong_source_question_value(self):
        """
        Test for get_neea_bpa_dishwasher_installed_status.
        'estar_dishwasher_installed' value is not 'Yes'.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_dishwasher_installed": "N/A"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_dishwasher_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbdis_wrong_required_question_slug(self):
        """
        Test for get_neea_bpa_dishwasher_installed_status.
        'clothes-washer-combo' key is not in input_values.
        expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_dishwasher_installed": "Yes"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_dishwasher_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        self.assertEqual(
            result.message,
            "Brand & Model Number are required if an ENERGY STAR dishwasher is " "installed.",
        )
        self.assertEqual(kwrgs["checklist_url"], result.url)

    def test_nbdis_passing_status(self):
        """Test for get_neea_bpa_dishwasher_installed_status. expected back Passing status"""
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_dishwasher_installed": "Yes", "dishwasher-combo": "value"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_dishwasher_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertEqual(input_values["dishwasher-combo"], result.data)

    def test_nbcstis_with_certification_date(self):
        """
        Test for get_neea_bpa_checklist_smart_thermostat_installed_status. home status has a
        certification_date. expected back None.
        """
        import datetime

        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        EEPProgramHomeStatus.objects.filter(eep_program=eep_program).update(
            certification_date=datetime.date(2018, 1, 1)
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertTrue(home_status.certification_date)
        result = eep_program.get_neea_bpa_checklist_smart_thermostat_installed_status(
            home_status.home, home_status, {}
        )
        self.assertIsNone(result)

    def test_nbcstis_wrong_source_question_slug(self):
        """
        Test for get_neea_bpa_checklist_smart_thermostat_installed_status.
        'estar_dishwasher_installed' key not in input values.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"estar_front_load_clothes_washer_installed": "Hydronic Radiant Heat Pump"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_checklist_smart_thermostat_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbcstis_wrong_source_question_value(self):
        """
        Test for get_neea_bpa_checklist_smart_thermostat_installed_status.
        'estar_dishwasher_installed' value is not 'Yes'.
        expected back None
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"smart_thermostat_installed": "N/A"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_checklist_smart_thermostat_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNone(result)

    def test_nbcstis_wrong_required_question_slug(self):
        """
        Test for get_neea_bpa_checklist_smart_thermostat_installed_status.
        'clothes-washer-combo' key is not in input_values.
        expected back Failing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"smart_thermostat_installed": "Yes"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_checklist_smart_thermostat_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertIsNone(result.data)
        self.assertEqual(
            result.message, "Brand & Model Number are required if smart thermostat is installed."
        )
        self.assertEqual(kwrgs["checklist_url"], result.url)

    def test_nbcstis_passing_status(self):
        """
        Test for get_neea_bpa_checklist_smart_thermostat_installed_status.
        expected back Passing status
        """
        eep_program = EEPProgram.objects.get(owner__name="EEP4")
        home_status = EEPProgramHomeStatus.objects.get(eep_program=eep_program)
        self.assertFalse(home_status.certification_date)
        input_values = {"smart_thermostat_installed": "Yes", "smart-thermostat-combo": "value"}
        kwrgs = {"checklist_url": "url"}
        result = eep_program.get_neea_bpa_checklist_smart_thermostat_installed_status(
            home_status.home, home_status, input_values, **kwrgs
        )
        self.assertIsNotNone(result)
        self.assertTrue(result.status)
        self.assertEqual(input_values["smart-thermostat-combo"], result.data)
