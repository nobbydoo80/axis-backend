"""urls.py: Django builder_agreement"""

import logging

from django.urls import include, path

from axis.builder_agreement.views.views import (
    BuilderAgreementUpdateView,
    BuilderAgreementDeleteView,
    BuilderAgreementListView,
    BuilderAgreementDetailView,
    BuilderAgreementCreateView,
    BuilderAgreementStatusListView,
    AsynchronousProcessedDocumentCreateBuilderSudivisionReport,
)

__author__ = "Steven Klass"
__date__ = "3/2/12 1:33 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "builder_agreement"

urlpatterns = [
    path("", BuilderAgreementListView.as_view(), name="list"),
    path("add/", BuilderAgreementCreateView.as_view(), name="add"),
    path(
        "<int:pk>/",
        include(
            [
                path("", BuilderAgreementDetailView.as_view(), name="view"),
                path("update/", BuilderAgreementUpdateView.as_view(), name="update"),
                path("delete/", BuilderAgreementDeleteView.as_view(), name="delete"),
            ]
        ),
    ),
    path("report/agreement_status/", BuilderAgreementStatusListView.as_view(), name="status"),
    path(
        "report/agreement_status/export/",
        AsynchronousProcessedDocumentCreateBuilderSudivisionReport.as_view(),
        name="status_export",
    ),
]
