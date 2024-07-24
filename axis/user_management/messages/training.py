"""training.py: """


from axis.messaging.messages import ModernMessage

__author__ = "Artem Hruzd"
__date__ = "12/03/2019 17:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingStatusStateChangedMessage(ModernMessage):
    title = "Training state changed"
    content = (
        "Training {training} for {trainee} changed state from "
        "<b>{old_state}</b> to <b>{new_state}</b><br>"
        "<a href='{url}#/tabs/training' "
        "target='_blank'>View {trainee} training list</a>"
    )
    category = "User training"
    level = "info"
    sticky_alert = True

    verbose_name = "Training state changed"
    description = "Sent once the training status state been changed"
