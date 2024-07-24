"""hirl_project_registration.py: """

__author__ = "Artem Hruzd"
__date__ = "04/22/2021 17:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Count, DateField, Sum, F
from django.db.models.functions import TruncMonth, Cast, Coalesce
from django.http import Http404
from django_fsm import has_transition_perm, can_proceed
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.core.api_v3.viewsets import NestedHistoryViewSet
from axis.customer_hirl.api_v3 import (
    HIRL_PROJECT_REGISTRATION_SEARCH_FIELDS,
    HIRL_PROJECT_REGISTRATION_ORDERING_FIELDS,
)
from axis.customer_hirl.api_v3.filters import (
    HIRLProjectRegistrationFilter,
    HIRLProjectRegistrationActivityMetricsByMonthFilter,
)
from axis.customer_hirl.api_v3.permissions import (
    HIRLCompanyMemberPermission,
    HIRLProjectRegistrationCreatePermission,
    HIRLProjectRegistrationUpdatePermission,
    HIRLProjectRegistrationViewPermission,
    HIRLProjectRegistrationDeletePermission,
)
from axis.customer_hirl.api_v3.serializers import (
    BasicHIRLProjectSerializer,
    HIRLProjectRegistrationSerializer,
    BasicHIRLProjectRegistrationSerializer,
    CreateSFHIRLProjectRegistrationSerializer,
    CreateMFHIRLProjectRegistrationSerializer,
    HIRLProjectRegistrationListSerializer,
    AbandonHIRLProjectRegistrationSerializer,
    HIRLProjectRegistrationActivityMetricsByMonthSerializer,
    CreateLandDevelopmentHIRLProjectRegistrationSerializer,
    HIRLProjectRegistrationActivityMetricsByUnitsMonthSerializer,
)
from axis.customer_hirl.messages import (
    SingleFamilyProjectCreatedHIRLNotificationMessage,
    HIRLProjectRegistrationApprovedByHIRLCompanyMessage,
    HIRLProjectRegistrationCreatedMessage,
    HIRLProjectBuilderIsNotWaterSensePartnerMessage,
)
from axis.customer_hirl.messages.project import (
    MultiFamilyProjectCreatedHIRLNotificationMessage,
    HIRLProjectInvoiceCantGeneratedWithoutClientAgreement,
    LandDevelopmentProjectCreatedHIRLNotificationMessage,
    IsAppealsHIRLProjectCreatedNotificationMessage,
)
from axis.customer_hirl.models import HIRLProjectRegistration, BuilderAgreement
from axis.invoicing.messages import (
    HIRLResponsibleEntityForPaymentInvoiceItemGroupCreatedMessage,
    InvoiceCreatedNotificationMessage,
)
from axis.invoicing.models import Invoice, InvoiceItemGroup, InvoiceItem

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLProjectRegistrationViewSet(
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    approve:
        Approve project for customer HI user. Moving SF project
        type to state Active and MF project to state Pending
    """

    model = HIRLProjectRegistration
    queryset = model.objects.all().order_by(*model._meta.ordering)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HIRL_PROJECT_REGISTRATION_SEARCH_FIELDS
    ordering_fields = HIRL_PROJECT_REGISTRATION_ORDERING_FIELDS
    ordering = ("-id",)

    @property
    def permission_classes(self):
        if self.action in [
            "create_single_family",
            "create_multi_family",
            "create_land_development",
        ]:
            return [
                HIRLProjectRegistrationCreatePermission,
            ]
        if self.action in [
            "list",
            "retrieve",
        ]:
            return [
                HIRLProjectRegistrationViewPermission,
            ]
        if self.action in ["update", "partial_update"]:
            return [
                HIRLProjectRegistrationUpdatePermission,
            ]
        if self.action in [
            "destroy",
        ]:
            return [
                HIRLProjectRegistrationDeletePermission,
            ]
        return [
            HIRLCompanyMemberPermission,
        ]

    @property
    def filterset_class(self):
        if self.action in [
            "registration_activity_metrics_by_month",
            "registration_activity_metrics_units_by_month",
        ]:
            return HIRLProjectRegistrationActivityMetricsByMonthFilter
        return HIRLProjectRegistrationFilter

    def get_queryset(self):
        queryset = super(HIRLProjectRegistrationViewSet, self).get_queryset()
        queryset = queryset.filter_by_user(user=self.request.user).annotate(
            projects_count=Count("projects", distinct=True)
        )
        return queryset.select_related(
            "builder_organization__shipping_geocode_response__geocode",
            "builder_organization__shipping_geocode__raw_city__county__climate_zone",
            "builder_organization__city",
            "builder_organization__city__county",
            "builder_organization__metro",
            "subdivision__place",
            "subdivision__community",
            "subdivision__community__geocode_response",
        ).prefetch_related(
            "builder_organization__sponsors",
            "developer_organization_contact__emails",
            "builder_organization_contact__emails__contact",
            "builder_organization_contact__phones",
            "builder_organization_contact__phones__contact",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return HIRLProjectRegistrationListSerializer
        if self.action == "create_single_family":
            return CreateSFHIRLProjectRegistrationSerializer
        if self.action == "create_multi_family":
            return CreateMFHIRLProjectRegistrationSerializer
        if self.action == "create_land_development":
            return CreateLandDevelopmentHIRLProjectRegistrationSerializer
        if self.action == "registration_activity_metrics_by_month":
            return HIRLProjectRegistrationActivityMetricsByMonthSerializer
        if self.action == "registration_activity_metrics_units_by_month":
            return HIRLProjectRegistrationActivityMetricsByUnitsMonthSerializer

        if self.request.user.is_authenticated and (
            self.request.user.is_superuser or self.request.user.is_customer_hirl_company_member()
        ):
            return HIRLProjectRegistrationSerializer
        return BasicHIRLProjectRegistrationSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        """
        When we delete registration delete all related objects, mf developments, etc.
        :param instance: HIRLProjectRegistration
        :return:
        """
        # In case of MF, we need to delete subdivision - and this will CASCADE delete -
        # registration/home/home_status/hirl_projects
        # For not approved registration we just need to delete only registration and this
        # will CASCADE delete projects
        if instance.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            subdivision = getattr(instance, "subdivision", None)
            # MF subdivision always contains only homes from one registration
            if subdivision:
                subdivision.delete()
            else:
                project = instance.projects.first()
                home_status = getattr(project, "home_status", None)
                if home_status:
                    home = home_status.home
                    # do not delete home if we have more than one homestatus
                    if home.homestatuses.count() < 2:
                        home.delete()

                instance.delete()
        else:
            for project in instance.projects.all():
                home_status = getattr(project, "home_status", None)
                if home_status:
                    home = home_status.home
                    subdivision = getattr(instance, "subdivision", None)
                    if subdivision:
                        # do not delete subdivision if we have more than one home in it
                        if subdivision.home_set.all().count() < 2:
                            subdivision.delete()

                    # do not delete home if we have more than one homestatus
                    if home.homestatuses.count() < 2:
                        home.delete()

                    project.home_status.delete()
                project.delete()
            instance.delete()

    @action(
        detail=False,
        methods=[
            "post",
        ],
    )
    def create_single_family(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            registration = serializer.save(
                project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
                registration_user=self.request.user,
            )
        hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

        for project in registration.projects.all():
            url = project.get_absolute_url()
            context = {
                "url": url,
                "verifier": registration.registration_user.get_full_name(),
                "project_address": f"{project.home_address_geocode.raw_address}",
                "project": project,
                "site": get_current_site(self.request),
            }
            SingleFamilyProjectCreatedHIRLNotificationMessage(url=url).send(
                company=hirl_company,
                context=context,
            )
            SingleFamilyProjectCreatedHIRLNotificationMessage(url=url).send(
                company=registration.registration_user.company,
                context=context,
            )

            if project.is_require_water_sense_certification:
                HIRLProjectBuilderIsNotWaterSensePartnerMessage().send(
                    company=registration.registration_user.company,
                    context={
                        "url": url,
                        "verifier": registration.registration_user,
                        "project_address": f"{project.home_address_geocode.raw_address}",
                        "project": project,
                        "site": get_current_site(self.request),
                    },
                )

            if project.is_appeals_project:
                IsAppealsHIRLProjectCreatedNotificationMessage().send(
                    company=hirl_company,
                    context={
                        "url": url,
                        "verifier": registration.registration_user,
                        "project_address": f"{project.home_address_geocode.raw_address}",
                        "h_number": project.h_number,
                        "project": project,
                        "site": get_current_site(self.request),
                    },
                )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(
        detail=False,
        methods=[
            "post",
        ],
    )
    def create_multi_family(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            registration = serializer.save(
                project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
                registration_user=self.request.user,
            )
        hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

        projects = registration.projects.all()

        if projects:
            for project in projects:
                url = project.get_absolute_url()
                context = {
                    "url": url,
                    "verifier": registration.registration_user,
                    "project_address": f"{project.home_address_geocode.raw_address}",
                    "project": project,
                    "site": get_current_site(self.request),
                }
                MultiFamilyProjectCreatedHIRLNotificationMessage(url=url).send(
                    company=hirl_company,
                    context=context,
                )
                MultiFamilyProjectCreatedHIRLNotificationMessage(url=url).send(
                    company=registration.registration_user.company,
                    context=context,
                )
                if project.is_require_water_sense_certification:
                    HIRLProjectBuilderIsNotWaterSensePartnerMessage(url=url).send(
                        company=registration.registration_user.company,
                        context={
                            "url": url,
                            "verifier": registration.registration_user,
                            "project_address": f"{project.home_address_geocode.raw_address}",
                            "project": project,
                            "site": get_current_site(self.request),
                        },
                    )

                if project.is_appeals_project:
                    IsAppealsHIRLProjectCreatedNotificationMessage(url).send(
                        company=hirl_company,
                        context={
                            "url": url,
                            "verifier": registration.registration_user,
                            "project_address": f"{project.home_address_geocode.raw_address}",
                            "h_number": project.h_number,
                            "project": project,
                            "site": get_current_site(self.request),
                        },
                    )
        else:
            HIRLProjectRegistrationCreatedMessage().send(
                company=hirl_company,
                context={
                    "url": registration.get_absolute_url(),
                    "verifier": registration.registration_user,
                    "registration_id": f"{registration.id}",
                },
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(
        detail=False,
        methods=[
            "post",
        ],
    )
    def create_land_development(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            registration = serializer.save(
                project_type=HIRLProjectRegistration.LAND_DEVELOPMENT_PROJECT_TYPE,
                registration_user=self.request.user,
                project_client=HIRLProjectRegistration.PROJECT_CLIENT_DEVELOPER,
                entity_responsible_for_payment=HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY,
            )
        hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

        for project in registration.projects.all():
            url = project.get_absolute_url()
            context = {
                "url": url,
                "verifier": registration.registration_user,
                "project_address": f"{project.home_address_geocode.raw_address}",
                "project": project,
                "site": get_current_site(self.request),
            }
            LandDevelopmentProjectCreatedHIRLNotificationMessage(url=url).send(
                company=hirl_company,
                context=context,
            )
            LandDevelopmentProjectCreatedHIRLNotificationMessage(url=url).send(
                company=registration.registration_user.company,
                context=context,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @swagger_auto_schema(request_body=no_body)
    @action(
        detail=True,
        methods=[
            "post",
        ],
    )
    def approve(self, request, *args, **kwargs):
        from axis.home.tasks import update_home_states

        registration = self.get_object()

        if registration.project_type in [
            HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            HIRLProjectRegistration.LAND_DEVELOPMENT_PROJECT_TYPE,
        ]:
            transition_method = getattr(registration, "active")
        else:
            transition_method = getattr(registration, "pending")

        if not can_proceed(transition_method):
            raise PermissionDenied("You cannot move to this state")

        if not has_transition_perm(transition_method, request.user):
            raise PermissionDenied("You do not have permission to move to this state")

        # send notifications
        try:
            company_responsible_for_payment = registration.get_company_responsible_for_payment()
        except ObjectDoesNotExist:
            company_responsible_for_payment = None

        try:
            project_client = registration.get_project_client_company()
        except ObjectDoesNotExist:
            project_client = None

        with transaction.atomic():
            transition_method()
            registration.save()

        projects = registration.projects.all().select_related("home_status").order_by("id")

        for project in projects:
            if project.home_status:
                update_home_states(eepprogramhomestatus_id=project.home_status.id)
            else:
                with transaction.atomic():
                    project.create_home_status()

                if company_responsible_for_payment:
                    HIRLResponsibleEntityForPaymentInvoiceItemGroupCreatedMessage(
                        url=project.home_status.get_absolute_url()
                    ).send(
                        company=company_responsible_for_payment,
                        context={
                            "url": f"/app/hi/invoice_item_groups/",
                            "project_url": project.home_status.get_absolute_url(),
                            "project_id": project.id,
                        },
                    )

        self._apply_mf_volume_discount(registration=registration)

        HIRLProjectRegistrationApprovedByHIRLCompanyMessage(
            url=registration.get_absolute_url()
        ).send(
            company=registration.registration_user.company,
            context={
                "url": registration.get_absolute_url(),
                "project_registration_id": f"{registration.id}",
            },
        )

        registration.refresh_from_db()

        if registration.project_type in [
            HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
        ]:
            # create invoice if project have require_rough_inspection = False
            rough_bypass_projects = projects.filter(is_require_rough_inspection=False)

            if rough_bypass_projects:
                hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()

                countersigned_ca_exists = False
                if company_responsible_for_payment and project_client:
                    countersigned_ca_exists = (
                        project_client.customer_hirl_enrolled_agreements.filter(
                            state=BuilderAgreement.COUNTERSIGNED
                        ).exists()
                    )
                if countersigned_ca_exists:
                    # invoice for common InvoiceItemGroups
                    invoice_item_groups = InvoiceItemGroup.objects.filter(
                        home_status__customer_hirl_project__in=rough_bypass_projects,
                        category=InvoiceItemGroup.ANY_CATEGORY,
                    )

                    with transaction.atomic():
                        invoice = Invoice.objects.create(
                            invoice_type=Invoice.HIRL_PROJECT_INVOICE_TYPE,
                            issuer=hirl_company,
                            customer=company_responsible_for_payment,
                            note="Automatically generated after approve, "
                            "because project rough bypass have been set",
                        )
                        for invoice_item_group in invoice_item_groups:
                            invoice_item_group.invoice = invoice
                            invoice_item_group.save()

                    url = invoice.get_absolute_url()

                    invoice_created_context = {
                        "invoice_detail_url": url,
                        "customer": company_responsible_for_payment,
                        "customer_url": company_responsible_for_payment.get_absolute_url(),
                        "invoice_item_groups": invoice_item_groups,
                        "invoice_id": invoice.id,
                    }
                    InvoiceCreatedNotificationMessage(url=url).send(
                        company=hirl_company, context=invoice_created_context
                    )
                    InvoiceCreatedNotificationMessage(url=url).send(
                        company=registration.registration_user.company,
                        user=registration.registration_user,
                        context=invoice_created_context,
                    )
                    InvoiceCreatedNotificationMessage(url=url).send(
                        company=company_responsible_for_payment,
                        context=invoice_created_context,
                    )

                    # separate invoice for Appeal InvoiceItemGroups
                    for project in rough_bypass_projects:
                        invoice_item_groups = InvoiceItemGroup.objects.filter(
                            home_status__customer_hirl_project=project,
                            category=InvoiceItemGroup.APPEALS_FEE_CATEGORY,
                        )
                        if invoice_item_groups:
                            with transaction.atomic():
                                invoice = Invoice.objects.create(
                                    invoice_type=Invoice.HIRL_PROJECT_INVOICE_TYPE,
                                    issuer=hirl_company,
                                    customer=company_responsible_for_payment,
                                    note="Automatically generated after approve for Appeals Fees, "
                                    "because project rough bypass have been set",
                                )
                                for invoice_item_group in invoice_item_groups:
                                    invoice_item_group.invoice = invoice
                                    invoice_item_group.save()

                            appeals_invoice_url = invoice.get_absolute_url()
                            appeals_invoice_created_context = {
                                "invoice_detail_url": appeals_invoice_url,
                                "customer": company_responsible_for_payment,
                                "customer_url": company_responsible_for_payment.get_absolute_url(),
                                "invoice_item_groups": invoice_item_groups,
                                "invoice_id": invoice.id,
                            }
                            InvoiceCreatedNotificationMessage(url=appeals_invoice_url).send(
                                company=hirl_company, context=appeals_invoice_created_context
                            )
                            InvoiceCreatedNotificationMessage(url=appeals_invoice_url).send(
                                company=registration.registration_user.company,
                                user=registration.registration_user,
                                context=appeals_invoice_created_context,
                            )
                            InvoiceCreatedNotificationMessage(url=appeals_invoice_url).send(
                                company=company_responsible_for_payment,
                                context=appeals_invoice_created_context,
                            )
                else:
                    company_responsible_for_payment_url = ""
                    company_responsible_for_payment_name = "Unknown"
                    if company_responsible_for_payment:
                        company_responsible_for_payment_url = (
                            company_responsible_for_payment.get_absolute_url()
                        )
                    # modify message content
                    msg = HIRLProjectInvoiceCantGeneratedWithoutClientAgreement(
                        url=registration.get_absolute_url()
                    )
                    msg.content = (
                        "An active NGBS Client Agreement cannot be found for company "
                        "<a href=\"{company_responsible_for_payment_url}\" target='_blank'>"
                        "{company_responsible_for_payment_name}</a>. "
                        "Registration <a href=\"{registration_url}\" target='_blank'>{registration_name}</a> "
                        "invoices cannot "
                        "be generated until a Client Agreement has been executed."
                    )
                    ctx = {
                        "company_responsible_for_payment_url": company_responsible_for_payment_url,
                        "company_responsible_for_payment_name": company_responsible_for_payment_name,
                        "registration_url": registration.get_absolute_url(),
                        "registration_name": registration.id,
                    }
                    msg.send(
                        company=hirl_company,
                        context=ctx,
                    )
                    msg.send(
                        company=registration.registration_user.company,
                        user=registration.registration_user,
                        context=ctx,
                    )
                    if project_client:
                        msg.send(
                            company=project_client,
                            context=ctx,
                        )
                    if company_responsible_for_payment:
                        msg.send(
                            company=company_responsible_for_payment,
                            context=ctx,
                        )
        # re-calculate billing state for projects,
        # because we are working in transaction and some signals
        # may be ignored or called with incorrect order
        for project in registration.projects.all():
            project.calculate_billing_state()

        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    def _apply_mf_volume_discount(self, registration: HIRLProjectRegistration):
        """
        This is how it should work:
        IF, when registering,  verifier registers: (MORE THAN 9 BUILDINGS)
        AND (all buildings are LESS THAN 4 STORIES), then apply discount rates for each building
        If there is a mix of buildings that are < 4 stories
        and > 4 stories, count ONLY the < 4-story buildings when
        determining if a discount should be applied.  For example,
        a registration with 8 < 4-story buildings and 4 > 4-story buildings
        should NOT qualify for a discount (none of the buildings get the discount rate)
        since > 10 buildings of < 4 stories must be registered.
        If more buildings are ADDED after the registration is approved,
        AXIS applies the standard rate (no discount)
        If buildings are REMOVED after the registration is approved, AXIS does
        NOT change certification fees – HI will change those manually

        :param registration: HIRLProjectRegistration
        """
        apply_mf_volume_discount = False

        projects_for_discount = (
            registration.projects.all()
            .filter(
                story_count__lt=4,
                is_accessory_structure=False,
                is_accessory_dwelling_unit=False,
                is_include_commercial_space=False,
            )
            .order_by("id")
        )
        projects_for_discount_count = projects_for_discount.count()

        if registration.project_type == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE:
            if projects_for_discount_count > 9:
                apply_mf_volume_discount = True

        for project in projects_for_discount:
            if apply_mf_volume_discount:
                with transaction.atomic():
                    if 9 < projects_for_discount_count < 20:
                        fee_name = "MF Volume Pricing Discount(10-19 buildings)"
                        fee_cost = (
                            customer_hirl_app.MF_VOLUME_DISCOUNT_9_BUILDINGS_FEE
                            - project.calculate_certification_fees_cost()
                        )
                    elif 19 < projects_for_discount_count < 50:
                        fee_name = "MF Volume Pricing Discount(20-49 buildings)"
                        fee_cost = (
                            customer_hirl_app.MF_VOLUME_DISCOUNT_20_BUILDINGS_FEE
                            - project.calculate_certification_fees_cost()
                        )
                    elif 49 < projects_for_discount_count:
                        fee_name = "MF Volume Pricing Discount(50+ buildings)"
                        fee_cost = (
                            customer_hirl_app.MF_VOLUME_DISCOUNT_50_BUILDINGS_FEE
                            - project.calculate_certification_fees_cost()
                        )
                    else:
                        fee_name = "No MF Volume discount"
                        fee_cost = 0

                    # do not show not negative discount fee
                    if fee_cost < 1:
                        invoice_group = project.home_status.invoiceitemgroup_set.filter(
                            category=InvoiceItemGroup.ANY_CATEGORY
                        ).first()
                        _ = InvoiceItem.objects.create(
                            group=invoice_group, name=fee_name, cost=fee_cost, protected=True
                        )
                    else:
                        logging.error(
                            f"{registration.eep_program} NGBS customer_hirl_certification_fee "
                            f"is not configured correctly. MF Volume pricing discount is greater than basic fee"
                        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "reason": openapi.Schema(
                    title="Reason", description="Reject reason", type=openapi.TYPE_STRING
                )
            },
        ),
        responses={200: BasicHIRLProjectSerializer},
    )
    @action(
        detail=True,
        methods=[
            "post",
        ],
    )
    def reject(self, request, *args, **kwargs):
        registration = self.get_object()
        transition_method = getattr(registration, "reject")

        if not can_proceed(transition_method):
            raise PermissionDenied("You cannot move to this state")

        if not has_transition_perm(transition_method, request.user):
            raise PermissionDenied("You do not have permission to move to this state")

        reason = self.request.data.get("reason")
        if not reason:
            reason = ""
        transition_method(reason=reason)
        registration.save()
        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=[
            "post",
        ],
    )
    def abandon(self, request, *args, **kwargs):
        registration = self.get_object()
        transition_method = registration.abandon

        if not can_proceed(transition_method):
            raise PermissionDenied("You cannot move to this state")

        if not has_transition_perm(transition_method, request.user):
            raise PermissionDenied("You do not have permission to move to this state")

        data_serializer = AbandonHIRLProjectRegistrationSerializer(
            instance=registration, data=self.request.data
        )
        data_serializer.is_valid(raise_exception=True)

        reason = data_serializer.validated_data["reason"]
        billing_state = data_serializer.validated_data["billing_state"]
        transition_method(user=request.user, billing_state=billing_state, reason=reason)
        registration.save()
        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def registration_activity_metrics_by_month(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        qs = (
            qs.annotate(month=Cast(TruncMonth("created_at"), DateField()))
            .values("month")
            .annotate(registrations_count=Count("id"))
            .values("month", "registrations_count")
            .order_by("-month")
        )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def registration_activity_metrics_units_by_month(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        qs = (
            qs.annotate(month=Cast(TruncMonth("created_at"), DateField()))
            .values("month")
            .annotate(registrations_count=Count("id"))
            .annotate(
                units_count=Coalesce(Sum("projects__number_of_units"), 0) + F("registrations_count")
            )
            .order_by("-month")
        )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class HIRLProjectRegistrationNestedHistoryViewSet(NestedHistoryViewSet):
    model = HIRLProjectRegistration.history.model
    queryset = model.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = HIRL_PROJECT_REGISTRATION_SEARCH_FIELDS
    ordering_fields = HIRL_PROJECT_REGISTRATION_ORDERING_FIELDS

    def filter_queryset_by_parents_lookups(self, queryset):
        """History Model do not support HashidAutoField"""
        parents_query_dict = self.get_parents_query_dict()
        if parents_query_dict:
            try:
                project_ids = HIRLProjectRegistration.objects.filter(
                    **parents_query_dict
                ).values_list("id", flat=True)
                return queryset.filter(id__in=project_ids)
            except ValueError:
                raise Http404
        else:
            return queryset
