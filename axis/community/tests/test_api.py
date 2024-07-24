"""test_api.py - axis"""

__author__ = "Steven K"
__date__ = "10/26/22 13:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.community.models import Community
from axis.community.serializers import CommunitySerializer
from axis.community.tests.mixins import CommunityViewTestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.geocoder.models import GeocodeResponse

log = logging.getLogger(__name__)


class CommunityAPITests(CommunityViewTestMixin, AxisTestCase):
    """Test out community API"""

    client_class = AxisClient

    def test_display_raw_address_bug_zd41381(self):
        # We found a bug where on display raw addresses.
        user = self.admin_user
        user.company.display_raw_addresses = True
        user.company.save()
        user.refresh_from_db()

        instance = Community.objects.first()

        class Fake_req:
            pass

        Fake_req.user = user

        self.assertEqual(instance.geocode_response, None)
        geo_response = GeocodeResponse.objects.first()
        instance.geocode_response = geo_response
        instance.save()

        serializer = CommunitySerializer(instance=instance, context={"request": Fake_req})
        data = serializer.to_representation(instance=instance)
        self.assertEqual(data["geocode_response"], geo_response.id)
