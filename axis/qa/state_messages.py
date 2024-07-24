from datetime import timedelta
from axis.qa.messages import QACycleTimeReporting

__author__ = "Michael Jeffrey"
__date__ = "10/14/15 2:58 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


DEFAULT_COUNTDOWN = timedelta(hours=48).total_seconds()
DEFAULT_COUNTDOWN_PRETTY = "48 Hours"

messages = {
    "eto": {
        ("received", "file"): {
            "message": "QACycleTimeReporting",
            "recipients": ["owner"],  # qa company
            "countdown": DEFAULT_COUNTDOWN,
            "countdown_pretty": DEFAULT_COUNTDOWN_PRETTY,
        },
        ("in_progress", "file"): {
            "message": "QACycleTimeReporting",
            "recipients": ["owner"],  # qa company
            "countdown": DEFAULT_COUNTDOWN,
            "countdown_pretty": DEFAULT_COUNTDOWN_PRETTY,
        },
        ("correction_required", "file"): {
            "message": "QACycleTimeReporting",
            "recipients": ["home_status.company"],  # rater company
            "countdown": DEFAULT_COUNTDOWN,
            "countdown_pretty": DEFAULT_COUNTDOWN_PRETTY,
        },
        ("correction_received", "file"): {
            "message": "QACycleTimeReporting",
            "recipients": ["owner"],  # qa company
            "countdown": DEFAULT_COUNTDOWN,
            "countdown_pretty": DEFAULT_COUNTDOWN_PRETTY,
        },
    }
}

messages["eto-2015"] = messages["eto"]
messages["eto-2016"] = messages["eto"]
