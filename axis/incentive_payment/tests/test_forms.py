__author__ = "Michael Jeffrey"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

import logging
import datetime
from unittest.util import safe_repr

from django.core.exceptions import ValidationError
from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase

from ..models import IncentiveDistribution, IncentivePaymentStatus
from ..forms import (
    IncentiveDistributionForm,
    IncentiveDistributionUpdateForm,
    IncentiveDistributionReportForm,
    IncentivePaymentStatusAnnotationForm,
)
from ..strings import *

log = logging.getLogger(__name__)


class FormTestingMixin:
    def assertSubstringInList(self, substring, container, msg=None):
        expression_found = False
        for item in container:
            if substring in item:
                expression_found = True

        if not expression_found:
            standard_msg = "{} not found in {}".format(safe_repr(substring), safe_repr(container))
            self.fail(self._formatMessage(msg, standard_msg))


class IncentiveDistributionUpdateFormTestCase(AxisTestCase, FormTestingMixin):
    form = IncentiveDistributionUpdateForm

    @classmethod
    def setUpTestData(cls):
        from axis.company.tests.factories import general_organization_factory
        from axis.incentive_payment.tests.factories import (
            basic_pending_builder_incentive_distribution_factory,
        )

        company = general_organization_factory()
        basic_pending_builder_incentive_distribution_factory(check_number="1234")
        cls.test_data = {
            "company": company.id,
            "customer": company.id,
            "check_requested_date": datetime.date.today(),
            "paid_date": datetime.date.today(),
            "check_number": 12341,
            "comment": "test comment",
            "rater_incentives": [],
        }

    def test_fail_paid_date_requires_check_number(self):
        self.test_data.pop("check_number")
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_NO_CHECK_NUMBER, form.errors["__all__"])

    def test_fail_check_number_requires_paid_date(self):
        self.test_data.pop("paid_date")
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_NO_PAID_DATE, form.errors["__all__"])

    def test_fail_paid_date_before_request_date(self):
        self.test_data["check_requested_date"] += datetime.timedelta(days=1)
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_PAID_DATE_BEFORE_CHECK_REQUEST_DATE, form.errors["__all__"])

    def test_fail_request_check_not_past_future_date(self):
        """Check request date cannot be more than 3 days in advance"""
        self.test_data["check_requested_date"] += datetime.timedelta(days=5)
        self.test_data["paid_date"] += datetime.timedelta(days=6)
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_DATE_IN_FUTURE, form.errors["__all__"])

    def test_fail_paid_date_not_past_future_date(self):
        """Paid date cannot be more than 3 days from submission"""
        self.test_data.pop("check_requested_date")
        self.test_data["paid_date"] += datetime.timedelta(days=5)
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_DATE_IN_FUTURE, form.errors["__all__"])

    def test_fail_check_number_cannot_exist(self):
        check_number = IncentiveDistribution.objects.all()[0].check_number
        self.test_data["check_number"] = check_number
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        # String is dynamic, only check beginning
        self.assertSubstringInList(ERROR_CHECK_NUMBER_ALREADY_EXISTS[:60], form.errors["__all__"])


class IncentiveDistributionFormTestCase(AxisTestCase, FormTestingMixin):
    form = IncentiveDistributionForm

    @classmethod
    def setUpTestData(cls):
        from axis.builder_agreement.tests.factories import builder_agreement_factory
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory
        from axis.company.tests.factories import builder_organization_factory

        ip = basic_incentive_payment_status_factory(home_status__eep_program__no_close_dates=True)

        builder_agreement_factory(
            subdivision=ip.home_status.home.subdivision,
            builder_org=ip.home_status.home.get_builder(),
            company=ip.home_status.home.get_builder(),
            eep_programs=[ip.home_status.eep_program],
            total_lots=0,
        )
        cls.company = Company.objects.filter(company_type="builder")[0]

        builder_organization_factory(name="unrelated_builder")

        cls.stats = IncentivePaymentStatus.objects.filter(
            home_status__home__relationships__company=cls.company
        )
        cls.test_data = {
            "company": cls.company.id,
            "customer": cls.company.id,
            "check_requested_date": datetime.date.today(),
            "paid_date": datetime.date.today(),
            "comment": "test comment",
            "check_number": 1412434,
            "rater_incentives": [],
            "stats": [x.id for x in cls.stats],
        }

    def test_fail_no_stats_supplied(self):
        self.test_data.pop("stats")
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_NO_HOMES_SUPPLIED, form.errors["__all__"])

    def test_fail_multiple_home_builders(self):
        builder = Company.objects.get(name="unrelated_builder")

        stat = IncentivePaymentStatus.objects.all()[0]

        self.test_data["customer"] = builder.id
        self.test_data["company"] = builder.id

        self.test_data["stats"] = [stat.id]
        form = self.form(data=self.test_data)

        choices = [
            (x, x) for x in IncentivePaymentStatus.objects.all().values_list("id", flat=True)
        ]
        form.fields["stats"].choices = choices

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        # String is dynamic, only check beginning
        self.assertSubstringInList(ERROR_MULTIPLE_BUILDERS[:30], form.errors["__all__"])


class IncentiveDistributionReportFormTestCase(AxisTestCase, FormTestingMixin):
    form = IncentiveDistributionReportForm

    @classmethod
    def setUpTestData(cls):
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.company.tests.factories import builder_organization_factory
        from axis.eep_program.tests.factories import basic_eep_program_factory

        from axis.geographic.tests.factories import real_city_factory

        city = real_city_factory("DeRidder", "LA")
        cls.subdivision = subdivision_factory(city=city)
        cls.company = cls.subdivision.builder_org
        cls.eep_program = basic_eep_program_factory(no_close_dates=True)
        builder_organization_factory(city=city)
        cls.test_data = {
            "builder_org": cls.company,
            "subdivision": cls.subdivision.id,
            "eep_program": cls.eep_program.id,
            "start_date": datetime.date.today(),
            "end_date": datetime.date.today(),
        }

    def test_fail_no_builder_or_subdivision(self):
        self.test_data.pop("builder_org")
        self.test_data.pop("subdivision")
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_NO_BUILDER_ORG_OR_SUBDIVISION, form.errors["__all__"])

    def test_fail_builder_not_assigned_to_subdivision(self):
        self.test_data["builder_org"] = (
            Company.objects.filter(company_type="builder")
            .exclude(id=self.subdivision.builder_org.id)[0]
            .id
        )
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        # string starts with dynamic content (ERROR_BUILDER_ORG_DOES_NOT_REPRESENT_SUBDIVISION)
        self.assertSubstringInList("does not represent", form.errors["__all__"])

    def test_fail_start_date_in_future(self):
        self.test_data["start_date"] += datetime.timedelta(days=1)
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_START_END_DATE_IN_FUTURE, form.errors["__all__"])

    def test_fail_end_date_in_future(self):
        self.test_data["end_date"] += datetime.timedelta(days=1)
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_START_END_DATE_IN_FUTURE, form.errors["__all__"])

    def test_fail_end_date_before_start_date(self):
        self.test_data["end_date"] += datetime.timedelta(days=-1)
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_END_DATE_BEFORE_START_DATE, form.errors["__all__"])


class IncentivePaymentStatusAnnotationFormTestCase(AxisTestCase, FormTestingMixin):
    form = IncentivePaymentStatusAnnotationForm

    @classmethod
    def setUpTestData(cls):
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        basic_incentive_payment_status_factory(home_status__eep_program__no_close_dates=True)
        stats = IncentivePaymentStatus.objects.all()
        cls.test_data = {
            "new_state": "start",
            "annotation": None,
            "stats": stats,
        }

    def test_fail_no_annotation_provided(self):
        self.test_data.pop("annotation")
        form = self.form(data=self.test_data)

        self.assertEqual(form.is_valid(), False)
        self.assertRaises(ValidationError, form.clean)
        self.assertIn(ERROR_NO_ANNOTATION, form.errors["__all__"])
