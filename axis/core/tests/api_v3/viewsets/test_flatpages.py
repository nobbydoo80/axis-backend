"""flatpages.py: """

__author__ = "Artem Hruzd"
__date__ = "11/16/2020 14:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from django.utils import timezone

from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import provider_user_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.core.models import AxisFlatPage
from django.urls import reverse_lazy

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestFlatPageViewSet(ApiV3Tests):
    def setUp(self) -> None:
        static_flat_page = AxisFlatPage.objects.create(
            title="Static flat page", url="/statis/page", content="<p>HTML CONTENT</p>", order=1
        )

        news_flat_page = AxisFlatPage.objects.create(
            title="News flat page",
            url="/public-news/10-31-2014/",
            content="<p>HTML CONTENT</p>",
            created_at=timezone.now(),
        )

        news_flat_page2 = AxisFlatPage.objects.create(
            title="News flat page",
            url="/public-news/10-31-2016/",
            content="<p>HTML CONTENT</p>",
            created_at=timezone.now() - timezone.timedelta(days=1),
        )

        verifier_page = AxisFlatPage.objects.create(
            title="Verifier page",
            url=customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL,
            content="<p>HTML CONTENT</p>",
            created_at=timezone.now() - timezone.timedelta(days=1),
        )

        verifier_page_archive_2020 = AxisFlatPage.objects.create(
            title="Verifier page",
            url=f"{customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL}2020/",
            content="<p>HTML CONTENT</p>",
            created_at=timezone.now() - timezone.timedelta(days=1),
        )

        builder_central = AxisFlatPage.objects.create(
            title="Builder Central page",
            url=customer_hirl_app.BUILDER_CENTRAL_PAGE_URL,
            content="<p>HTML CONTENT</p>",
            created_at=timezone.now() - timezone.timedelta(days=1),
        )

    def test_list(self):
        url = reverse_lazy("api_v3:flatpages-list")
        data = self.list(url, user=None)
        self.assertEqual(len(data), 0)

    def test_news(self):
        url = reverse_lazy("api_v3:flatpages-news")
        data = self.list(url, user=None)
        self.assertEqual(len(data), 2)

    def test_verifier_resources_page(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_page = AxisFlatPage.objects.get(url=customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL)
        url = reverse_lazy("api_v3:flatpages-verifier-resources-page")
        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["id"], verifier_page.id)

    def test_verifier_resources_page_by_year(self):
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        verifier_page_archive_2020 = AxisFlatPage.objects.get(
            url=f"{customer_hirl_app.VERIFIER_RESOURCES_PAGE_URL}2020/"
        )
        url = reverse_lazy(
            "api_v3:flatpages-verifier-resources-page-by-year", kwargs={"year": 2020}
        )
        self.client.force_authenticate(user=hirl_user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["id"], verifier_page_archive_2020.id)

    def test_builder_central_page(self):
        builder_central_page = AxisFlatPage.objects.get(
            url=customer_hirl_app.BUILDER_CENTRAL_PAGE_URL
        )
        url = reverse_lazy("api_v3:flatpages-builder-central-page")
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["id"], builder_central_page.id)
