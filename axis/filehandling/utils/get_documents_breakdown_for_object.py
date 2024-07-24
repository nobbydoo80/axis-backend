import collections
import logging

from django.contrib.contenttypes.models import ContentType

log = logging.getLogger(__name__)

__author__ = "Steven Klass"
__date__ = "03/13/22 16:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Benjamin Stürmer"]

DocumentsBreakdownTuple = collections.namedtuple("DocumentsBreakdownTuple", ("total", "breakdown"))


def get_documents_breakdown_for_object(obj, user=None):
    from ..models import CustomerDocument

    breakdown = {}

    content_type = ContentType.objects.get_for_model(obj)
    documents = CustomerDocument.objects.filter(object_id=obj.id, content_type=content_type)
    if user:
        documents = documents.filter_by_user(user)
    breakdown["instance"] = documents

    extended_f = getattr(obj, "discover_related_documents", None)
    if extended_f:
        log.debug(
            "Model %s has callback 'discover_related_documents', allowing it to run...",
            repr(content_type),
        )
        breakdown = extended_f(breakdown, user=user)

    total = 0
    for name, queryset in breakdown.items():
        total += queryset.count()
    log.debug(
        "Discovered %d total documents in %d categories: %r",
        total,
        len(breakdown),
        tuple(breakdown.keys()),
    )

    return DocumentsBreakdownTuple(total, breakdown)
