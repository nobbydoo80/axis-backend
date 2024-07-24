"""test_triggers.py: Django relationships"""

__author__ = "Steven Klass"
__date__ = "3/16/14 11:04 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
from unittest import mock

from django.apps import apps

from axis.company.models import SponsorPreferences, Company
from axis.company.tests.factories import (
    provider_organization_factory,
    builder_organization_factory,
)
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import custom_home_factory
from ..models import Relationship

log = logging.getLogger(__name__)

customer_hirl_app = apps.get_app_config("customer_hirl")


class RelationshipTriggerTests(AxisTestCase):
    """Test out EPA Registry app"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        from axis.company.tests.factories import hvac_organization_factory
        from axis.home.tests.factories import eep_program_custom_home_status_factory

        hvac_organization_factory()

        status = eep_program_custom_home_status_factory(
            eep_program__require_hvac_relationship=True,
            eep_program__require_hvac_assigned_to_home=True,
            eep_program__no_close_dates=True,
        )

        assert status.eep_program.require_hvac_relationship
        assert status.eep_program.require_hvac_assigned_to_home

        assert status.state == "inspection", "We need an inspection home status"
        eligibile = status.report_eligibility_for_certification()
        assert len(eligibile) == 1, "Only one requirement"
        assert (
            "requires a HVAC Contractor" in eligibile[0]
        ), "Looking for a hvac relationship requirement"

    def test_post_save_customer_company_add_company(self):
        """A home is added with an program that requires it has a relationship with
        a builder.  Once the EEP Program owner has a relationship the state should change"""
        status = EEPProgramHomeStatus.objects.all()[0]
        status.eep_program.require_hvac_relationship = False
        status.eep_program.save()

        eligibile = status.report_eligibility_for_certification()
        self.assertEqual(len(eligibile), 1)
        self.assertIn("requires a HVAC Contractor", eligibile[0])
        self.assertEqual(status.state, "inspection")

        hvac = Company.objects.filter(company_type=Company.HVAC_COMPANY_TYPE)[0]
        self.assertEqual(hvac.is_customer, True)

        # Add the relationship this should dispatch the post save trigger.
        Relationship.objects.validate_or_create_relations_to_entity(status.home, hvac)

        self.assertEqual(status.state, "inspection")

        status = EEPProgramHomeStatus.objects.all()[0]
        self.assertEqual(status.pct_complete, 100.0)
        self.assertEqual(status.is_eligible_for_certification(), True)
        self.assertEqual(status.state, "certification_pending")

    def test_post_save_home_require_relationship(self):
        """A home is added with an program that requires builder. When a relationship is added
        verify the home progresses to the next state."""

        status = EEPProgramHomeStatus.objects.all()[0]
        self.assertEqual(status.state, "inspection")

        hvac = Company.objects.filter(company_type=Company.HVAC_COMPANY_TYPE)[0]
        self.assertEqual(hvac.is_customer, True)

        Relationship.objects.create_mutual_relationships(status.company, hvac)
        Relationship.objects.validate_or_create_relations_to_entity(status.home, hvac)
        Relationship.objects.validate_or_create_relations_to_entity(status.eep_program.owner, hvac)

        self.assertIn(status.eep_program.owner, hvac.relationships.get_companies())
        self.assertEqual(hvac in status.eep_program.owner.relationships.get_companies(), False)
        self.assertEqual(status.eep_program.owner.is_eep_sponsor, True)
        self.assertEqual(status.eep_program.require_hvac_relationship, True)

        eligible = status.report_eligibility_for_certification()
        self.assertEqual(len(eligible), 1)
        self.assertIn("not have an association with any of the HVAC companies.", eligible[0])
        self.assertEqual(status.state, "inspection")

        # Add the relationship this should dispatch the post save trigger.
        Relationship.objects.validate_or_create_relations_to_entity(hvac, status.eep_program.owner)

        status = EEPProgramHomeStatus.objects.all()[0]
        eligible = status.report_eligibility_for_certification()

        self.assertEqual(status.pct_complete, 100.0)
        self.assertEqual(status.is_eligible_for_certification(), True)
        self.assertEqual(status.state, "certification_pending")

    def test_post_save_company_remove_relationship(self):
        """A home is added with an program that requires it has a relationship with
        a builder. When a relationship changes verify the home can't progress"""

        status = EEPProgramHomeStatus.objects.all()[0]
        status.eep_program.require_hvac_relationship = False
        status.eep_program.save()

        eligibile = status.report_eligibility_for_certification()
        self.assertEqual(len(eligibile), 1)
        self.assertIn("requires a HVAC Contractor", eligibile[0])
        self.assertEqual(status.state, "inspection")

        hvac = Company.objects.filter(company_type=Company.HVAC_COMPANY_TYPE)[0]
        self.assertEqual(hvac.is_customer, True)

        # Add the relationship this should dispatch the post save trigger.
        Relationship.objects.validate_or_create_relations_to_entity(status.home, hvac)
        status = EEPProgramHomeStatus.objects.all()[0]
        self.assertEqual(status.state, "certification_pending")

        # HERE IS WHERE WE STOP!!  WHAT HAPPENS WHEN WE DELETE???

    @mock.patch("axis.messaging.messages.ModernMessage.send")
    def test_notify_sponsors_about_new_relationships_without_affiliation(self, send_message):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        provider_company = provider_organization_factory(name="Provider", slug="provider_company")

        builder_organization = builder_organization_factory()
        Relationship.objects.create_mutual_relationships(
            hirl_company, builder_organization, force=True
        )
        send_message.assert_called_once()

        with self.subTest("Check with non HIRL company"):
            Relationship.objects.create_mutual_relationships(
                provider_company, builder_organization, force=True
            )

            send_message.assert_called_once()

        home = custom_home_factory()

        with self.subTest("Do not do anything with non company relations"):
            Relationship.objects.validate_or_create_relations_to_entity(
                entity=home,
                direct_relation=hirl_company,
                force=True,
            )

            send_message.assert_called_once()

        with self.subTest("Call with existing affiliation"):
            builder_organization2 = builder_organization_factory()
            SponsorPreferences.objects.create(
                sponsor=hirl_company, sponsored_company=builder_organization2
            )
            Relationship.objects.create_mutual_relationships(
                hirl_company, builder_organization2, force=True
            )
            send_message.assert_called_once()
