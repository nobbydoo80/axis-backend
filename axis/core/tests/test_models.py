"""test_models.py: Django core"""

__author__ = "Steven Klass"
__date__ = "4/23/13 8:50 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from timezonefinder import TimezoneFinder

from axis.company.models import SponsorPreferences, Company, CompanyRole
from axis.company.tests.factories import provider_organization_factory, rater_organization_factory
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.testcases import AxisTestCase
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import city_factory
from .factories import (
    general_admin_factory,
    general_user_factory,
    provider_user_factory,
    rater_admin_factory,
    non_company_user_factory,
)

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
User = get_user_model()


class ProfileModelTests(AxisTestCase):
    include_company_types = ["general", "rater"]
    include_unrelated = False
    include_noperms = False

    def test_clear_permissions_post_save(self):
        """Test out the post save handler to make sure that perms are established"""
        user = self.user_model.objects.create(username="Bob")
        self.assertEqual(user.groups.all().count(), 0)

        group = Group.objects.create(name="Foo")
        user.groups.add(group)
        self.assertEqual(user.groups.all().count(), 1)

        user.save()
        self.assertEqual(user.groups.all().count(), 0)

    def test_user_company_admin(self):
        """Test when a user becomes an admin they gain / loose the right privileges"""
        user = general_user_factory()
        self.assertEqual(user.is_company_admin, False)
        self.assertEqual(user.groups.all().count(), 1)
        user.is_company_admin = True
        user.save()
        self.assertEqual(user.groups.all().count(), 2)
        user.is_company_admin = False
        user.save()
        self.assertEqual(user.groups.all().count(), 1)

    def test_user_group_changeout(self):
        """Test when a users groups get messed up they get realigned"""
        user = general_admin_factory()
        self.assertEqual(user.is_company_admin, True)
        self.assertEqual(user.groups.all().count(), 2)

        user.groups.clear()
        group = Group.objects.create(name="Foo")
        user.groups.add(group)
        self.assertEqual(user.groups.all().count(), 1)

        user.save()
        self.assertEqual(user.groups.all().count(), 2)
        self.assertNotIn(group, user.groups.all())


class UserModelTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["provider", "rater"]
    include_unrelated = False
    include_noperms = False

    def test_history(self):
        user = self.user_model.objects.create(username="Bob")
        self.assertEqual(user.history.all().count(), 1)
        user.save()
        self.assertEqual(user.history.all().count(), 2)

    def test_mult_history(self):
        bob = self.user_model.objects.create(username="Bob")
        self.assertEqual(bob.history.all().count(), 1)

        user = self.user_model.objects.create(username="Bob2")
        user.save()
        user.save()
        self.assertEqual(user.history.all().count(), 3)
        self.assertNotIn(bob.history.get(), list(user.history.all()))

    def test_is_company_type_member(self):
        rater_user = self.get_random_user(company_type=Company.RATER_COMPANY_TYPE)

        # check single value
        self.assertTrue(rater_user.is_company_type_member(Company.RATER_COMPANY_TYPE))

        # check list
        self.assertTrue(
            rater_user.is_company_type_member(
                [Company.RATER_COMPANY_TYPE, Company.PROVIDER_COMPANY_TYPE]
            )
        )

        # check non existing type
        with self.assertRaises(ValueError):
            rater_user.is_company_type_member([Company.RATER_COMPANY_TYPE, "non_existing_type"])

    def test_is_sponsored_by_company(self):
        non_sponsor_company = provider_organization_factory(name="Non Sponsor", slug="non_sponsor")

        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        rater_user = rater_admin_factory(first_name="Rater User", company__name="Rater Company")
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=rater_user.company
        )
        rater_user.company.update_permissions()

        self.assertTrue(rater_user.is_sponsored_by_company(hirl_user.company))
        self.assertTrue(rater_user.is_sponsored_by_company(hirl_user.company.slug))
        self.assertFalse(rater_user.is_sponsored_by_company(non_sponsor_company))

        # check list
        self.assertTrue(
            rater_user.is_sponsored_by_companies([hirl_user.company, non_sponsor_company])
        )

        new_sponsor_company = provider_organization_factory(name="New Sponsor", slug="new_sponsor")

        SponsorPreferences.objects.create(
            sponsor=new_sponsor_company, sponsored_company=rater_user.company
        )
        rater_user.company.update_permissions()
        self.assertTrue(rater_user.is_sponsored_by_company(new_sponsor_company))

        self.assertFalse(rater_user.is_sponsored_by_company(new_sponsor_company, only_sponsor=True))

    def test_is_customer_hirl_company_member(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Common user", company=hirl_company, is_company_admin=False
        )
        self.assertTrue(hirl_user.is_customer_hirl_company_member())

    def test_is_customer_hirl_company_admin_member(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        self.assertTrue(hirl_user.is_customer_hirl_company_admin_member())

    def test_set_correct_user_timezone_based_on_company_or_mailing_address(self):
        # set real Akutan lat lng for company city
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs",
            slug=customer_hirl_app.CUSTOMER_SLUG,
            city__latitude=54.134823,
            city__longitude=-165.773575,
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        tf = TimezoneFinder()

        tz_name = tf.timezone_at(
            lat=hirl_user.company.city.latitude, lng=hirl_user.company.city.longitude
        )
        self.assertEqual(hirl_user.timezone_preference.key, tz_name)

        # set real Washington lat lng as mailing city
        geocode = Geocode.objects.create(
            raw_address=f"479 Washington St, Providence, RI, 34342",
            raw_city=city_factory(latitude=47.751076, longitude=-120.740135),
        )

        hirl_user.mailing_geocode = geocode
        hirl_user.save()
        hirl_user.refresh_from_db()

        tz_name = tf.timezone_at(lat=geocode.raw_city.latitude, lng=geocode.raw_city.longitude)
        self.assertEqual(hirl_user.timezone_preference.key, tz_name)

        # unknown timezone

        provider_company = provider_organization_factory(
            city__latitude=999999, city__longitude=99999999
        )
        provider_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=provider_company, is_company_admin=True
        )
        self.assertEqual(provider_user.timezone_preference.key, "US/Pacific")

    def test_create_customer_hirl_rater_legacy_user(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        verifier_company = rater_organization_factory()
        verifier_company.sponsor_preferences.create(sponsor=hirl_company)

        rater_user = rater_admin_factory(company=verifier_company)
        self.assertIsNotNone(rater_user.hirlrateruser)

        with self.subTest("Test change user company"):
            rater_user = non_company_user_factory(company=None)
            self.assertIsNone(getattr(rater_user, "hirlrateruser", None))

            rater_user.company = verifier_company
            rater_user.save()
            self.assertIsNotNone(rater_user.hirlrateruser)

        with self.subTest("Test change user company"):
            rater_user = rater_admin_factory(company=verifier_company)
            self.assertIsNotNone(rater_user.hirlrateruser)

            old_legacy_user_id = rater_user.hirlrateruser.hirl_id

            verifier_company2 = rater_organization_factory()
            verifier_company2.sponsor_preferences.create(sponsor=hirl_company)

            rater_user.company = verifier_company2
            rater_user.save()

            self.assertEqual(rater_user.company, verifier_company2)
            self.assertEqual(old_legacy_user_id, rater_user.hirlrateruser.hirl_id)

    def test_only_active_users_filter_qs(self):
        not_active_user = rater_admin_factory(is_active=False)
        not_approved_user = rater_admin_factory(is_approved=False)
        active_user = rater_admin_factory(is_approved=True, is_active=True)

        self.assertIn(active_user, User.objects.all().only_active())
        self.assertNotIn(not_active_user, User.objects.all().only_active())
        self.assertNotIn(not_approved_user, User.objects.all().only_active())

    def test_default_company(self):
        rater_user = rater_admin_factory(company__name="Company 1")

        company2 = rater_organization_factory(name="Company 2")

        self.assertEqual(rater_user.default_company, rater_user.company)

        rater_user.company = company2
        rater_user.companies.add(company2)

        self.assertEqual(rater_user.default_company.name, "Company 1")

    def test_is_company_admin_attribute_changed(self):
        rater_user = rater_admin_factory(company__name="Company 1", is_company_admin=True)
        self.assertEqual(rater_user.companyaccess_set.count(), 1)

        company_access = rater_user.companyaccess_set.first()

        self.assertEqual(company_access.roles.filter(slug=CompanyRole.IS_COMPANY_ADMIN).count(), 1)

        rater_user.is_company_admin = False
        rater_user.save()

        rater_user.refresh_from_db()

        self.assertEqual(rater_user.companyaccess_set.count(), 1)
        self.assertEqual(company_access.roles.filter(slug=CompanyRole.IS_COMPANY_ADMIN).count(), 0)
