"""default.py: Django """


import logging

__author__ = "Steven Klass"
__date__ = "4/6/18 12:36 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

VALID_PROGRAM_SLUGS = [
    "aps-energy-star-v3-hers-60-2018",
    "aps-energy-star-v3-2018",
    "aps-energy-star-v3-2019",
    "aps-energy-star-2019-tstat",
    "aps-energy-star-2019-tstat-addon",
]
