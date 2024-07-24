"""message.py: """


from rest_framework import serializers

from axis.core.api_v3.serializers import BasicUserSerializer
from axis.messaging.messages import MESSAGE_REGISTRY
from axis.messaging.models import Message, MessagingPreference, DigestPreference

__author__ = "Artem Hruzd"
__date__ = "01/07/2020 12:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_info = BasicUserSerializer(source="user", read_only=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "user",
            "user_info",
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
        )


class MessageCategorySerializer(serializers.Serializer):
    value = serializers.CharField()
    name = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class MessagePreferenceListSerializer(serializers.ModelSerializer):
    """
    Using for display message preferences
    """

    required = serializers.BooleanField(read_only=True)
    verbose_name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    sticky_alert = serializers.BooleanField(read_only=True)
    unique = serializers.BooleanField(read_only=True)
    level = serializers.BooleanField(read_only=True)
    company_admins_only = serializers.ListField(read_only=True)
    company_types = serializers.ListField(read_only=True)
    company_slugs = serializers.ListField(read_only=True)
    companies_with_relationship = serializers.ListField(read_only=True)
    companies_with_relationship_or_self = serializers.ListField(read_only=True)

    class Meta:
        model = MessagingPreference
        fields = (
            "id",
            "category",
            "message_name",
            "receive_email",
            "receive_notification",
            # message class fields
            "required",
            "verbose_name",
            "description",
            "sticky_alert",
            "unique",
            "level",
            "company_admins_only",
            "company_types",
            "company_slugs",
            "companies_with_relationship",
            "companies_with_relationship_or_self",
        )
        read_only_fields = ("category", "message_name", "receive_email", "receive_notification")


class MessagePreferenceWritableSerializer(serializers.ModelSerializer):
    """
    Create or update single message preference
    """

    class Meta:
        model = MessagingPreference
        fields = ("message_name", "receive_email", "receive_notification")

    def validate_message_name(self, value):
        try:
            modern_message = MESSAGE_REGISTRY[value]
        except KeyError:
            raise serializers.ValidationError({"message_name": "Does not exist"})

        if modern_message.required:
            raise serializers.ValidationError(
                {"message_name": "Required message preference cannot be modified"}
            )

        user = self.context["user"]
        if (
            modern_message.company_types
            and user.company.company_type not in modern_message.company_types
        ):
            raise serializers.ValidationError(
                {"message_name": "Your company type cannot modify this message preference"}
            )

        if modern_message.company_slugs and user.company.slug not in modern_message.company_slugs:
            raise serializers.ValidationError(
                {"message_name": "Your company cannot modify this message preference"}
            )

        if modern_message.company_admins_only and user.is_company_admin:
            raise serializers.ValidationError(
                {"message_name": "You cannot modify this message preference"}
            )

        return value

    def create(self, validated_data):
        message_name = validated_data.pop("message_name")
        user = self.context["user"]

        instance, created = MessagingPreference.objects.update_or_create(
            message_name=message_name, user=user, defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        raise NotImplementedError


class DigestPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigestPreference
        fields = ("threshold",)

    def create(self, validated_data):
        user = self.context["user"]

        instance, created = DigestPreference.objects.update_or_create(
            user=user, defaults=validated_data
        )
        return instance
