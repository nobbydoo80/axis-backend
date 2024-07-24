"""__init__.py: Django company package container"""

__author__ = "Steven Klass"
__date__ = "2012/3/2 10:25:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Amit Kumar Pathak",
    "Eric Walker",
    "Rajesh Pappula",
    "Autumn Valenta",
    "Michael Jeffrey",
]
__license__ = "See the file LICENSE.txt for licensing information."

from .views import (
    LegacyCompanyListRedirectView,
    LegacyCompanyCreateRedirectView,
    LegacyCompanyDetailRedirectView,
    BoundCompaniesAjaxView,
    CompanyContactListView,
)
