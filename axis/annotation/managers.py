"""managers.py Django Annotation"""


from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

from axis.core.managers.utils import queryset_user_is_authenticated


class AnnotationTypeQueryset(QuerySet):
    def filter_by_target_model(self, model_class):
        """
        Filters by the ``applicable_content_types`` m2m field for the content type of
        ``model_class``

        """

        return self.filter(applicable_content_types=ContentType.objects.get_for_model(model_class))

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        return self.filter_by_relationships(
            company=company, show_attached=kwargs.pop("show_attached", False)
        ).filter(**kwargs)

    @queryset_user_is_authenticated
    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        show_attached = kwargs.pop("show_attached", False)
        kwargs["show_attached"] = show_attached
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_by_relationships(self, company, show_attached=False):
        """
        Returns objects within the relationship network.  In the future this might be a good method
        to include in a RelationshipManagerMixin class, because it is generic and reusable.

        """
        from axis.relationship.models import Relationship

        relationships = Relationship.objects.filter_by_company(company, show_attached=show_attached)
        relationships = relationships.filter_by_content_type(model=self.model)
        return self.filter(id__in=list(relationships.values_list("object_id", flat=True)))


class AnnotationQuerySet(models.QuerySet):
    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self.filter(Q(is_public=True) | Q(is_public=False) & Q(user__company=user.company))
