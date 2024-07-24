"""customer_hirl.py: """

__author__ = "Artem Hruzd"
__date__ = "08/20/2021 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import io
import os

from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import TABLOID
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import Table, TableStyle

from axis.core.checks import register_reportlab_fonts
from axis.customer_hirl.models import HIRLGreenEnergyBadge
from axis.customer_hirl.utils import CERTIFICATION_LEVEL_MAP
from axis.qa.models import QARequirement, QAStatus

register_reportlab_fonts()


class CustomerHIRLBadgePDFReport:
    """
    Draw PDF document from Invoice for HI customer
    """

    def __init__(self, home_status):
        """
        :param home_status: EEPProgramHomeStatus object
        """
        self.buffer = io.BytesIO()
        self.home_status = home_status

    def generate(self):
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=TABLOID,
            rightMargin=42,
            leftMargin=42,
            topMargin=18,
            bottomMargin=10,
        )
        badge_report = []

        green_energy_badge_icon_list_path = os.path.join(
            "axis",
            "home",
            "static",
            "images",
            "customer_hirl_badge_report",
            "green_energy_badge_icon_list.png",
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Left", alignment=TA_LEFT, fontName="Arial"))
        styles.add(ParagraphStyle(name="Justify", alignment=TA_JUSTIFY, fontName="Arial"))
        styles.add(ParagraphStyle(name="Center", alignment=TA_CENTER, fontName="Arial"))
        styles.add(ParagraphStyle(name="Right", alignment=TA_RIGHT, fontName="Arial"))

        address_line1 = self.home_status.home.street_line1
        if self.home_status.home.street_line2:
            address_line1 += " {}".format(self.home_status.home.street_line2)

        address_line2 = "{}, {} {}".format(
            self.home_status.home.city.name,
            self.home_status.home.city.state,
            self.home_status.home.zipcode,
        )

        try:
            final_qa = self.home_status.qastatus_set.get(
                requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
            )
        except QAStatus.DoesNotExist:
            final_qa = None

        wri_score = None
        certification_level = "Unknown"
        green_energy_badges = HIRLGreenEnergyBadge.objects.none()

        if final_qa:
            if final_qa.hirl_reviewer_wri_value_awarded:
                try:
                    wri_score = int(final_qa.hirl_reviewer_wri_value_awarded)
                except ValueError:
                    pass
            certification_level = final_qa.hirl_certification_level_awarded
            green_energy_badges = final_qa.hirl_badges_awarded.all()

        certification_level_hex_color = "#{:02x}{:02x}{:02x}".format(
            int(CERTIFICATION_LEVEL_MAP[certification_level]["color"][0] * 255),
            int(CERTIFICATION_LEVEL_MAP[certification_level]["color"][1] * 255),
            int(CERTIFICATION_LEVEL_MAP[certification_level]["color"][2] * 255),
        )

        badge_report.append(
            Table(
                [
                    [
                        Paragraph(
                            f'<font size="12" color=#333333>'
                            f"<b>{address_line1} {address_line2}</b></font>",
                            styles["Left"],
                        ),
                        Paragraph(
                            f'<font size="12" color={certification_level_hex_color}>'
                            f'{CERTIFICATION_LEVEL_MAP[certification_level]["title"]}'
                            f"</font>"
                            f'<font size="12" color=#333333> | '
                            f'{self.home_status.certification_date.strftime("%B %d, %Y")}'
                            f"</font>",
                            styles["Right"],
                        ),
                    ]
                ],
                style=TableStyle(
                    [
                        # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ],
                ),
            )
        )

        badge_report.append(Spacer(1, 12))

        badge_report.append(
            Paragraph(
                '<font size="20" color=#333333><b>NATIONAL GREEN BUILDING STANDARD</b></font>',
                ParagraphStyle(name="Center", alignment=TA_CENTER, fontName="Arial"),
            ),
        )
        badge_report.append(Spacer(1, 14))

        badge_report.append(
            Paragraph(
                '<i><font size="14" color=#333333>'
                "In addition to achieving NGBS Green certification from "
                "Home Innovation Research Labs, the project referenced above "
                "has achieved the following additional certifications. "
                "For more information on NGBS Green+ certifications, "
                "visit HomeInnovation.com/NGBSGreenPlus. "
                "For more information on WRI certification, "
                "visit HomeInnovation.com/WRI.</font></i>",
                ParagraphStyle(name="Center", alignment=TA_CENTER, fontName="Arial-Italic"),
            )
        )

        badge_report.append(Spacer(1, 12))

        for green_energy_badge in green_energy_badges:
            badge_report.append(
                Table(
                    [
                        [
                            [
                                Image(green_energy_badge_icon_list_path, 60, 88),
                                Paragraph(
                                    f'<font size="10.5" color="grey">'
                                    f"+{green_energy_badge.name} </font>",
                                    ParagraphStyle(
                                        name="Center", alignment=TA_CENTER, fontName="MuseoSans-500"
                                    ),
                                ),
                            ],
                            Paragraph(
                                f'<font size="10.5" color=#333333>'
                                f"<b>{green_energy_badge.name.upper()}:</b></font>"
                                f'<font size="10.5" color=#333333>'
                                f"{green_energy_badge.description}</font>",
                                styles["Left"],
                            ),
                            "",
                            "",
                            "",
                            "",
                            "",
                        ]
                    ],
                    style=TableStyle(
                        [
                            # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                            ("ALIGN", (0, 0), (0, 0), "CENTER"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("SPAN", (1, 0), (6, 0)),
                            ("VALIGN", (0, 0), (0, -1), "TOP"),
                            ("VALIGN", (1, -1), (1, -1), "MIDDLE"),
                        ],
                    ),
                )
            )
            badge_report.append(Spacer(1, 12))

        customer_hirl_project = getattr(self.home_status, "customer_hirl_project", None)
        if (
            wri_score is not None
            and self.home_status.eep_program.slug
            not in [
                "ngbs-sf-whole-house-remodel-2020-new",
                "ngbs-mf-whole-house-remodel-2020-new",
            ]
            and not (
                customer_hirl_project
                and (
                    customer_hirl_project.is_accessory_structure
                    or customer_hirl_project.is_accessory_dwelling_unit
                )
            )
        ):
            badge_report.append(
                Paragraph(
                    '<font size="10.5" color=#333333><b>WRI:</b> </font>'
                    '<font size="10.5" color=#333333>A Water Rating Index (WRI) '
                    "score indicates a property’s total "
                    "indoor and outdoor water use compared to a baseline based on the home’s "
                    "size and basic configurations, with a lower score "
                    "indicating lower overall water use.</font>"
                )
            )

            badge_report.append(Spacer(1, 12))

            badge_report.append(WaterRatingImage(wri=wri_score, width=723, height=205))

        doc.build(badge_report)

        self.buffer.seek(0)
        return self.buffer


class WaterRatingImage(Image):
    def __init__(self, wri=0, width=723, height=205):
        filename = os.path.join(
            "axis",
            "home",
            "static",
            "images",
            "customer_hirl_badge_report",
            "water_rating_index_bg.png",
        )
        self.wri = wri
        super(WaterRatingImage, self).__init__(filename, width, height)

    def draw(self):
        super(WaterRatingImage, self).draw()

        self.draw_typical_home_label()
        self.draw_cursor()

    def draw_typical_home_label(self):
        dx = getattr(self, "_offs_x", 0)
        dy = getattr(self, "_offs_y", 0)
        padding_right = self.drawWidth - (self.drawWidth / 1.4)

        typical_home_label = os.path.join(
            "axis",
            "home",
            "static",
            "images",
            "customer_hirl_badge_report",
            "typical_home_label.png",
        )

        typical_home_label_x = dx + self.drawWidth - padding_right / 2
        if self.wri > 90:
            typical_home_label_x = self.drawWidth / 30

        self.canv.drawImage(
            typical_home_label,
            x=typical_home_label_x,
            y=dy + (self.drawHeight / 2) - (self.drawWidth / 9.5),
            width=self.drawWidth / 7.5,
            height=self.drawWidth / 9.5,
            mask="auto",
        )

    def draw_cursor(self):
        dx = getattr(self, "_offs_x", 0)
        dy = getattr(self, "_offs_y", 0)

        wri_empty_cursor_path = os.path.join(
            "axis", "home", "static", "images", "customer_hirl_badge_report", "wri_empty_cursor.png"
        )

        wri_empty_cursor_width = self.drawWidth / 6.5
        wri_empty_cursor_height = wri_empty_cursor_width / 1.5

        padding_left = self.drawWidth / 7.2
        padding_right = self.drawWidth - (self.drawWidth / 1.4)
        scale_rect_width = self.drawWidth - padding_right - padding_left
        width_between_blocks = 7 * self.wri / 9

        wri_empty_cursor_x = (
            (scale_rect_width * self.wri / 100)
            + padding_left
            + width_between_blocks
            - wri_empty_cursor_width / 2
        )
        wri_empty_cursor_y_offset = 10
        wri_empty_cursor_y = (
            (self.drawHeight / 2) - wri_empty_cursor_height - wri_empty_cursor_y_offset
        )

        self.canv.drawImage(
            wri_empty_cursor_path,
            x=dx + wri_empty_cursor_x,
            y=dy + wri_empty_cursor_y,
            width=wri_empty_cursor_width,
            height=wri_empty_cursor_height,
            mask="auto",
        )

        wri_cursor_label_x = (
            (scale_rect_width * self.wri / 100)
            + padding_left
            + width_between_blocks
            - (wri_empty_cursor_width / 6)
        )
        if self.wri >= 100:
            wri_cursor_label_x -= 5

        self.canv.setFont("MuseoSans-500", 22)
        self.canv.setFillColorRGB(0.0, 0.396, 0.624)
        self.canv.drawString(
            x=dx + wri_cursor_label_x,
            y=dy
            + (self.drawHeight / 2)
            - (wri_empty_cursor_height / 2)
            - wri_empty_cursor_y_offset,
            text=f"{self.wri}",
        )
