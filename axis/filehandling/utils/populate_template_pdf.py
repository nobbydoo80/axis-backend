import io
import logging

from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

__author__ = "Steven Klass"
__date__ = "5/28/12 7:56 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def populate_template_pdf(template, n_pages, coordinates, fonts=None, **data):
    """Open `template` as a path and overlay `kwargs` at locations defined by coordinates."""

    if fonts is None:
        fonts = {}
    font_default = fonts.pop("default", ("Helvetica", 12))

    with io.open(template, "rb") as f:
        existing_pdf = PdfReader(f)
        output = PdfWriter()
        for n in range(n_pages):
            page = existing_pdf.pages[n]

            # If there are spec fields in the coordinates, we check for those names
            # in `data`, and write them to the predefined coordinate for the name.
            if n in coordinates:
                page_coords = coordinates[n]

                # Open and write a temp pdf file that will become the overlay
                packet = io.BytesIO()
                data_layer = canvas.Canvas(packet, pagesize=letter)
                for name, item_coords in page_coords.items():
                    text_obj = data_layer.beginText()
                    if name in fonts:
                        if not hasattr(fonts[name], "__len__") or len(fonts[name]) != 2:
                            raise ValueError(
                                "Font values should be a 2-tuple of "
                                "('reportlabfontname_str', size_int)"
                            )
                        text_obj.setFont(*fonts[name])
                    else:
                        text_obj.setFont(*font_default)
                    text_obj.setTextOrigin(*item_coords)
                    if data[name]:
                        text_obj.textLines(data[name], trim=0)
                    data_layer.drawText(text_obj)
                data_layer.save()

                overlay = PdfReader(packet).pages[0]

                # Put our data on the template's page
                page.merge_page(overlay)

            # Modified or not, add the page to the result
            output.add_page(page)

        # Write to customer document for tracking
        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        return output_stream.read()
