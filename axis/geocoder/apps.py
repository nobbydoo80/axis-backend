import os

from django.conf import settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class GeocoderConfig(technology.TechnologyAppConfig):
    """Geocoder technology configuration."""

    name = "axis.geocoder"
    verbose_name = "Geocoder"

    GEOCODER_DEFAULT_TIMEOUT = 2

    # Note if you plan to add to this list you will need to run the following to seed in a number
    # of cities to our DB.  Doing this will then enable the geocoder to filter results to these
    # countries and limits the scope of City matches.
    # ./manage.py update_base_geographic_data --country XX
    SUPPORTED_COUNTRIES = ["US", "DO", "PR", "VI"]

    CLOSE_PROXIMITY_RATIO_LOOKUP = {"city": 0.95, "intersection": 0.85, "street_address": 0.75}
    CACHED_STORAGE_FILENAME = os.path.join(os.path.dirname(__file__), "sources", "cached_db.db")
