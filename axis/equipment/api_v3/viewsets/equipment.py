__author__ = "Artem Hruzd"
__date__ = "04/03/2020 19:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.company.messages import EquipmentCreatedSponsorCompanyMessage
from axis.company.serializers import CompanyEquipmentSerializer
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter
from axis.equipment.api_v3 import EQUIPMENT_SEARCH_FIELDS, EQUIPMENT_ORDERING_FIELDS
from axis.equipment.api_v3.filters import EquipmentFilter
from axis.equipment.api_v3.permissions import CopyEquipmentPermissionPermission
from axis.equipment.api_v3.serializers import EquipmentSerializer
from axis.equipment.models import Equipment, EquipmentSponsorStatus
from axis.equipment.states import EquipmentSponsorStatusStates
from django.apps import apps


equipment_app = apps.get_app_config("equipment")


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    Represents Equipment endpoint
    retrieve:
        Return a Equipment instance.
    list:
        Return all Equipment's available for user
    create:
        Create a new Equipment.
    partial_update:
        Update one or more fields on an existing Equipment.
    update:
        Update Equipment.
    delete:
        Delete Equipment.
    """

    model = Equipment
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filterset_class = EquipmentFilter
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = EQUIPMENT_SEARCH_FIELDS
    ordering_fields = EQUIPMENT_ORDERING_FIELDS
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        for equipment_sponsor_status in serializer.instance.equipmentsponsorstatus_set.all():
            self._send_new_equipment_created_message(
                equipment=serializer.instance, sponsor_company=equipment_sponsor_status.company
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    @action(methods=["post"], detail=True, permission_classes=(CopyEquipmentPermissionPermission,))
    def copy_expired_equipment(self, request, pk=None):
        """
        Allows user to copy expired equipment and reset all EquipmentSponsorStatuses state to
        NEW
        :param request: request object
        :param pk: equipment object pk
        :return: equipment object copy
        """
        equipment = self.get_object()

        if not equipment.equipmentsponsorstatus_set.filter(
            state=EquipmentSponsorStatusStates.EXPIRED
        ).first():
            return Response(
                "Not expired equipment cannot be copy", status=status.HTTP_400_BAD_REQUEST
            )

        if equipment.expired_equipment:
            return Response("Equipment already copied", status=status.HTTP_400_BAD_REQUEST)

        equipment_copy = self.get_object()
        equipment_copy.id = None
        equipment_copy.pk = None
        equipment_copy.updated_at = timezone.now()
        equipment_copy.created = timezone.now()
        equipment_copy.save()

        sponsor_companies = []

        for equipment_sponsor_status in equipment.equipmentsponsorstatus_set.all():
            equipment_sponsor_status_copy = EquipmentSponsorStatus(
                equipment=equipment_copy, company=equipment_sponsor_status.company
            )
            equipment_sponsor_status_copy.save()

            sponsor_companies.append(equipment_sponsor_status.company)

        equipment.expired_equipment = equipment_copy
        equipment.save()

        for sponsor_company in sponsor_companies:
            self._send_new_equipment_created_message(
                equipment=equipment_copy, sponsor_company=sponsor_company
            )

        return Response(
            CompanyEquipmentSerializer(equipment_copy, context={"request": request}).data
        )

    def _send_new_equipment_created_message(self, equipment, sponsor_company):
        EquipmentCreatedSponsorCompanyMessage(url=equipment.owner_company.get_absolute_url()).send(
            company=sponsor_company,
            context={
                "owner_company": equipment.owner_company,
                "url": equipment.owner_company.get_absolute_url(),
                "equipment": equipment,
            },
        )


class NestedEquipmentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    Represents Equipment endpoint
    retrieve:
        Return a Equipment instance.
    list:
        Return all Equipment's available for user
    create:
        Create a new Equipment.
    partial_update:
        Update one or more fields on an existing Equipment.
    update:
        Update Equipment.
    delete:
        Delete Equipment.
    """

    model = Equipment
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filterset_class = EquipmentFilter
    filter_backends = [DjangoFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = EQUIPMENT_SEARCH_FIELDS
    ordering_fields = EQUIPMENT_ORDERING_FIELDS
