"""message.py: """


from unittest import mock

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse_lazy

from axis.core.tests.testcases import ApiV3Tests
from axis.messaging.models import Message, MessagingPreference
from axis.messaging.tests.factories import (
    modern_message_cls_factory,
    modern_message_registry_factory,
)
from axis.messaging.tests.mixins import MessagingTestMixin

__author__ = "Artem Hruzd"
__date__ = "05/20/2020 19:14"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

User = get_user_model()


class TestMessageViewSet(MessagingTestMixin, ApiV3Tests):
    def test_retrieve_as_owner(self):
        message = Message.objects.order_by("?").first()
        detail_url = reverse_lazy("api_v3:messages-detail", args=(message.id,))

        kwargs = dict(url=detail_url, user=message.user)
        data = self.retrieve(**kwargs)
        self.assertEqual(data["id"], message.id)

    def test_retrieve_as_another_user(self):
        rater_user = self.get_nonadmin_user(company_type="rater")
        provider_user = self.get_random_user(company_type="provider")
        message = rater_user.received_messages.first()
        detail_url = reverse_lazy("api_v3:messages-detail", args=(message.id,))

        kwargs = dict(url=detail_url, user=provider_user)
        with self.assertRaises(AssertionError):
            self.retrieve(**kwargs)

    def test_retrieve_as_superuser(self):
        rater_user = self.get_random_user(company_type="rater")
        superuser = self.super_user
        message = rater_user.received_messages.first()
        detail_url = reverse_lazy("api_v3:messages-detail", args=(message.id,))

        kwargs = dict(url=detail_url, user=superuser)
        data = self.retrieve(**kwargs)
        self.assertEqual(data["id"], message.id)

    def test_read_as_owner(self):
        message = Message.objects.filter(alert_read=False).order_by("?").first()
        read_url = reverse_lazy("api_v3:messages-read", args=(message.id,))

        self.client.force_authenticate(user=message.user)
        response = self.client.patch(read_url, format="json")
        data = response.data

        message.refresh_from_db()

        self.assertTrue(data["alert_read"])
        self.assertTrue(message.alert_read)

    def test_email_as_owner(self):
        Message.objects.update(date_sent=None)
        message = Message.objects.filter(date_sent__isnull=True).order_by("?").first()
        email_url = reverse_lazy("api_v3:messages-email", args=(message.id,))

        self.client.force_authenticate(user=message.user)
        response = self.client.patch(email_url, format="json")
        data = response.data

        message.refresh_from_db()

        self.assertIsNotNone(data["date_sent"])
        self.assertIsNotNone(message.date_sent)


class TestNestedMessageViewSet(MessagingTestMixin, ApiV3Tests):
    def test_list_as_owner(self):
        rater_user = self.get_nonadmin_user(company_type="rater")
        list_url = reverse_lazy("api_v3:user-messages-list", args=(rater_user.id,))

        kwargs = dict(url=list_url, user=rater_user)
        data = self.list(**kwargs)
        self.assertEqual(len(data), rater_user.received_messages.count())

    @override_settings(SERVER_TYPE="dev")
    @mock.patch("axis.messaging.api_v3.viewsets.message.NestedMessageViewSet._post_to_websocket")
    def test_mark_all_read_as_owner(self, _post_to_websocket):
        rater_user = self.get_nonadmin_user(company_type="rater")
        message_list_url = reverse_lazy("api_v3:user-messages-mark-all-read", args=(rater_user.id,))
        unread_messages_count = rater_user.received_messages.filter(alert_read=False).count()
        self.assertGreater(unread_messages_count, 0)
        self.client.force_authenticate(user=rater_user)
        self.client.post(message_list_url, format="json")

        self.assertEqual(_post_to_websocket.call_count, 1)
        unread_messages_count = rater_user.received_messages.filter(alert_read=False).count()
        self.assertEqual(unread_messages_count, 0)

    def test_categories(self):
        modern_message = modern_message_cls_factory(str("TestClassMessage"))
        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        with mock.patch.dict(
            "axis.messaging.utils.MESSAGE_CATEGORIES", message_categories, clear=True
        ):
            rater_user = self.get_nonadmin_user(company_type="rater")
            categories_url = reverse_lazy("api_v3:user-messages-categories", args=(rater_user.id,))
            self.client.force_authenticate(user=rater_user)
            response = self.client.get(categories_url, format="json")
            self.assertEqual(response.data[0]["value"], modern_message.category)
            self.assertEqual(response.data[0]["name"], modern_message.category.title())

    def test_read_action_as_owner(self):
        message_user = Message.objects.filter(alert_read=False).first().user
        message_ids = Message.objects.filter(alert_read=False, user=message_user).values_list(
            "id", flat=True
        )
        read_action_url = reverse_lazy("api_v3:user-messages-read-action", args=(message_user.id,))

        self.client.force_authenticate(user=message_user)
        self.client.patch(read_action_url, data={"ids": message_ids}, format="json")

        self.assertEqual(Message.objects.filter(alert_read=False, user=message_user).count(), 0)

        # read all messages
        Message.objects.filter(user=message_user).update(alert_read=False)
        self.client.patch("{}?all=true".format(read_action_url), data={"ids": []}, format="json")

        self.assertEqual(Message.objects.filter(alert_read=False, user=message_user).count(), 0)


class TestNestedMessagingPreferenceViewSet(MessagingTestMixin, ApiV3Tests):
    def test_list(self):
        message_name = str("TestClassMessage")
        modern_message = modern_message_cls_factory(
            message_name, receive_email=True, receive_notification=True
        )
        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        rater_user = self.get_nonadmin_user(company_type="rater")
        list_url = reverse_lazy("api_v3:user-messaging_preference-list", args=(rater_user.id,))
        self.client.force_authenticate(user=rater_user)

        # Assume that rater user choose his own preferences
        # they should override default
        MessagingPreference.objects.create(
            message_name=message_name,
            user=rater_user,
            receive_email=False,
            receive_notification=False,
        )

        with mock.patch.dict(
            "axis.messaging.api_v3.viewsets.message.MESSAGE_REGISTRY", message_registry, clear=True
        ):
            response = self.client.get(list_url, format="json")
            self.assertFalse(response.data[0]["required"])
            self.assertEqual(response.data[0]["message_name"], message_name)
            self.assertFalse(response.data[0]["receive_email"])
            self.assertFalse(response.data[0]["receive_notification"])

    def test_list_with_different_company_type(self):
        """
        Do not include preferences with different company_types
        """
        modern_message = modern_message_cls_factory(
            str("TestClassMessage"),
            company_types=[
                "provider",
            ],
        )
        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )
        rater_user = self.get_nonadmin_user(company_type="rater")
        list_url = reverse_lazy("api_v3:user-messaging_preference-list", args=(rater_user.id,))
        self.client.force_authenticate(user=rater_user)

        with mock.patch.dict(
            "axis.messaging.api_v3.viewsets.message.MESSAGE_REGISTRY", message_registry, clear=True
        ):
            response = self.client.get(list_url, format="json")
            self.assertListEqual(response.data, [])

    def test_list_with_different_company_slug(self):
        """
        Do not include preferences with different company_slugs
        """
        modern_message = modern_message_cls_factory(
            str("TestClassMessage"),
            company_slugs=[
                "someothercompany",
            ],
        )
        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )
        rater_user = self.get_nonadmin_user(company_type="rater")
        list_url = reverse_lazy("api_v3:user-messaging_preference-list", args=(rater_user.id,))
        self.client.force_authenticate(user=rater_user)

        with mock.patch.dict(
            "axis.messaging.api_v3.viewsets.message.MESSAGE_REGISTRY", message_registry, clear=True
        ):
            response = self.client.get(list_url, format="json")
            self.assertListEqual(response.data, [])

    def test_create(self):
        message_name = str("TestClassMessage")
        modern_message = modern_message_cls_factory(message_name)
        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )
        rater_user = self.get_nonadmin_user(company_type="rater")
        create_url = reverse_lazy("api_v3:user-messaging_preference-list", args=(rater_user.id,))
        self.client.force_authenticate(user=rater_user)
        with mock.patch.dict(
            "axis.messaging.api_v3.serializers.message.MESSAGE_REGISTRY",
            message_registry,
            clear=True,
        ):
            response = self.client.post(
                create_url,
                data={
                    "message_name": message_name,
                    "receive_email": False,
                    "receive_notification": False,
                },
                format="json",
            )
            self.assertFalse(response.data["receive_email"])
            self.assertFalse(response.data["receive_notification"])

    def test_create_required_preference(self):
        message_name = str("TestClassMessage")
        modern_message = modern_message_cls_factory(message_name, required=True)
        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )
        rater_user = self.get_nonadmin_user(company_type="rater")
        create_url = reverse_lazy("api_v3:user-messaging_preference-list", args=(rater_user.id,))
        self.client.force_authenticate(user=rater_user)
        with mock.patch.dict(
            "axis.messaging.api_v3.serializers.message.MESSAGE_REGISTRY",
            message_registry,
            clear=True,
        ):
            response = self.client.post(
                create_url,
                data={
                    "message_name": message_name,
                    "receive_email": False,
                    "receive_notification": False,
                },
                format="json",
            )
            self.assertEqual(
                response.data["message_name"]["message_name"],
                "Required message preference cannot be modified",
            )

    def test_reset(self):
        message_name = str("TestClassMessage")
        modern_message = modern_message_cls_factory(message_name)
        message_registry, message_categories = modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        rater_user = self.get_nonadmin_user(company_type="rater")
        reset_url = reverse_lazy("api_v3:user-messaging_preference-reset", args=(rater_user.id,))
        self.client.force_authenticate(user=rater_user)

        MessagingPreference.objects.create(
            message_name=message_name,
            user=rater_user,
            receive_email=False,
            receive_notification=False,
        )

        with mock.patch.dict(
            "axis.messaging.api_v3.viewsets.message.MESSAGE_REGISTRY", message_registry, clear=True
        ):
            # reset our preferences
            response = self.client.delete(reset_url, format="json")
            self.assertFalse(response.data[0]["receive_email"])
            self.assertTrue(response.data[0]["receive_notification"])
