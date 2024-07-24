import logging

from rest_framework import serializers

from . import validators
from .models import Project, HousePlan

__author__ = "Autumn Valenta"
__date__ = "10/31/16 09:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Axis API Serializers
class AxisHousePlanListingSerializer(serializers.ModelSerializer):
    # data = serializers.JSONField()

    class Meta:
        model = HousePlan
        fields = ("id", "name", "project")


# https://ekotrope.api-docs.io/v1.0.0/endpoints/house-plan


# Project List (ProjectStubSerializer)
class ProjectStubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name")

    def create(self, validated_data):
        # 'company' is assigned from the outside, in stub_project_list()
        return self.Meta.model.objects.create(company=self.company, **validated_data)


class climateZoneSerializer(serializers.Serializer):
    moistureRegime = serializers.CharField()
    zone = serializers.IntegerField()


# Project (ProjectSerializer)
class ProjectLocationSerializer(serializers.Serializer):
    streetAddress = serializers.CharField(allow_blank=True)
    city = serializers.CharField()
    state = serializers.CharField(validators=[validators.validate_location_state])
    zip = serializers.CharField(validators=[validators.validate_location_zip], allow_blank=True)
    climateZone = climateZoneSerializer()


class ProjectRaterCompanySerializer(serializers.Serializer):
    name = serializers.CharField()
    website = serializers.URLField(required=False)


class ProjectRaterSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField()
    resnetRaterId = serializers.CharField(allow_blank=True, required=False)
    resnetProviderId = serializers.CharField(allow_blank=True, required=False)

    ratingCompany = ProjectRaterCompanySerializer()


class ProjectRatingDetailsSerializer(serializers.Serializer):
    registryId = serializers.CharField(required=False)
    ratingDate = serializers.DateTimeField(required=False)
    ratingType = serializers.CharField(required=False, validators=[validators.validate_rating_type])
    submittedPlanId = serializers.CharField(required=False, validators=[validators.validate_id])

    rater = ProjectRaterSerializer(required=False)


class ProjectPlansSerializer(serializers.Serializer):
    id = serializers.CharField(validators=[validators.validate_id])
    name = serializers.CharField()


class ProjectSerializer(serializers.Serializer):
    model = serializers.CharField(allow_blank=True)
    community = serializers.CharField(allow_blank=True)
    builder = serializers.CharField(allow_blank=True)
    builderPermitDateOrNumber = serializers.CharField(allow_blank=True, required=False)

    location = ProjectLocationSerializer()
    hersRatingDetails = ProjectRatingDetailsSerializer()
    plans = ProjectPlansSerializer(many=True)


# HousePlan (HousePlanSerializer)
class ThermalEnvelopeSummarySerializer(serializers.Serializer):
    conditionedArea = serializers.FloatField(min_value=0, max_value=100000)
    conditionedVolume = serializers.FloatField(min_value=0, max_value=100000000)
    windowArea = serializers.FloatField(min_value=0, max_value=100000)
    wallArea = serializers.FloatField(min_value=0, max_value=100000)
    floorArea = serializers.FloatField(min_value=0, max_value=100000)
    ceilingArea = serializers.FloatField(min_value=0, max_value=100000)
    slabArea = serializers.FloatField(min_value=0, max_value=100000)


class ThermalEnvelopeInfiltrationSerializer(serializers.Serializer):
    cfm50 = serializers.FloatField()
    ach50 = serializers.FloatField()
    effectiveLeakageArea = serializers.FloatField()
    specificLeakageArea = serializers.FloatField()
    heatingNaturalACH = serializers.FloatField()
    coolingNaturalACH = serializers.FloatField()


class ThermalEnvelopeSerializer(serializers.Serializer):
    foundationType = serializers.CharField(validators=[validators.validate_foundation_type])

    summary = ThermalEnvelopeSummarySerializer()
    infiltration = ThermalEnvelopeInfiltrationSerializer()


class MechanicalsSummarySerializer(serializers.Serializer):
    ductSystemCount = serializers.IntegerField(min_value=0)
    ductLeakageTotal = serializers.FloatField(min_value=0)
    ductLeakageToOutside = serializers.FloatField(min_value=0)
    mechanicalVentilationRate = serializers.FloatField(min_value=0, required=False)  # !


class MechanicalsEquipmentSerializer(serializers.Serializer):
    percentLoad = serializers.FloatField(min_value=0, max_value=100)
    efficiencyType = serializers.CharField(validators=[validators.validate_efficiency_type])
    efficiency = serializers.FloatField(min_value=0)


class MechanicalsEquipmentSerializer(serializers.Serializer):
    equipmentType = serializers.CharField(validators=[validators.validate_equipment_type])

    heating = MechanicalsEquipmentSerializer()
    cooling = MechanicalsEquipmentSerializer()
    waterHeating = MechanicalsEquipmentSerializer()


class MechanicalsSerializer(serializers.Serializer):
    summary = MechanicalsSummarySerializer()
    equipment = MechanicalsEquipmentSerializer(many=True)


class DetailsSerializer(serializers.Serializer):
    bedrooms = serializers.IntegerField(min_value=0)


class HousePlanSerializer(serializers.Serializer):
    thermalEnvelope = ThermalEnvelopeSerializer()
    mechanicals = MechanicalsSerializer()
    details = DetailsSerializer()


# Analysis (AnalysisSerializer)
class AnalysisEnergySummarySerializer(serializers.Serializer):
    coolingConsumption = serializers.FloatField()
    heatingConsumption = serializers.FloatField()
    waterHeatingConsumption = serializers.FloatField(required=False)
    lightingAndAppliancesConsumption = serializers.FloatField(required=False)
    cost = serializers.FloatField()
    solarGeneration = serializers.FloatField(required=False)

    # Not yet implemented by Ekotrope at this time
    # winterElectricPowerPeak = serializers.FloatField(required=False)
    # summerElectricPowerPeak = serializers.FloatField(required=False)


class AnalysisEnergyBreakdownByFuelSerializer(serializers.Serializer):
    fuel = serializers.CharField(validators=[validators.validate_fuel_type])
    heatingConsumption = serializers.FloatField()
    coolingConsumption = serializers.FloatField()
    waterHeatingConsumption = serializers.FloatField()
    lightingAndAppliancesConsumption = serializers.FloatField()
    cost = serializers.FloatField()


class AnalysisEnergyBreakdownByComponentSerializer(serializers.Serializer):
    category = serializers.CharField(validators=[validators.validate_component_category])
    heatingLoad = serializers.FloatField()
    coolingLoad = serializers.FloatField()


class AnalysisEnergyBreakdownSerializer(serializers.Serializer):
    byFuel = AnalysisEnergyBreakdownByFuelSerializer(many=True)  # must have 5, one per fuel type
    byComponent = AnalysisEnergyBreakdownByComponentSerializer(many=True)


class AnalysisEnergySerializer(serializers.Serializer):
    summary = AnalysisEnergySummarySerializer()
    breakdown = AnalysisEnergyBreakdownSerializer()


class AnalysisComplianceSerializer(serializers.Serializer):
    code = serializers.CharField(validators=[validators.validate_compliance_code])
    complianceStatus = serializers.CharField(validators=[validators.validate_compliance_status])


class AnalysisSerializer(serializers.Serializer):
    hersScore = serializers.FloatField()
    hersScoreNoPv = serializers.FloatField()
    buildingType = serializers.CharField(required=False)

    energy = AnalysisEnergySerializer()
    compliance = AnalysisComplianceSerializer(many=True)
