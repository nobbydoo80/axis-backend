import logging
import io
import pathlib

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from axis.company.models import Company

from ..models import CustomerDocument

log = logging.getLogger(__name__)

__author__ = "Benjamin Stürmer"
__date__ = "03/13/22 16:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Benjamin Stürmer"]


def store_document_to_model_instance(
    instance: Model,
    file_name: str,
    stream: io.BytesIO,
    *,
    description: str = "",
    company: Company | None = None,
    is_public: bool,
    login_required: bool = True,
) -> CustomerDocument:
    """Attach a customer document to any model instance.
    :param instance: Can be any Model instance. The instance must have an ID - if you
    want to attach a document to a new instance you need to save it first.
    :param file_name: The name to save the file under
    :param stream: The file to be saved
    :param description: A brief description of the file
    :param company: The company with which to associate the file
    :param is_public: If True, the document can be downloaded by anyone
    :param login_required: If True, the document can only be downloaded by logged-in users
    """
    if instance.pk is None:
        raise Exception(
            "Unsaved model instances not allowed - you must save your "
            "instance before attaching a document to it"
        )

    content_type = ContentType.objects.get_for_model(instance)

    # The company argument is only necessary (and only does anything) if the passed
    # model instance doesn't have a `company` property
    if hasattr(instance, "company") and isinstance(instance.company, Company):
        company = instance.company
    elif company is None:
        raise Exception("You must either pass `company` or `instance.company` must be a Company")

    # We want the URL that pointed to a document to still work if the document
    # is re-generated, so if an identical document already exists we will
    # delete it and recycle its ID
    path = pathlib.Path(file_name)
    filter_kwargs = {
        "document__contains": path.name,
        "document__endswith": path.suffix,
        "content_type": content_type,
        "object_id": instance.pk,
    }
    existing_qs = CustomerDocument.objects.filter(**filter_kwargs)
    existing = existing_qs.first()
    if existing:
        existing_qs.exclude(pk=existing.pk).delete()

    return CustomerDocument.objects.store(
        content_object=instance,
        company=company,
        document=stream.getbuffer(),
        description=description,
        filename=file_name,
        filesize=len(stream.getvalue()),
        type="document",
        is_public=is_public,
        login_required=login_required,
        pk=existing.pk if existing else None,
    )
