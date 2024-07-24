"""control_center_new_list.py: """


from .control_center_base_list import EquipmentControlCenterBaseListView
from ..states import EquipmentSponsorStatusStates

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentControlCenterActiveListView(EquipmentControlCenterBaseListView):
    equipment_state = EquipmentSponsorStatusStates.ACTIVE

    def get_context_data(self, **kwargs):
        context = super(EquipmentControlCenterActiveListView, self).get_context_data(**kwargs)
        context["equipment_sponsor_status_state_choices"] = [
            (EquipmentSponsorStatusStates.REJECTED, "Rejected"),
            (EquipmentSponsorStatusStates.EXPIRED, "Expired"),
        ]
        return context
