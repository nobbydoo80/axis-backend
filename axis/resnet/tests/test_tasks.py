"""test_tasks.py Testing resnet tasks"""


from unittest.mock import patch

from django.test import TestCase

from axis.resnet.models import RESNETCompany
from axis.resnet.tasks import update_resnet_database
from .utils import mock_provider_start_page_data

__author__ = "Artem Hruzd"
__date__ = "06/11/19 09:27"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]


class RESNETTaskTest(TestCase):
    """Test the tasks"""

    @patch(
        "axis.resnet.data_scraper.RESENTProvider.get_start_page",
        return_value=mock_provider_start_page_data(provider_key="RESENTProvider"),
    )
    @patch(
        "axis.resnet.data_scraper.RESNETSamplingProvider.get_start_page",
        return_value=mock_provider_start_page_data(provider_key="RESNETSamplingProvider"),
    )
    @patch(
        "axis.resnet.data_scraper.RESNETTrainingProvider.get_start_page",
        return_value=mock_provider_start_page_data(provider_key="RESNETTrainingProvider"),
    )
    @patch(
        "axis.resnet.data_scraper.RESNETWaterSenseProvider.get_start_page",
        return_value=mock_provider_start_page_data(provider_key="RESNETWaterSenseProvider"),
    )
    def test_update_resnet_database_success(
        self, water_get_start_page, training_get_start_page, sampling_get_start_page, get_start_page
    ):
        """Verify that we can update the RESNET DB"""
        update_resnet_database()

        water_get_start_page.assert_called_once()
        training_get_start_page.assert_called_once()
        sampling_get_start_page.assert_called_once()
        get_start_page.assert_called_once()
        # Our test sources contains 108 RESNETCompany objects that should be created
        # if you will modify sources data this value must be changed
        self.assertEqual(RESNETCompany.objects.count(), 108)
