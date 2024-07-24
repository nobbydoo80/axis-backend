"""states.py: """


__author__ = "Artem Hruzd"
__date__ = "04/16/2020 17:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class VerifierAgreementStates(object):
    """Enum for valid state codes, their choices, and related lookups."""

    NEW = "new"
    APPROVED = "approved"
    VERIFIED = "verified"
    COUNTERSIGNED = "countersigned"
    EXPIRED = "expired"

    choices = (
        (NEW, "Submitted"),
        (APPROVED, "Approved"),
        (VERIFIED, "Routed for Counter-Signing"),
        (COUNTERSIGNED, "Counter-Signed"),
        (EXPIRED, "Expired"),
    )

    verbose_names = dict(choices)
    code_names = dict(map(reversed, choices))
    ordering = tuple(choice[0] for choice in choices)
    order_map = dict(
        map(reversed, enumerate(ordering)),
        **{str(k): v for k, v in map(reversed, enumerate(verbose_names.items()))},
    )
