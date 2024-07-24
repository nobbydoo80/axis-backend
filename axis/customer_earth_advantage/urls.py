import logging

from django.apps import apps
from django.urls import path, include

__author__ = "Michael Jeffrey"
__date__ = "8/9/17 2:51 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_earth_advantage")

app_name = "earth_advantage"
urlpatterns = [
    path("", include("{app_name}.appraisal_addendum.urls".format(app_name=app.name))),
]
