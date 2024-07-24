"""exceptions.py - Exceptions raised by Home Energy Score tasks"""

__author__ = "Benjamin Stürmer"
__date__ = "10/22/2022 12:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin Stürmer",
]


class TaskFailed(Exception):
    """Raise to indicate that a Home Energy Score task failed. This is our generic task error, and can
    be extended as necessary for more specific error conditions"""

    pass
