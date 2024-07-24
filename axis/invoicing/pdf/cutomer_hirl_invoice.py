"""cutomer_hirl_invoice.py: """

__author__ = "Artem Hruzd"
__date__ = "03/25/2021 19:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import Table, TableStyle, ListFlowable, ListItem, HRFlowable


class CustomerHIRLInvoiceNumberedCanvas(canvas.Canvas):
    """
    Add a number for every PDF page in CustomerHIRLInvoicePDFReport
    """

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.Canvas = canvas.Canvas
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            self.Canvas.showPage(self)
        self.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(
            200 * mm,
            15 * mm + (0.2 * inch),
            "Page %d of %d" % (self._pageNumber, page_count),
        )


class CustomerHIRLInvoicePDFReport:
    """
    Draw PDF document from Invoice for HI customer
    """

    def __init__(self, invoice):
        """
        :param invoice: Invoice object
        """
        self.buffer = io.BytesIO()
        self.invoice = invoice

    def generate(self):
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=42,
            leftMargin=42,
            topMargin=10,
            bottomMargin=10,
        )
        invoice = []

        logo = "axis/invoicing/static/img/customer_hirl_invoice_logo.png"

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Justify", alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(name="Center", alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="Right", alignment=TA_RIGHT))

        invoice.append(
            Table(
                [
                    [
                        Image(logo, 2 * inch, 1 * inch),
                        Paragraph(
                            f'<font size="24" color="grey">Invoice</font>',
                            styles["Center"],
                        ),
                        Paragraph(
                            f'<font size="10" color="grey">'
                            f"<b>Accounts receivable</b></font><br/>"
                            f'<font size="10" color="grey">'
                            f"Home Innovations Research Labs</font><br/>"
                            f'<font size="10" color="grey">'
                            f"400 Prince Georges Boulevard</font><br/>"
                            f'<font size="10" color="grey">'
                            f"Upper Marlboro MD 20774-8731</font><br/>"
                            f'<font size=10><a href="www.homeinnovation.com/green" '
                            f'color="blue">www.homeinnovation.com/green</a></font>',
                            styles["Right"],
                        ),
                    ]
                ],
                style=TableStyle(
                    [
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (1, 0), "BOTTOM"),
                        ("VALIGN", (-1, -1), (-2, -1), "BOTTOM"),
                        ("VALIGN", (1, 0), (-2, -1), "TOP"),
                    ],
                ),
            )
        )

        invoice.append(
            HRFlowable(
                width="100%",
                thickness=1,
                lineCap="round",
                color=colors.lightgrey,
                spaceBefore=1,
                spaceAfter=1,
                hAlign="CENTER",
                vAlign="BOTTOM",
                dash=None,
            )
        )
        invoice.append(
            HRFlowable(
                width="100%",
                thickness=1,
                lineCap="round",
                color=colors.lightgrey,
                spaceBefore=1,
                spaceAfter=1,
                hAlign="CENTER",
                vAlign="BOTTOM",
                dash=None,
            )
        )

        invoice.append(
            Table(
                [
                    [
                        Paragraph(
                            f'<font size="12"><b>Invoice ID:</b> ' f"{str(self.invoice.id)}</font>",
                            styles["Normal"],
                        ),
                        Paragraph(
                            f'<font size="12"><b>Invoice Date:</b> '
                            f'{self.invoice.created_at.strftime("%m/%d/%Y")}</font>',
                            styles["Right"],
                        ),
                    ]
                ],
                style=TableStyle(
                    [
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ],
                ),
            )
        )

        customer_name = ""
        if self.invoice.customer:
            customer_name = f"{self.invoice.customer}"
            ngbs_legacy_id = self.invoice.customer.get_customer_hirl_legacy_id()
            if ngbs_legacy_id:
                customer_name = f"{self.invoice.customer} (NGBS ID: {ngbs_legacy_id})"

        invoice.append(
            Table(
                [
                    [
                        Paragraph(
                            f'<font size="12"><b>Customer:</b> {customer_name}</font>',
                            styles["Normal"],
                        ),
                        Paragraph(
                            f'<font size="12"><b>Total Due:</b> '
                            f'{"${:,.2f}".format(self.invoice.current_balance)}</font>',
                            styles["Right"],
                        ),
                    ]
                ],
                style=TableStyle(
                    [
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ],
                ),
            )
        )

        invoice.append(Spacer(1, 24))

        invoice.append(
            Paragraph(
                '<font size="12">Payment of the NGBS Green certification fees '
                "for the projects listed below is due: </font>",
                styles["Normal"],
            )
        )

        invoice.append(Spacer(1, 24))

        invoice_table_data = [
            [
                Paragraph("<b>Project ID</b>", styles["Center"]),
                Paragraph("<b>Project Code</b>", styles["Center"]),
                Paragraph("<b>Project Address</b>", styles["Center"]),
                Paragraph("<b>Total Fees</b>", styles["Center"]),
                Paragraph("<b>Current Balance</b>", styles["Center"]),
            ]
        ]
        for invoice_item_group in self.invoice.invoiceitemgroup_set.all():
            home_address = f"{invoice_item_group.home_status.home.get_home_address_display()}"
            hud_disaster_case_number = (
                invoice_item_group.home_status.customer_hirl_project.hud_disaster_case_number
            )
            if hud_disaster_case_number:
                home_address += f" ({hud_disaster_case_number})"
            invoice_table_data.append(
                [
                    Paragraph(
                        f"{invoice_item_group.home_status.customer_hirl_project.id}",
                        styles["Center"],
                    ),
                    Paragraph(
                        f"{invoice_item_group.home_status.customer_hirl_project.h_number}",
                        styles["Center"],
                    ),
                    Paragraph(home_address),
                    Paragraph("${:,.2f}".format(invoice_item_group.total), styles["Center"]),
                    Paragraph(
                        "${:,.2f}".format(invoice_item_group.current_balance),
                        styles["Right"],
                    ),
                ]
            )

        invoice_table = Table(invoice_table_data, colWidths=(None, None, 100 * mm, None, None))

        invoice_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        invoice.append(invoice_table)
        invoice.append(Spacer(1, 36))

        invoice.append(
            Paragraph(
                '<font size="12">Please note the following instructions: </font>',
                styles["Normal"],
            )
        )

        invoice.append(Spacer(1, 12))

        invoice.append(
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            '<font size="12">'
                            "The information above (builder/developer/remodeler/company "
                            "name and project address) will be populated on "
                            "the NGBS Green certificate. Please check to "
                            "make sure it is correct. If corrections are necessary, "
                            "email mailto:lmosteller@homeinnovation.com "
                            "and reference the Project Code above. </font>",
                            styles["Normal"],
                        )
                    ),
                    ListItem(
                        Paragraph(
                            '<font size="12">'
                            "Home Innovation must receive the certification "
                            "payment before we will review the final NGBS Green "
                            "Verification Report. Final reports held for more than "
                            "90 days for lack of payment become void and a new final "
                            "inspection is required for the project to be eligible for "
                            "certification.  The certification fee is non-refundable."
                            "</font>",
                            styles["Normal"],
                        )
                    ),
                    ListItem(
                        Paragraph(
                            '<font size="12">'
                            "Please make checks payable to Home Innovation Research "
                            "Labs and mail to the address above. "
                            "A $25 fee will be assessed for insufficient "
                            "funds and/or returned checks."
                            "</font>",
                            styles["Normal"],
                        )
                    ),
                    ListItem(
                        Paragraph(
                            '<font size="12">To pay by credit card, '
                            "call Mario Gozum at 301.430.6253.</font>",
                            styles["Normal"],
                        )
                    ),
                ],
                bulletType="1",
            )
        )

        invoice.append(Spacer(1, 12))

        invoice.append(
            Paragraph(
                '<font size="12">'
                "Thank you for your support of the NGBS Green certification program. "
                "Please visit our website at www.homeinnovation.com/green for marketing "
                "materials and other resources. We always welcome feedback on the certification "
                "process or the program. Please contact us at "
                "www.homeinnovation.com/NGBSGreenContact if you have questions, concerns, "
                "or want to tell us how we are doing. "
                "</font>",
                styles["Normal"],
            )
        )

        invoice.append(Spacer(1, 12))

        invoice.append(
            Paragraph(
                '<font size="12">'
                "* Projects earn NGBS Green certification post-construction. "
                "Until then, anticipated certification "
                "levels are not determinative and should be  treated as aspirational. </font>",
                styles["Italic"],
            )
        )

        doc.build(invoice, canvasmaker=CustomerHIRLInvoiceNumberedCanvas)

        self.buffer.seek(0)
        return self.buffer
