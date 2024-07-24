import json

from django.http import Http404
from django.template import TemplateDoesNotExist
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, TemplateView

from .machinery import ExamineMachinery
from .utils import ExamineJSONEncoder

__author__ = "Autumn Valenta"
__date__ = "10-17-14  5:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class TemplatePreprocessorView(TemplateView):
    # Prefix for all valid url reversals, forcing served templates to begin with this substring.
    template_root = "examine/"

    def get_template_names(self):
        """Returns the matched url kwarg, containing the defined prefix."""
        return [self.kwargs["template"]]

    def get(self, *args, **kwargs):
        response = super(TemplatePreprocessorView, self).get(*args, **kwargs)
        try:
            # Force TemplateResponse render now instead of later
            return response.render()
        except TemplateDoesNotExist:
            raise Http404("Examine template not found")


class ExamineMixin(object):
    """View mixin for fetching context data about configured regions."""

    # Django generic view tweak
    template_name_suffix = "_examine"

    primary_machinery = None

    create_new = False

    def get_object(self):
        if self.create_new:
            return self._get_model()()
        return super(ExamineMixin, self).get_object()

    def get_object_name(self):
        if hasattr(self.object, "name"):
            return self.object.name
        return "{}".format(self.object)

    def add_machinery(self, machinery_instance, context_name=None):
        if not hasattr(self, "_machinery"):
            self._machinery = {}
        if not context_name:
            context_name = machinery_instance.type_name_slug
        self._machinery[context_name] = machinery_instance

    def get_machinery(self):
        self.add_machinery(self._get_default_machinery())
        return self._machinery

    def _get_model(self):
        if self.model:
            return self.model
        return self.get_queryset().model

    def _get_default_machinery(self):
        """Tries to build a machinery class with default settings for the default object."""
        name = str("Default{}Machinery".format(self.model.__name__))
        model = self._get_model()
        Machinery = type(
            name,
            (ExamineMachinery,),
            {
                "model": model,
                "type_name": model._meta.model_name,
            },
        )
        return Machinery(instance=self.object, create_new=self.create_new)

    def get_primary_region(self, regions):
        """Returns the first machinery's first Region tuple."""
        if self.primary_machinery:
            type_name_slug = self.primary_machinery.type_name_slug
        else:
            type_name_slug = list(regions.keys())[0]
        return regions[type_name_slug][0]

    def get_support_modules(self):
        modules = []
        for m in self.get_machinery().values():
            modules.extend(list(map(mark_safe, m.get_support_modules())))
        return modules

    # def get_regions(self):
    #     """ Iterates all linked machinery and gets regions associated to each. """
    #     regions = {}
    #     for context_name, machinery in self.get_machinery().items():
    #         regions[context_name] = machinery.get_regions()
    #     return regions

    # def get_regions_data(self):
    #     """ Returns the generated regions, primary region, and secondary regions list in a dict. """
    #     regions = self.get_regions()
    #     primary_region = self.get_primary_region(regions)
    #     secondary_regions = self.get_secondary_regions(regions)
    #     return {
    #         'regions': regions,
    #         'primary_region': primary_region,
    #         'secondary_regions': secondary_regions,
    #     }

    def get_regions_endpoints(self):
        machinery_specs = {}
        for context_name, machinery in self.get_machinery().items():
            # Store the key as a string so it can be put into template JS as-is.
            machinery_specs[context_name] = machinery.get_summary()

        if self.primary_machinery:
            primary_endpoint = machinery_specs[self.primary_machinery.type_name_slug]["endpoints"][
                0
            ]
        else:
            primary_endpoint = None

        return {
            "machinery_specs": machinery_specs,
            "regions": json.dumps(machinery_specs, cls=ExamineJSONEncoder),
            "primary_region": primary_endpoint,
        }

    def get_context_data(self, **kwargs):
        context = super(ExamineMixin, self).get_context_data(**kwargs)
        context.update(self.get_regions_endpoints())
        context["object_name"] = self.get_object_name()
        if self.primary_machinery:
            context["primary_type"] = self.primary_machinery.type_name_slug
            context["allow_geocoding"] = getattr(self.primary_machinery, "allow_geocoding", False)
        return context


class ExamineView(ExamineMixin, DetailView):
    pass
