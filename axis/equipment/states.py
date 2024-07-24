__author__ = "Artem Hruzd"
__date__ = "10/29/2019 16:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentSponsorStatusStates(object):
    """Enum for valid state codes, their choices, and related lookups."""

    NEW = "new"
    ACTIVE = "active"
    REJECTED = "rejected"
    EXPIRED = "expired"

    choices = (
        (NEW, "New (Unapproved)"),
        (ACTIVE, "Active"),
        (REJECTED, "Rejected"),
        (EXPIRED, "Expired"),
    )

    verbose_names = dict(choices)
    code_names = dict(map(reversed, choices))
    ordering = tuple(choice[0] for choice in choices)
    order_map = dict(
        map(reversed, enumerate(ordering)),
        **{str(k): v for k, v in map(reversed, enumerate(verbose_names.items()))},
    )
