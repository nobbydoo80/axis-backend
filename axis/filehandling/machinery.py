"""machinery.py: Django filehandling"""

__author__ = "Autumn Valenta"
__date__ = "2/25/15 10:01 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import logging

from django.urls import reverse_lazy

from axis import examine

from django.apps import apps
from .models import CustomerDocument
from .api import customerdocument_viewset_factory
from .forms import CustomerDocumentForm

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


def customerdocument_machinery_factory(  # pylint: disable=too-many-arguments
    model,
    bases=None,
    valid_content_types=None,
    allow_multiple=False,
    allow_delete=True,
    machinery_name=None,
    api_name=None,
    dependency_name=None,
):
    """Create a CustomerDocument machinery configured for a target model.

    `allow_multiple` controls the file picker behavior, to make it single or multiple.

    Note that `allow_delete=True` only enables a standard permission check, not replaces it.
    """

    if bases is None:
        bases = (BaseCustomerDocumentExamineMachinery,)

    attrs = {
        "model_name": dependency_name or model._meta.model_name,
        "type_name": api_name or "%s_documents" % (model._meta.model_name,),
        "api_provider": customerdocument_viewset_factory(model),
        "allow_multiple": allow_multiple,
        "allow_delete": allow_delete,
    }

    # Don't shadow something on the base if the local kwarg is unsest
    if valid_content_types:
        attrs["valid_content_types"] = valid_content_types

    if not machinery_name:
        machinery_name = "%sCustomerDocumentMachinery" % (model.__name__,)
    Machinery = type(str(machinery_name), bases, attrs)
    return Machinery


class BaseCustomerDocumentExamineMachinery(examine.TableMachinery):
    """Generic machinery for multiple models using CustomerDocument."""

    model = CustomerDocument
    form_class = CustomerDocumentForm
    verbose_name = "Document"
    detail_template = "examine/filehandling/document_detail.html"
    form_template = "examine/filehandling/document_form.html"

    model_name = None  # Filled in from factory for a given model class
    valid_content_types = None
    allow_delete = True

    def can_delete_object(self, instance, user=None):
        """Return typical value if `allow_delete` is True, and False otherwise."""

        if self.allow_delete:
            return super(BaseCustomerDocumentExamineMachinery, self).can_delete_object(
                instance, user
            )
        return False

    @property
    def regionset_template(self):
        """Return regionset template appropriate for the `allow_multiple` filepicker setting."""

        if self.allow_multiple:
            return "examine/filehandling/document_regionset.html"
        return super(BaseCustomerDocumentExamineMachinery, self).regionset_template

    def get_form_kwargs(self, instance):
        """Return dict that includes `allow_multiple` value."""

        return {"allow_multiple": self.allow_multiple}

    def get_region_dependencies(self):
        """Return upper dependency on `model_name` for the local `object_id`."""

        return {
            self.model_name: [
                {
                    "field_name": "id",
                    "serialize_as": "object_id",
                }
            ],
        }

    def get_helpers(self, instance):
        helpers = super(BaseCustomerDocumentExamineMachinery, self).get_helpers(instance)
        user = self.context["request"].user

        helpers["show_customer_hirl_quick_responses"] = False
        helpers["allow_multiple"] = self.allow_multiple
        if user:
            helpers[
                "show_customer_hirl_quick_responses"
            ] = user.is_customer_hirl_company_member() or user.is_sponsored_by_company(
                customer_hirl_app.CUSTOMER_SLUG
            )
        return helpers
