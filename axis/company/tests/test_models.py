"""test_models.py: Django company"""

__author__ = "Steven Klass"
__date__ = "4/23/13 8:17 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging
import re
from collections import defaultdict
from unittest import mock

from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from axis.company.models import COMPANY_MODELS, SponsorPreferences, CompanyRole
from axis.company.tests.factories import (
    general_organization_factory,
    rater_organization_factory,
    builder_organization_factory,
    provider_organization_factory,
)
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import general_admin_factory, rater_admin_factory
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import HIRLBuilderOrganization, HIRLCompanyClient
from axis.relationship.models import Relationship

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class CompanyModelTests(AxisTestCase):
    client_class = AxisClient

    def _get_perm_dict(self, user):
        perms = defaultdict(set)

        # Irregular permission schemes are excluded to prevent the tests from
        # assuming they will find regular ones.
        exclude_apps = ["messaging", "qa"]
        exclude_models = [
            "customer_eto.permitandoccupancysettings",
        ]

        for perm in list(user.get_all_permissions()):
            app_name, code = perm.split(".")
            perm_type, model_name = code.split("_", 1)
            app_label = ".".join((app_name, model_name))
            if app_name not in exclude_apps and app_label not in exclude_models:
                perms[perm_type].add(app_name)
        return perms

    def test_company_permissions_post_save(self):
        """Test out the post save handler to make sure that perms are established"""

        user = general_admin_factory(company__is_customer=False, company__is_active=False)
        company = user.company
        self.assertEqual(company.is_customer, False)
        self.assertEqual(company.is_active, False)

        perms = self._get_perm_dict(user)
        self.assertEqual(list(perms.keys()), [])

        company.is_active = True
        company.is_customer = True
        company.save()

        user.is_company_admin = True
        user.save()

        self.assertEqual(company.is_customer, True)
        self.assertGreater(company.group.permissions.all().count(), 0)
        self.assertGreater(company.get_admin_group().permissions.all().count(), 0)

        perms = self._get_perm_dict(company.users.get(is_company_admin=True))
        self.assertEqual(set(perms.keys()), {"add", "change", "view", "delete"})

    def test_company_permissions_loosing_post_save(self):
        """Test out the post save handler to make sure that perms are established"""

        user = general_admin_factory()
        company = user.company
        self.assertEqual(company.is_customer, True)
        self.assertGreater(company.group.permissions.all().count(), 0)
        self.assertEqual(company.users.filter(is_company_admin=True).all().count(), 1)
        self.assertGreater(company.get_admin_group().permissions.all().count(), 0)
        perms = self._get_perm_dict(user)
        self.assertEqual(set(perms.keys()), set(["add", "change", "view", "delete"]))

        company.is_customer = False
        company.save()

        perms = self._get_perm_dict(company.users.get())
        self.assertEqual(set(perms.keys()), set(["view", "add"]))
        self.assertEqual(company.users.filter(is_company_admin=True).all().count(), 0)

    def test_sponsored_permissions_for_company_types_based_on_sponsor(self):
        """Test to ensure that a sponsored company only sees company types for which the sponsor
        wants to see"""

        sponsor = general_admin_factory()
        sponsoring_company = sponsor.company

        # Remove a bunch of groups..
        ctypes = ContentType.objects.get_for_models(*COMPANY_MODELS).values()
        vperms = sponsoring_company.group.permissions.filter(
            content_type__in=ctypes, codename__istartswith="view"
        )

        viewable = ["rater", "builder"]
        for group in [sponsoring_company.group, sponsoring_company.get_admin_group()]:
            for perm in group.permissions.filter(content_type__in=ctypes):
                short_name = re.sub(r"organization", "", perm.codename.split("_")[1])
                if short_name not in viewable + [sponsoring_company.company_type]:
                    group.permissions.remove(perm)
        vperms = sponsoring_company.group.permissions.filter(
            content_type__in=ctypes, codename__istartswith="view"
        )
        self.assertEqual(vperms.all().count(), 2)

        rater = rater_admin_factory()
        rater_company = rater.company

        vperms = rater_company.group.permissions.filter(
            content_type__in=ctypes, codename__istartswith="view"
        )
        self.assertGreater(vperms.all().count(), 5)
        rater_company.add_sponsor(sponsoring_company)
        for group in [rater_company.group, sponsoring_company.get_admin_group()]:
            group.permissions.clear()
        # Force a permissions update
        rater_company.save()

        vperms = rater_company.group.permissions.filter(
            content_type__in=ctypes, codename__istartswith="view"
        )
        self.assertGreaterEqual(vperms.all().count(), 2)

    @mock.patch("requests.get")
    def test_is_water_sense_partner(self, request_mock):
        with self.subTest("Non builder company is never water sense partner"):
            rater_company = rater_organization_factory()
            self.assertEqual(rater_company.is_water_sense_partner(), False)

        builder = builder_organization_factory()
        with self.subTest("Builder is not water sense partner"):
            request_mock().status_code = 200
            request_mock().json.return_value = {"count": 0}

            self.assertEqual(builder.is_water_sense_partner(), False)

        with self.subTest("Builder is water sense partner"):
            request_mock().status_code = 200
            request_mock().json.return_value = {"count": 1}

            self.assertEqual(builder.is_water_sense_partner(), True)

        with self.subTest("Water sense api error"):
            request_mock().status_code = 200
            request_mock().json.return_value = {}

            self.assertEqual(builder.is_water_sense_partner(), False)

            request_mock().status_code = 500
            request_mock().json.return_value = {"count": 2}

            self.assertEqual(builder.is_water_sense_partner(), False)


class SponsorPreferencesModelTests(AxisTestCase):
    """
    Tests methods and settings on the ``SponsorPreferences`` model and ``SponsorPreferencesManager``
    """

    def test_unsponsored_customer_is_unrestricted(self):
        """Verifies that unsponsored companies are unaffected by sponsoring permission hooks."""
        company = general_organization_factory()

        policy = company.sponsor_preferences.get_edit_profile_policy()
        self.assertEqual(policy.has_permission, True)
        self.assertEqual(policy.warning, False)

        policy = company.sponsor_preferences.get_edit_identity_fields_policy()
        self.assertEqual(policy.has_permission, True)
        self.assertEqual(policy.warning, False)

    def test_sponsored_company_is_limited_by_unanimous_policy(self):
        """Verifies that policy fetching works."""
        company = general_organization_factory()
        sponsor1 = general_organization_factory()
        sponsor2 = general_organization_factory()
        company.add_sponsor(sponsor1)
        company.add_sponsor(sponsor2)

        policy = company.sponsor_preferences.get_edit_profile_policy()
        self.assertEqual(policy.has_permission, True)
        self.assertEqual(policy.warning, False)

        policy = company.sponsor_preferences.get_edit_identity_fields_policy()
        self.assertEqual(policy.has_permission, True)
        self.assertEqual(policy.warning, False)

        # Change policies across the board and verify again
        company.sponsor_preferences.update(can_edit_profile=False)

        policy = company.sponsor_preferences.get_edit_profile_policy()
        self.assertEqual(policy.has_permission, False)
        self.assertEqual(policy.warning, False)

        # Change policies across the board and verify again
        company.sponsor_preferences.update(can_edit_profile=True, can_edit_identity_fields=False)

        policy = company.sponsor_preferences.get_edit_identity_fields_policy()
        self.assertEqual(policy.has_permission, False)
        self.assertEqual(policy.warning, False)

    def test_sponsored_company_identity_fields_policy_limited_by_edit_policy(self):
        """
        Verifies that the ``can_edit_profile=False`` policy trumps whatever is set in the policies
        concerning ``can_edit_identity_fields``.
        """
        company = general_organization_factory()
        sponsor = general_organization_factory()
        company.add_sponsor(sponsor)

        company.sponsor_preferences.update(can_edit_profile=False, can_edit_identity_fields=True)

        policy = company.sponsor_preferences.get_edit_profile_policy()
        self.assertEqual(policy.has_permission, False)
        self.assertEqual(policy.warning, False)

        # These should still be false
        policy = company.sponsor_preferences.get_edit_identity_fields_policy()
        self.assertEqual(policy.has_permission, False)
        self.assertEqual(policy.warning, False)

    def test_sponsored_company_is_limited_by_mixed_policy(self):
        """Verifies that mixed policies result in the more restricted being chosen."""
        company = general_organization_factory()
        sponsor1 = general_organization_factory()
        sponsor2 = general_organization_factory()
        company.add_sponsor(sponsor1)
        company.add_sponsor(sponsor2)

        preferences1 = sponsor1.sponsored_preferences.get(sponsored_company=company)

        # Create can_edit_profile discrepancy
        preferences1.can_edit_profile = False
        preferences1.save()

        policy = company.sponsor_preferences.get_edit_profile_policy()
        self.assertEqual(policy.has_permission, False)
        self.assertEqual(policy.warning, True)

        # Create can_edit_identity_fields discrepancy
        preferences1.can_edit_profile = True
        preferences1.can_edit_identity_fields = False
        preferences1.save()

        policy = company.sponsor_preferences.get_edit_identity_fields_policy()
        self.assertEqual(policy.has_permission, False)
        self.assertEqual(policy.warning, True)

    def test_get_companies_to_be_notified(self):
        """Verifies that SponsorPreferences manager method works."""
        company = general_organization_factory()
        sponsor1 = general_organization_factory()
        sponsor2 = general_organization_factory()
        company.add_sponsor(sponsor1)
        company.add_sponsor(sponsor2)

        subscribed_sponsors = company.sponsor_preferences.get_companies_to_be_notified()
        self.assertEqual(len(subscribed_sponsors), 2)
        self.assertEqual({sponsor1, sponsor2}, set(list(subscribed_sponsors)))

        # Remove all subscriptions
        company.sponsor_preferences.update(notify_sponsor_on_update=False)

        subscribed_sponsors = company.sponsor_preferences.get_companies_to_be_notified()
        self.assertEqual([], list(subscribed_sponsors))

    def test_per_company_sponsored_defaults(self):
        """Verifies that SponsorPreferences looks up defaults via company slug."""
        company = general_organization_factory()
        sponsor = general_organization_factory()

        test_defaults = {
            "can_edit_profile": False,
            "can_edit_identity_fields": False,
            "notify_sponsor_on_update": False,
        }

        def sponsor_defaults(prefs):
            sponsor_defaults.executed = True
            return test_defaults

        sponsor_defaults.executed = False

        slug = sponsor.slug.replace("-", "_")
        setattr(
            SponsorPreferences,
            "get_{}_sponsored_defaults".format(slug),
            sponsor_defaults,
        )

        company.add_sponsor(sponsor)
        sponsor_preferences = company.sponsor_preferences.get()
        self.assertEqual(sponsor_defaults.executed, True)
        self.assertEqual(sponsor_preferences.can_edit_profile, test_defaults["can_edit_profile"])
        self.assertEqual(
            sponsor_preferences.can_edit_identity_fields,
            test_defaults["can_edit_identity_fields"],
        )
        self.assertEqual(
            sponsor_preferences.notify_sponsor_on_update,
            test_defaults["notify_sponsor_on_update"],
        )

        # Verify that these defaults do not affect existing sponsorships (where pk != None)
        sponsor_preferences.can_edit_profile = not sponsor_preferences.can_edit_profile
        sponsor_preferences.save()
        self.assertNotEqual(sponsor_preferences.can_edit_profile, test_defaults["can_edit_profile"])

    def test_create_relationship_with_sponsored_company_when_sponsor_preference_created(
        self,
    ):
        company = general_organization_factory()
        sponsor = rater_organization_factory()
        relationships = Relationship.objects.filter_by_company(company, show_attached=True)

        self.assertEqual(relationships.count(), 0)

        company.add_sponsor(sponsor)

        relationships = Relationship.objects.filter_by_company(company, show_attached=True)

        self.assertEqual(relationships.count(), 1)

    def test_create_customer_hirl_builder_organization_post_save(self):
        self.assertEqual(HIRLBuilderOrganization.objects.count(), 0)
        builder_organization = builder_organization_factory()
        hirl_builder_organization = HIRLBuilderOrganization.objects.get()
        self.assertEqual(hirl_builder_organization.builder_organization, builder_organization)
        builder_organization.name = "change name"
        builder_organization.save()
        self.assertEqual(HIRLBuilderOrganization.objects.count(), 1)

    def test_create_customer_hirl_client_organization(self):
        self.assertEqual(HIRLCompanyClient.objects.count(), 0)
        builder_organization = builder_organization_factory()
        hirl_company_client = HIRLCompanyClient.objects.get()
        self.assertEqual(hirl_company_client.company.id, builder_organization.id)
        builder_organization.name = "change name"
        builder_organization.save()
        self.assertEqual(HIRLCompanyClient.objects.count(), 1)

        with self.subTest("Create HIRLCompanyClient only for certain types"):
            general_organization_factory()
            self.assertEqual(HIRLCompanyClient.objects.count(), 1)

    def test_create_customer_hirl_legacy_rater_user_post_save(self):
        from axis.customer_hirl.models import HIRLRaterUser

        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        verifier_company = rater_organization_factory()
        rater_user = rater_admin_factory(company=verifier_company)
        rater_user2 = rater_admin_factory(company=verifier_company)

        self.assertIsNone(getattr(rater_user, "hirlrateruser", None))
        self.assertIsNone(getattr(rater_user2, "hirlrateruser", None))

        verifier_company.sponsor_preferences.create(sponsor=hirl_company)

        rater_user.refresh_from_db()
        rater_user2.refresh_from_db()

        self.assertIsNotNone(getattr(rater_user, "hirlrateruser", None))
        self.assertIsNotNone(getattr(rater_user2, "hirlrateruser", None))

        with self.subTest(
            "Check that we are not create duplicate legacy records "
            "when delete and assign new sponsor preference"
        ):
            verifier_company.sponsors.clear()

            self.assertEqual(verifier_company.sponsors.count(), 0)

            rater_user.refresh_from_db()
            rater_user2.refresh_from_db()

            self.assertIsNotNone(getattr(rater_user, "hirlrateruser", None))
            self.assertIsNotNone(getattr(rater_user2, "hirlrateruser", None))

            verifier_company.sponsor_preferences.create(sponsor=hirl_company)

            self.assertEqual(HIRLRaterUser.objects.count(), 2)


class GeographicAtomicityTestCase(AxisTestCase):
    def setUp(self):
        from axis.geographic.models import City, County

        self.county_obj = County.objects.create(
            name="Maricopa",
            legal_statistical_area_description="Maricopa County",
            state="AZ",
            latitude=33.346541,
            longitude=-112.495534,
            county_type=1,
            water_area_meters=62795719,
            land_area_meters=23828260196,
        )

        self.city_obj = City.objects.create(
            name="Gilbert",
            legal_statistical_area_description="Gilbert town",
            county=self.county_obj,
            latitude=33.310209,
            longitude=-111.742191,
            water_area_meters=475521,
            land_area_meters=176023316,
            place_fips="0427400",
            ansi_code="02412682",
        )

        self.zipcode = "85297"
        self.state = "AZ"
        self.county = self.county_obj
        self.city = self.city_obj

        self.intersection = "Gilbert Rd & Elliot Rd"
        self.street_line1 = "301 N Gilbert Road"
        self.street_line2 = ""

        self.addr = {
            "street_line1": self.street_line1,
            "street_line2": self.street_line2,
            "city": self.city,
            "state": self.state,
            "zipcode": self.zipcode,
        }

        self.addr_keys = [
            "street_line1",
            "street_line2",
            "city",
            "state",
            "zipcode",
            "latitude",
            "longitude",
            "geocode_response",
            "place",
        ]

    def test_company_blind_geocode_address(self):
        from axis.company.models import Company
        from axis.geocoder.models import GeocodeResponse
        from axis.geographic.models import Place
        from axis.geographic.utils.legacy import do_blind_geocode

        company = Company.objects.create(name="Joes BBQ", **self.addr)

        self.assertEqual(company.history.all().count(), 1)
        self.assertIsNone(company.latitude)
        self.assertIsNone(company.longitude)
        self.assertIsNone(company.geocode_response)
        self.assertIsNotNone(company.place)
        self.assertEqual(GeocodeResponse.objects.all().count(), 0)
        total_places = Place.objects.all().count()

        company = do_blind_geocode(company, **self.addr)

        self.assertIsNotNone(company.latitude)
        self.assertIsNotNone(company.longitude)
        self.assertIsNotNone(company.geocode_response)
        self.assertIsNotNone(company.place)
        self.assertEqual(company.history.all().count(), 2)
        self.assertEqual(GeocodeResponse.objects.all().count(), 2)

        self.assertIn(self.street_line1, company.geocode_response.geocode.raw_address)
        self.assertIn(self.street_line2, company.geocode_response.geocode.raw_address)
        self.assertIn(self.city.name, company.geocode_response.geocode.raw_address)
        self.assertIn(self.state, company.geocode_response.geocode.raw_address)
        self.assertIn(self.zipcode, company.geocode_response.geocode.raw_address)
        self.assertGreater(Place.objects.all().count(), total_places)


class TestCompanyAccess(AxisTestCase):
    def test_update_is_company_admin_for_user_when_role_changed(self):
        rater_user = rater_admin_factory(company__name="Company 1", is_company_admin=True)
        self.assertEqual(rater_user.companyaccess_set.count(), 1)
        self.assertTrue(rater_user.is_company_admin)

        company_access = rater_user.companyaccess_set.first()

        self.assertEqual(company_access.roles.filter(slug=CompanyRole.IS_COMPANY_ADMIN).count(), 1)

        is_company_admin_role = CompanyRole.objects.get(slug=CompanyRole.IS_COMPANY_ADMIN)

        company_access.roles.add(is_company_admin_role)

        rater_user.refresh_from_db()
        self.assertTrue(rater_user.is_company_admin)
