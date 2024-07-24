import logging

from django.urls import path, include

from . import views

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "certification"

urlpatterns = [
    path(
        "status/",
        include(
            (
                [
                    path("<str:type>/", views.WorkflowStatusListView.as_view(), name="list"),
                ],
                app_name,
            ),
            namespace="status",
        ),
    ),
    path(
        "",
        include(
            (
                [
                    path("<str:type>/", views.CertifiableObjectListView.as_view(), name="list"),
                    path(
                        "<str:type>/add/",
                        views.CertifiableObjectExamineView.as_view(create_new=True),
                        name="add",
                    ),
                    path(
                        "<str:type>/<int:pk>/",
                        views.CertifiableObjectExamineView.as_view(),
                        name="view",
                    ),
                    path(
                        "<str:type>/generate/<int:parent_id>/<int:workflow_id>/",
                        views.CertifiableObjectGenerateView.as_view(),
                        name="generate",
                    ),
                ],
                app_name,
            ),
            namespace="object",
        ),
    ),
]
