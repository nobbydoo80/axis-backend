import logging
from functools import partial

from .. import exceptions

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class unset:
    pass


class ConfigReaderType(type):
    """
    Reads items out of a ConfigReader's ``lookup_methods`` shorthand dict and generates those
    methods on the class.
    """

    def __new__(cls, name, bases, attrs):
        reader_class = super(ConfigReaderType, cls).__new__(cls, name, bases, attrs)

        # Needs to be built per-path so that the inner 'lookup' reference in the lambda isn't
        # referencing a loop closure
        def get_unwrapper(path):
            lookup = partial(reader_class.lookup, path=path)
            return lambda *args, **kwargs: lookup(*args, **kwargs)

        for name, path in attrs.get("lookup_methods", {}).items():
            getter_name = "get_{}".format(name)
            unwrapper_f = get_unwrapper(path)
            setattr(reader_class, getter_name, unwrapper_f)
        return reader_class


class ConfigReader(metaclass=ConfigReaderType):
    """
    Pythonic wrapper around an imported 'config' dict to streamline access to optional and thus
    potentially missing fields.
    """

    lookup_methods = {
        "state_machine": "object_types.{object_type}.state_machine",
        "name": "name",
        "object_url": "object_types.{object_type}.urls.{url_type}",
        "object_list_url": "object_types.{object_type}.urls.list",
        "object_add_url": "object_types.{object_type}.urls.add",
        "parent_type": "object_types.{object_type}.parent_type",
        "eep_program_tab_label": "object_types.{object_type}.programs.tab_label",
        "eep_program_verbose_name": "object_types.{object_type}.programs.verbose_name",
        "eep_program_verbose_name_plural": "object_types.{object_type}.programs.verbose_name_plural",
        "eep_program_display_link": "object_types.{object_type}.programs.display_link",
        "eep_program_parent_sync": "object_types.{object_type}.programs.parent_sync",
        "repr_setting": "object_types.{object_type}.repr_setting",
        "object_type_state_label": "object_types.{object_type}.state_label",
        "object_type_name": "object_types.{object_type}.name",
        "object_type_name_plural": "object_types.{object_type}.name_plural",
        "object_type_spec": "object_types.{object_type}",
        "object_type_specs": "object_types",
        "settings_spec": "object_types.{object_type}.settings",
        "data_spec": "object_types.{object_type}.data",
        "max_programs": "object_types.{object_type}.programs.max",
        "examine_object_templates": "object_types.{object_type}.examine.certifiableobject",
        "examine_status_templates": "object_types.{object_type}.examine.workflowstatus",
    }

    def __init__(self, config):
        self.config = config

    def __getitem__(self, k):
        """Forwards item access directly to the underlying data."""
        return self.config[k]

    def lookup(self, path, *bits, **format_kwargs):
        """
        Uses ``bits`` as a list of keys to access.  They will be joined together similar to an
        os.path.join(), where the separator is a ``.``.  Any item in the list can contain dotted
        notation of its own and it will be handled gracefully.
        """

        bits = [path] + list(bits)

        format_kwargs.setdefault("default", unset)
        default = format_kwargs.pop("default")
        bits = ".".join(bits).split(".")  # implode the explode again to handle mixed expressions

        obj = self.config
        for bit in bits:
            # Fill out formatting vars
            try:
                bit = bit.format(**format_kwargs)
            except KeyError as e:
                raise exceptions.MissingFormatKwargError(e)

            # Perform piece of lookup
            try:
                obj = self.get_component(obj, bit)
            except KeyError as e:
                if default is unset:
                    raise exceptions.MissingSettingError(e)
                obj = default
                break

        return obj

    def get_component(self, obj, k):
        """Handles lookups of ``k`` in various ``obj`` types."""
        if isinstance(obj, dict):
            return obj[k]
        # elif isintance(obj, (tuple, list)):
        #     return obj[k]

    # Convenience methods that don't map to a single data lookup
    def supports_object_type(self, object_type):
        """Returns True/False if the config has a spec for the given object_type."""
        type_spec = self.get_object_type_spec(object_type=object_type, default=None)
        return type_spec is not None

    def uses_workflow_status(self, object_type):
        """Returns True/False for if the object type allows state or data tracking."""

        type_spec = self.get_object_type_spec(object_type=object_type)

        if type_spec.get("state_machine"):
            return True

        if type_spec.get("data"):
            return True

        return False

    def get_settings_specs(self, object_type, **settings):
        """Returns all specs, data/settings and required/optional, the object_type provides."""
        from ..api.utils import restrict_field_spec

        data_spec = self.get_settings_spec(object_type=object_type)

        settings["object_type"] = object_type  # Make sure this still goes in as a setting
        return restrict_field_spec(data_spec, settings)

    def get_data_specs(self, object_type, **settings):
        """Returns all data specs, required or optional, the object_type provides."""
        from ..api.utils import restrict_field_spec

        data_spec = self.get_data_spec(object_type=object_type)

        settings["object_type"] = object_type  # Make sure this still goes in as a setting
        return restrict_field_spec(data_spec, settings)

    def get_required_data_specs(self, object_type, **settings):
        """Returns only required data specs the object_type provides."""
        from ..api.utils import restrict_field_spec

        data_spec = self.get_data_spec(object_type=object_type)

        settings["object_type"] = object_type  # Make sure this still goes in as a setting
        return restrict_field_spec(data_spec, settings, lambda spec: spec["required"])

    def get_computed_data_specs(self, object_type, **settings):
        """Returns only computed data specs the object_type provides."""
        from ..api.utils import restrict_field_spec

        data_spec = self.get_data_spec(object_type=object_type)

        settings["object_type"] = object_type  # Make sure this still goes in as a setting
        return restrict_field_spec(data_spec, settings, lambda spec: "value" in spec)

    def get_parent_object_spec(self, object_type, default=unset):
        parent_type = self.get_parent_type(object_type=object_type, default=unset)
        if parent_type is unset:
            return default
        return self.get_object_type_spec(object_type=parent_type)
