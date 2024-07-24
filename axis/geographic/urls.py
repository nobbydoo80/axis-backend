"""views.py: Django core urls"""


from django.urls import path, include

from .views import CityCreateView, CityDetailView, CityUpdateView, CityDeleteView, StaticView

__author__ = "Rajesh Pappula"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Rajesh Pappula", "Autumn Valenta"]

urlpatterns = [
    path(
        "city/",
        include(
            (
                [
                    path("add/", CityCreateView.as_view(), name="add"),
                    path(
                        "<int:pk>/",
                        include(
                            [
                                path("", CityDetailView.as_view(), name="view"),
                                path("update/", CityUpdateView.as_view(), name="update"),
                                path("delete/", CityDeleteView.as_view(), name="delete"),
                            ]
                        ),
                    ),
                ],
                "city",
            )
        ),
    ),
    # Superuser-only utility views that go direct to equivalently named template
    path("<str:page>.html)", StaticView.as_view()),
]
