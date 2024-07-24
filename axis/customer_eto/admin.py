"""admin.py: Django customer_eto"""


import logging
from django.contrib import admin
from .models import ETOAccount, FastTrackSubmission

__author__ = "Steven Klass"
__date__ = "3/3/14 1:26 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ETOAccountInline(admin.TabularInline):
    model = ETOAccount
    fk_name = "company"
    extra = 1


class FastTrackSubmissionStackedInline(admin.StackedInline):
    model = FastTrackSubmission
    extra = 0
