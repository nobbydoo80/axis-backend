"""views.py: Django geographic"""


import logging

from django.http import Http404
from django.template import TemplateDoesNotExist
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    AxisDetailView,
    AxisUpdateView,
    AxisCreateView,
    AxisDeleteView,
)
from .models import City
from .forms import CityForm

__author__ = "Steven Klass"
__date__ = "3/2/12 8:59 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CityMixin(object):
    model = City


class CityDetailView(AuthenticationMixin, CityMixin, AxisDetailView):
    permission_required = "geographic.view_city"


class CityUpdateView(AuthenticationMixin, CityMixin, AxisUpdateView):
    permission_required = "geographic.change_city"
    form_class = CityForm

    def has_permission(self):
        return self.get_object().can_be_edited(self.request.user)


class CityCreateView(AuthenticationMixin, CityMixin, AxisCreateView):
    permission_required = "geographic.add_city"
    form_class = CityForm
    initial = {
        "land_area_meters": 0,
        "water_area_meters": 0,
        "latitude": 0,
        "longitude": 0,
    }

    show_cancel_button = False


class CityDeleteView(AuthenticationMixin, CityMixin, AxisDeleteView):
    permission_required = "geographic.delete_city"
    success_url = reverse_lazy("home")

    def has_permission(self):
        return self.get_object().can_be_deleted(self.request.user)


class StaticView(AuthenticationMixin, TemplateView):
    permission_required = "geographic.view_place"

    def has_permission(self):
        return self.request.user.is_superuser

    def get(self, request, page, *args, **kwargs):
        self.template_name = page
        response = super(StaticView, self).get(request, *args, **kwargs)
        try:
            return response.render()
        except TemplateDoesNotExist:
            raise Http404()
