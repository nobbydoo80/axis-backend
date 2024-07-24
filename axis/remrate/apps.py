from django.apps import apps
from django.conf import settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

settings = getattr(settings, "REMRATE", {})


class REMRateConfig(technology.TechnologyAppConfig):
    """REMrate technology configuration."""

    name = "axis.remrate"

    # Imports
    @property
    def rater_organization_factory(self):
        return apps.get_app_config("company").rater_organization_factory

    @property
    def customer_document_factory(self):
        return apps.get_app_config("filehandling").customer_document_factory

    # Exports
    @property
    def rem_xml_customer_document_factory(self):
        dotted_path = ".tests.factories.remxml_customer_document_factory"
        return self._get_dotted_path_function(dotted_path)
