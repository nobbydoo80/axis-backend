"""test_management.py: Django Management Test Commands."""


__author__ = "Steven K"
__date__ = "08/27/2019 16:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import os

from django.core import management

from axis.core.tests.client import AxisClient
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.mixins import ProgramSpecsGenFixtureMixin

log = logging.getLogger(__name__)


class EEPProgramManagementTests(AxisTestCase):
    """Tests for eep_program program builder"""

    def test_aps_2019_tstat(self):
        from axis.core.tests.factories import utility_admin_factory
        from axis.geographic.tests.factories import city_factory

        city = city_factory(name="Gilbert", county__name="Maricopa", county__state="AZ")
        self.aps_user = utility_admin_factory(
            company__is_eep_sponsor=True,
            company__electricity_provider=True,
            company__gas_provider=False,
            company__slug="aps",
            company__city=city,
            company__name="APS",
        )

        management.call_command(
            "build_program", "-p", "aps-energy-star-2019-tstat", stdout=DevNull()
        )
        self.assertEqual(EEPProgram.objects.count(), 1)
        program = EEPProgram.objects.get()
        self.assertEqual(program.allow_metro_sampling, True)
        self.assertEqual(program.allow_sampling, True)
        self.assertEqual(program.builder_incentive_dollar_value, 200.00)
        self.assertEqual(program.enable_standard_disclosure, False)
        self.assertEqual(program.is_active, True)
        self.assertEqual(program.is_legacy, False)
        self.assertEqual(program.is_public, False)
        self.assertEqual(program.is_qa_program, False)
        self.assertEqual(program.manual_transition_on_certify, False)
        self.assertEqual(program.max_hers_score, 100)
        self.assertEqual(program.min_hers_score, 0)
        self.assertEqual(program.name, "APS 2019 + ST Program")
        self.assertEqual(program.opt_in, False)
        self.assertEqual(program.owner.slug, "aps")
        self.assertEqual(program.per_point_adder, 0.00)
        self.assertEqual(program.program_close_warning_date, None)
        self.assertEqual(program.program_end_date, datetime.date(year=2020, month=1, day=1))
        self.assertEqual(program.program_start_date, datetime.date(year=2019, month=8, day=1))
        self.assertEqual(program.program_submit_date, datetime.date(year=2019, month=11, day=15))
        self.assertEqual(program.program_visibility_date, datetime.date(year=2019, month=8, day=1))
        self.assertEqual(program.rater_incentive_dollar_value, 0.00)
        self.assertEqual(program.require_builder_assigned_to_home, True)
        self.assertEqual(program.require_builder_relationship, True)
        self.assertEqual(program.require_ekotrope_data, False)
        self.assertEqual(program.require_floorplan_approval, True)
        self.assertEqual(program.require_hvac_assigned_to_home, False)
        self.assertEqual(program.require_hvac_relationship, False)
        self.assertEqual(program.require_input_data, True)
        self.assertEqual(program.require_model_file, False)
        self.assertEqual(program.require_provider_assigned_to_home, True)
        self.assertEqual(program.require_provider_relationship, True)
        self.assertEqual(program.require_qa_assigned_to_home, False)
        self.assertEqual(program.require_qa_relationship, False)
        self.assertEqual(program.require_rater_assigned_to_home, False)
        self.assertEqual(program.require_rater_of_record, False)
        self.assertEqual(program.require_rater_relationship, False)
        self.assertEqual(program.require_rem_data, False)
        self.assertEqual(program.require_resnet_sampling_provider, False)
        self.assertEqual(program.require_utility_assigned_to_home, True)
        self.assertEqual(program.require_utility_relationship, False)
        self.assertEqual(program.slug, "aps-energy-star-2019-tstat")

    def test_aps_2019_tstat_addon(self):
        from axis.core.tests.factories import utility_admin_factory
        from axis.geographic.tests.factories import city_factory

        city = city_factory(name="Gilbert", county__name="Maricopa", county__state="AZ")
        self.aps_user = utility_admin_factory(
            company__is_eep_sponsor=True,
            company__electricity_provider=True,
            company__gas_provider=False,
            company__slug="aps",
            company__city=city,
            company__name="APS",
        )

        management.call_command(
            "build_program", "-p", "aps-energy-star-2019-tstat-addon", stdout=DevNull()
        )
        self.assertEqual(EEPProgram.objects.count(), 1)
        program = EEPProgram.objects.get()
        self.assertEqual(program.allow_metro_sampling, True)
        self.assertEqual(program.allow_sampling, True)
        self.assertEqual(program.builder_incentive_dollar_value, 30.00)
        self.assertEqual(program.enable_standard_disclosure, False)
        self.assertEqual(program.is_active, True)
        self.assertEqual(program.is_legacy, False)
        self.assertEqual(program.is_public, False)
        self.assertEqual(program.is_qa_program, False)
        self.assertEqual(program.manual_transition_on_certify, False)
        self.assertEqual(program.max_hers_score, 100)
        self.assertEqual(program.min_hers_score, 0)
        self.assertEqual(program.name, "APS 2019 Smart Thermostat ADD")
        self.assertEqual(program.opt_in, False)
        self.assertEqual(program.owner.slug, "aps")
        self.assertEqual(program.per_point_adder, 0.00)
        self.assertEqual(program.program_close_warning_date, None)
        self.assertEqual(program.program_end_date, datetime.date(year=2020, month=1, day=1))
        self.assertEqual(program.program_start_date, datetime.date(year=2019, month=8, day=1))
        self.assertEqual(program.program_submit_date, datetime.date(year=2019, month=11, day=15))
        self.assertEqual(program.program_visibility_date, datetime.date(year=2019, month=8, day=1))
        self.assertEqual(program.rater_incentive_dollar_value, 0.00)
        self.assertEqual(program.require_builder_assigned_to_home, True)
        self.assertEqual(program.require_builder_relationship, True)
        self.assertEqual(program.require_ekotrope_data, False)
        self.assertEqual(program.require_floorplan_approval, True)
        self.assertEqual(program.require_hvac_assigned_to_home, False)
        self.assertEqual(program.require_hvac_relationship, False)
        self.assertEqual(program.require_input_data, True)
        self.assertEqual(program.require_model_file, False)
        self.assertEqual(program.require_provider_assigned_to_home, True)
        self.assertEqual(program.require_provider_relationship, True)
        self.assertEqual(program.require_qa_assigned_to_home, False)
        self.assertEqual(program.require_qa_relationship, False)
        self.assertEqual(program.require_rater_assigned_to_home, False)
        self.assertEqual(program.require_rater_of_record, False)
        self.assertEqual(program.require_rater_relationship, False)
        self.assertEqual(program.require_rem_data, False)
        self.assertEqual(program.require_resnet_sampling_provider, False)
        self.assertEqual(program.require_utility_assigned_to_home, True)
        self.assertEqual(program.require_utility_relationship, False)
        self.assertEqual(program.slug, "aps-energy-star-2019-tstat-addon")

    def dump_program(self, program):
        """Dump the program for testing"""
        for f in EEPProgram._meta.fields:
            field = f.name
            if f.name in ["pk", "id"]:
                continue
            value = getattr(program, f.name)
            if field == "owner":
                field = "owner.slug"
                value = program.owner.slug

            if field == "collection_request" and value is not None:
                print("self.assertIsNotNone(program.%s)" % (field))
                continue

            if isinstance(value, str):
                value = "'{}'".format(value)
            if isinstance(value, datetime.date):
                value = "datetime.date(year=%s, month=%s, day=%s)" % (
                    value.year,
                    value.month,
                    value.day,
                )
            print("self.assertEqual(program.%s, %s)" % (field, value))

    def test_wa_code_study_builder(self):
        """Test out the WA Code Study builder"""
        from axis.core.tests.factories import eep_admin_factory

        eep_admin_factory(company__is_eep_sponsor=True, company__slug="neea", company__name="NEEA")

        management.call_command("build_program", "-p", "wa-code-study", stdout=DevNull())
        self.assertEqual(EEPProgram.objects.count(), 2)
        program = EEPProgram.objects.first()

        # self.dump_program(program)

        self.assertEqual(program.name, "Washington State 2015 Energy Code Compliance Study")
        self.assertEqual(program.is_qa_program, False)
        self.assertEqual(program.owner.slug, "neea")
        self.assertEqual(program.opt_in, False)
        self.assertEqual(program.workflow, None)
        self.assertEqual(program.workflow_default_settings, {})
        self.assertEqual(program.viewable_by_company_type, None)
        self.assertEqual(program.min_hers_score, 0)
        self.assertEqual(program.max_hers_score, 100)
        self.assertEqual(program.per_point_adder, 0.00)
        self.assertEqual(program.builder_incentive_dollar_value, 0.00)
        self.assertEqual(program.rater_incentive_dollar_value, 0.00)
        self.assertIsNotNone(program.collection_request)
        self.assertEqual(program.enable_standard_disclosure, False)
        self.assertEqual(program.require_floorplan_approval, False)
        self.assertEqual(program.comment, "")
        self.assertEqual(program.require_input_data, False)
        self.assertEqual(program.require_rem_data, False)
        self.assertEqual(program.require_model_file, False)
        self.assertEqual(program.require_ekotrope_data, False)
        self.assertEqual(program.manual_transition_on_certify, True)
        self.assertEqual(program.require_rater_of_record, False)
        self.assertEqual(program.require_builder_relationship, True)
        self.assertEqual(program.require_builder_assigned_to_home, True)
        self.assertEqual(program.require_hvac_relationship, False)
        self.assertEqual(program.require_hvac_assigned_to_home, False)
        self.assertEqual(program.require_utility_relationship, False)
        self.assertEqual(program.require_utility_assigned_to_home, False)
        self.assertEqual(program.require_rater_relationship, False)
        self.assertEqual(program.require_rater_assigned_to_home, False)
        self.assertEqual(program.require_provider_relationship, False)
        self.assertEqual(program.require_provider_assigned_to_home, False)
        self.assertEqual(program.require_qa_relationship, False)
        self.assertEqual(program.require_qa_assigned_to_home, False)
        self.assertEqual(program.allow_sampling, True)
        self.assertEqual(program.allow_metro_sampling, True)
        self.assertEqual(program.require_resnet_sampling_provider, False)
        self.assertEqual(program.is_legacy, False)
        self.assertEqual(program.is_public, False)

        # Every once in while we get tripped up on this based on when the test is run.
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        self.assertIn(program.program_visibility_date, [yesterday, today])
        self.assertIn(program.program_visibility_date, [yesterday, today])

        self.assertEqual(program.program_close_date, None)
        self.assertEqual(program.program_submit_date, None)
        self.assertEqual(program.program_end_date, None)
        self.assertEqual(program.program_close_warning_date, None)
        self.assertEqual(program.program_close_warning, None)
        self.assertEqual(program.program_submit_warning_date, None)
        self.assertEqual(program.program_submit_warning, None)
        self.assertEqual(program.is_active, True)
        self.assertEqual(program.slug, "wa-code-study")

    def test_neea_bpa(self):
        from axis.core.tests.factories import eep_admin_factory

        eep_admin_factory(company__is_eep_sponsor=True, company__slug="neea", company__name="NEEA")

        management.call_command("build_program", "-p", "neea-bpa", stdout=DevNull())
        self.assertEqual(EEPProgram.objects.count(), 1)
        program = EEPProgram.objects.get()

        # self.dump_program(program)

        self.assertEqual(program.name, "Utility Incentive V2 – Single Family Performance Path")
        self.assertEqual(program.is_qa_program, False)
        self.assertEqual(program.owner.slug, "neea")
        self.assertEqual(program.opt_in, False)
        self.assertEqual(program.workflow, None)
        self.assertEqual(program.workflow_default_settings, {})
        self.assertEqual(program.viewable_by_company_type, None)
        self.assertEqual(program.min_hers_score, 0)
        self.assertEqual(program.max_hers_score, 100)
        self.assertEqual(program.per_point_adder, 0.00)
        self.assertEqual(program.builder_incentive_dollar_value, 0.00)
        self.assertEqual(program.rater_incentive_dollar_value, 0.00)
        self.assertIsNotNone(program.collection_request)
        self.assertEqual(program.enable_standard_disclosure, False)
        self.assertEqual(program.require_floorplan_approval, False)
        self.assertEqual(program.comment, "")
        self.assertEqual(program.require_input_data, True)
        self.assertEqual(program.require_rem_data, True)
        self.assertEqual(program.require_model_file, False)
        self.assertEqual(program.require_ekotrope_data, False)
        self.assertEqual(program.manual_transition_on_certify, True)
        self.assertEqual(program.require_rater_of_record, False)
        self.assertEqual(program.require_energy_modeler, False)
        self.assertEqual(program.require_field_inspector, False)
        self.assertEqual(program.require_builder_relationship, False)
        self.assertEqual(program.require_builder_assigned_to_home, True)
        self.assertEqual(program.require_hvac_relationship, False)
        self.assertEqual(program.require_hvac_assigned_to_home, True)
        self.assertEqual(program.require_utility_relationship, True)
        self.assertEqual(program.require_utility_assigned_to_home, True)
        self.assertEqual(program.require_rater_relationship, True)
        self.assertEqual(program.require_rater_assigned_to_home, True)
        self.assertEqual(program.require_provider_relationship, False)
        self.assertEqual(program.require_provider_assigned_to_home, False)
        self.assertEqual(program.require_qa_relationship, False)
        self.assertEqual(program.require_qa_assigned_to_home, False)
        self.assertEqual(program.allow_sampling, False)
        self.assertEqual(program.allow_metro_sampling, False)
        self.assertEqual(program.require_resnet_sampling_provider, False)
        self.assertEqual(program.is_legacy, False)
        self.assertEqual(program.is_public, False)
        self.assertEqual(program.program_visibility_date, datetime.date(year=2019, month=4, day=21))
        self.assertEqual(program.program_start_date, datetime.date(year=2019, month=4, day=21))
        self.assertEqual(program.program_close_date, None)
        self.assertEqual(program.program_submit_date, None)
        self.assertEqual(program.program_end_date, None)
        self.assertEqual(program.program_close_warning_date, None)
        self.assertEqual(program.program_close_warning, None)
        self.assertEqual(program.program_submit_warning_date, None)
        self.assertEqual(program.program_submit_warning, None)
        self.assertEqual(program.is_active, True)
        self.assertEqual(program.slug, "neea-bpa")
        self.assertEqual(program.is_multi_family, False)


class ProgramSpecsWriterManagementTests(ProgramSpecsGenFixtureMixin, AxisTestCase):
    """ """

    client_class = AxisClient
    DIR_PATH = "axis/eep_program/program_builder/"
    FILENAME = "foo_bar"
    CLASS_NAME = "MyTestProgram"

    @classmethod
    def tearDownClass(cls):
        super(ProgramSpecsWriterManagementTests, cls).tearDownClass()
        filename = "generated_%s.py" % cls.FILENAME
        module_path = os.path.join(cls.DIR_PATH, filename)
        if os.path.exists(module_path):
            os.remove(module_path)
        else:
            log.info("The file does not exist")

    def test_program_writer(self):
        """Test out program writer"""
        with open(os.devnull, "w") as stdout:
            management.call_command(
                "write_program", "-p", "test-program", "-f", self.FILENAME, stdout=stdout
            )
        filename = "generated_%s.py" % self.FILENAME
        module_path = os.path.join(self.DIR_PATH, filename)
        self.assertTrue(os.path.exists(module_path))
