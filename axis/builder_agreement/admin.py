"""admin.py: Django builder_agreement"""


import logging
from django.contrib import admin
from axis.builder_agreement.models import BuilderAgreement

__author__ = "Steven Klass"
__date__ = "5/31/12 1:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class BuilderAgreementAdmin(admin.ModelAdmin):
    ordering = [
        "company",
    ]
    search_fields = ["builder_org__name", "subdivision__name", "company__name"]


admin.site.register(BuilderAgreement, BuilderAgreementAdmin)
