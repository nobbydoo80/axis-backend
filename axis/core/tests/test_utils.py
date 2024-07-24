__author__ = "Michael Jeffrey"
__date__ = "4/25/16 1:46 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import QueryDict
from django.apps import apps
from django.test.testcases import TransactionTestCase
from django.utils import timezone

from axis.annotation.models import Annotation
from axis.annotation.tests.factories import annotation_factory
from axis.company.models import Company
from axis.company.tests.factories import builder_organization_factory
from axis.core.merge_objects import MergeObjects
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import (
    builder_admin_factory,
    rater_admin_factory,
    general_super_user_factory,
)
from axis.core.tests.test_views import DevNull
from axis.core.tests.testcases import AxisTestCase
from axis.core.utils import (
    email_html_content_to_text,
    get_previous_day_start_end_times,
    has_beta_access,
    query_params_to_dict,
    get_frontend_url,
)
from axis.relationship.models import Relationship


User = get_user_model()
frontend_app = apps.get_app_config("frontend")


class MergeUtilTest(TransactionTestCase):
    def test_full(self):
        from axis.geographic.tests.factories import county_factory
        from axis.eep_program.models import EEPProgram
        from axis.eep_program.tests.factories import basic_eep_program_factory

        b = builder_admin_factory(company__name="Test")
        builder_admin_factory(company__name="Test 2", company__city=b.company.city)

        # Ensure separate users and companies are made.
        self.assertEqual(Company.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

        # Get the companies separately
        company_one, company_two = Company.objects.all()

        # Sanity check: each company has one user
        self.assertEqual(company_one.users.count(), 1)
        self.assertEqual(company_two.users.count(), 1)

        county1 = county_factory()
        county2 = county_factory()
        county3 = county_factory()

        company_one.counties.add(county1)
        company_two.counties.add(county1, county2, county3)

        self.assertEqual(company_one.counties.count(), 1 + 1)
        self.assertEqual(company_two.counties.count(), 1 + 3)

        p = basic_eep_program_factory(owner__name="Test")
        basic_eep_program_factory(owner=p.owner)

        program_one, program_two = EEPProgram.objects.all()

        # Add who can certify each program
        program_one.certifiable_by.add(company_one, company_two)
        program_two.certifiable_by.add(company_two)

        # Sanity Check
        self.assertEqual(program_one.certifiable_by.count(), 2)
        self.assertEqual(program_two.certifiable_by.count(), 1)

        Relationship.objects.validate_or_create_relations_to_entity(program_one, company_one)
        Relationship.objects.validate_or_create_relations_to_entity(program_two, company_two)
        self.assertEqual(Relationship.objects.count(), 2)

        rater = rater_admin_factory(company__city=b.company.city)
        Relationship.objects.create_mutual_relationships(company_two, company_one, rater.company)

        self.assertEqual(Relationship.objects.count(), 6)  # 4 sould have been created.

        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)
        self.assertEqual(len(merge.collect_nested_objects(company_two)), 1)

    def test_foreign_keys_are_replaced(self):
        """
        Two users belong to the same company.
        One pointing at the true company.
        Two pointing at a duplicate company.
        Two should point at the first company.
        Duplicate should be left with no users
        """
        builder_admin_factory(company__name="Test")
        builder_admin_factory(company__name="Test", company__city__name="Jefferson")

        # Ensure separate users and companies are made.
        self.assertEqual(Company.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

        # Get the companies separately
        company_one, company_two = Company.objects.all()

        # Sanity check: each company has one user
        self.assertEqual(company_one.users.count(), 1)
        self.assertEqual(company_two.users.count(), 1)

        # MERGE
        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)

        # refresh the companies
        company_one = Company.objects.get(id=company_one.id)
        company_two = Company.objects.get(id=company_two.id)

        # Count the users again
        self.assertEqual(company_one.users.count(), 2)
        self.assertEqual(company_two.users.count(), 0)

    def test_local_many_to_many_keys_are_replaced(self):
        """
        One company belongs to two counties.
        Two company instances.
        Each pointing to one county.
        Counties should all collapse to first company.
        Two should be left with none.
        """
        from axis.geographic.tests.factories import county_factory, County

        county0 = county_factory()
        self.assertEqual(County.objects.count(), 1)

        builder_organization_factory(
            name="Test",
            city__name="Jefferson",
            city__county=county0,
            counties=[county0],
        )
        builder_organization_factory(name="Test", city__county=county0, counties=[county0])

        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(Company.objects.count(), 2)

        county1 = county_factory()
        county2 = county_factory()
        county3 = county_factory()
        self.assertEqual(County.objects.count(), 4)

        company_one, company_two = Company.objects.all().order_by("id")

        # These should be identical at this point
        one_starting_out_counties = company_one.counties.count()
        two_starting_out_counties = company_two.counties.count()
        self.assertEqual(
            set(company_one.counties.values_list("pk", flat=True)),
            set(company_two.counties.values_list("pk", flat=True)),
        )

        # Add our expected counties
        company_one.counties.add(county1)
        company_two.counties.add(county2, county3)

        # Sanity check
        self.assertEqual(company_one.counties.count(), one_starting_out_counties + 1)
        self.assertEqual(company_two.counties.count(), two_starting_out_counties + 2)

        # MERGE
        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)

        # refresh the companies
        company_one = Company.objects.get(id=company_one.id)
        company_two = Company.objects.get(id=company_two.id)

        # Final check, company one should have all the counties
        self.assertEqual(company_one.counties.count(), 3 + one_starting_out_counties)
        self.assertEqual(company_two.counties.count(), 0)

    def test_reverse_many_to_many_keys_are_replaced(self):
        """
        One company can certify two EEPPrograms.
        Two company instances.
        Each pointing to one EEPProgram.
        Programs should collapse to the first company.
        Two should be left with None
        """
        from axis.eep_program.models import EEPProgram
        from axis.eep_program.tests.factories import basic_eep_program_factory

        builder_one = builder_organization_factory(name="one")
        builder_two = builder_organization_factory(name="two")
        builder_three = builder_organization_factory(name="three")

        basic_eep_program_factory(owner__name="Test")
        basic_eep_program_factory(owner__name="Test")

        program_one, program_two = EEPProgram.objects.all()

        # Add who can certify each program
        program_one.certifiable_by.add(builder_one, builder_two)
        program_two.certifiable_by.add(builder_three)

        # Sanity Check
        self.assertEqual(program_one.certifiable_by.count(), 2)
        self.assertEqual(program_two.certifiable_by.count(), 1)

        # MERGE
        merge = MergeObjects(program_one, program_two)
        merge.merge(prompt=False, delete_alternates=False)

        # Refresh the programs
        program_one = EEPProgram.objects.get(id=program_one.id)
        program_two = EEPProgram.objects.get(id=program_two.id)

        # Final check, program one should have all the companies
        self.assertEqual(program_one.certifiable_by.count(), 3)
        self.assertEqual(program_two.certifiable_by.count(), 0)

    def test_blank_fields_get_filled_in(self):
        from axis.company.models import Company
        from axis.company.tests.factories import builder_organization_factory

        company_one = builder_organization_factory()
        company_two = builder_organization_factory(street_line2="Two")

        self.assertEqual(company_one.street_line2, "")

        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)

        # Refresh companies
        company_one = Company.objects.get(id=company_one.id)
        company_two = Company.objects.get(id=company_two.id)

        # Final check, only checking company_one
        self.assertEqual(company_one.street_line2, "Two")

    def test_non_blank_fields_do_not_get_overwritten(self):
        # Create the companies
        company_one = builder_organization_factory(street_line2="One")
        company_two = builder_organization_factory(street_line2="Two")
        self.assertNotEqual(company_one.id, company_two.id)

        # Sanity Check
        self.assertEqual(company_one.street_line2, "One")

        # MERGE
        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)

        # Refresh companies
        company_one = Company.objects.get(id=company_one.id)
        company_two = Company.objects.get(id=company_two.id)

        # Make sure non-blank field has not been overwritten
        self.assertEqual(company_one.street_line2, "One")

    def test_generic_foreign_keys_for_model_type_are_moved(self):
        """
        One BuilderOrganization has 2 annotations.
        Two BuilderOrganization instances.
        Annotations split between instances.
        Annotations should collapse to the first BuilderOrganization.
        Two should be left with None.
        """
        # Create the companies
        company_one = builder_organization_factory(name="Test")
        company_two = builder_organization_factory(name="Test", city__name="Jefferson")
        self.assertNotEqual(company_one.id, company_two.id)

        # Fetch as specific model type
        company_one = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=company_one.id
        )
        company_two = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=company_two.id
        )

        # Get content type for model type
        company_content_type = ContentType.objects.get_for_model(Company)

        # Create annotations
        anno_one = annotation_factory(
            content_type=company_content_type,
            object_id=company_one.id,
            content="Annotation One",
        )
        anno_two = annotation_factory(
            content_type=company_content_type,
            object_id=company_two.id,
            type=anno_one.type,
            content="Annotation Two",
        )

        # Make sure each company has 1 annotation
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_one.id
            ).count(),
            1,
        )
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_two.id
            ).count(),
            1,
        )

        # MERGE
        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)

        # Don't need to refresh the companies, because we can't get at them from that direction.
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_one.id
            ).count(),
            2,
        )
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_two.id
            ).count(),
            0,
        )

    def test_generic_foreign_keys_for_model_parent_type_are_moded(self):
        """
        One BuilderOrganization has 2 annotations.
        Two BuilderOrganization instances.
        Annotations split between instance, but assigned to Company content_type.
        Annotations should collapse to the first BuilderOrganization, but keep content_type.
        Two should be left with None.
        """
        # Create the companies
        company_one = builder_organization_factory(name="Test")
        company_two = builder_organization_factory(name="Test", city__name="Jefferson")
        self.assertNotEqual(company_one.id, company_two.id)

        # Fetch as specific model type
        company_one = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=company_one.id
        )
        company_two = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=company_two.id
        )

        # Get content type for parent
        company_content_type = ContentType.objects.get_for_model(Company)

        # Create annotations
        anno_one = annotation_factory(
            content_type=company_content_type,
            object_id=company_one.id,
            content="Annotation One",
        )
        anno_two = annotation_factory(
            content_type=company_content_type,
            object_id=company_two.id,
            type=anno_one.type,
            content="Annotation Two",
        )

        # Make sure each company has 1 annotation
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_one.id
            ).count(),
            1,
        )
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_two.id
            ).count(),
            1,
        )

        # MERGE
        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)

        # Don't need to refresh the companies, because we can't get at them from that direction.
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_one.id
            ).count(),
            2,
        )
        self.assertEqual(
            Annotation.objects.filter(
                content_type=company_content_type, object_id=company_two.id
            ).count(),
            0,
        )

    def test_builder_fk_test(self):
        company_one = builder_organization_factory(name="Test")
        company_two = builder_organization_factory(name="Test", city__name="Jefferson")
        self.assertNotEqual(company_one.id, company_two.id)

        # Fetch as specific model type
        company_one = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=company_one.id
        )
        company_two = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=company_two.id
        )

        from axis.subdivision.tests.factories import subdivision_factory

        subdivision_factory(builder_org=company_two)

        merge = MergeObjects(company_one, company_two)
        merge.merge(prompt=False, delete_alternates=False)

        self.assertEqual(len(merge.collect_nested_objects(company_two)), 1)


class UtilTest(AxisTestCase):
    client_class = AxisClient

    def test_email_html_content_to_text(self):
        html_content = """<html><style>.cls{font-size:14px;}</style><p>hello world</p></html>"""
        text = email_html_content_to_text(html_content)
        self.assertEqual(text, "hello world")

    def test_get_previous_day_start_end_times(self):
        start_date, end_date = get_previous_day_start_end_times()
        today_midnight = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_midnight - timezone.timedelta(days=1)
        self.assertEqual(start_date, yesterday_start)
        self.assertEqual(end_date, today_midnight)

    def test_has_beta_access(self):
        superuser = general_super_user_factory()
        superuser.show_beta = True
        superuser.save()
        self.assertTrue(
            self.client.login(username=superuser.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (superuser.username, superuser.pk),
        )

        with self.subTest("Superuser with enabled beta"):
            response = self.client.get("/")
            request = response.wsgi_request
            self.assertTrue(has_beta_access(request))

        superuser.show_beta = False
        superuser.save()

        with self.subTest("Superuser with disabled beta"):
            response = self.client.get("/")
            request = response.wsgi_request
            self.assertFalse(has_beta_access(request))

        rater_user = rater_admin_factory()
        rater_user.show_beta = True
        rater_user.save()

        self.assertTrue(
            self.client.login(username=rater_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (rater_user.username, rater_user.pk),
        )

        with self.subTest("Common user with enabled beta"):
            response = self.client.get("/")
            request = response.wsgi_request
            self.assertFalse(has_beta_access(request))

    def test_get_frontend_url(self):
        frontend_url = get_frontend_url("company", "detail", 123)

        self.assertEqual(frontend_url, f"/{frontend_app.DEPLOY_URL}company/detail/123")

    def test_query_params_to_dict(self):
        query_params = QueryDict(query_string="a=1&a=2&b=3")
        # check standard behaviour
        self.assertEqual(query_params.dict(), {"a": "2", "b": "3"})

        # check query_params_to_dict behaviour
        self.assertEqual(query_params_to_dict(query_params), {"a": ["1", "2"], "b": "3"})

    def test_dump_test_case(self):
        # Dump out simple things
        data = True
        self.dump_test_data(data, output=DevNull().write)

        # Dump out comples things
        data = [
            {
                "dict": {
                    "bool": True,
                    "bool_f": False,
                    "str_id": 2,
                    "str_date": "10/2/30 98:202",
                    "str": "string",
                    "none": None,
                    "float_lt1": 0.0111112,
                    "float_gt1": 1.3333,
                    "date": datetime.date.today(),
                    "datetime": datetime.datetime.now().replace(tzinfo=datetime.timezone.utc),
                },
                "list": ["1", "2", "3"],
                "bool": True,
                "bool_f": False,
                "str_id": 2,
                "str_date": "10/2/30 98:202",
                "str": "string",
                "none": None,
                "float_lt1": 0.0111112,
                "float_gt1": 1.3333,
                "date": datetime.date.today(),
                "datetime": datetime.datetime.now().replace(tzinfo=datetime.timezone.utc),
            }
        ]
        self.dump_test_data(data, output=DevNull().write)

        # get json representation of it
        self.dump_test_data(data, dump_json=True, output=DevNull().write)

        # Dump out the attributes to a Models
        user = general_super_user_factory()
        self.dump_test_data(user, object_name="user", output=DevNull().write)
