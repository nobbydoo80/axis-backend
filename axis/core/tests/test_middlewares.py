"""test_middlewares.py: """

__author__ = "Artem Hruzd"
__date__ = "08/09/2021 7:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from unittest.mock import Mock

from django.contrib.sites.models import Site

from axis.core.middleware import DynamicSiteDomainMiddleware
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase


class MiddlewareTests(AxisTestCase):
    client_class = AxisClient

    def test_dynamic_site_domain_middleware(self):
        example_site = Site.objects.get(domain="example.com")
        hi_site = Site.objects.create(
            name="homeinnovation", domain="homeinnovation.pivotalenergy.net"
        )
        request = Mock()
        request.get_host = lambda: "homeinnovation.pivotalenergy.net"

        with self.settings(SITE_ID=1):
            my_middleware = DynamicSiteDomainMiddleware(request)
            my_middleware(request)
            self.assertEqual(request.current_site, hi_site)

        request.get_host = lambda: "Unknown domain"

        with self.settings(SITE_ID=1):
            my_middleware = DynamicSiteDomainMiddleware(request)
            my_middleware(request)
            self.assertEqual(request.current_site, example_site)
