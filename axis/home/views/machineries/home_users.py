from axis.examine.machinery import SingleObjectMachinery
from axis.home.api import HomeUsersViewSet
from axis.home.forms import HomeUsersForm
from axis.home.models import Home


__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeUsersExamineMachinery(SingleObjectMachinery):
    """Home Users - Users attached to a home"""

    model = Home
    form_class = HomeUsersForm
    type_name = "home_users"
    api_provider = HomeUsersViewSet

    # Override templates so that we can target only the "users" data on the Home instance
    detail_template = "examine/home/users_detail.html"

    def can_delete_object(self, instance, user=None):
        """Can we be deleted"""
        return False

    def get_region_dependencies(self):
        """Region depends on what"""
        return {
            "home": [
                {
                    "field_name": "id",
                    "serialize_as": "id",
                }
            ],
        }

    def get_edit_actions(self, instance):
        """Default Edit Actions"""
        if self.create_new:
            return []  # Primary region will issue a global save
        return super(HomeUsersExamineMachinery, self).get_edit_actions(instance)

    def get_form_kwargs(self, instance):
        """Default Form kwargs"""
        return {
            "user": self.context["request"].user,
        }
