import logging

from rest_framework import serializers

from django.utils.timezone import now
from django.conf import settings

from django.contrib.auth import get_user_model
from .models import Message, DigestPreference


__author__ = "Autumn Valenta"
__date__ = "3/3/15 1:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user")
    is_recent = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "user",
            "sender",
            "title",
            "content",
            "level",
            "category",
            "sticky_alert",
            "date_created",
            "date_alerted",
            "date_sent",
            "alert_read",
            "email_read",
            "url",
            "user_name",
            "is_recent",
        )

    def get_is_recent(self, obj):
        """
        Client-side hint for whether the alert actually needs to be shown or not by the pop-up
        notification system.
        """
        if obj.date_alerted is None:
            return True

        return now() <= (obj.date_alerted + settings.MESSAGING_RENOTIFICATION_GRACE_PERIOD)


class UserDigestSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("messages",)

    def to_representation(self, obj):
        data = super(UserDigestSerializer, self).to_representation(obj)
        data.update(
            {
                "count": len(data["messages"]),
                "threshold_display": dict(DigestPreference.DIGEST_CHOICES).get(
                    self.context.get("threshold")
                ),
            }
        )
        return data

    def get_messages(self, obj):
        queryset = (
            obj.received_messages.since(self.context.get("start"), self.context.get("end"))
            .threshold(self.context.get("threshold"))
            .select_related("user")
        )
        return MessageSerializer(queryset, many=True).data
