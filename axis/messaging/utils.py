""" Messaging system views """

__author__ = "Autumn Valenta"
__date__ = "3/3/15 1:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import copy
import inspect
import json
import logging
import re
import socket
from collections import OrderedDict
from importlib import import_module
from typing import Optional, List

import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import camel_case_to_spaces as cc2s
from django.utils.timezone import now
from rest_framework.renderers import JSONRenderer

from axis.core.utils import get_previous_day_start_end_times
from .messages import MESSAGE_CATEGORIES, MESSAGE_REGISTRY
from .tokens import unsubscribe_email_token

log = logging.getLogger(__name__)
User = get_user_model()

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

DEFAULT_MESSAGE_TITLES = {
    "debug": "Debug",
    "info": "Info",
    "success": "Success",
    "warning": "Warning",
    "error": "Error",
    "system": "System Message",
}
_ALERTS_AND_EMAILS = {
    "receive_notification": True,
    "receive_email": True,
}

_EMAIL_ONLY = {
    "receive_notification": False,
    "receive_email": True,
}

_DISABLED = {
    "receive_notification": False,
    "receive_email": False,
}

DEFAULT_COMPANY_MESSAGING_PREFERENCES = {
    # Company slugs mapping to a dict of message settings.
    # The ``None`` entry defines the default for all companies missing from the dict.
    # Values are dicts of ModernMessage names (again, ``None`` for default) that wish to customize
    # their delivery preferences on a per-message basis.
    # Note that if a ModernMessage class definition has ``required = True`` on it, it is immune to
    # modification via this dict.
    None: {  # fallback company
        None: {  # fallback default message preference
            "receive_notification": True,
            "receive_email": False,
        },
        "TensorAnonymousActivationMessage": _ALERTS_AND_EMAILS,
        "TensorAnonymousActivationWithoutCompanyMessage": _ALERTS_AND_EMAILS,
        "TensorCompanyApprovalMessage": _EMAIL_ONLY,
        "TensorActivationMessage": _EMAIL_ONLY,
        "TensorUserApprovalMessage": _ALERTS_AND_EMAILS,
        "AxisOutsideContactMessage": _ALERTS_AND_EMAILS,
        "PivotalAdminDailyEmail": _ALERTS_AND_EMAILS,
        "NeeaMonthlyHomeUtilityStatusBPAExportAvailableMessage": _ALERTS_AND_EMAILS,
        "PendingCertificationsDailyEmail": _ALERTS_AND_EMAILS,
        "CertificationsDailyEmail": _ALERTS_AND_EMAILS,
        "BPACertificationsDailyEmail": _ALERTS_AND_EMAILS,
        # QA
        "QADesigneeAssigneeMessage": _ALERTS_AND_EMAILS,
        "CustomerHIRLQaCorrectionReceivedMessage": _ALERTS_AND_EMAILS,
        "CustomerHIRLQADesigneeAssigneeMessage": _ALERTS_AND_EMAILS,
        # Customer HIRL Builder Agreement
        "RequestForCertificateOfInsuranceMessage": _ALERTS_AND_EMAILS,
        "ExpiredInsuranceOwnerAgreementMessage": _ALERTS_AND_EMAILS,
        "ExpiredOwnerAgreementMessage": _ALERTS_AND_EMAILS,
        "LegalAgreementReadyForSigningMessage": _ALERTS_AND_EMAILS,
        "EnrollmentCompleteMessage": _ALERTS_AND_EMAILS,
        "ExpiredBuilderAgreementMessage": _ALERTS_AND_EMAILS,
        "ExpiredInsuranceBuilderAgreementMessage": _ALERTS_AND_EMAILS,
        "NewBuilderEnrollmentMessage": _ALERTS_AND_EMAILS,
        "LegalAgreementSignedMessage": _ALERTS_AND_EMAILS,
        "LegalAgreementReadyForCountersigningMessage": _ALERTS_AND_EMAILS,
        "COIAvailableMessage": _ALERTS_AND_EMAILS,
        "NewBuilderAgreementDocumentMessage": _ALERTS_AND_EMAILS,
        "AgreementExpirationWarningMessage": _ALERTS_AND_EMAILS,
        "InsuranceExpirationWarningMessage": _ALERTS_AND_EMAILS,
        # Customer HIRL Verifier Agreement
        "VerifierAgreementRequestForCertificateOfInsuranceMessage": _ALERTS_AND_EMAILS,
        "VerifierLegalAgreementReadyForSigningMessage": _ALERTS_AND_EMAILS,
        "OfficerLegalAgreementReadyForSigningMessage": _ALERTS_AND_EMAILS,
        "VerifierEnrollmentCompleteMessage": _ALERTS_AND_EMAILS,
        "ExpiredVerifierAgreementMessage": _ALERTS_AND_EMAILS,
        "NewVerifierAgreementEnrollmentMessage": _ALERTS_AND_EMAILS,
        "VerifierLegalAgreementReadyForCountersigningMessage": _ALERTS_AND_EMAILS,
        "COIChangedMessage": _ALERTS_AND_EMAILS,
        "NewVerifierAgreementDocumentMessage": _ALERTS_AND_EMAILS,
        "VerifierAgreementChangedByVerifierMessage": _ALERTS_AND_EMAILS,
        "VerifierAgreementExpirationWarningMessage": _ALERTS_AND_EMAILS,
        "ExpiredOwnerVerifierAgreementMessage": _ALERTS_AND_EMAILS,
        # Customer HIRL Project registration
        "SingleFamilyProjectCreatedHIRLNotificationMessage": _ALERTS_AND_EMAILS,
        "MultiFamilyProjectCreatedHIRLNotificationMessage": _ALERTS_AND_EMAILS,
        "HIRLProjectRegistrationStateChangedMessage": _ALERTS_AND_EMAILS,
        "HIRLProjectRegistrationRejectedMessage": _ALERTS_AND_EMAILS,
        "GreenPaymentsImportAdminNotificationMessage": _ALERTS_AND_EMAILS,
        "HIRLProjectBuilderIsNotWaterSensePartnerMessage": _ALERTS_AND_EMAILS,
        "IsAppealsHIRLProjectCreatedNotificationMessage": _DISABLED,
        # Invoicing
        "InvoiceCreatedNotificationMessage": _ALERTS_AND_EMAILS,
        "HIRLInvoicePaidMessage": _ALERTS_AND_EMAILS,
        "HIRLInvoiceCancelledMessage": _ALERTS_AND_EMAILS,
        "HIRLResponsibleEntityForPaymentInvoiceItemGroupCreatedMessage": _ALERTS_AND_EMAILS,
        "HIRLInvoiceItemGroupUpdatedMessage": _ALERTS_AND_EMAILS,
        "HIRLProjectBillingStateChangedManuallyMessage": _ALERTS_AND_EMAILS,
        "QACorrectionRequiredDailyEmail": _ALERTS_AND_EMAILS,
        "QAFailingHomesDailyEmail": _ALERTS_AND_EMAILS,
        # User management
        "InspectionGradeCustomerHIRLQuarterReportMessage": _ALERTS_AND_EMAILS,
        # Scheduling
        "TaskCreatedMessage": _ALERTS_AND_EMAILS,
        "TaskApprovedMessage": _ALERTS_AND_EMAILS,
        "TaskRejectedMessage": _ALERTS_AND_EMAILS,
        "TaskChangedStatusMessage": _ALERTS_AND_EMAILS,
    },
    # Companies defaulting to email mirroring of all notifications.
    # This list is essentially APS + all Rater and Provider companies in AZ.
    "aps": {None: _ALERTS_AND_EMAILS},
    "provider-best-energy-rating-consulting": {None: _ALERTS_AND_EMAILS},
    "dr-wastchak": {None: _ALERTS_AND_EMAILS},
    "e3-energy-llc": {None: _ALERTS_AND_EMAILS},
    "energy-inspectors": {None: _ALERTS_AND_EMAILS},
    "provider-protex": {None: _ALERTS_AND_EMAILS},
    "rater-evo-energy-solutions": {None: _ALERTS_AND_EMAILS},
}

UNMANAGED_MESSAGE_PREFERENCE = {
    # Sane defaults for messages that have no delivery preferences. This is not customizable.
    "receive_notification": True,
    "receive_email": False,
}


def _message_class(message=None, message_name=None):
    """Resolves a message class/instance or a message name into the right class reference."""
    from .messages import MESSAGE_REGISTRY

    if not any([message, message_name]):
        raise ValueError("One of the following kwargs is required: message, message_name")

    if message:
        if inspect.isclass(message):
            return message
        return message.__class__

    return MESSAGE_REGISTRY[message_name]


def _message_name(message=None, message_name=None):
    """
    Resolves a message class/instance and fetches its name.  If a message name is provided directly,
    the corresponding message will be looked up and potentially raise a KeyError if the name is
    not valid (evidenced by the message not being registered, either because of never being imported
    or because of a typo, etc).
    """
    message = _message_class(message=message, message_name=message_name)
    return message.__name__


# Reusable utilities
def get_default_system_fallback_preference():
    return DEFAULT_COMPANY_MESSAGING_PREFERENCES[None][None].copy()


def get_default_company_fallback_preference(user):
    """
    Returns the default company preference for messages to user's company.  If no None-entry is
    provided in the company preferences, the None-None entry is returned from the Axis platform
    defaults.
    """
    defaults = get_default_company_preferences(user)  # already deep-copied
    system_default = get_default_system_fallback_preference()  # already shallow-copied
    return defaults.get(None, system_default)


def get_default_company_preferences(user):
    """
    Returns the entry from the master preferences dict for the user's company.  If no entry exists,
    return the None-entry, representing the whole set of Axis platform defaults.
    """
    axis_defaults = DEFAULT_COMPANY_MESSAGING_PREFERENCES[None]
    try:
        if user.company:
            company_defaults = DEFAULT_COMPANY_MESSAGING_PREFERENCES.get(
                user.company.slug, axis_defaults
            )
        else:
            company_defaults = axis_defaults
    except AttributeError:
        company_defaults = axis_defaults
    return copy.deepcopy(company_defaults)


def get_default_company_preference(user, message=None, message_name=None):
    """
    Returns the effective default preference for the given company and message.  If no message or
    message_name are given, the best-known fallback preference for the company is returned.
    """
    company_fallback_default = get_default_company_fallback_preference(user)

    if not any([message, message_name]):  # non-standard message with no ModernMessage obj
        return UNMANAGED_MESSAGE_PREFERENCE.copy()

    message_name = _message_name(message=message, message_name=message_name)
    company_defaults = get_default_company_preferences(user)

    return company_defaults.get(message_name, company_fallback_default)


def get_user_message_preference(user, message=None, message_name=None):
    """
    Returns a MessagingPreference instance representing the user's explicit preference for the given
    message.  If no such preference exists, return an unsaved MessagingPreference object holding the
    best-known default delivery settings.

    Unlike the other similar preference-retrieval utilities which rely on a concrete ModernMessage,
    supplying no message or message_name will still result in an unsaved MessagingPreference
    instance with delivery settings matching the best-known defaults.
    """
    from .models import MessagingPreference

    # If there is message info provided, resolve it, but otherwise we will keep a None message to
    # represent a request for a non-standard message where preferences can't be tracked.  In that
    # scenario, we still want it to obey whatever the default company preference says the delivery
    # settings should be.

    user = None if isinstance(user, AnonymousUser) else user

    if any([message, message_name]):
        message = _message_class(message=message, message_name=message_name)
        message_name = message.__name__
        user_preference = MessagingPreference.objects.filter(
            **{
                "user": user,
                "message_name": message_name,
            }
        ).first()
    else:
        user_preference = None

        # These are invalid for object creation, but it shouldn't be saved anyway
        category = None
        message_name = None

    if user_preference is None:  # Impossible to look up, or simply unset by the user
        default_company_preference = get_default_company_preference(user, message=message)
        preference_attrs = dict(
            default_company_preference,
            **{
                "user": user,
                "message_name": message_name,
            },
        )

        # NOTE: This is deliberately not saved!  It represents only a lazyily evaluated default from
        # the company's default preferences, which may change in the future.  Users who have not
        # explicitly overriden a given message setting should always have their defaults track with
        # the company defaults.  Saving this instance is an action indistinguishable from the user
        # having manually overriden their company default (even if the preference looks the same).
        user_preference = MessagingPreference(**preference_attrs)

    return user_preference


def get_preferences_report(user, trimmed=False, json_safe=False):
    """
    Returns dict mapping category name to a sub-dict of Message classes to user settings.

    The ``trimmed`` setting inspects attributes on the message classes to guess at whether the user
    should see each particular message on a sheet of settings available to them.

    ``json_safe`` will make references to class objects into simple string names instead.
    """
    from axis.company.models import Company
    from axis.company.strings import COMPANY_TYPES

    # Case-insensitive category ordering for when ``trimmed`` is True.
    # We're converting this list to a dict of {category: order} items.
    # Categories not represented here will appear at the end in alphebetical order.
    category_order_lookup = dict(
        map(
            reversed,
            enumerate(
                (
                    # Headlining stuff that shouldn't have to be searched for
                    "system",
                    "associations",
                    # Company-specific stuff
                    "neea",
                    "eto",
                    "aps",
                    # Workflow stuff
                    "home",
                    "annotation",
                    "qa",
                    "incentive payments",
                    # Extras, probably not often used
                    "profile",
                    "company",
                )
            ),
        )
    )

    all_company_types = list(dict(COMPANY_TYPES).keys())

    values = user.messagingpreference_set.values_list(
        "id", "category", "message_name", "receive_notification", "receive_email"
    )
    preferences = {}
    for id, category, name, receive_notification, receive_email in values:
        preferences.setdefault(category, {})
        preferences[category][name] = {
            "id": id,
            "receive_notification": receive_notification,
            "receive_email": receive_email,
        }
    configs = OrderedDict()
    for category, cls_list in MESSAGE_CATEGORIES.items():
        configs.setdefault(category, OrderedDict())
        for cls in sorted(cls_list, key=lambda cls: cls.verbose_name or cc2s(cls.__name__)):
            k = cls
            if json_safe:
                k = cls.__name__

            default_preference = get_default_company_preference(user, message=cls)
            default_preference["id"] = None
            configs[category][k] = preferences.get(category or "", {}).get(
                cls.__name__, default_preference
            )
            configs[category][k].update(
                {
                    # Display info
                    "required": cls.required,
                    "verbose_name": cls.verbose_name,
                    "description": cls.description,
                    "sticky_alert": cls.sticky_alert,
                    "unique": cls.unique,
                    "level": cls.level,
                    # Visibility conditions, respected later if requested
                    "company_admins_only": cls.company_admins_only,
                    "company_types": cls.company_types or all_company_types,
                    "company_slugs": cls.company_slugs,
                    "companies_with_relationship": cls.companies_with_relationship,
                    "companies_with_relationship_or_self": cls.companies_with_relationship_or_self,
                }
            )
            if cls.required:
                configs[category][k].update(
                    {
                        "receive_notification": True,
                        "receive_email": True,
                    }
                )

    if trimmed and not user.is_superuser:
        company = user.company
        for category, data in list(configs.items()):
            for k, preference in list(data.items()):
                if preference.get("company_admins_only") and not user.is_company_admin:
                    del data[k]
                    continue
                if company.company_type not in preference["company_types"]:
                    del data[k]
                    continue
                if preference["company_slugs"] and company.slug not in preference["company_slugs"]:
                    del data[k]
                    continue
                relationship_slugs = (
                    preference["companies_with_relationship"]
                    or preference["companies_with_relationship_or_self"]
                )
                if relationship_slugs:
                    if (
                        preference["companies_with_relationship_or_self"]
                        and company.slug in relationship_slugs
                    ):
                        continue  # Keep the item, ignore relationship logic

                    # Discover a qualifying relationship
                    company_ct = ContentType.objects.get_for_model(Company)
                    relation_ids = list(
                        Company.objects.filter(slug__in=relationship_slugs).values_list(
                            "id", flat=True
                        )
                    )
                    relations = company.relationships.filter(
                        content_type=company_ct, object_id__in=relation_ids
                    )
                    if not relations.exists():
                        del data[k]
                        continue
            if not data:
                del configs[category]

        def _get_priority(k_v):
            """
            Note that returning the category directly when ordering info is unavailable
            will automatically send it to the end of an ordered list
            due to built-in ascii comparisons.
            :param k_v: tuple
            :return: order from category_order_lookup
            """
            order = category_order_lookup.get(k_v[0].lower(), k_v[0])

            if type(order) is int:
                return order
            return len(category_order_lookup)

        configs = OrderedDict(sorted(configs.items(), key=_get_priority))

    return configs


def get_preferences_forms(queryset, data=None):
    """
    Returns dict mapping category name to a
    sub-dict of Message classes to user settings forms.
    """
    from .forms import MessagingPreferenceForm

    preferences = {}
    for instance in queryset:
        preferences.setdefault(instance.category, {})
        preferences[instance.category][instance.message_name] = instance
    configs = OrderedDict()
    for category, cls_list in MESSAGE_CATEGORIES.items():
        configs.setdefault(category, OrderedDict())
        for cls in cls_list:
            instance = preferences.get(category or "", {}).get(cls.__name__)
            configs[category][cls] = MessagingPreferenceForm(
                data, instance=instance, prefix=category
            )
    return configs


def get_digest_report(user_id=None):
    from .models import Message, DigestPreference
    from .serializers import UserDigestSerializer

    report = {}

    start, end = get_previous_day_start_end_times()
    all_messages = Message.objects.since(start, end)

    if user_id is not None:
        all_messages = all_messages.filter(user__id=user_id)

    per_user_report = all_messages.values("user").annotate(n=Count("user")).filter(n__gt=0)
    serializer_context = {
        "start": start,
        "end": end,
    }
    if user_id and not per_user_report:
        user = User.objects.get(id=user_id)
        preference, created = DigestPreference.objects.get_or_create(user=user)
        serializer_context["threshold"] = preference.threshold
        report = UserDigestSerializer(user, context=serializer_context).data
        return report, start, end

    for entry in per_user_report:
        user = User.objects.get(id=entry["user"])
        preference, created = DigestPreference.objects.get_or_create(user=user)
        serializer_context["threshold"] = preference.threshold
        breakdown = UserDigestSerializer(user, context=serializer_context).data

        if user_id:
            return breakdown, start, end

        report[entry["user"]] = breakdown
    return report, start, end


def get_simple_hostname():
    """
    Returns the subdomain portion of the machine's hostname, such as "staging-04-12"
    (from "staging-04-12.pivotalenergy.net").

    On dev, this would return a Mac's computer name (from "machinename.local").
    """
    return socket.gethostname().split(".", 1)[0]


def get_notification_email_obj(message, required=False):
    from_email = settings.DEFAULT_FROM_EMAIL

    server_domain = "axis"
    if settings.SERVER_TYPE != settings.PRODUCTION_SERVER_TYPE:
        server_domain = "{}".format(settings.SERVER_TYPE)

    domain = "%s.pivotalenergy.net" % server_domain

    if (
        getattr(message, "user", None)
        and getattr(message.user, "site", None)
        and getattr(message.user.site, "domain", None)
    ):
        domain = message.user.site.domain

    unsubscribe_email_link = None
    if not required and message.modern_message:
        uid = urlsafe_base64_encode(force_bytes(message.user.pk))
        mname = urlsafe_base64_encode(force_bytes(message.modern_message))
        token = unsubscribe_email_token.make_token(message.user)
        url = reverse(
            "messaging:unsubscribe_email",
            kwargs={"uidb64": uid, "mnameb64": mname, "token": token},
        )
        unsubscribe_email_link = f"https://{domain}{url}"
    context = {
        "message": message,
        "domain": domain,
        "unsubscribe_email_link": unsubscribe_email_link,
    }

    # Swap out any embedded URLs to include the site prefix.
    # We don't really need this saved back to the database.
    original_content = message.content
    original_email_content = message.email_content

    if message.email_content:
        content = re.sub(r'href="(?=/)', r'href="https://%s' % context["domain"], message.content)
        email_content = re.sub(
            r'href="(?=/)',
            r'href="https://%s' % context["domain"],
            message.email_content,
        )
        message.email_content = email_content
    else:
        content = re.sub(r'href="(?=/)', r'href="https://%s' % context["domain"], message.content)
    message.content = content

    text_message = render_to_string("messaging/notification_email.txt", context)
    html_message = render_to_string("messaging/notification_email.html", context)

    # Put original content back so that future messages can find duplicates if required.
    message.content = original_content
    message.email_content = original_email_content

    subject = message.email_subject
    if subject is None or len(subject) == "":
        subject = message.title

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=from_email,
        to=[
            f'"{message.user.get_full_name()}"<{message.user.email}>',
        ],
    )

    msg.attach_alternative(html_message, "text/html")
    return msg


def get_digest_email_obj(user, report, start, stop):
    from_email = settings.DEFAULT_FROM_EMAIL

    server_domain = (
        "{}".format(settings.SERVER_TYPE)
        if settings.SERVER_TYPE != settings.PRODUCTION_SERVER_TYPE
        else "axis"
    )
    context = {
        "user": user,
        "report": report,
        "start_date": start,
        "end_date": stop,
        "domain": "%s.pivotalenergy.net" % server_domain,
    }

    new_report = report.copy()
    for idx, item in enumerate(new_report.get("messages")[:]):
        content = re.sub(
            r'href="(?=/)', r'href="https://%s' % context["domain"], item.get("content")
        )
        item["content"] = re.sub(r"href='(?=/)", r"href='https://%s" % context["domain"], content)
        new_report["messages"][idx] = item
    context["report"] = new_report

    text_message = render_to_string("messaging/digest_email.txt", context)
    html_message = render_to_string("messaging/digest_email.html", context)

    msg = EmailMultiAlternatives(
        subject="Axis Notifications Digest",
        body=text_message,
        from_email=from_email,
        to=[user.email],
    )
    msg.attach_alternative(html_message, "text/html")
    return msg


@shared_task(time_limit=60 * 5, default_retry_delay=15, max_retries=3, ignore_result=True)
def send_message_task(
    message_id: int,
    # sending conditions
    force_resend: bool = False,
    unique: bool = False,
    required: bool = False,
):
    """
    Sends the provided message to ``user``.

    ``message`` may be a ``Message`` model instance, a dict of kwargs for instantiating one, or else
    a callable that returns a ``Message``.

    A ``Message`` instance already having a date value for its ``sent`` field will be skipped unless
    the ``force_resend`` kwarg is True.
    """
    from axis.messaging.models import UserSession, Message

    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist as err:
        send_message_task.retry(exc=err)

    # Obtain delivery preference settings.  If modern_message is None, the company's default
    # fallback preference will be represented.
    user_preference = get_user_message_preference(message.user, message_name=message.modern_message)

    methods = user_preference.get_delivery_settings()
    if not any(methods.values()):
        log.debug(
            f"All delivery methods disabled for user {message.user}, "
            f"avoiding message creation: {message.modern_message}"
        )
        return

    session_keys = UserSession.objects.filter(user=message.user).values_list("session", flat=True)
    for session_key in session_keys:
        message.send(
            required=required,
            force_resend=force_resend,
            config=user_preference,
            session_key=session_key,
            unique=unique,
        )
    else:
        message.send(
            required=required,
            force_resend=force_resend,
            config=user_preference,
            session_key=None,
            unique=unique,
        )


# Handlers for the different ways we can deliver a message.
# The right handlers are selected by Message.send()
def send_alert(
    message,
    required=False,
    config=None,
    request=None,
    session_key=None,
    only_mine=False,
):
    """
    Sends the target message to the local websocket or else re-queues the delivery on the correct
    server for such a delivery to succeed.  ``required`` and ``config`` are simple override values
    that can be excluded if ``message`` already contains the correct information.

    One of ``request`` or ``session_key`` should be supplied in order to provide a method of knowing
    which autoscaling servers in this group hold which active websockets.
    """

    from .serializers import MessageSerializer

    this_host = get_simple_hostname()
    session = None
    if session_key:
        session = SessionStore(session_key=session_key)
    elif request:
        session = request.session
        session_key = session._session_key

    client_data = None
    if session is not None:
        client_data = session.get("websocket_ids", None)

    if client_data is not None:
        client_hosts = {k: v.get("host") for k, v in client_data.items()}
        client_ids = list(client_data.keys())
        serializer = MessageSerializer(message)
        message_data = JSONRenderer().render(serializer.data)

        # Requeue messages that need to be delivered by websockets elsewhere.
        # Multiple client_ids might exist pointing to a common set of names, so reduce those to
        # dispatch one task per external host, rather than one per client_id.
        if not only_mine:
            external_hosts = set([v for v in client_hosts.values() if v != this_host])
            for other_host in external_hosts:
                requeue_message_for_destination(other_host, message.id, session_key=session_key)

        # Tell local nodejs server to forward the message to the client
        log.info("Pushing message to %d clients: %r", len(client_ids), client_ids)

        try:
            _msg_data = message_data.decode("utf-8")
        except UnicodeDecodeError:
            _msg_data = message_data.decode()

        payload = json.dumps(
            {
                "client_ids": [
                    client_id for client_id in client_ids if client_hosts[client_id] == this_host
                ],
                "message": _msg_data,
            }
        )
        host = settings.MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_HOST
        port = settings.MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT
        try:
            response = requests.post(
                "http://{host}:{port}/push".format(host=host, port=port),
                data=payload,
                headers={"content-type": "application/json"},
            )
        except:
            log.exception(
                "Lost connection to local private websocket server! Can't push message "
                "to clients %r! %r",
                client_ids,
                message_data,
            )
        else:
            if response.status_code == 200:
                message.date_alerted = now()
                message.save()
            else:
                log.info(
                    "Client websocket(s) at %r has disconnected before delivery could be "
                    "completed.",
                    client_ids,
                )
    else:
        # No known-active websocket with this user, the message is already saved to the system,
        # so their next page load will pull it down for them.
        pass


def send_email(message, required=False, config=None):
    email = get_notification_email_obj(message, required=required)
    extra = {
        "to": message.user.email,
        "subject": message.title,
        "from": get_simple_hostname(),
    }
    try:
        email.send()
        msg = f"Sent email to {message.user.username} for notification id={message.id}"
        log.info(msg, extra=extra)
    except Exception as err:
        msg = f"{err} caught sending email to {message.user.username}"
        msg += f"for notification id={message.id}"
        log.exception(msg, extra=extra)
    else:
        message.date_sent = now()
    message.save()


# API utility for ``read()`` and ``bulk_read()`` work.
def send_read_receipts(message_ids, session_key):
    session = SessionStore(session_key=session_key)
    client_data = session.get("websocket_ids", None)
    if client_data is None:
        return

    client_ids = list(client_data.keys())
    this_host = get_simple_hostname()

    # Tell local nodejs server to forward the message to the client
    log.info("Delivering read receipts to %d clients: %r", len(client_ids), client_ids)
    payload = json.dumps(
        {
            "client_ids": [id for id in client_data.keys() if client_data[id]["host"] == this_host],
            "message_ids": message_ids,
        }
    )
    host = settings.MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_HOST
    port = settings.MESSAGING_PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT
    try:
        response = requests.post(
            "http://{host}:{port}/read".format(host=host, port=port),
            data=payload,
            headers={"content-type": "application/json"},
        )
    except:
        log.exception(
            "Lost connection to local private websocket server! Can't push read receipts "
            "to clients %r! %r",
            client_ids,
            message_ids,
        )
    else:
        if response.status_code != 200:
            log.info(
                "Client websocket(s) at %r has disconnected before delivery could be " "completed.",
                client_ids,
            )


# Redirection methods for moving messages belonging to other load-balanced machines in the group.
# The tasks they fire will make calls back to the utilities here for final delivery on the correct
# location.  The function ``send_alert()`` and ``send_read_receipts()`` are specifically designed
# to call these "requeue" utilities when they encounter websocket references that are marked with a
# different hostname than that of the local thread's machine, yet carry through with delivery when
# the hostname matches their own.


# Corresponds to ``send_message()``
def requeue_message_for_destination(other_host, message_id, session_key):
    from .tasks import deliver_message_to_own_websocket

    # The other server's dedicated queue name will always match the given hostname value
    deliver_message_to_own_websocket.apply_async(
        queue=other_host,
        kwargs={
            "message_id": message_id,
            "session_key": session_key,
        },
    )


# Corresponds to ``send_read_receipts()``
def requeue_read_receipts_for_destination(other_host, message_ids, session_key):
    from .tasks import deliver_own_read_receipts

    deliver_own_read_receipts.apply_async(
        queue=other_host,
        kwargs={
            "message_ids": message_ids,
            "session_key": session_key,
        },
    )
