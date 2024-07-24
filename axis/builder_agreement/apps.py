from django.conf import settings

from axis.core import platform

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "PLATFORM_BUILDER_AGREEMENT", {})


class BuilderAgreementConfig(platform.PlatformAppConfig):
    """Builder Agreement platform configuration."""

    name = "axis.builder_agreement"

    # https://pivotalenergysolutions.zendesk.com/agent/tickets/25606
    # An incentives anomaly in APS's accounting has left homes without record of payment.
    APS_LOTS_PAID_HACK_SLUG = "desert-wind-villas-phase-c-phoenix-az-taylor-morri"
    APS_LOTS_PAID_HACK_OFFSET = 13
