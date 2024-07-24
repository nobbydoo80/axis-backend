"""hers_brochure.py: """

import PIL
import io

from PIL.Image import Resampling
from PyPDF2 import PdfWriter, PdfReader
from django.http import HttpResponse
from django.views.generic import DetailView
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from axis.core.mixins import AuthenticationMixin
from axis.core.checks import register_reportlab_fonts
from axis.home.models import EEPProgramHomeStatus

__author__ = "Artem Hruzd"
__date__ = "11/25/2020 22:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


register_reportlab_fonts()


class HERSBrochureDownloadView(AuthenticationMixin, DetailView):
    model = EEPProgramHomeStatus
    queryset = EEPProgramHomeStatus.objects.all()
    permission_required = "home.view_home"

    template_pdf = "axis/customer_wsu/static/templates/WSU_HERS_Report.pdf"
    filename = "HERS Brochure {instance.home.street_line1}.pdf"
    content_type = "application/pdf"

    def get_queryset(self):
        return self.model.objects.filter_by_user(self.request.user)

    def get_filename(self):
        return self.filename.format(instance=self.get_object())

    def get(self, request, *args, **kwargs):
        """Return download-type response of the rendered pdf."""
        self.object = self.get_object()

        address_line1 = self.object.home.street_line1
        if self.object.home.street_line2:
            address_line1 += " {}".format(self.object.home.street_line1)

        # address_line2 = '{}, {} {}'.format(self.object.home.city.name,
        #                                    self.object.home.city.state,
        #                                    self.object.home.zipcode)

        builder_organization = self.object.home.get_builder()

        with io.open(self.template_pdf, "rb") as template_file:
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            pdf_template = PdfReader(template_file)
            page = pdf_template.pages[0]

            page_size = (float(page.mediabox[2]), float(page.mediabox[3]))
            can = canvas.Canvas(packet, pagesize=page_size)

            if builder_organization.logo:
                image = PIL.Image.open(builder_organization.logo)
                image.thumbnail((128, 128), Resampling.LANCZOS)

                can.drawImage(
                    image=ImageReader(image),
                    x=(page_size[0] / 2) - 64,
                    y=6.9 * inch,
                    mask="auto",
                    preserveAspectRatio=True,
                )

            home_photo = self.object.home.get_preview_photo()

            if home_photo:
                can.drawImage(
                    image=ImageReader(home_photo.file),
                    x=(page_size[0] / 2) - 125,
                    y=3.0 * inch,
                    width=250,
                    height=250,
                    mask="auto",
                    preserveAspectRatio=True,
                )

            can.setFont("Times New Roman", 24)
            can.setFillColorRGB(0.396, 0.416, 0.439)
            can.drawCentredString(x=page_size[0] / 2, y=6.12 * inch, text=address_line1)

            can.showPage()
            # second page
            can.showPage()
            # third page
            can.showPage()
            # fourth page
            try:
                remrate_data = self.object.floorplan.get_normalized_remrate_result_data()
                hers_score = remrate_data["eri_score"]
                hers_score = str(int(hers_score))
            except (AttributeError, KeyError, TypeError):
                hers_score = ""

            can.setFont("Times New Roman", 54)
            can.setFillColorRGB(0.616, 0.125, 0.180)
            can.drawCentredString(x=page_size[0] / 2, y=2.3 * inch, text=hers_score)
            can.showPage()

            can.save()

            new_pdf = PdfReader(packet)

            output = PdfWriter()
            # merge templates
            page = pdf_template.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            page = pdf_template.pages[1]
            page.merge_page(new_pdf.pages[1])
            output.add_page(page)

            page = pdf_template.pages[2]
            page.merge_page(new_pdf.pages[2])
            output.add_page(page)

            page = pdf_template.pages[3]
            page.merge_page(new_pdf.pages[3])
            output.add_page(page)

            output_stream = io.BytesIO()
            output.write(output_stream)
            output_stream.seek(0)

        response = HttpResponse(content_type=self.content_type)
        response["Content-Disposition"] = "attachment; filename={filename}".format(
            filename=self.get_filename()
        )
        response.write(output_stream.read())
        return response
