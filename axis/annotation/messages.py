__author__ = "Michael Jeffrey"
__date__ = "8/27/15 10:32 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

from axis.messaging.messages import ModernMessage


class NWESHMeetsOrBeatsAnsweredNo(ModernMessage):
    content = (
        'Home <a target="_blank" href="{url}">{text}</a> does not meet or beat the '
        "reference home consumption target. Please add a comment to the home to explain the deviation."
    )
    sticky_alert = True
    category = "annotation"
    level = "warning"

    verbose_name = "Meets or Beats"
    description = 'Annotation "Meets or Beats" answered with "No".'
