from django.conf import settings

from axis.core import platform

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


settings = getattr(settings, "COMPANY", {})


class CompanyConfig(platform.PlatformAppConfig):
    """Company platform configuration."""

    name = "axis.company"

    @property
    def rater_organization_factory(self):
        dotted_path = ".tests.factories.rater_organization_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def builder_organization_factory(self):
        dotted_path = ".tests.factories.builder_organization_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def get_company_aliases(self):
        dotted_path = ".managers.get_company_aliases"
        return self._get_dotted_path_function(dotted_path)

    @property
    def build_company_aliases(self):
        dotted_path = ".managers.build_company_aliases"
        return self._get_dotted_path_function(dotted_path)
