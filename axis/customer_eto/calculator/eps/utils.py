""" Energy Performance Score calculator utilities """


import logging

__author__ = "Autumn Valenta"
__date__ = "11/16/15 4:26 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

ETO_GEN2 = ["eto-2017", "eto-2018", "eto-2019", "eto-2020"]

log = logging.getLogger(__name__)

QUESTION_SLUG_DATA = {
    "eto": {
        "ETO_HEAT_TYPE_QUESTION_SLUG": "eto-primary_heat_type",
        "ETO_PATHWAY_QUESTION_SLUG": "eto-eto_pathway",
        "ETO_WATER_HEATER_EF_QUESTION_SLUG": "eto-water_heater_ef",
        "ETO_WATER_HEATER_TYPE_SLUG": "eto-water_heater_heat_type",
    },
    "eto-2015": {
        "ETO_HEAT_TYPE_QUESTION_SLUG": "eto-primary_heat_type",
        "ETO_PATHWAY_QUESTION_SLUG": "eto-eto_pathway",
        "ETO_WATER_HEATER_EF_QUESTION_SLUG": "eto-water_heater_ef",
        "ETO_WATER_HEATER_TYPE_SLUG": "eto-water_heater_heat_type",
    },
    "eto-2016": {
        "ETO_HEAT_TYPE_QUESTION_SLUG": "eto-primary_heat_type-2016",
        "ETO_PATHWAY_QUESTION_SLUG": "eto-eto_pathway",
        "ETO_WATER_HEATER_EF_QUESTION_SLUG": "eto-water_heater_ef",
        "ETO_WATER_HEATER_TYPE_SLUG": "eto-water_heater_heat_type",
    },
    "eto-2017": {
        "ETO_HEAT_TYPE_QUESTION_SLUG": "eto-primary_heat_type-2016",
        "ETO_WATER_HEATER_EF_QUESTION_SLUG": "eto-water_heater_ef",
        "ETO_WATER_HEATER_TYPE_SLUG": "eto-water_heater_heat_type",
        "ETO_QUALIFYING_THERMOSTAT": "eto-qualifying_thermostat",
        "ETO_SHOWER_HEAD_1P5": "eto-shower-head-1p5",
        "ETO_SHOWER_HEAD_1P6": "eto-shower-head-1p6",
        "ETO_SHOWER_HEAD_1P75": "eto-shower-head-1p75",
        "ETO_SHOWER_WAND_1P5": "eto-shower-wand-1p5",
    },
    "eto-2018": {
        "ETO_HEAT_TYPE_QUESTION_SLUG": "primary-heating-equipment-type",
        "ETO_QUALIFYING_THERMOSTAT": "smart-thermostat-brand",
        "ETO_SHOWER_HEAD_1P5": "showerheads15-quantity",
        "ETO_SHOWER_HEAD_1P6": "showerheads16-quantity",
        "ETO_SHOWER_HEAD_1P75": "showerheads175-quantity",
        "ETO_SHOWER_WAND_1P5": "showerwands15-quantity",
    },
}

CHECKLIST_PATHWAY_ANSWERS = {
    "Pathway 1": "path 1",
    "Pathway 2": "path 2",
    "Pathway 3": "path 3",
    "Pathway 4": "path 4",
    "Pathway 5": "path 5",
    "Percent Improvement": "pct",
}


def get_legacy_eto_calculation_data(home_status):
    """
    Assembles the required data values for an ETO calculation.  Missing data or ``None`` values
    will cause the ETO calculator to raise errors for the frontend.
    """
    from axis.checklist.models import Answer

    calculator_variables = {
        "site_address": "{addr} {city}, {state} {zip}".format(
            **{
                "addr": home_status.home.get_addr(),
                "city": home_status.home.city,
                "state": home_status.home.state,
                "zip": home_status.home.zipcode,
            }
        ),
    }

    calculator_variables["program"] = home_status.eep_program.id
    calculator_variables["us_state"] = home_status.home.state

    answer_slugs = QUESTION_SLUG_DATA.get(home_status.eep_program.slug, {})
    electric_utility = home_status.get_electric_company()
    if electric_utility:
        calculator_variables["electric_utility"] = electric_utility.id

    gas_utility = home_status.get_gas_company()
    if gas_utility:
        calculator_variables["gas_utility"] = gas_utility.id

    if home_status.floorplan and home_status.floorplan.remrate_target:
        calculator_variables["rem_simulation"] = home_status.floorplan.remrate_target.id

    answers = home_status.home.answer_set.all()
    try:
        ans = answers.get(question__slug=answer_slugs.get("ETO_HEAT_TYPE_QUESTION_SLUG"))
        calculator_variables["primary_heating_equipment_type"] = ans.answer
    except Answer.DoesNotExist:
        log.debug(
            "No answer for ETO heat-type question %r",
            answer_slugs.get("ETO_HEAT_TYPE_QUESTION_SLUG"),
        )
    except Answer.MultipleObjectsReturned:
        ans = answers.filter(question__slug=answer_slugs.get("ETO_HEAT_TYPE_QUESTION_SLUG")).last()
        answers.filter(question__slug=answer_slugs.get("ETO_HEAT_TYPE_QUESTION_SLUG")).exclude(
            id=ans.id
        ).delete()
        log.warning(
            "Multiple answers for ETO heat-type question %r - %s",
            answer_slugs.get("ETO_HEAT_TYPE_QUESTION_SLUG"),
            home_status,
        )

    if home_status.eep_program.slug not in ETO_GEN2:
        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_WATER_HEATER_EF_QUESTION_SLUG"))
            calculator_variables["hot_water_ef"] = float(ans.answer)
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO hot water EF question %r",
                answer_slugs.get("ETO_WATER_HEATER_EF_QUESTION_SLUG"),
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(
                question__slug=answer_slugs.get("ETO_WATER_HEATER_EF_QUESTION_SLUG")
            ).last()
            answers.filter(
                question__slug=answer_slugs.get("ETO_WATER_HEATER_EF_QUESTION_SLUG")
            ).exclude(id=ans.id).delete()
            log.warning(
                "Multiple answers for ETO hot water EF question %r - %s",
                answer_slugs.get("ETO_WATER_HEATER_EF_QUESTION_SLUG"),
                home_status,
            )

        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_WATER_HEATER_TYPE_SLUG"))
            calculator_variables["hot_water_type"] = ans.answer
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO hot water type question %r",
                answer_slugs.get("ETO_WATER_HEATER_TYPE_SLUG"),
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(
                question__slug=answer_slugs.get("ETO_WATER_HEATER_TYPE_SLUG")
            ).last()
            answers.filter(question__slug=answer_slugs.get("ETO_WATER_HEATER_TYPE_SLUG")).exclude(
                id=ans.id
            ).delete()
            log.warning(
                "Multiple answers for ETO hot water type question %r - %s",
                answer_slugs.get("ETO_WATER_HEATER_TYPE_SLUG"),
                home_status,
            )

        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_PATHWAY_QUESTION_SLUG"))
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO pathway question %r",
                answer_slugs.get("ETO_PATHWAY_QUESTION_SLUG"),
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(
                question__slug=answer_slugs.get("ETO_PATHWAY_QUESTION_SLUG")
            ).last()
            answers.filter(question__slug=answer_slugs.get("ETO_PATHWAY_QUESTION_SLUG")).exclude(
                id=ans.id
            ).delete()
            log.warning(
                "Multiple answers for ETO pathway question %r - %s",
                answer_slugs.get("ETO_PATHWAY_QUESTION_SLUG"),
                home_status,
            )
        else:
            pathway = CHECKLIST_PATHWAY_ANSWERS.get(ans.answer)
            if pathway:
                calculator_variables["pathway"] = pathway
            else:
                log.debug(
                    "Invalid answer for ETO pathway question %r: %r",
                    answer_slugs.get("ETO_PATHWAY_QUESTION_SLUG"),
                    pathway,
                )
    else:
        calculator_variables["qualifying_thermostat"] = "no qualifying smart thermostat"
        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_QUALIFYING_THERMOSTAT"))
            if (
                "gas" in calculator_variables.get("primary_heating_equipment_type")
                and ans
                and ans.answer.lower() != "n/a"
            ):
                calculator_variables["qualifying_thermostat"] = "yes-ducted gas furnace"
            elif (
                "electric" in calculator_variables.get("primary_heating_equipment_type")
                and ans
                and ans.answer.lower() != "n/a"
            ):
                calculator_variables["qualifying_thermostat"] = "yes-ducted air source heat pump"
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO qualifying Thermostat %r",
                answer_slugs.get("ETO_QUALIFYING_THERMOSTAT"),
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(
                question__slug=answer_slugs.get("ETO_QUALIFYING_THERMOSTAT")
            ).last()
            answers.filter(question__slug=answer_slugs.get("ETO_QUALIFYING_THERMOSTAT")).exclude(
                id=ans.id
            ).delete()
            log.warning(
                "Multiple answers for ETO Qualifying Thermostat  %r - %s",
                answer_slugs.get("ETO_QUALIFYING_THERMOSTAT"),
                home_status,
            )
            calculator_variables["qualifying_thermostat"] = ans.answer

        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P5"))
            calculator_variables["qty_shower_head_1p5"] = ans.answer
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO 1.5 Showerheads %r", answer_slugs.get("ETO_SHOWER_HEAD_1P5")
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P5")).last()
            answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P5")).exclude(
                id=ans.id
            ).delete()
            log.warning(
                "Multiple answers for ETO 1.5 Showerheads  %r - %s",
                answer_slugs.get("ETO_SHOWER_HEAD_1P5"),
                home_status,
            )
            calculator_variables["qty_shower_head_1p5"] = ans.answer

        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P6"))
            calculator_variables["qty_shower_head_1p6"] = ans.answer
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO 1.6 Showerheads %r", answer_slugs.get("ETO_SHOWER_HEAD_1P6")
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P6")).last()
            answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P6")).exclude(
                id=ans.id
            ).delete()
            log.warning(
                "Multiple answers for ETO 1.6 Showerheads  %r - %s",
                answer_slugs.get("ETO_SHOWER_HEAD_1P6"),
                home_status,
            )
            calculator_variables["qty_shower_head_1p6"] = ans.answer

        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P75"))
            calculator_variables["qty_shower_head_1p75"] = ans.answer
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO 1.75 Showerheads %r", answer_slugs.get("ETO_SHOWER_HEAD_1P75")
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P75")).last()
            answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_HEAD_1P75")).exclude(
                id=ans.id
            ).delete()
            log.warning(
                "Multiple answers for ETO 1.75 Showerheads  %r - %s",
                answer_slugs.get("ETO_SHOWER_HEAD_1P75"),
                home_status,
            )
            calculator_variables["qty_shower_head_1p75"] = ans.answer

        try:
            ans = answers.get(question__slug=answer_slugs.get("ETO_SHOWER_WAND_1P5"))
            calculator_variables["qty_shower_wand_1p5"] = ans.answer
        except Answer.DoesNotExist:
            log.debug(
                "No answer for ETO 1.5 Shower wands %r", answer_slugs.get("ETO_SHOWER_WAND_1P5")
            )
        except Answer.MultipleObjectsReturned:
            ans = answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_WAND_1P5")).last()
            answers.filter(question__slug=answer_slugs.get("ETO_SHOWER_WAND_1P5")).exclude(
                id=ans.id
            ).delete()
            log.warning(
                "Multiple answers for ETO 1.5 Shower wands  %r - %s",
                answer_slugs.get("ETO_SHOWER_WAND_1P5"),
                home_status,
            )
            calculator_variables["qty_shower_wand_1p5"] = ans.answer

    return calculator_variables


def get_eto_calculation_collection_request_data(home_status):
    measure_variables = {
        "primary-heating-equipment-type": "heat_type",  # Coverts all prior measure aliases via get_input_values()
        "smart-thermostat-brand": "qualifying_thermostat",
        "ets-annual-etsa-kwh": "generated_solar_pv_kwh",
        "non-ets-annual-pv-watts": "generated_solar_pv_kwh",
    }

    calculator_variables = {
        "site_address": "{addr} {city}, {state} {zip}".format(
            **{
                "addr": home_status.home.get_addr(),
                "city": home_status.home.city,
                "state": home_status.home.state,
                "zip": home_status.home.zipcode,
            }
        ),
        "company": home_status.company,
    }

    calculator_variables["program"] = home_status.eep_program.id
    calculator_variables["us_state"] = home_status.home.state

    electric_utility = home_status.get_electric_company()
    if electric_utility:
        calculator_variables["electric_utility"] = electric_utility.id

    gas_utility = home_status.get_gas_company()
    if gas_utility:
        calculator_variables["gas_utility"] = gas_utility.id

    builder = home_status.home.get_builder()
    if builder:
        calculator_variables["builder"] = builder.id

    if home_status.floorplan:
        if home_status.floorplan.simulation:
            calculator_variables["simulation"] = home_status.floorplan.simulation.id
        elif home_status.floorplan.remrate_target:
            calculator_variables["rem_simulation"] = home_status.floorplan.remrate_target.id
        elif (
            home_status.floorplan.ekotrope_houseplan
            and home_status.floorplan.ekotrope_houseplan.project
        ):
            calculator_variables[
                "eko_simulation"
            ] = home_status.floorplan.ekotrope_houseplan.project.id

    input_values = home_status.get_input_values(user_role="rater")

    heat_type = input_values.get("primary-heating-equipment-type")
    calculator_variables["primary_heating_equipment_type"] = heat_type

    # calc_key = measure_variables.get('primary-heating-equipment-type')
    # calculator_variables[calc_key] = slugify(heat_type)

    if home_status.eep_program.slug not in ETO_GEN2:
        try:
            calculator_variables["hot_water_ef"] = float(input_values.get("eto-water_heater_ef"))
        except TypeError:
            calculator_variables["hot_water_ef"] = None
        calculator_variables["hot_water_type"] = input_values.get("eto-water_heater_heat_type")

        pathway = CHECKLIST_PATHWAY_ANSWERS.get(input_values.get("eto-eto_pathway"))
        if pathway:
            calculator_variables["pathway"] = pathway
    else:
        smart_thermo = input_values.get("smart-thermostat-brand")
        calculator_variables["smart_thermostat_brand"] = smart_thermo

        # calc_key = measure_variables.get('smart-thermostat-brand')
        # calculator_variables[calc_key] = 'no qualifying smart thermostat'
        #
        # if heat_type and smart_thermo and smart_thermo.lower() not in ['n/a', 'other, add comment']:
        #     heat_type_lower = heat_type.lower()
        #     if 'gas' in heat_type_lower:
        #         calculator_variables[calc_key] = 'yes-ducted gas furnace'
        #     elif 'electric' in heat_type_lower:
        #         calculator_variables[calc_key] = 'yes-ducted air source heat pump'
        if home_status.eep_program.slug in ["eto-2017", "eto-2018"]:
            calculator_variables["qty_shower_head_1p5"] = input_values.get("showerheads15-quantity")
            calculator_variables["qty_shower_head_1p6"] = input_values.get("showerheads16-quantity")
            calculator_variables["qty_shower_head_1p75"] = input_values.get(
                "showerheads175-quantity"
            )
            calculator_variables["qty_shower_wand_1p5"] = input_values.get("showerwands15-quantity")
        if home_status.eep_program.slug not in ["eto-2017", "eto-2018", "eto-2019"]:
            calculator_variables["has_gas_fireplace"] = input_values.get("has-gas-fireplace")
            calculator_variables["grid_harmonization_elements"] = input_values.get(
                "grid-harmonization-elements"
            )
            calculator_variables["smart_thermostat_brand"] = input_values.get(
                "smart-thermostat-brand"
            )
            calculator_variables["eps_additional_incentives"] = input_values.get(
                "eto-additional-incentives"
            )
            calculator_variables["solar_elements"] = input_values.get("solar-elements")

    pv_kwh_pri = input_values.get("ets-annual-etsa-kwh")
    pv_kwh_alt = input_values.get("non-ets-annual-pv-watts")

    pv_kwh = list(set(filter(None, (pv_kwh_pri, pv_kwh_alt))))
    if len(pv_kwh) > 1:
        log.error(
            "Mulitple PV KWH Values %r found for home status %d using first", pv_kwh, home_status.pk
        )

    calc_key = measure_variables.get("ets-annual-etsa-kwh")
    calculator_variables[calc_key] = pv_kwh[0] if len(pv_kwh) else None
    return calculator_variables


def get_eto_calculation_data(home_status):
    if home_status.eep_program.collection_request:
        return get_eto_calculation_collection_request_data(home_status)
    return get_legacy_eto_calculation_data(home_status)


def get_eto_calculation_completed_form(home_status, use_legacy_simulation=None):
    """Returns an instance of customer_eto.forms.EPSCalculatorForm ready for validation"""
    from axis.customer_eto.forms import EPSCalculatorForm

    variables = get_eto_calculation_data(home_status)
    if use_legacy_simulation is not None:
        variables["use_legacy_simulation"] = use_legacy_simulation
    form = EPSCalculatorForm(variables)
    return form
