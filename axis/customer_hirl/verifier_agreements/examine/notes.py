"""Generic Annotations-as-Notes machinery for customer VerifierAgreements."""


import logging

from django.apps import apps

from axis.annotation.machinery import annotations_machinery_factory, BaseAnnotationExamineMachinery
from axis.customer_hirl.models import VerifierAgreement

__author__ = "Artem Hruzd"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


def get_verifieragreement_notes_machinery():  # pylint: disable=invalid-name
    """Return a machinery equipped to talk to the BuilderAgreement endpoints."""

    return annotations_machinery_factory(
        VerifierAgreement, bases=(BaseVerifierAgreementNoteMachinery,), type_slug="note"
    )


class BaseVerifierAgreementNoteMachinery(BaseAnnotationExamineMachinery):
    """Base Annotation config for `get_verifieragreement_notes_machinery()`."""

    regionset_template = "examine/angular_regionset_table.html"
    region_template = "examine/angular_region_tablerow.html"
    detail_template = "examine/annotation/note_table_detail.html"
    form_template = "examine/annotation/note_table_form.html"

    edit_name = "Edit"
    edit_icon = None
    save_name = "Save"
    save_icon = None

    class NoteForm(BaseAnnotationExamineMachinery.form_class):
        """Labels fields for BuilderAgreement."""

        class Meta(BaseAnnotationExamineMachinery.form_class.Meta):
            labels = {
                "content": "Note",
                "is_public": "Public",
            }

    form_class = NoteForm

    def get_region_dependencies(self):
        """Return examine dependency spec for dynamic parent machinery (enrollee or owner)."""

        return {
            self.context["dependency_name"]: [
                {
                    "field_name": "id",
                    "serialize_as": "object_id",
                }
            ],
        }

    def can_delete_object(self, instance, user=None):
        """Return True if `user` is the author of the comment or is a company admin."""

        is_author = instance.user == user
        is_company_admin = instance.user == user and user.is_company_admin
        return is_author or is_company_admin or (user and user.is_superuser)

    def get_form_kwargs(self, instance):
        kwargs = super(BaseVerifierAgreementNoteMachinery, self).get_form_kwargs(instance)
        kwargs["initial"] = {
            "is_public": False,
        }
        return kwargs
