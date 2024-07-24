"""test_candidate_import.py - Axis"""

import logging
import os

from django.core import management

from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.company.models import Company
from axis.customer_neea.neea_data_report.models import NEEACertification, Candidate
from axis.customer_neea.tests.mixins import CustomerNEEABaseTestMixin

from axis.home.models import EEPProgramHomeStatus, Home

log = logging.getLogger(__name__)

TEST_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "candidate_neea_short.csv"))

__author__ = "Steven K"
__date__ = "2/28/21 09:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class CustomerNEEADataReportTests(CustomerNEEABaseTestMixin, AxisTestCase):
    @classmethod
    def setUpTestData(cls):
        super(CustomerNEEADataReportTests, cls).setUpTestData()

        from axis.company.tests.factories import eep_organization_factory
        from axis.eep_program.models import EEPProgram
        from axis.geocoder.models import Geocode
        from axis.home.tests.factories import (
            custom_home_factory,
            eep_program_custom_home_status_factory,
        )
        from axis.relationship.models import Relationship

        resnet = eep_organization_factory(
            slug="eep-resnet", is_customer=True, name="RESNET", city=cls.city
        )

        companies = [cls.neea, resnet]
        Relationship.objects.create_mutual_relationships(*companies)

        management.call_command(
            "build_program", "-p", "resnet-registry-data", "-r", "rater", stdout=DevNull()
        )
        resnet_program = EEPProgram.objects.get()

        # Home exists w certification
        addr = {
            "street_line1": "4825 NE 17th Ave",
            "street_line2": None,
            "city": cls.city,
            "state": "OR",
            "zipcode": "97211",
        }
        matches = Geocode.objects.get_matches(raw_address=None, **addr)
        assert len(matches) == 1, "Bad geocode we need one we got {} - {}".format(
            len(matches), addr
        )
        addr.update({"geocode": True, "builder_org": cls.builder.company})
        home = custom_home_factory(**addr)
        eep_program_custom_home_status_factory(
            home=home, eep_program=resnet_program, company=resnet_program.owner, state="complete"
        )

        # Home exists w/o certification and should align # Home ID 115160
        addr = {
            "street_line1": "12144 NW Schall St",
            "street_line2": None,
            "city": cls.city,
            "state": "OR",
            "zipcode": "97229",
        }
        matches = Geocode.objects.get_matches(raw_address=None, **addr)
        assert len(matches) == 1, "Bad geocode we need one we got {} - {}".format(
            len(matches), addr
        )
        addr.update({"geocode": True, "builder_org": cls.builder.company})
        custom_home_factory(**addr)

        # Home does not exist (no cert obviously)
        addr = {
            "street_line1": "3282 NW Kinsley Ter",  # Home ID 51736 (Delete it)
            "street_line2": None,
            "city": cls.city,
            "state": "OR",
            "zipcode": "97229",
        }
        matches = Geocode.objects.get_matches(raw_address=None, **addr)
        assert len(matches) == 1, "Bad geocode we need one we got {} - {}".format(
            len(matches), addr
        )

        # Home exists but address is not confirmed
        addr = {
            "street_line1": "6147 SE Failing Rd",  # 6147 NE Failing St - This will require a match
            "street_line2": None,
            "city": cls.city,
            "state": "OR",
            "zipcode": "97215",  # 97215
        }
        matches = Geocode.objects.get_matches(raw_address=None, **addr)
        assert len(matches) == 0, "Bad geocode we need one we got {} - {}".format(
            len(matches), addr, matches
        )
        addr.update({"geocode": True, "builder_org": cls.builder.company})
        home = custom_home_factory(**addr)
        assert home.confirmed_address is False, "Bad address"

        # Multi family  Create one with a street_line2 w/o certification
        addr = {
            "street_line1": "6718 NE Garfield Ave",
            "street_line2": None,
            "city": cls.city,
            "state": "OR",
            "zipcode": "97213",
        }

        matches = Geocode.objects.get_matches(raw_address=None, **addr)
        assert len(matches) == 1, "Bad geocode we need one we got {} - {}".format(
            len(matches), addr
        )
        addr.update({"geocode": True, "builder_org": cls.builder.company, "street_line2": "#103"})

        custom_home_factory(is_multi_family=True, **addr)

    def test_source_import(self):
        """ "This is how the certifications needs to be brought in."""

        self.assertEqual(Home.objects.count(), 4)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)

        self.assertEqual(NEEACertification.objects.count(), 0)
        self.assertEqual(Candidate.objects.count(), 0)

        self.assertEqual(NEEACertification.objects.count(), 0)

        management.call_command("certification_import", "--infile", TEST_FILE)

        self.assertEqual(NEEACertification.objects.count(), 5)

        self.assertEqual(EEPProgramHomeStatus.objects.count(), 4)

        # This bad home address
        self.assertEqual(Candidate.objects.count(), 1)  # This is our bad address
        self.assertEqual(Candidate.objects.get().home.street_line1, "6147 SE Failing Rd")
        self.assertEqual(NEEACertification.objects.filter(home__isnull=True).count(), 1)

    def test_source_no_duplicate_allowed(self):
        """This home already exists with the RESENT program on it."""
        management.call_command("certification_import", "--infile", TEST_FILE)
        self.assertEqual(NEEACertification.objects.count(), 5)

        self.assertEqual(EEPProgramHomeStatus.objects.count(), 4)

        home = Home.objects.get(street_line1="4825 NE 17th Ave")
        self.assertEqual(home.homestatuses.count(), 1)

    def test_start_from_scratch(self):
        """We can wipe out that table and it's resiliant"""

        management.call_command("certification_import", "--infile", TEST_FILE)
        self.assertEqual(NEEACertification.objects.count(), 5)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 4)
        target = EEPProgramHomeStatus.objects.last().id
        self.assertEqual(EEPProgramHomeStatus.objects.get(id=target).annotations.count(), 80)

        NEEACertification.objects.all().delete()
        Candidate.objects.all().delete()
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 4)
        self.assertEqual(EEPProgramHomeStatus.objects.get(id=target).annotations.count(), 80)

        management.call_command("certification_import", "--infile", TEST_FILE)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 4)
        self.assertEqual(EEPProgramHomeStatus.objects.get(id=target).annotations.count(), 80)

    def test_missing_annotations_add(self):
        """ "This will add the annotations as needed."""

        self.assertEqual(Home.objects.count(), 4)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)
        status_id = EEPProgramHomeStatus.objects.get().id
        self.assertEqual(EEPProgramHomeStatus.objects.get(id=status_id).annotations.count(), 0)

        management.call_command("certification_import", "--infile", TEST_FILE)

        self.assertEqual(EEPProgramHomeStatus.objects.get(id=status_id).annotations.count(), 80)

    def test_associations_add(self):
        """ "This will verify the associations exist"""

        self.assertEqual(Home.objects.count(), 4)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 1)
        self.assertEqual(EEPProgramHomeStatus.objects.get().associations.count(), 0)

        management.call_command("certification_import", "--infile", TEST_FILE)
        self.assertEqual(EEPProgramHomeStatus.objects.count(), 4)

        neea = Company.objects.get(slug="neea")
        for status in EEPProgramHomeStatus.objects.all():
            self.assertEqual(status.associations.count(), 1)
            association = status.associations.get()
            self.assertEqual(association.owner, status.eep_program.owner)
            self.assertEqual(association.company, neea)
            self.assertTrue(association.is_active)
