import logging

from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

log = logging.getLogger(__name__)

__author__ = "Steven Klass"
__date__ = "03/13/22 16:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Benjamin Stürmer"]


def render_customer_document_from_template(obj, filename, description, owner, f_populate, **kwargs):
    """Return a customerdocument instance attached `obj`, owned by `owner`.

    `f_populate` should be a function that accepts the `**kwargs` for its operative needs,
    and returns the pdf file-like object, which is saved to the customerdocument.
    """

    from ..models import CustomerDocument

    # get_or_create()-style params for this document to avoid duplicating.
    # description is the obvious choice for creating uniqueness or uniformity
    # in the auto-generating mechanism.
    content_type = ContentType.objects.get_for_model(obj)
    document_kwargs = {
        "content_type": content_type,
        "object_id": obj.id,
        "company": owner,
        "type": "document",
        "is_public": True,
        "description": description,
    }

    customer_document = CustomerDocument.objects.filter(**document_kwargs).last()
    if not customer_document:
        customer_document = CustomerDocument(**document_kwargs)

        # Generate the document concretely, first.
        # Set the path directly on the FieldFile, then save().
        prepared_document = kwargs.pop("prepared_document", None)
        if prepared_document is None:
            prepared_document = f_populate(obj, **kwargs)
        customer_document.document.name = default_storage.save(
            customer_document._meta.get_field("document").upload_to(customer_document, filename),
            ContentFile(prepared_document),
        )
        customer_document.save()

        log.info(
            "Created document %(pk)r: %(path)s",
            {"pk": customer_document.pk, "path": customer_document.document.name},
        )

    return customer_document
