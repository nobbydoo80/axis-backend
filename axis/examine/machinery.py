import time
import logging
from collections import OrderedDict
from operator import getitem
import json
import inspect

from django.db.models import Model
from django.db.models.query import QuerySet
from django.http import QueryDict
from django.urls import reverse
from django.forms import widgets
from django.forms.models import modelform_factory
from axis.core.six import safe_hasattr

from .utils import template_url

__author__ = "Autumn Valenta"
__date__ = "10-17-14  5:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

REGION_GETTER_NAMES = [
    "id",  # Generated
    "type_name",  # restframework API contenttype name, and the context name for templates
    "object_name",  # Friendly name for template output, by default the str() of the object
    "actions",  # List of ActionTuples
    "absolute_url",  # get_absolute_url() of the object, if it has one
    "passive_machinery",
    # Templates
    "region_template_url",
    "detail_template_url",
    "form_template_url",
    "delete_confirmation_template_url",
    # API sources
    "region_endpoint_pattern",
    "object_endpoint_pattern",
    "object_endpoint",  # the post/patch target
    "delete_endpoint",  # override can target m2m relationship, etc
    "relatedobjects_endpoint",  # inspected by frontend to warn user of deletion effects
    # Form specification
    "field_order",
    "fields",
    "visible_fields",
    "verbose_name",
    "verbose_names",
    # If given, will execute an actionbar instruction when loaded
    "default_instruction",
    "commit_instruction",
    # Slot for adding helpers to the region for rendering content about the object
    "helpers",
]

# TODO: Make this a getter for serializer.data, so only REGION_GETTER_NAMES is required
REGION_FIELD_NAMES = REGION_GETTER_NAMES + ["object"]

# Constants for less verbose subclass configuration
REGIONSET_DEFAULT_TEMPLATE = "examine/angular_regionset_default.html"
REGIONSET_PANEL_TEMPLATE = "examine/angular_regionset_panel.html"
REGIONSET_ACCORDION_TEMPLATE = "examine/angular_regionset_accordion.html"
REGIONSET_TABLE_TEMPLATE = "examine/angular_regionset_table.html"
REGIONSET_DATATABLE_TEMPLATE = "examine/angular_regionset_datatable.html"
REGIONSET_SIDETABS_TEMPLATE = "examine/angular_regionset_sidetabs.html"

REGION_DEFAULT_TEMPLATE = "examine/angular_region_default.html"
REGION_BOTTOMACTIONS_TEMPLATE = "examine/angular_region_bottomactions.html"
REGION_PANEL_TEMPLATE = "examine/angular_region_panel.html"
REGION_ACCORDION_TEMPLATE = "examine/angular_region_accordion.html"
REGION_TABLEROW_TEMPLATE = "examine/angular_region_tablerow.html"
REGION_DATATABLE_TEMPLATE = "examine/angular_region_datatable.html"
REGION_SIDETABS_TEMPLATE = "examine/angular_region_sidetabs.html"

DISPLAY_DEFAULT_TEMPLATE = "examine/angular_detail_default.html"
DISPLAY_TABLEROW_TEMPLATE = "examine/angular_detail_tablerow.html"
DISPLAY_DATATABLE_TEMPLATE = "examine/angular_detail_datatable.html"

FORM_DEFAULT_TEMPLATE = "examine/angular_form_default.html"
FORM_TABLEROW_TEMPLATE = "examine/angular_form_tablerow.html"

CONFIRM_DELETE_TEMPLATE = "examine/angular_delete_confirmation.html"

TEMPLATE_SETS = {
    "default": {
        "regionset": REGIONSET_DEFAULT_TEMPLATE,
        "region": REGION_DEFAULT_TEMPLATE,
        "detail": DISPLAY_DEFAULT_TEMPLATE,
        "form": FORM_DEFAULT_TEMPLATE,
        "delete_confirmation": CONFIRM_DELETE_TEMPLATE,
    },
    "primary": {
        "regionset": None,
        "region": REGION_BOTTOMACTIONS_TEMPLATE,
        "detail": DISPLAY_DEFAULT_TEMPLATE,
        "form": FORM_DEFAULT_TEMPLATE,
        "delete_confirmation": CONFIRM_DELETE_TEMPLATE,
    },
    "panel": {
        "regionset": REGIONSET_PANEL_TEMPLATE,
        "region": REGION_PANEL_TEMPLATE,
        "detail": DISPLAY_DEFAULT_TEMPLATE,
        "form": FORM_DEFAULT_TEMPLATE,
        "delete_confirmation": CONFIRM_DELETE_TEMPLATE,
    },
    "accordion": {
        "regionset": REGIONSET_ACCORDION_TEMPLATE,
        "region": REGION_ACCORDION_TEMPLATE,
        "detail": DISPLAY_DEFAULT_TEMPLATE,
        "form": FORM_DEFAULT_TEMPLATE,
        "delete_confirmation": CONFIRM_DELETE_TEMPLATE,
    },
    "table": {
        "regionset": REGIONSET_TABLE_TEMPLATE,
        "region": REGION_TABLEROW_TEMPLATE,
        "detail": DISPLAY_TABLEROW_TEMPLATE,
        "form": FORM_TABLEROW_TEMPLATE,
        "delete_confirmation": CONFIRM_DELETE_TEMPLATE,
    },
    "datatable": {
        "regionset": REGIONSET_DATATABLE_TEMPLATE,
        "region": REGION_DATATABLE_TEMPLATE,
        "detail": DISPLAY_DATATABLE_TEMPLATE,
        "form": None,
        "delete_confirmation": None,
    },
    "sidetabs": {
        "regionset": REGIONSET_SIDETABS_TEMPLATE,
        "region": REGION_SIDETABS_TEMPLATE,
        "detail": DISPLAY_DEFAULT_TEMPLATE,
        "form": FORM_DEFAULT_TEMPLATE,
        "delete_confirmation": CONFIRM_DELETE_TEMPLATE,
    },
}


# Widget classes can be added here to point at a callback for handling that widget.
# The vanilla Django widgets should all be handled via the
# BaseExamineMachinery.get_extra_widget_attrs callback, for simplicity in dealing with the default
# case. Callbacks will be sent the current machinery, the widget instance, and the simpler
# discoverable data on the widget.
def _widget_callback(*args, **kwargs):
    return BaseExamineMachinery.get_extra_widget_attrs(*args, **kwargs)


WIDGET_ATTR_GETTERS = OrderedDict(
    [
        (widgets.CheckboxInput, _widget_callback),
        (widgets.RadioSelect, _widget_callback),
        (widgets.Select, _widget_callback),
        (widgets.Textarea, _widget_callback),
    ]
)


# Default region setup
class BaseExamineMachinery(object):
    """Collection of methods that generate Region tuples for the examine templates and js."""

    # Must be declared on subclass!
    model = None
    form_class = None
    type_name = None  # API url reverse name
    api_provider = None
    commit_instruction = "save"  # Name of the action that finishes an Edit session

    # Public configuration for subclasses.  All are optional, since they have sane defaults.
    create_new = False  # flags a Create view variation instead of Edit
    can_add_new = True
    template_set = None
    support_modules = tuple()
    passive_machinery = False

    # Reversable api endpoint names
    new_object_endpoint = "apiv2:{model}-list"
    object_endpoint = "apiv2:{model}-detail"
    region_endpoint = "apiv2:{model}-region"
    new_region_endpoint = "apiv2:{model}-new-region"
    delete_success_url = None  # Deleting an object might mean the page is invalid, so this can be
    # returned to the client to indicate that they should go elsewhere.

    # Override action for Cancel when the region is in creation mode
    create_new_cancel_action = "destroy"

    # Model verbose_name override
    verbose_name = None
    verbose_name_plural = None

    # Individual overrides to the template_set option
    regionset_template = None
    region_template = None
    detail_template = None
    form_template = None
    delete_confirmation_template = None

    # Action button default styles
    action_type = "button"
    action_size = "xs"
    action_style = "default"

    # Configuration for common actions provided by default Examine machinery
    save_name = "Save"
    save_icon = None
    save_instruction = "save"
    cancel_name = "Cancel"
    cancel_icon = None
    cancel_instruction = "cancel"
    create_new_cancel_instruction = "destroy"
    edit_name = "Edit"
    edit_icon = None
    delete_name = "Delete"
    delete_icon = None

    # Auto-generated
    type_name_slug = None  # template-friendly slug version of type_name

    # Constructor values will be written here for later reference.
    instance = None
    objects = None
    context = None

    # Internal hack, disables serializer verbose_names by default so that old machinery classes
    # don't fail to instantiate ahead of when they sometimes expected to.
    # Try to turn this on as often as you can, or update machineries that aren't using it yet.
    use_serializer_verbose_names = False

    # Internal utilities to support region construction
    @classmethod
    def Region(cls, **kwargs):
        supplied = set(kwargs.keys())
        required = set(REGION_FIELD_NAMES)
        missing = required - supplied
        excess = supplied - required
        if excess:
            raise ValueError("Unknown keys for region configuration: %r" % (list(excess),))
        if missing:
            raise ValueError("Missing values for region: %r" % (list(missing),))
        return kwargs

    @classmethod
    def ActionGroup(cls, name, actions, style=None):
        return {
            "name": name,
            "actions": actions,
            "style": style,
        }

    @classmethod
    def Action(
        cls,
        name,
        instruction,
        is_mode=False,
        style=None,
        type: str | None = None,
        size=None,
        attrs=None,
        items=None,
        icon: str | None = None,
        href=None,
        disabled: bool = False,
        modal=None,
    ):
        """Data container class for headline action buttons

        :param name: The text on the button
        :param instruction: May not be set if `href` is set. The name of the JavaScript function to trigger on click
        :param is_mode: TODO: Document this param.
        :param style: TODO: Document this param.
        :param type: "link" or ...TODO: Document this param.
        :param size: TODO: Document this param.
        :param attrs: TODO: Document this param.
        :param items: TODO: Document this param.
        :param icon: Reference to a font-awesome icon. To get an icon named like "fa-bob", pass "bob"
        :param href: This may not be set if `instruction` is set - a URL to go to when clicked
        :param disabled: If True, the button will be disabled
        :param modal: TODO: Document this param.
        """
        if attrs is None:
            attrs = {}
        if style is None:
            style = cls.action_style
        if type is None:
            type = cls.action_type
        if size is None:
            size = cls.action_size
        return {
            "name": name,
            # Mutually exclusive options
            "instruction": instruction,
            "href": href,
            # Extras
            "icon": icon,  # fa-* name (without the "fa-")
            "is_mode": is_mode,
            "style": style,
            "type": type,
            "attrs": attrs,
            "items": items,
            "size": size,
            "disabled": disabled,
            "modal": modal,
        }

    def __init__(
        self,
        instance=None,
        objects=None,
        create_new=False,
        extra=0,
        max_num=None,
        min_num=None,
        context=None,
    ):
        # Set this as early as possible.  get_model() might want to inspect related data.
        self.context = dict(context) if context else {}

        if create_new and instance is None and objects is None:
            instance = self.get_model()()

        if instance:
            self.instance = instance
            self.objects = [instance]
        elif objects is not None:
            self.instance = None
            self.objects = list(objects)

        extra_available = 0
        if min_num:
            extra_available = min_num - len(self.objects)

        if extra:
            extra_available = 0
            if max_num:
                extra_available = len(self.objects) - max_num
            else:
                extra_available = extra

        if extra_available > 0:
            self.objects.extend([self.get_model()() for i in range(extra_available)])

        if self.instance is None and self.objects is None:
            raise ValueError(
                "%s requires one of the following init kwargs: instance, objects, "
                "create_new" % (self.__class__.__name__,)
            )

        if not hasattr(self, "get_objects"):
            setattr(self, "get_objects", lambda: self.objects)

        self.type_name_slug = self.type_name.replace("-", "_")  # naive slug
        self.create_new = create_new

    # Dynamic configuration hooks
    def get_model(self):
        return self.model

    def get_api_provider_instance(self, api_provider):
        instance = api_provider()
        instance.request = self.context.get("request")
        instance.format_kwarg = None
        instance.kwargs = {
            "_dummy": "This viewset was NOT instantiated by restframework.  There are no URL kwargs."
        }
        return instance

    # Primary access method from the view
    def get_summary(self):
        """Returns the context entry for this machinery type."""
        return {
            # Generics about the type
            "type_name": self.type_name,
            "type_name_slug": self.type_name_slug,
            "verbose_name": self.get_verbose_name(),
            "verbose_name_plural": self.get_verbose_name_plural(),
            "visible_fields": self.get_visible_fields(None, **self.get_visible_fields_kwargs(None)),
            "verbose_names": self.get_verbose_names(
                self.get_model()(), **self.get_verbose_names_kwargs(None)
            ),
            "new_region_url": self.get_new_region_endpoint(),
            "object_endpoint_pattern": self.get_object_endpoint_pattern(),
            "region_endpoint_pattern": self.get_region_endpoint_pattern(),
            "regionset_template_url": self.get_regionset_template_url(),
            "region_dependencies": self.get_region_dependencies(),
            "max_regions": self.get_max_regions(),
            # Locations to request actual details on each object over API
            "endpoints": [self.get_region_endpoint(o) for o in self.get_objects()],
        }

    def get_delete_success_url(self):
        return self.delete_success_url

    # Object-list getters, not dealing with the individual object(s), but the whole group
    def get_api_provider(self):
        return self.api_provider

    def _format_url_name(self, url_name, **kwargs):
        return url_name.format(**kwargs)

    def _reverse_url(self, url_name, *args, **kwargs):
        return reverse(url_name, args=args, kwargs=kwargs)

    def get_object_endpoint_pattern(self, instance=None):
        """
        Returns the object endpoint for a saved object where 'pk' is a placeholder that can be
        filled in once it has been determined by the frontend (after a save operation).  It may
        contain placeholders for any other values listed in ``get_region_dependencies()`` that are
        expected to be filled in at runtime by the network of machineries.
        """
        url_name = self._format_url_name(self.object_endpoint, model=self.type_name_slug)
        return self._reverse_url(url_name, pk="__id__") + self.parameterize_context()

    def get_region_endpoint(self, obj):
        """
        Returns the correct endpoint for retrieving an object's region serialization.  If the
        machinery is in create_new=True mode, the ``new_region_endpoint`` will be reversed and
        returned.  If instead this method is called with one of the machinery's bound objects, the
        ``region_endpoint`` is reversed.
        """
        if obj.pk is None:
            if self.new_region_endpoint in [None, ""]:
                return None
            # Don't call get_new_region_endpoint() because that method will return None
            # if the machinery disallows the add-another workflow.
            url_name = self._format_url_name(self.new_region_endpoint, model=self.type_name_slug)
            return self._reverse_url(url_name) + self.parameterize_context(obj)

        url_name = self._format_url_name(self.region_endpoint, model=self.type_name_slug)
        return self._reverse_url(url_name, pk=obj.pk) + self.parameterize_context(obj)

    def get_region_endpoint_pattern(self, instance=None):
        """
        Returns the region endpoint for a saved object where 'pk' is a placeholder that can be
        filled in once it has been determined by the frontend (after a save operation).  This is
        available so that, in a situation where a region in create_new=True mode which shares an
        unsaved instance with another region, either one can be saved first to create the underlying
        instance and generate a real pk, and the other region can borrow that pk and reload itself
        out of create_new=True mode and into an edit mode on an existing object.
        """
        url_name = self._format_url_name(self.region_endpoint, model=self.type_name_slug)
        return self._reverse_url(url_name, pk="__id__") + self.parameterize_context()

    def get_new_region_endpoint(self):
        """
        Returns the reversed ``new_region_endpoint``.  If ``self.can_add_new`` is False (e.g., the
        machinery is a subclass of SingleObjectMachinery), then None is returned.
        """
        if self.can_add_new and self.new_region_endpoint:
            url_name = self._format_url_name(self.new_region_endpoint, model=self.type_name_slug)
            return self._reverse_url(url_name) + self.parameterize_context()
        return None

    def get_regionset_template_url(self):
        """
        Returns the 'regionset' template for the selected template suite, as specified by
        ``self.template_set``
        """
        template = None
        if self.regionset_template:
            template = self.regionset_template
        else:
            template_set = self.get_template_set()
            if template_set is None:
                raise ValueError(
                    "%s requires a declared class 'template_set' setting, or an explicit "
                    "attribute or getter method for 'regionset_template'."
                    % (self.__class__.__name__,)
                )
            template = template_set["regionset"]
            if template is None:
                return None
        return template_url(template)

    def get_max_regions(self):
        return None

    def get_regions(self, **overrides):
        """
        Returns a list-like object of regions per each object in the set.
        """
        if hasattr(self, "configured_regions"):
            return self.configured_regions

        regions = []

        # Create the Regions for each instance in get_objects()
        for obj in self.get_objects():
            region_data = {}

            # Announce the new instance to the machinery for external hooks
            self.configure_for_instance(obj)

            for k in REGION_GETTER_NAMES:
                if k not in region_data:
                    kwargs_getter = getattr(self, "get_{}_kwargs".format(k), None)
                    if kwargs_getter:
                        kwargs = kwargs_getter(instance=obj)
                    else:
                        kwargs = {}
                    getter = getattr(self, "get_{}".format(k))
                    region_data[k] = getter(instance=obj, **kwargs)

            region_data["object"] = self.serialize_object(obj)
            region = self.Region(**region_data)
            regions.append(region)

        self.configured_regions = regions
        return self.configured_regions

    # Machinery settings for the serialization stage
    def get_template_set(self):
        return TEMPLATE_SETS.get(self.template_set)

    def get_support_modules(self):
        modules = list(self.support_modules)
        if self.get_template_set() == "datatable":
            modules.append("datatable")
        return modules

    def get_action_groups(self, instance):
        return ["static", "default", "edit"]

    def serialize_form_spec(self, instance, form):
        """Returns a JSON-compatible serialization of the machinery's form field configuration."""

        data = {}

        for field in form:
            item = {
                # BoundField data points
                "field_name": field.name,
                "prefixed_name": field.html_name,
                "help_text": field.help_text,
                "label": field.label,
                # Field data points
                "value": field.value(),
                # Should we include this?  How useful is it in this setup?  (There isn't an 'error'
                # class because we're not binding the form to data.)
                # 'css_classes': field.css_classes(),
            }

            # FIXME: Just because the object isn't saved doesn't mean its other attributes can't be
            # inspected for label_from_instance, but there are some oddities around m2m fields.
            if hasattr(field.field, "label_from_instance"):
                related_obj = None
                get_label_from_instance = field.field.label_from_instance
                label_from_instance_kwargs = {}
                if hasattr(field.field.widget, "label_from_instance"):
                    get_label_from_instance = field.field.widget.label_from_instance
                if "request" in inspect.getfullargspec(get_label_from_instance).args:
                    label_from_instance_kwargs["request"] = self.context.get("request")

                if field.name in form.initial and form.initial[field.name] is not None:
                    related_obj = form.initial[field.name]

                elif safe_hasattr(instance, field.name):
                    try:
                        related_obj = getattr(instance, field.name)
                    except (AttributeError, field.field.queryset.model.DoesNotExist):
                        pass  # Keep related_obj None
                elif instance.pk:
                    # Ask the machinery to retrieve a value for a given instance + attr pair.
                    # If the field is virtual, but can be obtained with some business logic, then
                    # we should be able to provide a value.
                    callback = getattr(self, "get_field_{}_value".format(field.name), None)
                    if callback:
                        related_obj = callback(instance, field)

                if hasattr(related_obj, "all"):
                    related_obj = list(related_obj.all()) if instance.pk else []

                _choices = None  # lazy populated dict, because it might be hugely expensive

                if isinstance(related_obj, list):
                    value_labels = []

                    for obj in related_obj:
                        if hasattr(obj, "pk"):
                            value_label = get_label_from_instance(obj, **label_from_instance_kwargs)
                        elif obj is None:
                            value_label = ""
                        else:
                            if hasattr(field.field, "queryset") and field.field.queryset.exists():
                                try:
                                    value_label = "{}".format(field.field.queryset.get(pk=obj))
                                except Exception:
                                    if _choices is None:
                                        _choices = dict(field.field.choices)
                                    value_label = _choices.get(obj, "")
                            else:
                                if _choices is None:
                                    _choices = dict(field.field.choices)
                                value_label = _choices.get(obj, "")
                        value_labels.append(value_label)
                    item["value_label"] = value_labels
                else:
                    if hasattr(related_obj, "pk"):
                        item["value_label"] = get_label_from_instance(
                            related_obj, **label_from_instance_kwargs
                        )
                    elif related_obj is None:
                        item["value_label"] = ""
                    else:
                        if hasattr(field.field, "queryset") and field.field.queryset.exists():
                            try:
                                item["value_label"] = "{}".format(
                                    field.field.queryset.get(pk=related_obj)
                                )
                            except Exception:
                                if _choices is None:
                                    # https://docs.djangoproject.com/en/3.1/ref/forms/fields/#modelchoiceiterator
                                    _choices = dict(
                                        [(str(c[0]), c[1]) for c in field.field.choices]
                                    )
                                item["value_label"] = _choices.get(
                                    related_obj, "{}".format(related_obj)
                                )
                        else:
                            if _choices is None:
                                _choices = dict([(str(c[0]), c[1]) for c in field.field.choices])
                            item["value_label"] = _choices.get(
                                related_obj, "{}".format(related_obj)
                            )

            # Axis-specific hack for our convension for de-obfuscating the filename
            elif hasattr(instance, "filename"):
                filename = instance.filename
                if callable(filename):
                    filename = filename()
                item["value_label"] = filename

            else:
                item["value_label"] = None

            item["options"] = self.serialize_field_spec(instance, field.field)
            item["widget"] = self.serialize_widget_spec(instance, field.field.widget)
            data[item["field_name"]] = item

        return data

    def serialize_field_spec(self, instance, field):
        """Reads attributes from the given Field instance."""

        # Things that appear on the built-in fields
        common_attrs = (
            "required",
            # Constraints
            "max_length",
            "min_length",
            "max_value",
            "min_value",
            "max_digits",
            "max_decimal_places",
            "max_whole_digits",
            "allow_empty_file",
            "empty_value",
            # django_select2 ajax fields
            "max_results",
        )

        data = {k: getattr(field, k, None) for k in common_attrs}

        # Special case for RegexField, which converts its regex to a validator callback, but which
        # we would need on the frontend to do the lord's work.
        if hasattr(field, "_regex"):
            data["regex"] = field._regex

        return data

    def serialize_widget_spec(self, instance, widget):
        """Reads attributes from the given Widget instance."""
        common_attrs = (
            "is_hidden",
            "is_localized",
            "needs_multipart_form",
            "input_type",
            "format",
            "allow_multiple_selected",
            "attrs",
            # ClearableFileInput adds some unique things
            "initial_text",
            "input_text",
            "clear_checkbox_label",
            "template_with_initial",
            "template_with_clear",
            # django_select2
            "widget_id",
            "relationship_add_url",
        )

        # Let django_select2 widgets build important attributes
        widget.build_attrs({})
        if hasattr(widget, "set_to_cache"):
            widget.set_to_cache()

        # Hidden widgets still end up having a full 'choices' list, so avoid inspecting that.
        if not widget.is_hidden and not getattr(widget, "widget_id", None):
            common_attrs += ("choices",)

        data = {k: getattr(widget, k, None) for k in common_attrs}

        # Debug
        data["_widget"] = widget.__class__.__name__

        for Widget, callback in WIDGET_ATTR_GETTERS.items():
            if isinstance(widget, Widget):
                data = callback(self, widget, data)
                break

        return data

    def get_extra_widget_attrs(self, widget, data):
        """Inspects the default Django widgets for known non-attribute instance characteristics."""
        if isinstance(widget, widgets.CheckboxInput):
            data["input_type"] = "checkbox"
        elif isinstance(widget, widgets.RadioSelect):
            data["input_type"] = "radio"
        elif isinstance(widget, widgets.Select):
            data["input_type"] = "select"
        elif isinstance(widget, widgets.Textarea):
            data["input_type"] = "textarea"

        return data

    def serialize_object(self, instance):
        api_provider = self.get_api_provider()
        if api_provider:
            obj = instance
            # if instance.pk is None:
            #     obj = None
            api_provider_instance = self.get_api_provider_instance(api_provider)
            serializer = api_provider_instance.get_serializer(instance=obj)
            data = serializer.data
        else:
            data = instance
        return data

    def get_form_class(self):
        # This form will never be initialized with request data because it is only used to set up
        # how the fields will behave.  The API will be
        form_class = self.form_class
        if not form_class:
            # Maybe one day we should add lookups for attributes that provide "fields", "exclude",
            # "widgets", "labels", etc, etc.
            form_class = modelform_factory(self.get_model(), exclude=[])
        return form_class

    def get_form(self, instance):
        """Instantiates the form class backing the machinery's editing capabilities."""
        form_class = self.get_form_class()
        kwargs = self.get_form_kwargs(instance)
        return form_class(instance=instance, **kwargs)

    def get_form_kwargs(self, instance):
        return {}

    # Permission getters
    def can_delete_object(self, instance, user=None):
        if user:
            if hasattr(instance, "can_be_deleted"):
                return instance.can_be_deleted(user)
            elif hasattr(instance, "can_delete"):
                return instance.can_delete(user)
            return user.has_perm(
                "{meta.app_label}.delete_{meta.model_name}".format(meta=instance._meta)
            )
        return False

    def can_edit_object(self, instance, user=None):
        if user:
            if hasattr(instance, "can_be_edited"):
                return instance.can_be_edited(user)
            elif hasattr(instance, "can_edit"):
                return instance.can_edit(user)
            return user.has_perm(
                "{meta.app_label}.change_{meta.model_name}".format(meta=instance._meta)
            )
        return False

    # Internal helper for default set of value getters
    def _get_instance_form(self, instance):
        """Common form getter for callbacks so the form isn't wastefully built more than once."""
        _form_obj_id = getattr(self, "_form_obj_id", None)
        if id(instance) != _form_obj_id:
            form = self.get_form(instance)
            self._form = form
            self._form_obj_id = id(instance)
        return self._form

    def _get_serializer(self, **kwargs):
        class request:  # pylint: disable=invalid-name
            class MissingUser:
                id = "fake"
                username = "fake"

            user = MissingUser()

        serializer_class = self.api_provider().get_serializer_class()
        return serializer_class(**kwargs)

    # URL building helper
    def get_context(self):
        return dict(self.context)

    def parameterize_context(self, instance=None, **kwargs):
        """
        Returns a urlencoded GET parameter string (including the leading "?") that contains data
        saved on ``self.context``.  This should always be appended to queries for examine API
        endpoints that return region serializations.

        Any ``kwargs`` sent to this method will be added to that context during serialization in a
        fashion such that inspecting request.GET in the API will yield those values first, in the
        event that the machinery context already had a value for that key.

        This method is guaranteed to return at least the string "?", making it safe to call super()
        and then add arbitrary extra parameters.
        """
        q = QueryDict("", mutable=True)

        def dump_value(v):
            v = json.dumps(v)
            if v.startswith('"'):
                v = v[1:-1]
            return v

        unserializable_context_keys = {"request", "lightweight"}
        for k, v in self.get_context().items():
            if k not in unserializable_context_keys:
                if isinstance(v, Model):
                    v = v.pk
                elif isinstance(v, QuerySet):
                    v = list(v.values_list("pk", flat=True))
                if not isinstance(v, (list, tuple, set)):
                    v = [v]
                v = list(map(dump_value, v))  # nice values to hide Python
                for v_ in reversed(v):  # reversed so first item is set last, dominant in querydict
                    q[k] = v_

        q.update(kwargs)  # Doing this last so they are the prominent k-v pairs in the querydict
        q.setlist("machinery", [self.__class__.__name__])

        return "?%(context)s" % {"context": q.urlencode()}

    # Hook called before region data is generated for an instance
    def configure_for_instance(self, instance):
        """
        Hook for setting up values on the machinery, called each time a new instance goes through
        the machinery for serialization.
        """
        pass

    # Default fallback getters if subclass fails to define an override.
    # Optional getters can exist for "get_xxxxx_kwargs()" to supply a dict for additional kwargs
    # that may be required for a call to "get_xxxxx()".
    def get_actions(self, instance):
        """Returns the base set of actions that a region can use by default."""
        action_groups = {}.fromkeys(self.get_action_groups(instance))

        for name in action_groups:
            action_list_getter = getattr(self, "get_{}_actions".format(name))
            group = self.ActionGroup(name, actions=action_list_getter(instance=instance))
            action_groups[name] = group

        return action_groups

    def get_static_actions(self, instance) -> list:
        actions = []
        return actions

    def get_default_actions(self, instance):
        actions = []

        if instance.pk is None:
            return actions

        request = self.context.get("request", None)
        if request:
            user = request.user
        else:
            user = None

        if self.can_delete_object(instance, user=user):
            actions.append(
                self.Action(self.delete_name, instruction="delete", icon=self.delete_icon)
            )

        if self.can_edit_object(instance, user=user):
            actions.append(
                self.Action(
                    self.edit_name,
                    instruction="edit",
                    icon=self.edit_icon,
                    is_mode=True,
                    style="primary",
                )
            )

        return actions

    def get_edit_actions(self, instance):
        cancel_instruction = self.cancel_instruction

        if instance.pk is None:
            cancel_instruction = self.create_new_cancel_instruction

        actions = [
            self.Action(self.cancel_name, instruction=cancel_instruction, icon=self.cancel_icon),
            self.Action(
                self.save_name,
                instruction=self.save_instruction,
                style="primary",
                icon=self.save_icon,
            ),
        ]
        return actions

    def get_id(self, instance):
        type_name_slug = self.type_name.replace("-", "_")
        if instance.pk is None:
            id = getattr(instance, "__examine_id", None)
            if id is None:
                id = "_{}".format(int(time.time()))
                instance.__examine_id = id
        else:
            id = instance.pk
        return "{type}_{id}".format(type=type_name_slug, id=id)

    def get_type_name(self, instance):
        return self.type_name

    def get_object_name(self, instance):
        if instance.pk is None:
            return "New {}".format(self.get_verbose_name())
        return "{}".format(instance)

    def get_passive_machinery(self, instance):
        return self.passive_machinery

    def get_default_instruction(self, instance):
        if instance.pk is None:
            return "edit"
        return None

    def get_commit_instruction(self, instance):
        return self.commit_instruction

    def get_region_template_url(self, instance):
        """
        Returns ``self.region_template``, or else the 'region' template for the selected template
        suite, as specified by ``self.template_set``
        """
        template = None
        if self.region_template:
            template = self.region_template
        else:
            template_set = self.get_template_set()
            if template_set is None:
                raise ValueError(
                    "%s requires a declared class 'template_set' setting, or an explicit "
                    "attribute or getter method for 'region_template'." % (self.__class__.__name__,)
                )
            template = template_set["region"]
            if template is None:
                return None
        return template_url(template)

    def get_detail_template_url(self, instance):
        """
        Returns ``self.detail_template``, or else the 'detail' template for the selected template
        suite, as specified by ``self.template_set``
        """
        template = None
        if self.detail_template:
            template = self.detail_template
        else:
            template_set = self.get_template_set()
            if template_set is None:
                raise ValueError(
                    "%s requires a declared class 'template_set' setting, or an explicit "
                    "attribute or getter method for 'detail_template'." % (self.__class__.__name__,)
                )
            template = template_set["detail"]
            if template is None:
                return None
        return template_url(template)

    def get_form_template_url(self, instance):
        """
        Returns ``self.form_template``, or else the 'form' template for the selected template suite,
        as specified by ``self.template_set``
        """
        template = None
        if self.form_template:
            template = self.form_template
        else:
            template_set = self.get_template_set()
            if template_set is None:
                raise ValueError(
                    "%s requires a declared class 'template_set' setting, or an explicit "
                    "attribute or getter method for 'form_template'." % (self.__class__.__name__,)
                )
            template = template_set["form"]
            if template is None:
                return None
        return template_url(template)

    def get_delete_confirmation_template_url(self, instance):
        """
        Returns ``self.delete_confirmation_template``, or else the 'delete_confirmation' template
        for the selected template suite, as specified by ``self.template_set``
        """
        template = None
        if self.delete_confirmation_template:
            template = self.delete_confirmation_template
        else:
            template_set = self.get_template_set()
            if template_set is None:
                raise ValueError(
                    "%s requires a declared class 'template_set' setting, or an explicit "
                    "attribute or getter method for 'delete_confirmation_template'."
                    % (self.__class__.__name__,)
                )
            template = template_set["delete_confirmation"]
            if template is None:
                return None
        return template_url(template)

    def get_absolute_url(self, instance):
        """Returns ``instance.get_absolute_url()`` if the method is available, else None."""
        if instance.pk is not None and hasattr(instance, "get_absolute_url"):
            return instance.get_absolute_url()
        return None

    def get_object_endpoint(self, instance):
        """
        Returns the reversed ``object_endpoint``, or if the machinery is in create_new=True mode,
        returns the reversed ``new_object_endpoint``.
        """

        kwargs = {}
        if instance.pk is None:
            endpoint = self.new_object_endpoint
            if endpoint is None:
                return None
        else:
            endpoint = self.object_endpoint
            kwargs["pk"] = instance.pk

        url_name = self._format_url_name(endpoint, model=self.type_name_slug)
        return self._reverse_url(url_name, **kwargs) + self.parameterize_context()

    def get_delete_endpoint(self, instance):
        """
        Endpoint that can remove this object.  In many cases this will be the object's own url and
        the frontend can request it via the DELETE http method.

        Special cases can target an m2m through model in order to simply remove associations, rather
        than actually delete the object from the database.
        """
        if instance.pk is None:
            return None
        return self.get_object_endpoint(instance)

    def get_relatedobjects_endpoint(self, instance):
        """
        Returns the url for retrieving the tree of related objects affected by cascading deletion.
        """
        return reverse(
            "apiv2:%s_relatedobjects-detail" % (self.get_model().__name__.lower(),),
            kwargs={"pk": instance.pk},
        )

    def get_visible_fields_kwargs(self, instance):
        """Builds a dict of kwargs to be sent to ``get_visible_fields()``"""
        return {"form": self._get_instance_form(instance)}

    def get_visible_fields(self, instance, form):
        """Returns the form field names on the sample form's ``visible_fields()`` list."""
        visible_fields = getattr(self, "visible_fields", None)
        if visible_fields is None:
            visible_fields = [field.name for field in form.visible_fields()]
        return visible_fields

    def get_field_order_kwargs(self, instance):
        """Builds a dict of kwargs to be sent to ``get_field_order()``"""
        return {"form": self._get_instance_form(instance)}

    def get_field_order(self, instance, form):
        """Returns the form field names in the order they should appear by default."""
        return [f.name for f in form]

    def get_fields_kwargs(self, instance):
        """Builds a dict of kwargs to be sent to ``get_fields()``"""
        return {"form": self._get_instance_form(instance)}

    def get_fields(self, instance, form):
        """
        Serializes the nominated form class field spec for a JSON-friendly interpretation on the
        frontend.
        """
        return self.serialize_form_spec(instance, form)

    def get_verbose_name(self, instance=None):
        """Returns the model's ``Meta.verbose_name`` value."""
        if self.verbose_name:
            return self.verbose_name
        return self.get_model()._meta.verbose_name

    def get_verbose_name_plural(self, instance=None):
        """Returns the model's ``Meta.verbose_name_plural`` value."""
        if self.verbose_name_plural:
            return self.verbose_name_plural
        return self.get_model()._meta.verbose_name_plural

    def get_verbose_names_kwargs(self, instance):
        """Builds a dict of kwargs to be sent to ``get_verbose_names()``"""
        return {
            "form": self._get_instance_form(instance),
            "serializer": self._get_serializer() if self.use_serializer_verbose_names else None,
        }

    def get_verbose_names(self, instance, form=None, serializer=None, **kwargs):
        """
        Returns a dict of model field names mapped to their ``verbose_name``.  If any form fields
        define their own "label" value, that value will override the model field's original
        ``verbose_name``.  Fields on the form that are missing from the model are also added to the
        dictionary.
        """
        verbose_names = getattr(self, "verbose_names", None)
        if verbose_names is None:
            verbose_names = {
                f.name: (
                    (getattr(form.fields.get(f.name), "label", None) if form else None)
                    or (
                        getattr(getitem(serializer.fields, f.name), "label", None)
                        if serializer and f.name in serializer.fields
                        else None
                    )
                    or f.verbose_name
                    or f.name
                )
                for f in (self.model._meta.fields if self.model else [])
            }
        return verbose_names

    def get_region_dependencies(self):
        """
        Returns a dict where a key is the "type_name" of another machinery found on a loaded page,
        and the value is a list, each item in that list being a small dictionary containing just
        two keys: 'field_name' and 'serialize_as'.  Each item in the list represents a request for
        the selected other machinery to supply the named field.  'serialize_as' is the name the
        fetched dependency value will use when placed on the local object before being sent to the
        object_endpoint for save operations.

        Example dependency declaration:

            return {
                'other_machinery_typename': [{
                    'field_name': 'id',
                    'serialize_as': 'relatedthing_id',
                }],
            }
        """
        return {}

    def get_helpers(self, instance):
        """
        Returns a dict of JSON-friendly data that the machinery can use on the client frontend in
        templates or javascript to more richly present the object without making additional AJAX
        queries.
        """
        return {
            "verbose_name": self.get_verbose_name(),
        }


# Region style mixins
class PlainMachineryMixin(object):
    """Normal machinery with default template set."""

    template_set = "default"


class SingleObjectMixin(object):
    """Mixin for forcing instantiation to target only one instance."""

    can_add_new = False
    template_set = "default"

    def __init__(self, instance=None, create_new=False, context=None):
        super(SingleObjectMixin, self).__init__(
            instance=instance, create_new=create_new, context=context
        )


class PrimaryMachineryMixin(SingleObjectMixin):
    """Minor variant of the default machinery to support our main object strategies."""

    object_list_url = None

    template_set = "primary"

    @staticmethod
    def ActionGroup(name, *args, **kwargs):
        if name == "edit":
            kwargs.setdefault("style", "well well-sm wide")
        return BaseExamineMachinery.ActionGroup(name, *args, **kwargs)

    @staticmethod
    def Action(*args, **kwargs):
        """Default the button type to "button-md" instead of "button-xs"."""
        kwargs.setdefault("size", "md")
        return BaseExamineMachinery.Action(*args, **kwargs)

    def get_edit_actions(self, instance):
        """Flips action button order and makes Save into SaveAll"""

        actions = super(PrimaryMachineryMixin, self).get_edit_actions(instance)
        actions.reverse()
        if instance.pk is None:
            for action in actions:
                if action["instruction"] == "destroy":
                    action.update(
                        {
                            "instruction": None,
                            "type": "link",
                            "href": self.get_object_list_url(),
                        }
                    )
                if action["instruction"] == "save":
                    action["instruction"] = "saveAll"
        return actions

    def get_object_list_url(self):
        if self.object_list_url:
            return self.object_list_url
        reverse_urls = [
            "{app}:{model}:list",
            "{app}:{model}_list",
            "{app}:{model}-list",
            "{model}:list",
            "{model}_list",
            "{model}-list",
        ]
        app_label = self.get_model()._meta.app_label
        model_name = self.get_model()._meta.model_name
        for url_name in reverse_urls:
            name = url_name.format(app=app_label, model=model_name)
            try:
                return self._reverse_url(name)
            except Exception:
                continue

        raise ValueError(
            "No url could be automatically discovered for a '%s.%s' "
            "list view" % (app_label, model_name)
        )


class PanelMachineryMixin(object):
    template_set = "panel"


class TableMachineryMixin(object):
    template_set = "table"

    # edit_name = ""
    # edit_icon = 'pencil-square-o'
    delete_name = ""
    delete_icon = "trash-o"


class SideTabsMachineryMixin(object):
    template_set = "sidetabs"


# class DatatableMachineryMixin(object):
#     template_set = "datatable"


class ReadonlyMachineryMixin(object):
    """Machinery that uses only a display_content setup."""

    # This is useful for loading deferred sections of a page that don't actually require a form.

    commit_instruction = None

    can_add_new = False

    # Instead of forcing get_actions() to return an empty list, we'll return individual empty lists
    # for each action strip, so that a subclass could still easily specify static actions if it
    # needed to.

    def get_static_actions(self, instance):
        return []

    def get_default_actions(self, instance):
        return []

    def get_edit_actions(self, instance):
        return []

    def get_delete_endpoint(self, instance):
        return None

    # Gut the form components
    def get_form_template_url(self, instance):
        """Returns None, since no edit mode is allowed."""
        return None

    def get_form(self, instance):
        return None

    def get_field_order_kwargs(self, instance):
        return {}

    def get_field_order(self, instance):
        return None

    def get_fields_kwargs(self, instance):
        return {}

    def get_fields(self, instance):
        return None

    def get_visible_fields_kwargs(self, instance):
        return {}

    def get_visible_fields(self, instance):
        visible_fields = getattr(self, "visible_fields", None)
        if visible_fields is not None:
            return list(visible_fields)
        if instance:
            return [f.name for f in instance._meta.get_fields()]

    def get_verbose_names_kwargs(self, instance):
        return {
            "form": None,
            "serializer": self._get_serializer(),
        }


class PassiveMachineryMixin(object):
    passive_machinery = True


# Region concrete classes
class ExamineMachinery(PlainMachineryMixin, BaseExamineMachinery):
    pass


class SingleObjectMachinery(SingleObjectMixin, BaseExamineMachinery):
    pass


class PrimaryMachinery(PrimaryMachineryMixin, BaseExamineMachinery):
    pass


class PanelMachinery(PanelMachineryMixin, BaseExamineMachinery):
    pass


class TableMachinery(TableMachineryMixin, BaseExamineMachinery):
    pass


class SideTabsMachinery(SideTabsMachineryMixin, BaseExamineMachinery):
    pass


# class DatatableMachinery(DatatableMachineryMixin, BaseExamineMachinery):
#     pass


class ReadonlyMachinery(ReadonlyMachineryMixin, PlainMachineryMixin, BaseExamineMachinery):
    pass


class PassiveMachinery(PassiveMachineryMixin, PlainMachineryMixin, BaseExamineMachinery):
    pass
