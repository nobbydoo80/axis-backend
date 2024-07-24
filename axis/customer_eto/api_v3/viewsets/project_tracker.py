"""project_tracker.py - Axis"""

__author__ = "Steven K"
__date__ = "8/22/21 12:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from celery import states
from django.apps import apps
from django.db.models import QuerySet
from drf_yasg import openapi

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.core.api_v3.serializers.task import STATE_CHOICES
from ..renderers import XMLRenderer
from ..serializers import (
    WashingtonCodeCreditCalculatorSerializer,
    EPS2021CalculatorSerializer,
    EPSFire2021CalculatorSerializer,
    EPS2022CalculatorSerializer,
)
from ..serializers.project_tracker import ProjectTrackerXMLSerializer, ProjectTrackerSerializer

from ..serializers.project_tracker.misc import (
    ProjectTrackerSubmitSerializer,
    ProjectTrackerStatusSerializer,
)
from ...calculator.eps_2021.base import HomePath, HomeSubType
from ...enumerations import ProjectTrackerSubmissionStatus
from ...models import FastTrackSubmission
from axis.core.api_v3.filters import AxisSearchFilter, AxisOrderingFilter, AxisFilterBackend
from axis.customer_eto.api_v3 import FASTTRACK_SUBMISSION_SEARCH_FIELDS, ProjectTrackerFilter

log = logging.getLogger(__name__)
config = apps.get_app_config("customer_eto")

prior_covered = config.PRE_2021_PROGRAMS + ["washington-code-credit"]


home_path_str_dict = {
    HomePath.PATH_1: "Pathway 1",
    HomePath.PATH_2: "Pathway 2",
    HomePath.PATH_3: "Pathway 3",
    HomePath.PATH_4: "Pathway 4",
}

home_subtype_str_dict = {
    HomeSubType.GHGW: "Gas Heat - Gas DHW",
    HomeSubType.EHEW: "Ele Heat - Ele DHW",
    HomeSubType.GHEW: "Gas Heat - Ele DHW",
    HomeSubType.EHGW: "Ele Heat - Gas DHW",
}


class ProjectTrackerXMLViewSet(viewsets.ViewSet):
    serializer_class = ProjectTrackerXMLSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["post", "get", "options", "trace"]

    @classmethod
    def get_eto_2022_calculator_context(cls, instance: FastTrackSubmission) -> dict:
        serializer = EPS2022CalculatorSerializer(data={"home_status": instance.home_status.id})
        serializer.is_valid(raise_exception=True)
        calculator = serializer.calculator

        data = {
            # Project Attributes!
            "annual_cost_electric": calculator.improved_electric_cost,
            "annual_cost_gas": calculator.improved_gas_cost,
            "carbon_score": calculator.carbon.carbon_score.total,
            "code_carbon_score": calculator.carbon.code_carbon_score.total,
            "code_carbon_similar": calculator.carbon.similar_size_carbon_score.total,
            "eto_path": home_path_str_dict.get(calculator.allocations.home_path, "Unknown"),
            "home_config": home_subtype_str_dict.get(calculator.allocations.sub_type, "Unknown"),
            "code_eps_score": calculator.calculations.code_eps_score,
            "eps_similar": calculator.projected.similar_size_eps,
            "total_kwh": calculator.savings.kwh.proposed,
            "total_therms": calculator.savings.therm.proposed,
            "estimated_annual_cost": calculator.annual_cost,
            "eps_score": calculator.calculations.eps_score,
            "estimated_monthly_cost": calculator.monthly_cost,
            "percentage_improvement": calculator.savings.mbtu.floored_pct_improvement * 100.0,
            # Measure Attributes
            "electric_life": calculator.allocations.electric.measure_life,
            "electric_load_profile": calculator.allocations.electric.load_profile.value,
            "verifier_electric_incentive": round(
                calculator.allocations.electric.verifier_incentive, 0
            ),
            "builder_electric_incentive": round(
                max(
                    [
                        calculator.allocations.electric.builder_incentive
                        + calculator.allocations.pt_builder_heat_pump_water_heater_allocation.electric,
                        0,
                    ]
                ),
                0,
            ),
            "gas_life": calculator.allocations.gas.measure_life,
            "gas_load_profile": calculator.allocations.gas.load_profile.value,
            "verifier_gas_incentive": round(calculator.allocations.gas.verifier_incentive, 0),
            "builder_gas_incentive": round(
                max(
                    [
                        calculator.allocations.gas.builder_incentive
                        + calculator.allocations.pt_builder_heat_pump_water_heater_allocation.gas,
                        0,
                    ]
                ),
                0,
            ),
            "kwh_savings": calculator.savings.kwh.savings,
            "therm_savings": calculator.savings.therm.savings,
            # EPSNZ SLE = net_zero_solar_incentive
            "net_zero_eps_incentive": calculator.incentives.net_zero_builder_incentive.incentive,
            "percentage_generation_kwh": calculator.percent_generation_kwh * 100.0,
            "percentage_therm_improvement": calculator.savings.therm.floored_pct_improvement
            * 100.0,
            # SOLRDYCON SLE  solar_ready_builder_incentive
            "solar_ready_builder_incentive": calculator.incentives.solar_ready_builder_incentive.incentive,
            "solar_ready_verifier_incentive": calculator.incentives.solar_ready_verifier_incentive.incentive,
            # EPSESH SLE = solar_storage_builder_incentive
            "solar_storage_builder_incentive": calculator.incentives.solar_storage_builder_incentive.incentive,
            # EPSESH ENH = EV Ready Incentive
            "ev_ready_builder_incentive": calculator.incentives.ev_ready_builder_incentive.incentive,
            # DEIBONUSBUILDER
            "cobid_builder_measure": calculator.incentives.cobid_builder_incentive.incentive,
            # DEIBONUSVERIFIER
            "cobid_verifier_incentive": calculator.incentives.cobid_verifier_incentive.incentive,
            # EPSFRFRTW
            "heat_type": calculator.heat_type,
            "has_triple_pane_windows": calculator.triple_pane_windows,
            "has_rigid_insulation": calculator.exterior_rigid_insulation,
            "has_sealed_attic": calculator.sealed_attic,
        }

        updateable_fields = [
            "builder_electric_incentive",
            "builder_gas_incentive",
            "rater_electric_incentive",
            "rater_gas_incentive",
            "net_zero_eps_incentive",
            "therm_savings",
            "kwh_savings",
        ]

        # Pull in the overrides for PT
        project_tracker = FastTrackSubmission.objects.get(home_status_id=instance.home_status.id)
        if project_tracker.payment_change_datetime:
            for field in updateable_fields:
                original = getattr(project_tracker, f"original_{field}")
                updated = getattr(project_tracker, field)
                if original and original != updated:
                    data[field] = updated
        return data

    @classmethod
    def get_eto_2021_calculator_context(cls, instance: FastTrackSubmission) -> dict:
        program_slug = instance.home_status.eep_program.slug
        if program_slug in "eto-2022" and instance.home_status.home.state == "WA":
            serializer = EPS2021CalculatorSerializer(data={"home_status": instance.home_status.id})
        elif program_slug in "eto-2021":
            serializer = EPS2021CalculatorSerializer(data={"home_status": instance.home_status.id})
        elif program_slug == "eto-fire-2021":
            serializer = EPSFire2021CalculatorSerializer(
                data={"home_status": instance.home_status.id}
            )
        else:
            raise KeyError(f"Program not found {instance.home_status.eep_program}")

        serializer.is_valid(raise_exception=True)
        calculator = serializer.calculator

        try:
            pv_generation_pct = calculator.improved.pv_kwh / (
                calculator.improved.total_kwh + calculator.improved.pv_kwh
            )
            pv_generation_pct = min([max([0, pv_generation_pct * 100.0]), 100.0])
        except TypeError:
            pv_generation_pct = 0.0

        data = {
            # Project Attributes!
            "annual_cost_electric": calculator.improved.electric_cost,
            "annual_cost_gas": calculator.improved.gas_cost,
            "carbon_score": calculator.improved_calculations.carbon_score,
            "code_carbon_score": calculator.code_calculations.code_carbon_score,
            "code_carbon_similar": calculator.projected.similar_size_carbon,
            "eto_path": home_path_str_dict.get(calculator.incentives.home_path, "Unknown"),
            "home_config": home_subtype_str_dict.get(calculator.incentives.sub_type, "Unknown"),
            "code_eps_score": calculator.code_calculations.code_eps_score,
            "eps_similar": calculator.projected.similar_size_eps,
            "total_kwh": calculator.improved.total_kwh,
            "total_therms": calculator.improved.total_therms,
            "estimated_annual_cost": calculator.annual_cost,
            "eps_score": calculator.improved_calculations.eps_score,
            "estimated_monthly_cost": calculator.monthly_cost,
            "percentage_improvement": calculator.improvement_data.floored_improvement_breakout.mbtu
            * 100.0,
            # Measure Attributes
            "electric_life": calculator.incentives.builder_allocation_data.electric.waml,
            "electric_load_profile": calculator.incentives.builder_allocation_data.electric.load_profile.value,
            "verifier_electric_incentive": round(
                calculator.incentives.verifier_allocation_data.electric.incentive, 0
            ),
            "builder_electric_incentive": round(
                calculator.incentives.builder_allocation_data.electric.incentive, 0
            ),
            "gas_life": calculator.incentives.builder_allocation_data.gas.waml,
            "gas_load_profile": calculator.incentives.builder_allocation_data.gas.load_profile.value,
            "verifier_gas_incentive": round(
                calculator.incentives.verifier_allocation_data.gas.incentive, 0
            ),
            "builder_gas_incentive": round(
                calculator.incentives.builder_allocation_data.gas.incentive, 0
            ),
            "kwh_savings": calculator.improvement_data.savings.kwh,
            "therm_savings": calculator.improvement_data.savings.therms,
            "net_zero_eps_incentive": calculator.net_zero.net_zero_incentive,
            "percentage_generation_kwh": pv_generation_pct,
            "percentage_therm_improvement": calculator.improvement_data.percent_improvement_breakout.therms
            * 100.0,
            "energy_smart_homes_eps_incentive": calculator.net_zero.energy_smart_incentive,
        }

        updateable_fields = [
            "builder_electric_incentive",
            "builder_gas_incentive",
            "rater_electric_incentive",
            "rater_gas_incentive",
            "net_zero_eps_incentive",
            "energy_smart_homes_eps_incentive",
        ]

        if program_slug == "eto-fire-2021":
            data["heat_type"] = calculator.heat_type
            data["has_triple_pane_windows"] = calculator.net_zero.has_triple_pane_windows
            data["has_rigid_insulation"] = calculator.net_zero.has_rigid_insulation
            data["has_sealed_attic"] = calculator.net_zero.has_rigid_insulation
            updateable_fields += [
                "therm_savings",
                "kwh_savings",
                "mbtu_savings",
            ]

        # Pull in the overrides for PT
        project_tracker = FastTrackSubmission.objects.get(home_status_id=instance.home_status.id)
        if project_tracker.payment_change_datetime:
            for field in updateable_fields:
                original = getattr(project_tracker, f"original_{field}")
                updated = getattr(project_tracker, field)
                if original and original != updated:
                    data[field] = updated
        return data

    @classmethod
    def get_washington_code_credit_calculator_context(cls, instance: FastTrackSubmission) -> dict:
        serializer = WashingtonCodeCreditCalculatorSerializer(
            data={"home_status": instance.home_status.id}
        )
        serializer.is_valid(raise_exception=True)
        raw = serializer.calculator.summary_data
        savings = serializer.calculator.savings_data

        return {
            "builder_incentive": raw["total_builder_incentive"],
            "verifier_incentive": raw["verifier_incentive"],
            "fireplace_incentive": raw["fireplace_incentive"],
            "thermostat_incentive": raw["thermostat_incentive"],
            "code_credit_incentive": raw["code_credit_incentive"],
            "fireplace_therm_savings": savings["fireplace_therm_savings"],
            "thermostat_therm_savings": savings["thermostat_therm_savings"],
            "code_based_therm_savings": savings["code_based_therm_savings"],
            "water_heating_option": serializer.calculator.water_heating_option.value,
            "total_kwh": 0,  # TODO Need to know where to get this from
            "total_therms": 0,  # TODO Need to know where to get this from
        }

    @classmethod
    def get_legacy_calculator_context(cls, instance: FastTrackSubmission) -> dict:
        """These are used under project > attributes"""
        # This is legacy to make sure that we can do this from one place
        from ...reports.legacy_utils import get_legacy_calculation_data

        raw = get_legacy_calculation_data(
            instance.home_status, return_fastrack_data=False, return_errors=True
        )

        if raw is None or "errors" in raw:
            return {}

        return {
            # Project Attributes!
            "annual_cost_electric": raw["improved_input"]["electric_cost"],
            "annual_cost_gas": raw["improved_input"]["gas_cost"],
            "carbon_score": raw["result"]["carbon_score"],
            "code_carbon_score": raw["result"]["code_carbon_score"],
            "code_carbon_similar": raw["result"]["projected_size_or_home_carbon"],
            "eto_path": raw["incentive"].get("project_tracker_pathway"),
            "home_config": raw["incentive"].get("project_tracker_home_config"),
            "code_eps_score": raw["result"]["code_eps_score"],
            "eps_similar": raw["result"]["projected_size_or_home_eps"],
            "total_kwh": raw["improved_input"]["total_kwh"],
            "total_therms": raw["improved_input"]["total_therms"],
            "estimated_annual_cost": raw["result"]["estimated_annual_cost"],
            "eps_score": raw["result"]["eps_score"],
            "estimated_monthly_cost": raw["result"]["estimated_monthly_cost"],
            "percentage_improvement": raw["result"]["floored_percentage_improvement"] * 100.0,
            # Measure Attributes
            "electric_life": raw["incentive"]["electric_waml"],
            "electric_load_profile": raw["incentive"]["electric_load_profile"],
            "verifier_electric_incentive": raw["incentive"]["verifier_electric_incentive"],
            "builder_electric_incentive": raw["incentive"]["builder_electric_incentive"],
            "gas_life": raw["incentive"]["gas_waml"],
            "gas_load_profile": raw["incentive"]["gas_load_profile"],
            "verifier_gas_incentive": raw["incentive"]["verifier_gas_incentive"],
            "builder_gas_incentive": raw["incentive"]["builder_gas_incentive"],
            "kwh_savings": raw["calculations"]["savings"]["kwh"],
            "therm_savings": raw["calculations"]["savings"]["therms"],
            "net_zero_eps_incentive": raw.get("net_zero", {}).get("net_zero_eps_incentive", 0.0),
            "percentage_generation_kwh": raw["calculations"].get("percentage_generation_kwh", 0.0)
            * 100.0,
            "percentage_therm_improvement": raw["calculations"]["pct_improvement"]["therms"]
            * 100.0,
            "energy_smart_homes_eps_incentive": raw.get("net_zero", {}).get(
                "energy_smart_homes_eps_incentive"
            ),
        }

    @classmethod
    def get_collected_input_context(cls, instance: FastTrackSubmission) -> dict:
        """These are used in the project > measures"""
        context = {"user__company": instance.home_status.company}
        collector = ExcelChecklistCollector(instance.home_status.collection_request, **context)
        instruments = collector.get_instruments()
        instrument_lookup = {i.measure_id: i for i in instruments}

        def get_collected_input(measure_id, default=None, as_integer=False, unprocessed=False):
            if measure_id not in instrument_lookup:
                return default

            value = (
                collector.get_inputs(
                    instrument=instrument_lookup[measure_id], cooperative_requests=True
                )
                .order_by("pk")
                .last()
            )
            if value is None:
                return default
            if unprocessed:
                return value.data
            value = value.data.get("input")
            return int(value) if as_integer else value

        if instance.home_status.eep_program.slug in ["washington-code-credit"]:
            return {
                "conditioned_floor_area": get_collected_input("wcc-conditioned_floor_area"),
                "water_heater_brand": get_collected_input("wcc-water_heater_brand"),
                "water_heater_model": get_collected_input("wcc-water_heater_model"),
                "water_heater_gas_uef": get_collected_input("wcc-gas_water_heater_uef"),
                "water_heater_electric_uef": get_collected_input("wcc-electric_water_heater_uef"),
                "water_heater_fuel": get_collected_input("wcc-water_heating_fuel"),
                "furnace_brand": get_collected_input("wcc-furnace_brand"),
                "furnace_model": get_collected_input("wcc-furnace_model"),
                "furnace_afue": get_collected_input("wcc-furnace_afue"),
                "furnace_location": get_collected_input("wcc-furnace_location"),
                "thermostat_brand": get_collected_input("wcc-thermostat_type"),
            }
        else:
            water_heater_equipment = get_collected_input(
                "equipment-water-heater", unprocessed=True, default={}
            ).get("input", {})
            furnace_equipment = get_collected_input(
                "equipment-furnace", unprocessed=True, default={}
            ).get("input", {})
            heat_pump_equipment = get_collected_input(
                "equipment-heat-pump", unprocessed=True, default={}
            ).get("input", {})

            solar_kw = get_collected_input("ets-solar-kw-capacity")
            if solar_kw is None:
                solar_kw = get_collected_input("non-ets-solar-kw-capacity")

            return {
                # Water Heater
                "water_heater_brand": water_heater_equipment.get("brand_name"),
                "water_heater_model": water_heater_equipment.get("model_number"),
                "water_heater_heat_pump_sn": get_collected_input(
                    "equipment-heat-pump-water-heater-serial-number"
                ),
                "water_heater_gas_sn": get_collected_input(
                    "equipment-gas-tank-water-heater-serial-number"
                ),
                "water_heater_tankless_sn": get_collected_input(
                    "equipment-gas-tankless-water-heater-serial-number"
                ),
                # Heating
                "primary_heating_type": get_collected_input("primary-heating-equipment-type"),
                "furnace_brand": furnace_equipment.get("brand_name"),
                "furnace_model": furnace_equipment.get("model_number"),
                "heat_pump_brand": heat_pump_equipment.get("brand_name"),
                "heat_pump_model": heat_pump_equipment.get("outdoor_model_number"),
                "heat_pump_sn": get_collected_input(
                    "equipment-heat-pump-water-heater-serial-number"
                ),
                "other_heater_type": get_collected_input("equipment-heating-other-type"),
                "other_heater_brand": get_collected_input("equipment-heating-other-brand"),
                "other_heater_model": get_collected_input("equipment-heating-other-model-number"),
                "has_battery_storage": get_collected_input("has-battery-storage"),
                "grid_harmonization_elements": get_collected_input("grid-harmonization-elements"),
                "solar_elements": get_collected_input("solar-elements"),
                "thermostat_brand": get_collected_input("smart-thermostat-brand"),
                "eto_additional_incentives": get_collected_input("eto-additional-incentives"),
                "electric_elements": get_collected_input("eto-electric-elements"),
                "solar_kw_capacity": solar_kw,
                "fire_rebuild_qualification": get_collected_input("fire-rebuild-qualification"),
                "payment_redirected": get_collected_input("builder-payment-redirected"),
            }

    @classmethod
    def get_utility_codes_context(cls, instance: FastTrackSubmission) -> dict:
        """These all over the place"""
        app = apps.get_app_config("customer_eto")
        abbreviations = app.PROJECT_TRACKER_COMPANY_ABBREVIATIONS

        electric_utility = "N/A"
        electric_company = instance.home_status.get_electric_company()
        if electric_company:
            electric_utility = abbreviations.get(electric_company.slug, "N/A")

        gas_utility = "N/A"
        gas_company = instance.home_status.get_gas_company()
        if gas_company:
            gas_utility = abbreviations.get(gas_company.slug, "N/A")

        return {"gas_utility_code": gas_utility, "electric_utility_code": electric_utility}

    @classmethod
    def get_context_data(self, instance: FastTrackSubmission) -> dict:
        context = {}
        if instance.home_status.eep_program.slug in ["eto-2022"]:
            if instance.home_status.home.state == "WA":
                context.update(self.get_eto_2021_calculator_context(instance))
            else:
                context.update(self.get_eto_2022_calculator_context(instance))
        elif instance.home_status.eep_program.slug in ["eto-2021", "eto-fire-2021"]:
            context.update(self.get_eto_2021_calculator_context(instance))
        elif instance.home_status.eep_program.slug in ["washington-code-credit"]:
            context.update(self.get_washington_code_credit_calculator_context(instance))
        else:
            context.update(self.get_legacy_calculator_context(instance))

        context.update(self.get_collected_input_context(instance))
        context.update(self.get_utility_codes_context(instance))

        return context

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "task_ids",
                openapi.IN_QUERY,
                description="Task IDS relating to a particular submission",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.FORMAT_UUID),
            ),
        ],
        responses={"200": ProjectTrackerSubmitSerializer},
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def submit(self, request: Request, pk: int) -> Response:
        """This will submit data to ETO.  Note: ID is the home_status ID"""
        from axis.customer_eto.tasks.fasttrack import submit_fasttrack_xml

        submission = FastTrackSubmission.objects.filter(home_status_id=pk).first()
        if not submission:
            s = ProjectTrackerSubmitSerializer(
                data={"id": pk, "content": "PT does not exist for home_status"}
            )
            s.is_valid(raise_exception=True)
            return Response(s.data, status=status.HTTP_404_NOT_FOUND)

        project_types = submission.get_project_types()
        submission = FastTrackSubmission.objects.filter(home_status_id=pk).first()
        msg = f"{' and '.join(project_types)} PT on home {submission.home_status.home}"

        # Which ones are not satisfied, this allows resubmission
        sle_satisfied = True
        if "SLE" in project_types:
            sle_satisfied = submission.solar_project_id not in ["", None]
            if sle_satisfied:
                project_types.pop(project_types.index("SLE"))
        enh_satisfied = True
        if "ENH" in project_types:
            enh_satisfied = submission.project_id not in ["", None]
            if enh_satisfied:
                project_types.pop(project_types.index("ENH"))

        if enh_satisfied and sle_satisfied:
            msg += f" has already submitted with status {submission.get_submit_status_display()}"
            msg += f" Submission ID: {submission.id}"
            s = ProjectTrackerSubmitSerializer(
                data={
                    "id": pk,
                    "content": msg,
                    "project_types": project_types,
                }
            )

            s.is_valid(raise_exception=True)
            return Response(s.data, status=status.HTTP_400_BAD_REQUEST)

        # Ensure we can capture when/who this  was submitted.
        submission = FastTrackSubmission.objects.filter(home_status_id=pk).first()
        update_fields = ["modified_date", "submit_user"]
        if "ENH" in project_types:
            update_fields.append("submit_status")
            submission.submit_status = ProjectTrackerSubmissionStatus.SUBMITTED
        if "SLE" in project_types:
            update_fields.append("solar_submit_status")
            submission.solar_submit_status = ProjectTrackerSubmissionStatus.SUBMITTED
        submission.submit_user = request.user
        submission.save(update_fields=update_fields)

        data = {
            "id": pk,
            "content": msg
            + f" has been submitted for processing by {request.user.first_name} {request.user.last_name[0]}.",
            "task_ids": [],
            "project_types": project_types,
        }

        for project_type in project_types:
            task = submit_fasttrack_xml.delay(
                pk, user_id=request.user.id, project_type=project_type
            )
            data["task_ids"].append(task.id)
        s = ProjectTrackerSubmitSerializer(data=data)
        s.is_valid(raise_exception=True)
        return Response(s.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "task_ids",
                openapi.IN_QUERY,
                description="Task IDS relating to a particular submission",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.FORMAT_UUID),
            ),
        ],
        responses={"200": ProjectTrackerStatusSerializer},
    )
    @action(
        methods=["get"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def status(self, request: Request, pk: int) -> Response:
        # A particular submission can now have multiple tasks associated with it
        # as it could be both an ENH project and SLE project.
        task_ids = request.query_params.get("task_ids")
        task_ids = task_ids.split(",") if task_ids else []

        submission = FastTrackSubmission.objects.filter(home_status_id=pk).first()
        if not submission:
            s = ProjectTrackerStatusSerializer(
                data={
                    "id": pk,
                    "result": "PT does not exist for home_status",
                    "status": "FAILURE",
                    "status_display": "Failure",
                }
            )
            s.is_valid(raise_exception=True)
            return Response(s.data, status=status.HTTP_404_NOT_FOUND)

        project_types = submission.get_project_types()
        result = {"id": pk, "task_statuses": [], "task_ids": []}

        overall_status = None
        statuses = []
        _job_results = {pt_type: None for pt_type in project_types}
        for task_id in task_ids:
            result["task_statuses"].append({"task_id": task_id})
            result["task_ids"].append(task_id)
            # We want to figure out the statuses
            from axis.core.api_v3.serializers import CeleryAsyncResultSerializer

            serializer = CeleryAsyncResultSerializer(data={"task_id": task_id})
            serializer.is_valid(raise_exception=True)
            statuses.append(serializer.data)
        if statuses:
            # Top level statuses tell us whether the task was successful or not.
            # We will use those but prefer to dig deeper.  Let's collect each status
            # and result (if we have one.)
            _s = dict()
            for idx, stat in enumerate(statuses):
                if stat["kwargs"]:
                    idx = eval(stat["kwargs"])["project_type"]
                _s[idx] = stat["status"]
                _result = f"{stat['status'].lower()}"
                # Are we completed
                if stat["result"] and "status" in stat["result"]:
                    _s[idx] = stat["result"]["status"]
                    _result = stat["result"]["result"]

                if isinstance(idx, str):
                    _job_results[idx] = _result

            _s = list(set(_s.values()))

            # First did the job go through?
            if states.FAILURE in _s:
                overall_status = states.FAILURE
            elif len(_s) == 1:
                overall_status = _s[0]  # Could pending, completed, failed, started
            else:
                overall_status = states.STARTED

        # Async results default to pending.  We need to make sure that is accurate
        if not task_ids or overall_status == states.PENDING:
            _s = []
            if "ENH" in project_types:
                _s.append(submission.submit_status or states.PENDING)
                if submission.submit_status:
                    _job_results["ENH"] = submission.submit_status.lower()
                    if submission.project_id:
                        _job_results["ENH"] = f"{submission.project_id} identified"
            if "SLE" in project_types:
                _s.append(submission.solar_submit_status or states.PENDING)
                if submission.solar_submit_status:
                    _job_results["SLE"] = submission.solar_submit_status.lower()
                    if submission.solar_project_id:
                        _job_results["SLE"] = f"{submission.solar_project_id} identified"

            _s = list(set(_s))
            # First did the job go through?
            if states.FAILURE in _s:
                overall_status = states.FAILURE
            elif len(_s) == 1:
                overall_status = _s[0]  # Could pending, completed, failed, started
            else:
                overall_status = states.STARTED

        for pt_type in _job_results:
            if _job_results[pt_type] is None:
                _job_results[pt_type] = f"{pt_type} {overall_status.lower()}."

        result.update(
            {
                "status": overall_status,
                "status_display": dict(STATE_CHOICES).get(overall_status),
                "result": " ".join([f"{k}: {v}." for k, v in _job_results.items()]),
            }
        )
        s = ProjectTrackerStatusSerializer(data=result)
        s.is_valid(raise_exception=True)
        return Response(s.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        methods=["get"],
        responses={"200": ProjectTrackerXMLSerializer},
    )
    @action(
        methods=["get"],
        detail=True,
        permission_classes=[IsAuthenticated],
        renderer_classes=(XMLRenderer,),
    )
    def xml(self, request: Request, pk: int) -> Response:
        """Return the XML that is sent to Project Tracker.

        ID: Home Status ID
        """
        instance = FastTrackSubmission.objects.get(home_status=pk)

        results = []
        context = self.get_context_data(instance)
        for project_type in instance.get_project_types():
            context["project_type"] = project_type
            serializer = ProjectTrackerXMLSerializer(instance=instance, context=context)
            results.append(serializer.data)

        return Response(results, status=status.HTTP_200_OK)


class ProjectTrackerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ProjectTracker/FastTrackSubmission viewset
    """

    model = FastTrackSubmission
    permission_classes = (IsAuthenticated,)
    queryset = model.objects.all()
    serializer_class = ProjectTrackerSerializer
    filter_backends = [AxisFilterBackend, AxisSearchFilter, AxisOrderingFilter]
    search_fields = FASTTRACK_SUBMISSION_SEARCH_FIELDS
    filterset_class = ProjectTrackerFilter

    def get_queryset(self) -> QuerySet:
        return self.model.objects.filter_by_user(self.request.user)
