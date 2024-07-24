"""legacy_utils.py - axis"""

__author__ = "Steven K"
__date__ = "12/1/22 10:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from axis.customer_eto.models import FastTrackSubmission

log = logging.getLogger(__name__)


def get_legacy_calculation_data(home_status, return_fastrack_data=False, return_errors=False):
    """Provide calculator data as needed."""
    #
    if home_status.eep_program.slug not in [
        "eto",
        "eto-2014",
        "eto-2015",
        "eto-2016",
        "eto-2017",
        "eto-2018",
        "eto-2019",
        "eto-2020",
    ]:
        raise DeprecationWarning(
            f"{home_status.eep_program} ({home_status.eep_program.slug}) is "
            f"not supported via this way.  Use a corresponding serializer"
        )

    from axis.customer_eto.views.views import EPSCalculatorFormView
    from axis.customer_eto.calculator.eps import get_eto_calculation_completed_form

    _view = EPSCalculatorFormView()
    calculation_form = get_eto_calculation_completed_form(home_status)
    if calculation_form.is_valid():
        _eps_data = _view.calculate(home_status, **calculation_form.cleaned_data)
        submission, _create = FastTrackSubmission.objects.get_or_create(home_status=home_status)

        data = {}

        inputs = _eps_data.get("inputs")
        result = _eps_data.get("result")
        incentive = _eps_data.get("incentive")
        calc_results = _eps_data.get("calculations").get("savings")

        data["gas_utility"] = inputs.get("electric_utility", None)
        data["electric_utility"] = inputs.get("electric_utility", None)
        data["gas_hot_water"] = inputs.get("has_gas_hot_water", None)

        data["eps_score"] = round(result.get("eps_score"), 0)
        data["eps_score_built_to_code_score"] = round(result.get("code_eps_score"), 0)

        data["percent_improvement"] = round(result.get("floored_percentage_improvement"), 2)
        data["percent_improvement_kwh"] = round(result.get("floored_kwh_percentage_improvement"), 2)
        data["percent_improvement_therms"] = round(
            result.get("floored_therm_percentage_improvement"), 2
        )

        data["builder_incentive"] = round(incentive.get("builder_incentive"), 2)
        data["rater_incentive"] = round(incentive.get("verifier_incentive"), 2)

        data["carbon_score"] = round(result.get("carbon_score"), 1)
        data["carbon_built_to_code_score"] = round(result.get("code_carbon_score"), 1)
        data["estimated_annual_energy_costs"] = round(result.get("estimated_annual_cost"), 2)
        data["estimated_monthly_energy_costs"] = round(result.get("estimated_monthly_cost"), 2)
        data["estimated_annual_energy_costs_code"] = None
        data["estimated_monthly_energy_costs_code"] = None
        data["similar_size_eps_score"] = round(result.get("projected_size_or_home_eps"), 0)
        data["similar_size_carbon_score"] = round(result.get("projected_size_or_home_carbon"), 1)

        data["builder_gas_incentive"] = round(incentive.get("builder_gas_incentive"), 2)
        data["builder_electric_incentive"] = round(incentive.get("builder_electric_incentive"), 2)

        data["rater_gas_incentive"] = round(incentive.get("verifier_gas_incentive"), 2)
        data["rater_electric_incentive"] = round(incentive.get("verifier_electric_incentive"), 2)

        data["therm_savings"] = round(calc_results.get("therms"), 2)
        data["kwh_savings"] = round(calc_results.get("kwh"), 2)
        data["mbtu_savings"] = round(calc_results.get("mbtu"), 2)
        data["project_id"] = None
        data["solar_project_id"] = None
        data["homestatus_id"] = home_status.id
        version = datetime.datetime.strptime(_eps_data.get("version"), "%Y%m%d").date()
        data["version"] = data["eps_calculator_version"] = version
        data["state_abbreviation"] = home_status.home.state

        data["electric_load_profile"] = incentive.get("electric_load_profile")
        data["gas_load_profile"] = incentive.get("gas_load_profile")

        net_zero = _eps_data.get("net_zero")
        data["net_zero_eps_incentive"] = net_zero.get("net_zero_eps_incentive")
        data["energy_smart_homes_eps_incentive"] = net_zero.get("energy_smart_homes_eps_incentive")
        data["net_zero_solar_incentive"] = net_zero.get("net_zero_solar_incentive")
        data["energy_smart_homes_solar_incentive"] = net_zero.get(
            "energy_smart_homes_solar_incentive"
        )

        # EPS Report Fields
        improved_inputs = _eps_data.get("improved_input", {})
        data["electric_cost_per_month"] = round(improved_inputs.get("electric_cost", 0.0) / 12.0, 2)
        data["natural_gas_cost_per_month"] = round(improved_inputs.get("gas_cost", 0.0) / 12.0, 2)

        improved = _eps_data.get("calculations", {}).get("improved", {})
        data["improved_total_kwh"] = improved.get("total_kwh", 0.0)
        data["improved_total_therms"] = improved.get("total_kwh", 0.0)
        data["solar_hot_water_kwh"] = improved_inputs.get("solar_hot_water_kwh")
        data["solar_hot_water_therms"] = improved_inputs.get("solar_hot_water_therms")
        data["pv_kwh"] = improved_inputs.get("pv_kwh")
        data["projected_carbon_consumption_electric"] = result.get("total_electric_carbon")
        data["projected_carbon_consumption_natural_gas"] = result.get("total_gas_carbon")

        if not submission.is_locked():
            save_required = []
            for field in submission._meta.fields:
                if field.name in [
                    "id",
                    "home_status",
                    "project_id",
                    "solar_project_id",
                    "original_builder_electric_incentive",
                    "original_builder_gas_incentive",
                    "original_builder_incentive",
                    "original_rater_electric_incentive",
                    "original_rater_gas_incentive",
                    "original_rater_incentive",
                    "original_net_zero_eps_incentive",
                    "original_energy_smart_homes_eps_incentive",
                    "original_net_zero_solar_incentive",
                    "original_energy_smart_homes_solar_incentive",
                    "original_therm_savings",
                    "original_kwh_savings",
                    "original_mbtu_savings",
                    "payment_change_user",
                    "payment_change_datetime",
                    "payment_revision_comment",
                    # Washington Code Credit
                    "required_credits_to_meet_code",
                    "achieved_total_credits",
                    "eligible_gas_points",
                    "code_credit_incentive",
                    "thermostat_incentive",
                    "fireplace_incentive",
                    # EPS FIRE
                    "triple_pane_window_incentive",
                    "rigid_insulation_incentive",
                    "sealed_attic_incentive",
                    # ETO 2022
                    "cobid_builder_incentive",
                    "cobid_verifier_incentive",
                    "solar_ready_builder_incentive",
                    "solar_ready_verifier_incentive",
                    "ev_ready_builder_incentive",
                    "solar_storage_builder_incentive",
                    "heat_pump_water_heater_incentive",
                    "percent_generation_kwh",
                    # Task details
                    "submit_user",
                    "submit_status",
                    "solar_submit_status",
                    "submission_count",
                    "created_date",
                    "modified_date",
                ]:
                    continue

                sub_value = getattr(submission, field.name)
                if (
                    getattr(submission, field.name) is not None
                    and field.__class__.__name__ == "DecimalField"
                ):
                    sub_value = float(getattr(submission, field.name))

                if sub_value != data[field.name]:
                    # log.debug("%s - %s", getattr(submission, field.name), data[field.name])
                    setattr(submission, field.name, data[field.name])
                    save_required.append(field.name)

            if save_required:
                if not _create:
                    log.info(
                        "Updating %d value for Fast Track ID: %s with new data - %s",
                        len(save_required),
                        submission.id,
                        save_required,
                    )
                submission.save()
        else:
            # If this is locked we have externally changed the incentives respect it.
            incentive_elements = [
                "builder_gas_incentive",
                "builder_electric_incentive",
                "builder_incentive",
                "rater_gas_incentive",
                "rater_electric_incentive",
                "rater_incentive",
            ]
            net_zero_elements = [
                "net_zero_eps_incentive",
                "energy_smart_homes_eps_incentive",
                "net_zero_solar_incentive",
                "energy_smart_homes_solar_incentive",
            ]
            if submission.payment_change_user and submission.payment_change_datetime:
                for incentive_item in incentive_elements + net_zero_elements:
                    value = getattr(submission, incentive_item)
                    data[incentive_item] = value
                    if incentive_item in incentive_elements:
                        _eps_data["incentive"][incentive_item] = value
                    if incentive_item in net_zero_elements:
                        _eps_data["net_zero"][incentive_item] = value

        if not return_fastrack_data:
            return _eps_data
        return data
    if return_errors:
        errs = []
        for key, value in calculation_form.errors.items():
            if key == "__all__":
                errs.append(value.as_text())
            else:
                label = next((f.label for f in calculation_form if f.name == key))
                errs.append("{}: {}".format(label, value.as_text()))
        return {"errors": errs}
    return None
