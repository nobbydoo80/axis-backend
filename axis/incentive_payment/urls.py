"""urls.py: Django incentive_payment"""


import logging

from django.urls import path, include

from .views import (
    IncentiveDistributionListView,
    IncentiveDistributionDetailView,
    IncentiveDistributionUpdateView,
    IncentiveDistributionCreateView,
    IncentiveDistributionDeleteView,
    IPPItemDistributionListDetailPrintView,
    IncentiveDistributionDetailPrintView,
    IncentivePaymentPendingAnnotationList,
    IncentivePaymentRejectedAnnotationList,
    IncentiveDistributionIPPItems,
    IncentivePaymentPendingList,
)


from axis.incentive_payment.views import (
    ControlCenterView,
    AjaxPendingForm,
    AjaxNewForm,
    IncentivePaymentPendingDatatable,
    IncentivePaymentRejectedDatatable,
    IncentiveDistributionDatatable,
)

__author__ = "Steven Klass"
__date__ = "3/16/12 1:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "incentive_payment"

urlpatterns = [
    path("control_center/", ControlCenterView.as_view(), name="control_center"),
    path(
        "control_center/datatable/pending",
        IncentivePaymentPendingDatatable.as_view(),
        name="datatable_pending",
    ),
    path(
        "control_center/datatable/rejected",
        IncentivePaymentRejectedDatatable.as_view(),
        name="datatable_rejected",
    ),
    path(
        "control_center/datatable/incentives",
        IncentiveDistributionDatatable.as_view(),
        name="datatable_incentives",
    ),
    path("control_center/pending_form/", AjaxPendingForm.as_view(), name="pending_form"),
    path("control_center/new_form/", AjaxNewForm.as_view(), name="new_form"),
    path(
        "control_center/datatable/_pending_basic",
        IncentivePaymentPendingList.as_view(),
        name="datatable_pending_basic",
    ),
    path("", IncentiveDistributionListView.as_view(), name="list"),
    path("pending/", IncentivePaymentPendingAnnotationList.as_view(), name="pending"),
    path(
        "returned/",
        IncentivePaymentPendingAnnotationList.as_view(),
        kwargs={"state": "ipp_failed_restart"},
        name="returned",
    ),
    path("failure/", IncentivePaymentRejectedAnnotationList.as_view(), name="failures"),
    path("add/", IncentiveDistributionCreateView.as_view(), name="add"),
    path(
        "<int:pk>/",
        include(
            [
                path("", IncentiveDistributionDetailView.as_view(), name="view"),
                path("update/", IncentiveDistributionUpdateView.as_view(), name="update"),
                path("delete/", IncentiveDistributionDeleteView.as_view(), name="delete"),
                path("items/list/", IncentiveDistributionIPPItems.as_view(), name="ipp_items"),
                path("print/", IncentiveDistributionDetailPrintView.as_view(), name="print"),
                path(
                    "print/detail/",
                    IPPItemDistributionListDetailPrintView.as_view(),
                    name="print_detail",
                ),
            ]
        ),
    ),
]
