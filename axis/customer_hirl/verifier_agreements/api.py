"""api.py: """


import logging

from django.apps import apps
from django.db.models import Q
from django_fsm import can_proceed
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from axis.core.permissions import AxisModelPermissions
from axis.examine.api import ExamineViewSetAPIMixin
from .messages.owner import VerifierAgreementChangedByVerifierMessage
from .messages.verifier import VerifierAgreementRequestForCertificateOfInsuranceMessage
from axis.customer_hirl.models import VerifierAgreement, COIDocument
from .serializers import (
    VerifierAgreementEnrollmentSerializer,
    VerifierAgreementManagementSerializer,
    COIDocumentSerializer,
    BasicCOIDocumentSerializer,
)
from .states import VerifierAgreementStates
from axis.customer_hirl.tasks import (
    update_verifier_signed_status_from_docusign_task,
    update_officer_signed_status_from_docusign_task,
    update_verifier_countersigned_status_from_docusign_task,
    post_agreement_for_verifier_signing_task,
)

__author__ = "Artem Hruzd"
__date__ = "04/16/2020 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


class ManagementPermission(AxisModelPermissions):
    """Check perm given to owner in permissions.py."""

    perms_map = dict(
        AxisModelPermissions.perms_map, PATCH=["customer_hirl.change_verifieragreement"]
    )

    def has_permission(self, request, view):
        """Return boolean for company being the owner, enrollee, or super."""

        instance = view.get_object()
        is_owner = request.user.company_id == instance.owner_id
        return is_owner or request.user.is_superuser


class ParticipantPermission(AxisModelPermissions):
    """Check perm given to company in permissions.py."""

    perms_map = dict(AxisModelPermissions.perms_map, POST=["customer_hirl.add_verifieragreement"])

    def has_permission(self, request, view):
        """Return boolean for company being the owner, enrollee, or super."""

        instance = view.get_object()
        if not instance.pk:
            return True  # Allow perms_map to apply in creation scenario
        is_owner = request.user.company_id == instance.owner_id
        is_verifier = request.user == instance.verifier
        is_company_admin = (
            request.user.company == instance.verifier.company and request.user.is_company_admin
        )
        return is_owner or is_verifier or request.user.is_superuser or is_company_admin


class VerifierAgreementEnrollmentViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    """Enrollee-biased APIs for managing a single assigned BuilderAgreement."""

    model = VerifierAgreement
    queryset = model.objects.all()
    serializer_class = VerifierAgreementEnrollmentSerializer

    permission_classes = (ParticipantPermission,)

    def get_examine_machinery_classes(self):
        """Return machinery classes that handle examine work in this API."""

        from .examine import (
            VerifierAgreementEnrollmentMachinery,
            VerifierAgreementEnrollmentApprovalMachinery,
        )

        return {
            "VerifierAgreementEnrollmentMachinery": VerifierAgreementEnrollmentMachinery,
            "VerifierAgreementEnrollmentApprovalMachinery": (
                VerifierAgreementEnrollmentApprovalMachinery
            ),
        }

    def filter_queryset(self, queryset):
        """Filter on 'company' for request user.

        If the approval machinery is in use (i.e., by the owner), then all requests are returned.
        In other cases, when the company is the enrollee, is taken from the request.
        """

        if self.request.user.is_superuser:
            return queryset

        owner_approval_flow = (
            self.request.query_params.get("machinery")
            == "VerifierAgreementEnrollmentApprovalMachinery"
        )
        if owner_approval_flow:
            return queryset.filter(owner=app.get_customer_company())
        elif self.request.user.is_company_admin:
            return queryset.filter(verifier__company=self.request.user.company)
        return queryset.filter(verifier=self.request.user)

    def perform_create(self, serializer):
        """Create and issue docusign signing request."""
        super(VerifierAgreementEnrollmentViewSet, self).perform_create(serializer)

        instance = serializer.instance

        customer_document = instance.generate_unsigned_customer_document()
        post_agreement_for_verifier_signing_task.delay(
            agreement_id=instance.id, customer_document_id=customer_document.id
        )

        url = instance.get_absolute_url()
        if not instance.verifier.company.coi_documents.exists():
            VerifierAgreementRequestForCertificateOfInsuranceMessage(url=url).send(
                user=instance.verifier, context={"owner": instance.owner, "url": url}
            )

    def perform_update(self, serializer):
        super(VerifierAgreementEnrollmentViewSet, self).perform_update(serializer)
        instance = serializer.instance
        if instance.state == VerifierAgreementStates.COUNTERSIGNED:
            url = instance.get_absolute_url()
            VerifierAgreementChangedByVerifierMessage(url="{}#/tabs/history".format(url)).send(
                user=instance.get_countersigning_user(),
                context={"verifier": instance.verifier, "url": url},
            )

    def pre_validate_documents(self, machinery):
        """Use a custom implementation in the serializer."""
        pass

    def save_documents(self, machinery, instance):
        """Use a custom implementation in the serializer."""
        pass


class VerifierAgreementManagementViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    """Owner-biased APIs for managing owned BuilderAgreement instances."""

    model = VerifierAgreement
    queryset = model.objects.all()
    serializer_class = VerifierAgreementManagementSerializer

    permission_classes = (ManagementPermission,)

    def get_examine_machinery_class(self, raise_exception=False):
        """Return machinery class that handles all examine work in this API."""

        from .examine import VerifierAgreementMachinery

        return VerifierAgreementMachinery

    def filter_queryset(self, queryset):
        """Narrow queryset to 'owned' or 'company' for request user."""

        if self.request.user.is_superuser:
            return queryset

        company = self.request.user.company
        return queryset.filter(Q(owner=company) | Q(verifier=self.request.user))

    @action(detail=True, methods=["post"])
    def transition(self, request, **kwargs):
        """Execute the transition named in query_params['name']"""

        instance = self.get_object()
        name = request.query_params.get("name")
        transitions = {
            "all": list(sorted(set(t.name for t in instance.get_all_state_transitions()))),
            "available": list(
                sorted(set(t.name for t in instance.get_available_state_transitions()))
            ),
            "user": list(
                sorted(t.name for t in instance.get_available_user_state_transitions(request.user))
            ),
        }

        if name not in transitions["all"]:
            raise PermissionDenied(
                {
                    "message": "Transition '{name}' does not exist".format(name=name),
                    "possible": transitions["all"],
                }
            )
        elif name not in transitions["available"]:
            raise PermissionDenied(
                {"message": "Transition not available", "available": transitions["available"]}
            )
        elif name not in transitions["user"]:
            raise PermissionDenied(
                {"message": "Transition not possible", "available": transitions["user"]}
            )

        transition = getattr(instance, name)
        if not can_proceed(transition):
            raise PermissionDenied(
                {
                    "message": "Can't proceed with {transition}".format(transition=transition),
                    "can_proceed()": False,
                }
            )
        try:
            transition()
        except Exception as exception:  # pylint: disable=broad-except
            log.exception(
                "Error attempting HIRL verifier agreement transition to %r for verifier "
                "agreement id %d.",
                name,
                instance.pk,
            )
            return Response({"message": exception, "status": status.HTTP_500_INTERNAL_SERVER_ERROR})

        # Avoid race conditions for other fields when this save takes place vs
        # other saves called in tasks that will have already finished executing.
        # It is always problematic in celery's ALWAYS_EAGER mode, too.
        #
        # If you need it to be a different state than what is being saved and
        # returned here, create a different transition method with a different
        # `target` state listed (or dynamic state).
        instance.save(update_fields=["state"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def force_state(self, request, **kwargs):
        instance = self.get_object()
        name = request.query_params.get("name")
        if name in VerifierAgreementStates.ordering:
            instance.state = name
            instance.save(update_fields=["state"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def ensure_blank_document(self, *args, **kwargs):
        """get_or_create() a CustomerDocument for the builder to sign."""

        instance = self.get_object()
        instance.generate_unsigned_customer_document()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def update_docusign_status(self, *args, **kwargs):
        """Get the status from docusign"""
        instance = self.get_object()

        if instance.state in [VerifierAgreementStates.NEW, VerifierAgreementStates.APPROVED]:
            if instance.verifier_signed_agreement and instance.company_with_multiple_verifiers:
                latest = update_officer_signed_status_from_docusign_task(instance.pk)
            else:
                latest = update_verifier_signed_status_from_docusign_task(instance.pk)
        elif instance.state == VerifierAgreementStates.VERIFIED:
            latest = update_verifier_countersigned_status_from_docusign_task(instance.pk)

        if latest["status"] == "error":
            return Response(
                {
                    "message": latest["status_message"],
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        return Response({"message": latest["status_message"], "status": status.HTTP_204_NO_CONTENT})


class COIDocumentViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = COIDocument
    queryset = model.objects.all()
    serializer_class = COIDocumentSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from .examine.coi_document import CompanyCOIDocumentExamineMachinery

        return CompanyCOIDocumentExamineMachinery

    def get_serializer_class(self):
        if self.request.user.company.slug == app.CUSTOMER_SLUG or self.request.user.is_superuser:
            return COIDocumentSerializer
        return BasicCOIDocumentSerializer

    def get_queryset(self):
        return self.model.objects.filter_by_user(user=self.request.user)
