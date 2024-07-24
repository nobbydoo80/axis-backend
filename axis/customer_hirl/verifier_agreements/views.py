__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.apps import apps
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import RedirectView

from axis.annotation.models import Annotation
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import AxisFilterView, AxisExamineView
from axis.customer_hirl.models import VerifierAgreement
from axis.customer_hirl.verifier_agreements.filters import VerifierAgreementFilter
from axis.filehandling.machinery import customerdocument_machinery_factory
from .datatables import VerifierAgreementFilterDatatable
from .examine import (
    VerifierAgreementEnrollmentMachinery,
    VerifierAgreementMachinery,
    VerifierAgreementEnrollmentApprovalMachinery,
)
from .examine import get_verifieragreement_notes_machinery
from .forms import VerifierAgreementFilterForm
from .states import VerifierAgreementStates

from axis.customer_hirl.builder_agreements.examine.base import NGBSDocumentAgreementBase

app = apps.get_app_config("customer_hirl")


class ActiveVerifierAgreementEnrollmentRedirectView(RedirectView):
    """Redirect depending on enrollment existance."""

    def get_redirect_url(self):  # pylint: disable=arguments-differ
        """Redirect to user's active enrollment or creation page if one does not exist."""

        pk = (
            VerifierAgreement.objects.filter(
                owner=app.get_customer_company(), verifier=self.request.user
            )
            .exclude(state=VerifierAgreementStates.EXPIRED)
            .order_by("-pk")
            .values_list("pk", flat=True)
            .first()
        )
        if pk:
            return reverse("hirl:verifier_agreements:examine", kwargs={"pk": pk})
        return reverse("hirl:verifier_agreements:add")


class VerifierAgreementFilterView(AuthenticationMixin, AxisFilterView):
    """Agreement datatableview of enrolled companies."""

    model = VerifierAgreement
    permission_required = "customer_hirl.change_verifieragreement"
    show_add_button = False

    form_class = VerifierAgreementFilterForm
    datatable_class = VerifierAgreementFilterDatatable

    def has_permission(self):
        return (
            self.request.user.is_superuser
            or self.request.user.company.slug == app.CUSTOMER_SLUG
            or self.request.user.is_company_admin
        )

    def get_queryset(self):
        return VerifierAgreementFilter(
            data=self.request.GET, request=self.request, queryset=self.queryset
        ).qs

    def get_form_kwargs(self):
        kwargs = super(VerifierAgreementFilterView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class VerifierAgreementInitiateNew(RedirectView):
    def get_redirect_url(self):  # pylint: disable=arguments-differ
        """Expire all active agreements and redirect to enrollment page."""
        VerifierAgreement.objects.filter(
            owner=app.get_customer_company(), verifier=self.request.user
        ).exclude(state=VerifierAgreementStates.EXPIRED).update(
            state=VerifierAgreementStates.EXPIRED
        )
        return reverse("hirl:verifier_agreements:add")


class VerifierAgreementExamineView(AuthenticationMixin, AxisExamineView):
    """HIRL VerifierAgreement workflow page."""

    model = VerifierAgreement
    template_name = "customer_hirl/verifier_agreement_examine.html"

    enrollment_mode = False
    agreement_mode = False

    def get(self, request, **kwargs):
        try:
            self.object = self.get_object()
        except Exception:
            if self.request.user.company.slug == app.CUSTOMER_SLUG:
                return redirect("hirl:verifier_agreements:list")
            if self.request.user.is_company_admin:
                return super(VerifierAgreementExamineView, self).get(request, **kwargs)
            return redirect("hirl:verifier_agreements:enroll")

        if self.object and self.create_new:
            return redirect("hirl:verifier_agreements:examine", pk=self.object.id)
        return super(VerifierAgreementExamineView, self).get(request, **kwargs)

    def has_permission(self):
        return super(VerifierAgreementExamineView, self).has_permission() or (
            self.request.user.company and self.request.user.company.slug == app.CUSTOMER_SLUG
        )

    def get_permission_required(self):
        """Check the 'add' perm for enrollees, or 'change' for owners."""

        return ("customer_hirl.change_verifieragreement",)

    def get_object(self):
        """
        Returns a Verifier's active enrollment (state__in=[None, 'new']),
        or else the usual object at the url with access controls applied.
        """
        user = self.request.user
        customer = app.get_customer_company()
        queryset = self.model.objects.all()

        if self.enrollment_mode:
            queryset = queryset.filter(owner=customer, verifier=user).exclude(
                state=VerifierAgreementStates.EXPIRED
            )
        elif self.agreement_mode or user.is_superuser:
            if user.company_id == customer.id:
                queryset = queryset.filter(owner_id=user.company_id)
            elif user.is_company_admin and not user.is_superuser:
                queryset = queryset.filter(verifier__company=user.company)
            elif not user.is_superuser:
                queryset = queryset.filter(verifier=user)

            queryset = queryset.filter(pk=self.kwargs["pk"])
        else:
            raise Exception("as_view() must be given `enrollment_mode` or `agreement_mode` kwarg")

        instance = queryset.first()
        # redirect company admin users to creating form
        # in case we don't have any VA agreements
        if not instance and not self.create_new and self.request.user.is_company_admin:
            return instance

        if not instance and not self.create_new:
            raise Http404("Access to enrollment not allowed")
        return instance

    def get_machinery(self):
        """Builds a machinery scheme that fits the user's role."""

        user = self.request.user
        self.is_owner = (user.company.slug == app.CUSTOMER_SLUG) or user.is_superuser
        instance = self.get_object()
        if self.is_owner and self.enrollment_mode:
            raise Http404("The enrollment area is for verifiers only.")

        context = {
            "request": self.request,
        }

        machineries = {}

        if self.is_owner or user.is_superuser:
            # Customer manages the agreement parameters
            self.primary_machinery = VerifierAgreementMachinery(instance=instance, context=context)
            machineries["hirl_verifier_agreement"] = self.primary_machinery
            machineries[
                "hirl_verifier_agreement_enrollment"
            ] = VerifierAgreementEnrollmentApprovalMachinery(instance=instance, context=context)
        else:
            # Enrolling company see only the enrollment machinery
            self.primary_machinery = VerifierAgreementEnrollmentMachinery(
                instance=instance, create_new=self.create_new, context=context
            )
            machineries["hirl_verifier_agreement_enrollment"] = self.primary_machinery

        # Add documents under whichever api name is in play
        customer_document_machinery_class = customerdocument_machinery_factory(  # pylint: disable=invalid-name
            self.model,
            allow_delete=False,
            bases=(NGBSDocumentAgreementBase,),
            # Avoid model name clash in CustomerDocument's api for get_examine_machinery_classes()
            machinery_name="HIRLVerifierAgreementCustomerDocumentMachinery",
            dependency_name=self.primary_machinery.type_name_slug,
            api_name="hirl_verifier_agreement_documents",
        )
        machineries["documents"] = customer_document_machinery_class(
            objects=instance.customer_documents.all() if instance else [], context=context
        )

        # Generic notes system
        notes = Annotation.objects.none()
        if instance:
            notes = instance.annotations.filter_by_user(user)
        notes_machinery_class = get_verifieragreement_notes_machinery()
        machineries["notes"] = notes_machinery_class(
            objects=notes, context=dict(context, dependency_name=self.primary_machinery.type_name)
        )

        return machineries

    def get_context_data(self, **kwargs):
        """Add `is_owner` to context."""

        context = super(VerifierAgreementExamineView, self).get_context_data(**kwargs)

        context["is_owner"] = self.is_owner

        return context
