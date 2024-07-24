"""EPS Report generator."""

# TODO: fix sizing for half bold info text under scales.
# TODO: better place text related to dynamic arrows to allow for more space underneath.
import logging
import os
import re

from django.core.exceptions import ObjectDoesNotExist
from localflavor.us.us_states import US_STATES
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from axis.checklist.collection.excel import ExcelChecklistCollector
from axis.core.checks import register_reportlab_fonts
from axis.core.pdfgen import AxisParagraph, AxisPath
from axis.customer_eto.calculator.eps.calculator import EPSCalculator
from axis.customer_eto.calculator.eps.utils import get_eto_calculation_completed_form
from axis.home.models import EEPProgramHomeStatus
from simulation.enumerations import FuelType

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

register_reportlab_fonts()

COMPANY_RE = re.compile(r"company", re.I)

VARIABLES = {
    # Page 1
    "estimated_monthly_energy_costs": "103",
    "estimated_average_annual_energy_cost": "1,233",
    "street_line": "312345 SE Example Street",
    "city": "Portland",
    "zipcode": "97215",
    "year": "2012",
    "square_footage": "1,799",
    "eps_issue_date": "4-17-12",
    "electric_utility": "NW Natural",
    "gas_utility": "Portland General Electric",
    "electric_per_month": "78",
    "natural_gas_per_month": "25",
    "energy_score": "59",
    "electric_kwhs": "9,234",
    "natural_gas_therms": "274",
    "electric_tons_per_year": "4.9",
    "natural_gas_tons_per_year": "1.6",
    # Page 2
    "insulated_ceiling": "R-49",
    "insulated_walls": "R-21",
    "insulated_floors": "R-38",
    "efficient_windows": "U-0.31",
    "efficient_lighting": "79%",
    "water_heater": "Tankless 0.93 EF",
    "space_heating": "92% AFUE Furnace",
    "envelope_tightness": "4.4 ACH @ 50Pa",
}
CLOUDS = [
    {"x": 3.06, "y": 8.77, "width": 0.73, "height": 0.22, "color": (77, 77, 79), "flip": False},
    {"x": 3.85, "y": 8.77, "width": 0.65, "height": 0.20, "color": (99, 100, 102), "flip": True},
    {"x": 4.55, "y": 8.77, "width": 0.58, "height": 0.17, "color": (119, 120, 123), "flip": False},
    {"x": 5.18, "y": 8.77, "width": 0.55, "height": 0.16, "color": (138, 140, 142), "flip": True},
    {"x": 5.78, "y": 8.77, "width": 0.53, "height": 0.15, "color": (157, 159, 161), "flip": False},
    {"x": 6.36, "y": 8.77, "width": 0.44, "height": 0.12, "color": (175, 177, 180), "flip": True},
    {"x": 6.85, "y": 8.77, "width": 0.36, "height": 0.10, "color": (192, 194, 196), "flip": False},
    {"x": 7.24, "y": 8.77, "width": 0.28, "height": 0.08, "color": (209, 211, 212), "flip": True},
]

# x, y form bottom left of image
PAGE_ONE_STATIC_IMAGES = [
    {
        "x": 0.39,
        "y": (0.37 + 1.68),
        "width": 1.59,
        "height": 1.68,
        "path": "../static/images/MainLogo.png",
    },
    {
        "x": 6.4,
        "y": 10.65,
        "width": 1.72,
        "height": 0.77,
        "path": "../static/images/BottomLogo.png",
    },
]
PAGE_TWO_STATIC_IMAGES = [
    PAGE_ONE_STATIC_IMAGES[0],
    {
        "x": 6.4,
        "y": 9.25,
        "width": 1.72,
        "height": 0.77,
        "path": "../static/images/BottomLogo.png",
    },
]

STATIC_ARROW_SHAPES = [
    {
        "x": 2,
        "y": 3.6,
        "width": 2.5,
        "height": 0.5,
        "text": "Estimated Monthly Energy Costs",
        "text_font": "Arial-Bold",
        "text_size": 11,
        "text_color": {"r": 1, "g": 1, "b": 1},
    },
    {
        "x": 1.43,
        "y": 6.48,
        "width": 1.37,
        "height": 0.5,
        "text": "Energy Score",
        "text_font": "Arial-Bold",
        "text_size": 11,
        "text_color": {"r": 1, "g": 1, "b": 1},
    },
]

COLORS = {
    "header_shape_fill": {"r": 0.3, "g": 0.3, "b": 0.3},
    "frames_stroke": {"r": 0.9, "g": 0.9, "b": 0.9},
    "arrow_shape_text": {"r": 1, "g": 1, "b": 1},
}
text_black = Color(0.3, 0.3, 0.3)
text_white = Color(1, 1, 1)

AXIS_PARAGRAPHS = [
    {
        "x": 4.25,
        "y": 1.66,
        "charSpace": 0.5,
        "alignment": "left",
        "valignment": "top",
        "font": "Arial",
        "size": 10,
        "color": text_white,
        "text": ["EPS is a tool to assess a home's energy", "cost and carbon footprint."],
    },
    {
        "x": 0.44,
        "y": 2.27,
        "charSpace": 0.3,
        "leading": 11,
        "font": "Arial",
        "size": 8,
        "color": text_black,
        "text": [
            "EPS™ is an energy performance score that measures and rates the net energy consumptions ",
            "and carbon footprint of a newly constructed home. The lower the score, the better — a low EPS",
            "identifies a home as energy efficient with a smaller carbon footprint and lower energy costs.",
        ],
    },
    {
        "x": 2,
        "y": 3.6,
        "price": True,
        "font": "Arial-Bold",
        "alignment": "center",
        "valignment": "top",
        "asterisk_offset": 50,
        "size": 90,
        "color": text_black,
        "charSpace": -6,
        "text": "{estimated_monthly_energy_costs}",
    },
    {
        "x": 3.88,
        "y": 4.04,
        "price": True,
        "font": "Arial-Bold",
        "alignment": "left",
        "valignment": "top",
        "asterisk_offset": 5,
        "size": 28,
        "color": text_black,
        "charSpace": -1,
        "text": "{estimated_average_annual_energy_cost}",
    },
    {
        "x": 1.44,
        "y": 6.49,
        "font": "Arial-Bold",
        "alignment": "center",
        "valignment": "top",
        "size": 90,
        "color": text_black,
        "charSpace": -3,
        "text": "{energy_score}",
    },
    {
        "x": 0.59,
        "y": 9.75,
        "font": "Arial-Bold",
        "size": 8,
        "alignment": "left",
        "valignment": "top",
        "color": text_black,
        "text": "*",
    },
    {
        "x": 0.63,
        "y": 9.75,
        "font": "Arial",
        "size": 8,
        "leading": 10,
        "alignment": "left",
        "valignment": "top",
        "color": text_black,
        "text": [
            "Actual energy costs may vary and are affected by many factors ",
            "such as occupant behavior, weather, utility rates and potential for ",
            "renewable energy generation. A home’s EPS takes into account the ",
            "energy-efficient features installed in the home on the date the EPS ",
            "was issued, but does not account for occupant behavior.",
        ],
    },
]

AXIS_PARAGRAPHS_TWO = [
    AXIS_PARAGRAPHS[0],
    {
        "x": 0.55,
        "y": 4.36,
        "font": "Arial-Bold",
        "size": 11,
        "alignment": "left",
        "valignment": "bottom",
        "color": text_black,
        "text": "What was considered in developing this score?",
    },
    {
        "x": 0.55,
        "y": 4.42,
        "font": "Arial",
        "size": 9,
        "leading": 11,
        "alignment": "left",
        "valignment": "top",
        "color": text_black,
        "text": [
            "A home's EPS is based on the energy-efficient features listed above as well as the home's size and specific design. Improvements",
            "and updates made to the home after the issue date will impact its EPS. EPS does not factor in occupant behavior, and as a result,",
            "actual energy costs may vary.",
        ],
    },
    {
        "x": 0.55,
        "y": 8.29,
        "font": "Arial-Bold",
        "size": 11,
        "alignment": "left",
        "valignment": "bottom",
        "color": text_black,
        "text": "Brought to you by Energy Trust of Oregon",
    },
    {
        "x": 0.55,
        "y": 8.34,
        "font": "Arial",
        "size": 9,
        "leading": 11,
        "alignment": "left",
        "valignment": "top",
        "color": text_black,
        "text": [
            "Energy Trust developed EPS to educate about energy efficiency",
            "and provide a tool to help inform home-buying decisions.",
        ],
    },
]
PAGE_ONE_TEXT_BLOCKS = [
    {
        "x": 0.67,
        "y": 4.83,
        "font": "Arial",
        "size": 8,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <b>Estimated average energy cost per month:</b>
            <font size=7.5>Electric ${electric_per_month}, Natural Gas ${natural_gas_per_month}</font><br />
            <font size=7.5>Estimated Energy Cost calculated using {kwh_cost} per kWh and {therm_cost} per therm</font>
        """,
    },
    {
        "x": 3.75,
        "y": 3.55,
        "font": "Arial-Bold",
        "size": 12,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
                <b>Estimated average <br/>
                annual energy costs:</b>
            """,
    },
    # PANEL 2
    {
        "x": 5.8,
        "y": 2.4,
        "width": 2.12,
        "style": "Normal",
        "font": "Arial-Bold",
        "size": 12,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
        <b>Location</b> <br/>
        {street_line} <br/>
        {city}, {state} {zipcode} <br/>
        <br/>

        <b>YEAR BUILT:</b> {year} <br/>
        <b>SQ. FOOTAGE:</b> {square_footage} <br/>
        <b>EPS ISSUE DATE:</b> {eps_issue_date} <br/>
        <b>RATED BY:</b> {rater} <br/>
        {rater_ccb}
        <br/>

        <b>Utilities:</b> <br/>
        Gas: {gas_utility} <br/>
        Electric: {electric_utility} <br/>
        """,
    },
    # PANEL 4
    {
        "x": 2.74,
        "y": 5.41,
        "width": 4,
        "style": "big",
        "font": "Arial",
        "size": 12,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """<b>ENERGY SCALE:</b>""",
    },
    {
        "x": 4.65,
        "y": 5.43,
        "width": 4,
        "style": "small",
        "font": "Arial",
        "size": 8,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <font size=7>Based on home energy use of natural  gas, electricity, or energy  <br />
            generated from an installed renewable system.</font>""",
    },
    {
        "x": 2.55,
        "y": 6.89,
        "width": 0.5,
        "style": "scale-info",
        "font": "Arial",
        "size": 6,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
        <font size=14><b>200+</b></font>
        <b>WORST</b>
        """,
    },
    {
        "x": 7.44,
        "y": 6.89,
        "width": 0.5,
        "style": "scale-info",
        "font": "Arial",
        "size": 6,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
        <font size=14><b>0</b></font> <br/>
        <b>BEST</b>
        """,
    },
    {
        "x": 2.69,
        "y": 7.45,
        "font": "Arial",
        "size": 6,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <b>Estimated total annual gross energy usage:</b> <font size=7.5>Electric (kWh): {electric_kwhs}, Natural Gas (therms): {total_natural_gas_therms}</font><br />
        """,
    },
    {
        "x": 2.69,
        "y": 7.63,
        "font": "Arial",
        "size": 6,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <b>Estimated average annual energy generation:</b> <font size=7.5>{solar}</font><br />
        """,
    },
    {
        "x": 2.69,
        "y": 7.81,
        "font": "Arial",
        "size": 6,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <b>Estimated average net energy usage:</b> <font size=7.5>Electric (kWh): {net_electric_kwhs}*, Natural Gas (therms): {natural_gas_therms}</font><br />
        """,
    },
    # PANEL 5
    {
        "x": 0.66,
        "y": 8.42,
        "width": 1.96,
        "style": "tiny",
        "font": "Arial",
        "size": 8,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <font size=12><b>CARBON FOOTPRINT:</b></font> <br/>
            Measured in tons of carbon dioxide <br/>
            per year (tons/yr). One ton ≈ 2,000 miles <br/>
            driven by one car (typical 21 mpg car). <br/>
        """,
    },
    {
        "x": 2.69,
        "y": 9.22,
        "font": "Arial",
        "size": 7,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <b>Estimated average carbon footprint:</b>
            <font size=6.75>Electric (tons/yr): {electric_tons_per_year},
            Natural gas (tons/yr): {natural_gas_tons_per_year}</font>
        """,
    },
    {
        "x": 7.5,
        "y": 8.44,
        "width": 0.5,
        "style": "scale-info",
        "font": "Arial",
        "size": 6,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
        <font size=14><b>0</b></font> <br/>
        tons/yr <br/>
        <b>BEST</b>
        """,
    },
]
PAGE_TWO_TEXT_BLOCKS = [
    {
        "x": 0.95,
        "y": 5.25,
        "width": 2.19,
        "height": 2.19,
        "style": "small",
        "font": "Arial",
        "size": 8,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <font size=9><b>Energy-efficient features</b></font> <br/>
            <b>R-Value:</b> Rates the efficiency of insulation;
            a higher R-Value signals improved performance of floor, ceiling and wall insulation.
            <br/>
            <br/>
            <b>U-Value:</b> Indicates the rate of heat loss in windows;
            a lower U-Value demonstrates the effectiveness of a window,
            resulting in a more comfortable home.
            <br/>
            <br/>
            <b>ACH @ 50Pa:</b> Total air changes per hour at 50 pascals;
            a low number signifies a properly-sealed home with fewer air leaks.
            <br/>
            <br/>
            <b>EF:</b> Energy Factor for water heaters or appliances;
            the higher the EF, the more energy efficient the model.
        """,
    },
    {
        "x": 3.47,
        "y": 5.25,
        "width": 2.19,
        "height": 2.19,
        "style": "small",
        "font": "Arial",
        "size": 8,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <font size=10><b>Energy Score</b></font> <br/>
            A home’s EPS is shown on an energy scale that ranges from zero to 200+
            and is based on home energy use of natural gas, electricity,
            or energy generated from an installed renewable system.
            <br/>
            <br/>
            <b>Carbon footprint: </b><br/>
            A home’s energy consumption affects carbon emissions and impacts
            the environment. The carbon calculation for EPS is based on
            emissions from the utility-specific electricity generation
            method and natural gas consumption of the home at
            the time of this report.
        """,
    },
    {
        "x": 5.91,
        "y": 5.25,
        "width": 2,
        "height": 2,
        "style": "small",
        "font": "Arial",
        "size": 8,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            <font size=10><b>Similar size {cond_state_long}home</b></font><br/>
            <b>Energy:</b> The energy consumption of
            an average {cond_state_long}home of similar
            square footage, heating type and
            geographical region.
            <br/>
            <br/>
            <b>Carbon:</b> The carbon footprint of an
            average {cond_state_long}home of similar
            square footage, heating type,
            geographical region and utility mix.
            <br/>
            <br/>
            <b>This home if built to code:</b>
            The estimated annual energy and
            carbon use for this home if it was just
            built to the minimum standards allowed
            under {cond_state_long}code at the time of
            construction without energy-efficient
            features installed.
        """,
    },
    {
        "x": 0.53,
        "y": 8.78,
        "width": 3.58,
        "style": "small-alt",
        "font": "Arial",
        "size": 8,
        "color": {"r": 0, "g": 0, "b": 0},
        "text": """
            For more information about EPS, contact Energy Trust at
            <b>1.866.368.7878</b> or visit <b>www.energytrust.org/eps</b>.
        """,
    },
]


class EPSLegacyReportGenerator:
    def __init__(self, *args, **kwargs):
        kwargs["filename"] = kwargs.get("filename", "/tmp/axis_pdf_report.pdf")  # nosec
        kwargs["leftMargin"] = kwargs.get("left_margin", kwargs.get("margins", 0.5 * inch))
        kwargs["rightMargin"] = kwargs.get("right_margin", kwargs.get("margins", 0.5 * inch))
        kwargs["topMargin"] = kwargs.get("top_margin", kwargs.get("margins", 0.5 * inch))
        kwargs["bottomMargin"] = kwargs.get("bottom_margin", kwargs.get("margins", 0.5 * inch))
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

    def _get_styles(self):
        log.debug("Setting up styles")
        styles = getSampleStyleSheet()
        styles["Normal"].textColor = (0.3, 0.3, 0.3)
        styles["Normal"].fontName = "Arial"

        styles.add(
            ParagraphStyle(name="centered", parent=styles["Normal"], alignment=1), "centered"
        )
        styles.add(
            ParagraphStyle(
                name="centered-white-bold",
                parent=styles["Normal"],
                alignment=1,
                textColor=(1, 1, 1),
                fontName="Arial-Bold",
            ),
            "centered-white-bold",
        )
        styles.add(
            ParagraphStyle(name="dark_background", parent=styles["Normal"], textColor=colors.white),
            "dark_background",
        )
        styles.add(
            ParagraphStyle(name="small", parent=styles["Normal"], fontSize=8, leading=9), "small"
        )
        styles.add(
            ParagraphStyle(name="small-alt", parent=styles["Normal"], fontSize=9, leading=11),
            "small-alt",
        )
        styles.add(
            ParagraphStyle(
                name="scale-info", parent=styles["Normal"], fontSize=6, alignment=1, leading=8
            ),
            "scale-info",
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
            ParagraphStyle(name="tiny", parent=styles["Normal"], fontSize=7, leading=8), "tiny"
        )
        styles.add(
            ParagraphStyle(name="tiny-bold", parent=styles["tiny"], fontName="Arial-Bold"),
            "tiny-bold",
        )
        styles.add(
            ParagraphStyle(
                name="tiny-bold-right", parent=styles["tiny"], fontName="Arial-Bold", alignment=2
            ),
            "tiny-bold-right",
        )
        styles.add(
            ParagraphStyle(name="footer", parent=styles["tiny"], fontSize=6, leading=8), "footer"
        )
        return styles

    def _x(self, x):
        return x

    def _y(self, y):
        return letter[1] - y

    def _rgb(self, r, g, b):
        red = r / 256
        green = g / 256
        blue = b / 256
        return red, green, blue

    def _map_range(self, from_range, to_range, value, constrain=True):
        """
        change value given a range to a number in a new range
        :param from_range: tuple of original range
        :param to_range: tuple of desired range
        :param value: number to transform
        """
        if constrain:
            min_number, max_number = sorted(from_range)
            try:
                value = max(min_number, min(max_number, value))
            except TypeError:
                print(f"{min_number!r}, {value!r}, {max_number!r}")
                raise

        (a1, a2), (b1, b2) = from_range, to_range
        return b1 + ((value - a1) * (b2 - b1) / (a2 - a1))

    def string_width(self, string, font, size, charSpace=0):
        width = self.canvas.stringWidth(string, font, size)
        width += (len(string) - 1) * charSpace
        return width

    def _draw_text(self, x, y, font, size, text, **kwargs):
        charSpace = kwargs.get("charSpace", 0)
        color = kwargs.get("color", Color(0, 0, 0))
        self.canvas.saveState()
        to = self.canvas.beginText()
        to.setTextOrigin(self._x(x * inch), self._y(y * inch))
        to.setFont(font, size)
        to.setCharSpace(charSpace)
        to.setFillColor(color)
        to.textLines(text)
        self.canvas.drawText(to)
        self.canvas.restoreState()

    def _draw_centered_text(self, x, y, font, size, text, **kwargs):
        charSpace = kwargs.get("charSpace", 0)
        color = kwargs.get("color", Color(0, 0, 0))

        self.canvas.saveState()

        self.canvas._charSpace = charSpace

        width = self.canvas.stringWidth(text, font, size)
        t = self.canvas.beginText(self._x(x * inch) - 0.5 * width, self._y(y * inch))
        t.setFont(font, size)
        t.setCharSpace(charSpace)
        t.setFillColor(color)
        t.textLines(text)
        self.canvas.drawText(t)
        self.canvas.restoreState()

    def _shape_header_block(self, **kwargs):
        self.canvas.saveState()
        self.canvas.setFillColorRGB(**COLORS["header_shape_fill"])
        self.canvas.setLineWidth(0.2)
        p = AxisPath()
        p.move(3.42, 1.54 + 0.51)
        p.line((3.42 + 0.82 - 0.1), (1.54 + 0.03))
        # Custom curve
        p.curve(3.42 + 0.82 - 0.1, 1.54 + 0.03, 3.42 + 0.82 - 0.05, 1.54, 3.42 + 0.82, 1.54)
        p.topRightArc((3.42 + 4.7), 1.54)
        p.line((3.42 + 4.7), (1.54 + 0.51))
        p.close()
        self.canvas.drawPath(p, stroke=0, fill=1)
        self.canvas.restoreState()

    def _shape_block_arrow(
        self,
        x,
        y,
        width,
        text,
        radius=5,
        height=0.7,
        flip=False,
        text_font="Arial",
        text_size=8,
        offset=0,
        **kwargs,
    ):
        """
        Draw shape from middle given width and height
        :param canvas: canvas object
        :param x: x coordinate bottom point in inches
        :param y: y coordinate bottom point in inches
        :param w: total width of shape in inches
        :param height: total height of shape in inches
        """
        self.canvas.saveState()
        full_height = height
        arrow_height = 0.3 * full_height
        original_y = y
        if flip is True:
            self.canvas.translate(0, letter[1])
            self.canvas.scale(1, -1)
            y = letter[1] / inch - y
            original_y += full_height + arrow_height
        r = radius / inch
        w = width

        original_x = x
        x += offset

        self.canvas.setFillColorRGB(0.3, 0.3, 0.3)
        self.canvas.setLineWidth(0.2)
        p = AxisPath()
        p.move(original_x, y)

        bottom_left_curve_x = x - (0.5 * w)
        bottom_left_curve_y = y - arrow_height
        p.curve(
            x - (0.45 * w),
            bottom_left_curve_y,
            bottom_left_curve_x,
            bottom_left_curve_y + (0.25 * r),
            bottom_left_curve_x,
            bottom_left_curve_y - r,
        )

        p.topLeftArc(x - (0.5 * w), y - full_height, radius)
        p.topRightArc(x + (0.5 * w), y - full_height, radius)

        bottom_right_curve_x = x + (0.5 * w)
        bottom_right_curve_y = y - arrow_height
        p.line(bottom_right_curve_x, bottom_right_curve_y - r)
        p.curve(
            bottom_right_curve_x,
            bottom_right_curve_y + (0.25 * r),
            x + (0.45 * w),
            bottom_right_curve_y,
            original_x,
            y,
        )

        p.close()
        self.canvas.drawPath(p, stroke=1, fill=1)
        self.canvas.restoreState()

        text_y = original_y - (0.5 * full_height)
        self._draw_centered_text(x, text_y, text_font, text_size, text, color=Color(1, 1, 1))

    def _static_images(self, path, x, y, width, height, **kwargs):
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        self.canvas.drawImage(
            image_path,
            self._x(x * inch),
            self._y(y * inch),
            width=width * inch,
            height=height * inch,
            preserveAspectRatio=True,
        )

    def _text_block(self, x, y, text, width=6.0, height=letter[1], **kwargs):
        text = text.format(**self.home)
        style = self.styles["Normal"]
        if kwargs.get("style"):
            style = self.styles[kwargs.get("style")]
        p = Paragraph(text, style=style)
        width, height = p.wrapOn(self.canvas, width * inch, height)
        p.drawOn(self.canvas, self._x(x * inch), self._y(y * inch) - height)

    def _page_one_frames(self, **kwargs):
        self.canvas.setStrokeColorRGB(**COLORS["frames_stroke"])
        self.canvas.setLineWidth(2)
        p = AxisPath()
        p.move(self.left_margin, 5)
        p.topLeftArc(self.left_margin, 2.8)
        p.line(5.62, 2.8)
        p.topLeftArc(5.62, 2.2)
        p.topRightArc(self.right_margin, 2.2)
        p.bottomRightArc(self.right_margin, 9.5)
        p.line(4.1, 9.5)
        p.bottomRightArc(4.1, 10.6)
        p.bottomLeftArc(self.left_margin, 10.6)
        p.close()
        self.canvas.drawPath(p, stroke=1)

        p = AxisPath()
        p.move(self.left_margin, 5.3)
        p.line(self.right_margin, 5.3)
        p.move(self.left_margin, 8.1)
        p.line(self.right_margin, 8.1)
        p.move(self.left_margin, 9.5)
        p.line(self.right_margin - 3, 9.5)
        p.move(5.62, 2.8)
        p.line(5.62, 5.3)
        self.canvas.drawPath(p, stroke=1)

        # dotted lines
        self.canvas.saveState()
        p = AxisPath()
        self.canvas.setDash(0.1, 4)
        self.canvas.setStrokeColorRGB(0.3, 0.3, 0.3)
        self.canvas.setLineCap(1)
        p.move(2.4, 5.68)
        p.line(2.4, 7.76)
        p.move(3.56, 3.19)
        p.line(3.56, 4.57)
        self.canvas.drawPath(p, stroke=1)
        self.canvas.restoreState()

    def _page_two_frames(self, **kwargs):
        self.canvas.setStrokeColorRGB(**COLORS["frames_stroke"])
        self.canvas.setFillColorRGB(**COLORS["frames_stroke"])
        self.canvas.setLineWidth(2)
        p = AxisPath()
        p.move(self.left_margin, 3)
        p.topLeftArc(self.left_margin, 2.21)
        p.topRightArc(self.right_margin, 2.21)
        p.bottomRightArc(self.right_margin, 3.76)
        p.bottomLeftArc(self.left_margin, 3.76)
        p.close()
        self.canvas.drawPath(p, stroke=1, fill=1)

        # Frame
        p = AxisPath()
        p.move(self.left_margin, 5.04)
        p.topLeftArc(self.left_margin, 4.02)
        p.topRightArc(self.right_margin, 4.02)
        p.bottomRightArc(self.right_margin, 7.9)
        p.line(4.36, 7.9)
        p.bottomRightArc(4.36, 9.29)
        p.bottomLeftArc(self.left_margin, 9.29)
        p.close()
        self.canvas.drawPath(p, stroke=1, fill=0)

        # Lines
        p = AxisPath()
        p.move(self.left_margin, 5.04)
        p.line(self.right_margin, 5.04)
        p.move(self.left_margin, 7.9)
        p.line(5, 7.9)
        self.canvas.drawPath(p, stroke=1, fill=0)

        # dotted lines
        self.canvas.saveState()
        p = AxisPath()
        self.canvas.setDash(0.1, 4)
        self.canvas.setStrokeColorRGB(0.3, 0.3, 0.3)
        self.canvas.setLineCap(1)
        p.move(3.33, 5.57)
        p.line(3.33, 7.53)
        p.move(5.76, 5.57)
        p.line(5.76, 7.53)
        self.canvas.drawPath(p, stroke=1, fill=0)
        self.canvas.restoreState()

        # extra only here
        # height is negative because it's going from the bottom up
        self.canvas.rect(
            self._x(self.left_margin * inch),
            self._y(5.04 * inch),
            0.4 * inch,
            -2.86 * inch,
            stroke=1,
            fill=1,
        )
        self.canvas.saveState()
        self.canvas.rotate(90)
        self.canvas.setFillColorRGB(0.3, 0.3, 0.3)
        self.canvas.setFont("Arial", 10)
        self.canvas.drawString(self._y(7.34 * inch), -0.65 * inch, "USEFUL TERMINOLOGY")
        self.canvas.restoreState()

    def _page_two_footer(self):
        self.canvas.saveState()
        self.canvas.setFillColor(Color(0.3, 0.3, 0.3))
        self.canvas.setStrokeColor(Color(0.3, 0.3, 0.3))
        self.canvas.rect(
            self._x(0.55 * inch), self._y(10.06 * inch), 7.51 * inch, 0.07 * inch, stroke=1, fill=1
        )
        style = self.styles["tiny"]
        style.leftIndent = 0
        data = [
            [
                Paragraph("<b>Energy Trust of Oregon</b>", style=style),
                Paragraph("421 SW Oak St, Suite 300, Portland, Oregon 97204", style=style),
                Paragraph("1.866.368.7878", style=style),
                Paragraph("<b>energytrust.org</b>", style=style),
            ]
        ]
        t = Table(data, colWidths=[1.9 * inch, 3 * inch, 1.9 * inch])
        width, height = t.wrapOn(self.canvas, 8, 11)
        t.drawOn(self.canvas, self._x(0.47 * inch), self._y(9.7 * inch) - height)
        footer_text = """
            Energy Trust of Oregon is an independent nonprofit organization dedicated to helping
            utility customers benefit from saving energy and tapping renewable resources.
            Our services, cash incentives and energy solutions have helped participating customers
            of Portland General Electric, Pacific Power, NW Natural, Cascade Natural Gas and Avista
            save on energy costs. Our work helps keep energy costs as low as possible,
            creates jobs and builds a sustainable energy future. 1/18
        """
        style = self.styles["footer"]
        style.leading = 10
        p = Paragraph(footer_text, style=style)
        width, height = p.wrapOn(self.canvas, 7.51 * inch, 11 * inch)
        p.drawOn(self.canvas, self._x(0.55 * inch), self._y(10.2 * inch) - height)
        self.canvas.restoreState()

    def _draw_tables(self):
        header = "<b>+ Energy-efficient features that contribute to this home's score:</b>"
        style = self.styles["big"]
        p = Paragraph(header, style=style)
        p.wrapOn(self.canvas, 9 * inch, 1 * inch)
        p.drawOn(self.canvas, self._x(0.52 * inch), self._y(2.5 * inch))
        string = """
            [Insulated Ceiling: {insulated_ceiling}, Efficient Windows: {efficient_windows}, Space Heating: {space_heating}],
            [Insulated Walls: {insulated_walls}, Efficient Lighting: {efficient_lighting}, Envelope Tightness: {envelope_tightness}],
            [Insulated Floors: {insulated_floors}, Water Heater: {water_heater}, ]
        """.format(
            **self.home
        )
        strs = string.replace("[", "").split("],")
        data = [list(map(str, s.replace("]", "").split(","))) for s in strs]

        t = Table(data, rowHeights=0.25 * inch)
        t.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Arial-Bold"),
                    ("TEXTCOLOR", (0, 0), (-1, -1), (0.3, 0.3, 0.3)),
                ]
            )
        )
        t.wrapOn(self.canvas, 8, 11)
        t.drawOn(self.canvas, self._x(self.left_margin * inch), self._y(3.5 * inch))

    def _green_triangle(self, x, y, width, height):
        """Draw the green triangle for measuring schtuff"""
        self.canvas.saveState()
        p = AxisPath()
        p.move(x, y)
        p.line(x, y - height)
        p.line(x + width, y)
        p.close()
        self.canvas.clipPath(p, stroke=0, fill=1)
        self.canvas.linearGradient(
            x * inch,
            y * inch,
            (x + width) * inch,
            y * inch,
            ((self._rgb(159, 209, 147)), self._rgb(46, 98, 61)),
            extend=False,
        )
        p = AxisPath()
        self.canvas.setStrokeColorRGB(1, 1, 1)
        self.canvas.setLineWidth(1)
        self.canvas.setDash(2, 2)
        p.move(x + (0.25 * width), y)
        p.line(x + (0.25 * width), y - 0.055)
        p.move(x + (0.25 * width), y - 0.17)
        p.line(x + (0.25 * width), y - height)
        p.move(x + (0.5 * width), y)
        p.line(x + (0.5 * width), y - 0.055)
        p.move(x + (0.5 * width), y - 0.17)
        p.line(x + (0.5 * width), y - height)
        p.move(x + (0.75 * width), y)
        p.line(x + (0.75 * width), y - 0.055)
        p.move(x + (0.75 * width), y - 0.17)
        p.line(x + (0.75 * width), y - height)
        self.canvas.setFillColorRGB(1, 1, 1)
        self.canvas.setFont("Arial", 8)
        self.canvas.drawCentredString(
            self._x((x + (0.25 * width)) * inch), self._y((y - 0.06) * inch), "150"
        )
        self.canvas.drawCentredString(
            self._x((x + (0.5 * width)) * inch), self._y((y - 0.06) * inch), "100"
        )
        self.canvas.drawCentredString(
            self._x((x + (0.75 * width)) * inch), self._y((y - 0.06) * inch), "50"
        )
        self.canvas.drawPath(p, stroke=1, fill=1)
        self.canvas.restoreState()

    def _shape_cloud(self, x, y, width, height, color, flip=False, **kwargs):
        self.canvas.saveState()
        p = AxisPath()
        # point 1 - begninning
        p.move(x, y)

        section_width = 0.25 * width

        point_two_x = (x + section_width) - 0.03
        point_two_y = y - (0.5 * height)

        # point 2
        p.curve(
            x - (0.25 * section_width),
            point_two_y + (0.1 * height),
            x + (0.3 * section_width),
            point_two_y - (0.2 * height),
            point_two_x,
            point_two_y,
        )

        point_three_x = (x + (2 * section_width)) - 0.02
        point_three_y = y - height

        # point 3
        if flip is True:
            point_three_x += 0.04
            p.curve(
                point_two_x - (0.1 * section_width),
                point_three_y,
                point_two_x + (0.7 * section_width),
                point_three_y - (0.5 * height),
                point_three_x,
                point_three_y,
            )
        else:
            p.curve(
                point_two_x - (0.1 * section_width),
                point_three_y,
                point_two_x + (0.5 * section_width),
                point_three_y - (0.25 * height),
                point_three_x,
                point_three_y,
            )

        point_four_x = (x + (3 * section_width)) + 0.03
        point_four_y = y - (0.5 * height)

        # point 4
        if flip is True:
            p.curve(
                point_three_x + (0.5 * section_width),
                point_three_y - (0.25 * height),
                point_four_x + (0.1 * section_width),
                point_three_y,
                point_four_x,
                point_four_y,
            )
        else:
            p.curve(
                point_three_x + (0.7 * section_width),
                point_three_y - (0.5 * height),
                point_four_x + (0.1 * section_width),
                point_three_y,
                point_four_x,
                point_four_y,
            )

        # point 5 - end
        p.curve(
            point_four_x + (0.7 * section_width),
            point_four_y - (0.2 * height),
            (x + width) + (0.25 * section_width),
            point_four_y + (0.1 * height),
            x + width,
            y,
        )

        p.close()
        self.canvas.setFillColorRGB(*self._rgb(*color))
        self.canvas.drawPath(p, stroke=0, fill=1)
        self.canvas.restoreState()

    def _dynamic_arrows(self):
        number_font = "Arial-Bold"
        carbon_scale_max = 30
        scale_text = {
            "x": 2.6,
            "y": 8.44,
            "width": 0.5,
            "style": "scale-info",
            "font": "Arial",
            "size": 6,
            "color": {"r": 0, "g": 0, "b": 0},
            "text": """
            <font size=14><b>{carbon_scale_max}+</b></font> <br/>
            tons/yr <br/>
            <b>WORST</b>
            """,
        }

        # x = self._map_range((200, 0), (3.06, 7.43), self.home['energy_score'])
        # Green shape
        width = 0.25
        height = 0.28
        MIN_SPACE_VAL = 0.06
        energy_score = self.home["energy_consumption_score"]
        similar_home = self.home["energy_consumption_similar_home"]
        built_to_code = self.home["energy_consumption_to_code"]

        # energy_score = 190
        # similar_home = 180
        # built_to_code = 120

        carbon_similar_home = self.home["carbon_footprint_similar_home"]
        carbon_built_to_code = self.home["carbon_footprint_to_code"]

        # carbon_similar_home = 21
        # carbon_built_to_code = 20

        show_similar_home = True
        if similar_home < built_to_code:
            show_similar_home = False
        if carbon_similar_home < carbon_built_to_code:
            show_similar_home = False

        energy_home_y = self._map_range((200, 0), (7 - 0.8034, 7), energy_score)
        # 30 is the last time the text won't interfere with the scales reference text
        energy_home_text_y = self._map_range((200, 30), (6.08, 7), energy_score)
        energy_home_x = self._map_range((200, 0), (3.06, 3.06 + 4.2607), energy_score)
        energy_similar_home_x = self._map_range((200, 0), (3.06, 3.06 + 4.2607), similar_home)
        energy_built_to_code_x = self._map_range((200, 0), (3.06, 3.06 + 4.2607), built_to_code)

        distance = abs(energy_similar_home_x - energy_built_to_code_x)
        energy_similar_home_offset = energy_built_to_code_offset = offset = 0
        if distance < width and show_similar_home:
            min_sep = width + MIN_SPACE_VAL
            offset = (min_sep - distance) / 2
            # log.warning("Top: dx:{} w:{} min:{} off:{}".format(distance, width, min_sep, offset))

        if energy_built_to_code_x >= energy_similar_home_x:
            energy_similar_home_text_offset = -3.7
            similar_home_style = "tiny-bold-right"
            energy_similar_home_offset *= -1
            energy_similar_home_x -= offset
            if abs(similar_home - built_to_code) > 50 and similar_home > 160:
                log.warning("Top end similar_home - Swap side there appears to be room")
                energy_similar_home_text_offset = 0.75
                similar_home_style = "tiny-bold"
                energy_similar_home_offset *= -1
                energy_similar_home_x += 2 * offset

            energy_built_to_code_text_offset = 0.75
            built_to_code_style = "tiny-bold"
            energy_similar_home_offset *= -1
            energy_built_to_code_x += offset
            if abs(similar_home - built_to_code) > 50 and built_to_code < 40:
                log.warning("Bottom end built_to_code - Swap side there appears to be room")
                energy_built_to_code_text_offset = -3.7
                built_to_code_style = "tiny-bold-right"
                energy_built_to_code_offset *= -1
                energy_built_to_code_x -= 2 * offset

        else:
            energy_built_to_code_text_offset = -3.7
            built_to_code_style = "tiny-bold-right"
            energy_built_to_code_offset *= -1
            energy_built_to_code_x -= offset
            if abs(similar_home - built_to_code) > 50 and built_to_code > 160:
                log.warning("1 - Top end similar_home - Swap side there appears to be room")
                energy_built_to_code_text_offset = 0.75
                built_to_code_style = "tiny-bold"
                energy_similar_home_offset *= -1
                energy_built_to_code_x += 2 * offset

            energy_similar_home_text_offset = 0.75
            similar_home_style = "tiny-bold"
            energy_similar_home_x += offset
            if abs(similar_home - built_to_code) > 50 and similar_home < 40:
                log.warning("1 - Bottom end built_to_code - Swap side there appears to be room")
                energy_similar_home_text_offset = -3.7
                similar_home_style = "tiny-bold-right"
                energy_similar_home_offset *= -1
                energy_similar_home_x -= 2 * offset

        # top arrow
        self._shape_block_arrow(
            energy_home_x,
            energy_home_y,
            width,
            str(energy_score),
            text_font=number_font,
            height=height,
            radius=2,
        )

        text_offset_x, text_offset_y = 0, 0
        # if energy_score <= 30:
        #     text_offset_y -= self._map_range((0, 30), (.055, 0.25), energy_score)
        #     text_offset_x -= self._map_range((0, 30), (.7, .5), energy_score)

        self._text_block(
            energy_home_x + (0.75 * width) + text_offset_x,
            energy_home_text_y - height + text_offset_y,
            "This home's <br/> energy score",
            style="tiny-bold",
        )
        # similar home
        if show_similar_home:
            self._shape_block_arrow(
                energy_similar_home_x,
                7.01,
                width,
                str(similar_home),
                text_font=number_font,
                height=height,
                radius=2,
                flip=True,
                offset=energy_similar_home_offset,
            )
            self._text_block(
                energy_similar_home_x
                + (energy_similar_home_text_offset * width)
                + energy_similar_home_offset,
                7.06,
                "Similar size <br/> {cond_state_long}home".format(**self.home),
                style=similar_home_style,
                width=0.75,
            )
        # built to code
        self._shape_block_arrow(
            energy_built_to_code_x,
            7.01,
            width,
            str(built_to_code),
            text_font=number_font,
            height=height,
            radius=2,
            flip=True,
            offset=energy_built_to_code_offset,
        )
        self._text_block(
            energy_built_to_code_x
            + (energy_built_to_code_text_offset * width)
            + energy_built_to_code_offset,
            7.06,
            "This home if <br/> built to code",
            style=built_to_code_style,
            width=0.75,
        )

        # Clouds
        carbon_footprint = self.home["carbon_footprint_score"]
        similar_home = self.home["carbon_footprint_similar_home"]
        built_to_code = self.home["carbon_footprint_to_code"]

        # carbon_footprint = 6.3
        # similar_home = 9.2
        # built_to_code = 9.2001

        self.home["carbon_scale_max"] = carbon_scale_max
        self._text_block(**scale_text)

        carbon_home_y = self._map_range((carbon_scale_max, 0), (8.48, 8.68), carbon_footprint)
        carbon_home_x = self._map_range((carbon_scale_max, 0), (3.06, 7.52), carbon_footprint)
        carbon_similar_home_x = self._map_range((carbon_scale_max, 0), (3.06, 7.52), similar_home)
        carbon_built_to_code_x = self._map_range((carbon_scale_max, 0), (3.06, 7.52), built_to_code)

        # if arrows are closer than width of the arrows
        distance = abs(carbon_similar_home_x - carbon_built_to_code_x)
        carbon_similar_home_offset = carbon_built_to_code_offset = offset = 0
        if distance <= width and show_similar_home:
            min_sep = width + MIN_SPACE_VAL
            offset = (min_sep - distance) / 2
            # log.warning("Lower: dx:{} w:{} min:{} off:{}".format(distance, width, min_sep, offset))

        swap = not show_similar_home and built_to_code > 20
        if carbon_built_to_code_x >= carbon_similar_home_x or swap:
            # built to code is to the right
            carbon_similar_home_offset *= -1
            carbon_similar_home_text_offset = -3.7
            similar_home_style = "tiny-bold-right"
            carbon_built_to_code_text_offset = 0.75
            built_to_code_style = "tiny-bold"
            carbon_built_to_code_x += offset
            carbon_similar_home_x -= offset
        else:
            carbon_built_to_code_offset *= -1
            carbon_similar_home_text_offset = 0.75
            similar_home_style = "tiny-bold"
            carbon_built_to_code_text_offset = -3.7
            built_to_code_style = "tiny-bold-right"
            carbon_built_to_code_x -= offset
            carbon_similar_home_x += offset

        # top arrow
        self._shape_block_arrow(
            carbon_home_x,
            carbon_home_y,
            width,
            str(carbon_footprint),
            text_font=number_font,
            height=height,
            radius=2,
        )
        self._text_block(
            carbon_home_x + (-4.7 * width),
            carbon_home_y - height,
            "This home's <br/> carbon footprint",
            style="tiny-bold-right",
            width=1,
        )
        # similar home
        if show_similar_home:
            self._shape_block_arrow(
                carbon_similar_home_x,
                8.77,
                width,
                str(similar_home),
                text_font=number_font,
                height=height,
                radius=2,
                flip=True,
                offset=carbon_similar_home_offset,
            )
            self._text_block(
                carbon_similar_home_x
                + (carbon_similar_home_text_offset * width)
                + carbon_similar_home_offset,
                8.83,
                "Similar size <br/> {cond_state_long}home".format(**self.home),
                style=similar_home_style,
                width=0.75,
            )

        # built to code
        self._shape_block_arrow(
            carbon_built_to_code_x,
            8.77,
            width,
            str(built_to_code),
            text_font=number_font,
            height=height,
            radius=2,
            flip=True,
            offset=carbon_built_to_code_offset,
        )
        self._text_block(
            carbon_built_to_code_x
            + (carbon_built_to_code_text_offset * width)
            + carbon_built_to_code_offset,
            8.83,
            "This home if <br/> built to code",
            style=built_to_code_style,
            width=0.75,
        )

    def generate_page_one(self, **kwargs):
        self._page_one_frames()
        self._shape_header_block()
        paragraphs = AXIS_PARAGRAPHS
        for text in paragraphs:
            a = AxisParagraph(canvas=self.canvas, **text)
            a.format_text(self.home)
            a.draw()
        self._green_triangle(3.06, 7.00, 4.2607, 0.8034)
        for shape in STATIC_ARROW_SHAPES:
            self._shape_block_arrow(**shape)
        for text in PAGE_ONE_TEXT_BLOCKS:
            self._text_block(**text)
        for image in PAGE_ONE_STATIC_IMAGES:
            self._static_images(**image)
        for cloud in CLOUDS:
            self._shape_cloud(**cloud)
        self._dynamic_arrows()
        self.canvas.setFillColorRGB(*self._rgb(53, 180, 89))
        self.canvas.rect(
            4.25 * inch, self._y(9.95 * inch), 1.25 * inch, 0.28 * inch, fill=1, stroke=0
        )
        self._text_block(
            4.25, 9.72, self.home["floorplan_type"], width=1.25, style="centered-white-bold"
        )
        # self._text_block(4.25, 9.72, "OFFICIAL", width=1.25, style='centered-white-bold')

    def generate_page_two(self, **kwargs):
        self._page_two_frames()
        self._shape_header_block()
        for text in PAGE_TWO_TEXT_BLOCKS:
            self._text_block(**text)
        for image in PAGE_TWO_STATIC_IMAGES:
            self._static_images(**image)
        for text in AXIS_PARAGRAPHS_TWO:
            a = AxisParagraph(canvas=self.canvas, **text)
            a.format_text(self.home)
            a.draw()
        self._draw_tables()
        self._page_two_footer()

    def set_calculator_variables(self, home_stat, calculator_data):  # noqa: C901
        from axis.customer_eto.reports.legacy_utils import get_legacy_calculation_data

        if hasattr(home_stat, "fasttracksubmission") and home_stat.fasttracksubmission.is_locked():
            log.debug("Using FastTrack Stored Data")
            data = {}
            for k, v in home_stat.fasttracksubmission.__dict__.items():
                if k.startswith("_"):
                    continue
                if k == "id":
                    k = "fasttracksubmission_id"
                data[k] = v
        else:
            log.debug("Calculating Data")
            data = get_legacy_calculation_data(
                home_stat, return_fastrack_data=True, return_errors=True
            )

        is_2015 = home_stat.eep_program.slug == "eto-2015"
        is_2016 = home_stat.eep_program.slug == "eto-2016"
        is_2017 = home_stat.eep_program.slug == "eto-2017"
        is_2018 = home_stat.eep_program.slug == "eto-2018"
        is_2019 = home_stat.eep_program.slug == "eto-2019"
        is_2020 = home_stat.eep_program.slug == "eto-2020"

        simulation, sim_year_built, sim_conditioned_area = None, "1900", 0.0
        if hasattr(home_stat, "floorplan") and hasattr(home_stat.floorplan, "simulation"):
            if home_stat.floorplan.simulation is not None:
                simulation = home_stat.floorplan.simulation
                sim_year_built = simulation.project.construction_year
                sim_conditioned_area = simulation.conditioned_area

        if is_2015 or is_2016 or is_2017 or is_2018 or is_2019:
            if hasattr(home_stat, "floorplan") and hasattr(home_stat.floorplan, "remrate_target"):
                if home_stat.floorplan.remrate_target is not None:
                    simulation = home_stat.floorplan.remrate_target
                    sim_year_built = simulation.building.building_info.year_built
                    sim_conditioned_area = simulation.building.building_info.conditioned_area

        _calculator = EPSCalculator(**calculator_data)
        results = _calculator.report_data()
        improved_data = results.get("improved_input")
        calculations = results.get("calculations")
        result = results.get("result")

        # import json
        # print(json.dumps(results, indent=4))

        electric_utility = home_stat.get_electric_company()
        if electric_utility:
            electric_utility = COMPANY_RE.sub(r"", "{}".format(electric_utility)).strip()
        else:
            electric_utility = ""

        gas_utility = home_stat.get_gas_company()
        if gas_utility:
            gas_utility = COMPANY_RE.sub(r"", "{}".format(gas_utility)).strip()
        else:
            gas_utility = ""

        rater = COMPANY_RE.sub(r"", "{}".format(home_stat.company)).strip()
        try:
            ccb = home_stat.company.eto_account.ccb_number
        except ObjectDoesNotExist:
            ccb = "--"
        rater_ccb = "<b>CCB #:</b> {} <br/>".format(ccb) if home_stat.home.state == "OR" else ""

        try:
            electric_cost = improved_data.get("electric_cost") / 12.0
        except (TypeError, ZeroDivisionError):
            electric_cost = 0

        try:
            gas_cost = improved_data.get("gas_cost") / 12.0
        except (TypeError, ZeroDivisionError):
            gas_cost = 0

        _solar = []
        solar_kwh = improved_data.get("solar_hot_water_kwh") + improved_data.get("pv_kwh")
        solar_therms = improved_data.get("solar_hot_water_therms")
        if solar_kwh:
            _solar.append("Electric (kWh): {:,}".format(int(round(solar_kwh, 0))))
        if solar_therms:
            _solar.append("Natural gas (therms): {:,}".format(int(round(solar_therms, 0))))
        solar = ", ".join(_solar) if len(_solar) else "No system"

        improved_total_kwh = calculations.get("improved", {}).get("total_kwh")
        if is_2015 or is_2016 or is_2017 or is_2018 or is_2019 or improved_total_kwh is None:
            improved_total_kwh = improved_data.get("total_kwh")

        improved_total_therms = calculations.get("improved", {}).get("total_therms")
        if is_2015 or is_2016 or is_2017 or is_2018 or is_2019 or improved_total_therms is None:
            improved_total_therms = improved_data.get("total_therms")

        net_electric_kwhs = improved_total_kwh - solar_kwh
        total_electric_kwhs = solar_kwh + improved_total_kwh
        total_natural_gas_therms = solar_therms + improved_total_therms

        address_bits = home_stat.home.get_home_address_display_parts(
            **{
                "company": self.user.company,
                "include_city_state_zip": True,
            }
        )

        state_long = dict(US_STATES).get(address_bits.state)
        cond_state = ""
        cond_state_long = ""
        if address_bits.state == "OR":
            cond_state = address_bits.state + " "
            cond_state_long = state_long + " "

        data = {
            "home_stat": home_stat,
            "street_line": address_bits.street_line1,
            "city": address_bits.city,
            "state": address_bits.state,
            "state_long": state_long,
            "cond_state": cond_state,
            "cond_state_long": cond_state_long,
            "zipcode": address_bits.zipcode,
            "rater": rater,
            "rater_ccb": rater_ccb,
            # Page 1
            "estimated_monthly_energy_costs": "{:,}".format(
                max([int(round(data["estimated_monthly_energy_costs"], 0)), 0])
            ),
            "estimated_average_annual_energy_cost": "{:,}".format(
                max([int(round(data["estimated_annual_energy_costs"], 0)), 0])
            ),
            "year": sim_year_built,
            "square_footage": "{:,}".format(int(round(sim_conditioned_area, 0))),
            "eps_issue_date": home_stat.certification_date,  # ???
            "electric_utility": electric_utility,  # From 640S
            "gas_utility": gas_utility,  # From 640S
            "electric_per_month": "{:,}".format(max([int(round(electric_cost, 0)), 0])),  #
            "natural_gas_per_month": "{:,}".format(max([int(round(gas_cost, 0)), 0])),  #
            "kwh_cost": "0.xx",  # "{:,}".format(max([int(round(electric_cost, 0)), 0])),
            "therm_cost": "0.xx",  # "{:,}".format(max([int(round(gas_cost, 0)), 0])),
            "solar": solar,
            "energy_score": int(round(data["eps_score"], 0)),  #
            "net_electric_kwhs": "{:,}".format(int(round(net_electric_kwhs, 0))),  #
            "electric_kwhs": "{:,}".format(max([int(round(improved_total_kwh, 0)), 0])),  #
            "natural_gas_therms": "{:,}".format(max([int(round(improved_total_therms, 0)), 0])),  #
            "total_electric_kwhs": "{:,}".format(int(round(total_electric_kwhs, 0))),
            "total_natural_gas_therms": "{:,}".format(int(round(total_natural_gas_therms, 0))),
            "electric_tons_per_year": "{:,}".format(
                max([round(result.get("total_electric_carbon"), 1), 0])
            ),  #
            "natural_gas_tons_per_year": "{:,}".format(
                max([round(result.get("total_gas_carbon"), 1), 0])
            ),  #
            # Page 2 = False #
            "insulated_ceiling": "",
            "insulated_walls": "",
            "insulated_floors": "",
            "efficient_windows": "",
            "efficient_lighting": "",
            "water_heater": "",
            "space_heating": "",
            "envelope_tightness": "",
            "energy_consumption_score": int(round(result.get("eps_score"), 0)),
            "energy_consumption_similar_home": int(round(data["similar_size_eps_score"], 0)),
            "energy_consumption_to_code": int(round(data["eps_score_built_to_code_score"], 0)),
            "carbon_footprint_score": round(data["carbon_score"], 1),
            "carbon_footprint_similar_home": round(data["similar_size_carbon_score"], 1),
            "carbon_footprint_to_code": round(data["carbon_built_to_code_score"], 1),
        }

        if simulation and home_stat.certification_date is not None:
            data["floorplan_type"] = "OFFICIAL"
        else:
            data["floorplan_type"] = "PRELIMINARY"

        if address_bits.street_line2:
            data["street_line"] += "<br/>{}".format(address_bits.street_line2)

        context = {"user__company": home_stat.company}
        self.collector = ExcelChecklistCollector(home_stat.collection_request, **context)
        instruments = self.collector.get_instruments()
        instrument_lookup = {i.measure_id: i for i in instruments}

        def _get_answer(measure):
            instrument = instrument_lookup.get(measure)
            if instrument:
                return self.collector.get_data_display(instrument)
            return ""

        if is_2020 and simulation:
            try:
                ans = _get_answer("ceiling-r-value")
                data["insulated_ceiling"] = "R-%.0f" % float(ans)
            except ValueError:
                pass
        elif is_2019 and simulation:
            try:
                ans = _get_answer("ceiling-r-value")
                data["insulated_ceiling"] = "R-%.0f" % float(ans)
            except ValueError:
                pass
        elif is_2018:
            try:
                ans = _get_answer("ceiling-r-value")
                data["insulated_ceiling"] = "R-{}".format(int(round(float(ans), 0)))
            except ValueError:
                pass
        elif is_2017:
            try:
                ans = _get_answer("eto-flat_ceiling_r_value-2017")
                data["insulated_ceiling"] = "R-{}".format(int(round(float(ans), 0)))
            except ValueError:
                try:
                    ans = _get_answer("eto-vaulted_ceiling_r_value-2017")
                    data["insulated_ceiling"] = "R-{}".format(int(round(float(ans), 0)))
                except ValueError:
                    pass
        else:
            try:
                ans = _get_answer("eto-ceiling_r_value")
                data["insulated_ceiling"] = "R-{}".format(int(round(float(ans), 0)))
            except ValueError:
                pass

        # Only 2015 / 2016
        if is_2020:
            if simulation:
                wall = simulation.above_grade_walls.all().get_dominant_by_r_value()
                if wall:
                    cavity = wall.type.cavity_insulation_r_value or 0.0
                    continuous = wall.type.continuous_insulation_r_value or 0.0
                    r_value = cavity + continuous
                    data["insulated_walls"] = "R-%.0f" % r_value

        elif is_2018 or is_2019:
            if simulation:
                try:
                    r_value = simulation.abovegradewall_set.get_r_value_for_largest()
                    if r_value is not None:
                        data["insulated_walls"] = "R-%.0f" % r_value
                except (ObjectDoesNotExist, AttributeError):
                    pass
        elif is_2017:
            try:
                ans = _get_answer("eto-above_grade_walls_r_value-2017")
                data["insulated_walls"] = "R-{}".format(int(round(float(ans), 0)))
            except ValueError:
                pass
        else:
            try:
                ans = _get_answer("eto-wall_r_value")
                data["insulated_walls"] = "R-{}".format(int(round(float(ans), 0)))
            except ValueError:
                pass

        if is_2020:
            if simulation:
                floor = simulation.frame_floors.all().get_dominant_by_r_value()
                if floor:
                    cavity = floor.type.cavity_insulation_r_value or 0.0
                    continuous = floor.type.continuous_insulation_r_value or 0.0
                    r_value = cavity + continuous
                    data["insulated_floors"] = "R-%.0f" % r_value
                else:
                    r_value = simulation.slabs.all().dominant_underslab_r_value
                    if r_value is not None:
                        data["insulated_floors"] = "R-%.0f" % r_value

        elif is_2018 or is_2019:
            if simulation:
                try:
                    r_value = simulation.framefloor_set.get_r_value_for_largest()
                    if r_value is not None:
                        data["insulated_floors"] = "R-%.0f" % r_value
                    elif is_2019:
                        r_value = simulation.slab_set.get_dominant_underslab_r_value()
                        if r_value is not None:
                            data["insulated_floors"] = "R-%.0f" % r_value
                except (ObjectDoesNotExist, AttributeError):
                    pass
        elif is_2017:
            try:
                ans = _get_answer("eto-framed_floor_r_value")
                data["insulated_floors"] = "R-{}".format(int(round(float(ans), 0)))
            except ValueError:
                try:
                    ans = _get_answer("eto-slab_under_insulation_r_value")
                    data["insulated_floors"] = "R-{}".format(int(round(float(ans), 0)))
                except ValueError:
                    try:
                        ans = _get_answer("eto-slab_perimeter_r_value")
                        data["insulated_floors"] = "R-{}".format(int(round(float(ans), 0)))
                    except ValueError:
                        pass
        else:
            try:
                ans = _get_answer("eto-floor_r_value")
                data["insulated_floors"] = "R-{}".format(int(round(float(ans), 0)))
            except ValueError:
                pass

        if is_2020:
            if simulation:
                u_value = simulation.windows.all().dominant_u_value
                data["efficient_windows"] = "U-{}".format(round(u_value, 2))
        elif is_2018 or is_2019:
            if simulation:
                try:
                    values = simulation.window_set.get_dominant_values()
                    data["efficient_windows"] = "U-{}".format(round(values["u_value"], 2))
                except (ObjectDoesNotExist, AttributeError, ValueError, TypeError):
                    pass
        elif is_2017:
            try:
                ans = _get_answer("eto-window_u_value")
                data["efficient_windows"] = "U-{}".format(round(float(ans), 2))
            except (ObjectDoesNotExist, ValueError):
                pass

        if is_2020:
            if simulation:
                value = simulation.lights.interior_led_percent or 0.0
                data["efficient_lighting"] = "{} %".format(round(value, 1))
        elif is_2019:
            if simulation:
                try:
                    ans = simulation.lightsandappliance.pct_interior_led
                except (ObjectDoesNotExist, AttributeError, ValueError):
                    ans = 0
                try:
                    ans += simulation.lightsandappliance.pct_interior_cfl
                except (ObjectDoesNotExist, AttributeError):
                    pass
                data["efficient_lighting"] = "{} %".format(round(float(ans), 1))
        elif is_2018:
            if simulation:
                try:
                    ans = simulation.lightsandappliance.pct_interior_cfl
                except (ObjectDoesNotExist, AttributeError):
                    ans = 0
                try:
                    data["efficient_lighting"] = "{} %".format(round(float(ans), 1))
                except ValueError:
                    data["efficient_lighting"] = "{} %".format(0)
        else:
            try:
                if is_2016 or is_2017:
                    ans = _get_answer("eto-lighting_pct-2016")
                else:
                    ans = _get_answer("eto-lighting_pct")
                data["efficient_lighting"] = "{} %".format(round(float(ans), 1))
            except (ObjectDoesNotExist, ValueError):
                pass

        if is_2020:
            if simulation:
                dominant = (
                    simulation.mechanical_equipment.dominant_water_heating_equipment.equipment
                )
                value = f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}"
                data["water_heater"] = value
        elif is_2018 or is_2019:
            if simulation:
                try:
                    equip = simulation.installedequipment_set.get_dominant_values(simulation.id)[
                        simulation.id
                    ]
                    data["water_heater"] = "{energy_factor} EF".format(
                        **equip["dominant_hot_water"]
                    )
                except (ObjectDoesNotExist, AttributeError):
                    pass
        else:
            try:
                if is_2017:
                    ans = _get_answer("eto-water_heater_heat_type-2017")
                else:
                    ans = _get_answer("eto-water_heater_heat_type")
                data["water_heater"] += ans
            except (ObjectDoesNotExist, ValueError):
                pass
            try:
                ans = _get_answer("eto-water_heater_ef")
                data["water_heater"] += " {} EF".format(round(float(ans), 2))
            except (ObjectDoesNotExist, ValueError):
                pass

        if is_2020:
            if simulation:
                dominant = simulation.mechanical_equipment.dominant_heating_equipment.equipment
                try:
                    value = f"{dominant.efficiency:.2f} {dominant.get_efficiency_unit_display()}"
                except AttributeError:
                    value = (
                        f"{dominant.heating_efficiency:.2f} "
                        f"{dominant.get_heating_efficiency_unit_display()}"
                    )
                data["space_heating"] = value
        elif is_2018 or is_2019:
            if simulation:
                try:
                    equip = simulation.installedequipment_set.get_dominant_values(simulation.id)[
                        simulation.id
                    ]
                    data["space_heating"] = "{efficiency:.1f} {units_pretty}".format(
                        **equip["dominant_heating"]
                    )
                except (ObjectDoesNotExist, AttributeError):
                    pass
                except ValueError:
                    data["space_heating"] = "{efficiency} {units_pretty}".format(
                        **equip["dominant_heating"]
                    )
        else:
            try:
                ans = _get_answer("eto-primary_heat_afue")
                data["space_heating"] = "{} % AFUE".format(round(float(ans), 1))
            except (ObjectDoesNotExist, ValueError):
                try:
                    ans = _get_answer("eto-primary_heat_hspf-2016")
                    data["space_heating"] = "{} HSFP".format(round(float(ans), 1))
                except (ObjectDoesNotExist, ValueError):
                    try:
                        ans = _get_answer("eto-primary_heat_seer-2016")
                        data["space_heating"] = "{} SEER".format(round(float(ans), 1))
                    except (ObjectDoesNotExist, ValueError):
                        try:
                            ans = _get_answer("eto-primary_heat_cop-2016")
                            data["space_heating"] = "{} COP".format(round(float(ans), 1))
                        except (ObjectDoesNotExist, ValueError):
                            pass

        try:
            if is_2019 or is_2020:
                ans = _get_answer("primary-heating-equipment-type")
            elif is_2018:
                ans = _get_answer("primary-heating-equipment-type")
            elif is_2016 or is_2017:
                ans = _get_answer("eto-primary_heat_type-2016")
            else:
                ans = _get_answer("eto-primary_heat_type")

            if "pump" in ans.lower():
                data["space_heating"] += " Heat Pump"
            elif "radiant" in ans.lower():
                data["space_heating"] += " Radiant"
            elif "furnace" in ans.lower():
                data["space_heating"] += " Furnace"
            else:
                data["space_heating"] += " {}".format(ans)
        except (ObjectDoesNotExist, ValueError):
            pass

        if is_2020:
            if simulation:
                data["envelope_tightness"] = simulation.infiltration.envelope_tightness_pretty
        elif is_2018 or is_2019:
            if simulation:
                try:
                    data["envelope_tightness"] = "{} {}".format(
                        simulation.infiltration.heating_value,
                        simulation.infiltration.get_units_display(),
                    )
                except (ObjectDoesNotExist, AttributeError):
                    pass
        else:
            try:
                ans = _get_answer("eto-duct_leakage_ach50")
                data["envelope_tightness"] = "{} ACH @ 50Pa".format(round(float(ans), 1))
            except (ObjectDoesNotExist, ValueError):
                pass

        if is_2020:
            if simulation:
                try:
                    rate = simulation.utility_rates.get(fuel=FuelType.ELECTRIC)
                    electric_rate_unit = rate.get_cost_units_display()
                    electric_cost = round(rate.seasonal_rates.get().block_rates.first().cost, 2)
                except (ObjectDoesNotExist, AttributeError, TypeError):
                    electric_cost = 0.0
                    electric_rate_unit = "$"
                try:
                    rate = simulation.utility_rates.get(fuel=FuelType.NATURAL_GAS)
                    gas_rate_unit = rate.get_cost_units_display()
                    gas_cost = round(rate.seasonal_rates.get().block_rates.first().cost, 2)
                except (ObjectDoesNotExist, AttributeError, TypeError):
                    gas_cost = 0.0
                    gas_rate_unit = "$"
                data["kwh_cost"] = "{}{:,}".format(electric_rate_unit, electric_cost)
                data["therm_cost"] = "{}{:,}".format(gas_rate_unit, gas_cost)
        else:
            try:
                rate_data = home_stat.floorplan.remrate_target.block_set.get_first_fuel_rate_dict()
                data["kwh_cost"] = "${:,}".format(round(rate_data["Electric"][0], 2))
            except (ObjectDoesNotExist, AttributeError, TypeError):
                data["kwh_cost"] = "$0.0"

            try:
                rate_data = home_stat.floorplan.remrate_target.block_set.get_first_fuel_rate_dict()
                data["therm_cost"] = "${:,}".format(round(rate_data["Natural gas"][0], 2))
            except (ObjectDoesNotExist, AttributeError, TypeError):
                data["therm_cost"] = "$0.0"

        return data

    def _set_variables(self, home_stat):
        calculator_form = get_eto_calculation_completed_form(home_stat)
        if not calculator_form.is_valid():
            log.debug("Calculator Form invalid!! %s", calculator_form.errors)
        self.home = self.set_calculator_variables(
            home_stat, calculator_data=calculator_form.clean()
        )

    def set_report_variables(self, **kwargs):
        # Specific stuff
        expected = [
            "street_line",
            "city",
            "state",
            "zipcode",
            "floorplan_type",
            "rater",
            "rater_ccb",
            "estimated_monthly_energy_costs",
            "estimated_average_annual_energy_cost",
            "year",
            "square_footage",
            "eps_issue_date",
        ]
        for k in expected:
            kwargs[k]
        self.home = kwargs

    def build(self, user=None, home_stat=None, response=None, **kwargs):
        try:
            self.set_report_variables(**kwargs)
        except KeyError:
            self.user = user
            self._set_variables(home_stat)

        self.canvas = canvas.Canvas(response, pagesize=letter)
        self.canvas.setAuthor("Pivotal Energy Solutions")
        if user:
            self.canvas.setAuthor(user.get_full_name())
        self.canvas.setCreator("Pivotal Energy Solutions")
        self.canvas.setKeywords(["EnergyTrust of Oregon", "EPS"])
        self.canvas.setProducer("Pivotal Energy Solutions")
        self.canvas.setSubject("EPS Report")
        home_status = EEPProgramHomeStatus.objects.filter(id=kwargs.get("home_status")).first()
        if home_status:
            address = home_status.home.get_home_address_display(
                include_city_state_zip=True, include_lot_number=False
            )
            self.canvas.setTitle(address)
        self.generate_page_one(**kwargs)
        self.canvas.showPage()
        self.generate_page_two(**kwargs)
        self.canvas.save()


# References
#    http://blogs.sitepointstatic.com/examples/tech/canvas-curves/bezier-curve.html
#    http://www.reportlab.com/docs/reportlab-userguide.pdf
#    http://www.reportlab.com/apis/reportlab/2.4/pdfgen.html#module-reportlab.pdfgen.canvas
