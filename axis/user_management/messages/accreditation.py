"""training.py: """


from axis.messaging.messages import ModernMessage

__author__ = "Artem Hruzd"
__date__ = "12/03/2019 17:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AccreditationCreatedTraineeMessage(ModernMessage):
    title = "Accreditation created"
    content = (
        "New accreditation {accreditation} created by {approver_company} "
        "<a href='{url}#/tabs/accreditation' "
        "target='_blank'>View accreditation list</a>"
    )
    category = "User accreditation"
    level = "info"
    sticky_alert = True

    verbose_name = "Accreditation created"
    description = (
        "Sent to trainee user when new accreditation " "has been created by oversight company"
    )


class AccreditationStateChangedTraineeMessage(ModernMessage):
    title = "Accreditation state changed"
    content = (
        "Accreditation {accreditation} state changed "
        "from <b>{old_state}</b> to <b>{new_state}</b> "
        "<a href='{url}#/tabs/accreditation' "
        "target='_blank'>View accreditation list</a>"
    )
    category = "User accreditation"
    level = "info"
    sticky_alert = True

    verbose_name = "Accreditation state changed"
    description = (
        "Sent to trainee user when accreditation state" "has been changed by oversight company"
    )


class AccreditationExpireWarningMessage(ModernMessage):
    title = "Accreditation will expire soon"
    content = (
        "Accreditation {accreditation} for {trainee} will expire "
        "within {days_before_expire} days"
        "<a href='{url}#/tabs/accreditation' "
        "target='_blank'>View {trainee} accreditation list</a>"
    )
    category = "User accreditation"
    level = "warning"
    sticky_alert = True

    verbose_name = "Accreditation state changed"
    description = "Sent before accreditation for user will expire"
