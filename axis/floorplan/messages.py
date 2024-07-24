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


class FloorplanRemrateDataChangeMessage(ModernMessage):
    content = strings.APS_REMRATE_DATA_CHANGE
    sticky_alert = True
    category = "Floorplan"
    level = "info"

    verbose_name = "Floorplan REM/Rate® data has changed"
    description = "Sent when a REM/Rate® data has changed on a floorplan"

    unique = True
    company_slugs = ["aps"]


class FloorplanRemrateDataAddMessage(ModernMessage):
    content = strings.APS_REMRATE_DATA_ADD
    sticky_alert = True
    category = "Floorplan"
    level = "info"

    verbose_name = "Floorplan REM/Rate® data has been added"
    description = "Sent when a REM/Rate® data has added on a floorplan"

    unique = True
    company_slugs = ["aps"]
