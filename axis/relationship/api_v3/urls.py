"""router.py: """


from django.conf.urls import url

from rest_framework import routers

from .views import RelationshipViewSet

__author__ = "Artem Hruzd"
__date__ = "01/03/2020 21:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


relationship_router = routers.DefaultRouter()
relationship_router.register(
    r"relationships/(?P<content_type>\d+)/(?P<object_id>\d+)", RelationshipViewSet
)

app_name = "relationship"
urlpatterns = [] + relationship_router.urls
