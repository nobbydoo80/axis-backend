"""apps.py - axis"""

__author__ = "Steven K"
__date__ = "1/9/23 13:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.apps import AppConfig
from django.conf import settings

log = logging.getLogger(__name__)


class GBRAppConfig(AppConfig):
    name = "axis.gbr"
    API_KEY = getattr(settings, "GBR_API_KEY", "bhmcv4-f6f45cd12d4e49c77b317e3d65b0758c")
    EXTERNAL_ID_ANNOTATION_SLUG = "hpxml_gbr_id"
