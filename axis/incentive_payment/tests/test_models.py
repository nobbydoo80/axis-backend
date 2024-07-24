"""factory.py: Django company"""


__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from axis.core.tests.testcases import AxisTestCase
from axis.company.models import Company
from axis.home.models import EEPProgramHomeStatus
from axis.home.signals import eep_program_certified
from axis.home.tests.factories import certified_custom_home_with_basic_eep_factory
from ..models import IncentiveDistribution, IncentivePaymentStatus, IPPItem

log = logging.getLogger(__name__)


class IncentiveDistributionModelTestCase(AxisTestCase):
    """Tests to prove that the IncentiveDistribution model performs as expected."""

    @classmethod
    def setUpTestData(cls):
        from axis.incentive_payment.tests.factories import (
            basic_pending_builder_incentive_distribution_factory,
        )
        from axis.core.tests.factories import (
            builder_admin_factory,
            general_admin_factory,
            utility_admin_factory,
        )
        from axis.geographic.tests.factories import real_city_factory

        city = real_city_factory("Garden City", "KS")
        builder = builder_admin_factory(company__city=city)
        general_admin_factory(company__city=city)
        utility = utility_admin_factory(company__slug="aps", company__city=city)

        for i in range(2):
            basic_pending_builder_incentive_distribution_factory(
                customer=builder.company, company=utility.company, check_number=str(i)
            )

    def test_gains_automatic_invoice_number(self):
        """Verifies that ``save()`` generates the ``invoice_number`` attribute from the slug."""
        company, customer = Company.objects.all()[:2]
        obj = IncentiveDistribution(company=company, customer=customer, slug="UNIQUE", status=1)

        self.assertEqual(obj.invoice_number, None)
        obj.save()

        self.assertNotEqual(obj.invoice_number, None)
        self.assertEqual(bool(obj.invoice_number), True)

    def test_conflicting_check_number_detection_for_existing_obj(self):
        """Verifies that two saved instances can't have the same ``check_number``."""
        obj1, obj2 = IncentiveDistribution.objects.all()[:2]
        obj2.check_number = obj1.check_number

        msg = "IncentiveDistribution with this company and or check number already exists"
        with self.assertRaisesRegex(Exception, msg):
            obj2.save()

    def test_conflicting_check_number_detection_for_new_obj(self):
        """
        Verifies that an in-memory instance with the check number set is caught as a duplicate.
        Previous to this test, the uniqueness was only checked if the object already had an
        auto-incrementing ID assigned to it in the database (was already saved).

        """
        obj1 = IncentiveDistribution.objects.all()[0]
        obj2 = IncentiveDistribution(company=obj1.company, customer=obj1.customer)
        obj2.check_number = obj1.check_number

        msg = "IncentiveDistribution with this company and or check number already exists"
        with self.assertRaisesRegex(Exception, msg):
            obj2.save()

    def test_can_be_deleted(self):
        """
        Verifies that ``can_be_deleted()`` returns true only for the owning company.
        If that company is aps. Our permissions are setup to only give 'delete' perms to aps currently.
        """
        user = self.get_admin_user(company_type="utility")
        bad_user = self.get_admin_user(company_type="builder")
        obj = IncentiveDistribution(company=user.company, customer=bad_user.company)

        user.company.update_permissions("incentive_payment")
        bad_user.company.update_permissions("incentive_payment")

        self.assertEqual(obj.can_be_deleted(user), True)
        self.assertEqual(obj.can_be_deleted(bad_user), False)


class IncentivePaymentStatusTests(AxisTestCase):
    """Validate the process of Incentive Payment Status"""

    @classmethod
    def setUpTestData(cls):
        from axis.incentive_payment.tests.factories import (
            basic_incentive_payment_status_factory,
            basic_pending_builder_incentive_distribution_factory,
        )
        from axis.home.tests.factories import certified_custom_home_with_basic_eep_factory

        # testing certification origination
        certified_custom_home_with_basic_eep_factory(eep_program__no_close_dates=True)
        assert IncentivePaymentStatus.objects.count() == 0
        assert IncentiveDistribution.objects.count() == 0
        assert IPPItem.objects.count() == 0

        # testing states transition
        basic_incentive_payment_status_factory(home_status__eep_program__no_close_dates=True)
        assert IncentivePaymentStatus.objects.count() == 1
        assert IncentivePaymentStatus.objects.get().state == "start"
        assert IncentiveDistribution.objects.count() == 0
        assert IPPItem.objects.count() == 0

        # testing distribution transitions
        basic_pending_builder_incentive_distribution_factory()
        assert IncentivePaymentStatus.objects.count() == 2
        assert IncentivePaymentStatus.objects.last().state == "payment_pending"
        assert IncentiveDistribution.objects.count() == 1
        assert IPPItem.objects.count() == 1

    def setup_incentive_payment_count(self):
        """use when test relies on knowing whether or not an incentive payment was created."""
        self.incentive_payment_ids = list(
            IncentivePaymentStatus.objects.values_list("id", flat=True)
        )
        self.incentive_payment_initial_count = len(self.incentive_payment_ids)

    def test_certification_origination(self):
        """Verify that if a home_stat meet criteria is will propagate to the ipp
        stat and that its right"""
        self.setup_incentive_payment_count()

        def receiver(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        received_signals = []
        eep_program_certified.connect(receiver, sender=EEPProgramHomeStatus)

        self.assertEqual(
            IncentivePaymentStatus.objects.count(), self.incentive_payment_initial_count
        )

        home_stat = certified_custom_home_with_basic_eep_factory(
            eep_program__builder_incentive_dollar_value=100,
            eep_program__slug="SOMETHING_INTERESTING",
            eep_program__owner__slug="aps",
        )

        self.assertEqual(
            home_stat.is_eligible_for_certification(skip_certification_check=True), True
        )
        self.assertEqual(len(received_signals), 1)
        self.assertEqual(received_signals, [eep_program_certified])

        self.assertEqual(
            IncentivePaymentStatus.objects.count(), self.incentive_payment_initial_count + 1
        )
        ipp_stat = IncentivePaymentStatus.objects.exclude(id__in=self.incentive_payment_ids)[0]
        self.assertEqual(ipp_stat.owner.id, home_stat.eep_program.owner.id)
        self.assertEqual(ipp_stat.home_status, home_stat)
        self.assertEqual(ipp_stat.created_on.date(), home_stat.certification_date)
        self.assertEqual(ipp_stat.state, "start")

    def test_non_qualifying_origination(self):
        """Verify that if a home stat does not meet criteria it won't show up"""
        self.setup_incentive_payment_count()

        def receiver(sender, **kwargs):
            received_signals.append(kwargs.get("signal"))

        received_signals = []
        eep_program_certified.connect(receiver, sender=EEPProgramHomeStatus)

        certified_custom_home_with_basic_eep_factory()

        self.assertEqual(len(received_signals), 1)
        self.assertEqual(received_signals, [eep_program_certified])

        self.assertEqual(
            IncentivePaymentStatus.objects.count(), self.incentive_payment_initial_count
        )

    def test_states_transition(self):
        """Test the states transfer"""

        ipp_stat = IncentivePaymentStatus.objects.all()[0]

        # This will normally be done by the user..
        ipp_stat.make_transition("pending_requirements", user=None)

        # The automated post would move this to passing auto checks as there isn't a method for
        # this eep.
        ipp_stat = IncentivePaymentStatus.objects.all()[0]
        self.assertEqual(ipp_stat.state, "ipp_payment_automatic_requirements")

    def test_distribution_transitions(self):
        """Test that once we go to payment pending we track to distribution"""
        distribution = IncentiveDistribution.objects.filter(status=1)[0]
        ipp_stat = distribution.ippitem_set.all()[0].home_status.incentivepaymentstatus
        self.assertEqual(ipp_stat.state, "payment_pending")
        self.assertEqual(distribution.status, 1)
        # Transition
        distribution.status = 2
        distribution.save()
        # Verify
        distribution = IncentiveDistribution.objects.get(id=distribution.id)
        ipp_stat = IncentivePaymentStatus.objects.get(id=ipp_stat.id)
        self.assertEqual(ipp_stat.state, "complete")
        self.assertEqual(distribution.status, 2)

    def test_status_visibility(self):
        """Test to ensure that all of the players have visibility"""
        distribution = IncentiveDistribution.objects.all()[0]

        payer = distribution.company
        payee = distribution.customer
        provider = distribution.ippitem_set.all()[0].home_status.company
        home_stat = distribution.ippitem_set.all()[0].home_status

        self.assertNotEqual(payer, payee)
        self.assertNotEqual(payer, provider)
        self.assertNotEqual(payee, provider)

        stats = IncentivePaymentStatus.objects
        self.assertEqual(stats.filter_by_company(payer).count(), 1)
        self.assertEqual(stats.filter_by_company(payer).all()[0].home_status, home_stat)
        self.assertEqual(stats.filter_by_company(payee).count(), 1)
        self.assertEqual(stats.filter_by_company(payee).all()[0].home_status, home_stat)
        self.assertEqual(stats.filter_by_company(provider).count(), 1)
        self.assertEqual(stats.filter_by_company(provider).all()[0].home_status, home_stat)
