"""zendesk.py: """

__author__ = "Artem Hruzd"
__date__ = "05/21/2021 9:32 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from unittest import mock

from django.test import override_settings
from rest_framework.reverse import reverse_lazy

from axis.core.tests.factories import general_user_factory
from axis.core.tests.testcases import ApiV3Tests


class ZendeskMock:
    """
    Zendesk API Mock object
    """

    def __init__(self, *args, **kwargs):
        pass

    def ticket_show(self, ticket_id, **kwargs):
        return {
            "ticket": {
                "assignee_id": 235323,
                "collaborator_ids": [35334, 234],
                "created_at": "2009-07-20T22:55:29Z",
                "custom_fields": [
                    {"id": 27642, "value": "745"},
                    {"id": 27648, "value": "yes"},
                ],
                "description": "The fire is very colorful.",
                "due_at": None,
                "external_id": "ahg35h3jh",
                "follower_ids": [35334, 234],
                "group_id": 98738,
                "has_incidents": False,
                "id": 1,
                "organization_id": 509974,
                "priority": "high",
                "problem_id": 9873764,
                "raw_subject": "{{dc.printer_on_fire}}",
                "recipient": "support@company.com",
                "requester_id": 20978392,
                "satisfaction_rating": {
                    "comment": "Great support!",
                    "id": 1234,
                    "score": "good",
                },
                "sharing_agreement_ids": [84432],
                "status": "open",
                "subject": "Help, my printer is on fire!",
                "submitter_id": 76872,
                "tags": ["enterprise", "other_tag"],
                "type": "incident",
                "updated_at": "2011-05-05T10:38:52Z",
                "url": "https://company.zendesk.com/api/v2/tickets/1.json",
                "via": {"channel": "web"},
            }
        }

    def ticket_create(self, data, **kwargs):
        return "https://company.zendesk.com/api/v2/tickets/1.json"

    def request_show(self, request_id):
        return {
            "request": {
                "url": "https://company.zendesk.com/api/v2/requests/1.json",
                "id": 1,
                "status": "new",
                "priority": "urgent",
                "type": "incident",
                "subject": "artem test 7",
                "description": "test",
                "organization_id": "None",
                "via": {
                    "channel": "api",
                    "source": {"from": {}, "to": {}, "rel": "None"},
                },
                "custom_fields": [],
                "requester_id": 4535953494669,
                "collaborator_ids": [],
                "email_cc_ids": [],
                "is_public": True,
                "due_at": "None",
                "can_be_solved_by_me": False,
                "created_at": "2022-02-28T20:01:27Z",
                "updated_at": "2022-02-28T20:01:27Z",
                "recipient": "None",
                "followup_source_id": "None",
                "assignee_id": "None",
                "fields": [],
            }
        }

    def request_create(self, data, **kwargs):
        return "https://company.zendesk.com/api/v2/requests/1.json"


class TestZendeskViewset(ApiV3Tests):
    @mock.patch("axis.core.api_v3.serializers.zendesk.Zendesk", ZendeskMock)
    @override_settings(ZENDESK_URL="http://example.com")
    def test_request_create(self):
        user = general_user_factory()
        url = reverse_lazy("api_v3:zendesk-request-create")

        kwargs = dict(
            url=url,
            user=user,
            data={
                "subject": "New Ticket",
                "current_page": "Main Page",
                "ticket_type": "question",
                "priority": "low",
                "comment": {"body": "Comment Body"},
            },
        )

        data = self.create(**kwargs)

        self.assertEqual(
            data,
            {
                "api_url": "https://company.zendesk.com/api/v2/requests/1.json",
                "url": "http://example.com/requests/1",
            },
        )
