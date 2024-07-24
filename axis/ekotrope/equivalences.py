"""equivalences.py: Django Ekotrope"""


import logging

__author__ = "Steven Klass"
__date__ = "9/8/17 10:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# This is used to help us map bewtween REM/Rate® and Ekotrope - The number on the left refers to the REM/Rate® idenfier

FOUNDATION_TYPES = (
    (4, "CONDITIONED_BASEMENT"),
    (5, "UNCONDITIONED_BASEMENT"),
    (1, "SLAB_ON_GRADE"),
    (2, "CRAWLSPACE"),  # Warning not a direct map
)
