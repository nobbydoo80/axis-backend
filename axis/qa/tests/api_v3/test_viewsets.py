# -*- coding: utf-8 -*-
"""test_viewsets.py: """

__author__ = "Artem Hruzd"
__date__ = "08/22/2022 19:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.urls import reverse_lazy

from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import provider_user_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.qa.models import QAStatus
from axis.qa.tests.factories import qa_status_factory


class TestQAStatusViewSet(ApiV3Tests):
    def test_list(self):
        list_url = reverse_lazy("api_v3:qa_statuses-list")
        hirl_company = provider_organization_factory(name="Home Innovation Research Labs")
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        qa_status = qa_status_factory(owner=hirl_company)

        data = self.list(url=list_url, user=hirl_user)
        self.assertEqual(len(data), QAStatus.objects.count())
        self.assertEqual(data[0]["id"], qa_status.id)

    def test_customer_hirl_list(self):
        list_url = reverse_lazy("api_v3:qa_statuses-customer-hirl-list")
        hirl_company = provider_organization_factory(name="Home Innovation Research Labs")
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        qa_status = qa_status_factory(owner=hirl_company)

        data = self.list(url=list_url, user=hirl_user)
        self.assertEqual(len(data), QAStatus.objects.count())
        self.assertEqual(data[0]["id"], qa_status.id)

    def test_customer_hirl_user_filter_badges_count(self):
        list_url = reverse_lazy("api_v3:qa_statuses-customer-hirl-user-filter-badges-count")
        hirl_company = provider_organization_factory(name="Home Innovation Research Labs")
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )
        qa_status_factory(owner=hirl_company, qa_designee=hirl_user)

        data = self.retrieve(url=list_url, user=hirl_user)
        self.assertEqual(data["all_projects"], 1)
        self.assertEqual(data["my_projects"], 1)
