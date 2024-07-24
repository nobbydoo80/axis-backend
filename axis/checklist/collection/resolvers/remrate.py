"""REM/Rate resolvers"""

import logging

from django.apps import apps
from django_input_collection.collection import AttributeResolver

__author__ = "Autumn Valenta"
__date__ = "2012-10-08 1:48:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions.Consulting. All rights reserved."
__credits__ = [
    "Steven Klass",
]
__license__ = "See the file LICENSE.txt for licensing information."

log = logging.getLogger(__name__)
app = apps.get_app_config("django_input_collection")

_should_log = getattr(app, "VERBOSE_LOGGING", False)


class RemRateResolver(AttributeResolver):
    name = "rem"
    pattern = r"(?P<dotted_path>.*)"

    def resolve(self, instrument, dotted_path, **context):
        collection_request = instrument.collection_request
        home_status = getattr(collection_request, "eepprogramhomestatus", None)

        if home_status is None:
            # Skip program-tier instruments with no homestatus
            values = None
        else:
            values = self.resolve_dotted_path(home_status, dotted_path)

        # Treat values as plural, as if they are ResponsePolicy.multiple=True results
        if not isinstance(values, (list, tuple)):
            values = [values]

        # Ignore discovered values that are None
        values = [x for x in values if x is not None]

        if _should_log:
            log.debug(
                "REM resolver for %s Inst: %s (%s) → %s",
                dotted_path,
                instrument,
                instrument.pk,
                values,
            )

        return {
            "data": {
                "input": values,
            },
        }
