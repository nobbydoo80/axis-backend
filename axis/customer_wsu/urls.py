"""urls.py: """

from django.urls import path

from axis.customer_wsu.views import HERSBrochureDownloadView

__author__ = "Artem Hruzd"
__date__ = "11/25/2020 23:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

app_name = "customer_wsu"

urlpatterns = [
    path("hers_brochure/<int:pk>/", HERSBrochureDownloadView.as_view(), name="hers_brochure"),
]
