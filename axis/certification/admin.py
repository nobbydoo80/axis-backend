import logging

from django.contrib import admin

from . import models


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Register your models here.

admin.site.register(models.CertifiableObject)
admin.site.register(models.Workflow)
admin.site.register(models.WorkflowStatus)
