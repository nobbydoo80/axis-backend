"""urls.py: Django search"""
import sys

from django.urls import path
import appsearch

from .views import SearchView

__author__ = "Autumn Valenta"
__date__ = "2012/10/12 3:22:30 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

try:
    appsearch.autodiscover()
except ImportError:
    if "test" not in sys.argv:
        raise

app_name = "search"

urlpatterns = [
    path("", SearchView.as_view(), name="search"),
]
