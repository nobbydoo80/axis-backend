"""project.py: """

__author__ = "Artem Hruzd"
__date__ = "07/31/2020 12:47"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import os

from django.apps import apps
from django.conf import settings

from axis.messaging.messages import ModernMessage

customer_hirl_app = apps.get_app_config("customer_hirl")


class SingleFamilyProjectCreatedHIRLNotificationMessage(ModernMessage):
    title = "NGBS SF Project Registration"
    content = (
        "New project at <a href=\"{url}\" target='_blank'>"
        "{project_address}</a> registered by {verifier} "
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "customer_hirl",
        "templates",
        "customer_hirl",
        "projects",
        "single_family_project_create_verifier_email.html",
    )
    category = "NGBS Project"
    level = "info"
    sticky_alert = False

    verbose_name = "NGBS SF Project Registration"
    description = "Sent to NGBS users when SF Project has been registered by Verifier"

    companies_with_relationship_or_self = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class MultiFamilyProjectCreatedHIRLNotificationMessage(ModernMessage):
    title = "NGBS MF Project Registration"
    content = (
        "New project at <a href=\"{url}\" target='_blank'>"
        "{project_address}</a> registered by {verifier} "
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "customer_hirl",
        "templates",
        "customer_hirl",
        "projects",
        "multi_family_project_create_verifier_email.html",
    )
    category = "NGBS Project"
    level = "info"
    sticky_alert = False

    verbose_name = "NGBS MF Project Registration"
    description = "Sent to NGBS users when MF project has been registered by Verifier"

    companies_with_relationship_or_self = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class LandDevelopmentProjectCreatedHIRLNotificationMessage(ModernMessage):
    title = "NGBS Land Development Project Registration"
    content = (
        "New project at <a href=\"{url}\" target='_blank'>"
        "{project_address}</a> registered by {verifier} "
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "customer_hirl",
        "templates",
        "customer_hirl",
        "projects",
        "land_development_project_create_verifier_email.html",
    )
    category = "NGBS Project"
    level = "info"
    sticky_alert = False

    verbose_name = "NGBS Land Development Project Registration"
    description = "Sent to NGBS users when Project has been registered by Verifier"

    companies_with_relationship_or_self = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class HIRLProjectBuilderIsNotWaterSensePartnerMessage(ModernMessage):
    title = "Builder is not currently a WaterSense Builder Partner"
    content = (
        "You recently registered <a href='{url}' target='_blank'>{project_address}</a> for WaterSense certification. "
        "According to the EPA WaterSense website, the listed builder is not currently a WaterSense Builder Partner. "
        "Please direct your contact to visit https://www.epa.gov/watersense/watersense-partnership-agreement "
        "and complete the online partnership agreement. This partnership must be completed prior to submission. "
        "Thank you for your prompt attention to this request."
    )
    category = "NGBS Project"
    level = "info"
    sticky_alert = False
    verbose_name = (
        "When WaterSense Registration approved with builder that is not WaterSense Builder Partner"
    )
    description = "Send to verifier user instructions for WaterSense Builder Partnership "
    companies_with_relationship_or_self = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class IsAppealsHIRLProjectCreatedNotificationMessage(ModernMessage):
    title = "Appeals Project has been Registered"
    content = (
        "An Appeals Project has been registered at <a href=\"{url}\" target='_blank'>"
        "{project_address}</a> by {verifier}.\n Project H-Number: {h_number}"
    )
    category = "NGBS Project"
    level = "info"
    sticky_alert = False

    verbose_name = "NGBS Appeals Project Registration"
    description = (
        "Send additional notification when Appeals Project has been registered by Verifier"
    )

    companies_with_relationship_or_self = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class GreenPaymentsImportAdminNotificationMessage(ModernMessage):
    title = "New Green Payments file has been imported"
    content = (
        "New Green Payments file has been imported. "
        "<a href=\"{async_document_url}\" target='_blank'>View Details</a>"
    )
    email_content = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "customer_hirl",
        "templates",
        "customer_hirl",
        "projects",
        "green_payments_import_admin_notification.html",
    )
    category = "NGBS Project"
    level = "info"

    verbose_name = "New Green Payments file has been imported"
    description = "Sent to NGBS admin users after successfully Green Payments file import"

    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class HIRLProjectBillingStateChangedManuallyMessage(ModernMessage):
    title = "Billing state has been manually changed for Project"
    content = (
        "Billing state has been manually changed to <b>{new_state}</b> "
        "for Project ID: <a href=\"{project_url}\" target='_blank'>{project_id}</a>. \n Project H-Number: {h_number}"
    )

    category = "NGBS Project"
    level = "info"

    verbose_name = "Billing state has been manually changed"
    description = "Sent to NGBS admin users after project manual state has been changed"

    company_slugs = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]


class HIRLProjectInvoiceCantGeneratedWithoutClientAgreement(ModernMessage):
    title = "Auto-generated invoice cannot be created due to no Client Agreement"
    content = (
        "An active NGBS Client Agreement cannot be found for company "
        "<a href=\"{project_client_url}\" target='_blank'>{project_client_name}</a> for project "
        "<a href=\"{project_url}\" target='_blank'>{project_name}</a>. A Verification Report cannot be uploaded "
        "until a Client Agreement has been executed."
    )
    category = "NGBS Project"
    level = "warning"
    verbose_name = "Auto-generated invoice cannot be created due to no Client Agreement"
    description = "Sent if auto-generated invoice cannot be created due to no Client Agreement"

    companies_with_relationship_or_self = [
        customer_hirl_app.CUSTOMER_SLUG,
    ]

    waffle_disable_message_switches = [
        "Disable NGBS Notifications",
    ]
