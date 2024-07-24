from django.views.generic import DetailView
from django.http import HttpResponse

from axis.core.mixins import AuthenticationMixin
from axis.filehandling.utils import populate_template_pdf
from ..models import EEPProgramHomeStatus

__author__ = "Autumn Valenta"
__date__ = "8/29/2019 4:36 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class BuiltGreenWACertificateDownload(AuthenticationMixin, DetailView):
    model = EEPProgramHomeStatus
    permission_required = "home.view_home"

    programs = [
        "built-green-wa-prescriptive",
        "built-green-wa-performance",
    ]

    template_pdf = "axis/home/static/templates/BGWACertNoSponsors.pdf"
    pages = 1
    filename = "Certificate of Merit - {instance.home.street_line1}.pdf"
    content_type = "application/pdf"

    coordinates = {
        0: {
            "address": (60, 335),
            "certification_level": (278, 299),
            "builder": (60, 201),
            "verification_company": (60, 152),
            "verification_date": (425, 152),
            "efficient_electric": (612, 72),
            "efficient_gas": (670, 72),
            "axis_id": (65, 36),
        },
    }
    fonts = {
        "default": ("Helvetica", 12),
        "address": ("Helvetica-Bold", 18),
        "certification_level": ("Helvetica", 18),
    }

    def get_queryset(self):
        """Allow only certified items with the built-green-wa-* programs."""
        return self.model.objects.filter_by_user(self.request.user).filter(
            state="complete",
            certification_date__isnull=False,
            eep_program__slug__in=self.programs,
        )

    def get_filename(self):
        return self.filename.format(instance=self.get_object())

    def get(self, request, *args, **kwargs):
        """Return download-type response of the rendered pdf."""
        response = HttpResponse(content_type=self.content_type)
        response["Content-Disposition"] = "attachment; filename={filename}".format(
            filename=self.get_filename()
        )
        context = self.get_context_data()
        f = self.populate_template_pdf(**context)
        response.write(f)
        return response

    def populate_template_pdf(self, **context):
        """Render homestatus information on the template pdf."""
        return populate_template_pdf(
            self.template_pdf,
            n_pages=self.pages,
            coordinates=self.coordinates,
            fonts=self.fonts,
            **context,
        )

    def get_context_data(self):
        home_status = self.get_object()
        home = home_status.home
        certification_level = home_status.annotations.get(
            type__slug="built-green-certification-level"
        ).content.replace("star", "Stars")

        return {
            "address": home.get_addr(include_city_state_zip=True, company=self.request.company),
            "certification_level": certification_level,
            "builder": home.get_builder().name,
            "verification_company": home_status.company.name,
            "verification_date": home_status.certification_date.strftime("%x"),
            "efficient_electric": "x",
            "efficient_gas": "x",
            "axis_id": home.get_id(),
        }
