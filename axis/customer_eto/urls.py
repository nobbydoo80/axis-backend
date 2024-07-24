"""urls.py: Django customer_eto"""


import logging

from django.urls import path

from .views import views

__author__ = "Steven Klass"
__date__ = "9/4/13 10:20 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "eto"

urlpatterns = [
    path("eps/", views.EPSReportView.as_view(), name="download"),
    path("eps/<int:home_status>/", views.EPSReportView.as_view(), name="download"),
    path("calculator/", views.EPSCalculatorFormView.as_view(), name="calculator"),
    path("calculator/<str:mode>/", views.EPSCalculatorFormView.as_view(), name="calculator"),
    path(
        "basic_calculator/<str:mode>/",
        views.EPSCalculatorBasicFormView.as_view(),
        name="basic_calculator",
    ),
    path(
        "payment_adjust/<int:home_status>/",
        views.PaymentAdjustView.as_view(),
        name="payment_adjust",
    ),
    path(
        "upload/washington_code_credit/",
        views.WashingtonCodeCreditProcessedDocumentCreateView.as_view(),
        name="wcc-upload",
    ),
]
