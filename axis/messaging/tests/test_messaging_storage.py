"""test_messaging_store.py: """

__author__ = "Artem Hruzd"
__date__ = "10/24/2019 11:51"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.views import View

from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.messaging.models import Message
from axis.messaging.storage import MessagingStorage


class MessagingStorageTests(CompaniesAndUsersTestMixin, AxisTestCase):
    include_company_types = ["utility", "general"]
    include_unrelated_companies = False
    client_class = AxisClient

    class DummyView(View):
        def get(self, request, *args, **kwargs):
            messages.add_message(request, messages.INFO, "Info Message - This is interesting!")
            messages.debug(request, "Debug Message - Nothing special move along")
            messages.success(request, "Warning Message - Uggh oh!")
            messages.warning(request, "Error Message - Oh no!")
            messages.error(request, "Critical Message - Very Bad. Not good.")

            return "ok"

    def test_do_admin_request_and_get_messages_in_admin_view(self):
        """
        When we're sending message from /admin/ we are getting
        only django session messages list in admin
        """
        view = self.DummyView()
        request = RequestFactory().get("/admin/fake-path")

        # adding session
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

        # adding messages
        messaging_storage = MessagingStorage(request)
        setattr(request, "_messages", messaging_storage)

        # set user
        request.user = self.admin_user

        view.get(request)

        # assuming we get messages from /admin/
        storage = get_messages(request)
        self.assertEqual(len(storage), 5)
        self.assertEqual(Message.objects.all().count(), 0)

    def test_do_admin_request_and_get_messages_in_common_view(self):
        """
        When we're sending message from /admin/ we should not receive them in common axis view
        """
        view = self.DummyView()
        request = RequestFactory().get("/admin/fake-path")

        # adding session
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

        # adding messages
        messaging_storage = MessagingStorage(request)
        setattr(request, "_messages", messaging_storage)

        # set user
        request.user = self.admin_user

        view.get(request)

        # assuming we get messages from common view
        # in case we will receive 10 messages here from both  session and Message list
        request.path = "/fake-path"
        storage = get_messages(request)
        self.assertEqual(len(storage), 5)
        self.assertEqual(Message.objects.all().count(), 0)

    def test_do_common_request_and_get_messages_in_common_view(self):
        view = self.DummyView()
        request = RequestFactory().get("/fake-path")

        # adding session
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

        # adding messages
        messaging_storage = MessagingStorage(request)
        setattr(request, "_messages", messaging_storage)

        # set user
        request.user = self.admin_user

        view.get(request)

        storage = get_messages(request)
        self.assertEqual(len(storage), 5)
        self.assertEqual(Message.objects.all().count(), 5)

    def test_do_common_request_and_get_messages_in_admin_view(self):
        view = self.DummyView()
        request = RequestFactory().get("/fake-path")

        # adding session
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

        # adding messages
        messaging_storage = MessagingStorage(request)
        setattr(request, "_messages", messaging_storage)

        # set user
        request.user = self.admin_user

        view.get(request)

        request.path = "/admin/fake-path"
        storage = get_messages(request)
        self.assertEqual(len(storage), 0)
        self.assertEqual(Message.objects.all().count(), 5)
