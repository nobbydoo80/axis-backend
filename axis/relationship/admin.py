"""admin.py: Django relationship"""


import logging

from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Relationship

__author__ = "Steven Klass"
__date__ = "3/19/13 9:23 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RelationshipTabularInline(GenericTabularInline):
    """Inline Document"""

    model = Relationship
    extra = 2

    raw_id_fields = ("company",)
