"""history_utils.py: Django core"""

import logging

from django.core.exceptions import ObjectDoesNotExist

__author__ = "Steven Klass"
__date__ = "12/22/16 17:08"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def get_revision_delta(model, object_list, index, user=None):
    """Given an index number get the delta between the prior item"""
    fields = model._meta.fields
    item = object_list[index]

    related_dict = {}

    previous_item = {}
    for old_item in reversed(object_list[:index]):
        if old_item.get("id") == item.get("id"):
            previous_item = old_item
            break

    changed_fields, prev_values, cur_values = [], [], []
    for field in fields:
        prev_value = previous_item.get(field.name, "-")
        prev_value = prev_value if prev_value else "-"
        curr_value = item.get(field.name, "-")
        curr_value = curr_value if curr_value else "-"

        if hasattr(field, "rel") and field.rel:
            if prev_value == "-":
                prev_value = previous_item.get(field.name + "_id", "-")
                prev_value = prev_value if prev_value else "-"
            if curr_value == "-":
                curr_value = item.get(field.name + "_id", "-")
                curr_value = curr_value if curr_value else "-"

        # Handle nice choices keys
        if hasattr(field, "_choices") and len(field._choices) and curr_value != "-":
            try:
                curr_value = next((x[1] for x in field._choices if str(x[0]) == str(curr_value)))
            except StopIteration:
                pass
        # Handle foreign keys.
        elif hasattr(field, "rel") and field.rel and curr_value != "-":
            try:
                curr_value = related_dict[(field.name, curr_value)]
                # log.debug("Related (current) Dict - Query Saved {} = {}".format(field.name, curr_value))
            except KeyError:
                _v = "-"
                try:
                    _v = "{}".format(field.rel.model.objects.get(id=curr_value))
                    if user and user.is_superuser:
                        _v = "[{}] {}".format(curr_value, _v)
                except ObjectDoesNotExist:
                    _v = "Deleted"
                # log.debug("Setting C Related ({}, {}) = {}".format(field.name, curr_value,_v))
                related_dict[(field.name, curr_value)] = _v
                curr_value = related_dict[(field.name, curr_value)]

        if hasattr(field, "_choices") and len(field._choices) and prev_value != "-":
            try:
                prev_value = next((x[1] for x in field._choices if str(x[0]) == str(prev_value)))
            except StopIteration:
                pass

        elif hasattr(field, "rel") and field.rel and prev_value != "-":
            try:
                prev_value = related_dict[(field.name, prev_value)]
                # log.debug("Related (prev) Dict - Query Saved {} = {}".format(field.name, prev_value))
            except KeyError:
                _v = "-"
                try:
                    _v = "{}".format(field.rel.model.objects.get(id=prev_value))
                    if user and user.is_superuser:
                        _v = "[{}] {}".format(prev_value, _v)
                except ObjectDoesNotExist:
                    _v = "Deleted"
                # log.debug("Setting P Related ({}, {}) = {}".format(field.name, prev_value,_v))
                related_dict[(field.name, prev_value)] = _v
                prev_value = related_dict[(field.name, prev_value)]

        if field.__class__.__name__ == "DateTimeField":
            try:
                curr_value = curr_value.strftime("%m/%d/%y %H:%M")
            except AttributeError:
                pass
            try:
                prev_value = prev_value.strftime("%m/%d/%y %H:%M")
            except AttributeError:
                pass

        if field.__class__.__name__ == "DateField":
            try:
                curr_value = curr_value.strftime("%m/%d/%y")
            except AttributeError:
                pass
            try:
                prev_value = prev_value.strftime("%m/%d/%y")
            except AttributeError:
                pass

        if prev_value != curr_value:
            changed_fields.append(field.name)
            prev_values.append(prev_value)
            cur_values.append(curr_value)
    result = {"fields": [], "previous": [], "updated": []}
    if len(changed_fields):
        result = {
            "fields": ["{}".format(x) for x in changed_fields],
            "previous": ["{}".format(x) for x in prev_values],
            "updated": ["{}".format(x) for x in cur_values],
        }
    return result
