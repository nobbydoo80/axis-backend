"""management_commands.py: """
from io import StringIO
from unittest import mock
from unittest.mock import patch, Mock

from django.core.management import call_command

from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import ApiV3Tests
from .mixins import EquipmentFixtureMixin
from ..models import EquipmentSponsorStatus

__author__ = "Artem Hruzd"
__date__ = "11/11/2019 21:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrackEquipmentCompanySponsorStatusesTest(EquipmentFixtureMixin, ApiV3Tests):
    client_class = AxisClient

    @mock.patch(
        "axis.equipment.management.commands."
        "track_equipment_company_sponsor_statuses.Command._boolean_input",
        return_value="Y",
    )
    @patch(
        "axis.equipment.management.commands.track_equipment_company_sponsor_statuses.equipment_app",
        Mock(
            EQUIPMENT_APPLICABLE_REQUIREMENTS={
                "neea": [
                    "wa-code-study",
                ]
            }
        ),
    )
    def test_create_track_equipment_company_sponsor_statuses(self, mock_user_input):
        neea_equipment_sponsos_statuses = EquipmentSponsorStatus.objects.filter(
            company__slug="neea"
        )
        old_count = neea_equipment_sponsos_statuses.count()
        neea_equipment_sponsos_statuses.delete()
        self.assertGreater(old_count, 0)
        out = StringIO()
        call_command("track_equipment_company_sponsor_statuses", stdout=out)
        mock_user_input.assert_called_once()
        self.assertEqual(EquipmentSponsorStatus.objects.count(), old_count)
