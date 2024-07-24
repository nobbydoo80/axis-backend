"""control_center_approved_list.py: """


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


class TrainingControlCenterApprovedListView(TrainingControlCenterBaseListView):
    training_state = TrainingStatusStates.APPROVED

    def get_context_data(self, **kwargs):
        context = super(TrainingControlCenterApprovedListView, self).get_context_data(**kwargs)
        context["training_status_state_choices"] = [
            (TrainingStatusStates.REJECTED, "Rejected"),
        ]
        return context
