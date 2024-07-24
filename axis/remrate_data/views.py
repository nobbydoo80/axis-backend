"""views.py: Django remrate_data"""


import logging

from django.urls import reverse_lazy

from axis.core.views.generic import AxisDeleteView
from axis.core.mixins import AuthenticationMixin
from .models import Simulation

__author__ = "Steven Klass"
__date__ = "3/8/13 2:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RemRateDataDeleteView(AuthenticationMixin, AxisDeleteView):
    model = Simulation
    permission_required = "remrate_data.delete_simulation"
    success_url = reverse_lazy("floorplan:input:remrate")

    def get_queryset(self):
        return Simulation.objects.filter_by_user(user=self.request.user)

    def has_permission(self):
        return self.get_object().can_be_deleted(self.request.user)
