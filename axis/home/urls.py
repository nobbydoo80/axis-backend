"""urls.py: Django home"""


import logging

from django.urls import path, include

from . import views

__author__ = "Steven Klass"
__date__ = "3/5/12 12:56 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "home"

# These core patterns exclude url routes for home view/create/update.
urlpatterns = [
    path("", views.HomeListView.as_view(), name="list"),
    path("add/", views.HomeExamineView.as_view(create_new=True), name="add"),
    path(
        "<int:pk>/",
        include(
            [
                path("", views.HomeExamineView.as_view(), name="view"),
                # These urls are using pk as EEPProgramHomeStatus.pk, not Home.pk
                path("certify/", views.CertifyEEPHomeStatView.as_view(), name="certify"),
                path("update_state/", views.SetStateView.as_view(), name="set_state"),
                path("update_stats/", views.UpdateStatsView.as_view(), name="update_stats"),
                path(
                    "customer_hi/",
                    include(
                        [
                            path(
                                "bypass_rough_qa/",
                                views.BypassRoughQAActionView.as_view(),
                                name="bypass_rough_qa",
                            ),
                        ]
                    ),
                    name="customer_hi",
                ),
                path("home-photo/", views.HomePhotoView.as_view(), name="home_photo"),
                path(
                    "home-photo-detail/<int:photo_pk>/",
                    views.HomePhotoDetailView.as_view(),
                    name="home_photo_detail",
                ),
            ]
        ),
    ),
    path(
        "report/",
        include(
            (
                [
                    path(
                        "provider/",
                        views.ProviderDashboardView.as_view(),
                        name="provider_dashboard",
                    ),
                    path("status/", views.HomeStatusView.as_view(), name="status"),
                    path("legacy_status/", views.HomeStatusView.as_view(), name="legacy_status"),
                    path(
                        "built-green/wa/<int:pk>/",
                        views.BuiltGreenWACertificateDownload.as_view(),
                        name="built_green_wa",
                    ),
                    path(
                        "stats/generate/",
                        views.AsynchronousProcessedDocumentCreateHomeStatusXLS.as_view(),
                        name="stats_document",
                    ),
                    path("certificate/", views.HomeCertificateForm.as_view(), name="certificate"),
                    path(
                        "checklist/bulk/",
                        views.BulkHomeProgramReportCreateView.as_view(),
                        name="bulk_checklist_reports",
                    ),
                    path("checklist/", views.HomeChecklistreport.as_view(), name="checklist"),
                    path(
                        "checklist/<int:home_status>/",
                        views.HomeChecklistreport.as_view(),
                        name="checklist",
                    ),
                    path(
                        "energystar/",
                        views.HomeEnergyStarLabelForm.as_view(),
                        name="energy_star_certificate",
                    ),
                    path(
                        "customer_hi/scoring_path/<int:pk>/",
                        views.CustomerHIRLCertificateDownload.as_view(),
                        name="customer_hirl_scoring_path_certificate",
                    ),
                    path(
                        "customer_hi/water_sense/<int:pk>/",
                        views.CustomerHIRLWaterSenseCertificateDownload.as_view(),
                        name="customer_hirl_water_sense_certificate",
                    ),
                ],
                "report",
            )
        ),
    ),
    path(
        "certified/",
        views.EEPProgramHomeStatusListView.as_view(),
        kwargs={"certified_only": True},
        name="certified",
    ),
    path("upload/", views.BulkHomeAsynchronousProcessedDocumentCreateView.as_view(), name="upload"),
    path(
        "single_upload/",
        views.HomeAsynchronousProcessedDocumentCreateView.as_view(),
        name="single_upload",
    ),
    path("download/single/", views.HomeReportView.as_view(), name="download_single"),
    path(
        "download/single/<int:home_status>/",
        views.HomeReportView.as_view(),
        name="download_single_homestatus",
    ),
    path(
        "download/single/home/<int:home>/",
        views.HomeReportView.as_view(),
        name="download_single_home",
    ),
    path(
        "download/single/program/<int:eep_program>/",
        views.HomeReportView.as_view(),
        name="download_single_program",
    ),
    # These urls are using EEPProgramHomeStatus.pk
    path("status/<int:pk>/", views.HomeRedirectView.as_view(permanent=False), name="stat_redirect"),
    path(
        "home_status/<int:pk>/",
        views.HomeRedirectView.as_view(permanent=False),
        name="stat_redirect",
    ),
]
