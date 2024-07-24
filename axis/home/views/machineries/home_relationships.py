from axis.core.views.machinery import BaseRelationshipExamineMachinery
from axis.home.views.utils import _get_home_contributor_flag

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeRelationshipsExamineMachinery(BaseRelationshipExamineMachinery):
    """Relationships Widget"""

    region_template = "examine/home/relationship_region.html"
    detail_template = "examine/home/relationship_detail.html"

    is_contributor = None
    restricted_edit = False

    def configure_for_instance(self, instance):
        """Configure this for the user"""
        user = self.context["request"].user
        self.is_contributor = _get_home_contributor_flag(instance, user)

        if self.is_contributor and not self.context.get("lightweight") and not self.create_new:
            can_edit = instance.can_be_edited(user)
            self.restricted_edit = instance.has_locked_homestatuses() and can_edit

    def get_default_actions(self, instance):
        """Default actions"""
        if not self.is_contributor:
            return []

        actions = super(HomeRelationshipsExamineMachinery, self).get_default_actions(instance)
        if self.restricted_edit:
            for action in actions:
                if action["instruction"] == "edit":
                    action["icon"] = "unlock-alt"
        return actions

    def get_helpers(self, instance):
        """Helpers on the home relationship"""
        helpers = super(BaseRelationshipExamineMachinery, self).get_helpers(instance)
        helpers["is_contributor"] = self.is_contributor
        if self.restricted_edit:
            helpers["restricted_edit"] = True
            helpers["locked_company_ids"] = set(
                instance.relationships.values_list("company__id", flat=True)
            )
        return helpers
