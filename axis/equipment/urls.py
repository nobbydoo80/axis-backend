"""urls.py: equipment"""


from django.urls import path

from .views import (
    EquipmentControlCenterNewListView,
    EquipmentControlCenterActiveListView,
    EquipmentControlCenterRejectedListView,
    EquipmentControlCenterExpiredListView,
)

__author__ = "Artem Hruzd"
__date__ = "10/29/2019 17:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


app_name = "equipment"

urlpatterns = [
    path(
        "control_center/new/list/",
        EquipmentControlCenterNewListView.as_view(),
        name="control_center_new_list",
    ),
    path(
        "control_center/active/list/",
        EquipmentControlCenterActiveListView.as_view(),
        name="control_center_active_list",
    ),
    path(
        "control_center/rejected/list/",
        EquipmentControlCenterRejectedListView.as_view(),
        name="control_center_rejected_list",
    ),
    path(
        "control_center/expired/list/",
        EquipmentControlCenterExpiredListView.as_view(),
        name="control_center_expired_list",
    ),
]
