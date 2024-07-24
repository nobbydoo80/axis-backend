__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.utils.timezone import now
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.incentive_payment.models import IncentiveDistribution
from axis.home.models import EEPProgramHomeStatus

from ...company.models import SponsorPreferences

from ...core.tests.factories import eep_admin_factory, builder_admin_factory
from ...eep_program.models import EEPProgram

from ...geographic.tests.factories import real_city_factory
from ...incentive_payment.tests.factories import (
    basic_pending_builder_incentive_distribution_factory,
)
from ...relationship.models import Relationship

from ..models import BuilderAgreement
from ..tasks import update_lots_paid_count, audit_builder_agreements
from .factories import builder_agreement_factory


class BuilderAgreementTaskTests(AxisTestCase):
    """Test out company application"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        city = real_city_factory(name="Gilbert", state="AZ")
        eep_user = eep_admin_factory(company__city=city, company__slug="aps")
        builder_user = builder_admin_factory(company__city=city)

        SponsorPreferences.objects.get_or_create(
            sponsor=eep_user.company, sponsored_company=builder_user.company
        )

        distribution = basic_pending_builder_incentive_distribution_factory(
            company=eep_user.company, customer=builder_user.company, ipp_count=3
        )

        eep_program = EEPProgram.objects.first()

        Relationship.objects.create_mutual_relationships(eep_user.company, builder_user.company)
        builder_agreement_factory(
            company=eep_user.company,
            builder_org=builder_user.company,
            eep_programs=[eep_program],
            lots_paid=0,
        )

        distribution.is_paid = True
        distribution.paid_date = now()
        distribution.status = 2
        distribution.total = sum(list(distribution.ippitem_set.values_list("cost", flat=True)))
        distribution.check_number = "001"
        distribution.save()

    def test_update_lots_paid_count(self):
        incentive_distribution = IncentiveDistribution.objects.all()[0]

        company = incentive_distribution.company
        customer = incentive_distribution.customer
        builder_agreements = BuilderAgreement.objects.filter(company=company, builder_org=customer)
        self.assertEqual(builder_agreements.count(), 1)

        # Deliberately invalidated the lots_paid so that we can test the task output
        MAGIC_NUMBER = 87654321
        builder_agreements.update(lots_paid=MAGIC_NUMBER)

        # Task execution
        update_lots_paid_count(incentive_distribution.id)

        for builder_agreement in builder_agreements:
            expected = EEPProgramHomeStatus.objects.filter_homes_for_builder_agreement_paid(
                builder_agreement
            ).count()
            self.assertGreater(expected, 0)
            self.assertNotEqual(builder_agreement.lots_paid, MAGIC_NUMBER)
            self.assertEqual(builder_agreement.lots_paid, expected)

    def test_audit(self):
        audit_builder_agreements()
