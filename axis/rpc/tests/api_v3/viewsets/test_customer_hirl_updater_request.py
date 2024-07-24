"""test_customer_hirl_updater_request.py: """

__author__ = "Artem Hruzd"
__date__ = "12/11/2022 16:07"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io
import random

from unittest import mock
from unittest.mock import MagicMock

from django.apps import apps
from django.urls import reverse_lazy

from axis.company.tests.factories import (
    provider_organization_factory,
)
from axis.core.tests.factories import (
    provider_user_factory,
)
from axis.core.tests.testcases import ApiV3Tests
from axis.rpc.models import HIRLRPCUpdaterRequest, RPCSession
from axis.rpc.tests.factories import hirl_rpc_updater_request_factory, rpc_session_factory

customer_hirl_app = apps.get_app_config("customer_hirl")


class TestHIRLRPCUpdaterRequestViewSet(ApiV3Tests):
    def test_list(self):
        list_url = reverse_lazy("api_v3:hirl_rpc_updater_request-list")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        hirl_rpc_updater_request = hirl_rpc_updater_request_factory(
            user=hirl_user, state=HIRLRPCUpdaterRequest.SUCCESS_STATE
        )

        kwargs = dict(url=list_url, user=hirl_user)

        data = self.list(**kwargs)
        self.assertEqual(len(data), HIRLRPCUpdaterRequest.objects.count())
        self.assertEqual(data[0]["id"], hirl_rpc_updater_request.id)
        self.assertEqual(data[0]["state"], HIRLRPCUpdaterRequest.SUCCESS_STATE)

    @mock.patch("rpyc.connect")
    def test_create(self, rpyc_mock_connect):
        create_url = reverse_lazy("api_v3:hirl_rpc_updater_request-list")
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        hirl_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        rpc_session_factory(session_type=RPCSession.CUSTOMER_HIRL_UPDATER_SERVICE_TYPE)
        # mock service upload function
        m = MagicMock()
        rpyc_mock_connect.return_value = m
        m.root.upload.return_value = __file__

        with io.open(__file__, "rb") as f:
            minimum_required_data = {
                "scoring_path": random.choice(HIRLRPCUpdaterRequest.SCORING_PATH_CHOICES)[0],
                "report_file": f,
                "project_type": random.choice(HIRLRPCUpdaterRequest.PROJECT_TYPE_CHOICES)[0],
            }

            data = self.create(
                url=create_url, user=hirl_user, data=minimum_required_data, data_format="multipart"
            )

        hirl_rpc_updater_request = HIRLRPCUpdaterRequest.objects.get()

        self.assertEqual(hirl_rpc_updater_request.state, HIRLRPCUpdaterRequest.SUCCESS_STATE)
