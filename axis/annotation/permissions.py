"""permissions.py: Django annotations"""

from axis.core.management.commands.set_permissions import AppPermission
from .models import Annotation, Type

__author__ = "Steven Klass"
__date__ = "1/31/13 3:13 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class AnnotationTypePermissions(AppPermission):
    models = [
        Type,
    ]


class AnnotationPermissions(AppPermission):
    models = [
        Annotation,
    ]

    def get_rater_permissions(self):
        return [
            "view",
        ]

    def get_provider_permissions(self):
        return [
            "view",
        ]

    def get_qa_permissions(self):
        return [
            "view",
        ]

    def get_aps_permissions(self):
        return [
            "view",
        ]
