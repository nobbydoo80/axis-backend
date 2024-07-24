"""urls.py: Django checklist"""

from django.urls import path, include

from .views import AsynchronousChecklistCreateView, BulkChecklistDownload, BulkChecklistUpload

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

app_name = "checklist"

urlpatterns = [
    path(
        "checklist/",
        include(
            [
                path(
                    "add/upload/",
                    AsynchronousChecklistCreateView.as_view(),
                    name="checklist_upload",
                ),
            ]
        ),
    ),
    path(
        "bulk/",
        include(
            [
                path(
                    "download/<int:pk>/",
                    include(
                        [
                            path(
                                "", BulkChecklistDownload.as_view(), name="bulk_checklist_download"
                            ),
                            path(
                                "breakout/",
                                BulkChecklistDownload.as_view(breakout_choices=True),
                                name="bulk_checklist_download_breakout",
                            ),
                        ]
                    ),
                ),
                path("upload/", BulkChecklistUpload.as_view(), name="bulk_checklist_upload"),
            ]
        ),
    ),
]
