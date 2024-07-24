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


class EquipmentControlCenterNewListView(EquipmentControlCenterBaseListView):
    equipment_state = EquipmentSponsorStatusStates.NEW

    def get_context_data(self, **kwargs):
        context = super(EquipmentControlCenterNewListView, self).get_context_data(**kwargs)
        context["equipment_sponsor_status_state_choices"] = [
            (EquipmentSponsorStatusStates.ACTIVE, "Active"),
            (EquipmentSponsorStatusStates.REJECTED, "Rejected"),
        ]
        return context

    def get_datatable(self):
        datatable = super(EquipmentControlCenterNewListView, self).get_datatable()

        del datatable.columns["approval_status_notes"]

        return datatable
