# -*- coding: utf-8 -*-
"""customer_hirl_ld_program_letter_certificate.py: """

__author__ = "Artem Hruzd"
__date__ = "11/16/2022 18:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io
import os

from reportlab.lib.colors import blue, HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import TABLOID, LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer

from axis.core.checks import register_reportlab_fonts
from axis.qa.models import QARequirement, QAStatus

register_reportlab_fonts()


class CustomerHIRLLDProgramLetterCertificate:
    """
    Draw PDF document for Letter project
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
            pagesize=LETTER,
            rightMargin=42,
            leftMargin=42,
            topMargin=15,
            bottomMargin=10,
        )

        company_name = ""
        certification_level_display = ""
        developer_first_name = ""
        developer_last_name = ""
        project_name = ""

        address_line1 = self.home_status.home.street_line1
        address_line2 = ""
        if self.home_status.home.street_line2:
            address_line2 = self.home_status.home.street_line2

        city_line = "{}, {} {}".format(
            self.home_status.home.city.name,
            self.home_status.home.city.state,
            self.home_status.home.zipcode,
        )

        certification_date = self.home_status.certification_date.strftime("%B %d, %Y")

        if getattr(self.home_status, "customer_hirl_project", None):
            project_name = self.home_status.customer_hirl_project.registration.project_name
            developer_organization = (
                self.home_status.customer_hirl_project.registration.developer_organization
            )
            developer_organization_contact = (
                self.home_status.customer_hirl_project.registration.developer_organization_contact
            )
            if developer_organization_contact:
                developer_first_name = developer_organization_contact.first_name
                developer_last_name = developer_organization_contact.last_name
                company_name = developer_organization.name

        try:
            final_qa = self.home_status.qastatus_set.get(
                requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
            )
        except QAStatus.DoesNotExist:
            final_qa = None

        if final_qa:
            certification_level_display = final_qa.get_hirl_certification_level_awarded_display()

        letter_report = []

        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="Left",
                alignment=TA_LEFT,
                fontName="Arial",
                fontSize=14,
                leading=18,
                textColor=HexColor("#333333"),
            )
        )
        styles.add(
            ParagraphStyle(
                name="Justify",
                alignment=TA_JUSTIFY,
                fontName="Arial",
                fontSize=14,
                leading=18,
                textColor=HexColor("#333333"),
            )
        )
        styles.add(
            ParagraphStyle(
                name="Center",
                alignment=TA_CENTER,
                fontName="Arial",
                fontSize=14,
                leading=18,
                textColor=HexColor("#333333"),
            )
        )
        styles.add(
            ParagraphStyle(
                name="Right",
                alignment=TA_RIGHT,
                fontName="Arial",
                fontSize=14,
                leading=18,
                textColor=HexColor("#333333"),
            )
        )

        letter_report.append(
            Paragraph(
                f"{certification_date}<br/><br/>",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                f"{developer_first_name} {developer_last_name}",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                f"{company_name}",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                f"{address_line1}",
                styles.get("Justify"),
            )
        )

        if address_line2:
            letter_report.append(
                Paragraph(
                    f"{address_line2}",
                    styles.get("Justify"),
                )
            )

        letter_report.append(
            Paragraph(
                f"{city_line}<br/><br/>",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                f"Dear {developer_first_name} {developer_last_name}:<br/><br/>",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                f"{company_name} intends to have {project_name} certified as a Green Land Development per "
                "the ICC 700-2020 National Green Building Standard® (NGBS) once the construction has been completed. "
                "An initial review and approval of the plans has been requested as a first step toward certification.",
                styles.get("Justify"),
            )
        )

        letter_report.append(Spacer(width=0, height=10))

        letter_certificate_hirl_logo_path = os.path.join(
            "axis",
            "customer_hirl",
            "static",
            "customer_hirl",
            "reports",
            "customer_hirl_ld_program_letter_certificate",
            "letter_certificate_hirl_logo.jpg",
        )

        letter_report.append(Image(letter_certificate_hirl_logo_path, 172, 95))
        letter_report.append(Spacer(width=0, height=10))

        letter_report.append(
            Paragraph(
                "The plans and intended construction practices for this site development "
                "have been reviewed by a Home Innovation Research Labs’ Accredited NGBS "
                "Green Verifier, and the report from this assessment has been reviewed "
                "and approved by the Home Innovation Research Labs. "
                "This assessment indicates that this land development, when constructed in "
                "accordance with the plans submitted, will be eligible for NGBS Green Land Development "
                f"certification at the {certification_level_display} level.<br/><br/>",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                "Home Innovation Research Labs will issue the actual certification once construction "
                "is complete and the verifier has completed a final inspection of the site development. "
                "The final certification level will be determined by the total number of points awarded.<br/><br/>",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                "Learn more about the NGBS Green Land Development certification at:",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                '<font color="blue">'
                '<a href="www.homeinnovation.com/greendevelopment" '
                'target="_blank">www.homeinnovation.com/greendevelopment</a>'
                "</font><br/><br/>",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                "Best Regards",
                styles.get("Justify"),
            )
        )

        letter_certificate_michael_luzier_sign = os.path.join(
            "axis",
            "customer_hirl",
            "static",
            "customer_hirl",
            "reports",
            "customer_hirl_ld_program_letter_certificate",
            "letter_certificate_michael_luzier_sign.jpg",
        )

        letter_report.append(Image(letter_certificate_michael_luzier_sign, 178, 53, hAlign="LEFT"))

        letter_report.append(
            Paragraph(
                "Michael Luzier",
                styles.get("Justify"),
            )
        )

        letter_report.append(
            Paragraph(
                "President & CEO",
                styles.get("Justify"),
            )
        )

        doc.build(letter_report)

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
