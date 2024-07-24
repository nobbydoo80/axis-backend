"""managers.py: Django filehandling"""


import logging

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType

from .utils import get_documents_breakdown_for_object

__author__ = "Steven Klass"
__date__ = "5/29/12 10:01 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ..company.models import Company

log = logging.getLogger(__name__)


class AsynchronousProcessedDocumentManager(models.Manager):
    """Manager for Processed Documents"""

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        return self.filter(company=company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class CustomerDocumentManager(models.Manager):
    def get_queryset(self):
        return CustomerDocumentQuerySet(self.model, using=self._db)

    def store(
        self,
        content_object: models.Model,
        company: Company,
        document: File,
        filename: str,
        **kwargs,
    ):
        """Perform create() using the storage backend to save an unknown raw document."""

        content_type = ContentType.objects.get_for_model(content_object)

        instance = self.model(
            content_type=content_type,
            object_id=content_object.id,
            company=company,
            type=kwargs.pop("type", "document"),
            is_public=kwargs.pop("is_public", True),
            **kwargs,
        )
        instance.document.name = default_storage.save(
            instance._meta.get_field("document").upload_to(instance, filename),
            ContentFile(document),
        )
        instance.save()
        return instance

    def filter_by_company(self, company, include_public=False):
        return self.get_queryset().filter_by_company(company, include_public=include_public)

    def filter_by_user(self, user, include_public=False):
        return self.get_queryset().filter_by_user(user, include_public=include_public)

    def get_breakdown(self, user=None):
        if not hasattr(self, "instance"):
            raise Exception("'get_breakdown()' must be called from an instance related manager.")
        return get_documents_breakdown_for_object(self.instance, user=user)

    # Per-type methods
    def count_type(self, type_name):
        return self.get_queryset().count_type(type_name)

    def count_documents(self):
        return self.get_queryset().count_documents()

    def count_images(self):
        return self.get_queryset().count_images()


class CustomerDocumentQuerySet(QuerySet):
    def filter_by_company(self, company, include_public=False, **kwargs):
        q = Q(company=company)
        if include_public:
            q |= ~Q(company__company_type=company.company_type) & Q(is_public=True)
        return self.filter(q, **kwargs)

    def filter_by_user(self, user, include_public=False, **kwargs):
        if user.is_superuser:
            return self.filter()
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(include_public=include_public, **kwargs)

    def count_type(self, type_name):
        return self.filter(type=type_name).count()

    def count_documents(self):
        return self.count_type("document")

    def count_images(self):
        return self.count_type("image")
