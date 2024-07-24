"""urls.py: Django scheduling"""

__author__ = "Steven Klass"
__date__ = "11/22/11 4:59 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


from django.urls import path

from .views import (
    ConstructionStageListView,
    ConstructionStageDetailView,
    ConstructionStageCreateView,
    ConstructionStageUpdateView,
    ConstructionStageDeleteView,
)

app_name = "scheduling"


urlpatterns = [
    path(
        "construction_stages/", ConstructionStageListView.as_view(), name="construction_stage_list"
    ),
    path(
        "construction_stage/<int:pk>/",
        ConstructionStageDetailView.as_view(),
        name="construction_stage_detail",
    ),
    path(
        "construction_stage/create/",
        ConstructionStageCreateView.as_view(),
        name="construction_stage_create",
    ),
    path(
        "construction_stage/update/<int:pk>/",
        ConstructionStageUpdateView.as_view(),
        name="construction_stage_update",
    ),
    path(
        "construction_stage/delete/<int:pk>/",
        ConstructionStageDeleteView.as_view(),
        name="construction_stage_delete",
    ),
]
