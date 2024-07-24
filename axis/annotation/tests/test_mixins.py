"""test_mixins.py - Axis"""

__author__ = "Steven K"
__date__ = "8/24/21 11:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.contrib.contenttypes.models import ContentType

from ..models import Type as AnnotationType
from ..models import Annotation


log = logging.getLogger(__name__)


class AnnotationMixin:
    def add_annotation(
        self, content: str, type_slug: str, content_object: any, user=None
    ) -> Annotation:
        """Add an annotation to an object, or retrieve one if a matching annotation already exists"""
        a_type, _ = AnnotationType.objects.get_or_create(slug=type_slug)

        if user is None and hasattr(self, "user"):
            user = self.user
        return Annotation.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.id,
            type=a_type,
            defaults={"content": content, "user": user},
        )[0]
