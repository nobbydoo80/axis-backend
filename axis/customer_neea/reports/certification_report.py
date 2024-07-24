"""Certification Report for NEEA"""


import os
import logging

from django.conf import settings
from django.db.models import QuerySet
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from django.contrib.auth import get_user_model

__author__ = "Steven K"
__date__ = "08/02/2019 11:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)

User = get_user_model()


class NWESHCertificationReport(object):
    """NorthWest Energy Star for Homes Certificate"""

    def __init__(self, filename, *_args, **kwargs):
        self.canvas = canvas.Canvas(filename.name, pagesize=landscape(letter))
        kwargs["filename"] = kwargs.get("filename", "/tmp/axis_pdf_report.pdf")  # nosec
        kwargs["leftMargin"] = kwargs.get("left_margin", kwargs.get("margins", 0.4 * inch))
        kwargs["rightMargin"] = kwargs.get("right_margin", kwargs.get("margins", 0.4 * inch))
        kwargs["topMargin"] = kwargs.get("top_margin", kwargs.get("margins", 0.4 * inch))
        kwargs["bottomMargin"] = kwargs.get("bottom_margin", kwargs.get("margins", 0.4 * inch))
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
        self.page_size = landscape(letter)

    def _get_styles(self):
        """Set the style.
        available styles:
            energy_star
            certified_home
            home_description
            congrats
            fine_print
            website
            address
            verification_information
        """
        log.debug("Setting up styles")
        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="energy_star",
                parent=styles["Normal"],
                fontName="Archer-Bold",
                fontSize=32,
                textColor=self.colors["text"]["red"],
            ),
            "energy_star",
        )
        styles.add(
            ParagraphStyle(name="registered_trademark", parent=styles["energy_star"], fontSize=12),
            "registered_trademark",
        )
        styles.add(
            ParagraphStyle(name="certified_home", parent=styles["energy_star"], fontSize=62),
            "certified_home",
        )

        styles.add(
            ParagraphStyle(
                name="home_description",
                parent=styles["Normal"],
                fontName="Archer-Bold",
                fontSize=21,
                textColor=self.colors["text"]["blue"],
            ),
            "home_description",
        )
        styles.add(
            ParagraphStyle(
                name="congrats", parent=styles["home_description"], fontName="Archer", fontSize=16
            ),
            "congrats",
        )

        styles.add(
            ParagraphStyle(
                name="fine_print",
                parent=styles["Normal"],
                fontName="Archer",
                fontsize=7,
                textColor=self.colors["text"]["black"],
                alignment=1,
            ),
            "fine_print",
        )

        styles.add(
            ParagraphStyle(
                name="website",
                parent=styles["Normal"],
                fontName="Archer-Bold",
                fontSize=14,
                textColor=self.colors["text"]["white"],
            ),
            "website",
        )

        styles.add(
            ParagraphStyle(
                name="address",
                parent=styles["Normal"],
                fontName="Archer-Bold",
                fontSize=18,
                alignment=1,
            ),
            "address",
        )
        styles.add(
            ParagraphStyle(
                name="verification_information",
                parent=styles["address"],
                fontName="Archer",
                leading=18,
                fontSize=14,
            ),
            "verification_information",
        )

        return styles

    def x(self, x):
        """Here for consistency when getting x values."""
        return x

    def y(self, y):
        """Calculate y coordinates from the top of the page."""
        return self.page_size[1] - y

    @property
    def colors(self):
        """Colors"""
        return {
            "text": {
                "red": HexColor(0xA7410D),
                "blue": HexColor(0x3E6F8F),
                "black": HexColor(0x35423C),
                "white": HexColor(0xFFFFFE),
            },
            "background": {"beige": HexColor(0xFAEFD9), "blue": HexColor(0x3E6F8F)},
        }

    @property
    def paragraphs(self):
        """List out the paragraphs"""
        return [
            {"x": 1.4, "y": 1.22, "style": self.styles["energy_star"], "text": """ENERGY STAR"""},
            {"x": 4.6, "y": 1.25, "style": self.styles["registered_trademark"], "text": """®"""},
            {
                "x": 1.3,
                "y": 1.66,
                "style": self.styles["certified_home"],
                "text": """CERTIFIED HOME""",
            },
            {
                "x": 1.45,
                "y": 2.67,
                "style": self.styles["home_description"],
                "text": """This certifies that the home built at:""",
            },
            {
                "x": 1.45,
                "y": 4.6,
                "style": self.styles["congrats"],
                "text": """meets Northwest ENERGY STAR Homes specifications for energy efficiency""",
            },
            {
                "x": self.left_margin / inch,
                "y": 7.1,
                "width": (self.page_size[0] / inch) - (self.right_margin * 2 / inch),
                "style": self.styles["fine_print"],
                "text": """A complete record of your home's ENERGY STAR certification <br/>
                    is on file with your ENERGY STAR Provider.""",
            },
            {
                "x": 1.43,
                "y": 7.7,
                "style": self.styles["website"],
                "text": """northwestenergystar.com""",
            },
            {
                "x": self.left_margin / inch,
                "y": 3.26,
                "width": (self.page_size[0] / inch) - (self.right_margin * 2 / inch),
                "style": self.styles["address"],
                "text": """{address}""",
            },
            {
                "x": self.left_margin / inch,
                "y": 3.62,
                "width": (self.page_size[0] / inch) - (self.right_margin * 2 / inch),
                "style": self.styles["verification_information"],
                "text": """{builder_name}""",
            },
            {
                "x": self.left_margin / inch,
                "y": 5.88,
                "width": (self.page_size[0] / inch) - (self.right_margin * 2 / inch),
                "style": self.styles["verification_information"],
                "text": """Verified by {user_name} of {user_company} <br/>
                Site ID#: {home_id}""",
            },
        ]

    @property
    def images(self):
        """Images"""
        return [
            {
                "x": 9.08,
                "y": 6.17,
                "width": 1.7,
                "height": 2,
                "path": "/static/images/nwesh_logo.jpg",
            }
        ]

    def _backgrounds(self):
        """Backgrounds"""
        self.canvas.saveState()

        # draw background
        width = self.page_size[0] - self.right_margin * 2
        height = self.page_size[1] - (self.top_margin + self.bottom_margin)
        self.canvas.setFillColor(self.colors["background"]["beige"])
        self.canvas.rect(
            x=self.x(self.left_margin),
            y=self.y(self.top_margin),
            width=width,
            height=-1 * height,
            stroke=0,
            fill=1,
        )

        # draw lower blue bar
        width = width
        height = 0.5
        self.canvas.setFillColor(self.colors["background"]["blue"])
        self.canvas.rect(
            x=self.x(self.left_margin),
            y=self.bottom_margin + (inch * height),
            width=width,
            height=height * -inch,
            stroke=0,
            fill=1,
        )

        self.canvas.restoreState()

    def _text_block(self, x, y, text, width=8.0, height=None, style=None, **_kwargs):
        """Text Block"""
        if not height:
            height = self.page_size[1]

        text = text.format(**self.home_stat)

        style = style if style else self.styles["Normal"]

        p = Paragraph(text, style=style)
        width, height = p.wrapOn(self.canvas, width * inch, height)
        p.drawOn(self.canvas, self.x(x * inch), self.y(y * inch) - height)

    def _image(self, path, x, y, width, height, **_kwargs):
        abs_path = os.path.join(settings.SITE_ROOT, "axis", "customer_neea") + path
        self.canvas.drawImage(
            image=abs_path,
            x=self.x(x * inch),
            y=self.y((height + y) * inch),
            width=width * inch,
            height=height * inch,
            preserveAspectRatio=True,
        )

    def generate_page(self, **_kwargs):
        """Generate a page"""
        self._backgrounds()
        for text in self.paragraphs:
            self._text_block(**text)
        for image in self.images:
            self._image(**image)

    def get_variables(self, home_stat, certifier_id):
        """Get the variables"""
        user = User.objects.get(id=certifier_id)
        home = home_stat.home

        address = home.street_line1
        if home.street_line2:
            address += ", {}".format(home.street_line2)
        address += ", {} {}, {}".format(home.city.name, home.state, home.zipcode)

        return {
            "address": address,
            "builder_name": home.get_builder(),
            "user_name": user.get_full_name(),
            "user_company": user.company.name,
            "home_id": home.get_id(),
        }

    def build(self, home_stats, certifier_id, **kwargs):
        """Build the document"""
        if not isinstance(home_stats, (list, QuerySet)):
            home_stats = [home_stats]
        if isinstance(home_stats, QuerySet):
            home_stats = list(home_stats)

        for stat in home_stats:
            self.home_stat = self.get_variables(stat, certifier_id)
            self.generate_page(**kwargs)
            self.canvas.showPage()

        self.canvas.save()
