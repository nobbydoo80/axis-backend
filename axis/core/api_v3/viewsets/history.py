"""history.py: """

import itertools

from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from axis.core.api_v3.serializers import HistorySerializer

__author__ = "Artem Hruzd"
__date__ = "03/12/2020 10:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class NestedHistoryViewSet(NestedViewSetMixin, viewsets.GenericViewSet):
    """
    Using in nester router to show resource history
    retrieve:
        Return a history instance.
    list:
        Return all history instances for parent
    """

    model = None
    serializer_class = HistorySerializer
    ordering_fields = []
    blacklist_edit_fields = [
        "history_user",
        "history_type",
        "history_date",
        "history_id",
        "history_change_reason",
    ]
    blacklist_create_fields = [
        "id",
        "history_user",
        "history_type",
        "history_date",
        "history_id",
        "history_change_reason",
    ]

    def _get_changes(self, queryset):
        changes = []
        lst = list(queryset)
        if not lst:
            return []
        # create two lists with itertools.zip_longest like this:
        # original_history = [1, 2, None]
        # diff_history = [None, 1, 2]
        # to diff history objects
        for new_record, old_record in itertools.zip_longest(
            lst,
            [
                lst[0].prev_record,
            ]
            + lst,
        ):
            change_data = {"changes": []}

            if not new_record:
                continue

            if old_record:
                delta = new_record.diff_against(old_record)
                for change in delta.changes:
                    if change.field not in self.blacklist_edit_fields:
                        change_data["changes"].append(
                            {"field_name": change.field, "old": change.old, "new": change.new}
                        )
            else:
                for field in self.model._meta.fields:
                    if field.name not in self.blacklist_create_fields:
                        change_data["changes"].append(
                            {
                                "field_name": field.name,
                                "old": None,
                                "new": getattr(new_record, field.attname),
                            }
                        )
            change_data["history_id"] = new_record.history_id
            change_data["history_type"] = new_record.history_type
            change_data["history_datetime"] = new_record.history_date.astimezone(
                self.request.user.timezone_preference
            )
            if new_record.history_user:
                change_data["history_user"] = new_record.history_user.id
                change_data["history_user_info"] = new_record.history_user
            changes.append(change_data)
        return changes

    @property
    def filterset_class(self):
        class HistoryFilter(filters.FilterSet):
            class Meta:
                model = self.model
                fields = ("history_type", "history_user")

        return HistoryFilter

    def list(self, request, *args, **kwargs):
        # important to order queryset manually to correctly diff results
        queryset = self.filter_queryset(self.get_queryset()).order_by("-id")
        changes = self._get_changes(queryset=queryset)
        changes = list(filter(lambda change: len(change["changes"]), changes))

        page = self.paginate_queryset(changes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(changes, many=True)
        return Response(serializer.data)
