"""Built-in extensions for platform apps."""


from importlib import import_module
import logging

from .extensions import ExtensionConfig

__author__ = "Autumn Valenta"
__date__ = "2019-50-15 02:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class RegisterSignalsConfig(ExtensionConfig):
    """Base extension for classes contributing to a PlatformAppConfig."""

    def ready(self):
        """Register local app signals."""
        super(RegisterSignalsConfig, self).ready()
        self.register_signals()

    def register_signals(self):
        """Import and run `{app_label}.signals.register_signals`, if it is available."""
        try:
            signals = self.get_submodule("signals")
        except ImportError as e:
            log.debug(
                "No signals available in {app_name}: {error_preview}".format(
                    app_name=self.name, error_preview=e
                )
            )
        else:
            if hasattr(signals, "register_signals"):
                log.info(
                    "{module}: Imported + Calling `register_signals()`".format(
                        module=signals.__name__
                    )
                )
                signals.register_signals()
            else:
                log.info("{module}: Imported".format(module=signals.__name__))

    def get_submodule(self, name):
        """Import and return handle to module or package at `axis.appname.{name}."""
        return import_module("{app_label}.{name}".format(app_label=self.name, name=name))
