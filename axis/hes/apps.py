"""apps.py: Django apps.py"""


import logging

from django.conf import settings

from axis.core import technology

__author__ = "Steven K"
__date__ = "11/14/2019 09:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class HESConfig(technology.TechnologyAppConfig):
    """HES configuration."""

    name = "axis.hes"

    sandbox_url = "https://sandbox.hesapi.labworks.org/st_api/serve"
    URL = getattr(settings, "DOE_HES_URL", sandbox_url)
    API_KEY = getattr(settings, "DOE_HES_API_KEY")

    EXTERNAL_ID_ANNOTATION_SLUG = "hpxml_gbr_id"
    ORIENTATION_ANNOTATION_SLUG = "home-orientation"
