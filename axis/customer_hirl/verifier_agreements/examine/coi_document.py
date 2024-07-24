"""coi.py: """

from django.apps import apps

from axis.customer_hirl.models import COIDocument
from axis import examine
from ..forms import COIDocumentForm, BasicCOIDocumentForm
from ..api import COIDocumentViewSet

__author__ = "Artem Hruzd"
__date__ = "05/15/2020 12:11"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

app = apps.get_app_config("customer_hirl")


class CompanyCOIDocumentExamineMachinery(examine.PanelMachinery):
    model = COIDocument
    form_class = COIDocumentForm
    type_name = "hirl_verifier_agreement_coi_document"
    api_provider = COIDocumentViewSet

    regionset_template = "examine/customer_hirl/verifier_agreement/coi_regionset_panel.html"
    region_template = "examine/customer_hirl/verifier_agreement/coi_document_region_panel.html"
    detail_template = "examine/customer_hirl/verifier_agreement/coi_document_detail.html"

    def get_new_region_endpoint(self):
        user = self.context["request"].user
        if user and user.company:
            if not user.is_superuser or not user.is_customer_hirl_company_member():
                if not user.is_company_admin:
                    return None
        return super(CompanyCOIDocumentExamineMachinery, self).get_new_region_endpoint()

    def get_region_dependencies(self):
        return {
            "company_new": [
                {
                    "field_name": "id",
                    "serialize_as": "company",
                }
            ],
        }

    def get_form_class(self):
        if (
            self.context["request"].user.company.slug == app.CUSTOMER_SLUG
            or self.context["request"].user.is_superuser
        ):
            return COIDocumentForm
        return BasicCOIDocumentForm
