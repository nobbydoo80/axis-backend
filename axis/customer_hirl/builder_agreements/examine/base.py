__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


import logging

from django.apps import apps

from axis.filehandling.machinery import BaseCustomerDocumentExamineMachinery

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


class NGBSDocumentAgreementBase(BaseCustomerDocumentExamineMachinery):
    can_add_new = False
    detail_template = "examine/customer_hirl/agreement_document_detail.html"
    visible_fields = [
        "document",
        "description",
        "last_update",
        "is_public",
    ]

    def get_verbose_names(self, instance, form=None, serializer=None, **kwargs):
        verbose_names = super(NGBSDocumentAgreementBase, self).get_verbose_names(
            instance, form, serializer, **kwargs
        )
        verbose_names["last_update"] = "Last Update"
        return verbose_names

    def can_edit_object(self, instance, user=None):
        if user and user.is_superuser:
            return True
        return False

    def can_delete_object(self, instance, user=None):
        if user and user.is_superuser:
            return True
        return False
