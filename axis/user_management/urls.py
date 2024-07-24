"""urls.py: user_management"""

from django.urls import path, include

from .views import (
    TrainingControlCenterNewListView,
    TrainingControlCenterApprovedListView,
    TrainingControlCenterRejectedListView,
    TrainingControlCenterExpiredListView,
    AccreditationControlCenterListView,
    CertificationMetricControlCenterListView,
)

__author__ = "Artem Hruzd"
__date__ = "10/29/2019 17:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

app_name = "user_management"

training_urls = (
    [
        path(
            "control_center/new/list/",
            TrainingControlCenterNewListView.as_view(),
            name="control_center_new_list",
        ),
        path(
            "control_center/approved/list/",
            TrainingControlCenterApprovedListView.as_view(),
            name="control_center_approved_list",
        ),
        path(
            "control_center/rejected/list/",
            TrainingControlCenterRejectedListView.as_view(),
            name="control_center_rejected_list",
        ),
        path(
            "control_center/expired/list/",
            TrainingControlCenterExpiredListView.as_view(),
            name="control_center_expired_list",
        ),
    ],
    "training",
)

accreditation_urls = (
    [
        path(
            "control_center/list/",
            AccreditationControlCenterListView.as_view(),
            name="control_center_list",
        ),
    ],
    "accreditation",
)

certification_metric_urls = (
    [
        path(
            "control_center/list/",
            CertificationMetricControlCenterListView.as_view(),
            name="control_center_list",
        ),
    ],
    "certification_metric",
)

urlpatterns = [
    path("training/", include(training_urls)),
    path("accreditation/", include(accreditation_urls)),
    path("certification_metric/", include(certification_metric_urls)),
]
