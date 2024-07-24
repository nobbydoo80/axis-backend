"""Signals."""

__author__ = "Steven Klass"
__date__ = "1/17/17 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

import waffle
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver

from axis.customer_hirl.builder_agreements.docusign import HIRLDocuSignObject
from axis.customer_hirl.models import HIRLProject, BuilderAgreement, VerifierAgreement
from axis.invoicing.messages import HIRLInvoiceItemGroupUpdatedMessage
from axis.invoicing.models import InvoiceItem, InvoiceItemGroup

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


@receiver(m2m_changed, sender=HIRLProject.green_energy_badges.through)
def hirl_project_green_energy_badges_m2m_changed(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    if isinstance(instance, HIRLProject):
        # Get home status and new invoice or create it with badges that we added
        try:
            instance.home_status
        except ObjectDoesNotExist:
            return
        if instance.home_status:
            registration = instance.registration
            try:
                company_responsible_for_payment = registration.get_company_responsible_for_payment()
            except ObjectDoesNotExist:
                company_responsible_for_payment = None

            new_invoice_group = InvoiceItemGroup.objects.filter(
                home_status=instance.home_status, invoice__isnull=True
            ).first()

            hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

            if action == "post_add":
                if not new_invoice_group:
                    new_invoice_group = InvoiceItemGroup.objects.create(
                        home_status=instance.home_status, created_by=None
                    )

                for pk in pk_set:
                    green_energy_badge = model.objects.get(pk=pk)
                    _ = InvoiceItem.objects.create(
                        group=new_invoice_group,
                        name=green_energy_badge.get_name_with_invoice_label(),
                        cost=green_energy_badge.calculate_cost(
                            hirl_project_registration_type=instance.registration.project_type,
                            is_accessory_structure=instance.is_accessory_structure,
                            is_accessory_dwelling_unit=instance.is_accessory_dwelling_unit,
                            builder_organization=instance.registration.builder_organization,
                            story_count=instance.story_count,
                        ),
                        protected=True,
                    )

            elif action == "post_remove":
                # Find new invoice with Green Energy Badge name and remove if it is possible
                if new_invoice_group:
                    for pk in pk_set:
                        green_energy_badge = model.objects.get(pk=pk)
                        invoice_item = new_invoice_group.invoiceitem_set.filter(
                            name=green_energy_badge.get_name_with_invoice_label()
                        )
                        if invoice_item:
                            invoice_item.delete()

            if action in ["post_add", "post_remove"]:
                message_context = {
                    "home_url": f"{instance.home_status.home.get_absolute_url()}"
                    f"#/tabs/invoicing",
                    "home_address": instance.home_status.home,
                    "invoice_item_groups_url": f"/app/hi/invoice_item_groups/",
                }

                if company_responsible_for_payment:
                    HIRLInvoiceItemGroupUpdatedMessage().send(
                        company=company_responsible_for_payment,
                        context=message_context,
                    )

                    company_admins = hirl_company.users.filter(is_company_admin=True)

                    if company_admins:
                        HIRLInvoiceItemGroupUpdatedMessage().send(
                            users=company_admins,
                            context=message_context,
                        )


@receiver(post_save, sender="filehandling.CustomerDocument")
def client_agreement_notify_owner_of_new_document(
    sender, instance, raw=None, created=False, **kwargs
):
    """Notify `BuilderAgreement.owner` when new CustomerDocuments become available."""

    from axis.customer_hirl.builder_agreements.messages.owner import (
        NewBuilderAgreementDocumentMessage,
    )
    from axis.customer_hirl.models import BuilderAgreement
    from django.contrib.contenttypes.models import ContentType

    # Skip loaddata and irrelevant contenttypes
    if raw:
        return
    ct_agreement = ContentType.objects.get_for_model(BuilderAgreement)
    if instance.content_type_id != ct_agreement.id:
        return

    # Skip notifying about private documents, but notify once if/when they are made public
    if not instance.is_public:
        return

    # Skip this as we have already sent them a message to check their email
    if (
        "Ready for signing" in instance.description
        or "DocuSign Certification" in instance.description
    ):
        return

    agreement = instance.content_object
    url = agreement.get_absolute_url()
    NewBuilderAgreementDocumentMessage(
        url=url + "#/tabs/documents",
    ).send(
        company=agreement.owner,
        context={
            "url": url,
            "company": agreement.company,
            "filename": instance.filename,
            "download_url": instance.document.url,
        },
    )


@receiver(post_delete, sender=BuilderAgreement)
def client_agreement_set_docusign_envelope_status_to_voided(sender, instance, **kwargs):
    """
    Set envelope to status Voided in Docusign after we delete CA
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.data and instance.data.get("envelope_id"):
        envelope_id = instance.data.get("envelope_id")
        docusign = HIRLDocuSignObject()
        docusign.update_envelope(
            envelope_id=envelope_id,
            data={
                "status": "voided",
                "voidedReason": "Automatically set state to Voided, because Client Agreement on AXIS has been deleted",
            },
        )


@receiver(post_save, sender="filehandling.CustomerDocument")
def verifier_agreement_notify_owner_of_new_document(
    sender, instance, raw=None, created=False, **kwargs
):
    """Notify `VerifierAgreement.owner` when new CustomerDocuments become available."""

    from axis.customer_hirl.models import VerifierAgreement
    from axis.customer_hirl.verifier_agreements.messages.owner import (
        NewVerifierAgreementDocumentMessage,
    )
    from django.contrib.contenttypes.models import ContentType

    # Skip loaddata and irrelevant contenttypes
    if raw:
        return
    ct_agreement = ContentType.objects.get_for_model(VerifierAgreement)
    if instance.content_type_id != ct_agreement.id:
        return

    # Skip notifying about private documents, but notify once if/when they are made public
    if not instance.is_public:
        return

    # Skip this as we have already sent them a message to check their email
    if (
        "Ready for signing" in instance.description
        or "DocuSign Certification" in instance.description
    ):
        return

    agreement = instance.content_object
    url = agreement.get_absolute_url()
    NewVerifierAgreementDocumentMessage(url=url + "#/tabs/documents").send(
        company=agreement.owner,
        context={
            "url": url,
            "verifier": agreement.verifier,
            "filename": instance.filename,
            "download_url": instance.document.url,
        },
    )


@receiver(post_delete, sender=VerifierAgreement)
def verifier_agreement_set_docusign_envelope_status_to_voided(sender, instance, **kwargs):
    """
    Set envelope to status Voided in Docusign after we delete VA
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.verifier_agreement_docusign_data and instance.verifier_agreement_docusign_data.get(
        "envelope_id"
    ):
        envelope_id = instance.verifier_agreement_docusign_data.get("envelope_id")
        docusign = HIRLDocuSignObject()
        docusign.update_envelope(
            envelope_id=envelope_id,
            data={
                "status": "voided",
                "voidedReason": "Automatically set state to Voided, "
                "because Verifier Agreement on AXIS has been deleted",
            },
        )

    if instance.officer_agreement_docusign_data and instance.officer_agreement_docusign_data.get(
        "envelope_id"
    ):
        envelope_id = instance.officer_agreement_docusign_data.get("envelope_id")
        docusign = HIRLDocuSignObject()
        docusign.update_envelope(
            envelope_id=envelope_id,
            data={
                "status": "voided",
                "voidedReason": f"Automatically set state to Voided, "
                f"because Verifier Agreement on AXIS has been deleted",
            },
        )

    if instance.hirl_agreement_docusign_data and instance.hirl_agreement_docusign_data.get(
        "envelope_id"
    ):
        envelope_id = instance.hirl_agreement_docusign_data.get("envelope_id")
        docusign = HIRLDocuSignObject()
        docusign.update_envelope(
            envelope_id=envelope_id,
            data={
                "status": "voided",
                "voidedReason": "Automatically set state to Voided, "
                "because Verifier Agreement on AXIS has been deleted",
            },
        )
