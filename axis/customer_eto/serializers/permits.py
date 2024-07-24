"""permits.py: Django Permit and Occupancy Serializers"""


import logging

from django.apps import apps
from rest_framework import serializers

from axis.customer_eto import models
from axis.customer_eto.forms import PermitAndOccupancySettingsForm
from axis.home.utils import get_inheritable_settings_form_info

__author__ = "Steven K"
__date__ = "08/29/2019 11:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


class PermitAndOccupancySettingsFieldsMixin(object):
    """Serializer mixin for managing inherited serializer field values."""

    def __init__(self, *args, **kwargs):
        """Initialize nested settings management for the target object."""

        # Avoid obscure circular import errors while using this mixin
        from axis.company.models import Company
        from axis.subdivision.models import Subdivision
        from axis.home.models import Home, EEPProgramHomeStatus

        super(PermitAndOccupancySettingsFieldsMixin, self).__init__(*args, **kwargs)

        user = None
        if self.context.get("request"):
            user = self.context["request"].user

        community = False  # invalid logic tree for a community context
        if user and user.company.slug in app.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS:
            if not self.instance or not hasattr(self.instance, "pk"):
                community = False
            elif self.instance.pk is None:
                community = False
            elif isinstance(self.instance, Home) and self.instance.subdivision_id:
                community = self.instance.subdivision.community
            elif isinstance(self.instance, Subdivision):
                community = self.instance.community
            elif isinstance(self.instance, Company):
                community = None  # selectable but no preference specified

        is_created = (
            self.instance
            and not isinstance(self.instance, list)  # guard from list serializer
            and self.instance.pk
        )

        valid_community = community is None or (
            community and community.slug in app.CITY_OF_HILLSBORO_COMMUNITY_SLUGS
        )

        # Confirm available user, instance, and fk-related community slug
        if (
            user
            and user.has_perm("customer_eto.change_permitandoccupancysettings")
            and is_created
            and valid_community
        ):
            self._permitandoccupancysettings = (
                self.instance.permitandoccupancysettings_set.get_for_user(user)
            )
            obj = self.instance
            obj_company = user.company
            if isinstance(obj, EEPProgramHomeStatus):
                obj_company = obj.company
            question_data = get_inheritable_settings_form_info(
                obj_company,
                obj,
                "permitandoccupancysettings_set",
                form_class=PermitAndOccupancySettingsForm,
                settings_action_url="eto-compliance-option",
                document_action_url="eto-compliance-document",
            )
            self._permitandoccupancysettings_null_values = {
                item["name"]: item["null_value"]
                for grouping in question_data["question_data"]
                for item in grouping["items"]
            }
        else:
            self._permitandoccupancysettings = None
            self._permitandoccupancysettings_null_values = {}

    def get_fields(self):
        """Return fields without the ones excluded on the internal form."""

        fields = super(PermitAndOccupancySettingsFieldsMixin, self).get_fields()

        for k in app.CITY_OF_HILLSBORO_FIELDS:
            if k not in self._permitandoccupancysettings_null_values:
                del fields[k]

        return fields

    def _get_settings_value(self, obj, name):
        """Return attribute `name` from `obj`, or the local field's null-like value."""

        null_value = self._permitandoccupancysettings_null_values.get(name, None)
        value = getattr(self._permitandoccupancysettings, name, null_value)
        if value is None:
            return null_value
        return value

    def get_reeds_crossing_compliance_option(self, obj):  # pylint: disable=invalid-name
        """Return effective setting for "Reed's Crossing" on the serializer's obj."""

        return self._get_settings_value(obj, "reeds_crossing_compliance_option")

    def get_rosedale_parks_compliance_option(self, obj):  # pylint: disable=invalid-name
        """Return effective setting for "Rosedale Parks" on the serializer's obj."""

        return self._get_settings_value(obj, "rosedale_parks_compliance_option")


class PermitAndOccupancySettingsSerializer(serializers.ModelSerializer):
    """ETO Permit and Occupancy settings for a provided object instance."""

    class Meta:
        """Meta Options"""

        model = models.PermitAndOccupancySettings
        fields = (
            "reeds_crossing_compliance_option",
            "rosedale_parks_compliance_option",
        )

    def __init__(self, *args, **kwargs):
        """Initialize and remove `required` flag from all fields."""
        super(PermitAndOccupancySettingsSerializer, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].required = False

    def to_internal_value(self, data):
        """Translate incoming simplistic values to built-in types."""

        for k, v in data.items():
            if v == "true":
                data[k] = True
            elif v == "false":
                data[k] = False
            elif v in ("company", "subdivision"):  # indirection for inherited values
                data[k] = None
        return super(PermitAndOccupancySettingsSerializer, self).to_internal_value(data)
