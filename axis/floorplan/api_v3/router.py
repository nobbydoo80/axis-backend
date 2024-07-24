"""router.py: """

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from axis.floorplan.api_v3.viewsets import (
    FloorplanViewSet,
    FloorplanNestedHistoryViewSet,
    FloorplanNestedRelationshipViewSet,
    SimulationViewSet,
    SeedViewSet,
    FloorplanNestedDocumentViewSet,
    FloorplanNestedHomeStatusViewSet,
)
from axis.floorplan.api_v3.viewsets.simulation import (
    NestedProjectViewSet,
    NestedMechanicalEquipmentsViewSet,
    NestedFoundationWallViewSet,
    NestedAboveGradeWallViewSet,
    NestedRoofViewSet,
    NestedFrameFloorViewSet,
    NestedWindowViewSet,
    NestedDoorViewSet,
    NestedSlabViewSet,
    NestedSkylightViewSet,
    NestedRimJoistViewSet,
    NestedPhotovoltaicViewSet,
    NestedAnalyticsViewSet,
    NestedInfiltrationViewSet,
    NestedLightsViewSet,
    NestedAppliancesViewSet,
    NestedLocationViewSet,
    NestedUtilityRateViewSet,
)


class FloorplanRouter:
    @staticmethod
    def register(router):
        # floorplan app
        floorplan_router = router.register(r"floorplans", FloorplanViewSet, "floorplans")
        floorplan_router.register(
            "history",
            FloorplanNestedHistoryViewSet,
            "floorplan-history",
            parents_query_lookups=["id"],
        )
        floorplan_router.register(
            "relationships",
            FloorplanNestedRelationshipViewSet,
            "floorplan-relationships",
            parents_query_lookups=["object_id"],
        )
        floorplan_router.register(
            "documents",
            FloorplanNestedDocumentViewSet,
            "floorplan-documents",
            parents_query_lookups=["object_id"],
        )
        floorplan_router.register(
            "home_statuses",
            FloorplanNestedHomeStatusViewSet,
            "floorplan-home_statuses",
            parents_query_lookups=["floorplans"],
        )

        simulation_router = router.register(r"simulations", SimulationViewSet, "simulations")
        router.register(r"simulation-seeds", SeedViewSet, "simulation-seeds")

        simulation_router.register(
            "project",
            NestedProjectViewSet,
            "simulation-project",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "mechanicals",
            NestedMechanicalEquipmentsViewSet,
            "simulation-mechanicals",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "foundation_walls",
            NestedFoundationWallViewSet,
            "simulation-foundation_walls",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "abovegrade_walls",
            NestedAboveGradeWallViewSet,
            "simulation-abovegrade_walls",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "roofs",
            NestedRoofViewSet,
            "simulation-roofs",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "floors",
            NestedFrameFloorViewSet,
            "simulation-floors",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            r"windows",
            NestedWindowViewSet,
            "simulation-windows",
            parents_query_lookups=["simulation_id"],
        )

        simulation_router.register(
            "doors",
            NestedDoorViewSet,
            "simulation-doors",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "slabs",
            NestedSlabViewSet,
            "simulation-slabs",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "skylights",
            NestedSkylightViewSet,
            "simulation-skylights",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "rimjoists",
            NestedRimJoistViewSet,
            "simulation-rimjoists",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "photovoltaics",
            NestedPhotovoltaicViewSet,
            "simulation-photovoltaics",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "analytics",
            NestedAnalyticsViewSet,
            "simulation-analytics",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "infiltration",
            NestedInfiltrationViewSet,
            "simulation-infiltration",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "lights",
            NestedLightsViewSet,
            "simulation-lights",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "appliances",
            NestedAppliancesViewSet,
            "simulation-appliances",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "location",
            NestedLocationViewSet,
            "simulation-location",
            parents_query_lookups=["simulation_id"],
        )
        simulation_router.register(
            "utilityrates",
            NestedUtilityRateViewSet,
            "simulation-utilityrates",
            parents_query_lookups=["simulation_id"],
        )
