"""Auto-discovered admin registration."""


import logging

from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from axis.home.disambiguation.admin import CertificationAdmin, CandidateAdmin
from .models import NEEACertification, Candidate

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


admin.site.register(NEEACertification, CertificationAdmin)
admin.site.register(Candidate, CandidateAdmin)
