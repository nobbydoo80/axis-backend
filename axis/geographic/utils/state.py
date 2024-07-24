"""state.py - axis"""

__author__ = "Steven K"
__date__ = "7/28/22 11:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from axis.geographic.models import USState

from localflavor.us.us_states import STATES_NORMALIZED

from axis.geographic.tests.factories import us_states_factory

log = logging.getLogger(__name__)


def resolve_state(name: str | None) -> USState | None:
    """This will get (and create) a country"""

    if name is None:
        return None
    if isinstance(name, USState):
        return name
    if name.lower() in STATES_NORMALIZED:
        return us_states_factory(STATES_NORMALIZED[name.lower()], add_all=False)
    raise KeyError(f"US State {name} not valid")
