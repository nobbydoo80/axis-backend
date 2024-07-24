"""examine.py: Django builder_agreement"""


from axis.builder_agreement.api import BuilderAgreementViewSet
from axis.builder_agreement.models import BuilderAgreement
from axis.examine import ReadonlyMachinery

__author__ = "Steven Klass"
__date__ = "8/16/19 1:27 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class BuilderAgreementMachinery(ReadonlyMachinery):
    """Basic machinery for Builder Agreement"""

    model = BuilderAgreement
    api_provider = BuilderAgreementViewSet
    type_name = "builder_agreement"
    template_set = "panel"

    detail_template = "examine/agreement/builder_agreement_detail.html"

    def get_new_region_endpoint(self):
        """Nothing here move along"""
        return None
