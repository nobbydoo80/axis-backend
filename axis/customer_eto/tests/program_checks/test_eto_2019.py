"""eto_2019.py: Django """

__author__ = "Steven K"
__date__ = "12/17/2019 14:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import io
import logging
import os
from unittest.mock import patch

from django.core import management
from django.core.files.base import File
from django.utils.timezone import now

from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.tests.factories import (
    eep_organization_factory,
    provider_organization_factory,
    utility_organization_factory,
    rater_organization_factory,
    builder_organization_factory,
    qa_organization_factory,
)
from axis.core.tests.factories import qa_admin_factory, provider_admin_factory
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.customer_eto.calculator.eps import ETO_2019_FUEL_RATES
from axis.customer_eto.strings import ETO_2019_CHECKSUMS
from axis.eep_program.models import EEPProgram
from axis.floorplan.tests.factories import floorplan_with_remrate_factory
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import (
    home_factory,
    eep_program_custom_home_status_factory,
)
from axis.qa.models import QARequirement
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships
from axis.remrate_data.models import UtilityRate
from axis.remrate_data.tests.factories import udrh_simulation_factory
from ...models import ETOAccount

log = logging.getLogger(__name__)


def get_completion_requirements(self):
    return [
        self.get_floorplan_remrate_data_error_status,
        self.get_floorplan_remrate_data_warning_status,
        self.eep_program.get_eto_min_program_version,
        self.eep_program.get_remrate_udhr_check,
        self.eep_program.get_eto_2019_approved_utility_electric_utility,
        self.eep_program.get_eto_2019_approved_utility_gas_utility,
    ]


class ETO2019ProgramTestMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Portland", "OR")

        cls.eto = eep_organization_factory(slug="eto", is_customer=True, name="ETO", city=cls.city)

        cls.peci = provider_organization_factory(
            slug="peci", is_customer=True, name="EPS New Construction", city=cls.city
        )
        provider_admin_factory(company=cls.peci, username="eto_provider_admin")

        cls.pac_pwr = utility_organization_factory(
            slug="pacific-power",
            is_customer=True,
            name="Pacific Power",
            city=cls.city,
            gas_provider=False,
            electricity_provider=True,
        )
        cls.nw_nat = utility_organization_factory(
            slug="nw-natural-gas",
            is_customer=True,
            name="NW Natural Gas",
            city=cls.city,
            gas_provider=True,
            electricity_provider=False,
        )
        cls.rater_company = rater_organization_factory(
            is_customer=True, name="RATER", slug="rater", city=cls.city
        )
        cls.rater_eto_account = ETOAccount.objects.create(
            company=cls.rater_company, account_number="123", ccb_number="87B32"
        )

        cls.builder_company = builder_organization_factory(
            is_customer=True, name="BUILDER", slug="builder", city=cls.city
        )
        ETOAccount.objects.create(company=cls.builder_company, account_number="456")

        management.call_command(
            "build_program",
            "-p",
            "eto-2019",
            "--warn_only",
            "--no_close_dates",
            stdout=DevNull(),
        )
        cls.eep_program = EEPProgram.objects.get(slug="eto-2019")
        cls.eep_program.certifiable_by.add(cls.peci)

        cls.qa = qa_organization_factory(
            slug="csg-qa",
            is_customer=True,
            name="CSG",
            city=cls.city,
        )
        qa_admin_factory(company=cls.qa, username="eto_qa_admin")
        QARequirement.objects.get_or_create(
            qa_company=cls.qa,
            coverage_pct=1,
            gate_certification=True,
            eep_program=cls.eep_program,
        )

        companies = [
            cls.eto,
            cls.qa,
            cls.peci,
            cls.rater_company,
            cls.builder_company,
            cls.pac_pwr,
            cls.nw_nat,
        ]

        Relationship.objects.create_mutual_relationships(*companies)

        GOOD_BLG = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../remrate/tests/sources/ETO2019Gas.blg",
        )

        simulation = udrh_simulation_factory(
            version="15.7.1",
            flavor="rate",
            percent_improvement=0.21,
            udrh_filename=ETO_2019_CHECKSUMS[0][1],
            udrh_checksum=ETO_2019_CHECKSUMS[0][0],
            company=cls.rater_company,
            site__site_label="Portland, OR",
            site__climate_zone="4C",
            building_info__conditioned_area=2200.0,
            building_info__type=1,
            building_info__foundation_type=4,
            building_info__thermal_boundary=3,
            project__name="ETO2019Gas",
            project__property_address="2342 Maybee Ave.",
            project__property_city="Portland",
            project__property_state="OR",
            project__property_zip="97229",
            project__builder_name="BUILDER",
            project__builder_model="ETO2019Gas",
            project__builder_development="Subdivision",
            hot_water__type=3,
            hot_water__fuel_type=1,
            hot_water__energy_factor=0.91,
            air_conditioning__fuel_type=4,
            air_conditioning__type=1,
            heating__fuel_type=1,
            infiltration__mechanical_vent_type=1,
            infiltration__hours_per_day=24,
            infiltration__mechanical_vent_cfm=260,
            hers__score=60,
            duct_system__leakage_test_exemption=False,
            duct_system__leakage_tightness_test=1,
        )
        UtilityRate.objects.filter(fuel_type=4).update(name="PAC-Dec2018")
        UtilityRate.objects.filter(fuel_type=1).update(name="NWN_OR-Dec2018")

        assert simulation.results.udrh_percent_improvement > 0.20, (
            "Percent improvement %.2f" % simulation.results.udrh_percent_improvement
        )
        log.info("Percent improvement %.2f" % simulation.results.udrh_percent_improvement)

        with io.open(GOOD_BLG, "rb") as f:
            cls.floorplan = floorplan_with_remrate_factory(
                remrate_data_file=File(f, name=os.path.basename(GOOD_BLG)),
                name=os.path.splitext(os.path.basename(GOOD_BLG))[0],
                owner=cls.rater_company,
                remrate_target=simulation,
                square_footage=2200,
                subdivision__builder_org=cls.builder_company,
                subdivision__city=cls.city,
                subdivision__name="Subdivision",
            )

        cls.home = home_factory(
            subdivision=cls.floorplan.subdivision_set.first(),
            city=cls.city,
            zipcode=97229,
        )
        cls.home_status = eep_program_custom_home_status_factory(
            home=cls.home,
            floorplan=cls.floorplan,
            eep_program=cls.eep_program,
            company=cls.rater_company,
        )

        create_or_update_spanning_relationships(cls.pac_pwr, cls.home_status.home)
        create_or_update_spanning_relationships(cls.nw_nat, cls.home_status.home)
        create_or_update_spanning_relationships(cls.qa, cls.home_status.home)
        create_or_update_spanning_relationships(cls.peci, cls.home_status.home)

        # missing_checks = cls.home_status.report_eligibility_for_certification()
        # if missing_checks:
        #     print(
        #         "** Warning! Failing ETO-2019 Certification Eligibility Requirements:\n  - "
        #         + "\n  - ".join(missing_checks)
        #         + "\n** End Warning\n"
        #     )

        # assert len(missing_checks) == 0, "Should be ready for cert"


class ETO2019ProgramChecks(ETO2019ProgramTestMixin, CollectionRequestMixin, AxisTestCase):
    def setUp(self):
        method_to_patch = "axis.home.models.EEPProgramHomeStatus.get_completion_requirements"
        self.patcher = patch(method_to_patch, get_completion_requirements)
        self.mock_foo = self.patcher.start()
        self.addCleanup(self.patcher.stop)  # add this line
        missing_checks = self.home_status.report_eligibility_for_certification()
        if missing_checks:
            print(
                "Failing Certification Eligibility Requirements:\n  - "
                + "\n  - ".join(missing_checks)
            )
        self.assertEqual(len(missing_checks), 0)
        self.simulation = self.home_status.floorplan.remrate_target

    def test_get_eto_min_program_version(self):
        self.simulation.version = "15.7"
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("REM data must be version 15.7.1", missing_checks[0])

        self.simulation.version = "15.7.1"
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.simulation.flavor = "foo"
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("REM data must be version 15.7.1", missing_checks[0])

        self.simulation.flavor = "rate"
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

    def test_get_eto_2019_rem_udhr_check(self):
        self.simulation.udrh_filename = "FOOBAR"
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH File used", missing_checks[0])

        self.simulation.udrh_filename = ETO_2019_CHECKSUMS[0][1]
        self.simulation.save()
        self.home_status = EEPProgramHomeStatus.objects.get()
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.simulation.udrh_checksum = "FOO"
        self.simulation.save()
        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Incorrect UDRH associated with as built home", missing_checks[0])

    def test_get_eto_remdata_compare_fields_ventilation_air_cycler(self):
        """REM mechanical ventilation type may not be “Air cycler”"""
        self.assertEqual(
            self.home_status.floorplan.remrate_target.infiltration.mechanical_vent_type,
            1,
        )
        infiltration = self.home_status.floorplan.remrate_target.infiltration

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        infiltration.mechanical_vent_type = 4

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("not be Air Cycler", missing_checks[0])

    def test_get_eto_remdata_compare_fields_ventilation_exists(self):
        """REM Mechanical Ventilation System may not be "none"”"""
        self.assertEqual(
            self.home_status.floorplan.remrate_target.infiltration.mechanical_vent_type,
            1,
        )
        infiltration = self.home_status.floorplan.remrate_target.infiltration

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        infiltration.mechanical_vent_type = 0

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("system should exist", missing_checks[0])

    def test_get_eto_remdata_compare_fields_ventilation_rate(self):
        """REM ventilation rate must equal to or > ASHRAE 62.2 2010: ((# of bdrms+1)*7.5)+(conditioned floor area*.01)”"""
        self.assertEqual(
            self.home_status.floorplan.remrate_target.infiltration.mechanical_vent_cfm,
            260.0,
        )
        infiltration = self.home_status.floorplan.remrate_target.infiltration

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        infiltration.mechanical_vent_cfm = 25.0

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("ASHRAE 62.2 2010", missing_checks[0])

    def test_get_eto_2019_approved_utility_rate_gas(self):
        """Validate gas fuel rate matches an approved list"""
        fuel_rates = dict(ETO_2019_FUEL_RATES)

        # if home_status.home.state == 'WA':
        #     fuel_rates.update(dict(ETO_2019_FUEL_RATES_WA_OVERRIDE))

        self.assertIsNotNone(self.home_status.get_gas_company())

        utility = self.home_status.get_gas_company()
        self.assertIsNotNone(fuel_rates.get(utility.slug))

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.assertEqual(utility.slug, "nw-natural-gas")

        utility = self.simulation.utilityrate_set.filter(fuel_type=1).get()
        self.assertEqual(utility.name, "NWN_OR-Dec2018")

        utility.name = "FOO"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("AXIS gas utility must match EPS", missing_checks[0])

    def test_get_eto_2019_approved_utility_rate_electric(self):
        """Validate electric fuel rate matches an approved list"""
        fuel_rates = dict(ETO_2019_FUEL_RATES)

        self.assertIsNotNone(self.home_status.get_electric_company())

        utility = self.home_status.get_electric_company()
        self.assertIsNotNone(fuel_rates.get(utility.slug))

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        self.assertEqual(utility.slug, "pacific-power")

        utility = self.simulation.utilityrate_set.filter(fuel_type=4).get()
        self.assertEqual(utility.name, "PAC-Dec2018")

        utility.name = "FOO"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("AXIS electric utility must match EPS", missing_checks[0])

    def test_get_eto_2019_approved_utility_gas_utility(self):
        """Validate gas utility is in the list of ok'd utilities"""

        utility = self.home_status.get_gas_company()
        self.assertEqual(utility.slug, "nw-natural-gas")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        utility.slug = "FOO"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("is not an allowed Gas company", missing_checks[0])

    def test_get_eto_2019_approved_utility_electric_utility(self):
        """Validate electric utility is in the list of ok'd utilities"""

        utility = self.home_status.get_electric_company()
        self.assertEqual(utility.slug, "pacific-power")

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        utility.slug = "FOO"
        utility.save()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("is not an allowed Electric company", missing_checks[0])

    def test_get_eto_remdata_compare_fields_cz(self):
        """Validate climate zone in REM – compare to AXIS climate zone"""
        self.assertEqual(self.home_status.floorplan.remrate_target.site.climate_zone, "4C")
        issues = self.simulation.compare_to_home_status(self.home_status)
        self.assertIn("Home: Climate Zone", issues["success"])
        self.assertEqual(issues["warning"], [])

        site = self.home_status.floorplan.remrate_target.site
        site.climate_zone = "999"

        issues = self.simulation.compare_to_home_status(self.home_status)
        self.assertIn("Home: Climate Zone", issues["warning"])
        self.assertNotIn("Home: Climate Zone", issues["success"])

    def test_get_eto_remdata_compare_fields_housing_type(self):
        """REM Housing type must be one of: Single family detached, duplex single unit, townhouse, end unit,
        or townhouse, inside unit"""
        self.assertEqual(self.home_status.floorplan.remrate_target.buildinginfo.type, 1)
        buildinginfo = self.home_status.floorplan.remrate_target.buildinginfo

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        buildinginfo.type = 8
        buildinginfo.save()
        self.home_status = EEPProgramHomeStatus.objects.get()

        self.assertEqual(buildinginfo.type, 8)
        self.assertEqual(self.home_status.floorplan.remrate_target.buildinginfo.type, 8)

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Single family detached", missing_checks[0])

    def test_get_eto_remdata_compare_fields_foundation_type(self):
        """REM foundation type Conditioned Crawlspaces is not allowed"""
        self.assertEqual(self.home_status.floorplan.remrate_target.buildinginfo.foundation_type, 4)
        buildinginfo = self.home_status.floorplan.remrate_target.buildinginfo

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        buildinginfo.foundation_type = 8
        buildinginfo.save()
        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("Conditioned Crawlspaces", missing_checks[0])

    def test_get_eto_remdata_compare_fields_foundation_type_crawl_space(self):
        """If REM Foundation type of enclosed crawl space, then thermal boundary cannot be "REM default"""
        self.assertEqual(self.home_status.floorplan.remrate_target.buildinginfo.foundation_type, 4)
        self.assertEqual(self.home_status.floorplan.remrate_target.buildinginfo.thermal_boundary, 3)
        buildinginfo = self.home_status.floorplan.remrate_target.buildinginfo

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        buildinginfo.foundation_type = 3
        buildinginfo.save()
        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("for Enclosed Crawlspaces", missing_checks[0])

    def test_get_eto_remdata_compare_fields_foundation_type_gt_one(self):
        """If REM Foundation type is "more than one type", then thermal boundary cannot be "REM default" or "N/A" """
        self.assertEqual(self.home_status.floorplan.remrate_target.buildinginfo.foundation_type, 4)
        self.assertEqual(self.home_status.floorplan.remrate_target.buildinginfo.thermal_boundary, 3)
        buildinginfo = self.home_status.floorplan.remrate_target.buildinginfo

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        buildinginfo.foundation_type = 6
        buildinginfo.save()
        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("more than one type", missing_checks[0])

    def test_get_eto_remdata_compare_fields_refrigerator_location(self):
        """REM refrigerator location must be "conditioned" """
        self.assertEqual(
            self.home_status.floorplan.remrate_target.lightsandappliance.refrigerator_location,
            1,
        )
        l_and_a = self.home_status.floorplan.remrate_target.lightsandappliance

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        l_and_a.refrigerator_location = 2
        l_and_a.save()
        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("refrigerator location must", missing_checks[0])

    def test_get_eto_remdata_compare_fields_clothes_dryer_location(self):
        """REM Clothes Dryer location must be "conditioned" """
        self.assertEqual(
            self.home_status.floorplan.remrate_target.lightsandappliance.clothes_dryer_location,
            1,
        )
        l_and_a = self.home_status.floorplan.remrate_target.lightsandappliance

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        l_and_a.clothes_dryer_location = 2
        l_and_a.save()
        self.home_status = EEPProgramHomeStatus.objects.get()

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("clothes dryer location must", missing_checks[0])

    def test_get_eto_remdata_compare_fields_mechanical_ventilation_exhaust_time(self):
        """If REM mechanical ventilation type is Exhaust only, then Hours/day must be 24"""
        self.assertEqual(
            self.home_status.floorplan.remrate_target.infiltration.mechanical_vent_type,
            1,
        )
        infiltration = self.home_status.floorplan.remrate_target.infiltration
        self.assertEqual(infiltration.hours_per_day, 24)

        infiltration.mechanical_vent_type = 2
        infiltration.save()
        self.home_status.floorplan.modified_date = now()  # Update cache key

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        infiltration.hours_per_day = 23

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("must be 24hr/day", missing_checks[0])

    def test_get_eto_remdata_compare_fields_mechanical_ventilation_supply_time(self):
        """If REM mechanical ventilation type is Supply only, then Hours/day must be 24"""
        self.assertEqual(
            self.home_status.floorplan.remrate_target.infiltration.mechanical_vent_type,
            1,
        )
        infiltration = self.home_status.floorplan.remrate_target.infiltration
        self.assertEqual(infiltration.hours_per_day, 24)

        infiltration.mechanical_vent_type = 3
        infiltration.save()
        self.home_status.floorplan.modified_date = now()  # Update cache key

        context = {"user__company": self.home_status.company}
        self.assertFalse(self.home_status.collectedinput_set.filter_for_context(**context).exists())
        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 0)

        infiltration.hours_per_day = 23

        missing_checks = self.home_status.report_eligibility_for_certification()
        self.assertEqual(len(missing_checks), 1)
        self.assertIn("must be 24hr/day", missing_checks[0])
