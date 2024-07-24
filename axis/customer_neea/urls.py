"""urls.py: Django customer_neea"""

import logging

from django.urls import path, include

from .api_v3.neea_calculator_v2 import NEEACalculatorV2View, NEEACalculatorV2DownloadView
from .api_v3.neea_calculator_v3 import NEEACalculatorV3View, NEEACalculatorV3DownloadView
from .models import LegacyNEEAHome, LegacyNEEAContact
from .views import (
    LegacyNEEAPartnerListView,
    LegacyNEEAPartnerDetailView,
    LegacyNEEAHomeListView,
    LegacyNEEAHomeDetailView,
    LegacyNEEAContactDetailView,
    HomeCertificationView,
    UtilityStatusView,
    AsynchronousProcessedDocumentCreateUtilityRawHomeStatusXLS,
    AsynchronousProcessedDocumentCreateUtilityCustomHomeStatusXLS,
    AsynchronousProcessedDocumentCreateUtilityBPAHomeStatusXLS,
)

__author__ = "Steven Klass"
__date__ = "9/5/12 5:30 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

urlpatterns = [
    path(
        "contact/<int:pk>/",
        LegacyNEEAContactDetailView.as_view(model=LegacyNEEAContact),
        name="neea_legacy_contact_view",
    ),
    path("partner/list/", LegacyNEEAPartnerListView.as_view(), name="neea_legacy_partners_list"),
    path(
        "partners/ajax/", LegacyNEEAPartnerListView.as_view(), name="neea_legacy_partners_ajax_list"
    ),
    path(
        "partner/<int:pk>/", LegacyNEEAPartnerDetailView.as_view(), name="neea_legacy_partner_view"
    ),
    path("home/list/", LegacyNEEAHomeListView.as_view(), name="neea_legacy_home_list"),
    path("home/ajax/", LegacyNEEAHomeListView.as_view(), name="neea_legacy_home_ajax_list"),
    path(
        "home/<int:pk>/",
        LegacyNEEAHomeDetailView.as_view(model=LegacyNEEAHome),
        name="neea_legacy_home_view",
    ),
    path(
        "report/certificate/<int:pk>/",
        HomeCertificationView.as_view(),
        name="neea_certificate_view",
    ),
    path("utility/report/", UtilityStatusView.as_view(), name="neea_utility_report"),
    path(
        "utility/generate/",
        include(
            [
                path(
                    "raw/",
                    AsynchronousProcessedDocumentCreateUtilityRawHomeStatusXLS.as_view(),
                    name="neea_utility_raw_document",
                ),
                path(
                    "custom/",
                    AsynchronousProcessedDocumentCreateUtilityCustomHomeStatusXLS.as_view(),
                    name="neea_utility_custom_document",
                ),
                path(
                    "bpa/",
                    AsynchronousProcessedDocumentCreateUtilityBPAHomeStatusXLS.as_view(),
                    name="neea_utility_bpa_document",
                ),
            ]
        ),
    ),
    path("calculator/v2/", NEEACalculatorV2View.as_view(), name="neea_calculator_v2"),
    path(
        "calculator/v2/download/",
        NEEACalculatorV2DownloadView.as_view(),
        name="neea_calculator_download_v2",
    ),
    path("calculator/v3/", NEEACalculatorV3View.as_view(), name="neea_calculator_v3"),
    path(
        "calculator/v3/download/",
        NEEACalculatorV3DownloadView.as_view(),
        name="neea_calculator_download_v3",
    ),
]
