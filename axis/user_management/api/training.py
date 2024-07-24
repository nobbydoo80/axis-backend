"""training.py: """


from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.filehandling.models import AsynchronousProcessedDocument
from axis.user_management.filters import TrainingFilter
from axis.user_management.models import Training
from axis.user_management.serializers import TrainingSerializer
from axis.user_management.tasks import training_report_task

__author__ = "Artem Hruzd"
__date__ = "12/11/2019 21:59"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingViewSet(viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    filterset_class = TrainingFilter

    @transaction.atomic
    @action(detail=False, methods=["get"])
    def create_approver_report(self, request):
        training_ids = list(self.filter_queryset(self.get_queryset()).values_list("id", flat=True))
        asynchronous_process_document = AsynchronousProcessedDocument(
            download=True, company=request.user.company
        )
        asynchronous_process_document.save()

        training_report_task.delay(
            asynchronous_process_document_id=asynchronous_process_document.id,
            training_ids=training_ids,
            user_id=request.user.id,
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
