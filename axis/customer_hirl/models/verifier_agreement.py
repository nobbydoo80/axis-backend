__author__ = "Artem Hruzd"
__date__ = "04/16/2020 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import io
import os
import datetime

import waffle
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django_fsm import FSMField, transition
from simple_history.models import HistoricalRecords

from axis.core.fields import AxisJSONField
from axis.core.pypdf import AxisPdfFileReader, AxisPdfFileWriter
from axis.core.utils import unrandomize_filename
from axis.customer_hirl.builder_agreements.docusign import HIRLBaseDocuSignDeclarativeTemplate
from axis.customer_hirl.messages.coi import COIAvailableMessage, COIChangedMessage
from axis.filehandling.models import DOCUMENT_TYPES
from axis.geocoder.models import Geocode
from axis.geographic.models import USState
from axis.customer_hirl.managers import COIDocumentQuerySet
from axis.customer_hirl.verifier_agreements.messages.verifier import (
    VerifierEnrollmentCompleteMessage,
    ExpiredVerifierAgreementMessage,
)
from axis.customer_hirl.verifier_agreements.messages.owner import (
    ExpiredOwnerVerifierAgreementMessage,
)
from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class VerifierAgreement(models.Model):
    """
    Builder Verifier Agreement/Enrollment model.

    This is created by the `company`, and approved by the `owner`.
    """

    owner = models.ForeignKey(
        "company.Company",
        related_name="%(app_label)s_managed_verifier_agreements",
        on_delete=models.CASCADE,
    )
    verifier = models.ForeignKey(
        User,
        related_name="%(app_label)s_enrolled_verifier_agreements",
        on_delete=models.CASCADE,
    )

    state = FSMField(default=VerifierAgreementStates.NEW, choices=VerifierAgreementStates.choices)

    verifier_signed_agreement = models.OneToOneField(
        "filehandling.CustomerDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    verifier_certifying_document = models.OneToOneField(
        "filehandling.CustomerDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    officer_signed_agreement = models.OneToOneField(
        "filehandling.CustomerDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    officer_certifying_document = models.OneToOneField(
        "filehandling.CustomerDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    hirl_signed_agreement = models.OneToOneField(
        "filehandling.CustomerDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hirl_certifying_document = models.OneToOneField(
        "filehandling.CustomerDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    customer_documents = GenericRelation("filehandling.CustomerDocument")

    # Enrollee info
    mailing_geocode = models.ForeignKey(
        Geocode, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )

    shipping_geocode = models.ForeignKey(
        Geocode, related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )

    applicant_first_name = models.CharField(max_length=30, blank=True)
    applicant_last_name = models.CharField(max_length=30, blank=True)
    applicant_title = models.CharField(max_length=100, blank=True)
    applicant_phone_number = models.CharField(max_length=30, blank=True)
    applicant_cell_number = models.CharField(max_length=30, blank=True)
    applicant_email = models.EmailField(max_length=100, blank=True)

    administrative_contact_first_name = models.CharField(max_length=30, blank=True)
    administrative_contact_last_name = models.CharField(max_length=30, blank=True)
    administrative_contact_phone_number = models.CharField(max_length=30, blank=True)
    administrative_contact_email = models.EmailField(max_length=100, blank=True)

    company_with_multiple_verifiers = models.BooleanField(default=False)
    company_officer_first_name = models.CharField(max_length=30, blank=True)
    company_officer_last_name = models.CharField(max_length=30, blank=True)
    company_officer_title = models.CharField(max_length=30, blank=True)
    company_officer_phone_number = models.CharField(max_length=30, blank=True)
    company_officer_email = models.EmailField(max_length=100, blank=True)

    agreement_start_date = models.DateField(null=True, blank=True)
    agreement_expiration_date = models.DateField(null=True, blank=True)
    agreement_verifier_id = models.CharField("Verifier ID", max_length=64, blank=True)

    # used in DocuSign state management
    verifier_agreement_docusign_data = AxisJSONField(default=dict, blank=True)
    officer_agreement_docusign_data = AxisJSONField(default=dict, blank=True)
    hirl_agreement_docusign_data = AxisJSONField(default=dict, blank=True)

    us_states = models.ManyToManyField(USState, blank=True)
    provided_services = models.ManyToManyField("ProvidedService", blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    annotations = GenericRelation("annotation.Annotation")
    history = HistoricalRecords()

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Verifier Agreement"
        verbose_name_plural = "Verifier Agreements"

    def __str__(self):
        return "Verifier Agreement: {self.verifier}".format(self=self)

    # Django hooks
    def get_absolute_url(self):
        """Return examine url for both agreement/enrollment."""
        return reverse("hirl:verifier_agreements:examine", kwargs={"pk": self.pk})

    def has_owner_powers(self, user):
        """Return True if the user is an owner or super.  This is an object-level perm."""

        if user.is_superuser:
            return True
        is_owner = user.company_id == self.owner_id
        return is_owner and user.is_company_admin

    def has_verifier_powers(self, user):
        """Return True if the user is the enrollee or super.  This is an object-level perm."""
        return (
            user.is_superuser
            or user == self.verifier
            or (user.company == self.verifier.company and user.is_company_admin)
        )

    # Getters
    def get_countersigning_user(self):
        """Return the expected user in `owner` for countersigning."""

        return self.owner.users.get(
            username=customer_hirl_app.VERIFIER_AGREEMENT_COUNTER_SIGNING_USERNAME
        )

    def get_va_version_to_sign(self) -> int:
        """
        Everytime when NGBS change their document we need to update version based on date change
        to be able to detect version of sign document.
        :return: version number
        """
        if self.date_created.date() <= datetime.date(year=2022, month=9, day=18):
            return 1
        return 2

    # Internals

    def receive_verifier_signed_document(self, signed_document, certifying_document):
        """Store and remember document references.

        Issues notifications to the owner and enrollee that the agreement is signed.
        """

        date = timezone.now().date()

        self.verifier_signed_agreement = self.customer_documents.store(
            self,
            company=self.verifier.company,
            filename="Verifier Signed Agreement ({date}).pdf".format(date=date),
            description="Verifier Signed document ({date})".format(date=date),
            document=signed_document,
        )
        self.verifier_certifying_document = self.customer_documents.store(
            self,
            company=self.verifier.company,
            filename="Verifier Certifying Agreement ({date}).pdf".format(date=date),
            description="Verifier DocuSign Certification ({date})".format(date=date),
            document=certifying_document,
        )

        if self.company_with_multiple_verifiers and self.verifier_signed_agreement:
            from axis.customer_hirl.tasks import post_agreement_for_officer_signing_task

            post_agreement_for_officer_signing_task.delay(
                agreement_id=self.id, customer_document_id=self.verifier_signed_agreement.id
            )

    def receive_officer_signed_document(self, signed_document, certifying_document):
        date = timezone.now().date()

        self.officer_signed_agreement = self.customer_documents.store(
            self,
            company=self.verifier.company,
            filename="Officer Signed Agreement ({date}).pdf".format(date=date),
            description="Officer Signed document ({date})".format(date=date),
            document=signed_document,
        )
        self.officer_certifying_document = self.customer_documents.store(
            self,
            company=self.verifier.company,
            filename="Officer Certifying Agreement ({date}).pdf".format(date=date),
            description="Officer DocuSign Certification ({date})".format(date=date),
            document=certifying_document,
        )

    def generate_unsigned_customer_document(self):
        """Uses `populate_unsigned_template()` to create a concrete CustomerDocument."""

        date = timezone.now().date()
        unsigned_document = self.populate_unsigned_template()
        return self.customer_documents.store(
            self,
            company=self.verifier.company,
            filename="Unsigned Agreement ({date}).pdf".format(date=date),
            description="Ready for signing ({date})".format(date=date),
            document=unsigned_document,
        )

    def populate_unsigned_template(self):
        """Generate and return the pdf file rendered with pre-filled info."""
        output_stream = io.BytesIO()

        verifier_agreement_template = os.path.join(
            "axis", "customer_hirl", "static", "customer_hirl", "verifier_embedded_agreement.pdf"
        )
        version = self.get_va_version_to_sign()

        if version == 2:
            verifier_agreement_template = os.path.join(
                "axis",
                "customer_hirl",
                "static",
                "customer_hirl",
                "verifier_embedded_agreement_v2.pdf",
            )

        with io.open(verifier_agreement_template, "rb") as input_stream:
            pdf_reader = AxisPdfFileReader(input_stream, strict=False)
            pdf_writer = AxisPdfFileWriter()
            num_pages = len(pdf_reader.pages)
            context = {
                "individual_checkbox": True,
                "individual_name": "{} {}".format(
                    self.applicant_first_name, self.applicant_last_name
                ),
                "mailing_street_line1": self.mailing_geocode.raw_street_line1,
                "mailing_street_line2": self.mailing_geocode.raw_street_line2,
                "mailing_city_and_zipcode": "{} {}".format(
                    self.mailing_geocode.raw_city,
                    self.mailing_geocode.raw_zipcode,
                ),
                "individual_name6": "{} {}".format(
                    self.applicant_first_name, self.applicant_last_name
                ),
                "individual_title6": "{}".format(
                    self.applicant_title,
                ),
                "officer_name6": "{} {}".format(
                    self.company_officer_first_name, self.company_officer_last_name
                ),
                "officer_title6": "{}".format(
                    self.company_officer_title,
                ),
            }
            if self.company_with_multiple_verifiers:
                context.update(
                    {
                        "sponsor_company_checkbox": self.company_with_multiple_verifiers,
                        "individual_company_name1": self.verifier.company.name,
                        "officer_name1": "{} {}".format(
                            self.company_officer_first_name, self.company_officer_last_name
                        ),
                        "officer_title1": "{}".format(
                            self.company_officer_title,
                        ),
                    }
                )

            for i in range(num_pages):
                pdf_writer.add_page(pdf_reader.pages[i])
                page = pdf_writer.pages[i]
                pdf_writer.updatePageFormFieldValues(page, context)

            pdf_writer.write(output_stream)

        output_stream.seek(0)
        return output_stream.read()

    def resend_docusign_email(self):
        envelope_id = None
        va_docusign_data = None

        if (
            self.verifier_agreement_docusign_data
            and not self.officer_agreement_docusign_data
            and not self.hirl_agreement_docusign_data
        ):
            va_docusign_data = self.verifier_agreement_docusign_data
        elif self.officer_agreement_docusign_data and not self.hirl_agreement_docusign_data:
            va_docusign_data = self.officer_agreement_docusign_data
        elif self.hirl_agreement_docusign_data:
            va_docusign_data = self.hirl_agreement_docusign_data

        if va_docusign_data:
            latest_result = va_docusign_data.get("latest_result")
            if latest_result:
                source = latest_result.get("source")
                if source:
                    status = source.get("status")
                    if status != "completed":
                        envelope_id = va_docusign_data["envelope_id"]
            else:
                envelope_id = va_docusign_data["envelope_id"]

        if envelope_id:
            docusign = HIRLBaseDocuSignDeclarativeTemplate()
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

    def can_countersign(self):
        """
        Verify that we are ready to countersign by HIRL company.
        We should have verifier sign and
        officer sign(in case of company with multiple verifiers)
        :return:
        """
        if self.state != VerifierAgreementStates.APPROVED:
            return False
        if not self.verifier_signed_agreement:
            return False

        if not self.agreement_start_date or not self.agreement_expiration_date:
            return False

        if self.company_with_multiple_verifiers and not self.officer_signed_agreement:
            return False
        return True

    # Transitions

    @transition(
        field=state,
        source=VerifierAgreementStates.NEW,
        target=VerifierAgreementStates.APPROVED,
        permission=has_owner_powers,
    )
    def approve(self):
        """Start insurance certificate request if not already provided.

        Posts legal document for signing (notification comes from task).
        Issues notification via a task to the enrolled company, informing them of next steps.
        """
        pass

    @transition(
        field=state,
        source=VerifierAgreementStates.APPROVED,
        target=VerifierAgreementStates.VERIFIED,
        permission=has_owner_powers,
        conditions=[
            can_countersign,
        ],
    )
    def verify(self):
        """Verify completion of verifier setup and re-issues document for countersigning."""
        from axis.customer_hirl.tasks import post_verifier_agreement_for_owner_countersigning_task

        # Standard behavior
        document = self.verifier_signed_agreement
        if self.company_with_multiple_verifiers:
            document = self.officer_signed_agreement
        post_verifier_agreement_for_owner_countersigning_task.delay(
            agreement_id=self.id, customer_document_id=document.id
        )

    @transition(
        field=state,
        source=VerifierAgreementStates.VERIFIED,
        target=VerifierAgreementStates.COUNTERSIGNED,
        permission=has_owner_powers,
    )
    def countersign(self, countersigned_document, certifying_document):
        date = timezone.now().date()
        for_user = self.get_countersigning_user()

        self.hirl_signed_agreement = self.customer_documents.store(
            self,
            company=for_user.company,
            filename="Counter-signed Agreement ({date}).pdf".format(date=date),
            description="Counter-signed document ({date})".format(date=date),
            document=countersigned_document,
        )
        self.hirl_certifying_document = self.customer_documents.store(
            self,
            company=for_user.company,
            filename="Counter-signing Certifying Agreement ({date}).pdf".format(date=date),
            description="DocuSign Certification ({date})".format(date=date),
            document=certifying_document,
        )

        url = self.get_absolute_url()
        VerifierEnrollmentCompleteMessage(url=url).send(
            user=self.verifier,
            context={"owner": self.owner, "url": url, "end": self.agreement_expiration_date},
        )

    @transition(field=state, source="*", target=VerifierAgreementStates.EXPIRED)
    def expire(self):
        """Issue a notification to the verifier that the agreement has been expired."""

        url = self.get_absolute_url()

        ExpiredVerifierAgreementMessage(url=url).send(
            user=self.verifier, context={"owner": self.owner, "url": url}
        )

        admins = self.owner.users.filter(is_company_admin=True)
        if admins:
            ExpiredOwnerVerifierAgreementMessage(url=url).send(
                company=self.owner, context={"verifier": self.verifier, "url": url}
            )


class ProvidedService(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    order = models.IntegerField(default=0)

    last_update = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-order",)

    def __str__(self):
        return "{name}".format(name=self.name)


class COIDocument(models.Model):
    company = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, related_name="coi_documents"
    )
    document = models.FileField(max_length=512, null=True, blank=True)

    filesize = models.PositiveIntegerField(editable=False, blank=True, null=True)
    type = models.CharField(choices=DOCUMENT_TYPES, max_length=15, blank=True)
    description = models.CharField(max_length=255, blank=True)

    policy_number = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    objects = COIDocumentQuerySet.as_manager()

    history = HistoricalRecords()

    class Meta:
        verbose_name = "COI Document"
        ordering = ("-last_update",)

    def __str__(self):
        return f"COI Document {self.company}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(COIDocument, cls).from_db(db, field_names, values)
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        from axis.company.models import Company

        instance = super(COIDocument, self).save(*args, **kwargs)

        owners = Company.objects.filter(
            Q(customer_hirl_managed_verifier_agreements__verifier__company=self.company)
            | Q(customer_hirl_managed_agreements__company=self.company)
        ).distinct()
        url = "{}#/tabs/coi".format(self.company.get_absolute_url())

        original = dict()
        if hasattr(self, "_loaded_values"):
            original = self._loaded_values

        if self.document and not original.get("document"):
            if not waffle.switch_is_active("Disable NGBS Notifications"):
                for owner in owners:
                    COIAvailableMessage(url=url).send(
                        company=owner,
                        context={
                            "company": self.company.name,
                            "coi": "#{} {}".format(self.id, self.description),
                            "url": url,
                        },
                    )
        elif (
            self.document and original.get("document") and self.document != original.get("document")
        ):
            if not waffle.switch_is_active("Disable NGBS Notifications"):
                for owner in owners:
                    COIChangedMessage(url=url).send(
                        company=owner,
                        context={
                            "company": self.company,
                            "coi": "#{} {}".format(self.id, self.description),
                            "url": url,
                        },
                    )

        return instance

    @property
    def filename(self):
        """Used to return the real name of the file."""
        return os.path.basename(unrandomize_filename(self.document.name))

    def can_be_deleted(self, user):
        if user.is_superuser:
            return True

        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG and user.is_company_admin:
            if self.company.is_sponsored_by_customer_hirl():
                return True
        return False

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG and user.is_company_admin:
            if self.company.is_sponsored_by_customer_hirl():
                return True
        return user.company == self.company
