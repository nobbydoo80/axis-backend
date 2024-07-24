"""models.py: core models"""


import logging

from django.db import models

__author__ = "Autumn Valenta"
__date__ = "2017-11-17 16:06:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)


# Cached subclassess of GenericAccessor mapped to dictionaries of models they've been applied to,
# mapped to the synthesized BetterGenericModel holding the foreignkey to said model.
models_cache = {}


def get_generic_models(Accessor):
    return models_cache[Accessor]


def get_generic_model(Accessor, Model):
    return models_cache[Accessor][Model]


class BaseBetterGenericModel(models.Model):
    """
    Base model for tracking multiple records on another related model, created by adding a subclass
    of BetterGenericAccessor on some other model.
    """

    # The runtime-synthesized subclass of this model is what goes into the
    # models_cache for a given Model-BetterGenericAccessor pairing used throughout
    # the codebase.

    class Meta:
        abstract = True


class BetterGenericAccessor(object):
    """
    Accessor subclassed and placed on a model to imply support for a concrete "generic" foreign key
    table.
    """

    model = BaseBetterGenericModel
    model_name = "{source_model}{model}"  # e.g., "{BuilderOrganization}{Association}"
    attrs = None
    fields = None
    fk_name = None  #'object'  # Leave ``None`` to generate according to parent model name
    related_name = "%(class)s"  # '{source_model}' & '{model}' are valid

    def __init__(self, model=None, attrs={}, fields={}, related_name=None, fk_name=None):
        if self.__class__ == BetterGenericAccessor:
            raise NotImplementedError("You must subclass this and initialize that instead.")

        self.model = model or self.model

        self.attrs = self.attrs.copy() if self.attrs else {}
        self.attrs.update(attrs)

        self.fields = self.fields.copy() if self.fields else {}
        self.fields.update(fields)

        self.related_name = related_name or self.related_name
        self.fk_name = fk_name or self.fk_name  # Might still be None after this
        self.models_cache = models_cache.setdefault(self.__class__, {})

    def contribute_to_class(self, cls, name):
        self.attr_name = name

        if self.fk_name is None:
            self.fk_name = cls._meta.model_name

        models.signals.class_prepared.connect(self.get_model, sender=cls)

    def get_model(self, sender, **kwargs):
        """Signal handler for building a BaseBetterGenericModel subclass on the target model."""
        if sender not in self.models_cache:
            factory_kwargs = self.get_model_factory_kwargs(
                **{
                    "generic_model": self.model,
                    "model_name": self.model_name,
                    "attrs": self.attrs,
                    "fields": self.fields,
                    "fk_name": self.fk_name,
                    "query_name": self.attr_name,
                    "related_name": self.related_name,
                }
            )
            self.models_cache[sender] = build_better_generic_model(sender, **factory_kwargs)
            self.finalize_model(sender, self.models_cache[sender], self.attr_name)

        return self.models_cache[sender]

    def get_model_factory_kwargs(self, **kwargs):
        return kwargs

    def finalize_model(self, sender, model, name):
        # Make access to the model simpler.  Django >= 1.8 took away this lookup
        # in favor of the more verbose 'related.related_model'
        self.model = model


def build_better_generic_model(
    source_model, generic_model, model_name, attrs, fields, fk_name, query_name, related_name
):
    """
    Constructs a subclass of BaseBetterGenericModel for ``source_model``, based on ``model``.  The
    ForeignKey from the source model to the generic one is queryable through the accessor attribute
    name (e.g., 'associations').

    Any fields provided via the ``fields`` dict will have their related_name values string-formatted
    via the new-style "{}" formatting to replace references to {source_model} and {model} with the
    appropriate runtime names, where "source_model" is the one hosting the related objects on itself
    and "model" is the name of the new related objects model.
    """

    attrs.update(
        {
            "__module__": source_model.__module__,
            fk_name: models.ForeignKey(
                source_model, related_name=query_name, on_delete=models.CASCADE
            ),
        }
    )

    formattable_kwargs = ["related_name"]
    format_values = {
        "source_model": source_model.__name__,
        "model": generic_model.__name__,
    }

    related_name = related_name.format(**format_values)
    format_values["related_name"] = related_name

    for field_name, (field_class, args, kwargs) in fields.items():
        for formattable_kwarg in formattable_kwargs:
            if formattable_kwarg in kwargs:
                kwargs[formattable_kwarg] = kwargs[formattable_kwarg].format(**format_values)
        attrs[field_name] = field_class(*args, **kwargs)

    if "Meta" in attrs and getattr(attrs["Meta"], "abstract", False):
        raise ValueError("Meta.abstract for %r should not be True." % (attrs["Meta"],))

    model_name = model_name.format(source_model=source_model.__name__, model=generic_model.__name__)
    return type(str(model_name), (generic_model,), attrs)
