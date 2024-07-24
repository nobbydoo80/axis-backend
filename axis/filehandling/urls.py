"""urls.py: Django filehandling"""

from django.urls import path

from .views import (
    AsynchronousProcessedDocumentCreateView,
    AsynchronousProcessedDocumentDetailView,
    AsynchronousProcessedDocumentListView,
    TestAsynchronousProcessedDocument,
)

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

urlpatterns = [
    path("document/", AsynchronousProcessedDocumentListView.as_view(), name="async_document_list"),
    path(
        "document/ajax/",
        AsynchronousProcessedDocumentListView.as_view(),
        name="async_document_ajax_list",
    ),
    path(
        "document/create/",
        AsynchronousProcessedDocumentCreateView.as_view(),
        name="async_document_add",
    ),
    path(
        "document/<int:pk>/",
        AsynchronousProcessedDocumentDetailView.as_view(),
        name="async_document_detail",
    ),
    path(
        "document/<int:pk>/download/",
        AsynchronousProcessedDocumentDetailView.as_view(auto_download=True),
        name="async_document_download",
    ),
    path(
        "document/stat/<int:pk>/",
        AsynchronousProcessedDocumentDetailView.as_view(),
        name="async_document_ajax_status",
    ),
    path(
        "doc/test/create/", TestAsynchronousProcessedDocument.as_view(), name="async_document_test"
    ),
]
