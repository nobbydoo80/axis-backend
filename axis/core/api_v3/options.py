"""options.py - Axis"""

import logging

from rest_framework.exceptions import PermissionDenied
from rest_framework.metadata import SimpleMetadata

__author__ = "Steven K"
__date__ = "7/1/20 13:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


log = logging.getLogger(__name__)


class AxisFrontEndOptions:
    """
    Getting extra data from Viewsets to generate additional info for frontend
    developers about UI and permissions


    On a list Model View - the basics perms are
        - View
        - Add New

    On a detail Model View - the basics perms are
        - Edit
        - Delete

    If you want more flexibility you can add `get_permission_options` method
    to your  view / viewset.

        def get_permission_options(*actions):
            return {
                'show_filter_option': self.request.user == 'steven'
            }

    You can also append permissions add `add_permission_options` method

        def add_permission_options(*action, request):
            return {
                'show_filter_option': self.request.user == 'steven'
            }

    """

    def __init__(self, request, view):
        self.request = request
        self.view = view

    def get_available_actions_from_view(self):
        """For a given view get the available actions"""
        from rest_framework.routers import SimpleRouter

        router = SimpleRouter()
        try:
            routes = router.get_routes(self.view)
        # APIView do not have get_extra_actions, we ignore it
        except AttributeError:
            return []
        action_list = []
        for route in routes:
            action_list += list(route.mapping.values())
        distinct_action_list = list(set(action_list))
        distinct_action_list.sort()
        return distinct_action_list

    def get_default_perms(self, *actions):
        """
        Follows the same logic as DRF -- If any permission check fails the whole thing fails

        See: https://www.django-rest-framework.org/api-guide/permissions/#how-permissions-are-determined
        """

        total_available_actions = self.get_available_actions_from_view()
        available_actions = list(set(actions).intersection(set(total_available_actions)))

        # _base_action = self.view.action
        permissions = {"can_%s" % action: True for action in available_actions}
        for action in available_actions:
            self.view.action = action
            try:
                self.view.check_permissions(self.request)
                if (
                    hasattr(self.view, "lookup_field")
                    and self.view.lookup_field in self.view.kwargs
                ):
                    self.view.check_object_permissions(self.request, self.view.get_object())
            except PermissionDenied:
                permissions["can_%s" % action] = False
        # self.view.action = _base_action
        return permissions

    def determine_permissions(self):
        """This will allow us to get a standardized set of permission"""
        actions = []

        if hasattr(self.view, "action_map") and self.view.action_map:
            actions = list(self.view.action_map.values())
            if self.view.action_map.get("get") == "list":  # We are on a list view
                actions += ["retrieve"]
            if self.view.action_map.get("get") == "retrieve":  # We are on a detail view
                actions += ["destroy"]
            actions = list(set(actions))

        if hasattr(self.view, "get_permission_options"):
            return self.view.get_permission_options(*actions)

        perms = self.get_default_perms(*actions)
        if hasattr(self.view, "add_permission_options"):
            perms.update(self.view.add_permission_options(actions))
        return perms

    def get_available_elements(self):
        """Get a list of available elements"""
        if hasattr(self.view, "get_available_element_options"):
            return self.view.get_available_element_options(self.request)
        return []


class AxisMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super(AxisMetadata, self).determine_metadata(request, view)
        frontend_options = AxisFrontEndOptions(request=request, view=view)
        metadata["permissions"] = frontend_options.determine_permissions()
        metadata["available_elements"] = frontend_options.get_available_elements()

        return metadata
