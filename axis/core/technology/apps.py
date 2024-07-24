"""App configs."""
import importlib
import logging

from django.apps import AppConfig

from .register_signals import RegisterSignalsConfig

__author__ = "Autumn Valenta"
__date__ = "2019-50-15 02:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class TechnologyAppConfig(AppConfig):
    """Base AppConfig settings system for customer apps.

    Inherit from this AppConfig base to enable standard customer features.  Capture basic settings
    by assigning constants or flags from from settings.
    """

    name = None  # `axis.APPNAME`

    # Tuple of `ExtensionConfig` classes that contribute to this appconfig.
    extensions = (RegisterSignalsConfig,)

    def __new__(cls, *args, **kwargs):
        """Construct composed type with `cls.extensions` added to the bases."""

        composed_cls = type(cls.__name__, cls.extensions + (cls,), dict(cls.__dict__))
        return super(TechnologyAppConfig, composed_cls).__new__(composed_cls)

    def ready(self):
        super(TechnologyAppConfig, self).ready()

    def _get_dotted_path_function(self, dotted_path):
        dotted_path = self.name + dotted_path if dotted_path.startswith(".") else dotted_path
        module_path, method_name = dotted_path.rsplit(".", 1)
        module_object = importlib.import_module(module_path)
        return getattr(module_object, method_name)

    @classmethod
    def app_name(cls):
        """Return app name without a package prefix."""
        return cls.name.split(".", 1)[1]
