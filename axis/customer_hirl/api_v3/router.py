__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.customer_hirl.api_v3.viewsets import (
    HIRLProjectViewSet,
    HIRLGreenEnergyBadgeViewSet,
    HIRLProjectNestedHistoryViewSet,
    HIRLProjectRegistrationViewSet,
    HIRLProjectRegistrationNestedHistoryViewSet,
    HIRLProjectNestedViewSet,
    COIDocumentViewSet,
    ClientAgreementViewSet,
    VerifierAgreementViewSet,
    NestedProvidedServiceViewSet,
    COIDocumentNestedHistoryViewSet,
    ClientAgreementNestedHistoryViewSet,
    ClientAgreementNestedCustomerDocumentViewSet,
    ClientAgreementAnnotationViewSet,
)


class CustomerHIRLRouter:
    @staticmethod
    def register(router):
        hirl_project_registration_router = router.register(
            "hirl_project_registrations",
            HIRLProjectRegistrationViewSet,
            "hirl_project_registrations",
        )

        hirl_project_registration_router.register(
            "hirl_projects",
            HIRLProjectNestedViewSet,
            "hirl_project_registration-hirl_projects",
            parents_query_lookups=["registration_id"],
        )

        hirl_project_registration_router.register(
            "history",
            HIRLProjectRegistrationNestedHistoryViewSet,
            "hirl-project-registration-history",
            parents_query_lookups=["id"],
        )

        hirl_project_router = router.register("hirl_projects", HIRLProjectViewSet, "hirl_projects")

        hirl_project_router.register(
            "history",
            HIRLProjectNestedHistoryViewSet,
            "hirl-project-history",
            parents_query_lookups=["id"],
        )

        router.register(
            "hirl_green_energy_badges", HIRLGreenEnergyBadgeViewSet, "hirl_green_energy_badges"
        )

        coi_documents_router = router.register("coi_documents", COIDocumentViewSet, "coi_documents")

        coi_documents_router.register(
            "history",
            COIDocumentNestedHistoryViewSet,
            "coi_documents-history",
            parents_query_lookups=["id"],
        )

        client_agreements_router = router.register(
            r"client_agreements", ClientAgreementViewSet, "client_agreements"
        )

        client_agreements_router.register(
            "history",
            ClientAgreementNestedHistoryViewSet,
            "client_agreements-history",
            parents_query_lookups=["id"],
        )

        client_agreements_router.register(
            "documents",
            ClientAgreementNestedCustomerDocumentViewSet,
            "client_agreements-documents",
            parents_query_lookups=["object_id"],
        )

        client_agreements_router.register(
            "annotations",
            ClientAgreementAnnotationViewSet,
            "client_agreements-annotations",
            parents_query_lookups=["object_id"],
        )

        verifier_agreement_router = router.register(
            "verifier_agreements", VerifierAgreementViewSet, "verifier_agreements"
        )

        verifier_agreement_router.register(
            "provided_services",
            NestedProvidedServiceViewSet,
            "verifier_agreement-provided_service",
            parents_query_lookups=["id"],
        )
