__author__ = "Artem Hruzd"
__date__ = "07/06/2020 16:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.apps import apps
from rest_framework import status

from axis.company.models import (
    BuilderOrganization,
    SponsorPreferences,
    ProviderOrganization,
    Company,
)
from axis.company.tests.factories import provider_organization_factory
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.factories import provider_user_factory
from axis.core.tests.testcases import ApiV3Tests


User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class TestSponsoringViewSet(CompaniesAndUsersTestMixin, ApiV3Tests):
    include_company_types = ["provider", "builder"]
    include_unrelated_companies = False
    include_noperms_user = False

    def test_retrieve_as_provider_company_admin_member(self):
        user = User.objects.filter(
            is_superuser=False, is_company_admin=True, company__company_type="provider"
        ).first()
        builder_organization = Company.objects.filter(
            company_type=Company.BUILDER_COMPANY_TYPE
        ).first()
        sponsor_preferences = SponsorPreferences.objects.create(
            sponsor=user.company, sponsored_company=builder_organization
        )
        user.company.sponsored_preferences.add(sponsor_preferences)

        retrieve_url = reverse_lazy(
            "api_v3:sponsoring_preferences-detail", args=(sponsor_preferences.id,)
        )
        kwargs = dict(url=retrieve_url, user=user)
        data = self.retrieve(**kwargs)
        self.assertEqual(data["id"], sponsor_preferences.id)

    def test_retrieve_as_provider_company_member(self):
        user = User.objects.filter(
            is_superuser=False, is_company_admin=False, company__company_type="provider"
        ).first()
        builder_organization = Company.objects.filter(
            company_type=Company.BUILDER_COMPANY_TYPE
        ).first()
        sponsor_preferences = SponsorPreferences.objects.create(
            sponsor=user.company, sponsored_company=builder_organization
        )
        user.company.sponsored_preferences.add(sponsor_preferences)

        retrieve_url = reverse_lazy(
            "api_v3:sponsoring_preferences-detail", args=(sponsor_preferences.id,)
        )
        kwargs = dict(url=retrieve_url, user=user)
        self.retrieve(**kwargs)

    def test_update_as_provider_company_admin_member(self):
        user = User.objects.filter(
            is_superuser=False, is_company_admin=True, company__company_type="provider"
        ).first()
        builder_organization = Company.objects.filter(
            company_type=Company.BUILDER_COMPANY_TYPE
        ).first()
        sponsor_preferences = SponsorPreferences.objects.create(
            sponsor=user.company, sponsored_company=builder_organization
        )
        user.company.sponsored_preferences.add(sponsor_preferences)

        update_url = reverse_lazy(
            "api_v3:sponsoring_preferences-detail", args=(sponsor_preferences.id,)
        )
        kwargs = dict(
            url=update_url,
            user=user,
            data=dict(
                can_edit_profile=False,
                can_edit_identity_fields=False,
                notify_sponsor_on_update=False,
            ),
        )
        data = self.update(**kwargs)
        self.assertFalse(data["can_edit_profile"])
        self.assertFalse(data["can_edit_identity_fields"])
        self.assertFalse(data["notify_sponsor_on_update"])

    def test_create(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        another_provider_user = provider_user_factory()
        builder_organization = Company.objects.filter(
            company_type=Company.BUILDER_COMPANY_TYPE
        ).first()

        create_url = reverse_lazy("api_v3:sponsoring_preferences-list")
        kwargs = dict(
            url=create_url,
            user=hirl_user,
            data=dict(
                sponsor=hirl_company.id,
                sponsored_company=builder_organization.id,
                can_edit_profile=False,
                can_edit_identity_fields=False,
                notify_sponsor_on_update=False,
            ),
        )
        data = self.create(**kwargs)
        self.assertFalse(data["can_edit_profile"])
        self.assertFalse(data["can_edit_identity_fields"])
        self.assertFalse(data["notify_sponsor_on_update"])

        with self.subTest("Try to create Sponsor Preference by non HIRL company"):
            kwargs = dict(
                url=create_url,
                user=another_provider_user,
                data=dict(
                    sponsor=hirl_company.id,
                    sponsored_company=builder_organization.id,
                    can_edit_profile=False,
                    can_edit_identity_fields=False,
                    notify_sponsor_on_update=False,
                ),
            )
            data = self.create(**kwargs, expected_status=status.HTTP_403_FORBIDDEN)


class TestNestedSponsoringViewSet(CompaniesAndUsersTestMixin, ApiV3Tests):
    include_company_types = ["provider", "builder"]
    include_unrelated = False
    include_noperms = False

    def test_list_as_provider_company_member(self):
        user = User.objects.filter(is_superuser=False, company__company_type="provider").first()
        builder_organization = Company.objects.filter(
            company_type=Company.BUILDER_COMPANY_TYPE
        ).first()
        sponsor_preferences = SponsorPreferences.objects.create(
            sponsor=user.company, sponsored_company=builder_organization
        )
        user.company.sponsored_preferences.add(sponsor_preferences)
        list_url = reverse_lazy("api_v3:company-sponsoring-list", args=(user.company.pk,))
        data = self.list(user=user, url=list_url)
        affiliation_companies_count = user.company.sponsored_preferences.count()
        self.assertGreater(affiliation_companies_count, 0)
        self.assertEqual(len(data), affiliation_companies_count)


class TestNestedAffiliationsViewSet(CompaniesAndUsersTestMixin, ApiV3Tests):
    include_company_types = ["provider", "builder"]
    include_unrelated = False
    include_noperms = False

    def test_list_as_builder_company_member(self):
        user = User.objects.filter(is_superuser=False, company__company_type="builder").first()
        provider_organization = Company.objects.filter(
            company_type=Company.PROVIDER_COMPANY_TYPE
        ).first()
        sponsor_preferences = SponsorPreferences.objects.create(
            sponsor=provider_organization, sponsored_company=user.company
        )
        provider_organization.sponsored_preferences.add(sponsor_preferences)
        list_url = reverse_lazy("api_v3:company-affiliations-list", args=(user.company.pk,))
        data = self.list(user=user, url=list_url)
        sponsoring_companies_count = user.company.sponsor_preferences.count()
        self.assertGreater(sponsoring_companies_count, 0)
        self.assertEqual(len(data), sponsoring_companies_count)
