__author__ = "Artem Hruzd"
__date__ = "09/30/2020 17:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.company.api_v3.viewsets import (
    NestedAltNameViewSet,
    NestedAffiliationsViewSet,
    NestedSponsoringViewSet,
    AltNameViewSet,
    SponsoringViewSet,
    CompanyViewSet,
    CompanyNestedRelationshipViewSet,
    CompanyNestedCustomerDocumentViewSet,
    CompanyNestedHistoryViewSet,
    CompanyAccessViewSet,
    CompanyRoleViewSet,
    NestedCompanyAccessViewSet,
)
from axis.core.api_v3.viewsets import NestedCompanyContactCardViewSet
from axis.customer_hirl.api_v3.viewsets import NestedCOIDocumentViewSet
from axis.equipment.api_v3.viewsets import NestedEquipmentViewSet
from axis.remrate.api_v3.viewsets import RemRateUserViewSet, NestedRemRateUserViewSet


class CompanyRouter:
    @staticmethod
    def register(router):
        # company app
        company_router = router.register(r"companies", CompanyViewSet, "companies")

        company_router.register(
            "documents",
            CompanyNestedCustomerDocumentViewSet,
            "company-documents",
            parents_query_lookups=["object_id"],
        )
        company_router.register(
            "coi_documents",
            NestedCOIDocumentViewSet,
            "company-coi_documents",
            parents_query_lookups=["company_id"],
        )
        company_router.register(
            "equipments",
            NestedEquipmentViewSet,
            "company-equipments",
            parents_query_lookups=["owner_company_id"],
        )
        company_router.register(
            "contact_cards",
            NestedCompanyContactCardViewSet,
            "company-contact_cards",
            parents_query_lookups=["company_id"],
        )
        company_router.register(
            "alt_names",
            NestedAltNameViewSet,
            "company-alt_names",
            parents_query_lookups=["company_id"],
        )
        company_router.register(
            "affiliations",
            NestedAffiliationsViewSet,
            "company-affiliations",
            parents_query_lookups=["sponsored_company_id"],
        )
        company_router.register(
            "sponsoring",
            NestedSponsoringViewSet,
            "company-sponsoring",
            parents_query_lookups=["sponsor_id"],
        )
        company_router.register(
            "history",
            CompanyNestedHistoryViewSet,
            "company-history",
            parents_query_lookups=["id"],
        )
        company_router.register(
            "relationships",
            CompanyNestedRelationshipViewSet,
            "company-relationships",
            parents_query_lookups=["object_id"],
        )
        company_router.register(
            "remrate_users",
            NestedRemRateUserViewSet,
            "company-remrate_users",
            parents_query_lookups=["company_id"],
        )
        company_router.register(
            "company_accesses",
            NestedCompanyAccessViewSet,
            "company-company_accesses",
            parents_query_lookups=["company_id"],
        )

        # company alt names
        router.register(r"alt_names", AltNameViewSet, "alt_names")
        router.register(r"remrate_users", RemRateUserViewSet, "remrate_users")

        # company sponsoring preferences
        router.register(r"sponsoring_preferences", SponsoringViewSet, "sponsoring_preferences")

        router.register(r"company_accesses", CompanyAccessViewSet, "company_accesses")
        router.register(r"company_roles", CompanyRoleViewSet, "company_roles")
