"""customer_hirl_certificate_download.py: """

__author__ = "Artem Hruzd"
__date__ = "08/19/2020 22:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io

from PyPDF2 import PdfWriter, PdfReader
from django.apps import apps
from django.http import HttpResponse
from django.views.generic import DetailView
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from axis.core.checks import register_reportlab_fonts
from axis.core.mixins import AuthenticationMixin
from axis.customer_hirl.reports.certificate import CustomerHIRLCertificate
from axis.home.models import EEPProgramHomeStatus

register_reportlab_fonts()
customer_hirl_app = apps.get_app_config("customer_hirl")


class CustomerHIRLCertificateDownload(AuthenticationMixin, DetailView):
    model = EEPProgramHomeStatus
    queryset = EEPProgramHomeStatus.objects.all()
    permission_required = "home.view_home"

    content_type = "application/pdf"

    def get_queryset(self):
        available_programs = (
            customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
            + customer_hirl_app.HIRL_PROJECT_LEGACY_EEP_PROGRAM_SLUGS
        )
        return (
            self.model.objects.filter_by_user(self.request.user)
            .filter(
                state="complete",
                certification_date__isnull=False,
                eep_program__slug__in=available_programs,
            )
            .select_related("home", "customer_hirl_project", "eep_program")
        )

    def get(self, request, *args, **kwargs):
        """Return download-type response of the rendered pdf."""
        customer_hirl_certificate = CustomerHIRLCertificate(
            home_status=self.get_object(), user=self.request.user
        )
        output_stream = customer_hirl_certificate.generate()

        response = HttpResponse(content_type=self.content_type)
        response.write(output_stream.read())
        return response


class CustomerHIRLWaterSenseCertificateDownload(AuthenticationMixin, DetailView):
    model = EEPProgramHomeStatus
    queryset = EEPProgramHomeStatus.objects.all()
    permission_required = "home.view_home"

    template_pdf = "axis/home/static/templates/WS_homes_certificate_HIRL_Final.pdf"
    filename = "WaterSense Certificate {instance.home.street_line1}.pdf"
    content_type = "application/pdf"

    def get_queryset(self):
        available_programs = customer_hirl_app.HIRL_PROJECT_EEP_PROGRAM_SLUGS
        return self.model.objects.filter_by_user(self.request.user).filter(
            state="complete",
            certification_date__isnull=False,
            eep_program__slug__in=available_programs,
            customer_hirl_project__is_require_water_sense_certification=True,
            qastatus__hirl_water_sense_confirmed=True,
        )

    def get_filename(self):
        return self.filename.format(instance=self.get_object())

    def get(self, request, *args, **kwargs):
        """Return download-type response of the rendered pdf."""
        self.object = self.get_object()

        address_line1 = self.object.home.street_line1
        if self.object.home.street_line2:
            address_line1 += " {}".format(self.object.home.street_line2)

        address_line2 = "{} {}".format(
            self.object.home.city.as_simple_string(), self.object.home.zipcode
        )

        builder_organization = self.object.home.get_builder()

        with io.open(self.template_pdf, "rb") as template_file:
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=letter)

            center_x = letter[1] / 2

            # address line 1
            can.setFont("MuseoSans-500", 32)
            can.setFillColorRGB(0.176, 0.490, 0.180)
            can.drawCentredString(x=center_x, y=4.25 * inch, text=address_line1.upper())

            # address line 2
            can.setFont("MuseoSans-500", 32)
            can.setFillColorRGB(0.176, 0.490, 0.180)
            can.drawCentredString(x=center_x, y=3.65 * inch, text=address_line2.upper())

            # builder organization
            can.setFont("MuseoSans-500", 52)
            can.setFillColorRGB(0.0, 0.39, 0.62)
            can.drawCentredString(x=center_x, y=2.12 * inch, text=builder_organization.name)

            # verified by
            can.setFont("MuseoSans-500", 12)
            can.setFillColorRGB(0.0, 0.39, 0.62)
            can.drawCentredString(
                x=1.64 * inch,
                y=0.90 * inch,
                text=self.object.customer_hirl_final_verifier.get_full_name(),
            )

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

        response = HttpResponse(content_type=self.content_type)
        response["Content-Disposition"] = "attachment; filename={filename}".format(
            filename=self.get_filename()
        )
        response.write(output_stream.read())
        return response
