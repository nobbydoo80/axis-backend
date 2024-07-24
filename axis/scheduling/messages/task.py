"""task.py: """


from axis.messaging.messages import ModernMessage

__author__ = "Artem Hruzd"
__date__ = "01/13/2020 15:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TaskCreatedMessage(ModernMessage):
    title = "New Scheduled Task created"
    content = (
        'Scheduled Task #{task_id} created by <a href="{assigner_profile_url}" target="_blank">{assigner}</a>. '
        'Approve or Reject it <a href="{dashboard_url}" '
        'target="_blank">here</a> '
    )
    category = "Scheduled Task"
    level = "info"
    sticky_alert = False

    verbose_name = "New Task Created"
    description = "Sent to Assignee Users and Company Admins from Assignee users company"


class TaskApprovedMessage(ModernMessage):
    title = "Scheduled Task Approved"
    content = (
        "Scheduled Task #{task_id} assigned to {assignee_links_list} has been <b>Approved</b> "
        'by <a href="{approver_user_profile_url}">{approver_user}</a>.<br>'
        '<a href="{url}" '
        "target='_blank'>View task</a>"
    )
    category = "Scheduled Task"
    level = "info"
    sticky_alert = False

    verbose_name = "Scheduled Task Approved"
    description = "Sent to Assigner and Assignee users"


class TaskRejectedMessage(ModernMessage):
    title = "Scheduled Task Rejected"
    content = (
        "Scheduled Task #{task_id} assigned to {assignee_links_list} has been <b>Rejected</b> "
        'by <a href="{approver_user_profile_url}">{approver_user}</a>. Reason: "{reason}"<br>'
        '<a href="{url}" '
        "target='_blank'>View task</a>"
    )
    category = "Scheduled Task"
    level = "info"
    sticky_alert = False

    verbose_name = "Scheduled Task Rejected"
    description = "Sent to Assigner and Assignee users"


class TaskChangedStatusMessage(ModernMessage):
    title = "Scheduled Task Status Changed"
    content = (
        "Status of Schedule Task #{task_id} assigned to {assignee_links_list} has been changed to <b>{new_status}</b> "
        'by <a href="{status_approver_user_profile_url}">{status_approver_user}</a><br>'
        '<a href="{url}" '
        'target="_blank">View task</a>'
    )
    category = "Scheduled Task"
    level = "info"
    sticky_alert = False

    verbose_name = "Scheduled Task Status Changed"
    description = "Sent to Assigner and Assignee users"
