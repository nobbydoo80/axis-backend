"""accreditation.py: """

__author__ = "Artem Hruzd"
__date__ = "12/11/2019 21:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.filters import AccreditationFilter
from axis.user_management.models import Accreditation
from axis.user_management.serializers import (
    AccreditationSerializer,
    AccreditationChangeStateSerializer,
)
from axis.user_management.tasks import (
    accreditation_report_task,
    customer_hirl_accreditation_report_task,
)


class AccreditationViewSet(viewsets.ModelViewSet):
    queryset = Accreditation.objects.all()
    serializer_class = AccreditationSerializer
    filterset_class = AccreditationFilter

    @transaction.atomic
    @action(detail=False, methods=["get"])
    def create_approver_report(self, request):
        accreditation_ids = list(
            self.filter_queryset(self.get_queryset()).values_list("id", flat=True)
        )
        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=request.user.company
        )
        asynchronous_process_document.download = True
        asynchronous_process_document.company = self.request.user.company
        asynchronous_process_document.save()

        accreditation_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            accreditation_ids=accreditation_ids,
            user_id=self.request.user.id,
        )
        return Response(
            {
                "asynchronous_process_document_id": asynchronous_process_document.id,
                "asynchronous_process_document_url": request.build_absolute_uri(
                    asynchronous_process_document.get_absolute_url()
                ),
            },
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    @action(detail=False, methods=["get"])
    def create_customer_hirl_report(self, request):
        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=request.user.company
        )
        asynchronous_process_document.download = True
        asynchronous_process_document.company = self.request.user.company
        asynchronous_process_document.save()

        customer_hirl_accreditation_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            user_id=self.request.user.id,
        )
        return Response(
            {
                "asynchronous_process_document_id": asynchronous_process_document.id,
                "asynchronous_process_document_url": request.build_absolute_uri(
                    asynchronous_process_document.get_absolute_url()
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["patch"], serializer_class=AccreditationChangeStateSerializer)
    def change_state(self, request):
        """
        Change state for list of `accreditation_ids`
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            accreditations = Accreditation.objects.filter(
                id__in=serializer.validated_data["accreditation_ids"]
            )
            if not request.user.is_superuser:
                accreditations = accreditations.filter(approver__company=request.user.company)

            for accreditation in accreditations:
                accreditation.state = serializer.validated_data["new_state"]
                if not request.user.is_superuser or (
                    request.user.is_superuser
                    and request.user.company == accreditation.approver.company
                ):
                    accreditation.approver = request.user
                accreditation.save()

            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
