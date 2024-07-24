"""reports.py: Django incentive_payments"""


import logging
import sys

from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tables import Table, TableStyle

__author__ = "Steven Klass"
__date__ = "9/21/12 1:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CheckDetail(object):
    def __init__(self, *args, **kwargs):
        filename = kwargs.get("filename", "test.pdf")
        if not isinstance(filename, str):
            filename = filename.name
        log.debug("Writing to %s", filename)
        self.document = SimpleDocTemplate(
            filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )
        self.styles = getSampleStyleSheet()
        self.story = []

    def header(self, invoice="ab82376b", title="Check Detail"):
        ptext = "{}Customer: {}<br />Invoice: {}"
        pstyle = ParagraphStyle(name="pstyle", parent=self.styles["Title"], fontSize=16)
        if sys.version_info > (3,):
            import html

            customer = html.escape(invoice.customer.name)
        else:
            import cgi

            customer = cgi.escape(invoice.customer.name)

        self.story.append(
            Paragraph(ptext.format(title, customer, invoice.invoice_number[:8]), pstyle)
        )

    def subdivision_table(self, subdivision, data, company):
        final = [
            [subdivision],
            ["Lot", "Address", "Energy Star Program", "Cost"],
        ]
        span = 3
        if company.name == "APS":
            span = 4
            final = [
                [subdivision],
                ["Lot", "Address", "Meter Set", "Energy Star Program", "Cost"],
            ]

        for ipp in data["homes"]:
            addr = "{}, {}".format(ipp.home_status.home.street_line1, ipp.home_status.home.city)
            if len(addr) > 40:
                addr = addr[0:40] + "..."
            meterset = ""
            if hasattr(ipp.home_status.home, "apshome") and hasattr(
                ipp.home_status.home.apshome, "meterset_date"
            ):
                meterset = str(ipp.home_status.home.apshome.meterset_date)
            eep_program = ""
            if hasattr(ipp.home_status, "eep_program"):
                eep_program = str(ipp.home_status.eep_program)
            # log.info( '${:,}'.format(ipp.cost))
            lot_number = ipp.home_status.home.lot_number if ipp.home_status.home.lot_number else "-"
            sub_data = [
                Paragraph(lot_number, self.styles["Normal"]),
                Paragraph(addr, self.styles["Normal"]),
            ]
            if company.name == "APS":
                sub_data.append(Paragraph(meterset, self.styles["Normal"]))
            sub_data += [
                Paragraph(eep_program, self.styles["Normal"]),
                Paragraph("${:,}".format(ipp.cost), self.styles["Normal"]),
            ]

            final.append(sub_data)

        words = "Lots paid in this check: {}"
        if not self.invoice.is_paid:
            words = "Lots which will be paid: {}"
        # d_final = ["Total Lots Signed: {}".format(data['totals']['total']),
        #            "Lots Paid: {}".format(data['totals']['paid']),
        #            "Lots Remaining: {}".format(data['totals']['remaining']),
        #            words.format(len(data['homes']))]
        # if 'no_builder_agreement' in  data['totals']:
        d_final = ["", "", words.format(len(data["homes"]))]

        pstyle = ParagraphStyle(name="pstyle", parent=self.styles["Normal"], alignment=TA_CENTER)
        paragraph = Paragraph("            ".join(d_final), pstyle)

        table = Table(final, colWidths=[60, 225, 160, 75])
        if company.name == "APS":
            table = Table(final, colWidths=[50, 195, 60, 150, 65])

        table.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (span, 0)),
                    ("BACKGROUND", (0, 0), (span, 1), Color(195 / 255.0, 217 / 255.0, 252 / 255.0)),
                    ("BOX", (0, 0), (4, 1), 1.5, colors.black),
                    ("INNERGRID", (0, 2), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 1.5, colors.black),
                    # ('SPAN',(0,-2),(4,-1)),
                ]
            )
        )
        table.repeatRows = 2
        return table, paragraph

    def build(self, invoice, data, company, title):
        self.invoice = invoice
        self.header(self.invoice, title)

        subdivisions = list(data.keys())
        subdivisions.sort(key=lambda x: str(x))
        for subdivision in subdivisions:
            subtable, paragraph = self.subdivision_table(subdivision, data[subdivision], company)
            self.story.append(subtable)
            self.story.append(Spacer(1, 6))
            self.story.append(paragraph)
            self.story.append(Spacer(1, 12))
        self.story.append(Spacer(1, 12))

        pstyle = ParagraphStyle(name="pstyle", parent=self.styles["Normal"], alignment=TA_CENTER)
        final = [
            [
                "",
                Paragraph(
                    "Total Lots covered: {}".format(len(self.invoice.ippitem_set.all())), pstyle
                ),
                "",
                Paragraph("Total Payment amount: ${:,}".format(self.invoice.total), pstyle),
                "",
                Paragraph(
                    "Check Request Date: {}".format(self.invoice.check_requested_date), pstyle
                ),
                "",
            ],
        ]
        table = Table(final, colWidths=[10, 161, 10, 161, 10, 161, 10])
        table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        self.story.append(table)
        self.story.append(Spacer(1, 12))

        self.document.build(self.story)
