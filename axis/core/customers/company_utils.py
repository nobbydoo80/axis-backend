"""Built-in extensions for customer apps."""


import logging

from django.apps import apps

from axis.core.technology import ExtensionConfig

__author__ = "Autumn Valenta"
__date__ = "2019-50-15 02:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class CompanyUtils(ExtensionConfig):
    # Required
    # CUSTOMER_SLUG = None

    def get_customer_company(self):
        """Get the Company named in self.CUSTOMER_SLUG."""
        if not apps.ready:
            return None

        # Avoid global import dependency
        from axis.company.models import Company

        return Company.objects.get(slug=self.CUSTOMER_SLUG)
