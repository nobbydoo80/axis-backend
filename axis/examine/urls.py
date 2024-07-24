from django.urls import re_path

from .views import TemplatePreprocessorView

__author__ = "Autumn Valenta"
__date__ = "10-17-14  5:58 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

app_name = "examine"

urlpatterns = [
    re_path(
        r"^(?P<template>%s.*)$" % (TemplatePreprocessorView.template_root),
        TemplatePreprocessorView.as_view(),
        name="template",
    ),
]
