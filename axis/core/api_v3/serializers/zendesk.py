"""zendesk.py: """

__author__ = "Artem Hruzd"
__date__ = "05/21/2021 12:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.conf import settings
from rest_framework import serializers
from zdesk import get_id_from_url, Zendesk


class ZendeskCreateTicketCommentSerializer(serializers.Serializer):
    body = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class ZendeskCreateRequestSerializer(serializers.Serializer):
    """
    Ticket Create API ViewSet request data
    """

    subject = serializers.CharField(max_length=255)
    current_page = serializers.CharField()
    other_pages = serializers.CharField(allow_blank=True, default="")
    ticket_type = serializers.ChoiceField(
        choices=(
            ("question", "Question"),
            ("incident", "Incident"),
            ("problem", "Problem"),
            ("task", "Task"),
        )
    )
    priority = serializers.ChoiceField(
        choices=(("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent"))
    )
    comment = ZendeskCreateTicketCommentSerializer()

    def create(self, validated_data):
        request = self.context.get("request", None)
        zendesk_client = Zendesk(
            "https://pivotalenergysolutions.zendesk.com",
            zdesk_email=settings.ZENDESK_AGENT_EMAIL,
            zdesk_password=settings.ZENDESK_AGENT_PASSWORD,
        )

        if not request or not zendesk_client:
            raise serializers.ValidationError(
                {"non_field_errors": "User is not provided or credentials are not valid"}
            )

        if not request.user.is_authenticated:
            raise serializers.ValidationError({"non_field_errors": "User is not authenticated"})

        requester_name = f"{request.user.first_name} {request.user.last_name}"
        requester_email = f"{request.user.email}"

        response = zendesk_client.request_create(
            data={
                "request": {
                    "subject": validated_data["subject"],
                    "requester": {"name": requester_name, "email": requester_email},
                    "current_page": validated_data["current_page"],
                    "other_pages": validated_data["other_pages"],
                    "type": validated_data["ticket_type"],
                    "priority": validated_data["priority"],
                    "comment": {"body": validated_data["comment"]["body"]},
                }
            }
        )
        request_id = get_id_from_url(response)
        zendesk_request = zendesk_client.request_show(request_id)
        return zendesk_request

    def update(self, instance, validated_data):
        raise NotImplementedError


class ZendeskCreateRequestResponseSerializer(serializers.Serializer):
    """
    Ticket Create API ViewSet response
    """

    api_url = serializers.CharField()
    url = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
