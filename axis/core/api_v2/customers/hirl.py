from axis.filehandling.api import customerdocument_viewset_factory
from axis.customer_hirl import api, models
from ..router import api_router

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


api_router.register(
    r"hirl/agreement/documents",
    customerdocument_viewset_factory(models.BuilderAgreement),
    "hirl_builder_agreement_documents",
)

api_router.register(
    r"hirl/verifier_agreement/documents",
    customerdocument_viewset_factory(models.VerifierAgreement),
    "hirl_verifier_agreement_documents",
)
api_router.register(
    r"hirl/verifier_agreement",
    api.VerifierAgreementManagementViewSet,
    "hirl_verifier_agreement",
)
api_router.register(
    r"hirl/verifier_agreement_enrollment",
    api.VerifierAgreementEnrollmentViewSet,
    "hirl_verifier_agreement_enrollment",
)
api_router.register(
    r"hirl/verifier_agreement_coi_document",
    api.COIDocumentViewSet,
    "hirl_verifier_agreement_coi_document",
)
