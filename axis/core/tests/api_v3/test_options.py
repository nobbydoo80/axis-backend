"""options.py - Axis"""

import logging

from rest_framework.reverse import reverse_lazy

from axis.core.tests.mixins import ImpersonateTestMixin
from axis.core.tests.testcases import ApiV3Tests

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "7/1/20 13:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class AxisOptionsTests(ImpersonateTestMixin, ApiV3Tests):
    def test_list_options(self):
        """Verify that we can actually see some perms."""
        url = reverse_lazy("api_v3:users-list")
        data = self.options(url, self.super_user)
        self.assertEqual(set(data["permissions"].keys()), {"can_list", "can_retrieve"})
        self.assertTrue(data["permissions"]["can_list"])
        # self.assertTrue(data['permissions']['can_create'])
        self.assertTrue(data["permissions"]["can_retrieve"])

        # import json
        # print(json.dumps(data, indent=4))

    def test_detail_options(self):
        """Shows how the the perms work on a detail view"""
        url = reverse_lazy("api_v3:users-detail", kwargs={"pk": self.super_user.id})

        data = self.options(url, self.super_user)

        self.assertEqual(
            set(data["permissions"].keys()),
            {"can_retrieve", "can_partial_update", "can_update", "can_destroy"},
        )
        self.assertTrue(data["permissions"]["can_retrieve"])
        self.assertTrue(data["permissions"]["can_partial_update"])
        self.assertTrue(data["permissions"]["can_update"])
        self.assertTrue(data["permissions"]["can_destroy"])
