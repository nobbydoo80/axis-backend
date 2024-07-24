"""user_profile.py: """

__author__ = "Artem Hruzd"
__date__ = "05/07/2021 17:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from rest_framework import serializers

from axis.customer_hirl.models import HIRLUserProfile


class HIRLUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HIRLUserProfile
        fields = (
            "id",
            "is_qa_designee",
        )
