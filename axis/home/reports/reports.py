"""reports.py: Django home"""

__author__ = "Steven Klass"
__date__ = "2/23/13 6:58 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging
import string
from collections import defaultdict
from functools import partial
from io import BytesIO
from itertools import zip_longest
from typing import List

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.forms import model_to_dict
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
    Spacer,
    Table,
    TableStyle,
    Image,
)

from axis.annotation.models import Annotation
from axis.checklist.collection.collectors import ChecklistCollector
from axis.checklist.models import Answer
from axis.core.checks import register_reportlab_fonts
from axis.core.pdfgen import (
    AxisPanel,
    AxisCanvas,
    AxisParagraphTable,
    AxisImage,
    CoordinateMixin,
    AxisPath,
    AxisClipAndGradient,
)
from axis.core.pdfgen import AxisSimpleDocTemplate
from axis.customer_eto.api_v3.serializers.reports.home_project.eto_2022 import (
    HomeProjectETO2022IncentiveSerializer,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.customer_neea.utils import NEEA_BPA_SLUGS
from axis.floorplan.serializers import FloorplanSerializer
from axis.home.models import EEPProgramHomeStatus
from axis.incentive_payment.models import IncentivePaymentStatus
from axis.subdivision.models import Subdivision
from axis.home.utils import get_eps_data, flatten_inheritable_settings
from axis.customer_eto.api_v3.serializers.calculators.washington_code_credit import (
    WashingtonCodeCreditCalculatorSerializer,
)
from django_input_collection.models import get_input_model

log = logging.getLogger(__name__)
User = get_user_model()
register_reportlab_fonts()
CollectedInput = get_input_model()


class HomeEnergyStarLabel(object):
    """
    This will print out a home label for an EnergyStar New Home.
    """

    def __init__(self, *args, **kwargs):
        filename = kwargs.get("filename", open("test.pdf", "wb"))
        log.debug("Writing to %s", filename.name)
        self.canvas = Canvas(filename.name, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.initial_x_offset = 0.75 * inch
        self.initial_y_offset = 9.10 * inch
        self.line_offset = 12
        self.show_border = True

    def add_certification(self, stat, quarter, default_date=None):
        """
        1 | 2   This will print a label contents in a particular quarter.
        -----
        3 | 4
        """
        x_offset = self.initial_x_offset
        y_offset = self.initial_y_offset
        self.canvas.setFont("Helvetica", 10)
        log.debug("Base: %s, %s", x_offset / inch, y_offset / inch)
        if quarter in [2, 4]:
            x_offset += 4.25 * inch
        if quarter in [3, 4]:
            y_offset -= 5.5 * inch

        # Street Address -
        self.canvas.drawString(x_offset, y_offset, stat.home.street_line1)
        y_offset -= self.line_offset
        if stat.home.street_line2:
            self.canvas.drawString(x_offset, y_offset, stat.home.street_line2)
            y_offset -= self.line_offset
        city_state_zip = "{}, {} {}".format(stat.home.city.name, stat.home.state, stat.home.zipcode)
        self.canvas.drawString(x_offset, y_offset, city_state_zip)
        if not stat.home.street_line2:
            y_offset -= self.line_offset

        # Builder
        y_offset -= 3 * self.line_offset
        self.canvas.drawString(x_offset, y_offset, stat.home.get_builder().name)

        # Provider
        y_offset -= 3 * self.line_offset
        self.canvas.drawString(x_offset, y_offset, stat.company.name)

        # Date
        y_offset -= 3 * self.line_offset
        date_str = " "
        if default_date is not None:
            date_str = "{}".format(default_date.strftime("%B %d, %Y"))
        elif stat.certification_date:
            date_str = "{}".format(
                datetime.datetime.now(datetime.timezone.utc).strftime("%B %d, %Y")
            )
        self.canvas.drawString(x_offset, y_offset, date_str)

        # Version
        eep_rows = stat.eep_program.name.split(":")
        if len(eep_rows) > 1:
            y_offset -= 2 * self.line_offset + 3
            self.canvas.drawString(x_offset, y_offset, eep_rows[0] + ":")
            y_offset -= self.line_offset
            self.canvas.drawString(x_offset, y_offset, ":".join(eep_rows[1:]).strip())
            y_offset -= self.line_offset - 3
        else:
            y_offset -= 3 * self.line_offset
            self.canvas.drawString(x_offset, y_offset, stat.eep_program.name)
            y_offset -= self.line_offset * 1

        # Optional
        self.canvas.setFont("Helvetica-Oblique", 8)
        if stat.get_samplesethomestatus():
            y_offset -= self.line_offset * 0.9
            optional = "This home has been certified using a sampling protocol"
            self.canvas.drawString(x_offset, y_offset, optional)
            y_offset -= 1 * self.line_offset
            optional = "in accordance with Chapter 6 of the RESNET Standards."
            self.canvas.drawString(x_offset, y_offset, optional)
        else:
            y_offset -= 1 * self.line_offset
        y_offset -= 1 * self.line_offset
        optional = "Axis Home ID: {}".format(stat.home.get_id())
        self.canvas.drawString(x_offset, y_offset, optional)
        self.canvas.setFont("Helvetica", 10)

    def build(
        self,
        homes,
        quarter=None,
        repeat=False,
        default_date=datetime.datetime.now(datetime.timezone.utc),
    ):
        """
        This is what will generate the report.

        1 | 2  Quarter represents which quarter you want to print
        -----
        3 | 4

        :param homes: QuerySet of Homes
        :param quarter: Quarter you want to print in
        :param repeat: Repeat fills the page with the same home
        :param default_date: If the home isn't certified what date do you wan to print.
        """
        if not isinstance(homes, (list, QuerySet)):
            homes = [homes]
        if isinstance(homes, QuerySet):
            homes = list(homes)

        if quarter and quarter not in range(1, 4):
            raise SyntaxError("You must define the quarter between 1-4")
        if repeat and len(homes) > 1:
            raise SyntaxError("To repeat this you need one home!")
        if repeat:
            homes = [homes[0], homes[0], homes[0], homes[0]]

        initial_quarter = quarter
        for idx, home in enumerate(homes):
            quarter = initial_quarter if initial_quarter else (idx % 4) + 1
            log.debug("Working on quarter %s - %s", quarter, home)
            self.add_certification(stat=home, quarter=quarter, default_date=default_date)
            if (idx + 1) % 4 == 0:
                self.canvas.showPage()
        self.canvas.save()


class HomeCertificate(object):
    """
    This will print out a home certificate.
    """

    def __init__(self, *args, **kwargs):
        filename = kwargs.get("filename", open("test.pdf", "wb"))
        log.debug("Writing to %s", filename.name)
        self.document = SimpleDocTemplate(filename.name, pagesize=landscape(letter))
        self.styles = getSampleStyleSheet()
        self.story = []
        self.initial_x_offset = 5.5 * inch
        self.initial_y_offset = 3.0 * inch
        self.line_offset = 8
        self.show_border = True

    def add_certification(self, stat, certifier_id=None):
        """ """
        x_offset = self.initial_x_offset
        y_offset = self.initial_y_offset
        log.debug("Base: %s, %s", x_offset / inch, y_offset / inch)

        self.story.append(Spacer(0, 2.125 * inch))

        # Street Address
        address = stat.home.street_line1
        address += ", {}".format(stat.home.street_line2) if stat.home.street_line2 else ""
        address += ", {} {}, {}".format(stat.home.city.name, stat.home.state, stat.home.zipcode)
        pstyle = ParagraphStyle(
            name="pstyle",
            parent=self.styles["Normal"],
            alignment=TA_CENTER,
            fontSize=18,
            fontName="Helvetica-Bold",
        )
        self.story.append(Paragraph(address, pstyle))

        pstyle = ParagraphStyle(
            name="pstyle",
            parent=self.styles["Normal"],
            alignment=TA_CENTER,
            fontSize=14,
        )
        self.story.append(Spacer(0, 0.2 * inch))
        self.story.append(Paragraph(stat.home.get_builder().name, pstyle))

        # Verified by
        self.story.append(Spacer(0, 2.1 * inch))
        if certifier_id:
            user = User.objects.get(id=certifier_id)
        else:
            user = stat.company.get_admins()[0].user
            try:
                user = stat.get_answers_for_home().last().user
            except AttributeError:
                pass
        verf = "Verified by {} of {}".format(user.get_full_name(), user.company.name)
        self.story.append(Paragraph(verf, pstyle))

        # Site ID
        self.story.append(Spacer(0, 0.1 * inch))
        self.story.append(Paragraph("Site ID#: {}".format(stat.home.get_id()), pstyle))

    def build(self, home_stats, certifier_id):
        """
        This is what will generate the report.
        :param home_stats: QuerySet of EEPProgramHomeStatus
        """
        if not isinstance(home_stats, (list, QuerySet)):
            home_stats = [home_stats]
        if isinstance(home_stats, QuerySet):
            home_stats = list(home_stats)

        for idx, stat in enumerate(home_stats):
            self.add_certification(stat=stat, certifier_id=certifier_id)
            self.story.append(PageBreak())
        self.document.build(self.story)


class BuiltGreenCertificate(object):
    def __init__(self, *args, **kwargs):
        filename = kwargs.get("filename", open("test.pdf", "wb"))
        self.canvas = Canvas(filename.name, pagesize=landscape(letter))
        self.styles = getSampleStyleSheet()

    def get_address(self, stat):
        return "{stat.home.street_line1}, {stat.home.city}".format(stat=stat)

    def centered_string(self, height, text):
        width = 11 * inch / 2
        self.canvas.drawCentredString(width, height * inch, text)

    def add_certification(self, stat, certified_id=None):
        image = Image(
            settings.SITE_ROOT + "/axis/home/static/images/BuiltGreenCertificate.jpg",
            11 * inch,
            8.5 * inch,
        )
        image.wrapOn(self.canvas, 11, 8.5)
        image.drawOn(self.canvas, 0, 0)

        self.canvas.saveState()
        self.canvas.setFontSize(20)

        self.centered_string(4.1, "{}".format(stat.eep_program.owner))
        self.centered_string(3.4, self.get_address(stat))
        self.centered_string(2.7, "{}".format(stat.home.get_builder()))
        self.centered_string(
            2,
            "★"
            * int(stat.annotations.get(type__slug="built-green-certification-level").content[0]),
        )
        self.centered_string(1.3, datetime.datetime.now().strftime("%B %d, %Y"))

        self.canvas.restoreState()

    def build(self, home_stats, certifier_id):
        if not isinstance(home_stats, (list, QuerySet)):
            home_stats = [home_stats]
        if isinstance(home_stats, QuerySet):
            home_stats = list(home_stats)

        for idx, stat in enumerate(home_stats):
            self.add_certification(stat=stat, certified_id=certifier_id)
            self.canvas.showPage()

        self.canvas.save()


COLORS = {
    "panel_fill": Color(0.5, 0.5, 0.5),
    "panel_stroke": Color(0.5, 0.5, 0.5),
    "house_fill": Color(0.3, 0.3, 0.3),
    "house_stroke": Color(0.4, 0.4, 0.4),
    "house_marker_fill": Color(0.3, 0.3, 0.3),
    "house_marker_stroke": Color(0.3, 0.3, 0.3),
    "scale_fill": Color(0.3, 0.3, 0.3),
    "scale_stroke": Color(0.3, 0.3, 0.3),
    "companies_line_fill": Color(0.7, 0.7, 0.7),
    "companies_line_stroke": Color(0.7, 0.7, 0.7),
}

DEFAULT_HOME_INFORMATION = """
            [Site ID:,, {site_id}],
            [ ,, ],
            [Lot:,,{lot_number}],
            [Street:,,{street_line1}],
            [City:,,{city}],
            [State:,,{state}],
            [ZIP Code:,,{zipcode}],
            [ ,, ],
            [Const. Status:,, {construction_status}],
            [Current Status:,, {current_status}]
        """
# Placed after Project Start in NEEA_ENERGY_STAR_V3
# [Gas Utility Account #{gas-utility-account-number-required}:,, {gas-utility-account-number},, Electric Utility Account #{electric-utility-account-number-required}:,, {electric-utility-account-number}],
NEEA_ENERGY_STAR_V3 = [
    # [Site ID:,, {site-id},, ,, ],
    """
            [Program{bop-required}:,, {bop},, ,, ],
            [Primary Heat Source{heat-source-required}:,, {heat-source},, ,, ],
            [TCO:,, {tco-options},, ,, ]
""",
    """
            [Project Start{project-start-required}:,, {project-start},, ,, ],
            [Energy Trust of Oregon{eto-required}:,, {eto},, ,, ]
""",
    """
            [Home Type{home-type-required}:,, {home-type},, Description{residence-description-required}:,, {residence-description}],
            [Builder/Owner{builder-owner-required}:,, {builder-owner},, ,, ],
            [Reference Home ID{reference-home-site-id-required}:,, {reference-home-site-id},, ,, ]
""",
    """
            [<i>Utility Incentives</i>,, ,, ,, ],
            [Advanced Lighting Package{advanced-lighting-package-required}:,, {advanced-lighting-package},, Clothes Washer{clothes-washer-required}:,, {clothes-washer}],
            [Ducts{ducts-required}:,, {ducts},, Faucet Aerators{faucet-aerators-required}:,, {faucet-aerators}],
            [House fan(s){house-fans-required}:,, {house-fans},, HVAC{hvac-required}:,, {hvac}],
            [Light Bulbs{light-bulbs-required}:,, {light-bulbs},, Lighting Fixtures{lighting-fixtures-required}:,, {lighting-fixtures}],
            [Low-flow Showerheads{low-flow-showerheads-required}:,, {low-flow-showerheads},, Refrigerator{refrigerator-required}:,, {refrigerator}],
            [Water Heater{water-heater-required}:,, {water-heater},, Other{other-required}:,, {other}]
        """,
]
# Placed before Energy trust of Oregon in NEEA_ENERGY_STAR_V3_PERFORMANCE
# [Gas Utility Account #{gas-utility-account-number-required}:,, {gas-utility-account-number},, Electric Utility Account #{electric-utility-account-number-required}:,, {electric-utility-account-number}],
NEEA_ENERGY_STAR_V3_PERFORMANCE = [
    # [Site ID:,, {site-id},, ,, ],
    """
        [Primary Heat Source{heat-source-required}:,, {heat-source},, ,, ],
        [Project Start{project-start-required}:,, {project-start},, ,, ]
    """,
    """
        [Energy Trust of Oregon{eto-required}:,, {eto},, ,, ]
    """,
    """
        [Home Type{home-type-required}:,, {home-type},, Description{residence-description-required}:,, {residence-description}],
        [Builder/Owner{builder-owner-required}:,, {builder-owner},, ,, ],
        [Reference Home ID{reference-home-site-id-required}:,, {reference-home-site-id},, ,, ]
    """,
    """
        [Meets or Beat Ann. Fuel Usage:,, {beat-annual-fuel-usage},, ,,]
    """,
    # Were in above table, but got moved to Performance Items section to reflect Home Detail better.
    # [Heating Season Infiltration:,, {heating_season_infiltration},, Cooling Season Infiltration:,, {cooling_season_infiltration}],
    # [Conditioned Area:,, {conditioned_area},, Duct Leakage,, {duct_leakage}],
    NEEA_ENERGY_STAR_V3[-1],
]

NEEA_PRESCRIPTIVE_2015 = [
    # [Site ID:,, {site-id},, ,, ],
    """
            [Program{bop-required}:,, {bop},, ,, ],
            [Primary Heat Source{heat-source-required}:,, {heat-source},, ,, ]
""",
    """
            [Project Start{project-start-required}:,, {project-start},, ,, ]
""",
    """
            [<i>Utility Incentives</i>,, ,, ,, ],
            [HVAC Combined / Heating Only Brand{hvac-brand-required}:,, {hvac-brand},, HVAC Combined / Heating Only Model{hvac-required}:,, {hvac}],
            [HVAC Cooling-Only Brand{hvac-cooling-brand-required}:,, {hvac-cooling-brand},, HVAC Cooling-Only Model{hvac-cooling-required}:,, {hvac-cooling}],
            [Solar / PV Brand{solar-brand-required}:,, {solar-brand},, Solar / PV Model{solar-required}:,, {solar}],
            [Water Heater Brand{water-heater-brand-required}:,, {water-heater-brand},, Water Heater Model{water-heater-required}:,, {water-heater}],
            [Ventilation Brand{ventilation-brand-required}:,, {ventilation-brand},, Ventilation Model{ventilation-required}:,, {ventilation}],
            [HRV Brand{hrv-brand-required}:,, {hrv-brand},, HRV Model{hrv-required}:,, {hrv}],
            [House Fan(s) Brand{house-fans-brand-required}:,, {house-fans-brand},, House Fan(s) Model{house-fans-required}:,, {house-fans}],
            [Refrigerator Brand{refrigerator-brand-required}:,, {refrigerator-brand},, Refrigerator Model{refrigerator-required}:,, {refrigerator}],
            [Range Oven Brand{range-oven-brand-required}:,, {range-oven-brand},, Range Oven Model{range-oven-required}:,, {range-oven}],
            [Clothes Washer Brand{clothes-washer-brand-required}:,, {clothes-washer-brand},, Clothes Washer Model{clothes-washer-required}:,, {clothes-washer}],
            [Clothes Dryer Brand{clothes-dryer-brand-required}:,, {clothes-dryer-brand},, Clothes Dryer Model{clothes-dryer-required}:,, {clothes-dryer}],
            [Other Brand{other-brand-required}:,, {other-brand},, Other Model{other-required}:,, {other}]
        """,
]

NEEA_PERFORMANCE_2015 = [
    # [Site ID:,, {site-id},, ,, ],
    """
        [Primary Heat Source{heat-source-required}:,, {heat-source},, ,, ],
        [Project Start{project-start-required}:,, {project-start},, ,, ]
    """,
    """
        [Meets or Beat Ann. Fuel Usage:,, {beat-annual-fuel-usage},, ,,]
    """,
    # Were in above table, but got moved to Performance Items section to reflect Home Detail better.
    # [Heating Season Infiltration:,, {heating_season_infiltration},, Cooling Season Infiltration:,, {cooling_season_infiltration}],
    # [Conditioned Area:,, {conditioned_area},, Duct Leakage,, {duct_leakage}],
    NEEA_PRESCRIPTIVE_2015[-1],
]

NEEA_EFFICIENT_HOMES = [
    """
            [Site ID:,, {site-id},,Project Start{project-start-nr-required}:,, {project-start-nr}],
            [Primary Heat Source{heat-source-nr-required}:,, {heat-source-nr},,Project End{project-end-nr-required}:,, {project-end-nr}],
            [Pilot Specification{neea-pilot-specification-required}:,, {neea-pilot-specification},,Move-In Date{move-in-date-nr-required}:,, {move-in-date-nr}]
""",
    """
            [<i>Brand/Model Information</i>,, ,, ,, ],
            [HVAC Combined / Heating Only Brand{hvac-brand-required}:,, {hvac-brand},, HVAC Combined / Heating Only Model{hvac-required}:,, {hvac}],
            [HVAC Cooling-Only Brand{hvac-cooling-brand-required}:,, {hvac-cooling-brand},, HVAC Cooling-Only Model{hvac-cooling-required}:,, {hvac-cooling}],
            [Solar / PV Brand{solar-brand-required}:,, {solar-brand},, Solar / PV Model{solar-required}:,, {solar}],
            [Water Heater Brand{water-heater-brand-required}:,, {water-heater-brand},, Water Heater Model{water-heater-required}:,, {water-heater}],
            [Ventilation Brand{ventilation-brand-required}:,, {ventilation-brand},, Ventilation Model{ventilation-required}:,, {ventilation}],
            [HRV Brand{hrv-brand-required}:,, {hrv-brand},, HRV Model{hrv-required}:,, {hrv}],
            [House Fan(s) Brand{house-fans-brand-required}:,, {house-fans-brand},, House Fan(s) Model{house-fans-required}:,, {house-fans}],
            [Refrigerator Brand{refrigerator-brand-required}:,, {refrigerator-brand},, Refrigerator Model{refrigerator-required}:,, {refrigerator}],
            [Range Oven Brand{range-oven-brand-required}:,, {range-oven-brand},, Range Oven Model{range-oven-required}:,, {range-oven}],
            [Clothes Washer Brand{clothes-washer-brand-required}:,, {clothes-washer-brand},, Clothes Washer Model{clothes-washer-required}:,, {clothes-washer}],
            [Clothes Dryer Brand{clothes-dryer-brand-required}:,, {clothes-dryer-brand},, Clothes Dryer Model{clothes-dryer-required}:,, {clothes-dryer}],
            [Other Brand{other-brand-required}:,, {other-brand},, Other Model{other-required}:,, {other}]
""",
    """
            [ ,, ,, ,, ],
            [<i>Certifications</i>,, ,, ,, ],
            [ENERGY STAR\u00AE{certified-estar-required}:,, {certified-estar},, BuiltGreen{certified-builtgreen-required}:,, {certified-builtgreen}],
            [Energy Trust of Oregon - EPS{certified-eto-eps-required}:,, {certified-eto-eps},, Earth Advantage Certified Home{certified-earth-advantage-required}:,, {certified-earth-advantage}],
            [LEED{certified-leed-required}:,, {certified-leed},, HERS{certified-hers-required}:,, {certified-hers}],
            [PHIUS+{certified-phius-required}:,, {certified-phius},, DOE Zero Energy Ready{certified-doe-zero-ready-required}:,, {certified-doe-zero-ready}],
            [National Green Building Standard{certified-nat-gbs-required}:,, {certified-nat-gbs},, Environments for Living{certified-efl-required}:,, {certified-efl}],
            [Other Brand{certified-other-required}:,, {certified-other},, ,,]
""",
]

PERFORMANCE_ITEMS = """
        [Style:,, {rem_housing_type}],
        [# of Bedrooms:,, {rem_num_bedrooms}],
        [# of Stories:,, {rem_num_stories}],
        [Foundation Type:,, {rem_foundation_type}],
        [Conditioned Area (sqft):,, {rem_conditioned_area}],
        [Conditioned Volume (cu ft):,, {rem_conditioned_volume}],
        [Ceiling R-Values:,, Attic: {rem_ceiling_attic_r_values}  Vaulted: {rem_ceiling_vaulted_r_values}],
        [Wall R-Value:,, {rem_wall_r_value}],
        [Floor R-Value:,, {rem_floor_r_value}],
        [Window U-Values:,, {rem_windows_u_values}],
        [Infiltration:,, {rem_infiltration}],
        [Duct Leakage:,, {rem_total_duct_leakage}],
        [Duct Inside Percent:,, {rem_duct_inside_percent}],
        [Primary Heating Fuel:,, {primary_heating_fuel}],
        [Primary Heating:,, {primary_heating}],
        [Primary Cooling:,, {primary_cooling}],
        [Primary Water Heating:,, {primary_water_heating}],
        [Ventilation:,, {rem_ventilation_system}],
        [Solar P/V:,, {rem_solar_pv}]
"""

EPS_INCENTIVE_ITEMS = """
        [Builder Gas Incentive:,, {builder_gas_incentive}],
        [Builder Electric Incentive:,, {builder_electric_incentive}],
        [Total Builder Incentive:,, {total_builder_incentive}],
        [Rater Gas Incentive :,, {rater_gas_incentive }],
        [Rater Electric Incentive:,, {rater_electric_incentive}],
        [Total Rater Incentive:,, {total_rater_incentive}],
        [Savings (KWh):,, {savings_kwh}],
        [Savings (therms):,, {savings_therms}],
        [Percent Improvement (modeled vs. reference home):,, {percent_improvement}],
        [Net Zero EPS Incentive:,, {net_zero_eps_incentive}],
        [Energy Smart EPS Incentive:,, {energy_smart_homes_eps_incentive}],
        [Net Zero Solar Incentive:,, {net_zero_solar_incentive}],
        [Energy Smart Homes Solar Incentive:,, {energy_smart_homes_solar_incentive}],
        [Triple Pane Window Incentive:,, {triple_pane_window_incentive}],
        [Rigid Insulation Incentive:,, {rigid_insulation_incentive}],
        [Sealed Attic Incentive:,, {sealed_attic_incentive}]
"""

EPS_FIRE_INCENTIVE_ITEMS = """
        [Builder Gas Incentive:,, {builder_gas_incentive}],
        [Builder Electric Incentive:,, {builder_electric_incentive}],
        [Total Builder Incentive:,, {total_builder_incentive}],
        [Rater Gas Incentive :,, {rater_gas_incentive }],
        [Rater Electric Incentive:,, {rater_electric_incentive}],
        [Total Rater Incentive:,, {total_rater_incentive}],
        [Savings (KWh):,, {savings_kwh}],
        [Savings (therms):,, {savings_therms}],
        [Percent Improvement (modeled vs. reference home):,, {percent_improvement}],
        [Net Zero EPS Incentive:,, {net_zero_eps_incentive}],
        [Energy Smart EPS Incentive:,, {energy_smart_homes_eps_incentive}],
        [Net Zero Solar Incentive:,, {net_zero_solar_incentive}],
        [Energy Smart Homes Solar Incentive:,, {energy_smart_homes_solar_incentive}],
        [Triple Pane Window Incentive:,, {triple_pane_window_incentive}],
        [Rigid Insulation Incentive:,, {rigid_insulation_incentive}],
        [Sealed Attic Incentive:,, {sealed_attic_incentive}]
"""

EPS_WA_CODE_CREDITS_INCENTIVE = """
        [Total Builder Incentive:,, {total_builder_incentive}],
        [Total Verifier Incentive:,, {verifier_incentive}],
        [Total Savings(Therms):,, {total_therm_savings}],
        [Required credits:,, {required_credits_to_meet_code}],
        [Total selected credits:,, {achieved_total_credits}],
        [Eligible above code credits:,, {eligible_gas_points}],
        [Code Credit Incentive:,, {code_credit_incentive}],
        [Thermostat Incentive:,, {thermostat_incentive}],
        [Fireplace Incentive:,, {fireplace_incentive}]
"""

WCC_STATIC_INCENTIVES_BREAKDOWN = """
        [Builder Gas Incentive:,, $800.00 per 0.5 eligible above code credits],
        [Thermostat incentive:,, $125.00 if smart thermostat installed],
        [Fireplace incentive:,, $200.00 if efficient gas fireplace installed]
"""


def clean_number(value, round_to=0, none_value="-"):
    """
    Rounds a number to the provided decimal place or returns a character
    :param value:
    :param round_to:
    :return:
    """
    if value is not None:
        return format(value, ".{}f".format(round_to))
    return none_value


def rgb(r, g, b):
    """Turn an rgb code into a reportlab Color."""
    return Color(r / 256, g / 256, b / 256)


def map_range(from_range, to_range, value):
    """
    Change value given a range to a number in a new range.
    :param from_range: tuple of original range
    :param to_range: tuple of new range
    :param value: number
    """
    (a1, a2), (b1, b2) = from_range, to_range
    return b1 + ((value - a1) * (b2 - b1) / (a2 - a1))


def split_list(in_list, n):
    """Yield successive n-sized chunks from l."""
    temp = []
    for i in range(0, len(in_list), n):
        temp.append(in_list[i : i + n])
    return temp


def minimal_num(x):
    """
    Reduce float numbers that have no need for decimals.
    5        -> 5
    5.0      -> 5
    5.2      -> 5.2
    'string' -> 'string'
    True     -> True
    """
    try:
        f = float(x)
    except (ValueError, TypeError):
        return x
    else:
        if f.is_integer():
            return int(f)
        else:
            return f


class HomeDetailReport(CoordinateMixin):
    def __init__(self, *args, **kwargs):
        kwargs["filename"] = kwargs.get("filename", "/tmp/home_detail_report.pdf")  # nosec
        kwargs["leftMargin"] = kwargs.get("left_margin", kwargs.get("margins", 0.5))
        kwargs["rightMargin"] = kwargs.get("right_margin", kwargs.get("margins", 0.5))
        kwargs["topMargin"] = kwargs.get("top_margin", kwargs.get("margins", 0.5))
        kwargs["bottomMargin"] = kwargs.get("bottom_margin", kwargs.get("margins", 0.5))
        self.left_margin = kwargs["leftMargin"]
        self.right_margin = kwargs["rightMargin"]
        self.top_margin = kwargs["topMargin"]
        self.bottom_margin = kwargs["bottomMargin"]
        if self.left_margin == self.right_margin == self.top_margin == self.bottom_margin:
            self.margins = self.left_margin
        kwargs["pagesize"] = kwargs.get("pagesize", letter)
        kwargs["title"] = kwargs.get("title", "Axis Document")
        kwargs["author"] = kwargs.get("author", "Pivotal Energy Solutions")
        kwargs["subject"] = kwargs.get("subject", "Pivotal Energy Solutions Document")
        kwargs["keywords"] = kwargs.get("keywords", "Energy Efficiency")
        self.styles = self._get_styles()
        self.PAGE_ONE_CONTENT_CEILING = 1
        self.tracked_panels = {}

    # ==============================================================================================
    # HELPERS
    # ==============================================================================================

    def _add_annotation_table(
        self,
        data,
        panel,
        top_space=0.1,
        table_style=None,
        ensure_enough_space=False,
        **kwargs,
    ):
        if not data:
            return panel
        if isinstance(data, Table):
            t = data
        else:
            t = Table(data, **kwargs)
            if not table_style:
                table_style = self.annotations_table_style
            t.setStyle(table_style)

        if not self.axis_drawn or ensure_enough_space:
            panel.x, panel.y = self._get_coordinates(top_space, panel)
        width, height = t.wrapOn(self.canvas, 7.3 * inch, 10 * inch)
        if panel._height_on_page() + (height / inch) + top_space > 10.3:
            if panel.height == 0:
                try:
                    del self.panels[self.panels.index(panel)]
                except ValueError:
                    # Panel may not be in list yet.
                    pass
            self.draw_frames()
            self.draw_drawables()
            self.panels = []
            self.drawables = []
            self.canvas.showPage()
            panel = AxisPanel()
            self.panels.append(panel)

        panel_height = panel.height
        self.add_paragraph_table(t, 0.1, panel.height + top_space, width, height, panel)
        self._set_panel_height(panel, panel_height + (height / inch) + top_space)
        return panel

    def _set_panel_height(self, panel, height):
        """shortcut for setting height of a panel, pass height in inches"""
        if type(panel) is int:
            panel = self.panels[panel]

        if isinstance(panel, AxisPanel):
            if not panel.height > height:
                panel.height = height
        else:
            log.error("You must pass an integer or AxisPanel object")

    def _set_panel_width(self, panel, width):
        """shortcut for setting width of a panel, pass height in inches"""
        if type(panel) is int:
            panel = self.panels[panel]

        if isinstance(panel, AxisPanel):
            if not panel.width > width:
                panel.width = width
        else:
            log.error("You must pass an integer or AxisPanel object")

    def _set_active_floorplan_variables(self, var_dict):
        serializer = FloorplanSerializer(self.home_stat.floorplan)
        input_data = serializer.data["normalized_input_data"]

        total_duct_leakage = input_data.get("total_duct_leakage")
        total_duct_leakage = "; ".join(total_duct_leakage) if total_duct_leakage else "-"

        solar_pv = input_data.get("solar")
        solar_pv = " ".join(solar_pv) if solar_pv else "-"

        ceilings = input_data.get("ceilings") or {}

        var_dict.update(
            {
                "rem_housing_type": input_data.get("housing_type", "-"),
                "rem_conditioned_area": input_data.get("conditioned_area", "-"),
                "rem_conditioned_volume": input_data.get("conditioned_volume", "-"),
                "rem_num_bedrooms": input_data.get("num_bedrooms", "-"),
                "rem_num_stories": input_data.get("num_stories", "-"),
                "rem_infiltration": input_data.get("infiltration", "-"),
                "rem_total_duct_leakage": total_duct_leakage,
                "rem_ventilation_system": input_data.get("ventilation", "-"),
                "rem_solar_pv": solar_pv,
                "rem_foundation_type": input_data.get("foundation_type", "-"),
                "rem_ceiling_attic_r_values": ", ".join(
                    "{}".format(ceiling.get("r_value", "-"))
                    for ceiling in ceilings.get("attic") or []
                )
                or "-",
                "rem_ceiling_vaulted_r_values": ", ".join(
                    "{}".format(ceiling.get("r_value", "-"))
                    for ceiling in ceilings.get("vaulted") or []
                )
                or "-",
                "rem_wall_r_value": (input_data.get("above_grade_wall") or {}).get("r_value", "-"),
                "rem_floor_r_value": (input_data.get("floor") or {}).get("r_value", "-"),
                "rem_windows_u_values": ", ".join(
                    "{:.2f}".format(w["u_value"]) for w in input_data.get("windows", [])
                )
                or "-",
                "rem_duct_inside_percent": input_data.get("duct_inside_percent", "-"),
            }
        )

        # Default all equipment types to blank
        var_dict.update(
            {
                "primary_heating": "-",
                "primary_heating_fuel": "-",
                "primary_cooling": "-",
                "primary_water_heating": "-",
            }
        )

        if input_data["source_type"] == "ekotrope":
            var_dict["primary_heating"] = input_data["dominant_equipment"]["dominant_heating"]
            var_dict["primary_heating_fuel"] = input_data["dominant_equipment"][
                "dominant_heating"
            ].get_fuel_display()
            var_dict["primary_cooling"] = input_data["dominant_equipment"]["dominant_cooling"]
            var_dict["primary_water_heating"] = input_data["dominant_equipment"][
                "dominant_hot_water"
            ]
        else:
            if input_data["dominant_equipment"]["dominant_heating"]:
                label = "{type} {fuel} {capacity:.1f} kBtuh {efficiency:.1f} {units_pretty}"
                var_dict["primary_heating"] = label.format(
                    **input_data["dominant_equipment"]["dominant_heating"]
                )
                var_dict["primary_heating_fuel"] = input_data["dominant_equipment"][
                    "dominant_heating"
                ]["fuel"]

            if (input_data["dominant_equipment"]["dominant_cooling"] or {}).get("qty"):
                label = "{type} {fuel} {capacity:.1f} kBtuh {efficiency:.1f} {units_pretty}"
                var_dict["primary_cooling"] = label.format(
                    **input_data["dominant_equipment"]["dominant_cooling"]
                )

            if input_data["dominant_equipment"]["dominant_hot_water"]:
                label = "{type} {fuel} {tank_size} Gal EF {energy_factor:.2f}"
                var_dict["primary_water_heating"] = label.format(
                    **input_data["dominant_equipment"]["dominant_hot_water"]
                )

    def get_washington_code_credit_calculator_data(self):
        serializer = WashingtonCodeCreditCalculatorSerializer(
            data={"home_status": self.home_stat.id}
        )
        serializer.is_valid(raise_exception=True)
        raw = serializer.calculator.summary_data
        savings = serializer.calculator.savings_data

        return {
            "total_builder_incentive": f"${raw['total_builder_incentive']:,.2f}",
            "verifier_incentive": f"${raw['verifier_incentive']:,.2f}",
            "total_therm_savings": f"{savings['total_therm_savings']:.0f}",
            "required_credits_to_meet_code": raw["required_credits_to_meet_code"],
            "achieved_total_credits": raw["achieved_total_credits"],
            "eligible_gas_points": raw["eligible_gas_points"],
            "code_credit_incentive": f"${raw['code_credit_incentive']:,.2f}",
            "thermostat_incentive": f"${raw['thermostat_incentive']:,.2f}",
            "fireplace_incentive": f"${raw['fireplace_incentive']:,.2f}",
        }

    def _set_eps_incentive_variables(self, var_dict):
        ft_data = self.home_stat.fasttracksubmission
        percent_improvement = ft_data.percent_improvement
        if percent_improvement is not None:
            percent_improvement = 100 * percent_improvement
        # results = get_eps_data(self.home_stat)
        # if "errors" in results:
        #     return

        var_dict.update(
            {
                "builder_gas_incentive": "${:0,.2f}".format(ft_data.builder_gas_incentive),
                "builder_electric_incentive": "${:0,.2f}".format(
                    ft_data.builder_electric_incentive
                ),
                "total_builder_incentive": "${:0,.2f}".format(ft_data.builder_incentive),
                "total_builder_solar_incentive": "${:0,.2f}".format(
                    ft_data.solar_ready_builder_incentive
                    + ft_data.net_zero_solar_incentive
                    + ft_data.solar_storage_builder_incentive
                ),
                "rater_gas_incentive ": "${:0,.2f}".format(ft_data.rater_gas_incentive),
                "rater_electric_incentive": "${:0,.2f}".format(ft_data.rater_electric_incentive),
                "total_rater_incentive": "${:0,.2f}".format(ft_data.rater_incentive),
                "total_rater_solar_incentive": "${:0,.2f}".format(
                    ft_data.solar_ready_verifier_incentive,
                ),
                "savings_kwh": ft_data.kwh_savings,
                "savings_therms": ft_data.therm_savings,
                "percent_improvement": "{:.0f}%".format(percent_improvement),
                "net_zero_eps_incentive": "${:0,.2f}".format(ft_data.net_zero_eps_incentive),
                "energy_smart_homes_eps_incentive": "${:0,.2f}".format(
                    ft_data.energy_smart_homes_eps_incentive
                ),
                "net_zero_solar_incentive": "${:0,.2f}".format(ft_data.net_zero_solar_incentive),
                "energy_smart_homes_solar_incentive": "${:0,.2f}".format(
                    ft_data.energy_smart_homes_solar_incentive
                ),
                # Fire
                "triple_pane_window_incentive": "${:0,.2f}".format(
                    ft_data.triple_pane_window_incentive
                ),
                "rigid_insulation_incentive": "${:0,.2f}".format(
                    ft_data.rigid_insulation_incentive
                ),
                "sealed_attic_incentive": "${:0,.2f}".format(ft_data.sealed_attic_incentive),
                # WCC
                "code_credit_incentive": "${:0,.2f}".format(ft_data.code_credit_incentive),
                "thermostat_incentive": "${:0,.2f}".format(ft_data.thermostat_incentive),
                "cobid_builder_incentive": "${:0,.2f}".format(ft_data.cobid_builder_incentive),
                "cobid_verifier_incentive": "${:0,.2f}".format(ft_data.cobid_verifier_incentive),
                "solar_ready_builder_incentive": "${:0,.2f}".format(
                    ft_data.solar_ready_builder_incentive
                ),
                "solar_ready_verifier_incentive": "${:0,.2f}".format(
                    ft_data.solar_ready_verifier_incentive
                ),
                "ev_ready_builder_incentive": "${:0,.2f}".format(
                    ft_data.ev_ready_builder_incentive
                ),
                "solar_storage_builder_incentive": "${:0,.2f}".format(
                    ft_data.solar_storage_builder_incentive
                ),
                "heat_pump_water_heater_incentive": "${:0,.2f}".format(
                    ft_data.heat_pump_water_heater_incentive
                ),
            }
        )

    def _set_NEEA_performance_specific_variables(self, var_dict):
        try:
            var_dict["beat-annual-fuel-usage"] = Annotation.objects.get(
                type__slug="beat-annual-fuel-usage", object_id=self.home_stat.pk
            ).content
        except Annotation.DoesNotExist:
            var_dict["beat-annual-fuel-usage"] = "-"

    def _set_variables(self, home_stat, user):
        address_parts = home_stat.home.get_home_address_display_parts(
            **{
                "include_city_state_zip": True,
                "company": user.company,
            }
        )

        self.home_stat = EEPProgramHomeStatus.objects.get(id=home_stat.id)
        self.home = self.home_stat.home
        self.home_variables = dict(self.home.__dict__, **address_parts._asdict())
        if self.home.subdivision:
            self.home_variables["subdivision"] = "{}".format(self.home.subdivision)
        self.home_variables["site_id"] = self.home.get_id()
        construction_status = self.home.get_current_stage(user)
        self.home_variables["construction_status"] = (
            construction_status.stage if construction_status else "-"
        )
        self.home_variables["current_status"] = self.home_stat.state_description
        self.has_rem_data = False
        self.hide_hers_index = False
        if self.home_stat.floorplan and self.home_stat.floorplan.remrate_target:
            try:
                self.home_variables[
                    "hers_score"
                ] = self.home_stat.floorplan.get_hers_score_for_program(self.home_stat.eep_program)
            except AttributeError:
                pass
            else:
                self.has_rem_data = True
        if self.home_stat.eep_program.owner.slug in ["neea", "eto"]:
            self.hide_hers_index = True

        self.drawables, self.panels = [], []
        self.has_ekotrope_data = False
        if self.home_stat.floorplan and self.home_stat.floorplan.input_data_type == "ekotrope":
            self.has_ekotrope_data = True

    def _draw_image(self, path, x, y, max_width, max_height, **kwargs):
        panel = self.get_panel(kwargs.get("panel"))
        if panel:
            panel_x, panel_y = panel.x, panel.y
            if max_height > panel.height:
                self._set_panel_height(panel, max_height)
        else:
            panel_x = panel_y = 0

        image = Image(settings.SITE_ROOT + path)
        width, height = image._restrictSize(max_width * inch, max_height * inch)
        image.wrapOn(self.canvas, max_width * inch, max_height * inch)
        image.drawOn(self.canvas, self._myX(x + panel_x), self._myY(y + max_height + panel_y))

        if kwargs.get("border"):
            self.canvas.rect(x + panel_x, y + panel_y + max_height, width / inch, -height / inch)

    def _map_table_variables(self, dictionary, variables):
        """
        Takes a predefined layout in string type, inserts the variables,
        then turns it into a list structure to be used as Table data.
        """
        dictionary = dictionary.format(**variables)
        string_data = dictionary.replace("[", "").split("],")
        data = []
        for subs in string_data:
            subs = subs.replace("\u2605", "*")
            subs = subs.strip(" \t\n\r")
            subs = subs.replace("]", "")  # last line in a set will not have this removed via split
            data.append(subs.split(",,"))
        return data

    def _build_remrate_table_data(self, temp):
        data = []
        bold = self.styles["Bold"]
        normal = self.styles["Normal"]

        for key, value in temp:
            if not isinstance(key, Paragraph):
                data.extend([Paragraph(key, bold), Paragraph(str(value), normal)])
            else:
                data.extend([key, value])

        return data

    def _build_remrate_fuel_summary_table_data(self, left_table, right_table):
        bold = self.styles["Bold"]
        normal = self.styles["Normal"]
        data = []

        for one, two in zip_longest(left_table, right_table):
            key1, value1 = one if one else ("", "")
            key2, value2 = two if two else ("", "")

            data.extend(
                [
                    Paragraph(key1, bold),
                    Paragraph(value1, normal),
                    Paragraph(key2, bold),
                    Paragraph(value2, normal),
                ]
            )

        return data

    def _building_info_data_check(self):
        """Checks that all the data needed to make the building_info panel is present."""
        try:
            simulation = self.home_stat.floorplan.remrate_target
        except (AttributeError, ValueError):
            # Don't care what type of error. If it can't do this operation, we can't continue.
            return False

        if not hasattr(simulation, "building"):
            return False
        elif not hasattr(simulation.building, "building_info"):
            return False

        if not hasattr(simulation, "compliance"):
            return False

        if not hasattr(simulation, "site"):
            return False

        if self.home_stat.eep_program.owner.slug in ["neea", "eto"]:
            return False

        return True

    def _fuel_summary_data_check(self):
        try:
            simulation = self.home_stat.floorplan.remrate_target
        except (ArithmeticError, ValueError, AttributeError):
            return False

        if not hasattr(simulation, "results"):
            return False

        if self.home_stat.eep_program.owner.slug in ["neea", "eto"]:
            return False

        return True

    def _mechanical_systems_data_check(self):
        try:
            self.home_stat.floorplan.remrate_target
        except (AttributeError, ValueError):
            return False
        return True

    def _eps_incentives_data_check(self, user):
        if user.company.company_type == "rater":
            return False

        try:
            instance = self.home_stat.fasttracksubmission
        except (AttributeError, ValueError):
            return False

        if self.home_stat.eep_program.slug == "eto-2022" and self.home_stat.home.state == "OR":
            from axis.customer_eto.api_v3.serializers import EPS2022CalculatorSerializer

            serializer = EPS2022CalculatorSerializer(
                instance=instance, data={"home_status": self.home_stat.pk}
            )
            return serializer.is_valid()

        if self.home_stat.eep_program.slug == "eto-2021" or (
            self.home_stat.eep_program.slug == "eto-2022" and self.home_stat.home.state == "WA"
        ):
            from axis.customer_eto.api_v3.serializers import EPS2021CalculatorSerializer

            serializer = EPS2021CalculatorSerializer(
                instance=instance, data={"home_status": self.home_stat.pk}
            )
            return serializer.is_valid()

        if self.home_stat.eep_program.slug == "washington-code-credit":
            serializer = WashingtonCodeCreditCalculatorSerializer(
                data={"home_status": self.home_stat.id}
            )
            return serializer.is_valid(raise_exception=True)

        try:
            assert "errors" not in get_eps_data(self.home_stat)
            self.home_stat.fasttracksubmission
        except (AttributeError, ValueError, AssertionError):
            return False
        return True

    def _wcc_static_incentives_check(self, user):
        if self.home_stat.eep_program.slug == "washington-code-credit":
            return True
        return False

    def wcc_static_incentives(self, panel):
        panel = self.get_panel(panel)
        var_dict = {}

        temp = []
        temp.append(
            [Paragraph("Program builder incentives breakdown", self.styles["centered-bold"])]
        )
        style_bold = self.styles["Bold"]
        style_normal = self.styles["Normal"]

        items = WCC_STATIC_INCENTIVES_BREAKDOWN
        data = self.map_table_variables(items, var_dict)

        for key, value in data:
            key, value = key.strip(), value.strip()
            key = Paragraph(key, style_bold)
            value = Paragraph(value, style_normal)
            temp.append([key, value])

        panel = self._add_annotation_table(temp, panel, ensure_enough_space=True)

    def _standard_protocoL_calculations_check(self):
        return self.home_stat.eep_program.slug in NEEA_BPA_SLUGS

    # ==============================================================================================
    # GETTERS
    # ==============================================================================================

    def _get_styles(self):
        log.debug("Setting up styles")
        styles = getSampleStyleSheet()
        styles["Normal"].textColor = (0.3, 0.3, 0.3)
        styles["Normal"].fontName = "Arial"

        styles.add(
            ParagraphStyle(name="Bold", parent=styles["Normal"], fontName="Arial-Bold"),
            "Bold",
        )
        styles.add(
            ParagraphStyle(
                name="centered-bold",
                parent=styles["Normal"],
                alignment=1,
                fontName="Arial-Bold",
                fontSize=12,
            ),
            "centered-bold",
        )
        styles.add(
            ParagraphStyle(name="centered", parent=styles["Normal"], alignment=1),
            "centered",
        )
        styles.add(
            ParagraphStyle(
                name="centered-white-bold",
                parent=styles["centered"],
                textColor=(1, 1, 1),
                fontName="Arial-Bold",
            ),
            "centered-white-bold",
        )
        styles.add(
            ParagraphStyle(name="italic", parent=styles["Normal"], fontName="Arial-Italic"),
            "italic",
        )
        styles.add(
            ParagraphStyle(
                name="centered-italic",
                parent=styles["centered"],
                fontName="Arial-Italic",
            ),
            "centered-italic",
        )
        styles.add(
            ParagraphStyle(name="dark_background", parent=styles["Normal"], textColor=colors.white),
            "dark_background",
        )
        styles.add(
            ParagraphStyle(name="small", parent=styles["Normal"], fontSize=8, leading=9),
            "small",
        )
        styles.add(
            ParagraphStyle(
                name="small-centered",
                parent=styles["Normal"],
                fontSize=8,
                alignment=1,
                leading=8,
            ),
            "small-centered",
        )
        styles.add(
            ParagraphStyle(
                name="small-right",
                parent=styles["Normal"],
                fontSize=8,
                leading=9,
                alignment=2,
            ),
            "small-right",
        )
        styles.add(
            ParagraphStyle(
                name="small-centered-white",
                parent=styles["small-centered"],
                textColor=colors.white,
            ),
            "small-centered-white",
        )
        styles.add(
            ParagraphStyle(
                name="small-centered-white-bold",
                parent=styles["small-centered"],
                textColor=colors.white,
                fontName="Arial-Bold",
            ),
            "small-centered-white-bold",
        )
        styles.add(
            ParagraphStyle(
                name="big_price",
                parent=styles["Normal"],
                fontName="Arial-Black",
                alignment=1,
                fontSize=48,
            ),
            "big_price",
        )
        styles.add(ParagraphStyle(name="big", parent=styles["Normal"], fontSize=16), "big")
        styles.add(
            ParagraphStyle(name="tiny", parent=styles["Normal"], fontSize=7, leading=8),
            "tiny",
        )
        styles.add(
            ParagraphStyle(name="tiny-bold", parent=styles["tiny"], fontName="Arial-Bold"),
            "tiny-bold",
        )

        styles.add(
            ParagraphStyle(
                name="hers-score",
                parent=styles["Normal"],
                fontSize=30,
                leading=25,
                alignment=1,
            ),
            "hers-score",
        )

        styles.add(
            ParagraphStyle(name="heading", parent=styles["Normal"], fontSize=18, leading=24),
            "heading",
        )
        styles.add(
            ParagraphStyle(
                name="heading-centered",
                parent=styles["Normal"],
                fontSize=18,
                leading=24,
                alignment=1,
            ),
            "heading-centered",
        )
        styles.add(
            ParagraphStyle(name="subheading", parent=styles["Bold"], fontSize=10, leading=14),
            "subheading",
        )
        styles.add(
            ParagraphStyle(
                name="subheading-right",
                parent=styles["Bold"],
                fontSize=10,
                leading=14,
                alignment=2,
            ),
            "subheading-right",
        )
        styles.add(
            ParagraphStyle(name="list-item", parent=styles["Normal"], fontSize=10, leading=12),
            "list-item",
        )
        styles.add(
            ParagraphStyle(
                name="list-item-centered",
                parent=styles["Normal"],
                fontSize=10,
                leading=12,
                alignment=1,
            ),
            "list-item-centered",
        )

        self.master_table_style = TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Arial-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("LEADING", (0, 0), (-1, -1), 14),
                ("TEXTCOLOR", (0, 0), (-1, -1), (0, 0, 0)),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]
        )

        if settings.DEBUG:
            self.master_table_style = TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Arial-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                    ("LEADING", (0, 0), (-1, -1), 14),
                    ("TEXTCOLOR", (0, 0), (-1, -1), (0, 0, 0)),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    # debug features
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, (0, 0, 0, 0.2)),
                    # ('BOX', (0, 0), (-1, -1), 0.25, Color(0, 0, 0)),
                ]
            )

        # Default tablestyles
        self.table_with_header_style = TableStyle(
            [("SPAN", (0, 0), (-1, 0))], parent=self.master_table_style
        )

        self.table_no_header_style = TableStyle([], parent=self.master_table_style)

        self.remrate_fuel_summary_table_style = TableStyle(
            [
                ("SPAN", (0, 0), (1, 0)),
                ("SPAN", (2, 0), (3, 0)),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ],
            parent=self.master_table_style,
        )

        self.remrate_building_info_table_style = TableStyle(
            [("SPAN", (0, 0), (-1, 0)), ("BOTTOMPADDING", (0, 0), (-1, 0), 6)],
            parent=self.master_table_style,
        )

        self.remrate_mechanical_systems_table_style = TableStyle(
            [("BOTTOMPADDING", (0, 0), (-1, 0), 6)], parent=self.master_table_style
        )

        self.program_table_style = TableStyle(
            [
                ("SPAN", (0, 0), (-1, 0)),
                ("SPAN", (1, 1), (-1, 1)),
            ],
            parent=self.master_table_style,
        )

        self.company_table_style = TableStyle(
            [
                ("TOPPADDING", (0, 0), (-1, 0), 11),
                # ('LEFTPADDING', (0, 1), (-1, -1), 12),
                ("LINEABOVE", (0, 0), (-1, 0), 0.25, Color(0, 0, 0, alpha=0.2)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ],
            parent=self.master_table_style,
        )

        self.home_information_table_style = TableStyle(
            [
                ("SPAN", (0, 0), (-1, 0)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ],
            parent=self.master_table_style,
        )

        self.annotations_table_style = TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                # ('INNERGRID', (0, 0), (-1, -1), 0.25, Color(0, 0, 0, alpha=0.5)),
            ],
            parent=self.master_table_style,
        )

        self.checklist_table_style = TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("SPAN", (0, 1), (1, 1)),
                # ('INNERGRID', (0, 0), (-1, -1), 0.25, Color(0, 0, 0, alpha=0.5)),
                # ('LINEABOVE', (0, 0), (-1, -1), 0.25, Color(0, 0, 0, alpha=0.5)),
            ],
            parent=self.master_table_style,
        )

        self.checklist_with_header_table_style = TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("SPAN", (0, 0), (-1, 0)),
                # ('SPAN', (0, 1), (1, 1)),
                # ('INNERGRID', (0, 0), (-1, -1), 0.25, Color(0, 0, 0, alpha=0.5)),
                # ('LINEABOVE', (0, 0), (-1, -1), 0.25, Color(0, 0, 0, alpha=0.5)),
            ],
            parent=self.master_table_style,
        )

        self.styleless_table = TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.25, Color(0, 0, 0, 0)),
                ("LINEABOVE", (0, 0), (-1, -1), 0.25, Color(0, 0, 0, 0)),
            ]
        )

        return styles

    def _get_panel(self, panel):
        """
        return the user a panel object given a number.
        Checks in the panels to be drawn.
        Then checks in cached panels.
        """
        if type(panel) is int:
            try:
                panel = self.panels[panel]
            except IndexError:
                panel = AxisPanel()
                self.panels.append(panel)
        return panel

    def _get_coordinates(self, spacing, panel):
        horizontal_constraint = 8.1
        if isinstance(panel, AxisPanel):
            try:
                previous_panel = self.panels[self.panels.index(panel) - 1]
            except ValueError:
                previous_panel = AxisPanel()
        else:
            panel = self.panels[panel]
            previous_panel = self.panels[panel - 1]

        x, y = previous_panel.expected_space(spacing)

        if x + panel.width > horizontal_constraint:
            x = previous_panel.x
            if x + panel.width > horizontal_constraint or x < self.left_margin:
                x = self.left_margin
        elif panel.clear:
            _, y = previous_panel.expected_space(0.1)
            x = self.left_margin
        else:
            y = previous_panel.y

        if self.panels.index(panel) not in [0, 1] and y < 0.31:
            try:
                _, y = self.panels[self.panels.index(panel) - 2].expected_space(spacing)
            except IndexError:
                pass

        return x, y

    def _get_utility_string(self, relationship):
        types = []
        if hasattr(relationship, "utilitysettings"):
            # Read type from context
            settings = relationship.utilitysettings
            if settings.is_gas_utility:
                types.append("Gas")
            if settings.is_electric_utility:
                types.append("Electric")

        if not types:
            org = relationship.company
            if org.water_provider:
                types.append("Water")
            elif org.gas_provider:
                types.append("Gas")
            elif org.electricity_provider:
                types.append("Electric")

        if types:
            return [("- " + type) for type in types]
        return [""]

    def _get_map_image(self, lat, lon):
        """Pull the image"""
        url = (
            "http://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=15&"
            "size={width}x{height}&maptype=roadmap&markers={lat},{lon}&"
            "sensor=false&key={key}".format(
                lat=lat,
                lon=lon,
                width=int(3.3 * inch * 2),
                height=int(2.1 * inch * 2),
                key="AIzaSyBVBa5Gu8JkJGN51S5Fh5VfQT4RrY3Njx8",
            )
        )
        try:
            response = requests.get(url)
        except requests.exceptions:
            log.error("Unable to get google static image - %s", url)
            return
        else:
            im = BytesIO(response.content)
            return Image(im)

    def _get_house_path(self, x, y, text, width=1.0, height=1.0):
        half_width = width * 0.5
        base_width = width * 0.35
        base_height = height * 0.35

        p = AxisPath(strokeColor=COLORS["house_stroke"], fillColor=COLORS["house_fill"], fill=1)
        p.move(x, y)

        p.line(x - base_width, y)
        p.line(x - base_width, y - base_height)
        p.line(x - half_width, y - base_height)

        # top of roof
        p.line(x, y - height)

        map_x = partial(map_range, (0, 100), (x, x + half_width))
        map_y = partial(map_range, (0, 100), (y - height, y - base_height))

        # chimney
        p.line(map_x(40), map_y(40))
        p.line(map_x(40), y - height + 0.05)
        p.line(map_x(60), y - height + 0.05)
        p.line(map_x(60), map_y(60))

        p.line(x + half_width, y - base_height)
        p.line(x + base_width, y - base_height)
        p.line(x + base_width, y)
        p.close()

        return p

    def get_panel(self, panel):
        if panel is not None:
            panel = self._get_panel(panel)
        return panel

    # ==============================================================================================
    # ACTIONS
    # ==============================================================================================

    def add_paragraph_table(self, drawable, x, y, width, height, panel=None):
        """
        adds drawable to array to be drawn later
        :param drawable: object to be drawn
        :param x: x position in inches
        :param y: y position in inches from panel top
        :param width: width directly from wrapOn method
        :param height: height directly from wrapOn method
        :param panel: panel for y coordinate to be based off of, 0 index
        """

        panel_spacing = 0.1

        panel = self.get_panel(panel)

        if panel is not None:
            width /= inch
            height /= inch
            y += panel.padding

            if height > panel.height:
                self._set_panel_height(panel, height)
                if panel != 0 and self.panels.index(panel) != 0:
                    panel.x, panel.y = self._get_coordinates(panel_spacing, panel)
                else:
                    if not self.axis_drawn:
                        (panel.x, panel.y) = (
                            self.left_margin,
                            self.PAGE_ONE_CONTENT_CEILING,
                        )
                    else:
                        (panel.x, panel.y) = (self.left_margin, self.top_margin)
            if width > panel.width:
                self._set_panel_width(panel, width)

        self.drawables.append(AxisParagraphTable(drawable, x, y, width, height, panel))

    def map_table_variables(self, dictionary, variables):
        if not isinstance(dictionary, str):
            dictionary = str(dictionary)
        return self._map_table_variables(dictionary, variables)

    def draw_logos(self):
        if not self.axis_drawn:
            self._draw_image("/axis/home/static/images/Axis_evolve_logo1.png", 0.45, 0.3, 2.5, 0.7)
            self.axis_drawn = True
            if self.home_stat.eep_program.owner.slug == "aps":
                self.customer_logo = (
                    "/axis/core/static/images/sponsor_aps.png",
                    5.45,
                    0.325,
                    2.5,
                    0.6,
                )
            elif self.home_stat.eep_program.owner.slug == "neea":
                if self.home_stat.eep_program.slug == "neea-efficient-homes":
                    self.customer_logo = (
                        "/axis/customer_neea/static/images/neea_logo.png",
                        6.78,
                        0.325,
                        2.5,
                        0.6,
                    )
                else:
                    self.customer_logo = (
                        "/axis/home/static/images/BetterBuiltNW_logo_Master.jpg",
                        6,
                        0.325,
                        2.5,
                        0.6,
                    )
            if self.customer_logo:
                self._draw_image(*self.customer_logo)

    def draw_frames(self):
        self.draw_logos()
        self.canvas.saveState()
        self.canvas.setFillColor(COLORS["panel_fill"], alpha=0.2)
        self.canvas.setStrokeColor(COLORS["panel_stroke"], alpha=0.2)
        self.canvas.setLineWidth(0.5)
        for panel in self.panels:
            if panel.x != 0 or panel.y != 0:
                self.canvas.roundRect(
                    panel.x,
                    panel.y,
                    panel.final_width(),
                    panel.final_height(),
                    5,
                    fill=1,
                )
        self.canvas.restoreState()

    def draw_drawables(self):
        for drawable in self.drawables:
            drawable.axisDraw(self.canvas)

    def printed_by_info(self, user):
        p = Paragraph(
            "This report was generated by {user} on {date}".format(
                user=user.get_full_name(),
                date=datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%MZ"),
            ),
            self.styles["small"],
        )
        width, height = p.wrapOn(self.canvas, 7.4 * inch, 1 * inch)
        a = AxisParagraphTable(p, 0.5, letter[1] / inch - 0.4, width, height / inch)
        a.axisDraw(self.canvas)

    # ==============================================================================================
    # INFORMATION HELPERS
    # ==============================================================================================

    def _get_building_information(self, simulation):
        building_info = simulation.building.building_info
        res = simulation.results
        heading = self.styles["centered-bold"]

        temp = [
            [Paragraph("Building Information", heading), Paragraph("", heading)],
            [Paragraph("", heading), Paragraph("", heading)],
        ]

        temp.append(["Conditioned Area (sq ft)", clean_number(building_info.conditioned_area)])
        temp.append(["Conditioned Volume (cubic ft)", clean_number(building_info.volume)])
        temp.append(["Insulated Shell Area (sq ft)", clean_number(res.shell_area)])
        temp.append(["Number of Bedrooms", building_info.number_bedrooms])
        temp.append(["Number of Stories", building_info.number_stories])
        temp.append(["Housing Type", building_info.get_type_display()])
        temp.append(["Foundation Type", building_info.get_foundation_type_display()])

        return temp

    def _get_building_info_ratings(self, simulation):
        heading = self.styles["centered-bold"]
        hers = simulation.hers
        energystar = simulation.energystar

        if energystar.energy_star_v3p1_hers_score:
            return [
                [Paragraph("Ratings", heading), ""],
                ["", ""],
                ("HERS Score", clean_number(hers.score)),
                (
                    "ENERGY STAR v3.1 HERS",
                    clean_number(energystar.energy_star_v3p1_pv_score),
                ),
                (
                    "ENERGY STAR v3.1 HERS w/o PV",
                    clean_number(energystar.energy_star_v3p1_pv_score),
                ),
                (
                    "ENERGY STAR v3.1 HERS (SAF adjusted)",
                    clean_number(energystar.energy_star_v3p1_hers_saf_score),
                ),
                (
                    "ENERGY STAR v3.1 HERS Size adjustment Factor",
                    clean_number(energystar.energy_star_v3p1_hers_saf_score),
                ),
            ]
        if energystar.energy_star_v3_hers_score:
            return [
                [Paragraph("Ratings", heading), ""],
                ["", ""],
                ("HERS Score", clean_number(hers.score)),
                (
                    "ENERGY STAR v3 HERS",
                    clean_number(energystar.energy_star_v3_pv_score),
                ),
                (
                    "ENERGY STAR v3 HERS w/o PV",
                    clean_number(energystar.energy_star_v3_pv_score),
                ),
                (
                    "ENERGY STAR v3 HERS (SAF adjusted)",
                    clean_number(energystar.energy_star_v3_hers_saf_score),
                ),
                (
                    "ENERGY STAR v3 HERS Size adjustment Factor",
                    clean_number(energystar.energy_star_v3_hers_saf_score),
                ),
            ]
        if energystar.energy_star_v2p5_pv_score:
            return [
                [Paragraph("Ratings", heading), ""],
                ["", ""],
                ("HERS Score", clean_number(hers.score)),
                (
                    "ENERGY STAR v2.5 HERS",
                    clean_number(energystar.energy_star_v2p5_pv_score),
                ),
                (
                    "ENERGY STAR v2.5 HERS w/o PV",
                    clean_number(energystar.energy_star_v2p5_pv_score),
                ),
                (
                    "ENERGY STAR v2.5 HERS (SAF adjusted)",
                    clean_number(energystar.energy_star_v2p5_hers_saf_score),
                ),
                (
                    "ENERGY STAR v2.5 HERS Size adjustment Factor",
                    clean_number(energystar.energy_star_v2p5_hers_saf_score),
                ),
            ]

    def _get_building_info_site_data(self, simulation):
        site = simulation.site
        heading = self.styles["centered-bold"]

        temp = [[Paragraph("Site Data", heading), ""], ["", ""]]
        temp.append(["City Label", site.site_label])
        temp.append(["Climate Zone", site.climate_zone])
        temp.append(["Elevation", site.elevation])
        temp.append(
            [
                "Avg Heating Temp",
                clean_number(site.avg_seasonal_heating_temp, round_to=1),
            ]
        )
        temp.append(
            [
                "Avg Cooling Temp",
                clean_number(site.avg_seasonal_cooling_temp, round_to=1),
            ]
        )
        temp.append(["Avg Num Heating Days", site.num_heating_season_days])
        temp.append(
            [
                "Avg Num Cooling Days",
                clean_number(site.num_cooling_season_days, round_to=1),
            ]
        )

        return temp

    def _remrate_data_lights_and_appliances(self, panel):
        panel = self.get_panel(panel)
        sim = self.home_stat.floorplan.remrate_target
        lightsandappliance = sim.lightsandappliance
        temp = []

        temp.append(["Percent Interior Lighting", lightsandappliance.pct_interior_cfl])
        temp.append(["Percent Garage Lighting", lightsandappliance.pct_garage_cfl])
        temp.append(["Refrigerator (kWh/yr)", lightsandappliance.refrigerator_kw_yr])
        temp.append(["Dishwasher Energy Factor", lightsandappliance.dishwasher_energy_factor])
        temp.append(["Ceiling Fan (cfm/Watt)", lightsandappliance.ceiling_fan_cfm_watt])

        temp.append(["Clothes Dryer Fuel", lightsandappliance.get_clothes_dryer_fuel_display])
        temp.append(
            [
                "Clothes Dryer Energy Factor",
                lightsandappliance.clothes_dryer_energy_factor,
            ]
        )
        temp.append(
            [
                "Clothes Washer LER",
                lightsandappliance.clothes_washer_label_energy_rating,
            ]
        )
        temp.append(["Clothes Washer Capacity", lightsandappliance.clothes_washer_capacity])
        temp.append(["Range/Oven Fuel", lightsandappliance.get_oven_fuel_display])

        data = []
        style_bold = self.styles["Bold"]
        style_normal = self.styles["Normal"]
        for key, value in temp:
            data.extend([Paragraph(key, style_bold), Paragraph(str(value), style_normal)])

        data = split_list(data, 4)

        panel = self._add_annotation_table(data, panel, table_style=self.master_table_style)

    def _get_annual_energy_cost(self, simulation):
        # Annual Energy Cost ($/yr)
        temp = []

        for item in simulation.fuelsummary_set.get_fuel_summary():
            if item.total_cost > 0:
                temp.append((item.get_fuel_type_display(), "${:0,.2f}".format(item.total_cost)))

        return temp

    def _get_annual_end_use_cost(self, simulation):
        temp = []

        # Annual End-Use Cost ($/yr)
        temp.append(("Heating", "${:0,.2f}".format(simulation.results.heating_cost)))
        temp.append(("Cooling", "${:0,.2f}".format(simulation.results.cooling_cost)))
        temp.append(("Water Heating", "${:0,.2f}".format(simulation.results.hot_water_cost)))
        temp.append(
            (
                "Lights & Appliances",
                "${:0,.2f}".format(simulation.results.lights_and_appliances_total_cost),
            )
        )
        temp.append(("Photovoltaics", "${:0,.2f}".format(simulation.results.photo_voltaic_cost)))
        temp.append(("Service Charges", "${:0,.2f}".format(simulation.results.service_cost)))
        temp.append(("Total", "${:0,.2f}".format(simulation.results.total_cost)))

        return temp

    def _get_annual_end_use_consumption(self, simulation):
        # Annual End-Use Consumption
        temp = []

        items = simulation.fuelsummary_set.all()
        for item in items:
            if item.heating_consumption > 3 and item.fuel_units != 7:
                temp.append(
                    (
                        "Heating ({})".format(item.get_fuel_units_display()),
                        clean_number(item.heating_consumption),
                    )
                )

            if item.cooling_consumption > 3 and item.fuel_units != 8:
                temp.append(
                    (
                        "Cooling ({})".format(item.get_fuel_units_display()),
                        clean_number(item.cooling_consumption),
                    )
                )

            if item.hot_water_consumption > 3:
                temp.append(
                    (
                        "Hot Water ({})".format(item.get_fuel_units_display()),
                        clean_number(item.hot_water_consumption),
                    )
                )

            if item.lights_and_appliances_consumption > 3:
                temp.append(
                    (
                        "Lights & Appliances ({})".format(item.get_fuel_units_display()),
                        clean_number(item.lights_and_appliances_consumption),
                    )
                )

        return temp

    def _get_annual_energy_demands(self, simulation):
        temp = []
        round = partial(clean_number, round_to=1)

        # Annual Energy Demands (kW)
        winter = simulation.fuelsummary_set.get_winter_fuel_demands()[0]
        summer = simulation.fuelsummary_set.get_summer_fuel_demands()[0]
        temp.append(("Heating", round(winter.heating_consumption)))
        temp.append(("Cooling", round(summer.cooling_consumption)))
        temp.append(("Water Heating (Winter Peak)", round(winter.hot_water_consumption)))
        temp.append(("Water Heating (Summer Peak)", round(summer.hot_water_consumption)))
        temp.append(
            (
                "Lights and Appliances (Winter Peak)",
                round(winter.lights_and_appliances_consumption),
            )
        )
        temp.append(
            (
                "Lights and Appliances (Summer Peak)",
                round(summer.lights_and_appliances_consumption),
            )
        )
        temp.append(("Total Winter Peak", round(winter.total_cost)))
        temp.append(("Total Summer Peak", round(summer.total_cost)))

        return temp

    def _hers_score_title(self, panel):
        text = "<b>HERS</b> <br/> <font size=25>Score</font>"
        title = Paragraph(text, self.styles["hers-score"])
        title_width, title_height = title.wrapOn(self.canvas, 1.6 * inch, 11 * inch)
        self.add_paragraph_table(title, 0, 0.1, title_width, title_height, panel)
        return title_width

    def _hers_score_clipping_path(self, height, left_side, panel_top, scale_top, width):
        clipping_path = AxisPath()
        clipping_path.move(left_side, panel_top + scale_top)
        clipping_path.line(left_side + width, panel_top + scale_top)
        clipping_path.line(left_side + width, panel_top + scale_top + height)
        clipping_path.line(left_side, panel_top + scale_top + height)
        clipping_path.close()
        temp = AxisClipAndGradient(
            clipping_path,
            left_side,
            panel_top + scale_top,
            left_side + width,
            panel_top + scale_top + height,
            (rgb(23, 131, 70), rgb(240, 230, 90), rgb(215, 47, 53)),
            positions=(0, 0.75, 1),
            extend=False,
        )
        self.drawables.append(temp)

    def _hers_score_scale_markers(self, height, left_side, panel, panel_top, scale_top, width):
        """Draw scale markers and Numbers."""
        path = AxisPath(strokeColor=COLORS["scale_stroke"], fillColor=COLORS["scale_fill"])
        marker_left = left_side + 0.1
        marker_right = left_side + width - 0.1
        text_left = left_side + 0.1 - panel.x
        text_right = left_side + width - 0.1 - panel.x
        for i in range(0, 13):
            marker_x = map_range((0, 12), (marker_left, marker_right), i)
            text_x = map_range((0, 12), (text_left, text_right), i)
            path.move(marker_x, panel_top + scale_top + (height / 2))
            path.line(marker_x, panel_top + scale_top + (height * 1.5))

            paragraph = Paragraph(str(i * 10), self.styles["small-centered"])
            text_width, text_height = paragraph.wrapOn(self.canvas, 0.21 * inch, 2 * inch)
            self.add_paragraph_table(
                paragraph,
                text_x - ((text_width / 2) / inch),
                scale_top + height,
                text_width,
                text_height,
                panel,
            )
        self.drawables.append(path)

    def _hers_score_house(
        self, height, house_height, house_width, left_side, panel_top, scale_top, width
    ):
        # Make house
        hers_score = self.home_variables["hers_score"]
        house_x = map_range((0, 150), (left_side + 0.1, left_side + width - 0.1), hers_score)
        house_y = panel_top + (0.8 * scale_top)
        house = self._get_house_path(
            house_x,
            house_y + (house_height / 2),
            str(hers_score),
            width=house_width,
            height=house_height,
        )
        self.drawables.append(house)
        # Stick coming out of home
        house_marker = AxisPath(
            strokeColor=COLORS["house_marker_stroke"],
            fillColor=COLORS["house_marker_fill"],
            fill=1,
        )
        house_marker.move(house_x, house_y)
        house_marker.line(house_x, panel_top + scale_top + (height / 2))
        self.drawables.append(house_marker)
        # Place house with score inside
        self._set_panel_height(1, scale_top + height + 0.2)
        house_text = Paragraph(str(hers_score), self.styles["small-centered-white"])
        house_text_width, house_text_height = house_text.wrapOn(self.canvas, 0.3 * inch, 0.3 * inch)
        self.add_paragraph_table(
            house_text,
            house_x - (house_text_width / inch) / 2,
            house_y,
            house_text_width,
            0.1,
        )

    def _standard_protocol_calculations_variables(self):
        from axis.customer_neea.rtf_calculator.calculator import (
            NEEAV2Calculator,
            NEEAV3Calculator,
        )

        input_values = self.home_stat.get_input_values()
        answers = {m_id.replace("neea-", ""): value for m_id, value in input_values.items()}

        calculator_class = NEEAV3Calculator
        if self.home_stat.eep_program.slug == "neea-bpa":
            calculator_class = NEEAV2Calculator

        try:
            calc = calculator_class(home_status_id=self.home_stat.id, **answers).result_data()
        except (AttributeError, ValueError):
            calc = None

        return calc

    # ==============================================================================================
    # INFORMATION
    # ==============================================================================================

    def home_information(self, panel):
        panel = self.get_panel(panel)
        data = self._map_table_variables(DEFAULT_HOME_INFORMATION, self.home_variables)

        if "street_line2" in self.home_variables.keys():
            if self.home_variables["street_line2"]:
                data.insert(4, ["", self.home_variables["street_line2"]])
        if "subdivision" in self.home_variables.keys():
            data.insert(2, ["Subdivision/MF Development:", self.home_variables["subdivision"]])

        temp = [[Paragraph("System Information", self.styles["centered-bold"])]]
        # Row data needs to be wrapped in flowable so line breaks work
        for key, value in data:
            key = Paragraph(key, style=self.styles["Bold"])
            value = Paragraph(value, style=self.styles["Normal"])
            temp.append([key, value])

        t = Table(temp, colWidths=[1.5 * inch, 2 * inch])
        t.setStyle(self.home_information_table_style)
        width, height = t.wrapOn(self.canvas, 8 * inch, 11 * inch)
        self.add_paragraph_table(t, 0.1, 0, width, height, panel)

    def map(self, panel):
        panel = self.get_panel(panel)
        if self.home.latitude and self.home.longitude:
            image = self._get_map_image(self.home.latitude, self.home.longitude)
            self.drawables.append(AxisImage(image, 4.3, panel.y + 0.3, 3.3, 2.1, radius=5))
            self._set_panel_height(panel, 2.1)

    # flake8: noqa: C901
    def standard_protocol_calculations(self, panel):
        data = self._standard_protocol_calculations_variables()

        if data is None:
            return

        panel = self.get_panel(panel)

        COLSPAN = "COLSPAN"

        def p(text):
            return Paragraph(text, self.styles["Normal"])

        def b(text):
            return Paragraph(text, self.styles["Bold"])

        def kwh(lookup, include_units=True):
            s = "{:.2f}".format(data["{}_kwh_savings".format(lookup)])
            if include_units:
                s += " kWh"
            return p(s)

        def therm(lookup):
            return p("{:.2f} Therms".format(data["{}_therm_savings".format(lookup)]))

        def kwhrate_row(label, lookup, rate):
            return [b(label), kwh(lookup, include_units=False), p(rate)]

        def kwhtherm_row(label, lookup):
            return [b(label), kwh(lookup), therm(lookup)]

        def kwh_row(label, lookup):
            return [b(label), kwh(lookup), p("0.00 Therms")]

        table_styles = []
        rows = [
            [
                Paragraph("Standard Protocol Calculations", self.styles["centered-bold"]),
                COLSPAN,
                COLSPAN,
            ],
        ]

        has_bpa_affiliation = self.user.company.sponsors.filter(slug="bpa").exists()
        if has_bpa_affiliation:
            rows.extend(
                [
                    [  # Rather long spec for a header row
                        Paragraph("Energy Savings Category", self.styles["centered-bold"]),
                        Paragraph("Savings (kWh)", self.styles["centered-bold"]),
                        Paragraph("Rate", self.styles["centered-bold"]),
                    ],
                    kwhrate_row(
                        "Shell Upgrades, incl. Windows",
                        "reported_shell_windows",
                        rate="$0.45",
                    ),
                    kwhrate_row(
                        "HVAC and Water Heat Upgrades",
                        "reported_hvac_waterheater",
                        rate="$0.27",
                    ),
                    kwhrate_row("Appliance Upgrades", "appliance", rate="$0.27"),
                    kwhrate_row(
                        "Lighting Upgrades, including Fixtures, Showerheads and Smart Thermostats",
                        "reported_lighting_showerhead_tstats",
                        rate="$0.10",
                    ),
                    [
                        b("Total"),
                        p("{:.2f}".format(data["total_kwh_savings"])),
                        COLSPAN,
                    ],
                ]
            )
            table_styles.extend(
                [
                    ("LEFTPADDING", (1, 2), (2, 7), 0.735 * inch),
                ]
            )
        else:
            rows.extend(
                [
                    kwhtherm_row("Heating", "heating"),
                    kwhtherm_row("Cooling", "cooling"),
                    kwhtherm_row("Smart Thermostat", "smart_thermostat"),
                    kwhtherm_row("Water Heater", "water_heater"),
                    kwhtherm_row("Low Flow Shower Heads", "showerhead"),
                    kwh_row("Lighting", "lighting"),
                    kwh_row("Appliances", "appliance"),
                    kwhtherm_row("Total Annual Savings (kWh)", "total"),
                    [
                        b("Total Annual Savings (MBtu)"),
                        p("{:.2f} MMBtu".format(data["total_mmbtu_savings"])),
                        COLSPAN,
                    ],
                ]
            )

        bpa_payment_row = [
            b("Total BPA Utility Payment to BPA utility customer"),
            p(data["pretty_total_incentive"]),
            COLSPAN,
        ]
        rows.extend(
            [
                # Removed when show_utility_payment is False
                bpa_payment_row,
                [
                    Paragraph("Utility Incentive Calculations", self.styles["centered-bold"]),
                    COLSPAN,
                    COLSPAN,
                ],
            ]
        )

        if data["pct_improvement_method"] == "alternate":
            rows.append(
                [
                    b("As-Built Total Consumption"),
                    p("{:.2f} MMBtu".format(data["improved_total_consumption_mmbtu_with_savings"])),
                    COLSPAN,
                ]
            )
        else:
            rows.append(
                [
                    b("As-Built Total Consumption"),
                    p("{:.2f} MMBtu".format(data["improved_total_consumption_mmbtu"])),
                    COLSPAN,
                ]
            )

        rows.append(
            [
                b("Reference Total Consumption"),
                p("{:.2f} MMBtu".format(data["code_total_consumption_mmbtu"])),
                COLSPAN,
            ]
        )

        if data["pct_improvement_method"] == "alternate":
            rows.append(
                [
                    b("Percent Improvement"),
                    p("{} Improvement".format(data["pretty_revised_percent_improvement"])),
                    COLSPAN,
                ]
            )
        else:
            rows.append(
                [
                    b("Percent Improvement"),
                    p("{} Improvement".format(data["pretty_percent_improvement"])),
                    COLSPAN,
                ]
            )

        rows.append(
            [
                b("Total Utility Builder Incentive"),
                p("${:.2f}".format(data["builder_incentive"])),
                COLSPAN,
            ]
        )

        if has_bpa_affiliation:
            # Only nudge the values to align better when the top section is the new BPA values
            table_styles.extend(
                [
                    ("LEFTPADDING", (1, -4), (2, -1), 0.735 * inch),
                ]
            )

        # Remove BPA Utility payment if user shouldn't see it
        company = self.user.company
        show_utility_payment = any(
            [
                self.user.is_superuser,
                company.slug in (["neea", "clearesult-qa"]),
                company.company_type == "utility" and company.sponsors.filter(slug="bpa").exists(),
                company.company_type == "qa" and company.sponsors.filter(slug="bpa").exists(),
            ]
        )
        if not show_utility_payment:
            rows.pop(rows.index(bpa_payment_row))

        def row_span(y, data):
            """Returns a coordinate tuple for TableStyle spanning out the COLSPAN entries."""
            # NOTE: This naively spans the first and last occurance of COLSPAN
            start = 0
            end = 0

            try:
                # This -1 comes from needing to start spanning on the column before the COLSPAN
                start = data.index(COLSPAN) - 1
            except IndexError:
                pass
            try:
                # This -1 comes from TableStyle spans wanting indexes, not slices
                end = data[::-1].index(COLSPAN) + len(data) - 1
            except IndexError:
                pass

            return ((start, y), (end, y))

        table_styles.extend(
            [("SPAN",) + row_span(i, row) for i, row in enumerate(rows) if COLSPAN in row]
        )
        panel = self._add_annotation_table(
            rows,
            panel,
            style=TableStyle(table_styles),
            colWidths=[3.65 * inch, 1.825 * inch, 1.825 * inch],
        )

    def programs(self, panel):
        panel = self.get_panel(panel)
        programs = []
        style_normal = self.styles["Normal"]
        style_bold = self.styles["Bold"]
        visible_programs = self.home.eep_programs.filter_by_user(self.user)
        if "eto" in self.home_stat.eep_program.slug:
            visible_programs = [self.home_stat.eep_program]

        programs.append([Paragraph("Program Information", self.styles["centered-bold"])])

        for program in visible_programs:
            home_stat = self.home.homestatuses.get(eep_program=program)
            program_state = home_stat.get_state_display()

            row_one = [
                Paragraph("Program:", style_bold),
                Paragraph(program.name, style_normal),
                " ",
                " ",
            ]
            row_two = [
                Paragraph("State:", style_bold),
                Paragraph(program_state, style_normal),
            ]

            if home_stat.certification_date:
                cert_date = home_stat.certification_date.isoformat()
                row_two.extend(
                    (
                        Paragraph("Cert. Date:", style_bold),
                        Paragraph(cert_date, style_normal),
                    )
                )
            else:
                pct_complete = "{:.2f}".format(home_stat.pct_complete)
                row_two.extend((Paragraph("{}% Complete".format(pct_complete), style_normal), " "))
                self.program_table_style.add("SPAN", (3, 1), (-1, 1))

            floorplan = home_stat.floorplan.name if home_stat.floorplan else ""
            row_three = [
                Paragraph("Floorplan:", style_bold),
                Paragraph(floorplan, style_normal),
            ]
            try:
                incentive_payment_status = home_stat.incentivepaymentstatus
            except IncentivePaymentStatus.DoesNotExist:
                incentive_payment_status = None

            if incentive_payment_status:
                incentive_phase = home_stat.incentivepaymentstatus.get_state_display()
                row_three.extend(
                    (
                        Paragraph("Incentive State:", style_bold),
                        Paragraph(incentive_phase, style_normal),
                    )
                )
            else:
                row_three.extend(("", ""))

            programs.extend((row_one, row_two, row_three))

        t = Table(programs)
        t.setStyle(self.program_table_style)
        width, height = t.wrapOn(self.canvas, 7.3 * inch, 8 * inch)
        self.add_paragraph_table(t, 0.1, 0, width, height, panel)

    def companies(self, panel):
        from axis.company.strings import COMPANY_TYPES_PLURAL

        panel = self.get_panel(panel)
        results = defaultdict(list)

        for relationship in self.home.relationships.all():
            if relationship.company.get_company_type_display() == "Utility Company":
                co_types = self._get_utility_string(relationship)
            else:
                co_types = [""]
            results[relationship.company.company_type].append((relationship.company.name, co_types))

        data = []
        for co_type in COMPANY_TYPES_PLURAL:
            co_type_list = results.get(co_type, [])
            if not len(co_type_list):
                continue
            if len(co_type_list) > 1:
                title = COMPANY_TYPES_PLURAL[co_type][1]
            else:
                title = COMPANY_TYPES_PLURAL[co_type][0]
            subheading = Paragraph("{}:".format(title), self.styles["subheading"])
            comps = []
            for company, co_types in co_type_list:
                text = "{} {}"
                for co_type in co_types:
                    comps.append(Paragraph(text.format(company, co_type), self.styles["list-item"]))

            data.append([subheading, comps])

        col_one, col_two = data[: len(data) // 2], data[len(data) // 2 :]
        dangling = "left"
        divided_list = []
        for one, two in zip_longest(col_one, col_two):
            if dangling == "middle":
                if not one:
                    one = ["", two[0], two[1], ""]
                else:
                    one.extend(two)
                divided_list.append(one)
            elif dangling == "right":
                one.extend(two)
                divided_list.append(one)
            elif dangling == "left":
                if not one:
                    one = [two[0], two[1], " ", " "]
                else:
                    one.extend(two)
                divided_list.append(one)

        # divided_list.insert(0,
        #                     [Paragraph('Companies', self.styles['heading-centered']), '', '', ' '])

        t = Table(divided_list)
        t.setStyle(self.company_table_style)
        width, height = t.wrapOn(self.canvas, 7.3 * inch, 8 * inch)
        panel_height = panel.height
        self.add_paragraph_table(t, 0.1, panel.height + 0.1, width, height, panel)
        self._set_panel_height(panel, panel_height + (height / inch) + 0.1)

    def active_floorplan(self, panel):
        panel = self.get_panel(panel)
        var_dict = {}

        if self.home_stat.floorplan:
            self._set_active_floorplan_variables(var_dict)

        data = self.map_table_variables(PERFORMANCE_ITEMS, var_dict)

        temp = [[Paragraph("Rating Summary", self.styles["centered-bold"])]]
        style_bold = self.styles["Bold"]
        style_normal = self.styles["Normal"]

        program_skips = {
            "neea-bpa": ["Ceiling Attic R-Value:", "Ceiling Vaulted R-Value:"],
            "neea-bpa-v3": ["Ceiling Attic R-Value:", "Ceiling Vaulted R-Value:"],
        }
        hide_blank = [
            "Space Heating:",
            "Space Cooling:",
            "Water Heating:",
            "Air Source Heat Pump:",
            "Ground Source Heat Pump:",
            "Dual Fuel Heat Pump:",
            "Integrated Space/Water Heating:",
        ]

        skip = program_skips.get(self.home_stat.eep_program.slug, [])
        for key, value in data:
            key, value = key.strip(), value.strip()
            if key in hide_blank and (not value or value == "-"):
                continue
            if key in skip:
                continue
            key = Paragraph(key, style_bold)
            value = Paragraph(value, style_normal)
            temp.append([key, value])

        panel = self._add_annotation_table(temp, panel, table_style=self.table_with_header_style)

    def eps_incentives(self, panel) -> None:
        panel = self.get_panel(panel)

        temp = []
        if self.home_stat.eep_program.slug == "eto-2022":
            instance = FastTrackSubmission.objects.filter(home_status=self.home_stat).first()
            serializer = HomeProjectETO2022IncentiveSerializer(instance=instance)
            table = serializer.get_reportlab_table(styles=self.styles)
            self._add_annotation_table(
                table,
                panel,
                ensure_enough_space=True,
            )
            return

        style_bold = self.styles["Bold"]
        style_normal = self.styles["Normal"]

        def map_data_to_paragraph(data) -> list:
            # Map our tablespace into report paragraphse
            p_data = []
            for item in data:
                key = [Paragraph(item[0].strip(), style_bold)]
                try:
                    values = (
                        [Paragraph(x.strip(), style_normal) for x in item[1:]] if len(item) else []
                    )
                except AttributeError:
                    print(key, item)
                    raise
                p_data.append(key + values)
            return p_data

        items = EPS_INCENTIVE_ITEMS
        col_widths = [5 * inch, 2.5 * inch]
        var_dict = {}
        self._set_eps_incentive_variables(var_dict)
        if self.home_stat.eep_program.slug == "eto-fire-2021":
            items = EPS_FIRE_INCENTIVE_ITEMS
        elif self.home_stat.eep_program.slug == "washington-code-credit":
            items = EPS_WA_CODE_CREDITS_INCENTIVE
            var_dict.update(self.get_washington_code_credit_calculator_data())
            temp.append(
                [
                    Paragraph(
                        "Program Incentives & Savings Summary",
                        self.styles["centered-bold"],
                    )
                ]
            )
        p_data = map_data_to_paragraph(self.map_table_variables(items, var_dict))
        self._add_annotation_table(
            p_data,
            panel,
            ensure_enough_space=True,
            colWidths=col_widths,
        )

    def _annotations_check(self):
        requirements = {}

        # When the report is generated from a ETO or NEEA Efficient homestatus, show only
        # annotations for that homestatus and no others.
        if ("eto" in self.home_stat.eep_program.slug) or (
            self.home_stat.eep_program.slug == "neea-efficient-homes"
        ):
            visible_homestatuses = [self.home_stat]
        else:
            # Show annotations for all programs if some other program is the center of the report
            visible_homestatuses = self.home.homestatuses.filter_by_user(self.user)

        for stat in visible_homestatuses:
            requirements[stat.eep_program] = stat.get_annotations_breakdown()

        for program in requirements.keys():
            if len(requirements[program]) > 0:
                return True

        return False

    def annotations(self, panel):
        panel = self.get_panel(panel)

        requirements = {}

        # When the report is generated from a ETO or NEEA Efficient homestatus, show only
        # annotations for that homestatus and no others.
        if ("eto" in self.home_stat.eep_program.slug) or (
            self.home_stat.eep_program.slug == "neea-efficient-homes"
        ):
            visible_homestatuses = [self.home_stat]
        else:
            # Show annotations for all programs if some other program is the center of the report
            visible_homestatuses = self.home.homestatuses.filter_by_user(self.user)

        for stat in visible_homestatuses:
            requirements[stat.eep_program] = stat.get_annotations_breakdown()

        header_already_shown = False

        if requirements:
            for eep in requirements:
                specific_annotations = []
                variable_list = []
                variable_dictionary = {}

                if eep.slug == "neea-energy-star-v3":
                    specific_annotations = NEEA_ENERGY_STAR_V3
                elif eep.slug == "neea-energy-star-v3-performance":
                    specific_annotations = NEEA_ENERGY_STAR_V3_PERFORMANCE
                    self._set_NEEA_performance_specific_variables(variable_dictionary)
                elif eep.slug == "neea-prescriptive-2015":
                    specific_annotations = NEEA_PRESCRIPTIVE_2015
                elif eep.slug == "neea-performance-2015":
                    specific_annotations = NEEA_PERFORMANCE_2015
                    self._set_NEEA_performance_specific_variables(variable_dictionary)
                elif eep.slug == "neea-efficient-homes":
                    specific_annotations = NEEA_EFFICIENT_HOMES
                if specific_annotations:
                    for annotation_type, annotation in requirements[eep].items():
                        variable_dictionary[annotation_type.slug] = (
                            annotation.content if annotation else "-"
                        )
                        variable_dictionary["{}-required".format(annotation_type.slug)] = (
                            "*" if annotation_type.is_required else ""
                        )
                    variable_dictionary["site-id"] = self.home.get_id()
                else:
                    for annotation_type, annotation in requirements[eep].items():
                        variable_list.append(
                            [
                                annotation_type.name,
                                annotation.content if annotation else "-",
                            ]
                        )

                # put title for block
                # t = Table([[Paragraph('Annotations', self.styles['subheading'])]])
                # t.setStyle(self.annotations_table_style)
                # width, height = t.wrapOn(self.canvas, 7.3*inch, 8*inch)
                # panel_height = panel.height
                # self.add_paragraph_table(t, 0.1, panel.height, width, height, panel)
                # self._set_panel_height(panel, panel_height + (height / inch))

                rows = []
                if not header_already_shown:
                    rows.append([Paragraph("Program Summary", self.styles["centered-bold"])])

                if specific_annotations:
                    for dictionary in specific_annotations:
                        data = self._map_table_variables(dictionary, variable_dictionary)

                        # Row data needs to be wrapped in flowable so line breaks work
                        style_bold = self.styles["Bold"]
                        style_normal = self.styles["Normal"]
                        # print(data)
                        for key, value, key2, value2 in data:
                            key = Paragraph(key, style_bold)
                            value = Paragraph(value, style_normal)
                            key2 = Paragraph(key2, style_bold)
                            value2 = Paragraph(value2, style_normal)
                            rows.append([key, value, key2, value2])

                        # Avoid displaying the header alone if it's still pending but there are no
                        # annotations to display in this set.
                        if not header_already_shown and len(rows) == 1:
                            continue

                        panel = self._add_annotation_table(
                            rows,
                            panel,
                            top_space=0.1,
                            table_style=self.table_with_header_style,
                            ensure_enough_space=True,
                        )
                        rows = []  # Clear out for next dictionary in the specific set
                        header_already_shown = True  # Just shown or already shown, always mark it

                else:
                    # Loose annotations, no "specific" structure

                    style_bold = self.styles["Bold"]
                    style_normal = self.styles["Normal"]
                    for key, value in variable_list:
                        key = Paragraph(key, style_bold)
                        value = Paragraph(value, style_normal)
                        rows.extend([key, value])

                    # Avoid displaying the header alone if it's still pending but there are no
                    # annotations to display in this set.
                    if not header_already_shown and len(rows) == 1:
                        continue

                    if not header_already_shown:
                        # Chunk into 4 items, ignoring first
                        rows = [rows[0]] + split_list(rows[1:], 4)
                    else:
                        # No header present, chunk all items
                        rows = split_list(rows, 4)
                    panel = self._add_annotation_table(
                        rows,
                        panel,
                        top_space=0.1,
                        table_style=self.table_with_header_style,
                        ensure_enough_space=True,
                    )
                    rows = []
                    header_already_shown = True  # Just shown or already shown, always mark it

    def checklist_questions(self, panel):
        panel = self.get_panel(panel)
        style_bold = self.styles["Bold"]
        style_normal = self.styles["Normal"]

        is_eto = "eto" in self.home_stat.eep_program.slug
        inputs = []
        answers = []
        use_legacy = self.home_stat.collection_request is None
        if not use_legacy:
            context = {
                "user": self.user,
            }
            collector = ChecklistCollector(self.home_stat.collection_request, **context)
            # Duplicates found - take the last one.
            _inputs = (
                collector.get_inputs(cooperative_requests=True)
                .select_related("instrument")
                .order_by("id")
            )
            data = {i.instrument.measure_id: i.id for i in _inputs}
            inputs = CollectedInput.objects.filter(id__in=data.values())
        else:
            answers = (
                Answer.objects.filter_by_home_status(self.home_stat)
                .select_related("question")
                .order_by("question__priority")
            )

        lines = []
        for input in inputs or answers:
            if not use_legacy:
                text = input.instrument.text
                method = collector.get_method(measure=input.instrument.measure_id)
                value = method.get_data_display(input.data["input"])
                comment = input.data.get("comment")
            else:
                text = input.question.question
                value = input.answer
                comment = input.comment

            if is_eto and text.startswith("NWES"):
                continue

            value = "{}".format(value)

            question = [[Paragraph(text, style_bold), Paragraph(value, style_normal)]]
            if comment:
                question.append([Paragraph("Comment: {}".format(comment), style_normal)])
            lines.append(question)

        for i, line in enumerate(lines):
            table_style = self.checklist_table_style
            if i == 0:
                table_style = self.checklist_with_header_table_style
                line.insert(0, [Paragraph("Inspection Checklist", self.styles["centered-bold"])])
            panel = self._add_annotation_table(
                line,
                panel,
                table_style=table_style,
                colWidths=[5.475 * inch, 1.825 * inch],
            )

    def remrate_data_building_info(self, panel):
        panel = self.get_panel(panel)
        simulation = self.home_stat.floorplan.remrate_target

        # building information
        data = self._build_remrate_table_data(self._get_building_information(simulation))
        data = split_list(data, 4)
        panel = self._add_annotation_table(
            data, panel, table_style=self.remrate_building_info_table_style
        )

        # info ratings
        data = self._build_remrate_table_data(self._get_building_info_ratings(simulation))
        data = split_list(data, 4)
        panel = self._add_annotation_table(
            data, panel, table_style=self.remrate_building_info_table_style
        )

        # site data
        data = self._build_remrate_table_data(self._get_building_info_site_data(simulation))
        data = split_list(data, 4)
        self._add_annotation_table(data, panel, table_style=self.remrate_building_info_table_style)

    def remrate_data_fuel_summary(self, panel):
        panel = self.get_panel(panel)
        simulation = self.home_stat.floorplan.remrate_target
        heading = self.styles["centered-bold"]
        colWidths = ["35%", "15%", "35%", "15%"]

        # section 1 ================================================

        temp1 = self._get_annual_energy_cost(simulation)
        temp2 = self._get_annual_end_use_cost(simulation)

        data = [
            Paragraph("Annual Energy Cost ($/yr)", heading),
            "",
            Paragraph("Annual End-Use Cost ($/yr)", heading),
            "",
        ]
        data.extend(self._build_remrate_fuel_summary_table_data(temp1, temp2))
        data = split_list(data, 4)
        panel = self._add_annotation_table(
            data,
            panel,
            table_style=self.remrate_fuel_summary_table_style,
            colWidths=colWidths,
        )

        # section 2 ================================================

        temp1 = self._get_annual_end_use_consumption(simulation)
        temp2 = self._get_annual_energy_demands(simulation)

        data = [
            Paragraph("Annual End-Use Consumption", heading),
            "",
            Paragraph("Annual Energy Demands (kW)", heading),
            "",
        ]
        data.extend(self._build_remrate_fuel_summary_table_data(temp1, temp2))
        data = split_list(data, 4)
        self._add_annotation_table(
            data,
            panel,
            table_style=self.remrate_fuel_summary_table_style,
            colWidths=colWidths,
        )

    def remrate_data_mechanical_systems(self, panel):
        panel = self.get_panel(panel)
        simulation = self.home_stat.floorplan.simulation
        heading = self.styles["centered-bold"]
        bold = self.styles["Bold"]
        normal = self.styles["Normal"]

        if not simulation:
            return

        temp = [Paragraph("Mechanical Systems", heading)]

        for item in simulation.mechanical_equipment.all():
            temp.append(Paragraph(str(item), normal))

        # for item in simulation.generalmechanicalequipment_set.all():
        #     temp.append(Paragraph(str(item), normal))

        for item in simulation.photovoltaics.all():
            temp.append(Paragraph("Photo Voltaic System: {}".format(str(item)), normal))

        ventilation = simulation.infiltration
        if ventilation:
            temp.append(Paragraph("Ventilation: {}".format(ventilation), normal))

        # if self.has_rem_data and simulation.solarsystem:
        #     temp.append(Paragraph('Solar System: {}'.format(simulation.solarsystem), normal))

        data = split_list(temp, 1)
        self._add_annotation_table(
            data,
            panel,
            table_style=self.remrate_mechanical_systems_table_style,
            ensure_enough_space=True,
        )

    def hers_score(self, panel):
        panel = self.get_panel(panel)

        title_width = self._hers_score_title(panel)

        house_width = house_height = 0.3
        panel_top = panel.y
        width = 5
        height = 0.25
        scale_top = 0.5
        left_side = panel.x + title_width / inch + 0.1

        self._hers_score_clipping_path(height, left_side, panel_top, scale_top, width)

        self._hers_score_scale_markers(height, left_side, panel, panel_top, scale_top, width)

        self._hers_score_house(
            height, house_height, house_width, left_side, panel_top, scale_top, width
        )

    def generate_page_one(self, user, **kwargs):
        self.axis_drawn = False
        self.customer_logo = False

        self.groups_and_checks = [
            ([self.home_information, self.map], True),
            ([self.hers_score], self.has_rem_data and not self.hide_hers_index),
            ([self.programs, self.companies], True),
            ([self.active_floorplan], self.has_rem_data or self.has_ekotrope_data),
            (
                [self.standard_protocol_calculations],
                self._standard_protocoL_calculations_check(),
            ),
            ([self.wcc_static_incentives], self._wcc_static_incentives_check(user)),
            ([self.eps_incentives], self._eps_incentives_data_check(user)),
            ([self.annotations], self._annotations_check()),
            ([self.remrate_data_building_info], self._building_info_data_check()),
            ([self.checklist_questions], True),
            ([self.remrate_data_fuel_summary], self._fuel_summary_data_check()),
            (
                [self.remrate_data_mechanical_systems],
                self._mechanical_systems_data_check(),
            ),
        ]
        self.groups = [group for group, perm in self.groups_and_checks if perm]

        for index, group in enumerate(self.groups):
            for method in group:
                method(index)

        self.draw_frames()
        self.draw_drawables()

    def build(self, home_stat, response, user, **kwargs):
        self.user = user
        self.vertical_hers = False
        self._set_variables(home_stat, user)
        self.canvas = AxisCanvas(response, pagesize=letter)
        self.generate_page_one(user, **kwargs)
        self.printed_by_info(user)
        self.canvas.showPage()
        self.canvas.save()


class StandardDisclosureFormPDF(AxisSimpleDocTemplate):
    file_name = "RESNET_disclosure_form.pdf"
    file_name_plural = "RESNET_disclosure_form.zip"
    inner_file_name = "RESNET_disclosure_form_{obj.pk}.pdf"

    @classmethod
    def new(cls, company, home_status=None, subdivision=None, bulk=None):
        if not any((home_status, subdivision, bulk)):
            raise ValueError("One of 'home' or 'subdivision' or 'bulk' is required.")

        variables = {
            "company": company,
            "use_raw_addresses": False,
        }
        if subdivision:
            object_list = [subdivision]
        elif bulk:
            object_list = list(
                EEPProgramHomeStatus.objects.filter_by_company(company).filter(
                    home__subdivision=bulk
                )
            )
        else:
            object_list = [home_status]
            if company.display_raw_addresses:
                if (
                    home_status.home.geocode_response
                    and home_status.home.geocode_response.geocode.raw_street_line1
                ):
                    variables["use_raw_addresses"] = True

        return super(StandardDisclosureFormPDF, cls).new(object_list, variables=variables)

    def __init__(self, *args, **kwargs):
        kwargs["margin"] = 1 * inch
        kwargs["leftMargin"] = 1 * inch
        kwargs["rightMargin"] = 1 * inch
        kwargs["topMargin"] = 1 * inch
        kwargs["bottomMargin"] = 1 * inch
        self.styles = self.get_styles()
        super(StandardDisclosureFormPDF, self).__init__(*args, **kwargs)

    @property
    def table_styles(self):
        return getattr(self.styles, "table_styles")

    @property
    def variables(self):
        if not hasattr(self, "_data"):
            var = lambda key: self._variables.get(key, "")
            yesno = lambda key, value=True: "X" if self._variables.get(key) == value else " "
            yesany = (
                lambda keys: "X"
                if any(self._variables.get(k) not in (None, "none") for k in keys)
                else " "
            )
            self._data = {
                "location": var("location"),
                "city": var("city"),
                "state": var("state"),
                "one": yesno("rater_receives_fee"),
                "two": yesany(
                    [
                        "service_mechanical_design",
                        "service_moisture_consulting",
                        "service_performance_testing",
                        "service_training",
                        "service_other",
                    ]
                ),
                "two_A": yesno("service_mechanical_design"),
                "two_B": yesno("service_moisture_consulting"),
                "two_C": yesno("service_performance_testing"),
                "two_D": yesno("service_training"),
                "two_E": yesany(["service_other"]),
                "two_E_specify": var("service_other"),
                "three": yesany(["rater_responsibility"]),
                "three_A": yesno("rater_responsibility", value="seller"),
                "three_B": yesno("rater_responsibility", value="mortgagor"),
                "three_C": yesno("rater_responsibility", value="employee"),
                "supplier_hvac_rater_installed": yesno("supplier_hvac", value="rater_installed"),
                "supplier_hvac_employer_installed": yesno(
                    "supplier_hvac", value="employer_installed"
                ),
                "supplier_hvac_rater_supplied": yesno("supplier_hvac", value="rater_supplied"),
                "supplier_hvac_employer_supplied": yesno(
                    "supplier_hvac", value="employer_supplied"
                ),
                "supplier_thermal_rater_installed": yesno(
                    "supplier_thermal", value="rater_installed"
                ),
                "supplier_thermal_employer_installed": yesno(
                    "supplier_thermal", value="employer_installed"
                ),
                "supplier_thermal_rater_supplied": yesno(
                    "supplier_thermal", value="rater_supplied"
                ),
                "supplier_thermal_employer_supplied": yesno(
                    "supplier_thermal", value="employer_supplied"
                ),
                "supplier_sealing_rater_installed": yesno(
                    "supplier_sealing", value="rater_installed"
                ),
                "supplier_sealing_employer_installed": yesno(
                    "supplier_sealing", value="employer_installed"
                ),
                "supplier_sealing_rater_supplied": yesno(
                    "supplier_sealing", value="rater_supplied"
                ),
                "supplier_sealing_employer_supplied": yesno(
                    "supplier_sealing", value="employer_supplied"
                ),
                "supplier_windows_rater_installed": yesno(
                    "supplier_windows", value="rater_installed"
                ),
                "supplier_windows_employer_installed": yesno(
                    "supplier_windows", value="employer_installed"
                ),
                "supplier_windows_rater_supplied": yesno(
                    "supplier_windows", value="rater_supplied"
                ),
                "supplier_windows_employer_supplied": yesno(
                    "supplier_windows", value="employer_supplied"
                ),
                "supplier_appliances_rater_installed": yesno(
                    "supplier_appliances", value="rater_installed"
                ),
                "supplier_appliances_employer_installed": yesno(
                    "supplier_appliances", value="employer_installed"
                ),
                "supplier_appliances_rater_supplied": yesno(
                    "supplier_appliances", value="rater_supplied"
                ),
                "supplier_appliances_employer_supplied": yesno(
                    "supplier_appliances", value="employer_supplied"
                ),
                "supplier_construction_rater_installed": yesno(
                    "supplier_construction", value="rater_installed"
                ),
                "supplier_construction_employer_installed": yesno(
                    "supplier_construction", value="employer_installed"
                ),
                "supplier_construction_rater_supplied": yesno(
                    "supplier_construction", value="rater_supplied"
                ),
                "supplier_construction_employer_supplied": yesno(
                    "supplier_construction", value="employer_supplied"
                ),
                "supplier_other_rater_installed": yesno("supplier_other", value="rater_installed"),
                "supplier_other_employer_installed": yesno(
                    "supplier_other", value="employer_installed"
                ),
                "supplier_other_rater_supplied": yesno("supplier_other", value="rater_supplied"),
                "supplier_other_employer_supplied": yesno(
                    "supplier_other", value="employer_supplied"
                ),
                "supplier_other_specify": var("supplier_other_specify"),
                "five": yesno("verified"),
            }
            four = "X" in [
                self._data["supplier_hvac_rater_installed"],
                self._data["supplier_hvac_employer_installed"],
                self._data["supplier_hvac_rater_supplied"],
                self._data["supplier_hvac_employer_supplied"],
                self._data["supplier_thermal_rater_installed"],
                self._data["supplier_thermal_employer_installed"],
                self._data["supplier_thermal_rater_supplied"],
                self._data["supplier_thermal_employer_supplied"],
                self._data["supplier_sealing_rater_installed"],
                self._data["supplier_sealing_employer_installed"],
                self._data["supplier_sealing_rater_supplied"],
                self._data["supplier_sealing_employer_supplied"],
                self._data["supplier_windows_rater_installed"],
                self._data["supplier_windows_employer_installed"],
                self._data["supplier_windows_rater_supplied"],
                self._data["supplier_windows_employer_supplied"],
                self._data["supplier_appliances_rater_installed"],
                self._data["supplier_appliances_employer_installed"],
                self._data["supplier_appliances_rater_supplied"],
                self._data["supplier_appliances_employer_supplied"],
                self._data["supplier_construction_rater_installed"],
                self._data["supplier_construction_employer_installed"],
                self._data["supplier_construction_rater_supplied"],
                self._data["supplier_construction_employer_supplied"],
                self._data["supplier_other_rater_installed"],
                self._data["supplier_other_employer_installed"],
                self._data["supplier_other_rater_supplied"],
                self._data["supplier_other_employer_supplied"],
            ]
            self._data["four"] = "X" if four else " "

            if isinstance(self._obj, EEPProgramHomeStatus):
                home_status = self._obj
                ror = home_status.rater_of_record
                location = home_status.home.get_addr(raw=self._variables["use_raw_addresses"])
                city = home_status.home.city.name
                state = home_status.home.city.state
                serial_number = "H-{}".format(home_status.home.get_id())
            elif isinstance(self._obj, Subdivision):
                subdivision = self._obj
                homes = subdivision.home_set.filter_by_company(self._variables["company"])

                ror = None
                rors = set(
                    filter(
                        None,
                        homes.values_list("homestatuses__rater_of_record", flat=True),
                    )
                )
                if len(rors) == 1:
                    ror = User.objects.get(id=list(rors)[0])

                location = "{}{} / {}".format(
                    *(
                        "{} / ".format(subdivision.community.name) if subdivision.community else "",
                        subdivision.name,
                        subdivision.builder_org.name,
                    )
                )
                city = subdivision.city.name
                state = subdivision.city.state
                serial_number = "S-{}".format(subdivision.get_id())
            else:
                raise ValueError("wo there")
            self._data.update(
                {
                    "serial_number": serial_number,
                    "rater_of_record": ror or "",
                    "rater_resnet_rtin": (ror.rater_id or "") if ror else "",
                    "location": location,
                    "city": city,
                    "state": state,
                }
            )
            if ror and ror.signature_image:
                if settings.SERVER_TYPE == "dev":
                    filepath = ror.signature_image.path
                else:
                    filepath = ror.signature_image.url
                self._data.update(
                    {
                        "signature_filepath": filepath,
                        "signature_width_ratio": ror.signature_image.width
                        / ror.signature_image.height,
                    }
                )
            else:
                self._data.update(
                    {
                        "signature_filepath": None,
                        "signature_width_ratio": None,
                    }
                )
        return self._data

    def add_styles(self, s, **styles):
        for name, settings in styles.items():
            s.add(ParagraphStyle(name=name, **settings), name)

    def get_styles(self):
        styles = getSampleStyleSheet()

        self.add_styles(
            styles,
            **{
                "page_title": {
                    "parent": styles["h1"],
                    "alignment": 1,
                },
                "table_head": {
                    "parent": styles["h5"],
                    "fontSize": 9,
                },
                "bold_italic_centered": {
                    "parent": styles["h3"],
                    "fontSize": 9,
                    "alignment": 1,
                },
                "large_bold": {
                    "parent": styles["h5"],
                    "fontSize": 10,
                    "leading": 13,
                },
                "bold": {
                    "parent": styles["h1"],
                    "fontSize": 9,
                    "spaceBefore": 0,
                    "spaceAfter": 0,
                    "leading": 10,
                },
                "link": {
                    "parent": styles["Normal"],
                    "textColor": colors.blue,
                },
                "centered": {
                    "parent": styles["Normal"],
                    "alignment": 1,
                },
                "right": {
                    "parent": styles["Normal"],
                    "alignment": 2,
                },
            },
        )

        self.add_styles(
            styles,
            **{
                "table_centered": {
                    "parent": styles["table_head"],
                    "alignment": 1,
                    "spaceBefore": 0,
                    "spaceAfter": 0,
                    "leading": 10,
                },
                "footer": {
                    "parent": styles["table_head"],
                    "alignment": 1,
                    "leading": 18,
                },
            },
        )
        self.add_styles(
            styles,
            **{
                "table_left": {"parent": styles["table_centered"], "alignment": 0},
                "small": {
                    "parent": styles["table_centered"],
                    "fontSize": 5,
                    "leading": 6,
                },
            },
        )

        location_table_one = TableStyle(
            [
                ("LINEBELOW", (1, 0), (-1, -1), 0.5, colors.black),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
        location_table_two = TableStyle(
            [
                ("LINEBELOW", (1, 0), (1, 0), 0.5, colors.black),
                ("LINEBELOW", (3, 0), (3, 0), 0.5, colors.black),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
        checklist_table = TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
        checklist_four_table = TableStyle(
            [
                ("SPAN", (1, 0), (2, 0)),
                ("SPAN", (3, 0), (4, 0)),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
        signature_table = TableStyle(
            [
                ("LINEBELOW", (0, 0), (0, 0), 0.5, colors.black),
                ("LINEBELOW", (0, 2), (0, 2), 0.5, colors.black),
                ("LINEBELOW", (2, 0), (2, 0), 0.5, colors.black),
                ("LINEBELOW", (2, 2), (2, 2), 0.5, colors.black),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
        serial_number_table = TableStyle([])

        setattr(
            styles,
            "table_styles",
            {
                "location_table_one": location_table_one,
                "location_table_two": location_table_two,
                "checklist_table": checklist_table,
                "checklist_four_table": checklist_four_table,
                "signature_table": signature_table,
                "serial_number_table": serial_number_table,
            },
        )

        return styles

    def get_checklist_table_kwargs(self):
        return {
            "style": self.table_styles["checklist_table"],
            "colWidths": (0.2 * inch, 0.2 * inch, None),
        }

    def format_text(self, text):
        return str(text.format(**self.variables))

    def table_left(self, text):
        return Paragraph(self.format_text(text), style=self.styles["table_left"])

    def table_centered(self, text):
        return Paragraph(self.format_text(text), style=self.styles["table_centered"])

    def normal_p(self, text):
        return Paragraph(self.format_text(text), self.styles["Normal"])

    def normal_b(self, text):
        return Paragraph(self.format_text(text), self.styles["bold"])

    def main_header(self):
        header_text = "RESNET HOME ENERGY RATING Standard Disclosure"
        return [Paragraph(header_text, style=self.styles["page_title"])]

    def location_info(self):
        for_homes = self.table_centered("For home(s) located at:")
        location = self.table_left("{location}")

        city_heading = self.table_centered("City:")
        city = self.table_left("{city}")
        state_heading = self.table_centered("State:")
        state = self.table_left("{state}")

        table_one_kwargs = {
            "style": self.table_styles["location_table_one"],
            "colWidths": (1.55 * inch, None),
        }
        table_two_kwargs = {
            "style": self.table_styles["location_table_two"],
            "colWidths": (0.45 * inch, 2.85 * inch, 0.52 * inch, None),
        }

        return [
            Table([[for_homes, location]], **table_one_kwargs),
            Table([[city_heading, city, state_heading, state]], **table_two_kwargs),
        ]

    def checklist_info(self):
        data = [
            (
                "one",
                "The Rater or Rater's employer is receiving a fee for providing the rating on this home.",
                [],
            ),
            (
                "two",
                "In addition to the rating, the Rater or Rater's employer has also provided the following consulting services for this home:",
                [
                    ("A", "Mechanical system design"),
                    ("B", "Moisture control or indoor air quality consulting"),
                    (
                        "C",
                        "Performance testing and/or commissioning other than required for the rating itself",
                    ),
                    ("D", "Training for sales or construction personnel"),
                    ("E", "Other (specify) {two_E_specify}"),
                ],
            ),
            (
                "three",
                "The Rater or Rater's employer is:",
                [
                    ("A", "The seller of this home or their agent"),
                    (
                        "B",
                        "The mortgagor for some portion of the financed payments on this home",
                    ),
                    (
                        "C",
                        "An employee, contractor or consultant of the electric and/or natural gas utility serving this home",
                    ),
                ],
            ),
            (
                "four",
                "The Rater or Rater's employer is a supplier or installer of products, which may include",
                self.checklist_four_table,
            ),
            (
                "five",
                """This home has been verified under the provisions of Chapter 6, Section 603 "Technical
                Requirements for Sampling" of the Mortgage Industry National Home Energy Rating Standard as
                set forth by the Residential Energy Services Network (RESNET).""",
                [],
            ),
        ]

        story = []
        for index, (variable_name, text, children) in enumerate(data, 1):
            table_data = [
                [
                    self.normal_p("%i." % index),
                    self.normal_p("[{%s}]" % variable_name),
                    self.normal_p(text),
                ]
            ]
            if isinstance(children, list):
                for child_index, (child_variable_name, child_text) in enumerate(children):
                    table_data.append(
                        [
                            self.normal_p("[{%s_%s}]" % (variable_name, child_variable_name)),
                            self.normal_p("%s." % string.ascii_uppercase[child_index]),
                            self.normal_p(child_text),
                        ]
                    )

            story.append(Table(table_data, **self.get_checklist_table_kwargs()))
            story.append(Spacer(0, 10))

            if callable(children):
                # Handles making sure checklist 4 table gets put after its heading.
                story.extend(children())

        return story

    def checklist_four_table(self):
        rater = lambda item, answer: self.normal_p("[{{{}_{}}}] Rater".format(item, answer))
        employer = lambda item, answer: self.normal_p("[{{{}_{}}}] Employer".format(item, answer))
        default = lambda item, text: [
            self.normal_p(text),
            rater(item, "rater_installed"),
            employer(item, "employer_installed"),
            rater(item, "rater_supplied"),
            employer(item, "employer_supplied"),
        ]

        data = [
            [
                self.normal_p(""),
                self.normal_b("Installed in this home by:"),
                self.normal_p(""),
                self.normal_b("OR Is in the business of:"),
                self.normal_p(""),
            ],
            default("supplier_hvac", "HVAC systems"),
            default("supplier_thermal", "Thermal insulation systems"),
            default("supplier_sealing", "Air sealing of envelope or duct systems"),
            default("supplier_windows", "Window or window shading systems"),
            default("supplier_appliances", "Energy efficient appliances"),
            default(
                "supplier_construction",
                "Construction (builder, developer, construction contractor, etc)",
            ),
            default("supplier_other", "Other (specify): {supplier_other_specify}"),
        ]

        return [
            Table(
                data,
                style=self.table_styles["checklist_four_table"],
                colWidths=(2.55 * inch, None, None, None, None),
            ),
            Spacer(0, 10),
        ]

    def signature_area(self):
        """
        Empty lines are for creating space for signatures.
        Middle column is to create space so Certification and Date
        don't bump up against the signature line.
        """
        if self.variables["signature_filepath"]:
            signature = Image(
                self.variables["signature_filepath"],
                0.2 * inch * self.variables["signature_width_ratio"],
                0.2 * inch,
            )
        else:
            signature = ""
        data = [
            [
                self.normal_p("{rater_of_record}"),
                "",
                self.normal_p("{rater_resnet_rtin}"),
            ],
            [
                self.normal_p("Rater's Printed Name"),
                "",
                self.normal_p("Certification #"),
            ],
            [
                signature,
                "",
                self.normal_p(
                    datetime.datetime.utcnow()
                    .replace(tzinfo=datetime.timezone.utc)
                    .strftime("%m/%d/%y")
                ),
            ],
            [self.normal_p("Rater's Signature"), "", self.normal_p("Date")],
        ]
        return [
            Table(
                data,
                rowHeights=[None, None, 0.35 * inch, None],
                style=self.table_styles["signature_table"],
            )
        ]

    def proclamation(self):
        serial_number_data = [
            [
                self.normal_p("AXIS-{serial_number}"),
                "",
                Paragraph("RESNET Form 03001-2", style=self.styles["right"]),
            ],
        ]
        return [
            self.normal_p(
                """
                I attest that the above information is true and correct to the best of my knowledge. As a Rater or
                Rating Provider I abide by the rating quality control provisions of the Mortgage Industry National
                Home Energy Rating Standard as set forth by the Residential Energy Services Network
                (RESNET). The national rating quality control provision of the rating standard are contained in
                Chapter One 4.C.8 of the standard and are posted at
            """
            ),
            Paragraph(
                """
                <a href="http://www.resnet.us/standards/RESNET_Mortgage_Industry_National_HERS_Standards.pdf">
                    http://www.resnet.us/standards/RESNET_Mortgage_Industry_National_HERS_Standards.pdf
                </a>
            """,
                style=self.styles["link"],
            ),
            Spacer(0, 10),
            Paragraph(
                """
                The Home Energy Rating Standard Disclosure for this home is available from the rating provider.
            """,
                style=self.styles["large_bold"],
            ),
            Table(serial_number_data, style=self.table_styles["serial_number_table"]),
        ]

    def build(self, obj, variables={}, *args, **kwargs):
        self._obj = obj
        self._variables = dict(variables)

        if isinstance(obj, EEPProgramHomeStatus):
            # Inspect the actual source company rather of the object so the variable inheritance
            # comes from the expected source.
            company = obj.company
        else:
            # Use the requesting user's company
            company = variables["company"]

        self._variables.update(flatten_inheritable_settings(company, obj))

        spacer = lambda: [Spacer(0, 10)]
        layout = [
            self.main_header,
            self.location_info,
            spacer,
            self.checklist_info,
            spacer,
            self.signature_area,
            spacer,
            self.proclamation,
        ]

        flowables = []
        for piece in layout:
            flowables.extend(piece())

        return super(StandardDisclosureFormPDF, self).build(
            obj, variables, flowables, *args, **kwargs
        )


# References
#    http://blogs.sitepointstatic.com/examples/tech/canvas-curves/bezier-curve.html
#    http://www.reportlab.com/docs/reportlab-userguide.pdf
#    http://www.reportlab.com/apis/reportlab/2.4/pdfgen.html#module-reportlab.pdfgen.canvas


if __name__ == "__main__":
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.get(id=212)
    stat = EEPProgramHomeStatus.objects.get(home_id=61574)
    HomeDetailReport(filename="home_status_report.pdf").build(stat, "home_status_report.pdf", user)
