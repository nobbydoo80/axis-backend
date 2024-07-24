"""eps_report_2022.py - axis"""

__author__ = "Steven K"
__date__ = "9/21/22 09:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import os
from io import BytesIO

from django.contrib.auth import get_user_model
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table

from axis.customer_eto.eep_programs.eto_2022 import (
    ElectricCarElements2022,
    StorageElements2022,
    SolarElements2022,
)

log = logging.getLogger(__name__)
User = get_user_model()

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class EPSReportGenerator:
    canvas = None
    _base_font = "Arial"
    debug = False

    MARGIN = 0.50 * inch  # 148 px
    LEFT_COL_WIDTH = 1.65 * inch  # 421 px
    MIDDLE_COL_START = 2.4 * inch  # 611 px
    MIDDLE_COL_WIDTH = 2.65 * inch  # 667 px
    RIGHT_COL_START = 5.30 * inch  # 1340 px
    RIGHT_COL_WIDTH = MIDDLE_COL_WIDTH

    WHITE = HexColor("#FFFFFF")
    BLACK = HexColor("#000000")
    LIGHT_GREY = HexColor("#F9F8F7")
    DARK_GREY = HexColor("#5D6461")
    DARKER_GREY = HexColor("#131313")
    DARK_BLUE = HexColor("#00618B")
    WATERMARK = HexColor("#EAEAEA")
    FOOTER_BLUE = HexColor("#3CB8CB")

    @property
    def styles(self) -> StyleSheet1:
        stylesheet = StyleSheet1()

        stylesheet.add(
            ParagraphStyle(name="normal", fontName=self._base_font, fontSize=9, leading=12)
        )

        stylesheet.add(ParagraphStyle(name="normal_lead", parent=stylesheet["normal"], leading=14))

        stylesheet.add(
            ParagraphStyle(
                name="normal_center", parent=stylesheet["normal"], alignment=TA_CENTER, leading=10
            )
        )

        stylesheet.add(
            ParagraphStyle(name="banner_eps", fontName=self._base_font, fontSize=10, leading=12)
        )

        stylesheet.add(
            ParagraphStyle(
                name="banner",
                fontName="Arial-Bold",
                fontSize=24,
                leading=28,
                textColor=self.DARK_BLUE,
            )
        )

        stylesheet.add(
            ParagraphStyle(
                name="eps_score",
                parent=stylesheet["banner"],
                textColor=self.BLACK,
                alignment=TA_CENTER,
            )
        )

        stylesheet.add(
            ParagraphStyle(
                name="location_utilities",
                fontName="Arial-Bold",
                fontSize=10,
                leftIndent=4,
                leading=12,
                textTransform="uppercase",
                textColor=self.DARKER_GREY,
            )
        )
        stylesheet.add(
            ParagraphStyle(
                name="your_home",
                parent=stylesheet["location_utilities"],
                textColor=self.WHITE,
            )
        )

        stylesheet.add(
            ParagraphStyle(
                name="tile_header",
                parent=stylesheet["location_utilities"],
                fontSize=11,
                leftIndent=0,
                leading=13,
                textColor=self.WHITE,
            )
        )

        stylesheet.add(
            ParagraphStyle(
                name="monthly_cost",
                parent=stylesheet["tile_header"],
                fontSize=23,
                leading=25,
                alignment=TA_CENTER,
            )
        )

        stylesheet.add(
            ParagraphStyle(
                name="tiny", parent=stylesheet["normal"], fontSize=6, leading=8, leftIndent=0
            )
        )

        stylesheet.add(
            ParagraphStyle(name="footer_above", parent=stylesheet["tiny"], fontSize=8, leading=8)
        )

        stylesheet.add(
            ParagraphStyle(
                name="footer",
                parent=stylesheet["tiny"],
                alignment=TA_JUSTIFY,
            )
        )

        stylesheet.add(
            ParagraphStyle(
                name="watermark",
                fontName="Arial-Bold",
                parent=stylesheet["normal"],
                fontSize=92,
                alignment=TA_CENTER,
                textColor=self.WATERMARK,
            )
        )

        return stylesheet

    def set_eps_logo(self) -> None:
        """Place our EPS Logo"""
        self.canvas.drawImage(
            image=os.path.join(FILE_PATH, "../static/images/MainLogo.png"),
            x=self.MARGIN + 0.07 * inch,
            y=8.87 * inch,
            width=1.50 * inch,
            height=1.68 * inch,
            preserveAspectRatio=True,
        )

    def set_top_header(self) -> None:
        banner = """Discover a home’s energy savings potential with EPS"""

        self.canvas.saveState()
        p = Paragraph(banner, style=self.styles["banner"])
        p.wrapOn(self.canvas, 5.0 * inch, 11 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START, y=9.83 * inch)

        header_text = """
            EPS™ measures and rates how much energy a newly constructed home uses. Use it to
            design or find homes that provide consistent comfort, healthy indoor air quality
            and low energy costs.
        """
        p = Paragraph(header_text, style=self.styles["banner_eps"])
        p.wrapOn(self.canvas, 5.0 * inch, 11 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START, y=9.25 * inch)
        self.canvas.restoreState()

    def set_location(
        self,
        street_line: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zipcode: str | None = None,
    ) -> None:
        self.canvas.saveState()
        self.canvas.setFillColor(self.LIGHT_GREY)
        self.canvas.rect(
            x=self.MARGIN,
            y=8.2 * inch,
            width=self.LEFT_COL_WIDTH,
            height=0.26 * inch,
            fill=1,
            stroke=0,
        )

        p = Paragraph("Location", style=self.styles["location_utilities"])
        p.wrapOn(self.canvas, 2 * inch, 11 * inch)
        p.drawOn(self.canvas, x=self.MARGIN, y=8.25 * inch)

        address = f"{street_line}<br/>{city}, {state} {zipcode}"
        if self.debug:
            address = " ".join(map(str, list(range(35))))
        p = Paragraph(address, style=self.styles["normal_lead"])
        _w, h = p.wrapOn(self.canvas, self.LEFT_COL_WIDTH, 1.0 * inch)
        p.drawOn(
            self.canvas, x=self.MARGIN + 0.055 * inch, y=8.15 * inch - h
        )  # Vertically align to top
        self.canvas.restoreState()

    def set_utilities(
        self, electric_utility: str | None = None, gas_utility: str | None = None
    ) -> None:
        self.canvas.saveState()
        self.canvas.setFillColor(self.LIGHT_GREY)
        self.canvas.rect(
            x=self.MARGIN,
            y=7.2 * inch,
            width=self.LEFT_COL_WIDTH,
            height=0.26 * inch,
            fill=1,
            stroke=0,
        )

        p = Paragraph("Utilities", style=self.styles["location_utilities"])
        p.wrapOn(self.canvas, 2 * inch, 11 * inch)
        p.drawOn(self.canvas, x=self.MARGIN, y=7.25 * inch)

        if self.debug:
            gas_utility = " ".join(map(str, list(range(25))))
            electric_utility = " ".join(map(str, list(range(25))))

        utilities = f"Electric: {electric_utility}"
        if gas_utility:
            utilities = f"Gas: {gas_utility}<br/>Electric: {electric_utility}"
        p = Paragraph(utilities, style=self.styles["normal_lead"])
        _w, h = p.wrapOn(self.canvas, self.LEFT_COL_WIDTH, 1.0 * inch)
        p.drawOn(self.canvas, x=self.MARGIN + 0.055 * inch, y=7.15 * inch - h)
        self.canvas.restoreState()

    def set_your_home(
        self,
        year: str | None = None,
        square_footage: str | None = None,
        eps_issue_date: str | None = None,
        rater: str | None = None,
        builder: str | None = None,
    ) -> None:
        self.canvas.saveState()
        self.canvas.setFillColor(self.DARK_GREY)
        self.canvas.rect(
            x=self.MARGIN,
            y=5.99 * inch,
            width=self.LEFT_COL_WIDTH,
            height=0.26 * inch,
            fill=1,
            stroke=0,
        )

        p = Paragraph("your home", style=self.styles["your_home"])
        p.wrapOn(self.canvas, 2 * inch, 11 * inch)
        p.drawOn(self.canvas, x=self.MARGIN, y=6.04 * inch)

        if self.debug:
            year = "0000"
            square_footage = "1,000,000"
            eps_issue_date = str(datetime.date(2022, 12, 24))
            rater = " ".join(map(str, list(range(40))))
            builder = " ".join(map(str, list(range(40))))

        if eps_issue_date is None:
            eps_issue_date = "PENDING"

        text = f"Year built: {year}<br />Sq. footage: {square_footage}<br />"
        text += f"EPS issue date: {eps_issue_date}<br />"
        text += f"Rated by: {rater}<br />"
        text += f"Builder: {builder}"

        p = Paragraph(text, style=self.styles["normal_lead"])
        _w, h = p.wrapOn(self.canvas, self.LEFT_COL_WIDTH, 1.0 * inch)
        p.drawOn(self.canvas, x=self.MARGIN + 0.055 * inch, y=5.94 * inch - h)
        self.canvas.restoreState()

    def set_qr_code(self) -> None:
        self.canvas.drawImage(
            image=os.path.join(FILE_PATH, "../static/images/ETOQR.png"),
            x=self.MARGIN,
            y=2.95 * inch,
            width=0.75 * inch,
            height=0.75 * inch,
            preserveAspectRatio=True,
        )
        text = "Scan QR code or visit<br />"
        text += "<b>www.energytrust.org/eps</b><br />"
        text += "to learn more about EPS."

        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(self.canvas, 1.7 * inch, 1.0 * inch)  # Bumped for url
        p.drawOn(self.canvas, x=self.MARGIN + 0.04 * inch, y=2.90 * inch - h)

    def set_estimated_costs(
        self,
        electric_utility: str | None = None,
        gas_utility: str | None = None,
        estimated_monthly_energy_costs: str | None = None,
        estimated_monthly_energy_costs_code: str | None = None,
        electric_per_month: str | None = None,
        natural_gas_per_month: str | None = None,
        kwh_cost: str | None = None,
        therm_cost: str | None = None,
        total_electric_kwhs: str | None = None,
        total_natural_gas_therms: str | None = None,
        annual_savings: str | None = None,
        thirty_year_savings: str | None = None,
    ) -> None:
        self.canvas.saveState()
        self.canvas.setFillColor(self.DARK_BLUE)
        self.canvas.rect(
            x=self.MIDDLE_COL_START,
            y=8.2 * inch,
            width=self.MIDDLE_COL_WIDTH,
            height=0.75 * inch,
            fill=1,
            stroke=0,
        )

        self.canvas.setFillColor(self.LIGHT_GREY)
        self.canvas.rect(
            x=self.MIDDLE_COL_START,
            y=6.45 * inch,
            width=self.MIDDLE_COL_WIDTH,
            height=1.75 * inch,
            fill=1,
            stroke=0,
        )

        self.canvas.restoreState()

        self.canvas.saveState()
        text = "ESTIMATED MONTHLY ENERGY COSTS"
        p = Paragraph(text, style=self.styles["tile_header"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.75 * inch, aH=0.75 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.8 * inch, y=8.75 * inch - h)

        p = Paragraph(
            f"{estimated_monthly_energy_costs if not self.debug else '$888'}",
            style=self.styles["monthly_cost"],
        )
        _w, h = p.wrapOn(canv=self.canvas, aW=0.75 * inch, aH=0.75 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.02 * inch, y=8.77 * inch - h)

        text = f"Monthly electric cost: ${electric_per_month if not self.debug else 888}<br />"
        text += f"Monthly gas cost: ${natural_gas_per_month if not self.debug else 888}<br />"
        text += "<i>Standard newly built home monthly<br />energy cost: "
        text += f"{estimated_monthly_energy_costs_code if not self.debug else '$8,888'}</i>"

        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.1 * inch, aH=3.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.1 * inch, y=8.15 * inch - h)

        text = (
            f"<b>Annual energy savings: {annual_savings if not self.debug else '$8,888'}</b><br />"
        )
        text += f"<i>About {thirty_year_savings if not self.debug else '$88,888'} over the "
        text += "life of a<br />30-year mortgage</i>"
        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.1 * inch, aH=3.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.1 * inch, y=7.425 * inch - h)

        rates = (
            f"{kwh_cost} per kWh and {therm_cost} per therm"
            if gas_utility
            else f"{kwh_cost} per kWh"
        )
        usage = (
            f"{total_electric_kwhs} kWh and {total_natural_gas_therms} therms"
            if gas_utility
            else f"{total_electric_kwhs} kWh"
        )

        text = f"<i>Estimated energy costs calculated using utility rates ({rates})"
        text += f" and estimated annual gross energy use ({usage}). Costs do not include fees.</i>"
        p = Paragraph(text, style=self.styles["tiny"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.25 * inch, aH=3.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.1 * inch, y=6.55 * inch)

        self.canvas.restoreState()

    def add_checkmark(self, x, y):
        self.canvas.drawImage(
            image=os.path.join(FILE_PATH, "../static/images/EPS_Checkbox.png"),
            x=x,
            y=y,
            width=38 * 0.28,
            height=40 * 0.28,
            preserveAspectRatio=True,
            mask="auto",
        )

    def set_energy_features(self) -> None:
        pass

        self.canvas.saveState()
        self.canvas.setFillColor(self.DARK_GREY)
        self.canvas.rect(
            x=self.MIDDLE_COL_START,
            y=5.9 * inch,
            width=self.MIDDLE_COL_WIDTH,
            height=0.35 * inch,
            fill=1,
            stroke=0,
        )

        self.canvas.setFillColor(self.LIGHT_GREY)
        self.canvas.rect(
            x=self.MIDDLE_COL_START,
            y=3.75 * inch,
            width=self.MIDDLE_COL_WIDTH,
            height=2.15 * inch,
            fill=1,
            stroke=0,
        )
        self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=5.63 * inch)
        self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=5.255 * inch)
        self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=4.895 * inch)
        self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=4.54 * inch)
        self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=4.03 * inch)
        self.canvas.restoreState()

        self.canvas.saveState()
        text = "ENERGY FEATURES"
        p = Paragraph(text, style=self.styles["tile_header"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH, aH=0.75 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.1 * inch, y=6.17 * inch - h)

        text = "Quality insulation improves comfort in any season."
        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.6 * inch, aH=1.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=5.79 * inch - h)

        text = "High-performance windows reduce outside noise."
        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.6 * inch, aH=1.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=5.43 * inch - h)

        text = "Efficient water heater keeps<br />costs down."
        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.6 * inch, aH=1.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=5.07 * inch - h)

        text = "Efficient heating and cooling provides reliable year-round comfort and savings."
        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.6 * inch, aH=1.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=4.71 * inch - h)

        text = "Tight envelope helps with indoor air quality and durability."
        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.MIDDLE_COL_WIDTH - 0.6 * inch, aH=1.0 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=4.2 * inch - h)

        self.canvas.restoreState()

    def set_energy_score(
        self,
        energy_score: int | None = None,
        energy_consumption_similar_home: int | None = None,
        energy_consumption_to_code: int | None = None,
    ) -> None:
        self.canvas.saveState()
        self.canvas.setFillColor(self.DARK_GREY)
        self.canvas.rect(
            x=self.RIGHT_COL_START,
            y=8.55 * inch,
            width=self.RIGHT_COL_WIDTH,
            height=0.4 * inch,
            fill=1,
            stroke=0,
        )

        self.canvas.setFillColor(self.LIGHT_GREY)
        self.canvas.rect(
            x=self.RIGHT_COL_START,
            y=3.75 * inch,
            width=self.RIGHT_COL_WIDTH,
            height=4.8 * inch,
            fill=1,
            stroke=0,
        )

        # STANDARD NEW HOME
        standard_width = 0.8 * inch
        standard_height = 1.0 * inch
        self.canvas.setFillColor(self.WHITE)
        self.canvas.rect(
            x=self.RIGHT_COL_START + 0.275 * inch,
            y=5.35 * inch,
            width=standard_width,
            height=standard_height,
            fill=1,
            stroke=1 if self.debug else 0,
        )

        # Similar Size
        self.canvas.setFillColor(self.WHITE)
        self.canvas.rect(
            x=self.RIGHT_COL_START + 0.275 * inch,
            y=3.95 * inch,
            width=standard_width,
            height=standard_height,
            fill=1,
            stroke=1 if self.debug else 0,
        )

        # Slider on right
        self.canvas.drawImage(
            image=os.path.join(FILE_PATH, "../static/images/EPS_2022_ESCORE.png"),
            x=6.64 * inch,
            y=3.86 * inch,
            width=334 * 0.28,
            height=972 * 0.28,
            preserveAspectRatio=True,
            mask="auto",
        )

        # Home
        self.canvas.drawImage(
            image=os.path.join(FILE_PATH, "../static/images/EPS_2022_HOME.png"),
            x=5.5 * inch,
            y=6.63 * inch,
            width=244 * 0.28,
            height=270 * 0.28,
            preserveAspectRatio=True,
            mask="auto",
        )
        self.canvas.restoreState()
        self.canvas.saveState()

        text = "This home's energy score"
        p = Paragraph(text, style=self.styles["tile_header"])
        _w, h = p.wrapOn(canv=self.canvas, aW=self.RIGHT_COL_START - 0.1 * inch, aH=0.5 * inch)
        p.drawOn(self.canvas, x=self.RIGHT_COL_START + 0.1 * inch, y=8.84 * inch - h)

        text = (
            "The lower the score, the better — a low EPS indicates an energy-efficient "
            "home with a smaller carbon footprint and lower energy costs."
        )

        p = Paragraph(text, style=self.styles["normal"])
        _w, h = p.wrapOn(canv=self.canvas, aW=2.40 * inch, aH=4.0 * inch)
        p.drawOn(self.canvas, x=self.RIGHT_COL_START + 0.1 * inch, y=8.5 * inch - h)

        center = 5.629 * inch
        p = Paragraph("YOUR HOME", style=self.styles["normal_center"])
        _w, h = p.wrapOn(canv=self.canvas, aW=standard_width - 0.1 * inch, aH=standard_height)
        p.drawOn(self.canvas, x=center, y=7.4 * inch - h)

        p = Paragraph(f"{energy_score if not self.debug else 888}", style=self.styles["eps_score"])
        _w, h = p.wrapOn(canv=self.canvas, aW=standard_width - 0.1 * inch, aH=standard_height)
        p.drawOn(self.canvas, x=center, y=7.15 * inch - h)

        p = Paragraph("STANDARD NEWLY BUILT HOME", style=self.styles["normal_center"])
        _w, h = p.wrapOn(canv=self.canvas, aW=standard_width - 0.1 * inch, aH=standard_height)
        p.drawOn(self.canvas, x=center, y=6.32 * inch - h)

        p = Paragraph(
            f"{energy_consumption_to_code if not self.debug else 888}",
            style=self.styles["eps_score"],
        )
        _w, h = p.wrapOn(canv=self.canvas, aW=standard_width - 0.1 * inch, aH=standard_height)
        p.drawOn(self.canvas, x=center, y=5.8 * inch - h)

        p = Paragraph(" SIMILAR SIZE EXISTING HOME", style=self.styles["normal_center"])
        _w, h = p.wrapOn(canv=self.canvas, aW=standard_width - 0.1 * inch, aH=standard_height)
        p.drawOn(self.canvas, x=center, y=4.92 * inch - h)

        p = Paragraph(
            f"{energy_consumption_similar_home if not self.debug else 888}",
            style=self.styles["eps_score"],
        )
        _w, h = p.wrapOn(canv=self.canvas, aW=standard_width - 0.1 * inch, aH=standard_height)
        p.drawOn(self.canvas, x=center, y=4.4 * inch - h)

        self.canvas.restoreState()

    def set_additional_features(
        self,
        solar_elements: str | None = None,
        electric_vehicle_type: str | None = None,
        storage_type: str | None = None,
        pv_capacity_watts: str | None = None,
        pv_watts: str | None = None,
        storage_capacity: str | None = None,
    ) -> None:
        self.canvas.saveState()
        self.canvas.setFillColor(self.DARK_GREY)
        self.canvas.rect(
            x=self.MIDDLE_COL_START,
            y=3.1 * inch,
            width=5.55 * inch,
            height=0.35 * inch,
            fill=1,
            stroke=0,
        )

        self.canvas.setFillColor(self.LIGHT_GREY)
        self.canvas.rect(
            x=self.MIDDLE_COL_START,
            y=2.35 * inch,
            width=5.55 * inch,
            height=0.75 * inch,
            fill=1,
            stroke=0,
        )

        _pointer, _delta = 2.89 * inch, 0.22 * inch
        if electric_vehicle_type:
            self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=_pointer)
            _pointer -= _delta
        if solar_elements:
            self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=_pointer)
            _pointer -= _delta
        if storage_type:
            self.add_checkmark(x=self.MIDDLE_COL_START + 0.1 * inch, y=_pointer)
            _pointer -= _delta

        self.canvas.restoreState()

        self.canvas.saveState()
        text = "Additional Features"
        p = Paragraph(text, style=self.styles["tile_header"])
        _w, h = p.wrapOn(canv=self.canvas, aW=6.0 * inch, aH=0.5 * inch)
        p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.1 * inch, y=3.375 * inch - h)

        _pointer, _delta = 3.045 * inch, 0.22 * inch
        if electric_vehicle_type:
            text = "Electric vehicle ready makes it easy to install an electric vehicle charger."
            if electric_vehicle_type == ElectricCarElements2022.EV_INSTALLED.value:
                text = "Electric vehicle charging equipment installed."
            p = Paragraph(text, style=self.styles["normal"])
            _w, h = p.wrapOn(canv=self.canvas, aW=6.0 * inch, aH=1.0 * inch)
            p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=_pointer - h)
            _pointer -= _delta
        if solar_elements:
            text = "Solar ready makes it easy to install rooftop solar."
            if solar_elements in [
                SolarElements2022.SOLAR_PV.value,
                SolarElements2022.NON_ETO_SOLAR.value,
                SolarElements2022.NET_ZERO.value,
            ]:
                text = (
                    f"Solar installed with a {pv_capacity_watts} watts solar system and {pv_watts} "
                    f"kWh in annual production."
                )
            p = Paragraph(text, style=self.styles["normal"])
            _w, h = p.wrapOn(canv=self.canvas, aW=6.0 * inch, aH=1.0 * inch)
            p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=_pointer - h)
            _pointer -= _delta
        if storage_type:
            text = "Storage ready allows for the installation of a future battery storage system."
            if storage_type == StorageElements2022.STORAGE_INSTALLED.value:
                text = f"Storage installed with a battery capacity of {storage_capacity} kWh. "
            p = Paragraph(text, style=self.styles["normal"])
            _w, h = p.wrapOn(canv=self.canvas, aW=6.0 * inch, aH=1.0 * inch)
            p.drawOn(self.canvas, x=self.MIDDLE_COL_START + 0.3 * inch, y=_pointer - h)
            _pointer -= _delta

        self.canvas.restoreState()

    def set_eto_logo(self) -> None:
        self.canvas.drawImage(
            image=os.path.join(FILE_PATH, "../static/images/BottomLogo.png"),
            x=6.55 * inch,
            y=1.4 * inch,
            width=1.4 * inch,
            height=0.77 * inch,
            preserveAspectRatio=True,
        )

    def set_footer(self) -> None:
        self.canvas.saveState()
        # Blue line
        self.canvas.setFillColor(self.FOOTER_BLUE)
        self.canvas.setStrokeColor(Color(0.3, 0.3, 0.3))
        self.canvas.rect(
            x=self.MARGIN,
            y=0.875 * inch,
            width=8.5 * inch - 2 * self.MARGIN,
            height=0.07 * inch,
            stroke=0,
            fill=1,
        )
        # Name address phone url
        style = self.styles["footer_above"]
        data = [
            [
                Paragraph("Energy Trust of Oregon", style=style),
                Paragraph("1.866.368.7878", style=style),
                Paragraph("421 SW Oak St, Suite 300, Portland, Oregon 97204", style=style),
                Paragraph("energytrust.org", style=style),
            ]
        ]
        t = Table(data, colWidths=[1.85 * inch, 1.85 * inch, 3.0 * inch])
        t.wrapOn(self.canvas, 8, 11)
        t.drawOn(canvas=self.canvas, x=0.46 * inch, y=1.06 * inch)
        # Below line
        footer_text = """
            Energy Trust of Oregon is an independent nonprofit organization dedicated to helping
            utility customers benefit from saving energy and generating renewable power. Our
            services, cash incentives and energy solutions have helped participating customers
            of Portland General Electric, Pacific Power, NW Natural, Cascade Natural Gas
            and Avista save on energy bills. Our work helps keep energy costs as low as possible,
            creates jobs and builds a sustainable energy future. <b>8/21</b>
        """
        style = self.styles["footer"]
        p = Paragraph(footer_text, style=style)
        width, height = p.wrapOn(self.canvas, 8.5 * inch - 2 * self.MARGIN, 11 * inch)
        p.drawOn(self.canvas, x=self.MARGIN, y=11 * inch - 10.25 * inch - height)
        self.canvas.restoreState()

    def add_preliminary_watermark(self):
        self.canvas.saveState()
        self.canvas.setFont(
            self.styles["watermark"].fontName,
            self.styles["watermark"].fontSize,
        )
        self.canvas.setFillColor(self.BLACK, 0.2)
        self.canvas.rotate(45)
        self.canvas.drawString(x=2.5 * inch, y=0.5 * inch, text="PRELIMINARY")
        self.canvas.restoreState()

    def generate_page_one(
        self,
        street_line: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zipcode: str | None = None,
        electric_utility: str | None = None,
        gas_utility: str | None = None,
        year: str | None = None,
        square_footage: str | None = None,
        eps_issue_date: str | None = None,
        rater: str | None = None,
        builder: str | None = None,
        energy_score: int | None = None,
        energy_consumption_similar_home: int | None = None,
        energy_consumption_to_code: int | None = None,
        estimated_monthly_energy_costs: str | None = None,
        estimated_monthly_energy_costs_code: str | None = None,
        electric_per_month: str | None = None,
        natural_gas_per_month: str | None = None,
        kwh_cost: str | None = None,
        therm_cost: str | None = None,
        total_electric_kwhs: str | None = None,
        total_natural_gas_therms: str | None = None,
        annual_savings: str | None = None,
        thirty_year_savings: str | None = None,
        solar_elements: str | None = None,
        electric_vehicle_type: str | None = None,
        storage_type: str | None = None,
        pv_capacity_watts: str | None = None,
        pv_watts: str | None = None,
        storage_capacity: str | None = None,
    ) -> None:
        self.set_eps_logo()
        self.set_top_header()
        self.set_location(street_line=street_line, city=city, state=state, zipcode=zipcode)
        self.set_utilities(gas_utility=gas_utility, electric_utility=electric_utility)
        self.set_your_home(
            year=year,
            square_footage=square_footage,
            eps_issue_date=eps_issue_date,
            rater=rater,
            builder=builder,
        )
        self.set_qr_code()
        self.set_estimated_costs(
            gas_utility=gas_utility,
            electric_utility=electric_utility,
            estimated_monthly_energy_costs=estimated_monthly_energy_costs,
            estimated_monthly_energy_costs_code=estimated_monthly_energy_costs_code,
            electric_per_month=electric_per_month,
            natural_gas_per_month=natural_gas_per_month,
            kwh_cost=kwh_cost,
            therm_cost=therm_cost,
            total_electric_kwhs=total_electric_kwhs,
            total_natural_gas_therms=total_natural_gas_therms,
            annual_savings=annual_savings,
            thirty_year_savings=thirty_year_savings,
        )
        self.set_energy_features()
        self.set_energy_score(
            energy_score=energy_score,
            energy_consumption_similar_home=energy_consumption_similar_home,
            energy_consumption_to_code=energy_consumption_to_code,
        )

        # Only add additional features if we have them.
        valid_solar = solar_elements in [
            SolarElements2022.SOLAR_READY.value,
            SolarElements2022.NET_ZERO.value,
            SolarElements2022.SOLAR_PV.value,
            SolarElements2022.NON_ETO_SOLAR.value,
        ]
        valid_car = electric_vehicle_type in [
            ElectricCarElements2022.EV_READY.value,
            ElectricCarElements2022.EV_INSTALLED.value,
        ]

        valid_storage = storage_type in [
            StorageElements2022.STORAGE_READY.value,
            StorageElements2022.STORAGE_INSTALLED.value,
        ]
        if self.debug or any([valid_solar, valid_car, valid_storage]):
            self.set_additional_features(
                solar_elements=solar_elements,
                electric_vehicle_type=electric_vehicle_type,
                storage_type=storage_type,
                pv_watts=pv_watts,
                pv_capacity_watts=pv_capacity_watts,
                storage_capacity=storage_capacity,
            )

        self.set_eto_logo()
        self.set_footer()
        if eps_issue_date is None:
            self.add_preliminary_watermark()

    def build(
        self,
        response: BytesIO | None = None,
        user: User | None = None,
        street_line: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zipcode: str | None = None,
        year: str | None = None,
        square_footage: str | None = None,
        eps_issue_date: str | None = None,
        rater: str | None = None,
        builder: str | None = None,
        electric_utility: str | None = None,
        gas_utility: str | None = None,
        energy_score: int | None = None,
        energy_consumption_similar_home: int | None = None,
        energy_consumption_to_code: int | None = None,
        estimated_monthly_energy_costs: str | None = None,
        estimated_monthly_energy_costs_code: str | None = None,
        electric_per_month: str | None = None,
        natural_gas_per_month: str | None = None,
        kwh_cost: str | None = None,
        therm_cost: str | None = None,
        total_electric_kwhs: str | None = None,
        total_natural_gas_therms: str | None = None,
        annual_savings: str | None = None,
        thirty_year_savings: str | None = None,
        solar_elements: str | None = None,
        electric_vehicle_type: str | None = None,
        storage_type: str | None = None,
        pv_capacity_watts: str | None = None,
        pv_watts: str | None = None,
        storage_capacity: str | None = None,
    ) -> None:
        self.canvas = canvas.Canvas(response, pagesize=letter)
        self.canvas.setAuthor("Pivotal Energy Solutions")
        if user:
            self.canvas.setAuthor(user.get_full_name())

        self.canvas.setCreator("Pivotal Energy Solutions")
        self.canvas.setKeywords(["EnergyTrust of Oregon", "EPS"])
        self.canvas.setProducer("Pivotal Energy Solutions")
        self.canvas.setSubject("EPS Report")

        if all([street_line, city, state, zipcode]):
            self.canvas.setTitle(", ".join([street_line, city, state, zipcode]))

        self.generate_page_one(
            street_line=street_line,
            city=city,
            state=state,
            zipcode=zipcode,
            electric_utility=electric_utility,
            gas_utility=gas_utility,
            year=year,
            square_footage=square_footage,
            eps_issue_date=eps_issue_date,
            rater=rater,
            builder=builder,
            energy_score=energy_score,
            energy_consumption_similar_home=energy_consumption_similar_home,
            energy_consumption_to_code=energy_consumption_to_code,
            estimated_monthly_energy_costs=estimated_monthly_energy_costs,
            estimated_monthly_energy_costs_code=estimated_monthly_energy_costs_code,
            electric_per_month=electric_per_month,
            natural_gas_per_month=natural_gas_per_month,
            kwh_cost=kwh_cost,
            therm_cost=therm_cost,
            total_electric_kwhs=total_electric_kwhs,
            total_natural_gas_therms=total_natural_gas_therms,
            annual_savings=annual_savings,
            thirty_year_savings=thirty_year_savings,
            solar_elements=solar_elements,
            electric_vehicle_type=electric_vehicle_type,
            storage_type=storage_type,
            pv_capacity_watts=pv_capacity_watts,
            pv_watts=pv_watts,
            storage_capacity=storage_capacity,
        )
        self.canvas.showPage()
        self.canvas.save()
