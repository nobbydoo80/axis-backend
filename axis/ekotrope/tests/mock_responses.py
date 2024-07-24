"""mock_responses.py - Axis"""
import json
import logging
from unittest import mock

from axis.ekotrope.utils import import_project_tree

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "8/6/20 14:04"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class MockedResponse:
    def __init__(self, url, _return_data="{}", **kw):
        self.text = _return_data
        self.params = kw.get("params")
        self.url = url
        self.status_code = kw.get("status_code", 200)

    def json(self):
        try:
            return json.loads(self.text)
        except json.decoder.JSONDecodeError:
            raise ValueError("Error")


def mocked_requests_get_projects(url, **kw):
    """This is the projects that are returned from Ekotrope"""
    data = """[{"id":"q2R6WDq2","name":"Test Home A","createdAt":"2020-05-15T20:12:26.000+0000",
        "createdBy":"axis-api","lastSavedAt":"2020-05-15T20:12:26.000+0000",
        "lastSavedBy":"axis-api","selfOrPlanLastSavedAt":"2020-05-15T20:12:26.000+0000",
        "isLocked":false}, {"id":"x25VNRxL","name":"Test Home B",
        "createdAt":"2020-05-15T20:12:29.000+0000", "createdBy":"axis-api",
        "lastSavedAt":"2020-05-15T20:12:29.000+0000","lastSavedBy":"axis-api",
        "selfOrPlanLastSavedAt":"2020-05-15T20:12:29.000+0000","isLocked":false}] """
    return MockedResponse(url, data, **kw)


def mocked_requests_get_projects_eula(url, **kw):
    data = """{"internalErrorCode": 10, "message": "User must accept EULA dummy"}"""
    return MockedResponse(url, data, **kw)


def mocked_requests_get_project(url, **kw):
    """Given an ID this is a sample of what is returned from Ekotrope"""
    data = """{"id":"q2R6WDq2","name":"Test Home A",
    "createdAt":"2020-05-15T20:12:26.000+0000","createdBy":"axis-api",
    "lastSavedAt":"2020-05-15T20:12:26.000+0000","lastSavedBy":"axis-api",
    "selfOrPlanLastSavedAt":"2020-05-15T20:12:26.000+0000","isLocked":false,
    "status":"UNREGISTERED","location":{"streetAddress":"Type A","city":"Phoenix",
    "state":"AZ","zip":"85085","zipWeather":"85085","climateZone":{"zone":2,"moistureRegime":"DRY"},
    "weatherStationName":"DEER VALLEY/PHOENIX, AZ","county":"MARICOPA"},"notes":"",
    "model":"Type A","community":"Elux at Deer Valley","lotNumber":"",
    "builder":"Harvard Investments","builderPermitDateOrNumber":"","constructionYear":"2020",
    "submittedProjectId":"M28loWw2","hersRatingDetails":{"rater":{"name":"Katie Johnson",
    "email":"katie@pivotal.com","resnetRaterId":"5377019","resnetProviderId":"1998-056",
    "ratingCompany":{"name":"JKP Energy Inspections, LLC","id":"eGqO0Yd0"}},"ratingType":"SAMPLED",
    "sampledSetId":"00000000","associatedUsers":[]},
    "plans":[{"id":"x7jJOPK7","name":"20.01.23 kj ESv3"}],"masterPlanId":"x7jJOPK7",
    "resultsUnchangedSince":"2020-05-15T20:12:26.000+0000",
    "utilityRates":[{"fuel":"ELECTRIC","name":"APS 2020 Premier Choice"},
    {"fuel":"NATURAL_GAS","name":"SWG 2020 Single Family"}],
    "algorithmVersion":"3.2.3","thirdParty":{}}"""
    return MockedResponse(url, data, **kw)


def mocked_requests_get_detail_bad(url, **kw):
    data = "Unauthorized"
    return MockedResponse(url, data, **kw)


def mocked_requests_get_houseplan(url, **kw):
    """Given an ID this is a sample of what is returned from Ekotrope"""
    data = """{"id":"x7jJOPK7","name":"20.01.23 kj ESv3","lighting":{"percentEfficient":
    {"interior":0.0,"exterior":0.0,"garage":0.0},"percentLED":{"interior":100.0,"exterior":100.0,
    "garage":100.0}},"appliances":{"dishwasherEfficiencyType":"kWh","dishwasherEfficiency":265.0,
    "dishwasherPlaceSettings":12,"refrigeratorConsumption":433.0,"clothesDryer":{"fuel":"ELECTRIC",
    "combinedEfficiencyFactor":3.73,"utilizationFactor":"TIMER_CONTROLS"},
    "clothesWasher":{"labeledEnergyRating":125.0,"electricRate":0.12,"gasRate":1.09,
    "annualGasCost":9.0,"capacity":4.5,"integratedModifiedEnergyFactor":2.06},
    "rangeOven":{"fuel":"ELECTRIC"}},"thermalEnvelope":{"summary":{"conditionedArea":678.0,
    "conditionedVolume":6098.0,"windowArea":90.0,"wallArea":981.0,"floorArea":0.0,
    "ceilingArea":678.0,"slabArea":678.0,"totalThermalBoundaryArea":2337.0,
    "aboveGradeThermalBoundaryArea":1659.0,"dominantWallType":{"id":"bkaPwwWY",
    "name":"x4 R13+4 g1 stucco","description":"2016-12 SL","uFactor":0.0651464524825033,
    "hasAssemblyDetails":true,"assemblyDetails":{"cavityR":13.0,"cavityInsulationGrade":["I"],
    "cavityInsulationMaterial":["Custom"],"continuousR":4.0,"framingSpacing":[16.0],
    "framingDepth":[3.5],"framingFraction":[0.23005]},"isVerified":true},
    "dominantSlabType":{"id":"VQQPddxV","name":"Uninsulated","description":"","isVerified":true,
    "slabCompletelyInsulated":false,"perimeterRValue":0.0,"underSlabRValue":0.0,
    "underslabInsulationWidth":0.0,"perimeterInsulationDepth":0.0},
    "dominantCeilingType":{"id":"be9POOBb","name":"Vent R38 g1",
    "description":"Loose blown over studs. 2017.01 SL","uFactor":0.02623229484050109,
    "hasAssemblyDetails":true,"assemblyDetails":{"cavityR":13.0,"cavityInsulationGrade":["I"],
    "cavityInsulationMaterial":["CelluloseAttic"],"continuousR":25.0,"framingSpacing":[24.0],
    "framingDepth":[3.5],"framingFraction":[0.11]},"isVerified":true,"radiantBarrier":false},
    "dominantWindowType":{"id":"6MMxddx6","name":"U-.51, SHGC-.23","description":"17.09.08 kj",
    "uFactor":0.51,"SHGC":0.23,"isVerified":true},"dominantDoorType":{"id":"VJ0jeeq6",
    "name":"Fg R7.1 Therma-Tru","description":"2017-01 SL","isVerified":true,"uFactor":0.14006}},
    "infiltration":{"fieldTestStatus":"Tested","cfm50":508.1666666666667,"ach50":5.0,
    "effectiveLeakageArea":27.949166666666667,"specificLeakageArea":0.00028608734021632254,
    "heatingNaturalACH":0.23255813953488372,"coolingNaturalACH":0.23255813953488372},
    "foundationType":"SLAB_ON_GRADE","slabs":[{"name":"Slab","encloses":"ConditionedSpace",
    "surfaceArea":678.0,"exteriorPerimeter":109.0,"exposedMasonryArea":0.0,"grade":"OnGrade",
    "type":{"id":"VQQPddxV","name":"Uninsulated","description":"","isVerified":true,
    "slabCompletelyInsulated":false,"perimeterRValue":0.0,"underSlabRValue":0.0,
    "underslabInsulationWidth":0.0,"perimeterInsulationDepth":0.0}}],"framedFloors":[],
    "foundationWalls":[],"walls":[{"name":"exposed","surfaceColor":"Medium","betweenInteriorAnd":
    "ExposedExterior","surfaceArea":981.0,"type":{"id":"bkaPwwWY","name":"x4 R13+4 g1 stucco",
    "description":"2016-12 SL","uFactor":0.0651464524825033,"hasAssemblyDetails":true,
    "assemblyDetails":{"cavityR":13.0,"cavityInsulationGrade":["I"],
    "cavityInsulationMaterial":["Custom"],"continuousR":4.0,"framingSpacing":[16.0],
    "framingDepth":[3.5],"framingFraction":[0.23005]},"isVerified":true}}],"rimJoists":[],
    "ceilings":[{"name":"Roof","surfaceColor":"Medium","betweenInteriorAnd":"VentedAttic",
    "surfaceArea":678.0,"roofDeckArea":678.0,"clayConcreteRoofTiles":true,
    "type":{"id":"be9POOBb","name":"Vent R38 g1","description":"Loose blown over studs. 2017.01 SL",
    "uFactor":0.02623229484050109,"hasAssemblyDetails":true,"assemblyDetails":{"cavityR":13.0,
    "cavityInsulationGrade":["I"],"cavityInsulationMaterial":["CelluloseAttic"],"continuousR":25.0,
    "framingSpacing":[24.0],"framingDepth":[3.5],"framingFraction":[0.11]},"isVerified":true,
    "radiantBarrier":false}}],"windows":[{"name":"Front Unshaded","orientation":"East",
    "installedWallIndex":0,"surfaceArea":20.0,"type":{"id":"6MMxddx6","name":"U-.51, SHGC-.23",
    "description":"17.09.08 kj","uFactor":0.51,"SHGC":0.23,"isVerified":true},"overhangDepth":0.0,
    "distanceOverhangToTop":0.0,"distanceOverhangToBottom":0.0,"shadingFactors":
    {"interior":{"summer":0.7,"winter":0.85},"adjacent":{"summer":1.0,"winter":1.0}}},
    {"name":"Left Unshaded","orientation":"South","installedWallIndex":0,"surfaceArea":10.0,
    "type":{"id":"6MMxddx6","name":"U-.51, SHGC-.23","description":"17.09.08 kj","uFactor":0.51,
    "SHGC":0.23,"isVerified":true},"overhangDepth":0.0,"distanceOverhangToTop":0.0,
    "distanceOverhangToBottom":0.0,"shadingFactors":{"interior":{"summer":0.7,"winter":0.85},
    "adjacent":{"summer":1.0,"winter":1.0}}},{"name":"Back Unshaded","orientation":"West",
    "installedWallIndex":0,"surfaceArea":58.0,"type":{"id":"6MMxddx6","name":"U-.51, SHGC-.23",
    "description":"17.09.08 kj","uFactor":0.51,"SHGC":0.23,"isVerified":true},"overhangDepth":0.0,
    "distanceOverhangToTop":0.0,"distanceOverhangToBottom":0.0,
    "shadingFactors":{"interior":{"summer":0.7,"winter":0.85},"adjacent":{"summer":1.0,
    "winter":1.0}}},{"name":"Right Unshaded","orientation":"North","installedWallIndex":0,
    "surfaceArea":2.0,"type":{"id":"6MMxddx6","name":"U-.51, SHGC-.23","description":"17.09.08 kj",
    "uFactor":0.51,"SHGC":0.23,"isVerified":true},"overhangDepth":0.0,"distanceOverhangToTop":0.0,
    "distanceOverhangToBottom":0.0,"shadingFactors":{"interior":{"summer":0.7,"winter":0.85},
    "adjacent":{"summer":1.0,"winter":1.0}}}],"skylights":[],"doors":[{"name":"Front Door & patio",
    "installedWallIndex":0,"surfaceArea":48.0,"type":{"id":"VJ0jeeq6","name":"Fg R7.1 Therma-Tru",
    "description":"2017-01 SL","isVerified":true,"uFactor":0.14006}}]},
    "mechanicals":{"summary":{"ductSystemCount":1,"ductLeakageTotal":27.12,
    "ductLeakageToOutside":27.12,"mechanicalVentilationRate":21.8,
    "dominantHeatingEquipmentType":{"id":"brJArX7b","name":"14.0seer 8.0hspf 24k",
    "description":"2017-03 SL","fuel":"ELECTRIC","equipmentType":"AIR_SOURCE_HEAT_PUMP",
    "motorType":"SingleSpeed","isVerified":true,"ahriReferenceNumber":"",
    "heating":{"efficiency":8.0,"efficiencyType":"HSPF","capacity":24.0},
    "cooling":{"efficiency":14.0,"efficiencyType":"SEER","capacity":24.0},
    "hotWater":{"efficiency":0.0,"efficiencyType":"ENERGY_FACTOR","isTankless":false,
    "tankSize":40.0}},"dominantCoolingEquipmentType":{"id":"brJArX7b","name":"14.0seer 8.0hspf 24k",
    "description":"2017-03 SL","fuel":"ELECTRIC","equipmentType":"AIR_SOURCE_HEAT_PUMP",
    "motorType":"SingleSpeed","isVerified":true,"ahriReferenceNumber":"",
    "heating":{"efficiency":8.0,"efficiencyType":"HSPF","capacity":24.0},
    "cooling":{"efficiency":14.0,"efficiencyType":"SEER","capacity":24.0},
    "hotWater":{"efficiency":0.0,"efficiencyType":"ENERGY_FACTOR","isTankless":false,
    "tankSize":40.0}},"dominantHotWaterEquipment":{"id":"YOnNEKjV","name":"m-9950961",
    "description":"RE230LN*-*****","fuel":"ELECTRIC","equipmentType":"HOT_WATER_HEATER",
    "motorType":"SingleSpeed","isVerified":true,"ahriReferenceNumber":"",
    "heating":{"efficiency":0.0,"efficiencyType":"AFUE","capacity":0.0},
    "cooling":{"efficiency":0.0,"efficiencyType":"SEER","capacity":0.0},
    "hotWater":{"efficiency":0.92,"efficiencyType":"ENERGY_FACTOR","isTankless":false,
    "tankSize":28.0}},"dominantMechanicalVentilationType":{"ventilationType":"ExhaustOnly",
    "operationalHoursPerDay":24.0,"watts":9.81,"ventilationRate":21.8,"recoveryEfficiency":0},
    "dominantDistributionSystem":{"systemType":"ForcedAir","fieldTestStatus":"ThresholdOrSampled",
    "isTested":true,"testedDetails":{"sqFtServed":678.0,"numberOfReturnGrilles":1,
    "supplyDuctSurfaceArea":183.06,"returnDuctSurfaceArea":33.9,"isLeakageToOutsideTested":true,
    "leakageToOutside":27.12,"totalLeakage":27.12,
    "fieldTestLeakageToOutsideForThresholdOrSampled":0.0,
    "fieldTestTotalLeakageForThresholdOrSampled":0.0,
    "totalLeakageTestCondition":"RoughInWithAirHandler","ducts":[{"location":"ConditionedSpace",
    "percentSupplyArea":100.0,"percentReturnArea":100.0,"supplyR":6.0,"returnR":6.0},
    {"location":"ConditionedSpace","percentSupplyArea":0.0,"percentReturnArea":0.0,"supplyR":6.0,
    "returnR":6.0},{"location":"ConditionedSpace","percentSupplyArea":0.0,"percentReturnArea":0.0,
    "supplyR":6.0,"returnR":6.0},{"location":"ConditionedSpace","percentSupplyArea":0.0,
    "percentReturnArea":0.0,"supplyR":6.0,"returnR":6.0},{"location":"ConditionedSpace",
    "percentSupplyArea":0.0,"percentReturnArea":0.0,"supplyR":6.0,"returnR":6.0},
    {"location":"ConditionedSpace","percentSupplyArea":0.0,"percentReturnArea":0.0,"supplyR":6.0,
    "returnR":6.0}]},"heatingEquipmentIndex":0,"coolingEquipmentIndex":0}},"equipment":[{"equipmentType":"AIR_SOURCE_HEAT_PUMP","heating":{"efficiencyType":"HSPF","percentLoad":100.0,
    "efficiency":8.0},"cooling":{"efficiencyType":"SEER","percentLoad":100.0,"efficiency":14.0},
    "waterHeating":{"efficiencyType":"ENERGY_FACTOR","percentLoad":0.0,"efficiency":0.0}},
    {"equipmentType":"HOT_WATER_HEATER","heating":{"efficiencyType":"AFUE","percentLoad":0.0,
    "efficiency":0.0},"cooling":{"efficiencyType":"SEER","percentLoad":0.0,"efficiency":0.0},
    "waterHeating":{"efficiencyType":"ENERGY_FACTOR","percentLoad":100.0,"efficiency":0.92}}],
    "mechanicalEquipment":[{"name":"ASHP","heatingPercentLoad":100.0,"coolingPercentLoad":100.0,
    "hotWaterPercentLoad":0.0,"location":"ConditionedSpace","type":{"id":"brJArX7b",
    "name":"14.0seer 8.0hspf 24k","description":"2017-03 SL","fuel":"ELECTRIC",
    "equipmentType":"AIR_SOURCE_HEAT_PUMP","motorType":"SingleSpeed","isVerified":true,
    "ahriReferenceNumber":"","heating":{"efficiency":8.0,"efficiencyType":"HSPF","capacity":24.0},
    "cooling":{"efficiency":14.0,"efficiencyType":"SEER","capacity":24.0},
    "hotWater":{"efficiency":0.0,"efficiencyType":"ENERGY_FACTOR","isTankless":false,
    "tankSize":40.0}}},{"name":"Water Heater","heatingPercentLoad":0.0,"coolingPercentLoad":0.0,
    "hotWaterPercentLoad":100.0,"location":"ConditionedSpace","type":{"id":"YOnNEKjV",
    "name":"m-9950961","description":"RE230LN*-*****","fuel":"ELECTRIC",
    "equipmentType":"HOT_WATER_HEATER","motorType":"SingleSpeed","isVerified":true,
    "ahriReferenceNumber":"","heating":{"efficiency":0.0,"efficiencyType":"AFUE","capacity":0.0},
    "cooling":{"efficiency":0.0,"efficiencyType":"SEER","capacity":0.0},
    "hotWater":{"efficiency":0.92,"efficiencyType":"ENERGY_FACTOR","isTankless":false,
    "tankSize":28.0}}}],"mechanicalVentilation":[{"ventilationType":"ExhaustOnly",
    "operationalHoursPerDay":24.0,"watts":9.81,"ventilationRate":21.8,"recoveryEfficiency":0}],
    "distributionSystems":[{"systemType":"ForcedAir","fieldTestStatus":"ThresholdOrSampled",
    "isTested":true,"testedDetails":{"sqFtServed":678.0,"numberOfReturnGrilles":1,
    "supplyDuctSurfaceArea":183.06,"returnDuctSurfaceArea":33.9,"isLeakageToOutsideTested":true,
    "leakageToOutside":27.12,"totalLeakage":27.12,
    "fieldTestLeakageToOutsideForThresholdOrSampled":0.0,
    "fieldTestTotalLeakageForThresholdOrSampled":0.0,
    "totalLeakageTestCondition":"RoughInWithAirHandler","ducts":[{"location":"ConditionedSpace",
    "percentSupplyArea":100.0,"percentReturnArea":100.0,"supplyR":6.0,"returnR":6.0},
    {"location":"ConditionedSpace","percentSupplyArea":0.0,"percentReturnArea":0.0,
    "supplyR":6.0,"returnR":6.0},{"location":"ConditionedSpace","percentSupplyArea":0.0,
    "percentReturnArea":0.0,"supplyR":6.0,"returnR":6.0},{"location":"ConditionedSpace",
    "percentSupplyArea":0.0,"percentReturnArea":0.0,"supplyR":6.0,"returnR":6.0},
    {"location":"ConditionedSpace","percentSupplyArea":0.0,"percentReturnArea":0.0,
    "supplyR":6.0,"returnR":6.0},{"location":"ConditionedSpace","percentSupplyArea":0.0,
    "percentReturnArea":0.0,"supplyR":6.0,"returnR":6.0}]},"heatingEquipmentIndex":0,
    "coolingEquipmentIndex":0}],"thermostats":[{"thermostatType":"Programmable","makeAndModel":"",
    "serialNumber":""}]},"onsiteGenerations":{"summary":{"hasSolarGeneration":false},
    "solarGenerationSystems":[]},"waterSystem":{"fixtureEffectiveness":"LOW_FLOW",
    "usingEstimatedHotWaterPipeLength":true,"hotWaterPipeLength":62.076866265166146,
    "allHotWaterPipesInsulatedToAtLeastR3":false},"details":{"bedrooms":1,"residenceType":
    "SingleFamilyHouse","numberOfFloorsOnOrAboveGrade":1.0,"programmableThermostat":true,
    "buildingType":"EkotropeAsModeled","unitsInBuilding":1,"hasElectricVehicleReadySpace":false}}"""
    return MockedResponse(url, data, **kw)


def mocked_requests_get_analysis(url, **kw):
    """Given an Houseplan ID this is a sample of what is returned from Ekotrope"""

    data = """{"id":"x7jJOPK7","name":"20.01.23 kj ESv3",
    "energy":{"summary":{"coolingConsumption":5.216071479902736,
    "heatingConsumption":1.508978809769489,"waterHeatingConsumption":3.683010211931584,
    "cost":888.299,"solarGeneration":0.0,"winterElectricPowerPeak":0.9311050640461359,
    "summerElectricPowerPeak":1.2273669744398121,
    "lightingAndAppliancesConsumption":9.010312584722957,"coolingCost":189.357,
    "heatingCost":54.78,"waterHeatingCost":133.703,"lightingAndAppliancesCost":327.098,
    "serviceCharges":183.359,"generationSavings":0.0,"generationRevenue":0.0},
    "breakdown":{"byFuel":[{"fuel":"NATURAL_GAS","heatingConsumption":0.0,
    "coolingConsumption":0.0,"waterHeatingConsumption":0.0,"lightingAndAppliancesConsumption":0.0,
    "cost":0.0},{"fuel":"ELECTRIC","heatingConsumption":1.508978809769489,
    "coolingConsumption":5.216071479902736,"waterHeatingConsumption":3.683010211931584,
    "lightingAndAppliancesConsumption":9.010312584722957,"cost":888.2993726410049},
    {"fuel":"OIL","heatingConsumption":0.0,"coolingConsumption":0.0,"waterHeatingConsumption":0.0,
    "lightingAndAppliancesConsumption":0.0,"cost":0.0},{"fuel":"PROPANE","heatingConsumption":0.0,
    "coolingConsumption":0.0,"waterHeatingConsumption":0.0,"lightingAndAppliancesConsumption":0.0,
    "cost":0.0},{"fuel":"WOOD","heatingConsumption":0.0,"coolingConsumption":0.0,
    "waterHeatingConsumption":0.0,"lightingAndAppliancesConsumption":0.0,"cost":0.0}],
    "byComponent":[{"category":"FOUNDATION_WALL","heatingLoad":0.0,"coolingLoad":0.0},
    {"category":"SLAB","heatingLoad":1.9924548115542873,"coolingLoad":3.2456512119825516},
    {"category":"FRAMED_FLOOR","heatingLoad":0.0,"coolingLoad":0.0},{"category":"ABOVE_GROUND_WALL",
    "heatingLoad":1.2716278609193623,"coolingLoad":3.106379840673382},{"category":"RIM_JOIST",
    "heatingLoad":0.0,"coolingLoad":0.0},{"category":"ROOF","heatingLoad":0.4391630494939698,
    "coolingLoad":0.9149381078247709},{"category":"DOOR","heatingLoad":0.1834566414365845,
    "coolingLoad":0.29884555833937226},{"category":"WINDOW","heatingLoad":1.25253757942121,
    "coolingLoad":2.0403474593890043},{"category":"SKYLIGHT","heatingLoad":0.0,"coolingLoad":0.0},
    {"category":"INFILTRATION","heatingLoad":0.21452012971724646,"coolingLoad":0.3891636432910353},
    {"category":"MECHANICAL_VENTILATION","heatingLoad":0.6165958158737929,
    "coolingLoad":1.0044167353201028}]}},"compliance":[],"hersScore":53,"hersScoreNoPv":53,
    "buildingType":"EkotropeAsModeled","emissions":{"summary":{"totalCo2":2.987031240004215,
    "totalSo2":9.103333302869988,"totalNox":5.120624982864368},
    "byEnergySink":{"heating":{"co2":0.23211866541279166,"so2":0.7074092660199365,
    "nox":0.39791771213621424},"cooling":{"co2":0.8023621953960384,"so2":2.4452943097784026,
    "nox":1.3754780492503513},"hotWater":{"co2":0.566539045850376,"so2":1.7265951873535266,
    "nox":0.9712097928863587},"lightsAndAppliances":{"co2":1.386011333345009,
    "so2":4.224034539718122,"nox":2.3760194285914435},"pvOffset":{"co2":0.0,"so2":0.0,"nox":0.0}}},
    "thirdParty":{}}
    """
    codes = {
        "Ashrae62_2_2010": {
            "code": "Ashrae62_2_2010",
            "complianceStatus": "Pass",
            "targetHers": 0.0,
        },
        "Ashrae62_2_2013": {
            "code": "Ashrae62_2_2013",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "DOEZeroEnergyReady": {
            "code": "DOEZeroEnergyReady",
            "complianceStatus": "Fail",
            "targetHers": 47.0,
        },
        "EnergyStarV2": {
            "code": "EnergyStarV2",
            "complianceStatus": "Pass",
            "targetHers": 85.0,
        },
        "EnergyStarV3": {
            "code": "EnergyStarV3",
            "complianceStatus": "Pass",
            "targetHers": 66.0,
        },
        "EnergyStarV31": {
            "code": "EnergyStarV31",
            "complianceStatus": "Pass",
            "targetHers": 57.0,
        },
        "IECC2006Performance": {
            "code": "IECC2006Performance",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2006Prescriptive": {
            "code": "IECC2006Prescriptive",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2009Performance": {
            "code": "IECC2009Performance",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2009Prescriptive": {
            "code": "IECC2009Prescriptive",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2012Performance": {
            "code": "IECC2012Performance",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2012Prescriptive": {
            "code": "IECC2012Prescriptive",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2015ERI": {
            "code": "IECC2015ERI",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2015Performance": {
            "code": "IECC2015Performance",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2015Prescriptive": {
            "code": "IECC2015Prescriptive",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2018ERI": {
            "code": "IECC2018ERI",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "IECC2018Performance": {
            "code": "IECC2018Performance",
            "complianceStatus": "Pass",
            "targetHers": 0.0,
        },
        "IECC2018Prescriptive": {
            "code": "IECC2018Prescriptive",
            "complianceStatus": "Warn",
            "targetHers": 0.0,
        },
        "IndoorAirPlus": {
            "code": "IndoorAirPlus",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "LeedSourceEnergyBudget": {
            "code": "LeedSourceEnergyBudget",
            "complianceStatus": "Pass",
            "targetHers": 0.0,
        },
        "NGBS2015": {"code": "NGBS2015", "complianceStatus": "Pass"},
        "NorthCarolina2012Performance": {
            "code": "NorthCarolina2012Performance",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "NorthCarolina2012Prescriptive": {
            "code": "NorthCarolina2012Prescriptive",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
        "TaxCredit45L": {
            "code": "TaxCredit45L",
            "complianceStatus": "Fail",
            "targetHers": 0.0,
        },
    }

    def get_default(code):
        return {"code": code, "complianceStatus": "Pass", "targetHers": 0.0}

    if kw.get("params") and kw["params"].get("buildingType"):
        _data = json.loads(data)
        _data["buildingType"] = kw["params"].get("buildingType")
        if kw["params"].get("codesToCheck"):
            for code in kw["params"].get("codesToCheck", []):
                code_item = codes.get(code, get_default(code))
                _data["compliance"].append(code_item)
        data = json.dumps(_data)
    return MockedResponse(url, data, **kw)


def mocked_project_list(_auth):
    """This is the output of request_project_list"""
    return mocked_requests_get_projects(None).json()


def mocked_request_project(_auth, id):
    """This is the output of request_project"""
    data = mocked_requests_get_project(None).json()
    data["id"] = id
    for idx, plan in enumerate(data["plans"]):
        data["plans"][idx]["id"] = id[:-2] + "p%s" % idx
    data["masterPlanId"] = id[:-2] + "p0"
    return data, "http://someurl"


def mocked_request_houseplan(_auth, id):
    """This is the output of request_houseplan"""
    data = mocked_requests_get_houseplan(None).json()
    data["id"] = id
    return data, "http://someurl"


def mocked_request_analysis(_auth, id, **kw):
    """This is the output of request_analysis"""
    _data = {"buildingType": kw["building_type"]}
    if "codes_to_check" in kw:
        _data = {
            "buildingType": kw["building_type"],
            "codesToCheck": kw["codes_to_check"],
        }
    data = mocked_requests_get_analysis(None, params=_data).json()
    data["id"] = id
    return data, "http://someurl"


def mocked_request_fail(_auth, id, **kw):
    """This bad data is universal for all three request types"""
    return "BAD DATA", "http://someurl"


@mock.patch("axis.ekotrope.utils.request_project", side_effect=mocked_request_project)
@mock.patch("axis.ekotrope.utils.request_houseplan", side_effect=mocked_request_houseplan)
@mock.patch("axis.ekotrope.utils.request_analysis", side_effect=mocked_request_analysis)
def mocked_import_project_tree(
    auth_details,
    id,
    _mock_request_analysis,
    _mock_request_houseplan,
    _mock_request_project,
):
    """This will allow us to simplify a number of fixtures"""
    data = import_project_tree(auth_details, id)
    assert _mock_request_project.called
    assert _mock_request_project.call_count == 1
    assert _mock_request_houseplan.called
    assert _mock_request_houseplan.call_count == 1
    assert _mock_request_analysis.called
    assert _mock_request_analysis.call_count == 32
    return data
