"""utils.py: Django customer_eto"""


import datetime
import logging
from collections import OrderedDict

from django.apps import apps
from django.utils.timezone import now

from axis.filehandling.utils import populate_template_pdf, get_physical_file

from . import strings

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")

ETO_REGIONS = OrderedDict(
    (
        (1, "North Coast - 1"),
        (2, "South Coast - 2"),
        (3, "Portland Metro - 3"),
        (4, "Mid-Willamette - 4"),
        (5, "Southern Willamette - 5"),
        (6, "Southern - 6"),
        (7, "Columbia Basin - 7"),
        (8, "Central - 8"),
        (9, "Klamath Basin - 9"),
        (10, "Northeast - 10"),
        (11, "Eastern - 11"),
        (12, "Southwest Washington - 12"),
    )
)

ETO_ZIPCODE_REGION_MAP = {
    "97001": 7,
    "97002": 4,
    "97003": 3,
    "97004": 3,
    "97005": 3,
    "97006": 3,
    "97007": 3,
    "97008": 3,
    "97009": 3,
    "97010": 3,
    "97011": 3,
    "97013": 3,
    "97014": 7,
    "97015": 3,
    "97016": 3,
    "97017": 3,
    "97018": 3,
    "97019": 3,
    "97020": 4,
    "97021": 7,
    "97022": 3,
    "97023": 3,
    "97024": 3,
    "97026": 4,
    "97027": 3,
    "97028": 3,
    "97029": 7,
    "97030": 3,
    "97031": 7,
    "97032": 4,
    "97033": 7,
    "97034": 3,
    "97035": 3,
    "97036": 3,
    "97037": 7,
    "97038": 3,
    "97039": 7,
    "97040": 7,
    "97041": 7,
    "97042": 3,
    "97044": 7,
    "97045": 3,
    "97048": 3,
    "97049": 3,
    "97050": 7,
    "97051": 3,
    "97053": 3,
    "97054": 3,
    "97055": 3,
    "97056": 3,
    "97057": 7,
    "97058": 7,
    "97060": 3,
    "97062": 3,
    "97063": 7,
    "97064": 3,
    "97065": 7,
    "97067": 3,
    "97068": 3,
    "97070": 3,
    "97071": 4,
    "97075": 3,
    "97076": 3,
    "97077": 3,
    "97078": 3,
    "97080": 3,
    "97086": 3,
    "97089": 3,
    "97101": 3,
    "97102": 1,
    "97103": 1,
    "97106": 3,
    "97107": 1,
    "97108": 1,
    "97109": 3,
    "97110": 1,
    "97111": 3,
    "97112": 1,
    "97113": 3,
    "97114": 3,
    "97115": 3,
    "97116": 3,
    "97117": 3,
    "97118": 1,
    "97119": 3,
    "97121": 1,
    "97122": 1,
    "97123": 3,
    "97124": 3,
    "97125": 3,
    "97127": 3,
    "97128": 3,
    "97130": 1,
    "97131": 1,
    "97132": 3,
    "97133": 3,
    "97134": 1,
    "97135": 1,
    "97136": 1,
    "97137": 4,
    "97138": 1,
    "97140": 3,
    "97141": 1,
    "97143": 1,
    "97144": 3,
    "97145": 1,
    "97146": 1,
    "97147": 1,
    "97148": 3,
    "97149": 1,
    "97201": 3,
    "97202": 3,
    "97203": 3,
    "97204": 3,
    "97205": 3,
    "97206": 3,
    "97207": 3,
    "97208": 3,
    "97209": 3,
    "97210": 3,
    "97211": 3,
    "97212": 3,
    "97213": 3,
    "97214": 3,
    "97215": 3,
    "97216": 3,
    "97217": 3,
    "97218": 3,
    "97219": 3,
    "97220": 3,
    "97221": 3,
    "97222": 3,
    "97223": 3,
    "97224": 3,
    "97225": 3,
    "97227": 3,
    "97228": 3,
    "97229": 3,
    "97230": 3,
    "97231": 3,
    "97232": 3,
    "97233": 3,
    "97236": 3,
    "97238": 3,
    "97239": 3,
    "97240": 3,
    "97242": 3,
    "97251": 3,
    "97253": 3,
    "97254": 3,
    "97255": 3,
    "97256": 3,
    "97258": 3,
    "97259": 3,
    "97266": 3,
    "97267": 3,
    "97268": 3,
    "97269": 3,
    "97271": 3,
    "97272": 3,
    "97280": 3,
    "97281": 3,
    "97282": 3,
    "97283": 3,
    "97286": 3,
    "97290": 3,
    "97291": 3,
    "97292": 3,
    "97293": 3,
    "97294": 3,
    "97296": 3,
    "97298": 3,
    "97299": 3,
    "97301": 4,
    "97302": 4,
    "97303": 4,
    "97304": 4,
    "97305": 4,
    "97306": 4,
    "97307": 4,
    "97308": 4,
    "97309": 4,
    "97310": 4,
    "97311": 4,
    "97312": 4,
    "97313": 4,
    "97314": 4,
    "97317": 4,
    "97321": 5,
    "97322": 5,
    "97324": 5,
    "97325": 4,
    "97326": 5,
    "97327": 5,
    "97329": 5,
    "97330": 5,
    "97331": 5,
    "97333": 5,
    "97335": 5,
    "97336": 5,
    "97338": 4,
    "97339": 5,
    "97341": 1,
    "97342": 4,
    "97343": 1,
    "97344": 4,
    "97345": 5,
    "97346": 4,
    "97347": 4,
    "97348": 5,
    "97350": 4,
    "97351": 4,
    "97352": 4,
    "97355": 5,
    "97357": 1,
    "97358": 4,
    "97359": 4,
    "97360": 5,
    "97361": 4,
    "97362": 4,
    "97364": 1,
    "97365": 1,
    "97366": 1,
    "97367": 1,
    "97368": 1,
    "97369": 1,
    "97370": 5,
    "97371": 4,
    "97372": 4,
    "97373": 4,
    "97374": 5,
    "97375": 4,
    "97376": 1,
    "97377": 5,
    "97378": 3,
    "97380": 1,
    "97381": 4,
    "97383": 4,
    "97384": 4,
    "97385": 4,
    "97386": 5,
    "97388": 1,
    "97389": 5,
    "97390": 1,
    "97391": 1,
    "97392": 4,
    "97394": 1,
    "97396": 3,
    "97401": 5,
    "97402": 5,
    "97403": 5,
    "97404": 5,
    "97405": 5,
    "97406": 2,
    "97407": 2,
    "97408": 5,
    "97409": 5,
    "97410": 6,
    "97411": 2,
    "97412": 5,
    "97413": 5,
    "97414": 2,
    "97415": 2,
    "97416": 6,
    "97417": 6,
    "97419": 5,
    "97420": 2,
    "97423": 2,
    "97424": 5,
    "97425": 9,
    "97426": 5,
    "97427": 5,
    "97428": 6,
    "97429": 6,
    "97430": 5,
    "97431": 5,
    "97432": 6,
    "97434": 5,
    "97435": 6,
    "97436": 6,
    "97437": 5,
    "97438": 5,
    "97439": 5,
    "97440": 5,
    "97441": 6,
    "97442": 6,
    "97443": 6,
    "97444": 2,
    "97446": 5,
    "97447": 6,
    "97448": 5,
    "97449": 2,
    "97450": 2,
    "97451": 5,
    "97452": 5,
    "97453": 5,
    "97455": 5,
    "97456": 5,
    "97457": 6,
    "97458": 2,
    "97459": 2,
    "97461": 5,
    "97462": 6,
    "97463": 5,
    "97464": 2,
    "97465": 2,
    "97466": 2,
    "97467": 6,
    "97469": 6,
    "97470": 6,
    "97471": 6,
    "97472": 5,
    "97473": 6,
    "97476": 2,
    "97477": 5,
    "97478": 5,
    "97479": 6,
    "97480": 5,
    "97481": 6,
    "97482": 5,
    "97484": 6,
    "97486": 6,
    "97487": 5,
    "97488": 5,
    "97489": 5,
    "97490": 5,
    "97491": 2,
    "97492": 5,
    "97493": 5,
    "97494": 6,
    "97495": 6,
    "97496": 6,
    "97497": 6,
    "97498": 1,
    "97499": 6,
    "97501": 6,
    "97502": 6,
    "97503": 6,
    "97504": 6,
    "97520": 6,
    "97522": 6,
    "97523": 6,
    "97524": 6,
    "97525": 6,
    "97526": 6,
    "97527": 6,
    "97528": 6,
    "97530": 6,
    "97531": 6,
    "97532": 6,
    "97533": 6,
    "97534": 6,
    "97535": 6,
    "97536": 6,
    "97537": 6,
    "97538": 6,
    "97539": 6,
    "97540": 6,
    "97541": 6,
    "97543": 6,
    "97544": 6,
    "97601": 9,
    "97602": 9,
    "97603": 9,
    "97604": 9,
    "97620": 9,
    "97621": 9,
    "97622": 9,
    "97623": 9,
    "97624": 9,
    "97625": 9,
    "97626": 9,
    "97627": 9,
    "97630": 9,
    "97632": 9,
    "97633": 9,
    "97634": 9,
    "97635": 9,
    "97636": 9,
    "97637": 9,
    "97638": 9,
    "97639": 9,
    "97640": 9,
    "97641": 9,
    "97701": 8,
    "97702": 8,
    "97707": 8,
    "97708": 8,
    "97709": 8,
    "97711": 8,
    "97712": 8,
    "97730": 8,
    "97731": 9,
    "97733": 9,
    "97734": 8,
    "97735": 9,
    "97737": 9,
    "97739": 8,
    "97741": 8,
    "97750": 8,
    "97751": 8,
    "97752": 8,
    "97753": 8,
    "97754": 8,
    "97756": 8,
    "97759": 8,
    "97760": 8,
    "97761": 8,
    "97801": 10,
    "97810": 10,
    "97812": 7,
    "97813": 10,
    "97814": 11,
    "97817": 11,
    "97818": 10,
    "97819": 11,
    "97820": 11,
    "97823": 7,
    "97824": 10,
    "97825": 11,
    "97826": 10,
    "97827": 10,
    "97828": 10,
    "97830": 8,
    "97831": 11,
    "97833": 11,
    "97834": 11,
    "97835": 10,
    "97836": 10,
    "97837": 11,
    "97838": 10,
    "97839": 10,
    "97840": 11,
    "97841": 10,
    "97842": 10,
    "97843": 10,
    "97844": 10,
    "97845": 11,
    "97846": 10,
    "97848": 11,
    "97850": 10,
    "97856": 11,
    "97857": 10,
    "97859": 10,
    "97861": 7,
    "97862": 10,
    "97864": 11,
    "97865": 11,
    "97867": 10,
    "97868": 10,
    "97869": 11,
    "97870": 11,
    "97873": 11,
    "97874": 8,
    "97875": 10,
    "97876": 10,
    "97877": 11,
    "97880": 10,
    "97882": 10,
    "97883": 10,
    "97884": 11,
    "97885": 10,
    "97886": 10,
    "97903": 11,
    "97905": 11,
    "97906": 11,
    "97907": 11,
    "97908": 11,
    "97909": 11,
    "97911": 11,
    "97913": 11,
    "97914": 11,
    "97918": 11,
    "97920": 11,
    "98604": 12,
    "98606": 12,
    "98607": 12,
    "98610": 12,
    "98629": 12,
    "98639": 12,
    "98642": 12,
    "98660": 12,
    "98661": 12,
    "98662": 12,
    "98663": 12,
    "98664": 12,
    "98665": 12,
    "98671": 12,
    "98672": 12,
    "98674": 12,
    "98675": 12,
    "98682": 12,
    "98683": 12,
    "98684": 12,
    "98685": 12,
    "98686": 12,
    "97703": 8,
}

_log = logging.getLogger(__name__)


def update_fasttracksubmissions(instance, validated_data, all_objects, company):
    """
    Confirms existence of all Axis-related data points on a home whose incentive details are
    updated by the FastTrack people via our API.
    """
    from axis.incentive_payment.models import IncentivePaymentStatus, IncentiveDistribution
    from .models import ETOAccount

    project_id = instance.project_id

    # Look up the designated customer so that we can find the IncentiveDistribution with the
    # matching check number.
    try:
        eto_account = ETOAccount.objects.get(account_number=validated_data["account_number"])
    except ETOAccount.DoesNotExist:
        raise ETOAccount.DoesNotExist(
            "The provided account number does not correspond to a company in Axis."
        )
    except ETOAccount.MultipleObjectsReturned:
        # Outlandish scenario where we have duplicate companies in the system that should be
        # consolidated, and share the same ETOAccount number
        ids = ETOAccount.objects.filter(
            account_number=validated_data["account_number"]
        ).values_list("company_id", flat=True)
        raise ETOAccount.DoesNotExist(
            "The provided account number is assigned to duplicate company entries "
            "in Axis.  Please contact an administrator to have these companies "
            "consolidated to remove the abiguity: %s" % (", ".join(list(map(str, ids))))
        )
    else:
        customer = eto_account.company

    # Ensure the IncentiveDistribution exists
    check_info = {
        "status": validated_data.get("status"),
        "paid_date": validated_data.get("paid_date"),
        "check_number": validated_data.get("check_number", "eto_project_%s" % project_id),
    }

    try:
        request_date = IncentivePaymentStatus.objects.get(
            home_status=instance.home_status, owner=customer
        ).created_on
    except IncentivePaymentStatus.DoesNotExist:
        request_date = list(instance.history.filter(id=instance.id))[-1].history_date

    check_info["check_requested"] = True
    check_info["check_requested_date"] = request_date
    check_info["check_to_name"] = customer.name
    check_info["is_paid"] = True

    choices = dict(map(reversed, IncentiveDistribution._meta.get_field("status").choices))
    check_info["status"] = choices.get(check_info["status"])

    check_info["total"] = instance.rater_incentive
    if customer.company_type == "builder":
        check_info["total"] = instance.builder_incentive

    distribution, created = IncentiveDistribution.objects.get_or_create(
        company=company,
        customer=customer,
        check_number=check_info["check_number"],
        defaults=check_info,
    )

    # Make sure distribution details are current
    for k, v in check_info.items():
        setattr(distribution, k, v)
    distribution.save()

    # Ensure the IPPItem(s) exist for each Submission
    for idx, obj in enumerate(all_objects):
        home_status = instance.home_status
        cost = check_info["total"] if not idx else "0.00"
        ipp_info = {"cost": cost}
        home_status.ippitem_set.get_or_create(
            incentive_distribution=distribution, defaults=ipp_info
        )

    if not created:
        distribution.total = distribution.total_cost()
        distribution.save()


def get_remdata_compare_fields(home_status):
    is_eto_2016_program = home_status.eep_program.slug == "eto-2016"

    answers = home_status.get_input_values()

    def get_answer(slug, attempt_2016_lookup=True):
        if not attempt_2016_lookup:
            return answers.get(slug)

        if is_eto_2016_program:
            try:
                return answers["{}-2016".format(slug)]
            except KeyError:
                pass

        return answers.get(slug)

    data = OrderedDict(
        [
            ("volume", (get_answer("eto-home_volume"), "Volume")),
            ("number_bedrooms", (get_answer("eto-num_bedrooms"), "Number of bedrooms")),
            ("window_u_value", (get_answer("eto-window_u_value"), "Window U-Value")),
            ("window_shgc_value", (get_answer("eto-window_shgc_value"), "Window SHGC")),
            ("skylights_u_value", (get_answer("eto-skylights_u_value"), "Skylight U-Value")),
            ("skylights_shgc_value", (get_answer("eto-skylights_shgc_value"), "Skylight SHGC")),
            ("lighting_pct", (get_answer("eto-lighting_pct", False), "% CFL")),
            (
                "lighting_pct_2016",
                (get_answer("eto-lighting_pct-2016", False), "% High Eff Lighting"),
            ),
            ("dishwasher_efficiency_factor", (get_answer("eto-dishwasher_ef"), "Dishwasher EF")),
            (
                "air_conditioner_units",
                (1, 'A/C Units must be "SEER"', "REM"),
            ),  # Fake check to be used later
            ("air_conditioner_seer", (get_answer("eto-air_conditioner_seer"), "A/C SEER")),
            ("primary_heat_afue", (get_answer("eto-primary_heat_afue"), "Primary Heat AFUE")),
            ("primary_heat_hspf", (get_answer("eto-primary_heat_hspf"), "Primary Heat HSPF")),
            ("primary_heat_cop", (get_answer("eto-primary_heat_cop"), "Primary Heat COP")),
            (
                "primary_heat_location",
                (get_answer("eto-primary_heat_location-2016"), "Primary Heat Location"),
            ),
            ("water_heater_gallons", (get_answer("eto-water_heater_gallons"), "Water Heater Size")),
            ("water_heater_ef", (get_answer("eto-water_heater_ef"), "Water Heater EF")),
            (
                "water_heater_location",
                (get_answer("eto-water_heater_location-2016"), "Water Heater Location"),
            ),
            (
                "duct_leakage_units",
                ("CFM @ 50 Pascals", 'Duct Leakage Units must be set to "CFM @ 50 Pascals"', "REM"),
            ),  # Fake check to be used later
            (
                "duct_leakage_total_cfm50",
                (get_answer("eto-duct_leakage_cfm50"), "Total Duct Leakage"),
            ),
            (
                "whole_house_infiltration_verification_type",
                (
                    "Tested",
                    'Whole House Infiltration Code Verification must be set to "Tested"',
                    "REM",
                ),
            ),  # Fake check to be used later
            (
                "whole_house_infiltration_testing_type",
                (
                    "Blower door test",
                    'Whole House Infiltration test must be a "Blower door test"',
                    "REM",
                ),
            ),  # Fake check to be used later
            (
                "whole_house_infiltration_leakage_unit",
                (
                    "ACH @ 50 Pascals",
                    'Whole House Infiltration units must be set to "ACH @ 50 Pascals"',
                    "REM",
                ),
            ),  # Fake check to be used later
            (
                "whole_house_infiltration_heating_cooling_match",
                ("--", "Whole House Infiltration heating/cooling values match", "REM"),
            ),  # Fake check to be used later
            (
                "whole_house_infiltration_heating_cooling_match",
                ("--", "Whole House Infiltration heating/cooling values match", "REM"),
            ),  # Fake check to be used later
            (
                "whole_house_infiltratione_total_ach50",
                (get_answer("eto-duct_leakage_ach50"), "Whole House Infiltration ACH"),
            ),
            ("ventilation_type", (get_answer("eto-ventilation_type"), "Ventilation Type")),
        ]
    )
    if home_status.eep_program.slug == "eto-2016":
        data = OrderedDict(
            [
                (
                    x if x != "dishwasher_efficiency_factor" else "dishwasher_kwh",
                    y
                    if x != "dishwasher_efficiency_factor"
                    else (get_answer("eto-dishwasher_ef"), "Dishwasher KWH"),
                )
                for x, y in data.items()
            ]
        )
    result = OrderedDict()
    for k, fields in data.items():
        if fields[0]:
            result[k] = fields
    return result


def get_eto_remdata_compare_fields(home_status):
    # DEPRECATION WARNING - Moved to validations
    data = OrderedDict(
        [
            ("mechanical_vent_type_error", (False, "Mechanical ventilation may not be Air Cycler")),
            (
                "mechanical_system_exists_error",
                (False, "Mechanical ventilation system should exist"),
            ),
            (
                "mechanical_ventilation_rate_error",
                (False, "Mechanical ventilation must meet ASHRAE 62.2 2010"),
            ),
            (
                "mechanical_ventilation_hours_per_day",
                (False, "Mechanical ventilation rate must be 24hr/day"),
            ),
            (
                "allowed_housing_type",
                (
                    (1, 2, 3, 7),
                    "Single family detached, duplex single unit, townhouse, end unit, or townhouse, "
                    "inside unit allowed",
                ),
            ),
            (
                "allowed_foundation_type",
                ((1, 2, 3, 4, 5, 6, 7), "Conditioned Crawlspaces is not allowed"),
            ),
            (
                "enclosed_thermal_boundary",
                ((0, 1, 2), "Thermal boundary cannot be REM Default for Enclosed Crawlspaces"),
            ),
            (
                "more_than_one_thermal_boundary",
                ((1, 2), "Thermal boundary cannot be REM Default or N/A for more than one type"),
            ),
            ("refrigerator_conditioned_area", (1, "REM refrigerator location must be conditioned")),
            (
                "clothes_dryer_conditioned_area",
                (1, "REM clothes dryer location must be conditioned"),
            ),
        ]
    )

    from axis.customer_eto.calculator.eps.constants.eto_2020 import (
        ETO_2020_FUEL_RATES,
        ETO_2020_FUEL_RATES_WA_OVERRIDE,
    )

    fuel_rates = dict(ETO_2020_FUEL_RATES)
    if home_status.home.state == "WA":
        fuel_rates.update(dict(ETO_2020_FUEL_RATES_WA_OVERRIDE))

    if home_status.eep_program.slug == "eto-2019":
        from axis.customer_eto.calculator.eps import (
            ETO_2019_FUEL_RATES,
            ETO_2019_FUEL_RATES_WA_OVERRIDE,
        )

        fuel_rates = dict(ETO_2019_FUEL_RATES)
        if home_status.home.state == "WA":
            fuel_rates.update(dict(ETO_2019_FUEL_RATES_WA_OVERRIDE))

    gas_company = home_status.get_gas_company()
    if gas_company and fuel_rates.get(gas_company.slug):
        data["verify_gas_utility_name_error"] = (
            fuel_rates.get(gas_company.slug),
            "AXIS gas utility must match EPS REM library utility",
        )

    electric_company = home_status.get_electric_company()
    if electric_company and fuel_rates.get(electric_company.slug):
        data["verify_electric_utility_name_error"] = (
            fuel_rates.get(electric_company.slug),
            "AXIS electric utility must match EPS REM library utility",
        )

    if not home_status.collection_request:
        log.warning(
            "No collection request for %s home_status: %s"
            % (home_status.eep_program.slug, home_status.id)
        )
        return data

    return data


def get_eto_region_name_for_zipcode(zipcode):
    return ETO_REGIONS.get(ETO_ZIPCODE_REGION_MAP.get(zipcode))


def get_zipcodes_for_eto_region_id(eto_region):
    # Returns only the keys from ETO_ZIPCODE_REGION_MAP whose region is our target region
    return list(filter((lambda k: ETO_ZIPCODE_REGION_MAP[k] == eto_region), ETO_ZIPCODE_REGION_MAP))


def populate_building_permit_template(home, user):
    """Create a pdf for signing."""

    from .models import PermitAndOccupancySettings

    community_slug = home.subdivision.community.slug
    date_string = now().date().strftime("%x")  # locale date format

    # Get inherited or specified compliance choice
    settings_obj = PermitAndOccupancySettings.objects.get_for_object(home, user=user)
    compliance_code = getattr(
        settings_obj, app.CITY_OF_HILLSBORO_COMMUNITY_SETTINGS_FIELDS[community_slug]
    )
    compliance_long_option_text = strings.COMPLIANCE_LONGFORM_CHOICES[compliance_code]
    compliance_short_option_text = strings.COMPLIANCE_SHORTFORM_CHOICES[compliance_code]

    # Users
    verifier = user.company
    verifier_faux_signer = verifier.users.filter(is_company_admin=True, is_active=True).first()
    builder = home.get_builder()

    builder_signer = settings_obj.get_building_permit_signer()
    if not builder_signer:
        log.error("No builder email for home %(pk)s found for DocuSign Permit", {"pk": home.pk})
        return None

    # Coordinates are given by {page_number: {field_name: (x, y)}}
    # where (x, y) is at the bottom left of the screen, moving right and up.
    coordinates = {
        0: {
            # Top details
            "builder": (175, 695),
            "verification_company": (175, 674),
            "address": (175, 652),
            "development": (175, 630),
            "houseplan": (175, 608),
            # Building Permit compliance option
            "compliance_short_option_text": (
                25,
                430 if community_slug == "reeds-crossing" else 545,
            ),
            # Verifier Certification
            "verifier_faux_signature": (75, 208),
            "verifier_name": (75, 185),
            "verifier_date": (225, 185),
            # Builder Certification
            "builder_name": (75, 88),
            "builder_date": (225, 88),
        },
        1: {
            "compliance_long_option_text": (60, 415),
        },
    }
    fonts = {
        "default": ("Helvetica", 11),
        "compliance_short_option_text": ("Helvetica", 8),
        "compliance_long_option_text": ("Helvetica", 11),
        "verifier_faux_signature": ("Times-BoldItalic", 12),
    }

    # Data for this pre-fill render
    context = {
        "builder": "{}".format(builder),
        "verification_company": "{}".format(verifier),
        "address": home.get_addr(include_city_state_zip=True, company=user.company),
        "development": "{}".format(home.subdivision),
        "houseplan": "",
        "compliance_short_option_text": compliance_short_option_text,
        "compliance_long_option_text": compliance_long_option_text,
        "verifier_faux_signature": verifier_faux_signer.get_full_name(),
        "verifier_name": verifier_faux_signer.get_full_name(),
        "verifier_date": date_string,
        "builder_name": builder_signer.get_full_name(),
        "builder_date": date_string,
    }
    return populate_template_pdf(
        app.CITY_OF_HILLSBORO_COMMUNITY_FORM_TEMPLATES[community_slug],
        n_pages=app.PERMIT_PAGE_COUNTS[community_slug],
        coordinates=coordinates,
        fonts=fonts,
        **context,
    )


def populate_certificate_of_occupancy_template(home, user):
    """Create a second-round pdf for signing, based on the existing building permit."""

    from .models import PermitAndOccupancySettings

    community_slug = home.subdivision.community.slug
    date_string = now().date().strftime("%x")  # locale date format

    # Get inherited or specified compliance choice
    settings_obj = PermitAndOccupancySettings.objects.get_for_object(home, user=user)
    compliance_code = getattr(
        settings_obj, app.CITY_OF_HILLSBORO_COMMUNITY_SETTINGS_FIELDS[community_slug]
    )
    compliance_option_text = strings.COMPLIANCE_SHORTFORM_CHOICES[compliance_code]

    # Users
    verifier = user.company
    verifier_faux_signer = verifier.users.filter(is_company_admin=True, is_active=True).first()

    builder_signer = settings_obj.get_building_permit_signer()
    if not builder_signer:
        log.error("No builder email for home %(pk)s found for DocuSign COO", {"pk": home.pk})
        return None

    # Coordinates are given by {page_number: {field_name: (x, y)}}
    # where (x, y) is at the bottom left of the screen, moving right and up.
    coordinates = {
        0: {
            # Building Permit compliance option
            "compliance_option": (325, 545),
            # Verifier Certification
            "verifier_faux_signature": (375, 208),
            "verifier_name": (375, 185),
            "verifier_date": (525, 185),
            # Builder Certification
            "builder_name": (375, 88),
            "builder_date": (525, 88),
        },
    }
    fonts = {
        "default": ("Helvetica", 11),
        "compliance_option": ("Helvetica", 7),
        "verifier_faux_signature": ("Times-BoldItalic", 12),
    }

    # Data for this pre-fill render
    context = {
        "compliance_option": compliance_option_text,
        "verifier_faux_signature": verifier_faux_signer.get_full_name(),
        "verifier_name": verifier_faux_signer.get_full_name(),
        "verifier_date": date_string,
        "builder_name": builder_signer.get_full_name(),
        "builder_date": date_string,
    }

    # Get prior document to use as template
    permit_customer_document = get_physical_file(settings_obj.signed_building_permit.document.name)
    return populate_template_pdf(
        permit_customer_document[0],
        n_pages=app.PERMIT_PAGE_COUNTS[community_slug],
        coordinates=coordinates,
        fonts=fonts,
        **context,
    )
