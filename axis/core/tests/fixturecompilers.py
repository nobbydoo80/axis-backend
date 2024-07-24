"""Base fixture compiler classes"""


import logging
import os.path
import re

from django.apps import apps

__author__ = "Autumn Valenta"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class BaseFixtureCompiler(object):
    """Base class to generate fixtures through fixturecompiler management command"""

    fixtures = None  # Pre-req fixtures for testing runtime, if required
    filename = None  # Generated automatically from class name if not given
    format = "json"

    dumpdata_excludes = [
        # appnames for things that shouldn't get wildly duplicated throughout all fixtures
        # Things that live on the non-default db
        "aec_remrate",
        # Django stuff
        "auth.permission",
        "contenttypes",
        "flatpages",
        "sites",
    ]

    def populate_database(self, **options):
        """Loads arbitrary data to the blank database."""
        raise NotImplementedError

    @property
    def model_count_assertions(self):
        """Dictionary of dotted path model names to a count of expected models"""
        return {}

    def assert_model_count(self, model_path, count, raise_exception=True):
        """Will run a quick model assertion"""
        ModelObj = apps.get_model(model_path)
        total = ModelObj.objects.count()
        error = None
        if total != count:
            error = "%s (%s) expected %s received %s" % (ModelObj, model_path, count, total)
        if error and raise_exception:
            raise AssertionError(error)
        return error

    def check_model_count_assertions(self):
        errors = []
        model_count_assertions = self.model_count_assertions
        for model_path, count in model_count_assertions.items():
            error = self.assert_model_count(model_path, count, raise_exception=False)
            if error is not None:
                errors.append(error)
        if errors:
            raise AssertionError(
                "Model Count Assertion Error (%s)\n\t - %s"
                % (self.__class__.__name__, "\n\t - ".join(errors))
            )
        elif model_count_assertions:
            log.info("Successfully verified %d model assertions" % len(model_count_assertions))

    def get_app_config(self):
        """Gets django app config"""
        app_config = None
        names = self.__module__.split(".")
        names_count = len(names)
        for i in range(names_count):
            for _, config in apps.app_configs.items():
                mod_path = "/".join(names[: (names_count - i)])
                if mod_path in config.path and config.path.endswith(mod_path):
                    app_config = config
        return app_config

    def get_fixture_dir(self):
        """Gets the path to this app's "fixtures/" directory."""
        app_config = self.get_app_config()
        if not os.path.isdir(os.path.join(app_config.path, "fixtures")):
            if os.path.isdir(app_config.path):
                os.makedirs(os.path.join(app_config.path, "fixtures"))
        if os.path.isdir(os.path.join(app_config.path, "fixtures")):
            return os.path.join(app_config.path, "fixtures")

        raise ValueError(
            "Fixture compiler '{}.{}' does not appear "
            "to live in an installed app. "
            "Cannot automatically determine a "
            "fixture directory.".format(self.__module__, self.__class__.__name__)
        )

    def get_fixture_path(self):
        """Returns the full path to which the compiler intends to write its content."""
        return os.path.join(self.get_fixture_dir(), self.get_filename())

    def get_filename(self):
        """
        Returns the declared filename, or else the class name converted to snake_case, and stripped
        of any trailing "_fixture_compiler" suffix.
        """
        if self.filename:
            return self.filename

        # Convert the class name to snake_case
        name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", self.__class__.__name__)
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()

        # Remove trailing "_fixture_compiler"
        name = re.sub(r"_fixture_compiler$", "", name)

        if not name:
            raise ValueError(
                "Fixture compiler '{}.{}' is not "
                "specific enough to automatically "
                "generate a filename.".format(self.__module__, self.__class__)
            )

        return os.path.join(*(["compiled"] + ["{}.{}".format(name, self.format)]))

    def get_dumpdata_excludes(self):
        """Excludes system apps from dump"""
        excludes = self.dumpdata_excludes[:]
        for app_config in apps.get_app_configs():
            models = app_config.get_models()
            for model in models:
                if model._meta.object_name.startswith("Historical"):
                    excludes.append("{opts.app_label}.{opts.model_name}".format(opts=model._meta))
        return excludes
