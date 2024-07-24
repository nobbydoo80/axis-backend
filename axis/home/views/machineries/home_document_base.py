"""home_document_base.py: """

__author__ = "Artem Hruzd"
__date__ = "11/10/2021 5:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from axis.filehandling.machinery import BaseCustomerDocumentExamineMachinery


class HomeDocumentAgreementBase(BaseCustomerDocumentExamineMachinery):
    regionset_template = "examine/home/home_document_regionset.html"
    detail_template = "examine/home/home_document_detail.html"
    visible_fields = [
        "document",
        "description",
        "last_update",
        "is_public",
    ]

    def get_verbose_names(self, instance, form=None, serializer=None, **kwargs):
        verbose_names = super(HomeDocumentAgreementBase, self).get_verbose_names(
            instance, form, serializer, **kwargs
        )
        verbose_names["last_update"] = "Last Update"
        return verbose_names

    def can_delete_object(self, instance, user=None):
        can_delete_object = super(BaseCustomerDocumentExamineMachinery, self).can_delete_object(
            instance, user
        )
        return can_delete_object
