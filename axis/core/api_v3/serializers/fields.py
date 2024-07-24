# -*- coding: utf-8 -*-
"""fields.py: """

__author__ = "Artem Hruzd"
__date__ = "02/22/2023 11:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework import serializers


class FilterByUserPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Limit serializer queryset for request user by filtering it with filter_by_user manager method
    """

    def get_queryset(self):
        request = self.context.get("request", None)
        queryset = super(FilterByUserPrimaryKeyRelatedField, self).get_queryset()
        if not request:
            return queryset.none()
        return queryset.filter_by_user(user=request.user)
