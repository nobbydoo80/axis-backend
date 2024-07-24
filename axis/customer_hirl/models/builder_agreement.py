__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta", "Artem Hruzd"]

import datetime
import io
import logging
import os.path

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition
from simple_history.models import HistoricalRecords

from axis.core.fields import AxisJSONField
from axis.core.pypdf import AxisPdfFileReader, AxisPdfFileWriter
from axis.core.utils import get_frontend_url
from axis.customer_hirl.builder_agreements import messages
from axis.customer_hirl.builder_agreements.docusign import HIRLDocuSignObject
from axis.customer_hirl.managers import BuilderAgreementQuerySet
from axis.geocoder.models import Geocode
from axis.geographic.models import County

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
User = get_user_model()


class BuilderAgreement(models.Model):
    """Client Agreement/Enrollment model.

    This is created by the `company`, and approved by the `owner`.
    """

    NEW = "new"
    APPROVED = "approved"
    VERIFIED = "verified"
    COUNTERSIGNED = "countersigned"
    EXPIRED = "expired"

    STATE_CHOICES = (
        (NEW, "Submitted"),
        (APPROVED, "Approved"),
        (VERIFIED, "Routed for Counter-Signing"),
        (COUNTERSIGNED, "Counter-Signed"),
        (EXPIRED, "Expired"),
    )

    EXTENSION_REQUEST_NOT_SENT = "not_sent"
    EXTENSION_REQUEST_INITIATED = "initiated"
    EXTENSION_REQUEST_SENT_TO_CLIENT = "sent_to_client"
    EXTENSION_REQUEST_SENT_FOR_COUNTERSIGN = "sent_for_countersigned"
    EXTENSION_REQUEST_COUNTERSIGNED = "countersigned"
    EXTENSION_REQUEST_REJECTED = "rejected"

    EXTENSION_REQUEST_STATE_CHOICES = (
        (EXTENSION_REQUEST_NOT_SENT, "Not sent"),
        (EXTENSION_REQUEST_INITIATED, "Initiated"),
        (EXTENSION_REQUEST_SENT_TO_CLIENT, "Sent to Client"),
        (EXTENSION_REQUEST_SENT_FOR_COUNTERSIGN, "Sent for Counter-Signing"),
        (EXTENSION_REQUEST_COUNTERSIGNED, "Counter-Signed"),
        (EXTENSION_REQUEST_REJECTED, "Rejected"),
    )

    EXTENSION_REQUEST_DAYS_TO_EXTEND = 720

    owner = models.ForeignKey(
        "company.Company",
        related_name="%(app_label)s_managed_agreements",
        on_delete=models.CASCADE,
    )
    company = models.ForeignKey(
        "company.Company",
        related_name="%(app_label)s_enrolled_agreements",
        on_delete=models.CASCADE,
    )

    state = FSMField(default=NEW, choices=STATE_CHOICES)

    customer_documents = GenericRelation("filehandling.CustomerDocument")
    signed_agreement = models.ForeignKey(
        "filehandling.CustomerDocument",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
    )
    certifying_document = models.ForeignKey(
        "filehandling.CustomerDocument",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
    )
    agreement_start_date = models.DateField(null=True, blank=True)
    agreement_expiration_date = models.DateField(null=True, blank=True)

    extension_request_state = FSMField(
        default=EXTENSION_REQUEST_NOT_SENT,
        choices=EXTENSION_REQUEST_STATE_CHOICES,
        help_text="State for extension request",
    )

    extension_request_reject_reason = models.TextField(null=True, blank=True)

    extension_request_signed_agreement = models.ForeignKey(
        "filehandling.CustomerDocument",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
    )
    extension_request_certifying_document = models.ForeignKey(
        "filehandling.CustomerDocument",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
    )

    # Enrollee info
    website = models.CharField(max_length=100, blank=True)
    use_payment_contact_in_ngbs_green_projects = models.BooleanField(
        verbose_name="Should this person be contact for payment on future NGBS Green Projects?",
        default=False,
    )

    mailing_geocode = models.ForeignKey(
        Geocode, related_name="+", null=True, on_delete=models.SET_NULL, blank=True
    )
    mailing_geocode_response = models.ForeignKey(
        "geocoder.GeocodeResponse",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Selected by user in case of multiple valid results, "
        "automatically when we have one result and "
        "empty when geocode do not have valid results",
    )

    shipping_geocode = models.ForeignKey(
        Geocode, related_name="+", null=True, on_delete=models.SET_NULL, blank=True
    )
    shipping_geocode_response = models.ForeignKey(
        "geocoder.GeocodeResponse",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Selected by user in case of multiple valid results, "
        "automatically when we have one result and "
        "empty when geocode do not have valid results",
    )

    primary_contact_first_name = models.CharField(max_length=100, blank=True)
    primary_contact_last_name = models.CharField(max_length=100, blank=True)
    primary_contact_title = models.CharField(max_length=100, blank=True)
    primary_contact_phone_number = models.CharField(max_length=100, blank=True)
    primary_contact_cell_number = models.CharField(max_length=100, blank=True)
    primary_contact_email_address = models.CharField(max_length=100, blank=True)

    secondary_contact_first_name = models.CharField(max_length=100, blank=True)
    secondary_contact_last_name = models.CharField(max_length=100, blank=True)
    secondary_contact_title = models.CharField(max_length=100, blank=True)
    secondary_contact_phone_number = models.CharField(max_length=100, blank=True)
    secondary_contact_cell_number = models.CharField(max_length=100, blank=True)
    secondary_contact_email_address = models.CharField(max_length=100, blank=True)

    payment_contact_first_name = models.CharField(max_length=100, blank=True)
    payment_contact_last_name = models.CharField(max_length=100, blank=True)
    payment_contact_title = models.CharField(max_length=100, blank=True)
    payment_contact_phone_number = models.CharField(max_length=100, blank=True)
    payment_contact_cell_number = models.CharField(max_length=100, blank=True)
    payment_contact_email_address = models.CharField(max_length=100, blank=True)

    marketing_contact_first_name = models.CharField(max_length=100, blank=True)
    marketing_contact_last_name = models.CharField(max_length=100, blank=True)
    marketing_contact_title = models.CharField(max_length=100, blank=True)
    marketing_contact_phone_number = models.CharField(max_length=100, blank=True)
    marketing_contact_cell_number = models.CharField(max_length=100, blank=True)
    marketing_contact_email_address = models.CharField(max_length=100, blank=True)

    website_contact_first_name = models.CharField(max_length=100, blank=True)
    website_contact_last_name = models.CharField(max_length=100, blank=True)
    website_contact_title = models.CharField(max_length=100, blank=True)
    website_contact_phone_number = models.CharField(max_length=100, blank=True)
    website_contact_cell_number = models.CharField(max_length=100, blank=True)
    website_contact_email_address = models.CharField(max_length=100, blank=True)

    data = AxisJSONField(default=dict, blank=True, null=True)  # used in DocuSign state management

    extension_request_data = AxisJSONField(default=dict, blank=True, null=True)

    signer_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Using for direct DocuSign workflow without AXIS User",
    )
    signer_email = models.EmailField(
        null=True, blank=True, help_text="Using for direct DocuSign workflow without AXIS User"
    )
    initiator = models.ForeignKey(
        User,
        related_name="%(app_label)s_initiated_client_agreements",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User from other company(mostly Verifier) who created this Client Agreement for Company",
    )
    created_by = models.ForeignKey(
        User,
        related_name="%(app_label)s_created_client_agreements",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who created this Client Agreement for Company",
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    annotations = GenericRelation("annotation.Annotation")
    history = HistoricalRecords(excluded_fields=["data", "extension_request_data"])

    objects = BuilderAgreementQuerySet.as_manager()

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Client Agreement"
        verbose_name_plural = "Client Agreements"

    def __str__(self):
        return f"Client Agreement: {self.company.name}"

    def get_absolute_url(self):
        return get_frontend_url("hi", "client_agreements", "detail", self.pk)

    # Permissions
    def can_be_edited(self, user):
        from axis.company.models import Company

        if user.is_superuser:
            return True

        if user.company_id == self.owner_id:
            return True

        if self.state in [BuilderAgreement.EXPIRED, BuilderAgreement.COUNTERSIGNED]:
            return False

        if user.company_id == self.company_id:
            return True

        if (
            self.initiator
            and user.company == self.initiator.company
            and not self.certifying_document_id
        ):
            return True

        if user == self.created_by:
            return True

        return False

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if user.company_id == self.owner_id:
            return True

        if self.state in [BuilderAgreement.EXPIRED, BuilderAgreement.COUNTERSIGNED]:
            return False

        if (
            self.initiator
            and user.company == self.initiator.company
            and not self.certifying_document_id
        ):
            return True

        return False

    # Getters

    def has_insurance_dates_and_signed_document(self):
        """Return True when insurance fields for both parties are given.

        `self.signed_agreement` must also be set for a correct result.
        """

        return bool(
            self.agreement_start_date and self.agreement_expiration_date and self.signed_agreement
        )

    def get_signing_user(self) -> User:
        """
        Use one of the following to get recipient for Docusign:
        - signer_name and signer_email (Set via create CA w/o AXIS Account)
        - primary_contact_email_address and primary_contact_first_name and primary_contact_last_name (From current CA)
        - First company admin first_name last_name email
        - Company name and company default email

        Returns User object that can be in memory only
        """

        if self.signer_name and self.signer_email:
            return User(first_name=self.signer_name, email=self.signer_email)

        if (
            self.primary_contact_email_address
            and self.primary_contact_first_name
            and self.primary_contact_last_name
        ):
            return User(
                first_name=self.primary_contact_first_name,
                last_name=self.primary_contact_last_name,
                email=self.primary_contact_email_address,
            )

        user = self.company.users.filter(is_company_admin=True, is_active=True).first()
        if user and user.email:
            return user
        return User(first_name=self.company.name, email=self.company.default_email)

    def get_countersigning_user(self) -> User:
        """Return the expected user in `owner` for countersigning."""

        return self.owner.users.get(
            username=customer_hirl_app.BUILDER_AGREEMENT_COUNTER_SIGNING_USERNAME
        )

    def _get_envelope_id_for_email_resend(self, data_field_name: str) -> str:
        envelope_id = None
        field_data = getattr(self, data_field_name, None)

        if field_data:
            latest_result = field_data.get("latest_result")
            if latest_result:
                source = latest_result.get("source")
                if source:
                    status = source.get("status")
                    if status != "completed":
                        envelope_id = field_data["envelope_id"]
            else:
                envelope_id = field_data["envelope_id"]
        return envelope_id

    def resend_docusign_email(self) -> bool:
        """
        Resend DocuSing Email to current step recipient for main agreement or for extension agreement
        :return: boolean
        """
        envelope_id = self._get_envelope_id_for_email_resend(data_field_name="data")
        if not envelope_id:
            envelope_id = self._get_envelope_id_for_email_resend(
                data_field_name="extension_request_data"
            )

        if envelope_id:
            docusign = HIRLDocuSignObject()
            response = docusign.session_rest_get(
                f"/envelopes/{envelope_id}/recipients",
            )
            if response.status_code == 401:
                return False
            recipients_data = response.json()
            response = docusign.session_rest_put(
                f"/envelopes/{envelope_id}/recipients",
                params={"resend_envelope": True},
                data={"signers": recipients_data["signers"]},
            )
            if response.status_code != 200:
                return False
            return True
        return False

    def get_ca_version_to_sign(self) -> int:
        """
        Everytime when NGBS change their CA document, we need to update a version based on date change
        to be able to detect a version of a sign document.
        :return: Version number
        """
        if self.date_created.date() <= datetime.date(year=2022, month=5, day=31):
            return 1
        elif self.date_created.date() <= datetime.date(year=2022, month=8, day=8):
            return 2
        elif self.date_created.date() <= datetime.date(year=2023, month=4, day=22):
            return 3
        return 4

    # Transitions

    @transition(
        field=state,
        source=NEW,
        target=APPROVED,
        permission=lambda instance, user: user.is_superuser or user.company_id == instance.owner_id,
    )
    def approve(self):
        pass

    @transition(
        field=state,
        source=APPROVED,
        target=VERIFIED,
        permission=lambda instance, user: user.is_superuser or user.company_id == instance.owner_id,
        conditions=[
            has_insurance_dates_and_signed_document,
        ],
    )
    def verify(self):
        """Verify completion of builder setup and re-issues document for countersigning."""
        from axis.customer_hirl.tasks import post_agreement_for_owner_countersigning_task

        post_agreement_for_owner_countersigning_task.delay(
            agreement_id=self.id, customer_document_id=self.signed_agreement.id
        )

    @transition(
        field=state,
        source=VERIFIED,
        target=COUNTERSIGNED,
        permission=lambda instance, user: user.is_superuser or user.company_id == instance.owner_id,
    )
    def countersign(self, countersigned_document, certifying_document):
        date = timezone.now().date()
        hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

        self.signed_agreement = self.customer_documents.store(
            self,
            company=hirl_company,
            filename="Counter-signed Agreement ({date}).pdf".format(date=date),
            description="Counter-signed document ({date})".format(date=date),
            document=countersigned_document,
        )
        self.certifying_document = self.customer_documents.store(
            self,
            company=hirl_company,
            filename="Counter-signing Certifying Agreement ({date}).pdf".format(date=date),
            description="DocuSign Certification ({date})".format(date=date),
            document=certifying_document,
        )

        company_street_line1 = getattr(self.company, "street_line1", None)
        mailing_geocode = getattr(self, "mailing_geocode", None)
        if not company_street_line1 and mailing_geocode:
            self.company.street_line1 = mailing_geocode.raw_street_line1
            self.company.street_line2 = mailing_geocode.raw_street_line2
            self.company.city = mailing_geocode.raw_city
            self.company.zipcode = mailing_geocode.raw_zipcode
            self.company.save()

            self.company.counties.set(County.objects.all())
            self.company.save()

        company_shipping_geocode = getattr(self.company, "shipping_geocode", None)
        shipping_geocode = getattr(self, "shipping_geocode", None)
        if not company_shipping_geocode and shipping_geocode:
            self.company.shipping_geocode = shipping_geocode
            self.company.save()

        url = self.get_absolute_url()
        messages.builder.EnrollmentCompleteMessage(url=url).send(
            company=self.company,
            context={
                "owner": self.owner,
                "url": url,
                "start": self.agreement_start_date or "TBD",
                "end": self.agreement_expiration_date or "TBD",
            },
        )

    @transition(field=state, source="*", target=EXPIRED)
    def expire(self):
        """Issue a notification to the builder that the agreement has been retired."""
        url = self.get_absolute_url()

        messages.builder.ExpiredBuilderAgreementMessage(url=url).send(
            company=self.company, context={"owner": self.owner, "url": url}
        )

        admins = self.owner.users.filter(is_company_admin=True)
        if admins:
            messages.owner.ExpiredOwnerAgreementMessage(url=url).send(
                users=admins, context={"company": self.company, "url": url}
            )

    # Internals

    def receive_signed_document(self, signed_document, certifying_document):
        """Store and remember document references.

        Issues notifications to the owner and enrollee that the agreement is signed.
        """

        date = timezone.now().date()
        if signed_document:
            self.signed_agreement = self.customer_documents.store(
                self,
                company=self.company,
                filename="Signed Agreement ({date}).pdf".format(date=date),
                description="Signed document ({date})".format(date=date),
                document=signed_document,
            )
        if certifying_document:
            self.certifying_document = self.customer_documents.store(
                self,
                company=self.company,
                filename="Certifying Agreement ({date}).pdf".format(date=date),
                description="DocuSign Certification ({date})".format(date=date),
                document=certifying_document,
            )

    def generate_unsigned_customer_document(self):
        """Uses `populate_unsigned_template()` to create a concrete CustomerDocument."""

        date = timezone.now().date()
        unsigned_document = self.populate_unsigned_template()
        return self.customer_documents.store(
            self,
            company=self.company,
            filename="Unsigned Agreement ({date}).pdf".format(date=date),
            description="Ready for signing ({date})".format(date=date),
            document=unsigned_document,
        )

    def populate_unsigned_template(self):
        """Generate and return the pdf file rendered with pre-filled info."""

        output_stream = io.BytesIO()

        client_agreement_template = os.path.join(
            "axis", "customer_hirl", "static", "customer_hirl", "builder_embedded_agreement.pdf"
        )
        version = self.get_ca_version_to_sign()

        if version == 2:
            client_agreement_template = os.path.join(
                "axis",
                "customer_hirl",
                "static",
                "customer_hirl",
                "builder_embedded_agreement_v2.pdf",
            )
        elif version == 3:
            client_agreement_template = os.path.join(
                "axis",
                "customer_hirl",
                "static",
                "customer_hirl",
                "builder_embedded_agreement_v3.pdf",
            )
        elif version == 4:
            client_agreement_template = os.path.join(
                "axis",
                "customer_hirl",
                "static",
                "customer_hirl",
                "builder_embedded_agreement_v4.pdf",
            )

        with io.open(client_agreement_template, "rb") as input_stream:
            pdf_reader = AxisPdfFileReader(input_stream, strict=False)
            pdf_writer = AxisPdfFileWriter()
            num_pages = len(pdf_reader.pages)
            context = {
                "company_name": "{}".format(self.company.name),
                "company_street_line1": "{}".format(self.mailing_geocode.raw_street_line1),
                "company_street_line2": "{}".format(self.mailing_geocode.raw_street_line2),
                "company_city": "{}, {}".format(
                    self.mailing_geocode.raw_city,
                    self.mailing_geocode.raw_zipcode,
                ),
            }

            for i in range(num_pages):
                pdf_writer.add_page(pdf_reader.pages[i])
                page = pdf_writer.pages[i]
                pdf_writer.updatePageFormFieldValues(page, context)

            pdf_writer.write(output_stream)

        output_stream.seek(0)
        return output_stream.read()

    def populate_unsigned_extension_request_template(self):
        """Generate and return the pdf file rendered with pre-filled info."""

        output_stream = io.BytesIO()

        client_agreement_template = os.path.join(
            "axis", "customer_hirl", "static", "customer_hirl", "hi_ngbs_green_ca_extension.pdf"
        )

        with io.open(client_agreement_template, "rb") as input_stream:
            pdf_reader = AxisPdfFileReader(input_stream, strict=False)
            pdf_writer = AxisPdfFileWriter()
            num_pages = len(pdf_reader.pages)
            context = {
                "company_name": "{}".format(self.company.name),
                "company_street_line1": "{}".format(self.mailing_geocode.raw_street_line1),
                "company_street_line2": "{}".format(self.mailing_geocode.raw_street_line2),
                "company_city": "{}, {}".format(
                    self.mailing_geocode.raw_city,
                    self.mailing_geocode.raw_zipcode,
                ),
            }

            for i in range(num_pages):
                pdf_writer.add_page(pdf_reader.pages[i])
                page = pdf_writer.pages[i]
                pdf_writer.updatePageFormFieldValues(page, context)

            pdf_writer.write(output_stream)

        output_stream.seek(0)
        return output_stream.read()

    def generate_extend_request_unsigned_customer_document(self):
        """Uses `populate_unsigned_template()` to create a concrete CustomerDocument."""

        today = timezone.now().date()
        today_formatted = today.strftime("%m-%d-%Y")
        unsigned_document = self.populate_unsigned_extension_request_template()
        return self.customer_documents.store(
            self,
            company=self.company,
            filename=f"Unsigned Extension Request ({today_formatted}).pdf",
            description=f"Extension Request ready for signing ({today_formatted})",
            document=unsigned_document,
        )

    def can_initiate_extension_request(self, user):
        from axis.company.models import Company

        if user.is_superuser:
            return True

        if user.company_id == self.owner_id:
            return True

        if user.company_id == self.company_id:
            return True

        if user == self.initiator:
            return True

        if user == self.created_by:
            return True

        if user.company.company_type == Company.RATER_COMPANY_TYPE:
            return Company.objects.filter_by_user(user=user).filter(id=self.company_id).exists()

        return False

    @transition(
        field=extension_request_state,
        source=EXTENSION_REQUEST_NOT_SENT,
        target=EXTENSION_REQUEST_INITIATED,
        permission=can_initiate_extension_request,
        conditions=[
            lambda client_agreement: client_agreement.state == BuilderAgreement.COUNTERSIGNED,
        ],
    )
    def initiate_extension_request(self):
        url = self.get_absolute_url()
        messages.owner.NewExtensionRequestMessage(url=url).send(
            company=self.owner,
            context={
                "company": self.owner,
                "client_agreement_url": url,
            },
        )

    def can_approve_extension_request(self, user):
        if user.is_superuser:
            return True

        if user.company_id == self.owner_id:
            return True

        return False

    @transition(
        field=extension_request_state,
        source=EXTENSION_REQUEST_INITIATED,
        target=EXTENSION_REQUEST_SENT_TO_CLIENT,
        permission=can_approve_extension_request,
    )
    def approve_extension_request(self):
        from axis.customer_hirl.tasks import (
            post_client_agreement_extension_request_signing_task,
        )

        url = self.get_absolute_url()

        messages.builder.ExtensionRequestApprovedMessage(url=url).send(
            company=self.company,
            context={
                "owner": self.owner,
                "client_agreement_url": url,
            },
        )

        customer_document = self.generate_extend_request_unsigned_customer_document()
        post_client_agreement_extension_request_signing_task.delay(
            agreement_id=self.id, customer_document_id=customer_document.id
        )

    @transition(
        field=extension_request_state,
        source=EXTENSION_REQUEST_INITIATED,
        target=EXTENSION_REQUEST_REJECTED,
        permission=can_approve_extension_request,
    )
    def reject_extension_request(self, reason):
        self.extension_request_reject_reason = reason
        url = self.get_absolute_url()

        messages.builder.ExtensionRequestRejectedMessage(url=url).send(
            company=self.company,
            context={
                "owner": self.owner,
                "extension_request_reject_reason": reason,
                "client_agreement_url": url,
            },
        )

    @transition(
        field=extension_request_state,
        source=EXTENSION_REQUEST_SENT_TO_CLIENT,
        target=EXTENSION_REQUEST_SENT_FOR_COUNTERSIGN,
    )
    def send_for_countersign_extension_request(self):
        from axis.customer_hirl.tasks import (
            post_extension_request_agreement_for_owner_countersigning_task,
        )

        post_extension_request_agreement_for_owner_countersigning_task.delay(
            agreement_id=self.id,
            customer_document_id=self.extension_request_signed_agreement.id,
        )

    @transition(
        field=extension_request_state,
        source=EXTENSION_REQUEST_SENT_FOR_COUNTERSIGN,
        target=EXTENSION_REQUEST_COUNTERSIGNED,
    )
    def countersign_extension_request(self, countersigned_document, countersigned_certify_document):
        today = timezone.now().date()
        today_formatted = today.strftime("%m-%d-%Y")
        self.extension_request_signed_agreement = self.customer_documents.store(
            self,
            company=customer_hirl_app.get_customer_hirl_provider_organization(),
            filename=f"Counter-signing Extension Request Agreement ({today_formatted}).pdf",
            description=f"DocuSign Extension Request ({today_formatted})",
            document=countersigned_document,
        )

        self.extension_request_certifying_document = self.customer_documents.store(
            self,
            company=customer_hirl_app.get_customer_hirl_provider_organization(),
            filename=f"Counter-signing Extension Request Certifying Agreement Certification ({today_formatted}).pdf",
            description=f"DocuSign Extension Request Certify ({today_formatted})",
            document=countersigned_certify_document,
        )

        url = self.get_absolute_url()

        if self.agreement_expiration_date:
            self.agreement_expiration_date = self.agreement_expiration_date + timezone.timedelta(
                days=BuilderAgreement.EXTENSION_REQUEST_DAYS_TO_EXTEND
            )
        else:
            self.agreement_expiration_date = today + timezone.timedelta(
                days=BuilderAgreement.EXTENSION_REQUEST_DAYS_TO_EXTEND
            )

        if not self.agreement_start_date:
            self.agreement_start_date = today

        messages.builder.ExtensionRequestCompleteMessage(url=url).send(
            company=self.company,
            context={
                "owner": self.owner,
                "url": url,
                "start": self.agreement_start_date or "TBD",
                "end": self.agreement_expiration_date or "TBD",
            },
        )
