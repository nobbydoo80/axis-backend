"""urls.py: Django """

import logging

from django.urls import path

from axis.customer_aps.models import APSHome
from axis.customer_aps.views.apshome_views import (
    APSHomeListView,
    APSHomeDetailView,
    APSHomeUpdateView,
    APSBulkHomeAsynchronousProcessedDocumentCreateView,
)
from axis.customer_aps.views.legacy_views import (
    APSLegacyBuilderListView,
    APSLegacyBuilderDetailView,
    APSLegacySubdivisionListView,
    APSLegacySubdivisionDetailView,
    APSLegacyHomeListView,
    APSLegacyHomeDetailView,
)

__author__ = "Steven Klass"
__date__ = "1/20/12 8:24 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

urlpatterns = [
    path("meterset/", APSHomeListView.as_view(model=APSHome), name="aps_homes_list_view"),
    path(
        "meterset/<int:pk>/", APSHomeDetailView.as_view(model=APSHome), name="aps_homes_detail_view"
    ),
    path("meterset/update/<int:pk>/", APSHomeUpdateView.as_view(), name="aps_homes_update_view"),
    path(
        "meterset/upload/",
        APSBulkHomeAsynchronousProcessedDocumentCreateView.as_view(),
        name="aps_bulk_homes_add",
    ),
    path("meterset/list/ajax/", APSHomeListView.as_view(), name="aps_homes_ajax_list"),
    path(
        "legacy/builder/", APSLegacyBuilderListView.as_view(), name="aps_legacy_builder_list_view"
    ),
    path(
        "legacy/builder/list/ajax/",
        APSLegacyBuilderListView.as_view(),
        name="aps_legacy_builder_ajax_list",
    ),
    path(
        "legacy/builder/<int:pk>/",
        APSLegacyBuilderDetailView.as_view(),
        name="aps_legacy_builder_detail_view",
    ),
    path(
        "legacy/subdivision/",
        APSLegacySubdivisionListView.as_view(),
        name="aps_legacy_subdivision_list_view",
    ),
    path(
        "legacy/subdivision/list/ajax/",
        APSLegacySubdivisionListView.as_view(),
        name="aps_legacy_subdivision_ajax_list",
    ),
    path(
        "legacy/subdivision/<int:pk>/",
        APSLegacySubdivisionDetailView.as_view(),
        name="aps_legacy_subdivision_detail_view",
    ),
    path(
        "legacy/subdivision/<int:subdivision_id>/home/list/ajax/",
        APSLegacyHomeListView.as_view(),
        name="aps_legacy_subdivision_homes_ajax_list",
    ),
    path("legacy/home/", APSLegacyHomeListView.as_view(), name="aps_legacy_home_list_view"),
    path(
        "legacy/home/list/ajax/", APSLegacyHomeListView.as_view(), name="aps_legacy_home_ajax_list"
    ),
    path(
        "legacy/home/<int:pk>/",
        APSLegacyHomeDetailView.as_view(),
        name="aps_legacy_home_detail_view",
    ),
]
