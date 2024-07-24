""" Generic machinery classes for use in other axis. """


from django.urls import reverse
from django.utils.text import slugify

from axis.company.strings import COMPANY_TYPES_MAPPING
from axis.relationship.forms import object_relationships_form_factory
from axis import examine

__author__ = "Autumn Valenta"
__date__ = "10-01-14  1:30 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


def object_relationships_machinery_factory(Model, bases=None, company_types=None):
    """Builds a Machinery class that represents the given Model's "relationships" m2m."""
    from ..api import relationship_viewsets

    if not bases:
        bases = (BaseRelationshipExamineMachinery,)
    class_dict = {
        "model": Model,
        "type_name": "%s_relationships" % (slugify("{}".format(Model.__name__)),),
        "form_class": object_relationships_form_factory(Model, company_types=company_types),
        "api_provider": relationship_viewsets[Model.__name__],
    }
    if company_types is not None:
        class_dict["company_types"] = company_types
    return type(str("%sRelationshipsExamineMachinery" % (Model.__name__,)), bases, class_dict)


# If subclassing this machinery, send the subclass to object_relationships_machinery_factory()
class BaseRelationshipExamineMachinery(examine.ExamineMachinery):
    can_add_new = False

    detail_template = "examine/relationship/detail.html"
    form_template = "examine/relationship/form.html"

    verbose_names = dict(
        COMPANY_TYPES_MAPPING, electric_utility="Electric Utility", gas_utility="Gas Utility"
    )

    # Configurable list of field overrides for the form and serializer classes.
    # Can be customized during call to object_relationships_machinery_factory() above.
    # Overridden during an API call by GET params sent in the url (as constructed by the
    # various "get_xxxxx_endpoint()" methods on this base class).
    company_types = [
        "builder",
        "rater",
        "provider",
        "eep",
        "hvac",
        "qa",
        "general",
        "gas_utility",
        "electric_utility",
        "architect",
        "developer",
        "communityowner",
    ]

    def __init__(self, *args, **kwargs):
        super(BaseRelationshipExamineMachinery, self).__init__(*args, **kwargs)

        # Ensure that API request objects can have their GET data read
        request = self.context["request"]
        if hasattr(request, "query_params"):
            company_types = request.query_params.getlist("fields")
            if company_types:
                self.company_types = company_types

    def can_delete_object(self, instance, user=None):
        return False

    def get_region_dependencies(self):
        model_type_name = slugify("{}".format(self.model.__name__))
        return {
            model_type_name: [
                {
                    "field_name": "id",
                    "serialize_as": "id",
                }
            ],
        }

    def get_context(self):
        context = super(BaseRelationshipExamineMachinery, self).get_context()
        context["creating"] = self.create_new
        return context

    def parameterize_context(self, instance=None, **kwargs):
        s = super(BaseRelationshipExamineMachinery, self).parameterize_context(instance, **kwargs)
        return s + "&fields={}".format("&fields=".join(self.company_types))

    def get_edit_actions(self, instance):
        if self.create_new:
            return []  # Primary region will issue a global save
        return super(BaseRelationshipExamineMachinery, self).get_edit_actions(instance)

    def get_region_endpoint_pattern(self, instance=None):
        return (
            reverse(
                self.region_endpoint.format(model=self.type_name_slug),
                kwargs={
                    "pk": "__id__",
                },
            )
            + self.parameterize_context()
        )

    def get_object_endpoint_pattern(self, instance=None):
        return (
            reverse(
                self.object_endpoint.format(model=self.type_name_slug),
                kwargs={
                    "pk": "__id__",
                },
            )
            + self.parameterize_context()
        )

    def get_form_kwargs(self, instance):
        # The dynamic relationship ObjectRelationshipForm requires the user for field customization.
        return {
            "user": self.context["request"].user,
            "company_types": self.company_types,
        }

    def _get_field_value(self, instance, field):
        return list(field.field.queryset.model.objects.filter(id__in=field.value()))

    def get_field_rater_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_provider_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_eep_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_hvac_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_utility_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_qa_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_general_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_architect_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_developer_value(self, instance, field):
        return self._get_field_value(instance, field)

    def get_field_communityowner_value(self, instance, field):
        return self._get_field_value(instance, field)


# # Don't use this directly.  It is programatically subclassed in the factory above
# class _SimpleHistoryExamineMachinery(examine.DatatableMachineryMixin, examine.ReadonlyMachinery):
#     can_add_new = False
#     region_template = 'examine/simple_history/history_region_table.html'
#     detail_template = 'examine/simple_history/history_detail_table.html'
#
#     def get_visible_fields(self, instance):
#         return ["Date", "User", "Object", "Type", "Fields", "Previous Values", "Current Values"]


# Tweaks specific to us
class AxisPrimaryMachinery(examine.PrimaryMachinery):
    region_template = "examine/bottomactions_region_with_relationships.html"


# Geocoded variant for Axis
class AxisGeocodedMachineryMixin(object):
    commit_instruction = "geocode"
    original_commit_instruction = None
    allow_geocoding = True

    def get_edit_actions(self, instance):
        actions = super(AxisGeocodedMachineryMixin, self).get_edit_actions(instance)
        for action in actions:
            # 'saveAll' will reflect on the region for it's commit_instruction,
            # but 'save' needs to be replaced so it targets geocoding explicitly.
            if action["instruction"] == "save":
                action["original_instruction"] = action["instruction"]
                action["instruction"] = "geocode"
                break
        return actions


class AxisGeocodedMachinery(AxisGeocodedMachineryMixin, examine.ExamineMachinery):
    pass
