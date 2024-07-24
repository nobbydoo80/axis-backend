"""messages.py: Django floorplan"""


import logging

from axis.messaging.messages import ModernMessage
from . import strings

__author__ = "Steven Klass"
__date__ = "11/19/15 10:31 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ProgramSubmitSunsetMessage(ModernMessage):
    # content =   # Dictated by eep_program.program_close_warning
    sticky_alert = True
    category = "project"
    level = "warning"

    verbose_name = "Program submit warning"
    description = "Sent when a program nearing its submit date has been added to a project."

    unique = True  # Message text better have something unique in it (home address at least)


class ProgramSunsetMessage(ModernMessage):
    # content =   # Dictated by eep_program.program_close_warning
    sticky_alert = True
    category = "project"
    level = "warning"

    verbose_name = "Program close warning"
    description = "Sent when a program nearing its close date has been added to a project."

    unique = True  # Message text better have something unique in it (home address at least)
