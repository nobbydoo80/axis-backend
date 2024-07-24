__author__ = "Steven Klass"
__date__ = "3/2/12 3:16 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.urls import path, include

from .views import (
    BoundCompaniesAjaxView,
    CompanyContactListView,
    LegacyCompanyListRedirectView,
    LegacyCompanyCreateRedirectView,
    LegacyCompanyDetailRedirectView,
)

app_name = "company"

urlpatterns = [
    path(
        "<str:type>/",
        include(
            [
                path("", LegacyCompanyListRedirectView.as_view(), name="list"),
                path("add/", LegacyCompanyCreateRedirectView.as_view(), name="add"),
                path("<int:pk>/", LegacyCompanyDetailRedirectView.as_view(), name="view"),
            ]
        ),
    ),
    # Bound Companies
    path(
        "<str:app_label>/<str:model>/<int:pk>/",
        BoundCompaniesAjaxView.as_view(),
        name="bound",
    ),
    # Reports
    path("report/<str:type>/", CompanyContactListView.as_view(), name="contact_list"),
]
