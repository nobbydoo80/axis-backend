from axis.floorplan import api
from axis.filehandling.api import customerdocument_viewset_factory
from .router import api_router

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


api_router.register(
    r"floorplan/documents",
    customerdocument_viewset_factory("floorplan.floorplan"),
    "floorplan_documents",
)
api_router.register(r"floorplan/remrate", api.FloorplanRemrateViewSet, "floorplan_remrate")
api_router.register(r"floorplan/ekotrope", api.FloorplanEkotropeViewSet, "floorplan_ekotrope")
api_router.register(r"floorplan/approval", api.FloorplanApprovalViewSet, "floorplan_approval")
api_router.register(r"floorplan", api.FloorplanViewSet, "floorplan")
