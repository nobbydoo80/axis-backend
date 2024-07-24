"""Urls."""

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.apps import apps
from django.urls import path, include

app_name = "hirl"
app = apps.get_app_config("customer_hirl")


urlpatterns = [
    path("", include("{app_name}.builder_agreements.urls".format(app_name=app.name))),
    path("", include("{app_name}.verifier_agreements.urls".format(app_name=app.name))),
]
