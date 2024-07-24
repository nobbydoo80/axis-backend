"""washington_code_credit.py - Axis"""

__author__ = "Steven K"
__date__ = "10/18/21 10:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging
import os
import tempfile

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.colors import white, lightgrey

from ..calculator.washington_code_credit.constants.defaults import (
    BUILDING_ENVELOPE_OPTIONS,
    AIR_LEAKAGE,
    HVAC,
    HVAC_DISTRIBUTION,
    DRAIN_WATER_HEAT_RECOVER,
    HOT_WATER,
    RENEWABLES,
    APPLIANCES,
)
from ..eep_programs.washington_code_credit import (
    BuildingEnvelope,
    AirLeakageControl,
    HighEfficiencyHVAC,
    HighEfficiencyHVACDistribution,
    DWHR,
    EfficientWaterHeating,
    RenewableEnergy,
    Appliances,
)

log = logging.getLogger(__name__)

BuildingEnvelopeStrings = {
    BuildingEnvelope.OPTION_1p1: {
        "text": ("<b>Selected Credit: 1.1</b>\n" "Vertical fenestration U = 0.24.",),
        "width": 0.75,
    },
    BuildingEnvelope.OPTION_1p2: {
        "text": ("<b>Selected Credit: 1.2</b>\n" "Vertical fenestration U = 0.20.",),
        "width": 0.75,
    },
    BuildingEnvelope.OPTION_1p3a: {
        "text": (
            "<b>Selected Credit: 1.3a</b>\n"
            "Vertical fenestration U = 0.28\n"
            "Floor R-38\n"
            "Slab on grade R-10 perimeter and under entire slab\n"
            "Below grade slab R-10 perimeter and under entire slab"
        ),
        "width": 0.9,
    },
    BuildingEnvelope.OPTION_1p3b: {
        "text": ("<b>Selected Credit: 1.3b</b>\n" "Reduce the Total conductive UA by 5%.",),
        "width": 0.75,
    },
    BuildingEnvelope.OPTION_1p4a: {
        "text": (
            "<b>Selected Credit: 1.4a</b>\n"
            "Vertical fenestration U = 0.25\n"
            "Wall R-21 plus R-4 ci\n"
            "Floor R-38\n"
            "Basement wall R-21 int plus R-5 ci\n"
            "Slab on grade R-10 perimeter and under entire slab\n"
            "Below grade slab R-10 perimeter and under entire slab"
        ),
        "width": 1.5,
    },
    BuildingEnvelope.OPTION_1p4b: {
        "text": ("<b>Selected Credit: 1.4b</b>\n" "Reduce the total conductive UA by 15%.",),
        "width": 0.75,
    },
    BuildingEnvelope.OPTION_1p5a: {
        "text": (
            "<b>Selected Credit: 1.5a</b>\n"
            "Vertical fenestration U = 0.22\n"
            "Ceiling and single-rafter or joist-vaulted R-49 advanced\n"
            "Wood frame wall R-21 int plus R-12 ci\n"
            "Floor R-38\n"
            "Basement wall R-21 int plus R-12 ci\n"
            "Slab on grade R-10 perimeter and under entire slab\n"
            "Below grade slab R-10 perimeter and under entire slab"
        ),
        "width": 1.5,
    },
    BuildingEnvelope.OPTION_1p5b: {
        "text": ("<b>Selected Credit: 1.5b</b>\n" "Reduced the total conductive UA by 30%.",),
        "width": 0.75,
    },
    BuildingEnvelope.OPTION_1p6a: {
        "text": (
            "<b>Selected Credit: 1.6a</b>\n"
            "Vertical fenestration U = 0.18\n"
            "Ceiling and single-rafter or joist-vaulted R-60 advanced\n"
            "Wood frame wall R-21 int plus R-16 ci\n"
            "Floor R-48\n"
            "Basement wall R-21 int plus R-16 ci\n"
            "Slab on grade R-20 perimeter and under entire slab\n"
            "Below grade slab R-20 perimeter and under entire slab\n"
        ),
        "width": 1.5,
    },
    BuildingEnvelope.OPTION_1p6b: {
        "text": ("<b>Selected Credit: 1.6b</b>\n" "Reduced the total conductive UA by 40%.",),
        "width": 0.75,
    },
    BuildingEnvelope.OPTION_1p7: {
        "text": (
            "<b>Selected Credit: 1.7</b>\n"
            "Advanced framing and raised heel trusses or rafters\n"
            "Vertical Glazing U-0.28\n"
            "R-49 Advanced (U-0.020) as listed in Section A102.2.1\n"
            "Ceilings below a vented attic and R-49 vaulted ceilings with full height of "
            "uncompressed\n"
            "insulation extending over the wall top plate at the eaves."
        ),
        "width": 1.5,
    },
}

AirLeakageControlStrings = {
    AirLeakageControl.OPTION_2p1: {
        "text": (
            "<b>Selected Credit: 2.1</b>\n"
            "3 ACH50\nand\nAll whole house ventilation requirements as determined by Section M1507.3 "
            "of the International Residential Code or Section 403.8 of the International Mechanical "
            "Code shall be met with a high efficiency fan(s) (maximum 0.35 watts/cfm), not "
            "interlocked with the furnace fan (if present). Ventilation systems using a furnace "
            "including an ECM motor are allowed, provided that they are controlled to operate at "
            "low speed in ventilation only mode."
        ),
        "width": 1.5,
    },
    AirLeakageControl.OPTION_2p2: {
        "text": (
            "<b>Selected Credit: 2.2</b>\n"
            "2 ACH50\nand\nAll whole house ventilation requirements as determined by Section M1507.3 "
            "of the International Residential Code or Section 403.8 of the International Mechanical "
            "Code shall be met with a heat recovery ventilation system with minimum sensible heat "
            "recovery efficiency of 0.65."
        ),
        "width": 1.2,
    },
    AirLeakageControl.OPTION_2p3: {
        "text": (
            "<b>Selected Credit: 2.3</b>\n"
            "1.5 ACH50\nand\nAll whole house ventilation requirements as determined by Section "
            "M1507.3 of the International Residential Code or Section 403.8 of the International "
            "Mechanical Code shall be met with a heat recovery ventilation system with minimum "
            "sensible heat recovery efficiency of 0.75"
        ),
        "width": 1.2,
    },
    AirLeakageControl.OPTION_2p4: {
        "text": (
            "<b>Selected Credit: 2.4</b>\n"
            "0.6 ACH50\nand\nAll whole house ventilation requirements as determined by Section "
            "M1507.3 of the International Residential Code or Section 403.8 of the International "
            "Mechanical Code shall be met with a heat recovery ventilation system with minimum "
            "sensible heat recovery efficiency of 0.80. Duct installation shall comply with "
            "Section R403.3.7."
        ),
        "width": 1.3,
    },
}

HighEfficiencyHVACStrings = {
    HighEfficiencyHVAC.OPTION_3p1: {
        "text": (
            "<b>Selected Credit: 3.1</b>\n"
            "Energy Star rated (U.S. North) Gas or propane furnace with minimum AFUE of 95%"
        ),
        "width": 0.75,
    },
    HighEfficiencyHVAC.OPTION_3p2: {
        "text": "<b>Selected Credit: 3.2</b>\n**INELIGIBLE SELECTION**",
        "width": 0.5,
    },
    HighEfficiencyHVAC.OPTION_3p3: {
        "text": "<b>Selected Credit: 3.3</b>\n**INELIGIBLE SELECTION**",
        "width": 0.5,
    },
    HighEfficiencyHVAC.OPTION_3p4: {
        "text": "<b>Selected Credit: 3.4</b>\n**INELIGIBLE SELECTION**",
        "width": 0.5,
    },
    HighEfficiencyHVAC.OPTION_3p5: {
        "text": "<b>Selected Credit: 3.5</b>\n**INELIGIBLE SELECTION**",
        "width": 0.5,
    },
    HighEfficiencyHVAC.OPTION_3p6: {
        "text": "<b>Selected Credit: 3.6</b>\n**INELIGIBLE SELECTION**",
        "width": 0.5,
    },
}

HighEfficiencyHVACDistributionStrings = {
    HighEfficiencyHVACDistribution.OPTION_4p1: {
        "text": (
            "<b>Selected Credit: 4.1</b>\n"
            "All supply and return ducts located in an unconditioned attic shall be deeply buried "
            "in ceiling insulation in accordance with Section R403.3.7.\n "
            "For mechanical equipment located outside the conditioned space, a maximum of 10 linear "
            "feet of return duct and 5 linear feet of supply duct connections to the equipment may "
            "be outside the deeply buried insulation. All metallic ducts located outside the "
            "conditioned space must have both transverse and longitudinal joints sealed with "
            "mastic. If flex ducts are used, they cannot contain splices.\n"
            "Duct leakage shall be limited to 3 cfm per 100 square feet of conditioned floor area.\n"
            "Air handler(s) shall be located within the conditioned space."
        ),
        "width": 1.3,
    },
    HighEfficiencyHVACDistribution.OPTION_4p2: {
        "text": (
            "<b>Selected Credit: 4.2</b>\n"
            "HVAC equipment and associated duct system(s) installation shall comply with the "
            "requirements of Section R403.3.7.\n"
            "Locating system components in conditioned crawl spaces is not permitted under "
            "this option.\n"
            "Electric resistance heat and ductless heat pumps are not permitted under this option.\n"
            "Direct combustion heating equipment with AFUE less than 80% is not permitted "
            "under this option."
        ),
        "width": 1.1,
    },
}

DWHRStrings = {
    DWHR.OPTION_5p1: {
        "text": (
            "<b>Selected Credit: 5.1</b>\n"
            "A drain water heat recovery unit(s) shall be installed, which captures waste water "
            "heat from all and only the showers, and has a minimum efficiency of 40% if installed "
            "for equal flow or a minimum efficiency of 54% if installed for unequal flow. Such "
            "units shall be rated in accordance with CSA B55.1 or IAPMO IGC 346-2017 and be so "
            "labeled."
        ),
        "width": 1,
    },
}

EfficientWaterHeatingStrings = {
    EfficientWaterHeating.OPTION_5p2: {
        "text": (
            "<b>Selected Credit: 5.2</b>\n"
            "**INELIGIBLE SELECTION - Gas water heating must have UEF > 0.91**"
        ),
        "width": 1,
    },
    EfficientWaterHeating.OPTION_5p3: {
        "text": (
            "<b>Selected Credit: 5.3</b>\n"
            "Energy Star rated gas or propane water heater with a minimum UEF of 0.91"
        ),
        "width": 1,
    },
    EfficientWaterHeating.OPTION_5p4: {
        "text": (
            "<b>Selected Credit: 5.4</b>\n"
            "Electric heat pump water heater meeting the standards for Tier I of NEEA's advanced "
            "water heating specification"
        ),
        "width": 1.2,
    },
    EfficientWaterHeating.OPTION_5p5: {
        "text": (
            "<b>Selected Credit: 5.5</b>\n"
            "Electric heat pump water heater meeting the standards for Tier III of NEEA's advanced "
            "water heating specification"
        ),
        "width": 1.2,
    },
    EfficientWaterHeating.OPTION_5p6: {
        "text": (
            "<b>Selected Credit: 5.6</b>\n"
            "Electric heat pump water heater with a minimum UEF of 2.9 and utilizing a split system "
            "configuration with the air-to-refrigerant heat exchanger located outdoors. Equipment "
            "shall meet Section 4, requirements for all units, of the NEEA standard Advanced Water "
            "Heating Specification with the UEF noted above"
        ),
        "width": 1,
    },
}

RenewableEnergyStrings = {
    RenewableEnergy.OPTION_6p1a: {
        "text": (
            "<b>Selected Credit: 6.1a</b>\n"
            "For each 1200 kWh of electrical generation per housing unit provided annually by "
            "on-site wind or solar equipment a 1.0 credit shall be allowed, up to 3 credits. "
            "Generation shall be calculated as follows:\n"
            "For solar electric systems, the design shall be demonstrated to meet this requirement "
            "using the National Renewable Energy Laboratory calculator PVWATTs or approved "
            "alternate by the code official.\n"
            "Documentation noting solar access shall be included on the plans.\n"
            "For wind generation projects designs shall document annual power generation based on "
            "the following factors:\n"
            "The wind turbine power curve; average annual wind speed at the site; frequency "
            "distribution of the wind speed at the site and height of the tower."
        ),
        "width": 1.3,
    },
    RenewableEnergy.OPTION_6p1b: {
        "text": (
            "<b>Selected Credit: 6.1b</b>\n"
            "For each 1200 kWh of electrical generation per housing unit provided annually by "
            "on-site wind or solar equipment a 1.0 credit shall be allowed, up to 3 credits. "
            "Generation shall be calculated as follows:\n"
            "For solar electric systems, the design shall be demonstrated to meet this requirement "
            "using the National Renewable Energy Laboratory calculator PVWATTs or approved "
            "alternate by the code official.\n"
            "Documentation noting solar access shall be included on the plans.\n"
            "For wind generation projects designs shall document annual power generation based "
            "on the following factors:\n"
            "The wind turbine power curve; average annual wind speed at the site; frequency "
            "distribution of the wind speed at the site and height of the tower.\n"
        ),
        "width": 1.3,
    },
    RenewableEnergy.OPTION_6p1c: {
        "text": (
            "<b>Selected Credit: 6.1c</b>\n"
            "For each 1200 kWh of electrical generation per housing unit provided annually by "
            "on-site wind or solar equipment a 1.0 credit shall be allowed, up to 3 credits. "
            "Generation shall be calculated as follows:\n"
            "For solar electric systems, the design shall be demonstrated to meet this requirement "
            "using the National Renewable Energy Laboratory calculator PVWATTs or approved "
            "alternate by the code official.\n"
            "Documentation noting solar access shall be included on the plans.\n"
            "For wind generation projects designs shall document annual power generation based "
            "on the following factors:\n"
            "The wind turbine power curve; average annual wind speed at the site; frequency "
            "distribution of the wind speed at the site and height of the tower."
        ),
        "width": 1.3,
    },
}

AppliancesStrings = {
    Appliances.OPTION_7p1: {
        "text": (
            "<b>Selected Credit: 7.1</b>\n"
            "All of the following appliances shall be new and installed in the dwelling unit and shall "
            "meet the following standards:\n"
            "Dishwasher – Energy Star rated\n"
            "Refrigerator (if provided) – Energy Star rated\n"
            "Washing machine – Energy Star rated\n"
            "Dryer – Energy Star rated, ventless dryer with a minimum CEF rating of 5.2.",
        ),
        "width": 1.7,
    },
}

text_black = Color(0.3, 0.3, 0.3)
text_white = Color(1, 1, 1)


class WashingtonCodeCreditReport:
    def __init__(self, *_args, **kwargs):
        filename = os.path.join(tempfile.gettempdir(), "axis_washington_code_credit_report.pdf")
        self.filename = kwargs.get("filename", filename)
        self.margins = kwargs.get("margins", 0.75 * inch)
        self.pagesize = letter
        self.title = "Washington Code Credit Report"
        self.subject = "Washington Code Credit Report"
        self.author = "Pivotal Energy Solutions"
        self.keywords = "Pivotal Energy Solutions,Washington Code Credit,Energy Efficiency"
        self.styles = self._get_styles()
        self.canvas = None
        self.default_wrap_on = (
            self.pagesize[0] - 2 * self.margins,
            self.pagesize[1] - 2 * self.margins,
        )
        self.current_y_location = 0

    def _get_styles(self):
        log.debug("Setting up styles")
        styles = getSampleStyleSheet()
        styles["Normal"].textColor = (0.3, 0.3, 0.3)
        styles["Normal"].fontName = "Arial"

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Default",
                textColor=(0.3, 0.3, 0.3),
                fontName="Arial",
                fontSize=11,
                parent=styles["Normal"],
            ),
            "wcc_default",
        )

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Title",
                parent=styles["Normal"],
                fontName="Arial",
                fontSize=18,
                leading=8,
            ),
            "wcc_title",
        )
        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Sub Title",
                fontName="Arial",
                parent=styles["Normal"],
                fontSize=12,
            ),
            "wcc_sub_title",
        )

        styles.add(
            ParagraphStyle(
                name="Footer Bold",
                fontName="Arial",
                fontSize=10,
                parent=styles["Normal"],
            ),
            "footer_bold",
        )

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Address",
                parent=styles["Normal"],
                fontName="Arial",
                fontSize=11,
            ),
            "wcc_address",
        )

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Table Header",
                parent=styles["Normal"],
                fontName="Arial",
                textColor=white,
                fontSize=9,
            ),
            "wcc_table_header",
        )

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Table Credit Column Header",
                parent=styles["Normal"],
                fontName="Arial",
                textColor=white,
                fontSize=9,
                alignment=1,
            ),
            "wcc_table_credit_header",
        )

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Table Contents",
                fontName="Arial",
                fontSize=9,
                parent=styles["Normal"],
            ),
            "wcc_table_content",
        )

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Cell Contents",
                fontName="Arial-Bold",
                fontSize=9,
                parent=styles["Normal"],
                alignment=1,
            ),
            "wcc_credit_cell_content",
        )

        styles.add(
            ParagraphStyle(
                name="Washington Code Credit Category Cell Contents",
                fontName="Arial",
                fontSize=9,
                parent=styles["Normal"],
            ),
            "wcc_credit_category_cell_content",
        )

        styles.add(
            ParagraphStyle(
                name="tiny",
                fontName="Arial",
                parent=styles["Normal"],
                fontSize=7,
                leading=8,
                leftIndent=-1,
            ),
            "tiny",
        )
        styles.add(
            ParagraphStyle(
                name="footer",
                fontName="Arial",
                parent=styles["Normal"],
                fontSize=7.5,
                leading=10,
            ),
            "footer",
        )
        return styles

    def add_title(self):
        self.canvas.saveState()
        p = Paragraph("<b>Washington New Home Energy Report</b>", style=self.styles["wcc_title"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        p.drawOn(self.canvas, self.margins, self.pagesize[1] - 1.4 * inch)

        self.canvas.drawImage(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../static/images/ETLogo_grayscale.png",
            ),
            self.margins + 4.25 * inch,
            self.pagesize[1] - (self.margins + 0.50 * inch),
            width=1.49 * inch * 0.7,
            height=1.65 * inch * 0.7,
            preserveAspectRatio=True,
        )
        # self.canvas.restoreState()
        self.canvas.saveState()
        self.canvas.drawImage(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../static/images/NWNatural_black.png",
            ),
            self.margins + 3.20 * inch,
            self.pagesize[1] - (self.margins + 0.15 * inch),
            height=0.3 * inch,
            preserveAspectRatio=True,
        )

        self.canvas.restoreState()

    def add_header(self, address, builder, rater, certification_date):
        self.canvas.saveState()
        text = (
            "Energy Trust of Oregon supports builders to construct new homes that perform better "
            "than the Washington State Energy Code. This Participation Report summarizes energy "
            "efficient features for the home at:"
        )
        p = Paragraph(text, style=self.styles["wcc_default"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        p.drawOn(self.canvas, self.margins, self.pagesize[1] - 2.1 * inch)

        text = f"<b>{address}</b>"
        p = Paragraph(text.format(address=address), style=self.styles["wcc_address"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        p.drawOn(self.canvas, self.margins, self.pagesize[1] - 2.5 * inch)

        text = (
            f"<b>Builder Company</b>:  {builder}<br/>"
            f"<b>Verification Company</b>:  {rater}<br/>"
            f"<b>Energy Trust Certification Date</b>:  {certification_date}<br/>"
        )
        p = Paragraph(text, style=self.styles["wcc_default"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        p.drawOn(self.canvas, self.margins, self.pagesize[1] - 3.25 * inch)

        self.canvas.restoreState()

    def add_site_details(self, year_built, square_footage, gas_utility, electric_utility):
        data = [
            [
                Paragraph("SITE DETAILS", style=self.styles["wcc_table_header"]),
                "",
                "",
                "",
            ],
            [
                Paragraph("Year Built:", style=self.styles["wcc_table_content"]),
                Paragraph(f"{year_built}", style=self.styles["wcc_table_content"]),
                Paragraph("Gas Utility:", style=self.styles["wcc_table_content"]),
                Paragraph(f"{gas_utility}", style=self.styles["wcc_table_content"]),
            ],
            [
                Paragraph("Square Footage:", style=self.styles["wcc_table_content"]),
                Paragraph(f"{square_footage}", style=self.styles["wcc_table_content"]),
                Paragraph("Electric Utility:", style=self.styles["wcc_table_content"]),
                Paragraph(f"{electric_utility}", style=self.styles["wcc_table_content"]),
            ],
        ]

        t = Table(
            # data, rowHeights=0.30 * inch, colWidths=(self.pagesize[0] - 2 * self.margins) / 4.0
            data,
            rowHeights=0.30 * inch,
            colWidths=(1.5 * inch, 0.65 * inch, 1.35 * inch, 3.5 * inch),
        )
        t.setStyle(
            TableStyle(
                [
                    # # Header Row
                    ("BOX", (0, 0), (-1, 0), 1, (0, 0, 0)),  # Black
                    ("BACKGROUND", (0, 0), (-1, 0), (0, 0, 0)),  # Black
                    # Rest of it..
                    ("GRID", (0, 1), (-1, -1), 0.5, (0.7, 0.7, 0.7)),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        t.wrapOn(self.canvas, *self.default_wrap_on)
        t.drawOn(self.canvas, self.margins, self.pagesize[1] - (3.5 * inch) - t._height)
        self.current_y_location = self.pagesize[1] - (3.5 * inch) - t._height

    def get_text(self, value):
        value = value.get("text", value)
        if isinstance(value, (list, tuple)):
            if len(value) == 1:
                value = value[0]
            else:
                value = "<br />".join(value)
        return value.replace("\n", "<br />")

    def add_energy_table(self, data: list, y_location: float):
        tabe_style = TableStyle(
            [
                # Header Row
                ("BOX", (0, 0), (-1, 0), 1, (0, 0, 0)),  # Black
                ("BACKGROUND", (0, 0), (-1, 0), (0, 0, 0)),  # Black
                # Rest of it..
                ("GRID", (0, 1), (-1, -1), 0.5, (0, 0, 0)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )

        for column in range(len(data)):
            tabe_style.add("COLBACKGROUNDS", (0, column + 1), (0, column + 1), (lightgrey,))

        t = Table(
            data,
            colWidths=[0.9 * inch, 5.30 * inch, 0.8 * inch],
        )

        t.setStyle(tabe_style)
        t.wrapOn(self.canvas, *self.default_wrap_on)

        height = sum([x[1].height for x in data])
        height += 12 * (len(data) - 1) + 12
        t.drawOn(self.canvas, self.margins, self.current_y_location - t._height)
        self.current_y_location = self.current_y_location - t._height

    def add_energy_options(
        self,
        envelope_option: BuildingEnvelope,
        air_leakage_option: AirLeakageControl,
        hvac_option: HighEfficiencyHVAC,
        hvac_distribution_option: HighEfficiencyHVACDistribution,
    ):
        self.canvas.saveState()

        text = "<b>Home Selections from 2018 Washington State Energy Code Table 406.3</b>"
        p = Paragraph(text, style=self.styles["wcc_default"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        p.drawOn(self.canvas, self.margins, self.current_y_location - 0.5 * inch)
        self.current_y_location = self.current_y_location - (0.5 * inch) - p.height

        inches = 0

        data = [
            [
                Paragraph("CATEGORY", style=self.styles["wcc_table_header"]),
                Paragraph("SELECTION", style=self.styles["wcc_table_header"]),
                Paragraph("CREDITS", style=self.styles["wcc_table_credit_header"]),
            ]
        ]

        if BuildingEnvelopeStrings.get(envelope_option):
            data.append(
                [
                    Paragraph(
                        "<b>Efficient building envelope </b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(BuildingEnvelopeStrings.get(envelope_option)),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(BUILDING_ENVELOPE_OPTIONS[envelope_option]['eligible_credits']):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += BuildingEnvelopeStrings.get(envelope_option).get("width")

        if AirLeakageControlStrings.get(air_leakage_option):
            data.append(
                [
                    Paragraph(
                        "<b>Air leakage control & efficient ventilation</b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(AirLeakageControlStrings.get(air_leakage_option)),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(AIR_LEAKAGE[air_leakage_option]['eligible_credits']):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += AirLeakageControlStrings.get(air_leakage_option).get("width")

        if HighEfficiencyHVACStrings.get(hvac_option):
            data.append(
                [
                    Paragraph(
                        "<b>High efficiency HVAC</b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(HighEfficiencyHVACStrings.get(hvac_option, "N/A")),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(HVAC[hvac_option]['eligible_credits']):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += HighEfficiencyHVACStrings.get(hvac_option).get("width")

        if HighEfficiencyHVACDistributionStrings.get(hvac_distribution_option):
            data.append(
                [
                    Paragraph(
                        "<b>High efficiency HVAC distribution system</b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(
                            HighEfficiencyHVACDistributionStrings.get(
                                hvac_distribution_option, "N/A"
                            )
                        ),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(HVAC_DISTRIBUTION[hvac_distribution_option]['eligible_credits']):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += HighEfficiencyHVACDistributionStrings.get(hvac_distribution_option).get(
                "width"
            )

        # self.add_energy_table(data, self.margins + row_width * inch)
        self.add_energy_table(data, self.current_y_location - inches * inch)
        # self.current_y_location = self.current_y_location - inches * inch
        self.canvas.restoreState()

    def add_energy_options_page_2(
        self,
        dwhr_option: DWHR,
        water_heating_option: EfficientWaterHeating,
        renewable_electric_option: RenewableEnergy,
        appliance_option: Appliances,
    ):
        self.canvas.saveState()

        text = (
            "<b>Home Selections from 2018 Washington State Energy Code Table 406.3 (continued)</b>"
        )
        p = Paragraph(text, style=self.styles["wcc_default"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        p.drawOn(self.canvas, self.margins, self.pagesize[1] - (self.margins - 0.025 * inch))
        # self.current_y_location = self.pagesize[1] - (self.margins + 0.25 * inch)
        self.current_y_location = self.pagesize[1] - (0.5 * inch) - p.height - 18

        inches = 0

        data = [
            [
                Paragraph("CATEGORY", style=self.styles["wcc_table_header"]),
                Paragraph("SELECTION", style=self.styles["wcc_table_header"]),
                Paragraph("CREDITS", style=self.styles["wcc_table_credit_header"]),
            ]
        ]

        if DWHRStrings.get(dwhr_option):
            data.append(
                [
                    Paragraph(
                        "<b>Efficient water heating (drain water)</b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(DWHRStrings.get(dwhr_option, "N/A")),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(DRAIN_WATER_HEAT_RECOVER.get(dwhr_option)['eligible_credits']):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += DWHRStrings.get(dwhr_option).get("width")

        if EfficientWaterHeatingStrings.get(water_heating_option):
            data.append(
                [
                    Paragraph(
                        "<b>Efficient water heating (equipment)</b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(
                            EfficientWaterHeatingStrings.get(water_heating_option, "N/A"),
                        ),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(HOT_WATER[water_heating_option]['eligible_credits'] or 0.0):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += EfficientWaterHeatingStrings.get(water_heating_option).get("width")

        if RenewableEnergyStrings.get(renewable_electric_option):
            data.append(
                [
                    Paragraph(
                        "<b>Renewable generation credit</b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(
                            RenewableEnergyStrings.get(renewable_electric_option, "N/A"),
                        ),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(RENEWABLES[renewable_electric_option]['eligible_credits']):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += RenewableEnergyStrings.get(renewable_electric_option).get("width")

        if AppliancesStrings.get(appliance_option):
            data.append(
                [
                    Paragraph(
                        "<b>Appliance package</b>",
                        style=self.styles["wcc_credit_category_cell_content"],
                    ),
                    Paragraph(
                        self.get_text(AppliancesStrings.get(appliance_option, "N/A")),
                        style=self.styles["wcc_table_content"],
                    ),
                    Paragraph(
                        f"{(APPLIANCES[appliance_option]['eligible_credits']):.1f}",
                        style=self.styles["wcc_credit_cell_content"],
                    ),
                ]
            )
            inches += AppliancesStrings.get(appliance_option).get("width")

        # self.add_energy_table(data, row_width * inch)
        self.add_energy_table(data, self.current_y_location - inches * inch)
        self.canvas.restoreState()

    def add_code_summary(
        self,
        required_credits_to_meet_code: float = 0.0,
        achieved_total_credits: float = 0.0,
        eligible_gas_points: float = 0.0,
    ):
        self.canvas.saveState()

        text = "<b>Code Credit Summary</b>"
        p = Paragraph(text, style=self.styles["wcc_default"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        # p.drawOn(self.canvas, self.margins, 2.95 * inch)
        p.drawOn(self.canvas, self.margins, self.current_y_location - 40)

        required = str(round(required_credits_to_meet_code, 1))
        total = str(round(achieved_total_credits, 1))
        gas = str(round(eligible_gas_points, 1))

        data = [
            [
                Paragraph(
                    "<para align=center>CREDITS REQUIRED TO<br></br>MEET CODE</para>",
                    style=self.styles["wcc_table_header"],
                ),
                Paragraph(
                    "<para align=center>TOTAL CREDITS<br></br>ACHIEVED</para>",
                    style=self.styles["wcc_table_header"],
                ),
                Paragraph(
                    "<para align=center>GAS-RELATED CREDITS THAT<br></br>EXCEED CODE</para>",
                    style=self.styles["wcc_table_header"],
                ),
            ],
            [
                Paragraph(
                    f"<para align=center><b>{required}</b></para>",
                    style=self.styles["wcc_table_content"],
                ),
                Paragraph(
                    f"<para align=center><b>{total}</b></para>",
                    style=self.styles["wcc_table_content"],
                ),
                Paragraph(
                    f"<para align=center><b>{gas}</b></para>",
                    style=self.styles["wcc_table_content"],
                ),
            ],
        ]

        t = Table(data, colWidths=(self.pagesize[0] - 1.95 * self.margins) / 3.0)
        t.setStyle(
            TableStyle(
                [
                    # # Header Row
                    ("BOX", (0, 0), (-1, 0), 1, (0, 0, 0)),  # Black
                    ("BACKGROUND", (0, 0), (-1, 0), (0, 0, 0)),  # Black
                    # Rest of it..
                    ("GRID", (0, 1), (-1, -1), 0.5, (0.7, 0.7, 0.7)),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        t.wrapOn(self.canvas, *self.default_wrap_on)
        # t.drawOn(self.canvas, self.margins, 2.15 * inch)
        t.drawOn(self.canvas, self.margins, self.current_y_location - 99)
        self.canvas.restoreState()

    def add_footer(self):
        self.canvas.saveState()
        text = "<b>Energy Trust of Oregon</b>"
        p = Paragraph(text, style=self.styles["wcc_sub_title"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        # p.drawOn(self.canvas, self.margins, self.pagesize[1] - 9.25 * inch)
        p.drawOn(self.canvas, self.margins, self.current_y_location - 127)

        text = (
            "For more information about the New Homes program, contact Energy Trust at "
            "<b>1.866.368.7878</b> or visit <a href='www.energytrust.org'><u><b>www.energytrust.org</b></u></a>."
        )
        p = Paragraph(text, style=self.styles["footer_bold"])
        p.wrapOn(self.canvas, *self.default_wrap_on)
        # p.drawOn(self.canvas, self.margins, self.pagesize[1] - 9.45 * inch)
        p.drawOn(self.canvas, self.margins, self.current_y_location - 155)

        # self.canvas.setFillColor(Color(0.3, 0.3, 0.3))
        # self.canvas.setStrokeColor(Color(0.3, 0.3, 0.3))
        # self.canvas.rect(
        #     x=self.margins,
        #     y=self.pagesize[1] - 10.20 * inch,
        #     width=self.pagesize[0] - 2 * self.margins,
        #     height=0.07 * inch,
        #     stroke=1,
        #     fill=1,
        # )
        data = [
            [
                Paragraph(
                    "<para align=left><b>Energy Trust of Oregon</b></para>",
                    style=self.styles["tiny"],
                ),
                Paragraph(
                    "<para align=center>421 SW Oak St, Suite 300, Portland, Oregon 97204</para>",
                    style=self.styles["tiny"],
                ),
                Paragraph(
                    "<para align=center>1.866.368.7878</para>",
                    style=self.styles["tiny"],
                ),
                Paragraph(
                    "<para align=right><b>energytrust.org</b></para>",
                    style=self.styles["tiny"],
                ),
            ]
        ]
        t = Table(data, colWidths=[1.5 * inch, 2.5 * inch, 2.0 * inch, 1.0 * inch])
        t.wrapOn(self.canvas, *self.default_wrap_on)
        # t.drawOn(self.canvas, self.margins / 1.125, self.pagesize[1] - 10.13 * inch)
        t.drawOn(self.canvas, self.margins / 1.09, self.current_y_location - 177)

        footer_text = """
            Energy Trust of Oregon is an independent nonprofit organization dedicated to helping
            utility customers benefit from saving energy and tapping renewable resources. Our
            services, cash incentives, and energy solutions have helped participating customers
            of Portland General Electric, Pacific Power, NW Natural, Cascade Natural Gas and
            Avista save on energy costs. Our work helps keep energy costs as low as possible,
            create jobs and build sustainable energy future.<br/><b>12/20</b>
        """
        p = Paragraph(footer_text, style=self.styles["footer"])
        default_wrap_on = (
            self.pagesize[0] - 2.25 * self.margins,  # Bump in a bit
            self.pagesize[1] - 2 * self.margins,
        )
        p.wrapOn(self.canvas, *default_wrap_on)
        # p.drawOn(self.canvas, self.margins, self.pagesize[1] - 10.65 * inch)
        p.drawOn(self.canvas, self.margins / 1.01, self.current_y_location - 233)
        self.canvas.restoreState()

    def generate_page_one(
        self,
        address: str,
        builder: str,
        rater: str,
        certification_date: str,
        year_built: str,
        square_footage: str,
        electric_utility: str,
        gas_utility: str,
        envelope_option: BuildingEnvelope,
        air_leakage_option: AirLeakageControl,
        hvac_option: HighEfficiencyHVAC,
        hvac_distribution_option: HighEfficiencyHVACDistribution,
        **_kwargs,
    ):
        self.add_title()
        self.add_header(address, builder, rater, certification_date)
        self.add_site_details(year_built, square_footage, gas_utility, electric_utility)
        self.add_energy_options(
            envelope_option,
            air_leakage_option,
            hvac_option,
            hvac_distribution_option,
        )

    def generate_page_two(
        self,
        dwhr_option: DWHR,
        water_heating_option: EfficientWaterHeating,
        renewable_electric_option: RenewableEnergy,
        appliance_option: Appliances,
        required_credits_to_meet_code: float,
        achieved_total_credits: float,
        eligible_gas_points: float,
        **_kwargs,
    ):
        self.add_energy_options_page_2(
            dwhr_option,
            water_heating_option,
            renewable_electric_option,
            appliance_option,
        )
        self.add_code_summary(
            required_credits_to_meet_code, achieved_total_credits, eligible_gas_points
        )
        self.add_footer()

    def build(self, user=None, response=None, data: dict = None):
        if response is None:
            response = self.filename

        self.canvas = canvas.Canvas(response, pagesize=letter)
        self.canvas.setAuthor("Pivotal Energy Solutions")
        if user:
            self.canvas.setAuthor(user.get_full_name())
        self.canvas.setCreator("Pivotal Energy Solutions")
        self.canvas.setKeywords(["EnergyTrust of Oregon", "Washington Code Credit"])
        self.canvas.setProducer(str(user) if user is not None else "Pivotal Energy Solutions")
        self.canvas.setSubject("Washington Code Credit")
        self.canvas.setTitle(data["address"])
        self.generate_page_one(**data)
        self.canvas.showPage()
        self.generate_page_two(**data)
        self.canvas.showPage()
        self.canvas.save()
        return response
