"""client.py: """

__author__ = "Artem Hruzd"
__date__ = "05/03/2022 23:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers

from axis.customer_hirl.models import HIRLCompanyClient


class HIRLCompanyClientSerializer(serializers.ModelSerializer):
    """
    Using as nested serializer in Company serializer and can be updated only via Company model
    """

    class Meta:
        model = HIRLCompanyClient
        fields = ("id",)
