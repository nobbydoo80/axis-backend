""" Messaging tests """

__author__ = "Autumn Valenta"
__date__ = "6/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


import logging
import os.path
import time
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail
from django.test import TestCase
from django.utils.timezone import now
from waffle.models import Switch

from axis.company.models import Company
from axis.core.tests.factories import rater_user_factory, basic_user_factory
from .factories import modern_message_registry_factory, message_factory, modern_message_cls_factory
from ..messages import MESSAGE_CATEGORIES
from ..models import Message, MessagingPreference
from ..utils import get_preferences_report, DEFAULT_COMPANY_MESSAGING_PREFERENCES

log = logging.getLogger(__name__)
User = get_user_model()


class MessageModelTestCase(TestCase):
    """Test `Message` and related `MessagingPreference` controls."""

    def make_message(self, **kwargs):
        """Shortcut for real `Message` creation."""

        u1, _ = User.objects.get_or_create(id=1, email="user1@gmail.com", username="user1")
        u2, _ = User.objects.get_or_create(id=2, email="user2@gmail.com", username="user2")

        data = dict(
            {
                "user": u1,
                "sender": u2,
                "title": "title",
                "content": "content",
                "email_content": None,
                "email_subject": None,
                "level": "debug",
                "category": "category",
                "url": "dummy",
                "sticky_alert": True,
                "date_alerted": now(),
                "date_sent": now(),
                "alert_read": True,
                "email_read": True,
            },
            **kwargs,
        )

        obj = Message(**data)
        obj.save()
        return obj

    def test_copy_is_unsaved_clone_without_state(self):
        """
        The object returned from copy() should be the same message, just free of any stateful
        delivery information.
        """
        obj = self.make_message()

        new_obj = obj.copy()
        self.assertEqual(new_obj.pk, None)
        self.assertEqual(new_obj.user, obj.user)
        self.assertEqual(new_obj.sender, obj.sender)
        self.assertEqual(new_obj.title, obj.title)
        self.assertEqual(new_obj.content, obj.content)
        self.assertEqual(new_obj.level, obj.level)
        self.assertEqual(new_obj.category, obj.category)
        self.assertEqual(new_obj.url, obj.url)
        self.assertEqual(new_obj.email_subject, obj.email_subject)
        self.assertEqual(new_obj.email_content, obj.email_content)
        self.assertEqual(new_obj.sticky_alert, obj.sticky_alert)
        self.assertEqual(new_obj.date_alerted, None)
        self.assertEqual(new_obj.date_sent, None)
        self.assertEqual(new_obj.alert_read, False)
        self.assertEqual(new_obj.email_read, None)

    def test_detect_content_duplicate(self):
        """Message.duplicates property returns a queryset of prior content-equal messages."""
        m1 = self.make_message(title="deliberate dup", content="content")
        m2 = self.make_message(title="deliberate dup", content="content")
        m3 = self.make_message(title="different", content="content")
        m4 = self.make_message(title="different", content="different")

        self.assertEqual(list(m1.duplicates), [m2])
        self.assertEqual(list(m2.duplicates), [m1])
        self.assertEqual(list(m3.duplicates), [])
        self.assertEqual(list(m4.duplicates), [])

        self.assertEqual(m1.is_duplicate(), True)
        self.assertEqual(m2.is_duplicate(), True)
        self.assertEqual(m3.is_duplicate(), False)
        self.assertEqual(m4.is_duplicate(), False)

    def test_render_with_context(self):
        """Message formatting syntax works."""

        obj = self.make_message(
            title="Title {a}",
            content="Content {b}",
        )
        obj.render(a="1", b="2")

        self.assertEqual(obj.title, "Title 1")
        self.assertEqual(obj.content, "Content 2")

    def test_send_from_delivery_preferences(self):
        """User's `MessagingPreference` controls `send_message()` behavior"""
        # Receive nothing
        obj = self.make_message(
            date_alerted=None, date_sent=None, alert_read=False, email_read=None
        )
        config = MessagingPreference(receive_notification=False, receive_email=False)
        ret = obj.send(config=config)
        self.assertEqual(ret, (False, False))
        self.assertEqual(obj.date_alerted, None)
        self.assertEqual(obj.date_sent, None)

        # Receive in-system alert only
        obj = self.make_message(
            date_alerted=None, date_sent=None, alert_read=False, email_read=None
        )
        config = MessagingPreference(receive_notification=True, receive_email=False)
        ret = obj.send(config=config)
        self.assertEqual(ret, (True, False))
        self.assertEqual(obj.date_alerted, None)  # Still None because no clients listening
        self.assertEqual(obj.date_sent, None)

        # Receive email alert only
        obj = self.make_message(
            date_alerted=None, date_sent=None, alert_read=False, email_read=None
        )
        config = MessagingPreference(receive_notification=False, receive_email=True)
        ret = obj.send(config=config)
        self.assertEqual(ret, (False, True))
        self.assertEqual(obj.date_alerted, None)
        self.assertNotEqual(obj.date_sent, None)

        # Receive both
        obj = self.make_message(
            date_alerted=None, date_sent=None, alert_read=False, email_read=None
        )
        config = MessagingPreference(receive_notification=True, receive_email=True)
        ret = obj.send(config=config)
        self.assertEqual(ret, (True, True))
        self.assertEqual(obj.date_alerted, None)  # Still None because no clients listening
        self.assertNotEqual(obj.date_sent, None)

    def test_send_skipped_if_already_delivered(self):
        """No delivery flags are set when message is already handled."""

        obj = self.make_message()
        ret = obj.send()

        self.assertEqual(ret, (False, False))

    def test_send_forced(self):
        """Test `force_resent=True` makes both delivery flags True."""

        obj = self.make_message()
        ret = obj.send(force_resend=True)

        self.assertEqual(ret, (True, True))

    def test_send_email_when_required(self):
        """
        Even if the user's preferences don't subscribe them to the email, required=True will force
        the in-system alert and the email delivery.
        """
        obj = self.make_message(
            date_alerted=None,
            date_sent=None,
            alert_read=False,
            email_read=None,
            title="Required message",
        )
        config = MessagingPreference(receive_notification=False, receive_email=False)
        ret = obj.send(required=True, config=config)
        self.assertEqual(ret, (True, True))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Required message")

    def test_send_email_for_user_with_customer_domain(self):
        """
        Message that sending for user that registered on customer website must
        use his site domain
        """
        hi_site = Site.objects.create(
            name="homeinnovation", domain="homeinnovation.pivotalenergy.net"
        )
        u3, _ = User.objects.get_or_create(
            id=3, email="user3@gmail.com", username="user3", site=hi_site
        )
        message = self.make_message(
            user=u3,
            sender=None,
            date_alerted=None,
            date_sent=None,
            alert_read=False,
            email_read=None,
            title="Required message",
        )
        ret = message.send(required=True)
        self.assertEqual(ret, (True, True))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Required message")
        self.assertIn(hi_site.domain, mail.outbox[0].body)

    def test_send_email_with_separate_content(self):
        """Test that if we use an email_context it gets used we assume that the email context is
        html and ONLY apply it to the attchment"""
        obj = self.make_message(
            date_alerted=None,
            date_sent=None,
            alert_read=False,
            email_read=None,
            content="XXX content XXX",
            email_content="XXX email_html_content XXX",
            title="Required message",
        )

        self.assertEqual(obj.content, "XXX content XXX")
        self.assertEqual(obj.email_content, "XXX email_html_content XXX")

        config = MessagingPreference(receive_notification=False, receive_email=False)
        ret = obj.send(required=True, config=config)
        self.assertEqual(ret, (True, True))
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(mail.outbox[0].subject, "Required message")
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn("XXX email_html_content XXX", mail.outbox[0].alternatives[0][0])
        self.assertIn("XXX content XXX", mail.outbox[0].body)

    def test_send_email_with_separate_subject(self):
        """Test that if we use an email subject it will be respected"""
        obj = self.make_message(
            date_alerted=None,
            date_sent=None,
            alert_read=False,
            email_read=None,
            content="XXX content XXX",
            email_content="XXX email_html_content XXX",
            email_subject="XXX email Subject",
            title="Required message",
        )

        self.assertEqual(obj.content, "XXX content XXX")
        self.assertEqual(obj.email_content, "XXX email_html_content XXX")
        self.assertEqual(obj.email_subject, "XXX email Subject")

        config = MessagingPreference(receive_notification=False, receive_email=True)
        ret = obj.send(config=config)
        self.assertEqual(ret, (False, True))
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual("XXX email Subject", mail.outbox[0].subject)
        self.assertIn("XXX content XXX", mail.outbox[0].body)

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        self.assertIn("XXX email_html_content XXX", mail.outbox[0].alternatives[0][0])

    def test_create_message_with_email_content(self):
        """This will test out a template for email content"""

        message_name = str("TestClassMessage")
        kw = {
            "category": "category",
            "title": "Personal report for {user}",
            "subject": "Subject {user}",
            "content": "{user} report contents stuff.",
            "email_content": os.path.abspath(os.path.join(os.path.dirname(__file__), "msg.html")),
            "email_subject": "My fancy report for {{ user.first_name }}",
        }
        modern_message = modern_message_cls_factory(message_name, **kw)
        modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        company, _ = Company.objects.get_or_create(name="Company", slug="company")
        user = basic_user_factory(
            username="BOB",
            first_name="Bob",
            last_name="Johnson",
            company=company,
            email="user1@gmail.com",
        )

        # Make sure we get this email..
        MessagingPreference.objects.create(
            message_name=message_name,
            user=user,
            category=modern_message.category,
            receive_email=True,
            receive_notification=True,
        )

        context = {"user": user, "elements": ["foo", "bar"]}

        modern_message().send(context=context, url="/foo/bar/test.html", user=user)

        self.assertEqual("My fancy report for Bob", mail.outbox[0].subject)

        self.assertIn("Bob Johnson report contents stuff", mail.outbox[0].body)  # Text stuff

        # Now lets verify our pretty report.
        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        self.assertEqual(mail.outbox[0].alternatives[0][1], "text/html")
        # print(mail.outbox[0].alternatives[0][0])
        self.assertIn("DJANGO_EMAIL_CONTENT", mail.outbox[0].alternatives[0][0])
        self.assertNotIn("THIS IS THE CONTENT ONLY", mail.outbox[0].alternatives[0][0])
        self.assertIn("<li>foo</li>", mail.outbox[0].alternatives[0][0])
        self.assertIn("<li>bar</li>", mail.outbox[0].alternatives[0][0])

    def test_create_message_with_email_subject_fallback(self):
        """This will test out a test that if an email_subject is not used we get the fallback"""

        message_name = str("TestClassMessage")
        kw = {
            "category": "category",
            "title": "Personal report for {user}",
            "subject": "Subject {user}",
            "content": "{user} report contents stuff.",
            "email_content": os.path.abspath(os.path.join(os.path.dirname(__file__), "msg.html")),
        }
        modern_message = modern_message_cls_factory(message_name, **kw)
        modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        company, _ = Company.objects.get_or_create(name="Company", slug="company")
        user = basic_user_factory(
            username="BOB",
            first_name="Bob",
            last_name="Johnson",
            company=company,
            email="user1@gmail.com",
        )

        # Make sure we get this email
        MessagingPreference.objects.create(
            message_name=message_name,
            user=user,
            category=modern_message.category,
            receive_email=True,
            receive_notification=True,
        )

        context = {"user": user, "elements": ["foo", "bar"]}

        modern_message().send(context=context, url="/foo/bar/test.html", user=user)

        self.assertEqual("Personal report for Bob Johnson", mail.outbox[0].subject)

    def test_admins_only(self):
        """ "This will test out admins_only functionality"""

        message_name = "TestClassMessage"
        kw = {
            "category": "category",
            "title": "Personal report for {user}",
            "subject": "Subject {user}",
            "content": "{user} report contents stuff. {var}",
            "company_admins_only": True,
        }
        modern_message = modern_message_cls_factory(message_name, **kw)
        modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        company, _ = Company.objects.get_or_create(name="Company", slug="company")
        user = basic_user_factory(
            username="BOB",
            first_name="Bob",
            last_name="Johnson",
            company=company,
            email="user1@gmail.com",
        )

        # Make sure we get this email
        MessagingPreference.objects.create(
            message_name=message_name,
            user=user,
            category=modern_message.category,
            receive_email=True,
            receive_notification=True,
        )

        modern_message().send(context={"user": user, "var": "a"}, user=user)
        self.assertEqual(len(mail.outbox), 0)

        modern_message().send(context={"user": user, "var": "b"}, company=company)
        self.assertEqual(len(mail.outbox), 0)

        modern_message().send(context={"user": user, "var": "c"}, users=User.objects.all())
        self.assertEqual(len(mail.outbox), 0)

        user.is_company_admin = True
        user.save()

        modern_message().send(context={"user": user, "var": "d"}, user=user)
        self.assertEqual(len(mail.outbox), 1)

        modern_message().send(context={"user": user, "var": "e"}, company=company)
        self.assertEqual(len(mail.outbox), 2)

        modern_message().send(context={"user": user, "var": "f"}, users=User.objects.all())
        self.assertEqual(len(mail.outbox), 3)

    def test_queryset_since_shortcut(self):
        """Window for `since()` start/stop thresholds work."""

        today = now()
        m1 = self.make_message()
        m1.date_created = today - timedelta(days=7)
        m1.save()
        m2 = self.make_message()
        m2.date_created = today
        m2.save()

        # Start date before latest message, no cutoff date
        qs = Message.objects.since(today - timedelta(days=1))
        self.assertEqual(list(qs), [m2])

        # Window between the two messages
        qs = Message.objects.since(today - timedelta(days=2), today - timedelta(days=1))
        self.assertEqual(list(qs), [])

        # Start date before earliest message, cutoff before latest
        qs = Message.objects.since(today - timedelta(days=8), today - timedelta(days=1))
        self.assertEqual(list(qs), [m1])

        # Start date before earliest message, cutoff after latest
        qs = Message.objects.since(today - timedelta(days=8), today + timedelta(days=1))
        self.assertEqual(list(qs), [m2, m1])  # Coming out in reverse order

        # Start date before earliest message, no cutoff date
        qs = Message.objects.since(today - timedelta(days=8))
        self.assertEqual(list(qs), [m2, m1])  # Coming out in reverse order

    def test_queryset_debounce_detection(self):
        """
        Building on the concept of duplicate detection, debounce detection is called on a queryset
        of duplicate messages to decide if it has been long enough since the last dup delivery to
        go ahead and notify the user again.
        """

        m1 = self.make_message(title="deliberate dup", content="content")
        m1.date_created = now() - (settings.MESSAGING_DUPLICATE_DEBOUNCE - timedelta(seconds=3))
        m1.save()
        m2 = self.make_message(title="deliberate dup", content="content")

        # Verify assumptions
        self.assertEqual(list(m1.duplicates), [m2])
        self.assertEqual(list(m2.duplicates), [m1])
        self.assertEqual(m1.is_duplicate(), True)
        self.assertEqual(m2.is_duplicate(), True)

        # Real tests
        self.assertEqual(m2.duplicates.is_debouncing(), True)

        wait_seconds = settings.MESSAGING_DUPLICATE_DEBOUNCE.total_seconds()
        log.info("Waiting %d seconds for debounce period to end...", wait_seconds)
        time.sleep(wait_seconds)
        self.assertEqual(m2.duplicates.is_debouncing(), False)

        # Generate a third message that falls outside of the debounce window by default
        m3 = self.make_message(title="deliberate dup", content="content")
        self.assertEqual(list(m3.duplicates), [m2, m1])
        self.assertEqual(m3.is_duplicate(), True)

        self.assertEqual(m3.duplicates.is_debouncing(), False)

    def test_send_message_to_company(self):
        """A Message sent to a company is copied to all active users of that company."""
        company, _ = Company.objects.get_or_create(name="Company", slug="company")
        basic_user_factory(username="user1", company=company)
        basic_user_factory(username="user2", company=company)
        basic_user_factory(username="user3", company=company, is_active=False)
        basic_user_factory(username="user3", company=company, is_active=True, is_approved=False)

        self.assertEqual(Message.objects.count(), 0)
        modern_message = modern_message_cls_factory("ModernMessageTest")
        modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        modern_message().send(company=company)

        self.assertNotEqual(Message.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 2)


class UtilsTestCase(TestCase):
    """Messaging utils tests."""

    no_alert_by_default = [
        "IsAppealsHIRLProjectCreatedNotificationMessage",
    ]
    has_email_by_default = [
        "TensorActivationMessage",
        "TensorAnonymousActivationMessage",
        "TensorAnonymousActivationWithoutCompanyMessage",
        "TensorUserApprovalMessage",
        "TensorCompanyApprovalMessage",
        "TensorCompanyAdminUserApprovalMessage",
        "NeeaMonthlyHomeUtilityStatusBPAExportAvailableMessage",
        "ExpiredInsuranceOwnerAgreementMessage",
        "LegalAgreementReadyForSigningMessage",
        "RequestForCertificateOfInsuranceMessage",
        "ExpiredOwnerAgreementMessage",
        "EnrollmentCompleteMessage",
        "ExpiredBuilderAgreementMessage",
        "ExpiredInsuranceBuilderAgreementMessage",
        "NewBuilderEnrollmentMessage",
        "LegalAgreementSignedMessage",
        "LegalAgreementReadyForCountersigningMessage",
        "COIAvailableMessage",
        "NewBuilderAgreementDocumentMessage",
        "AgreementExpirationWarningMessage",
        "InsuranceExpirationWarningMessage",
        "VerifierAgreementRequestForCertificateOfInsuranceMessage",
        "VerifierLegalAgreementReadyForSigningMessage",
        "OfficerLegalAgreementReadyForSigningMessage",
        "VerifierEnrollmentCompleteMessage",
        "ExpiredVerifierAgreementMessage",
        "NewVerifierAgreementEnrollmentMessage",
        "VerifierLegalAgreementReadyForCountersigningMessage",
        "COIAvailableMessage",
        "COIChangedMessage",
        "NewVerifierAgreementDocumentMessage",
        "VerifierAgreementChangedByVerifierMessage",
        "VerifierAgreementExpirationWarningMessage",
        "ExpiredOwnerVerifierAgreementMessage",
        "HIRLProjectRegistrationStateChangedMessage",
        "HIRLProjectRegistrationRejectedMessage",
        "QACorrectionRequiredDailyEmail",
        "QAFailingHomesDailyEmail",
        "SingleFamilyProjectCreatedHIRLNotificationMessage",
        "MultiFamilyProjectCreatedHIRLNotificationMessage",
        "HIRLProjectBuilderIsNotWaterSensePartnerMessage",
        "InvoiceCreatedNotificationMessage",
        "HIRLInvoicePaidMessage",
        "HIRLInvoiceCancelledMessage",
        "HIRLResponsibleEntityForPaymentInvoiceItemGroupCreatedMessage",
        "HIRLInvoiceItemGroupUpdatedMessage",
        "QACorrectionRequiredDailyEmail",
        "CertificationsDailyEmail",
        "PendingCertificationsDailyEmail",
        "BPACertificationsDailyEmail",
        "PivotalAdminDailyEmail",
        "AxisOutsideContactMessage",
        "QADesigneeAssigneeMessage",
        "CustomerHIRLQaCorrectionReceivedMessage",
        "CustomerHIRLQaCorrectionReceivedMessage",
        "CustomerHIRLQADesigneeAssigneeMessage",
        "GreenPaymentsImportAdminNotificationMessage",
        "HIRLProjectBillingStateChangedManuallyMessage",
        "TensorAuthenticatedUserApproveMessage",
        "TensorAnonymousActivationWithoutCompanyMessage",
        "TensorUserApprovalMessage",
        "TensorAuthenticatedUserApproveMessage",
        "TensorCompanyApprovalMessage",
        "InspectionGradeCustomerHIRLQuarterReportMessage",
        "TaskCreatedMessage",
        "TaskApprovedMessage",
        "TaskRejectedMessage",
        "TaskChangedStatusMessage",
    ]

    def test_user_has_default_preferences(self):
        """Unset preferences have default values."""
        u, _ = User.objects.get_or_create(id=1, username="user1")
        u.company, _ = Company.objects.get_or_create(name="Company", slug="slug")
        self.assertNotEqual(len(MESSAGE_CATEGORIES), 0)
        self.assertEqual(u.messagingpreference_set.count(), 0)

        report = get_preferences_report(u)
        self.assertEqual(len(report.keys()), len(MESSAGE_CATEGORIES))

        for category_configs in report.values():
            for message, config in category_configs.items():
                message_name = message.__name__

                # Global defaults.  Some companies have their own defaults, but this is generic.
                if message_name in self.no_alert_by_default:
                    self.assertEqual(config["receive_notification"], False, message_name)
                else:
                    self.assertEqual(config["receive_notification"], True, message_name)

                if message_name in self.has_email_by_default:
                    self.assertEqual(config["receive_email"], True, message_name)
                else:
                    self.assertEqual(config["receive_email"], False, message_name)

    def test_user_has_non_default_custom_preferences(self):
        """Unset preferences have default values declared by the company slug."""
        u, _ = User.objects.get_or_create(id=1, username="user1")
        u.company, _ = Company.objects.get_or_create(name="Company", slug="slug")
        self.assertNotEqual(len(MESSAGE_CATEGORIES), 0)
        self.assertEqual(u.messagingpreference_set.count(), 0)

        # Arrange a non-standard default setting for this company slug
        DEFAULT_COMPANY_MESSAGING_PREFERENCES["slug"] = {
            None: {
                "receive_notification": False,
                "receive_email": True,
            }
        }

        report = get_preferences_report(u)
        self.assertEqual(len(report.keys()), len(MESSAGE_CATEGORIES))

        for category_configs in report.values():
            for config in category_configs.values():
                if not config["required"]:
                    # Test against our custom settings
                    self.assertEqual(config["receive_notification"], False)
                    self.assertEqual(config["receive_email"], True)

    def test_user_has_non_default_custom_preferences_for_specific_message(self):
        """A specific message can have non-standard default settings for a specific company."""
        u, _ = User.objects.get_or_create(id=1, username="user1")
        u.company, _ = Company.objects.get_or_create(name="Company", slug="slug")
        self.assertNotEqual(len(MESSAGE_CATEGORIES), 0)
        self.assertEqual(u.messagingpreference_set.count(), 0)

        # Arrange a non-standard default setting for this company slug
        DEFAULT_COMPANY_MESSAGING_PREFERENCES["slug"] = {
            "CompanyProfileUpdateMessage": {
                "receive_notification": False,
                "receive_email": True,
            },
        }

        report = get_preferences_report(u)
        self.assertEqual(len(report.keys()), len(MESSAGE_CATEGORIES))

        for category_configs in report.values():
            for message_cls, config in category_configs.items():
                # Check global default unless it's for the message preference we're singling out
                if message_cls.__name__ == "CompanyProfileUpdateMessage":
                    self.assertEqual(config["receive_notification"], False)
                    self.assertEqual(config["receive_email"], True)

    def test_send_email_with_disable_email_waffle_switch(self):
        Switch.objects.create(name="Disable Email Sending", active=True)

        rater_common_user = rater_user_factory()

        message_name = str("TestClassMessage")
        kw = {
            "category": "category",
            "title": "Personal report for {user}",
            "subject": "Subject {user}",
            "content": "{user} report contents stuff.",
            "email_content": os.path.abspath(os.path.join(os.path.dirname(__file__), "msg.html")),
        }
        modern_message = modern_message_cls_factory(message_name, **kw)
        modern_message_registry_factory(
            modern_messages=[
                modern_message,
            ]
        )

        MessagingPreference.objects.create(
            message_name=message_name,
            user=rater_common_user,
            category=modern_message.category,
            receive_email=True,
            receive_notification=True,
        )
        message_factory(
            user=rater_common_user, level="info", alert_read=False, modern_message=message_name
        )

        self.assertEqual(len(mail.outbox), 0)
        modern_message().send(
            user=rater_common_user,
        )
        self.assertEqual(len(mail.outbox), 0)
