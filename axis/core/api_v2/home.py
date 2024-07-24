"""API Endpoints for Home"""


from axis.home import api
from axis.filehandling.api import customerdocument_viewset_factory
from .router import api_router

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


api_router.register(
    r"home/documents", customerdocument_viewset_factory("home.home"), "home_documents"
)
api_router.register(r"home/users", api.HomeUsersViewSet, "home_users")
api_router.register(r"home", api.HomeViewSet, "home")
api_router.register(r"home_document_actions", api.HomeViewSet, "home_document_actions")

api_router.register(r"homestatuses/pipeline", api.HomeStatusPipelineViewSet, "home_status_list")
api_router.register(
    r"homestatus/floorplans", api.HomeStatusFloorplansViewSet, "home_status_floorplans"
)
api_router.register(
    r"homestatus/hirl_projects",
    api.HomeStatusHIRLProjectViewSet,
    "home_status_hirl_project",
)
api_router.register(
    r"homestatus/hirl_invoice_item_group",
    api.HIRLInvoiceItemGroupViewSet,
    "hirl_invoice_item_group",
)
api_router.register(
    r"homestatus/hirl_invoice_item", api.HIRLInvoiceItemViewSet, "hirl_invoice_item"
)
api_router.register(
    r"homestatus/annotations",
    api.HomeStatusAnnotationsViewSet,
    "home_status_annotations",
)
api_router.register(r"homestatus", api.HomeStatusViewSet, "home_status")
api_router.register(r"invoice_homestatus", api.HomeStatusViewSet, "invoice_home_status")
api_router.register(
    r"hirl_project_registration_home_status",
    api.HomeStatusViewSet,
    "hirl_project_registration_home_status",
)

api_router.register(r"quick_links", api.ReportQuickLinksCountViewSet, "quick_links")
api_router.register(r"find_certified_home", api.FindCertifiedHomeViewSet, "find_certified_home")
