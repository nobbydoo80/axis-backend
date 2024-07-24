"""reports.py: Django customer_aps"""


import datetime
import io
import logging

from django.conf import settings
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, String, Group, Rect
from reportlab.lib.colors import Color
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph

__author__ = "Steven Klass"
__date__ = "4/20/12 3:03 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CheckRequest(object):
    def __init__(self, *args, **kwargs):
        filename = kwargs.get("filename", "test.pdf")
        if not isinstance(filename, str):
            filename = filename.name
        log.info("Writing to %s", filename)
        self.canvas = Canvas(filename)
        self.styles = getSampleStyleSheet()

        self.show_border = True

    def add_header(self):
        story = list()
        story.append(Paragraph("CHECK REQUEST", self.styles["Heading1"]))
        frame = Frame(3 * inch, 11 * inch, 2.35 * inch, 0.5 * inch, showBoundary=0)
        frame.addFromList(story, self.canvas)
        return frame

    def add_buiness_unit(self, business_unit="APSCO = Arizona Public Service"):
        story = list()
        story.append(Paragraph("<b>BUSINESS\nUNIT</b>", self.styles["Normal"]))
        frame = Frame(0.5 * inch, 10.5 * inch, 1 * inch, 0.5 * inch, showBoundary=1)
        frame.addFromList(story, self.canvas)

        story.append(Paragraph(business_unit, self.styles["Normal"]))
        frame = Frame(1.5 * inch, 10.5 * inch, 2.25 * inch, 0.5 * inch, showBoundary=1)
        frame.addFromList(story, self.canvas)
        return frame

    def add_payee(
        self,
        vendor_number="",
        payee_name="Meritage Homes",
        street_line1="123 E. Main St",
        city="Phoenix",
        state="AZ",
        zipcode="85011",
        country="USA",
        attn="",
        street_line2="",
        date_to_be_mailed=None,
    ):
        # Create the Payee box

        if date_to_be_mailed:
            date_to_be_mailed = date_to_be_mailed.strftime("%m/%d/%Y")
        else:
            date_to_be_mailed = ""

        self.canvas.setFillColorRGB(0.5, 0.5, 0.5)
        self.canvas.rect(15, 570, 30, 180, fill=1)
        self.canvas.rotate(90)
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(640, -35, "PAYEE")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.rotate(-90)

        self.canvas.rect(50, 720, 250, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(55, 740, "VENDOR NUMBER / EMPLOYEE NUMBER")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 725, vendor_number.upper())

        self.canvas.rect(50, 690, 300, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(55, 710, "PAYEE NAME (All Caps)")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 695, payee_name.upper())

        self.canvas.rect(50, 660, 300, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(55, 680, "ATTN")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 665, attn.upper())

        self.canvas.rect(50, 630, 300, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(55, 650, "PAYEE ADDRESS LINE 1 (All Caps)")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 635, street_line1.upper())

        self.canvas.rect(50, 600, 300, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(55, 620, "PAYEE ADDRESS LINE 2 (All Caps)")
        self.canvas.setFont("Helvetica", 12)
        try:
            self.canvas.drawString(55, 605, street_line2.upper())
        except AttributeError:
            self.canvas.drawString(55, 605, "")

        self.canvas.rect(50, 570, 100, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(55, 590, "CITY")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 575, city.upper())

        self.canvas.rect(150, 570, 75, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(155, 590, "STATE")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(155, 575, state.upper())

        self.canvas.rect(225, 570, 75, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(230, 590, "ZIP")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(230, 575, zipcode)

        self.canvas.rect(300, 570, 50, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(305, 590, "CNTRY")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(305, 575, country.upper())

        self.canvas.rect(50, 550, 175, 15)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(70, 553.5, "DATE CHECK TO BE MAILED")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.rect(50, 520, 175, 30)
        self.canvas.drawString(55, 525, date_to_be_mailed)

    def cash_mgmt(self, check_number="", check_date=""):
        self.canvas.rect(375, 730, 200, 15)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(405, 735, "CASH MANAGEMENT USE ONLY")

        self.canvas.rect(375, 715, 100, 15)
        self.canvas.drawString(395, 720, "PREPAID (P)")
        self.canvas.rect(375, 700, 100, 15)
        self.canvas.drawString(405, 705, "WIRE (P)")

        self.canvas.rect(475, 700, 50, 30)
        self.canvas.drawString(478, 720, "BANK NO")

        self.canvas.rect(525, 700, 50, 30)
        self.canvas.drawString(530, 720, "AUTH.")

        self.canvas.rect(375, 670, 200, 30)
        self.canvas.drawString(380, 690, "CHECK / WIRE NUMBER")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(375, 705, check_number)
        self.canvas.setFont("Helvetica", 10)

        self.canvas.rect(375, 640, 200, 30)
        self.canvas.drawString(380, 660, "CHECK / WIRE DATE")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(375, 675, check_date)
        self.canvas.setFont("Helvetica", 10)

        self.canvas.rect(375, 595, 200, 40)
        self.canvas.rect(385, 610, 10, 10)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(435, 625, "ATTACHMENTS")
        self.canvas.drawString(400, 610, "CHECK THIS BOX IF ATTACHMENTS")
        self.canvas.drawString(425, 598, "ARE REQUIRED BY VENDOR")
        self.canvas.setFont("Helvetica", 12)

        self.canvas.rect(375, 580, 200, 15)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(400, 585, "SPECIAL INSTRUCTIONS")

        self.canvas.rect(375, 550, 100, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(380, 570, "MAIL TO STA.")
        self.canvas.setFont("Helvetica", 12)

        self.canvas.rect(475, 550, 100, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(480, 570, "CALL EXT.")

        self.canvas.rect(375, 520, 200, 30)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(380, 540, "EMPLOYEE")

    def invoice(
        self, invoice_date="1/2/2010", invoice_number="1234", invoice_total="2100.00", builder=None
    ):
        invoice_date = "" if not invoice_date else invoice_date
        invoice_number = "" if not invoice_number else invoice_number
        invoice_total = 0 if not invoice_total else invoice_total
        builder = "Builder: {}".format(builder) if builder else ""

        self.canvas.setFillColorRGB(0.5, 0.5, 0.5)
        self.canvas.rect(15, 300, 30, 200, fill=1)
        self.canvas.rotate(90)
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(385, -35, "INVOICE")
        self.canvas.rotate(-90)

        self.canvas.setFillColorRGB(0.5, 0.5, 0.5)
        self.canvas.rect(50, 470, 125, 30, fill=1)
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.drawCentredString(112, 482, "INVOICE BILL DATE")
        self.canvas.setFillColorRGB(0.5, 0.5, 0.5)
        self.canvas.rect(175, 470, 300, 30, fill=1)
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.drawCentredString(325, 490, "INVOICE NUMBER AND/OR INVOICE BILL DESCRIPTION")
        self.canvas.drawCentredString(325, 475, "(LIMIT ONE INVOICE PER CHECK REQUEST)")
        self.canvas.setFillColorRGB(0.5, 0.5, 0.5)
        self.canvas.rect(475, 470, 100, 30, fill=1)
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.drawCentredString(525, 490, "TOTAL CHECK")
        self.canvas.drawCentredString(525, 475, "AMOUNT")

        self.canvas.rect(50, 440, 125, 30)
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 445, invoice_date)
        self.canvas.rect(175, 440, 300, 30)
        self.canvas.setFont("Helvetica", 18)
        self.canvas.drawString(180, 445, invoice_number.upper())
        self.canvas.rect(475, 440, 100, 30)
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(480, 445, "${:,}".format(invoice_total))

        self.canvas.rect(50, 400, 525, 30)
        self.canvas.drawString(
            55, 420, "OPTIONAL: REMIT MESSAGE TO BE PRINTED ON CHECK (4 LINES " "MAX)"
        )
        self.canvas.rect(50, 380, 525, 20)
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 385, "APS ENERGY STAR Homes Program")
        self.canvas.rect(50, 360, 525, 20)
        self.canvas.rect(50, 340, 525, 20)

        self.canvas.rect(50, 300, 525, 30)
        self.canvas.drawString(55, 320, "OPTIONAL: POWER PLANT MESSAGE (MAX 30 CHARACTERS)")

    def distribution(
        self, charge_number="DSM2044", department="6309", resource_cat="893", amount="2100.00"
    ):
        self.canvas.setFillColorRGB(0.5, 0.5, 0.5)
        self.canvas.rect(15, 180, 30, 110, fill=1)
        self.canvas.rotate(90)
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(200, -35, "DISTRIBUTION")
        self.canvas.rotate(-90)

        self.canvas.rect(50, 260, 50, 30)
        self.canvas.drawCentredString(75, 270, "LINE NO")
        self.canvas.rect(100, 260, 175, 30)
        self.canvas.drawCentredString(185, 270, "CHARGE NUMBER")
        self.canvas.rect(275, 260, 100, 30)
        self.canvas.drawCentredString(325, 270, "DEPARTMENT")
        self.canvas.rect(375, 260, 100, 30)
        self.canvas.drawCentredString(425, 270, "RESOURCE CAT.")
        self.canvas.rect(475, 260, 100, 30)
        self.canvas.drawCentredString(525, 270, "AMOUNT")

        self.canvas.rect(50, 240, 50, 20)
        self.canvas.drawCentredString(75, 245, "0001")
        self.canvas.rect(100, 240, 175, 20)
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawCentredString(185, 245, charge_number)
        self.canvas.rect(275, 240, 100, 20)
        self.canvas.drawCentredString(325, 245, department)
        self.canvas.rect(375, 240, 100, 20)
        self.canvas.drawCentredString(425, 245, resource_cat)
        self.canvas.rect(475, 240, 100, 20)
        self.canvas.drawCentredString(525, 245, "${:,}".format(amount))
        self.canvas.setFont("Helvetica", 10)

        self.canvas.rect(50, 220, 50, 20)
        self.canvas.drawCentredString(75, 225, "0002")
        self.canvas.rect(100, 220, 175, 20)
        self.canvas.rect(275, 220, 100, 20)
        self.canvas.rect(375, 220, 100, 20)
        self.canvas.rect(475, 220, 100, 20)

        self.canvas.rect(50, 200, 50, 20)
        self.canvas.drawCentredString(75, 205, "0003")
        self.canvas.rect(100, 200, 175, 20)
        self.canvas.rect(275, 200, 100, 20)
        self.canvas.rect(375, 200, 100, 20)
        self.canvas.rect(475, 200, 100, 20)

        self.canvas.rect(50, 180, 50, 20)
        self.canvas.drawCentredString(75, 185, "0004")
        self.canvas.rect(100, 180, 175, 20)
        self.canvas.rect(275, 180, 100, 20)
        self.canvas.rect(375, 180, 100, 20)
        self.canvas.rect(475, 180, 100, 20)

        self.canvas.rect(475, 160, 100, 20)
        self.canvas.drawString(275, 165, "TOTAL DISTRIBUTION AMOUNT")
        self.canvas.drawString(275, 155, "(Must balance with total check amount)")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawCentredString(525, 165, "${:,}".format(amount))

    def authorization(
        self,
        requestor_first,
        requestor_last,
        employee_number,
        extension,
        date="1/2/1201",
        station="8028",
    ):
        self.canvas.setFillColorRGB(0.5, 0.5, 0.5)
        self.canvas.rect(15, 50, 30, 90, fill=1)
        self.canvas.rotate(90)
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(55, -35, "AUTHORIZATION")
        self.canvas.rotate(-90)

        self.canvas.rect(50, 110, 150, 30)
        self.canvas.drawString(55, 130, "REQUESTOR (Last Name)")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 115, requestor_last)
        self.canvas.setFont("Helvetica", 10)

        self.canvas.rect(200, 110, 150, 30)
        self.canvas.drawString(205, 130, "(First Name)")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(205, 115, requestor_first)
        self.canvas.setFont("Helvetica", 10)

        self.canvas.rect(350, 110, 100, 30)
        self.canvas.drawString(355, 130, "EMPLOYEE NO")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(355, 115, employee_number)
        self.canvas.setFont("Helvetica", 10)

        self.canvas.rect(50, 80, 150, 30)
        self.canvas.drawString(55, 100, "DATE")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(55, 85, str(date))
        self.canvas.setFont("Helvetica", 10)
        self.canvas.rect(200, 80, 150, 30)
        self.canvas.drawString(205, 100, "EXTENSION")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(205, 85, extension)
        self.canvas.setFont("Helvetica", 10)
        self.canvas.rect(350, 80, 100, 30)
        self.canvas.drawString(355, 100, "STATION")
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawString(355, 85, station)
        self.canvas.setFont("Helvetica", 10)

        self.canvas.rect(50, 50, 300, 30)
        self.canvas.drawString(55, 70, "AUTHORIZATION REQUIRED                      EMP NO.")
        self.canvas.rect(350, 50, 100, 30)
        self.canvas.drawString(355, 70, "DATE")
        self.canvas.drawCentredString(
            306, 30, "PLEASE SEND SIGNED FORM TO ACCOUNTS PAYABLE, " "STATION 9540"
        )

    def build(self, invoice):
        self.add_header()
        self.add_buiness_unit()
        self.add_payee(
            vendor_number="",
            payee_name=invoice.customer.name,
            street_line1=invoice.customer.street_line1,
            street_line2=invoice.customer.street_line2,
            city=invoice.customer.city.name,
            state=invoice.customer.city.state,
            zipcode=invoice.customer.zipcode,
            country="USA",
            attn="",
            date_to_be_mailed=invoice.check_requested_date,
        )

        self.cash_mgmt(check_number="", check_date="")

        invoice_date = ""
        if invoice.check_requested_date:
            invoice_date = invoice.check_requested_date.strftime("%m/%d/%Y")

        builder = None
        parent_incentive_distribution = invoice.parent_incentive_distributions.first()
        if parent_incentive_distribution:
            builder = parent_incentive_distribution.customer.name

        self.invoice(
            invoice_date=invoice_date,
            invoice_number=invoice.invoice_number[:8],
            invoice_total=invoice.total,
            builder=builder,
        )
        self.distribution(
            charge_number="DSM2044", department="6309", resource_cat="893", amount=invoice.total
        )
        self.authorization(
            requestor_first=settings.APS_INCENTIVE_DETAILS["first_name"],
            requestor_last=settings.APS_INCENTIVE_DETAILS["last_name"],
            employee_number=settings.APS_INCENTIVE_DETAILS["employee_number"],
            date=datetime.date.today().strftime("%m/%d/%Y"),
            extension=settings.APS_INCENTIVE_DETAILS["extension"],
            station="8028",
        )
        self.canvas.save()


class ECBSVGBuilder(object):
    padding = 10
    first_column_width = 275
    subsequent_column_width = 100
    row_height = 30

    header_defaults = {
        "fontSize": 10,
        "fontName": "Helvetica-Bold",
    }
    font_defaults = {
        "fontSize": 10,
        "fontName": "Helvetica",
    }

    def __init__(self, data, *args, **kwargs):
        self.filename = kwargs.get("filename", "test.svg")
        log.info("Writing to %s", self.filename)

        self.data = data
        self.total_x = self.total_width = (
            self.first_column_width
            + (len(data[0])) * self.subsequent_column_width
            + 2 * self.padding
            - 0.5 * self.subsequent_column_width
        )
        self.total_y = self.total_height = 2 * self.row_height * (len(data)) + 2 * self.padding

        self.document = Drawing(self.total_x, self.total_y)
        self.document.vAlign = "TOP"
        self.story = []

    def add_headers(self):
        sections = ("Plan Names", "Square Feet")

        rect = Rect(
            0,
            self.total_height - 2 * self.row_height,
            self.total_width - 2 * self.padding,
            self.total_height - self.padding,
            strokeColor=Color(195 / 255.0, 217 / 255.0, 252 / 255.0),
            fillColor=Color(195 / 255.0, 217 / 255.0, 252 / 255.0),
        )

        self.document.add(rect)

        group = Group()
        y = self.total_y - 2 * self.padding
        for i, section_header in enumerate(sections):
            group.add(
                String(self.padding, y, section_header, **dict(self.font_defaults, fontSize=12))
            )

            x = self.first_column_width
            for column in self.data[i]:
                try:
                    column = "{:,d}".format(int(column))
                except:
                    pass
                group.add(String(x, y, column, textAnchor="middle", **self.font_defaults))
                x += self.subsequent_column_width
            self.document.add(group)

            y -= self.row_height

    def add_rows(self):
        sections = (
            ("Average Monthly Heating/Cooling Estimate", ("Electric and Gas",)),
            ("Water Heating", ("Electrict and Gas",)),
            ("Lights and Appliances", ("Electric and Gas",)),
            ("Service Fees and Taxes", ("Electric and Gas",)),
            ("TOTAL ANNUAL ELECTRIC & GAS", ()),
            ("ESTIMATED AVG MONTHLY ELECTRIC & GAS", ()),
        )

        def _add_data(x, y, index):
            # Data columns
            for column in self.data[index + 2]:  # +2 to skip header text and data
                if column:
                    column = "$ {:,d}".format(int(column))
                else:
                    column = ""

                group.add(String(x, y, column, textAnchor="middle", **self.font_defaults))
                x += self.subsequent_column_width

        group = Group()
        y = self.total_y - 2 * self.padding - 2 * self.row_height

        # Bold sections
        for i, section in enumerate(sections):
            section_header, entries = section
            group.add(String(self.padding, y, section_header, **self.header_defaults))

            x = self.first_column_width
            if entries:
                # Non-bold sections with data values
                for entry_text in entries:
                    y -= self.row_height
                    group.add(String(self.padding, y, entry_text, **self.font_defaults))

                    _add_data(x, y, i)
            else:
                # Print values inline with header
                _add_data(x, y, i)

            y -= self.row_height

        self.document.add(group)

    def build(self):
        self.add_headers()
        self.add_rows()

        return renderSVG.drawToString(self.document)
