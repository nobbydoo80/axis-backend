"""customer_hirl_certificate.py: """

__author__ = "Artem Hruzd"
__date__ = "12/11/2021 22:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io
import os

from PyPDF2 import PdfWriter, PdfReader
from django.apps import apps
from django.conf import settings
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from axis.core.checks import register_reportlab_fonts

register_reportlab_fonts()
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHIRLAccreditationPDFReport:
    """
    Draw PDF document from Accreditation for HI customer
    """

    template_pdf = None

    def __init__(self, accreditation):
        """
        :param accreditation: Accreditation object
        """
        self.buffer = io.BytesIO()
        self.accreditation = accreditation

    def draw_date_start(self, can):
        # Accreditation date start
        date_initial = self.accreditation.date_initial
        if date_initial:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=6.4 * inch,
                y=1.40 * inch,
                text=date_initial.strftime("%m/%d/%y"),
            )

    def draw_expiration_date(self, can):
        # Accreditation expiration date
        expiration_date = self.accreditation.get_expiration_date()
        if expiration_date:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=8.5 * inch,
                y=1.40 * inch,
                text=expiration_date.strftime("%m/%d/%y"),
            )

    def draw_verifier_info(self, can):
        x = 7.8
        y = 6.4

        # Verifier Name
        can.setFont("MuseoSans-500", 18)
        can.setFillColorRGB(0.314, 0.322, 0.314)
        can.drawCentredString(
            x=x * inch, y=y * inch, text=f"{self.accreditation.trainee.get_full_name()}"
        )

        # Verifier Company
        y = y - 0.4
        can.setFont("MuseoSans-500", 18)
        can.setFillColorRGB(0.314, 0.322, 0.314)
        can.drawCentredString(x=x * inch, y=y * inch, text=self.accreditation.trainee.company.name)

        # Verifier Company City
        y = y - 0.4
        can.setFont("MuseoSans-500", 18)
        can.setFillColorRGB(0.314, 0.322, 0.314)
        can.drawCentredString(
            x=x * inch, y=y * inch, text=self.accreditation.trainee.company.city.name
        )

        # Verifier Company State
        y = y - 0.4

        if self.accreditation.trainee.company.city.country.abbr == "US":
            company_state = self.accreditation.trainee.company.city.county.state
        else:
            company_state = self.accreditation.trainee.company.city.country.name

        can.setFont("MuseoSans-500", 18)
        can.setFillColorRGB(0.314, 0.322, 0.314)
        can.drawCentredString(
            x=x * inch,
            y=y * inch,
            text=company_state,
        )

    def generate(self):
        with io.open(self.template_pdf, "rb") as template_file:
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=(11 * inch, 17 * inch))

            self.draw_verifier_info(can=can)

            # Accreditation date start
            self.draw_date_start(can=can)

            # Accreditation expiration date
            self.draw_expiration_date(can=can)

            can.save()

            new_pdf = PdfReader(packet)

            pdf_template = PdfReader(template_file)
            output = PdfWriter()
            # merge templates
            page = pdf_template.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            output_stream = io.BytesIO()
            output.write(output_stream)
            output_stream.seek(0)
        return output_stream


class CustomerHIRLMasterVerifierPDFReport(CustomerHIRLAccreditationPDFReport):
    template_pdf = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "user_management",
        "static",
        "templates",
        "Master Verifier Accreditation Certificate template.pdf",
    )


class CustomerHIRLNGBS2020PDFReport(CustomerHIRLAccreditationPDFReport):
    template_pdf = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "user_management",
        "static",
        "templates",
        "2020 NGBS Accreditation Certificate template.pdf",
    )


class CustomerHIRLNGBS2015PDFReport(CustomerHIRLNGBS2020PDFReport):
    template_pdf = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "user_management",
        "static",
        "templates",
        "2015 NGBS Accreditation Certificate template.pdf",
    )


class CustomerHIRLNGBS2012PDFReport(CustomerHIRLNGBS2020PDFReport):
    template_pdf = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "user_management",
        "static",
        "templates",
        "2012 NGBS Accreditation Certificate template.pdf",
    )

    def draw_date_start(self, can):
        # Accreditation date start
        date_initial = self.accreditation.date_initial
        if date_initial:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=6.4 * inch,
                y=1.57 * inch,
                text=date_initial.strftime("%m/%d/%y"),
            )

    def draw_expiration_date(self, can):
        # Accreditation expiration date
        expiration_date = self.accreditation.get_expiration_date()
        if expiration_date:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=8.2 * inch,
                y=1.57 * inch,
                text=expiration_date.strftime("%m/%d/%y"),
            )


class CustomerHIRLWRIVerifierPDFReport(CustomerHIRLAccreditationPDFReport):
    template_pdf = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "user_management",
        "static",
        "templates",
        "WRI Verifier Accreditation Certificate template.pdf",
    )

    def draw_date_start(self, can):
        # Accreditation date start
        date_initial = self.accreditation.date_initial
        if date_initial:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=6.4 * inch,
                y=2.01 * inch,
                text=date_initial.strftime("%m/%d/%y"),
            )

    def draw_expiration_date(self, can):
        # Accreditation expiration date
        expiration_date = self.accreditation.get_expiration_date()
        if expiration_date:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=8.2 * inch,
                y=2.01 * inch,
                text=expiration_date.strftime("%m/%d/%y"),
            )


class CustomerHIRLGreenFieldRepPDFReport(CustomerHIRLAccreditationPDFReport):
    template_pdf = os.path.join(
        settings.SITE_ROOT,
        "axis",
        "user_management",
        "static",
        "templates",
        "NGBS Field Rep Accreditation Certificate template.pdf",
    )

    def draw_date_start(self, can):
        # Accreditation date start
        date_initial = self.accreditation.date_initial
        if date_initial:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=6.4 * inch,
                y=2.01 * inch,
                text=date_initial.strftime("%m/%d/%y"),
            )

    def draw_expiration_date(self, can):
        # Accreditation expiration date
        expiration_date = self.accreditation.get_expiration_date()
        if expiration_date:
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=8.2 * inch,
                y=2.01 * inch,
                text=expiration_date.strftime("%m/%d/%y"),
            )
