"""mixins.py: Django """


import logging

from axis.home.export_data import HomeDataXLSExport
from .mixins import ExtraFiltersMixin

__author__ = "Steven K"
__date__ = "08/02/2019 11:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class NEEAHomeDataRawExport(ExtraFiltersMixin, HomeDataXLSExport):
    """Purely a title change"""

    def __init__(self, *args, **kwargs):
        kwargs["title"] = kwargs["subject"] = "Project Utility Export"
        super(NEEAHomeDataRawExport, self).__init__(*args, **kwargs)
