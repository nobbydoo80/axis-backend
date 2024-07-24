"""control_center_new_list.py: """


from axis.user_management.states import TrainingStatusStates
from axis.user_management.views.training.control_center_base_list import (
    TrainingControlCenterBaseListView,
)

__author__ = "Artem Hruzd"
__date__ = "10/30/2019 18:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingControlCenterNewListView(TrainingControlCenterBaseListView):
    training_state = TrainingStatusStates.NEW

    def get_context_data(self, **kwargs):
        context = super(TrainingControlCenterNewListView, self).get_context_data(**kwargs)
        context["training_status_state_choices"] = [
            (TrainingStatusStates.APPROVED, "Approved"),
            (TrainingStatusStates.REJECTED, "Rejected"),
        ]
        return context

    def get_datatable(self):
        datatable = super(TrainingControlCenterNewListView, self).get_datatable()

        del datatable.columns["approval_status_notes"]

        return datatable
