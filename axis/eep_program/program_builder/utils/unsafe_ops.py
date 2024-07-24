"""Program checklist utils"""


import logging


__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


def drop_checklist(eep_program):
    eep_program.required_checklists.clear()
