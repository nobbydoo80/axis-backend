import logging

from rest_framework import viewsets

from axis.examine.api.restframework import ExamineViewSetAPIMixin
from .models import BuilderAgreement
from .serializers import BuilderAgreementSerializer

__author__ = "Michael Jeffrey"
__date__ = "5/13/15 1:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)


class BuilderAgreementViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = BuilderAgreement
    serializer_class = BuilderAgreementSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from axis.builder_agreement.views.examine import BuilderAgreementMachinery

        return BuilderAgreementMachinery
