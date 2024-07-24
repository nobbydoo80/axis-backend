"""hirl_user_profile.py: """

__author__ = "Artem Hruzd"
__date__ = "10/16/2020 19:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.examine import SingleObjectMachinery
from axis.customer_hirl.models import HIRLUserProfile
from axis.core.api import HIRLUserProfileViewSet
from axis.core.forms import HIRLUserProfileForm


class HIRLUserProfileExamineMachinery(SingleObjectMachinery):
    model = HIRLUserProfile
    form_class = HIRLUserProfileForm
    type_name = "hirl_user_profile"
    api_provider = HIRLUserProfileViewSet

    detail_template = "examine/user/hirl_user_profile_detail_default.html"

    def get_region_dependencies(self):
        return {
            "user": [
                {
                    "field_name": "id",
                    "serialize_as": "user_id",
                }
            ],
        }

    def can_edit_object(self, instance, user=None):
        """Who can edit this"""
        if not user:
            return False
        return user.is_superuser or user.is_customer_hirl_company_member()

    def can_delete_object(self, instance, user=None):
        return False
