"""test_utils.py: Django eep_program utils tests"""


__author__ = "Johnny Fang"
__date__ = "30/7/19 11:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Johnny Fang",
]
import logging
import datetime
import json

from axis.annotation.models import Type
from axis.checklist.models import CheckList
from axis.company.models import Company
from axis.core.tests.testcases import AxisTestCase
from django.contrib.auth import get_user_model
from axis.eep_program.forms import EEPProgramForm
from axis.eep_program.models import EEPProgram

from .mixins import EEPProgramsTestMixin, EEPProgramManagerTestMixin

log = logging.getLogger(__name__)

User = get_user_model()


class EEPProgramFormsTests(EEPProgramsTestMixin, AxisTestCase):
    """Tests for EEPProgram forms"""

    form = EEPProgramForm

    @classmethod
    def setUpTestData(cls):
        super(EEPProgramFormsTests, cls).setUpTestData()
        EEPProgramManagerTestMixin().setUpTestData()

    @classmethod
    def setUpClass(cls):
        """Load all defaults for EEPProgramFormsTests"""
        from axis.annotation.tests.factories import type_factory
        from axis.relationship.models import Relationship

        super(EEPProgramFormsTests, cls).setUpClass()
        co = EEPProgram.objects.get(name="Single Checklist - Basic").owner
        cls.form_user = User.objects.filter(company=co).first()
        cls.form_company = Company.objects.get(company_type="eep", name__contains="Sponsor")
        cls.form_checklist = list(CheckList.objects.filter_by_company(cls.form_company))

        # Create annotations
        anno_one = type_factory()
        Relationship.objects.validate_or_create_relations_to_entity(anno_one, co)

    def test_no_required_fields_supplied(self):
        """Test for EEPProgramForm. None of the required fields were supplied with the form"""
        user = User.objects.order_by("id").first()
        form = self.form(data={}, user=user)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(len(form.errors), 15)

    def test_required_fields_supplied(self):
        """Test for EEPProgramForm. all 13 required fields supplied"""
        user = self.form_user
        company = self.form_company
        checklists = self.form_checklist
        a_type = list(Type.objects.filter_by_user(user))
        certifiable_by = list(Company.objects.filter_by_company(user.company, include_self=True))

        wd_settings_json = json.loads('{ "name":"John"}')
        data = {
            "per_point_adder": "0.00",
            "name": "EEP10",
            "min_hers_score": 0,
            "program_start_date": datetime.date.today(),
            "max_hers_score": 100,
            "workflow_default_settings": wd_settings_json,
            "builder_incentive_dollar_value": 20.0,
            "program_visibility_date": datetime.date.today(),
            "rater_incentive_dollar_value": 5.0,
            "sponsor": company.id,
            "required_checklists": checklists,
            "required_annotation_types": a_type,
            "certifiable_by": certifiable_by,
            "customer_hirl_certification_fee": 0,
            "customer_hirl_per_unit_fee": 0,
        }

        form = self.form(data=data, user=user)

        self.assertEqual(form.is_valid(), True)

    def test_validate_program_visibility_date(self):
        """Test for EEPProgramForm"""
        user = self.form_user
        company = self.form_company
        checklists = self.form_checklist
        a_type = list(Type.objects.filter_by_user(user))
        certifiable_by = list(Company.objects.filter_by_company(user.company, include_self=True))

        wd_settings_json = json.loads('{ "name":"John"}')
        data = {
            "per_point_adder": "0.00",
            "name": "EEP10",
            "min_hers_score": 0,
            "max_hers_score": 100,
            "workflow_default_settings": wd_settings_json,
            "builder_incentive_dollar_value": 20.0,
            "program_visibility_date": datetime.date.today(),
            "rater_incentive_dollar_value": 5.0,
            "sponsor": company.id,
            "required_checklists": checklists,
            "required_annotation_types": a_type,
            "certifiable_by": certifiable_by,
            "customer_hirl_certification_fee": 0,
            "customer_hirl_per_unit_fee": 0,
        }

        form = self.form(data=data, user=user)
        self.assertEqual(form.is_valid(), False)
        errors_dict = form.errors
        self.assertIn("program_start_date", errors_dict)
        self.assertEqual(
            form.errors["__all__"].data[0].message,
            "You must have a start date with a program visibility date",
        )

    def test_validate_program_visibility_date_after_start_date(self):
        """Test for EEPProgramForm. cannot have a program visibility date after it starts"""
        user = self.form_user
        company = self.form_company
        checklists = self.form_checklist
        a_type = list(Type.objects.filter_by_user(user))
        certifiable_by = list(Company.objects.filter_by_company(user.company, include_self=True))

        wd_settings_json = json.loads('{ "name":"John"}')
        data = {
            "per_point_adder": "0.00",
            "name": "EEP10",
            "min_hers_score": 0,
            "program_visibility_date": datetime.date(2019, 5, 5),
            "max_hers_score": 100,
            "workflow_default_settings": wd_settings_json,
            "builder_incentive_dollar_value": 20.0,
            "program_start_date": datetime.date(2019, 1, 1),
            "rater_incentive_dollar_value": 5.0,
            "sponsor": company.id,
            "required_checklists": checklists,
            "required_annotation_types": a_type,
            "certifiable_by": certifiable_by,
        }
        form = self.form(data=data, user=user)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors["__all__"].data[0].message,
            "You cannot have a program visibility date after it starts.",
        )

    def test_validate_program_close_date_before_start_date(self):
        """Test for EEPProgramForm. cannot have a program visibility date after it starts"""
        user = self.form_user
        company = self.form_company
        checklists = self.form_checklist
        a_type = list(Type.objects.filter_by_user(user))
        certifiable_by = list(Company.objects.filter_by_company(user.company, include_self=True))

        wd_settings_json = json.loads('{ "name":"John"}')
        data = {
            "per_point_adder": "0.00",
            "name": "EEP10",
            "min_hers_score": 0,
            "program_visibility_date": datetime.date(2019, 2, 5),
            "max_hers_score": 100,
            "workflow_default_settings": wd_settings_json,
            "builder_incentive_dollar_value": 20.0,
            "program_start_date": datetime.date(2019, 5, 1),
            "program_close_date": datetime.date(2019, 1, 1),
            "rater_incentive_dollar_value": 5.0,
            "sponsor": company.id,
            "required_checklists": checklists,
            "required_annotation_types": a_type,
            "certifiable_by": certifiable_by,
        }
        form = self.form(data=data, user=user)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors["__all__"].data[0].message,
            "You cannot have a program closed date before it starts.",
        )

    def test_validate_program_end_date_before__close_date(self):
        """Test for EEPProgramForm. cannot have a program visibility date after it starts"""
        user = self.form_user
        company = self.form_company
        checklists = self.form_checklist
        a_type = list(Type.objects.filter_by_user(user))
        certifiable_by = list(Company.objects.filter_by_company(user.company, include_self=True))

        wd_settings_json = json.loads('{ "name":"John"}')
        data = {
            "per_point_adder": "0.00",
            "name": "EEP10",
            "min_hers_score": 0,
            "program_visibility_date": datetime.date(2019, 1, 1),
            "max_hers_score": 100,
            "workflow_default_settings": wd_settings_json,
            "builder_incentive_dollar_value": 20.0,
            "program_start_date": datetime.date(2019, 2, 1),
            "program_close_date": datetime.date(2019, 5, 1),
            "program_end_date": datetime.date(2019, 4, 1),
            "rater_incentive_dollar_value": 5.0,
            "sponsor": company.id,
            "required_checklists": checklists,
            "required_annotation_types": a_type,
            "certifiable_by": certifiable_by,
        }
        form = self.form(data=data, user=user)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors["__all__"].data[0].message,
            "You cannot have a program end before it closes.",
        )

    def test_validate_program_end_date_before_start_date(self):
        """Test for EEPProgramForm. cannot have a program visibility date after it starts"""
        user = self.form_user
        company = self.form_company
        checklists = self.form_checklist
        a_type = list(Type.objects.filter_by_user(user))
        certifiable_by = list(Company.objects.filter_by_company(user.company, include_self=True))

        wd_settings_json = json.loads('{ "name":"John"}')
        data = {
            "per_point_adder": "0.00",
            "name": "EEP10",
            "min_hers_score": 0,
            "program_visibility_date": datetime.date(2019, 1, 1),
            "max_hers_score": 100,
            "workflow_default_settings": wd_settings_json,
            "builder_incentive_dollar_value": 20.0,
            "program_start_date": datetime.date(2019, 2, 1),
            "program_end_date": datetime.date(2019, 1, 1),
            "rater_incentive_dollar_value": 5.0,
            "sponsor": company.id,
            "required_checklists": checklists,
            "required_annotation_types": a_type,
            "certifiable_by": certifiable_by,
        }
        form = self.form(data=data, user=user)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors["__all__"].data[0].message,
            "You cannot have a program end date before it starts.",
        )
