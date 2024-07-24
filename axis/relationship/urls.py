"""urls.py: Django relationship"""


import logging

from django.urls import include, path

from axis.relationship.views import (
    RelationshipCreateView,
    RelationshipDeleteView,
    RelationshipListView,
    RelationshipSideBarListView,
    AssociationDashboardView,
)

__author__ = "Steven Klass"
__date__ = "8/21/12 8:35 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "relationship"

urlpatterns = [
    path(
        "<str:app_label>/<str:model>/",
        include(
            [
                # These are your 'normal' urls
                path("add/", RelationshipCreateView.as_view(), name="add"),
                path("delete/", RelationshipDeleteView.as_view(), name="delete"),
                path(
                    "<int:object_id>/",
                    include(
                        [
                            path("", RelationshipListView.as_view(), name="list"),
                            path(
                                "ajax/", RelationshipSideBarListView.as_view(), name="sidebar_ajax"
                            ),
                            path("add/", RelationshipCreateView.as_view(), name="add_id"),
                            path("remove/", RelationshipDeleteView.as_view(), name="remove_id"),
                            path(
                                "reject/",
                                RelationshipDeleteView.as_view(),
                                kwargs={"reject": True},
                                name="reject_id",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path(
        "delete/<int:pk>/",
        RelationshipDeleteView.as_view(),
        kwargs={"delete": True},
        name="delete_id",
    ),
    # Associations
    path("shared/", AssociationDashboardView.as_view(), name="associations"),
]
