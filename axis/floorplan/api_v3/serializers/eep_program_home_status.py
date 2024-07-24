"""eep_program_home_status.py: """


__author__ = "Rajesh Pethe"
__date__ = "10/22/2022 10:55:43"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


import logging

from rest_framework import serializers

from axis.home.models import EEPProgramHomeStatus
from axis.home.api_v3.serializers import HomeSubdivisionEEPSerializer

log = logging.getLogger(__name__)


class EEPProgramHomeStatusSerializerMixin(metaclass=serializers.SerializerMetaclass):
    home_info = HomeSubdivisionEEPSerializer(source="home")


class EEPProgramHomeStatusMeta:
    """
    Base Meta model for EEPProgramHomeStatus with common fields
    """

    model = EEPProgramHomeStatus
    fields = (
        "home",
        "home_info",
    )


class EEPProgramHomeStatusSerializer(
    EEPProgramHomeStatusSerializerMixin, serializers.ModelSerializer
):
    """Basic control of EEPProgramHomeStatus instance."""

    class Meta(EEPProgramHomeStatusMeta):
        ref_name = "EEPProgramHomeStatusSerializer"
