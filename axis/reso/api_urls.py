"""api_urls.py: Django reso"""


import logging

from django.urls import path
from rest_framework import renderers
from rest_framework.routers import DefaultRouter

from .api import ServiceViewSet, DataServicesViewSet, RESOAtomRenderer, ResoHomeViewSet

__author__ = "Steven Klass"
__date__ = "8/2/17 11:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

base_renders = (RESOAtomRenderer, renderers.BrowsableAPIRenderer)
json_renders = (RESOAtomRenderer, renderers.BrowsableAPIRenderer, renderers.JSONRenderer)

app_name = "reso"

urlpatterns = [
    path(
        "OData/",
        ServiceViewSet.as_view({"get": "retrieve"}, renderer_classes=base_renders),
        name="odata",
    ),
    # So this should serve up our EDMX as this is a single system per Appendix 2 Section 3
    path(
        "OData/$metadata",
        ServiceViewSet.as_view({"get": "metadata"}, renderer_classes=json_renders),
        name="odata_meta",
    ),
    path(
        "OData/DataSystem/",
        DataServicesViewSet.as_view({"get": "retrieve"}, renderer_classes=json_renders),
        name="reso_metadata",
    ),
    path(
        "OData/DataSystem/$metadata",
        DataServicesViewSet.as_view({"get": "metadata"}),
        name="reso_datasystems_metadata",
    ),
    # Because we have to define our systems, the metadata will return the same as a
    path("OData/DataSystem('RESO_MLS')", DataServicesViewSet.as_view({"get": "reso"})),
    path(
        "OData/DataSystem('RESO_MLS')/$metadata",
        DataServicesViewSet.as_view({"get": "reso_metadata"}),
    ),
]

router = DefaultRouter()
router.register(r"^OData/Listing", ResoHomeViewSet, basename="reso_listing")
urlpatterns += router.urls
