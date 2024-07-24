"""certificate.py: """

__author__ = "Artem Hruzd"
__date__ = "11/14/2022 23:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import io
import os

from PyPDF2 import PdfWriter, PdfReader
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from axis.annotation.models import Annotation
from axis.core.checks import register_reportlab_fonts
from axis.customer_hirl.models import HIRLProjectRegistration, HIRLGreenEnergyBadge, HIRLProject
from axis.customer_hirl.reports import CustomerHIRLLDProgramLetterCertificate
from axis.customer_hirl.utils import CERTIFICATION_LEVEL_MAP
from axis.home.models import EEPProgramHomeStatus
from axis.home.reports import CustomerHIRLBadgePDFReport
from axis.home.reports.customer_hirl_badge_report import WaterRatingImage
from axis.qa.models import QARequirement, QAStatus

register_reportlab_fonts()
customer_hirl_app = apps.get_app_config("customer_hirl")
User = get_user_model()


class CustomerHIRLCertificate:
    def __init__(self, home_status: EEPProgramHomeStatus, user: User):
        self.user = user
        self.home_status = home_status

    def get_filename(self):
        return f"Certificate {self.home_status.home.street_line1}.pdf"

    def generate(self):
        if self.home_status.eep_program.slug in [
            "ngbs-sf-new-construction-2020-new",
            "ngbs-mf-new-construction-2020-new",
            "ngbs-sf-whole-house-remodel-2020-new",
            "ngbs-mf-whole-house-remodel-2020-new",
            "ngbs-sf-certified-2020-new",
        ]:
            output_stream = self.generate_2020_certificate()
        elif self.home_status.eep_program.slug in customer_hirl_app.WRI_PROGRAM_LIST:
            output_stream = self.generate_wri_program_certificate()
        elif self.home_status.eep_program.slug in customer_hirl_app.LAND_DEVELOPMENT_PROGRAM_LIST:
            if (
                self.home_status.customer_hirl_project.land_development_project_type
                == HIRLProject.LD_PROJECT_TYPE_LETTER_PROJECT
            ):
                output_stream = self.generate_ld_program_letter_certificate()
            else:
                output_stream = self.generate_ld_program_certificate()
        else:
            output_stream = self.generate_2012_2015_and_legacy_certificate()

        return output_stream

    def generate_2020_certificate(self):
        template_pdf_path = os.path.join(
            "axis", "home", "static", "templates", "2020_scoring_path_template.pdf"
        )

        hirl_project = getattr(self.home_status, "customer_hirl_project")

        try:
            final_qa = self.home_status.qastatus_set.get(
                requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
            )
        except QAStatus.DoesNotExist:
            final_qa = None

        wri_score = None
        certification_level = "UNKNOWN"
        green_energy_badges = HIRLGreenEnergyBadge.objects.none()

        if final_qa:
            if final_qa.hirl_reviewer_wri_value_awarded:
                try:
                    wri_score = int(final_qa.hirl_reviewer_wri_value_awarded)
                except ValueError:
                    pass
            certification_level = final_qa.hirl_certification_level_awarded
            green_energy_badges = final_qa.hirl_badges_awarded.all()

        pdf_data_map = {
            "ngbs-sf-new-construction-2020-new": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-new-construction-2020-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-whole-house-remodel-2020-new": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-whole-house-remodel-2020-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-certified-2020-new": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
        }

        address_line1 = self.home_status.home.street_line1
        if self.home_status.home.street_line2:
            address_line1 += " {}".format(self.home_status.home.street_line2)

        address_line2 = "{} {}".format(
            self.home_status.home.city.as_simple_string(), self.home_status.home.zipcode
        )

        builder_organization = self.home_status.home.get_builder()

        certification_level = CERTIFICATION_LEVEL_MAP.get(certification_level)
        additional_pdf_data = pdf_data_map[self.home_status.eep_program.slug]

        if hirl_project and hirl_project.commercial_space_type:
            additional_pdf_data["title1"] = "THIS NON-RESIDENTIAL SPACE"
            additional_pdf_data["title1_1"] = "HAS MET THE STRINGENT REQUIREMENTS OF THE"
        elif hirl_project and hirl_project.is_accessory_structure:
            additional_pdf_data["title1"] = "THIS ACCESSORY STRUCTURE"
            additional_pdf_data["title1_1"] = "HAS MET THE STRINGENT REQUIREMENTS OF THE"
        elif hirl_project and hirl_project.is_accessory_dwelling_unit:
            additional_pdf_data["title1"] = "THIS ACCESSORY DWELLING UNIT"
            additional_pdf_data["title1_1"] = "HAS MET THE STRINGENT REQUIREMENTS OF THE"

        with io.open(template_pdf_path, "rb") as template_file:
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=(11 * inch, 17 * inch))

            # grade
            can.setFont("MuseoSans-500", 52)
            if hirl_project.commercial_space_type:
                if (
                    hirl_project.commercial_space_type
                    == HIRLProject.CORE_AND_SHELL_COMMERCIAL_SPACE_TYPE
                ):
                    text = "CORE AND SHELL"
                else:
                    text = "FULL FITTED-OUT AND EQUIPPED"

                can.setFillColorRGB(*certification_level["color"])
                can.drawRightString(x=10.5 * inch, y=6.42 * inch, text=certification_level["title"])
                can.setFont("MuseoSans-100", 25)
                can.setFillColorRGB(0.314, 0.322, 0.314)
                can.drawRightString(x=10.5 * inch, y=6.0 * inch, text=text)
            else:
                can.setFillColorRGB(*certification_level["color"])
                can.drawRightString(x=10.5 * inch, y=6.12 * inch, text=certification_level["title"])

            # title1
            # check if we have 2 or 3 lines for AS or CS title
            if additional_pdf_data.get("title1_1"):
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.314, 0.322, 0.314)
                can.drawRightString(
                    x=10.5 * inch, y=5.72 * inch, text=additional_pdf_data["title1"]
                )
                can.drawRightString(
                    x=10.5 * inch, y=5.42 * inch, text=additional_pdf_data["title1_1"]
                )
            else:
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.314, 0.322, 0.314)
                can.drawRightString(
                    x=10.5 * inch, y=5.50 * inch, text=additional_pdf_data["title1"]
                )

            # title2
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.314, 0.322, 0.314)
            can.drawRightString(x=10.5 * inch, y=5.12 * inch, text=additional_pdf_data["title2"])

            if hirl_project.registration.community_named_on_certificate:
                # project name
                can.setFont("MuseoSans-500", 14)
                can.setFillColorRGB(0.505, 0.670, 0.239)
                can.drawRightString(
                    x=10.5 * inch,
                    y=4.75 * inch,
                    text=hirl_project.registration.project_name.upper(),
                )

            if hirl_project.hud_disaster_case_number:
                base_y = 4.45
            else:
                base_y = 4.25
            # address line 1
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text=address_line1.upper())

            base_y = base_y - 0.3
            # address line 2
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text=address_line2.upper())

            if hirl_project.hud_disaster_case_number:
                base_y = base_y - 0.3
                can.setFont("MuseoSans-100", 11)
                can.setFillColorRGB(0.505, 0.670, 0.239)
                can.drawRightString(
                    x=10.5 * inch,
                    y=base_y * inch,
                    text=f"HUD CASE NUMBER {hirl_project.hud_disaster_case_number}".upper(),
                )

            if (
                hirl_project.registration.project_type
                == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
                # ignore builder label, because it is always on certificate below
                and hirl_project.registration.party_named_on_certificate
                != HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY
            ):
                base_y = 3.55

                organization_map = {
                    HIRLProjectRegistration.ARCHITECT_RESPONSIBLE_ENTITY: {
                        "title": "DESIGNED BY:",
                        "company_name": hirl_project.registration.architect_organization.name,
                    },
                    HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY: {
                        "title": "DEVELOPED BY:",
                        "company_name": hirl_project.registration.developer_organization.name,
                    },
                    HIRLProjectRegistration.COMMUNITY_OWNER_RESPONSIBLE_ENTITY: {
                        "title": "OWNED BY:",
                        "company_name": hirl_project.registration.community_owner_organization.name,
                    },
                }

                organization_data = organization_map[
                    hirl_project.registration.party_named_on_certificate
                ]

                # additional by label
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.314, 0.322, 0.314)
                can.drawRightString(x=10.5 * inch, y=base_y * inch, text=organization_data["title"])

                base_y = base_y - 0.30

                # organization by label
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.505, 0.670, 0.239)
                can.drawRightString(
                    x=10.5 * inch, y=base_y * inch, text=organization_data["company_name"].upper()
                )

                base_y = base_y - 0.40
            else:
                base_y = 3.25

            # built by label
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.314, 0.322, 0.314)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text="BUILT BY:")

            # builder organization name
            base_y = base_y - 0.30
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)

            if (
                hirl_project.registration.project_type
                == HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
                and hirl_project.registration.is_build_to_rent
            ):
                can.drawRightString(
                    x=10.5 * inch,
                    y=base_y * inch,
                    text=hirl_project.registration.developer_organization.name.upper(),
                )
            else:
                can.drawRightString(
                    x=10.5 * inch, y=base_y * inch, text=builder_organization.name.upper()
                )

            # builder organization address
            base_y = base_y - 0.30
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            if builder_organization.city:
                can.drawRightString(
                    x=10.5 * inch,
                    y=base_y * inch,
                    text=builder_organization.city.as_simple_string().upper(),
                )

            certification_number = hirl_project.certification_counter

            can.setFont("MuseoSans-500", 18)
            can.setFillColorRGB(0, 0, 0)
            can.drawRightString(
                x=10.5 * inch, y=1.75 * inch, text="Certificate #{}".format(certification_number)
            )

            # certification date
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=5.27 * inch,
                y=1.9 * inch,
                text=self.home_status.certification_date.strftime("%B %d, %Y"),
            )

            # badges
            badges_offset_x = 0
            badges_offset_y = 0

            badges_offset_x_max = 0

            for i, green_energy_badge in enumerate(green_energy_badges):
                can.setFont("MuseoSans-500", 14)
                can.setFillColorRGB(0.505, 0.670, 0.239)

                green_energy_badge_name = f"+{green_energy_badge.name}"
                green_energy_badge_name_width = can.stringWidth(green_energy_badge_name)

                can.roundRect(
                    x=1.5 * inch + badges_offset_x - 4,
                    y=2.85 * inch - badges_offset_y - 7,
                    width=green_energy_badge_name_width + 8,
                    height=22,
                    radius=0,
                    stroke=0,
                    fill=1,
                )
                can.setFillColorRGB(1, 1, 1)
                can.drawString(
                    x=1.5 * inch + badges_offset_x,
                    y=2.85 * inch - badges_offset_y,
                    text=green_energy_badge_name,
                )

                badges_offset_x += min(140, green_energy_badge_name_width + 15)
                badges_offset_x_max = max(badges_offset_x, badges_offset_x_max)
                if i == 2:
                    badges_offset_x = 0
                    badges_offset_y = 30

            # wri icon
            if (
                wri_score is not None
                and self.home_status.eep_program.slug
                not in [
                    "ngbs-sf-whole-house-remodel-2020-new",
                    "ngbs-mf-whole-house-remodel-2020-new",
                ]
                and not (
                    hirl_project
                    and (
                        hirl_project.is_accessory_structure
                        or hirl_project.is_accessory_dwelling_unit
                    )
                )
            ):
                wri_empty_cursor_path = os.path.join(
                    "axis",
                    "home",
                    "static",
                    "images",
                    "customer_hirl_badge_report",
                    "wri_empty_cursor.png",
                )

                wri_empty_cursor_path_width = 85.5
                wri_empty_cursor_path_height = 55.2

                can.drawImage(
                    wri_empty_cursor_path,
                    x=1.5 * inch + badges_offset_x_max - wri_empty_cursor_path_width / 4,
                    y=2.33 * inch,
                    width=wri_empty_cursor_path_width,
                    height=wri_empty_cursor_path_height,
                    mask="auto",
                )

                wri_score_x = 1.5 * inch + badges_offset_x_max + wri_empty_cursor_path_width / 8
                if wri_score >= 100:
                    wri_score_x = (
                        1.5 * inch + badges_offset_x_max + wri_empty_cursor_path_width / 14
                    )
                can.setFont("MuseoSans-500", 18)
                can.setFillColorRGB(0.0, 0.396, 0.624)
                can.drawString(
                    x=wri_score_x,
                    y=2.33 * inch + wri_empty_cursor_path_height / 2,
                    text=f"{wri_score}",
                )

            can.save()

            new_pdf = PdfReader(packet)

            pdf_template = PdfReader(template_file)
            output = PdfWriter()
            # merge templates
            page = pdf_template.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            if wri_score is not None or len(green_energy_badges):
                badges_pdf_cls = CustomerHIRLBadgePDFReport(home_status=self.home_status)
                badges_pdf_data = badges_pdf_cls.generate()
                badges_pdf = PdfReader(badges_pdf_data)
                for page_num in range(len(badges_pdf.pages)):
                    output.add_page(badges_pdf.pages[page_num])

            output_stream = io.BytesIO()
            output.write(output_stream)
            output_stream.seek(0)
        return output_stream

    def generate_2012_2015_and_legacy_certificate(self):
        template_pdf = os.path.join(
            "axis", "home", "static", "templates", "ngbs_scoring_path_sf_certificate_template.pdf"
        )
        hirl_project = None
        output_stream = io.BytesIO()

        if self._is_legacy_project:
            try:
                certification_level_annotation = self.home_status.annotations.get(
                    type__slug="certified-nat-gbs"
                ).content.lower()
            except ObjectDoesNotExist:
                certification_level_annotation = None
        else:
            hirl_project = getattr(self.home_status, "customer_hirl_project", None)
            if not hirl_project:
                return output_stream
            try:
                certification_level_annotation = self.home_status.qastatus_set.get(
                    requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
                ).hirl_certification_level_awarded
            except ObjectDoesNotExist:
                certification_level_annotation = None

        pdf_data_map = {
            "ngbs-sf-new-construction-2015-new": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-new-construction-2015-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-whole-house-remodel-2015-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-whole-house-remodel-2015-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-new-construction-2012-new": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-new-construction-2012-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-whole-house-remodel-2012-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-whole-house-remodel-2012-new": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            # legacy
            "ngbs-mf-new-construction-2012": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-new-construction-2012": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-remodel-building-2012": {
                "title1": "THIS REMODELED BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-whole-house-remodel-2012": {
                "title1": "THIS REMODELED BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2012 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-new-construction-2015": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-new-construction-2015": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-whole-house-remodel-2015": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-remodel-building-2015": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2015 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-new-construction-2020": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-new-construction-2020": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-sf-whole-house-remodel-2020": {
                "title1": "THIS HOME HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
            "ngbs-mf-remodel-building-2020": {
                "title1": "THIS BUILDING HAS MET THE STRINGENT REQUIREMENTS OF THE",
                "title2": "ICC/ASHRAE 700-2020 NATIONAL GREEN BUILDING STANDARD",
            },
        }

        use_raw = (
            self.user.company.display_raw_addresses
            # ignore display as entered for all NGBS Projects, because
            # for their registration we always use one address
            # and allow user to select even non geocoded address
            and not self.home_status.home.homestatuses.filter(
                customer_hirl_project__isnull=False
            ).count()
        )
        has_raw_fields = self.home_status.home.geocode_response and any(
            (
                getattr(self.home_status.home.geocode_response.geocode, k)
                for k in ["raw_street_line1", "raw_city", "raw_zipcode"]
            )
        )

        if use_raw and has_raw_fields:
            geocode = self.home_status.home.geocode_response.geocode

            address_line1 = geocode.raw_street_line1
            if geocode.raw_street_line2:
                address_line1 += " {}".format(geocode.raw_street_line2)

            address_line2 = "{} {}".format(
                geocode.raw_city.as_simple_string(),
                geocode.raw_zipcode,
            )
        else:
            address_line1 = self.home_status.home.street_line1
            if self.home_status.home.street_line2:
                address_line1 += " {}".format(self.home_status.home.street_line2)

            address_line2 = "{} {}".format(
                self.home_status.home.city.as_simple_string(), self.home_status.home.zipcode
            )

        builder_organization = self.home_status.home.get_builder()

        certification_level = CERTIFICATION_LEVEL_MAP.get(certification_level_annotation)
        additional_pdf_data = pdf_data_map.get(
            self.home_status.eep_program.slug, {"title1": "", "title2": ""}
        )

        if hirl_project and hirl_project.commercial_space_type:
            additional_pdf_data["title1"] = "THIS NON-RESIDENTIAL SPACE"
            additional_pdf_data["title1_1"] = "HAS MET THE STRINGENT REQUIREMENTS OF THE"
        elif hirl_project and hirl_project.is_accessory_structure:
            additional_pdf_data["title1"] = "THIS ACCESSORY STRUCTURE"
            additional_pdf_data["title1_1"] = "HAS MET THE STRINGENT REQUIREMENTS OF THE"
        elif hirl_project and hirl_project.is_accessory_dwelling_unit:
            additional_pdf_data["title1"] = "THIS ACCESSORY DWELLING UNIT"
            additional_pdf_data["title1_1"] = "HAS MET THE STRINGENT REQUIREMENTS OF THE"

        with io.open(template_pdf, "rb") as template_file:
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=(11 * inch, 17 * inch))

            # grade
            can.setFont("MuseoSans-500", 52)
            can.setFillColorRGB(*certification_level["color"])
            can.drawRightString(x=10.5 * inch, y=6.12 * inch, text=certification_level["title"])

            # title1
            # check if we have 2 or 3 lines for AS or CS title
            if additional_pdf_data.get("title1_1"):
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.314, 0.322, 0.314)
                can.drawRightString(
                    x=10.5 * inch, y=5.72 * inch, text=additional_pdf_data["title1"]
                )
                can.drawRightString(
                    x=10.5 * inch, y=5.42 * inch, text=additional_pdf_data["title1_1"]
                )
            else:
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.314, 0.322, 0.314)
                can.drawRightString(
                    x=10.5 * inch, y=5.50 * inch, text=additional_pdf_data["title1"]
                )

            # title2
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.314, 0.322, 0.314)
            can.drawRightString(x=10.5 * inch, y=5.12 * inch, text=additional_pdf_data["title2"])

            if hirl_project:
                if hirl_project.registration.community_named_on_certificate:
                    # project name
                    can.setFont("MuseoSans-500", 14)
                    can.setFillColorRGB(0.505, 0.670, 0.239)
                    can.drawRightString(
                        x=10.5 * inch,
                        y=4.55 * inch,
                        text=hirl_project.registration.project_name.upper(),
                    )
            else:
                if self.home_status.home and self.home_status.home.subdivision:
                    # subdivision name
                    can.setFont("MuseoSans-500", 14)
                    can.setFillColorRGB(0.505, 0.670, 0.239)
                    can.drawRightString(
                        x=10.5 * inch,
                        y=4.55 * inch,
                        text=self.home_status.home.subdivision.name.upper(),
                    )

            hud_disaster_case_number = None
            if self._is_legacy_project:
                try:
                    certification_number_annotation = self.home_status.annotations.get(
                        type__slug="hud-disaster-case-number"
                    )
                    hud_disaster_case_number = certification_number_annotation.content.lower()
                except Annotation.DoesNotExist:
                    hud_disaster_case_number = ""
            else:
                if hirl_project and hirl_project.hud_disaster_case_number:
                    hud_disaster_case_number = hirl_project.hud_disaster_case_number

            if hud_disaster_case_number:
                base_y = 4.45
            else:
                base_y = 4.25

            # address line 1
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text=address_line1.upper())

            base_y = base_y - 0.3
            # address line 2
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text=address_line2.upper())

            if hud_disaster_case_number:
                base_y = base_y - 0.3
                can.setFont("MuseoSans-100", 11)
                can.setFillColorRGB(0.505, 0.670, 0.239)
                can.drawRightString(
                    x=10.5 * inch,
                    y=base_y * inch,
                    text=f"HUD CASE NUMBER {hud_disaster_case_number}".upper(),
                )

            if (
                hirl_project
                and hirl_project.registration.project_type
                == HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
                # ignore builder label, because it is always on certificate below
                and hirl_project.registration.party_named_on_certificate
                != HIRLProjectRegistration.BUILDER_RESPONSIBLE_ENTITY
            ):
                base_y = 3.55

                organization_map = {
                    HIRLProjectRegistration.ARCHITECT_RESPONSIBLE_ENTITY: {
                        "title": "DESIGNED BY:",
                        "company_name": hirl_project.registration.architect_organization.name,
                    },
                    HIRLProjectRegistration.DEVELOPER_RESPONSIBLE_ENTITY: {
                        "title": "DEVELOPED BY:",
                        "company_name": hirl_project.registration.developer_organization.name,
                    },
                    HIRLProjectRegistration.COMMUNITY_OWNER_RESPONSIBLE_ENTITY: {
                        "title": "OWNED BY:",
                        "company_name": hirl_project.registration.community_owner_organization.name,
                    },
                }

                organization_data = organization_map[
                    hirl_project.registration.party_named_on_certificate
                ]

                # additional by label
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.314, 0.322, 0.314)
                can.drawRightString(
                    x=10.5 * inch, y=base_y * inch, text=organization_data["title"].upper()
                )

                base_y = base_y - 0.30

                # organization by label
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.505, 0.670, 0.239)
                can.drawRightString(
                    x=10.5 * inch, y=base_y * inch, text=organization_data["company_name"].upper()
                )

                base_y = base_y - 0.40
            else:
                base_y = 3.25

            # built by label
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.314, 0.322, 0.314)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text="BUILT BY:")

            # builder organization name
            base_y = base_y - 0.30
            if builder_organization:
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.505, 0.670, 0.239)
                can.drawRightString(
                    x=10.5 * inch, y=base_y * inch, text=builder_organization.name.upper()
                )

            # builder organization address
            base_y = base_y - 0.30
            if builder_organization:
                can.setFont("MuseoSans-100", 14)
                can.setFillColorRGB(0.505, 0.670, 0.239)
                if builder_organization.city:
                    can.drawRightString(
                        x=10.5 * inch,
                        y=base_y * inch,
                        text=builder_organization.city.as_simple_string().upper(),
                    )

            # certificate id
            if self._is_legacy_project:
                certification_number_annotation = self.home_status.annotations.get(
                    type__slug="certification-number"
                )
                certification_number = certification_number_annotation.content.lower()
            else:
                certification_number = hirl_project.certification_counter

            can.setFont("MuseoSans-500", 18)
            can.setFillColorRGB(0, 0, 0)
            can.drawRightString(
                x=10.5 * inch, y=1.75 * inch, text="Certificate #{}".format(certification_number)
            )

            # certification date
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=1.55 * inch,
                y=1.75 * inch,
                text=self.home_status.certification_date.strftime("%B %d, %Y"),
            )

            can.save()

            new_pdf = PdfReader(packet)

            pdf_template = PdfReader(template_file)
            output = PdfWriter()
            # merge templates
            page = pdf_template.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            output.write(output_stream)
            output_stream.seek(0)

        return output_stream

    def generate_wri_program_certificate(self):
        template_path_pdf = os.path.join(
            "axis", "home", "static", "templates", "2021_wri_scoring_path_template.pdf"
        )

        hirl_project = getattr(self.home_status, "customer_hirl_project")

        try:
            final_qa = self.home_status.qastatus_set.get(
                requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
            )
        except QAStatus.DoesNotExist:
            final_qa = None

        wri_score = None

        if final_qa:
            if final_qa.hirl_reviewer_wri_value_awarded:
                try:
                    wri_score = int(final_qa.hirl_reviewer_wri_value_awarded)
                except ValueError:
                    pass

        address_line = f"{self.home_status.home.street_line1} "
        if self.home_status.home.street_line2:
            address_line += "{} ".format(self.home_status.home.street_line2)

        address_line += "{}, {}".format(
            self.home_status.home.city.as_simple_string(), self.home_status.home.zipcode
        )

        builder_organization = self.home_status.home.get_builder()

        with io.open(template_path_pdf, "rb") as template_file:
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=(11 * inch, 17 * inch))

            base_y = 8.2
            # address line 1
            can.setFont("Arial", 20)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(x=4.5 * inch, y=base_y * inch, text=address_line)

            # builder organization name
            base_y = base_y - 0.25
            can.setFont("Arial", 16)
            can.drawCentredString(
                x=4.5 * inch, y=base_y * inch, text=f"Built by: {builder_organization.name.upper()}"
            )

            # certification number
            base_y = base_y - 0.25
            certification_number = hirl_project.wri_certification_counter

            can.setFont("Arial", 16)
            can.drawCentredString(
                x=4.5 * inch, y=base_y * inch, text=f"WRI Certificate #{certification_number}"
            )

            # certification date
            can.setFont("Arial", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=5.85 * inch,
                y=5.85 * inch,
                text=self.home_status.certification_date.strftime("%B %d, %Y"),
            )

            if wri_score:
                water_rating = WaterRatingImage(wri=wri_score, width=462, height=131)
                water_rating.canv = can
                water_rating._offs_x = 1.2 * inch
                water_rating._offs_y = 3.15 * inch
                water_rating.draw()

            # water savings
            try:
                designed_indoor_total = self.home_status.annotations.get(
                    type__slug=f"designed-indoor-total-{self.home_status.eep_program.slug}-final"
                ).content
                designed_indoor_total = float(designed_indoor_total)

                designed_outdoor_total = self.home_status.annotations.get(
                    type__slug=f"designed-outdoor-total-{self.home_status.eep_program.slug}-final"
                ).content
                designed_outdoor_total = float(designed_outdoor_total)

                baseline_indoor_total = self.home_status.annotations.get(
                    type__slug=f"baseline-indoor-total-{self.home_status.eep_program.slug}-final"
                ).content
                baseline_indoor_total = float(baseline_indoor_total)

                baseline_outdoor = self.home_status.annotations.get(
                    type__slug=f"baseline-outdoor-{self.home_status.eep_program.slug}-final"
                ).content
                baseline_outdoor = float(baseline_outdoor)

                water_savings = int(
                    (
                        (designed_indoor_total + designed_outdoor_total)
                        - (baseline_indoor_total + baseline_outdoor)
                    )
                    / (baseline_indoor_total + baseline_outdoor)
                    * 100
                )
            except ObjectDoesNotExist:
                water_savings = "0"

            can.setFont("Arial", 48)
            can.setFillColorRGB(0.125, 0.220, 0.392)
            can.drawCentredString(
                x=2.43 * inch,
                y=2.10 * inch,
                text=f"{water_savings}%",
            )

            # gallons saved
            try:
                gallons_saved = self.home_status.annotations.get(
                    type__slug=f"gallons-saved-{self.home_status.eep_program.slug}-final"
                ).content.lower()
            except ObjectDoesNotExist:
                gallons_saved = "0"

            can.setFont("Arial", 48)
            can.setFillColorRGB(0.125, 0.220, 0.392)
            can.drawCentredString(
                x=6.28 * inch,
                y=2.10 * inch,
                text=f"{int(gallons_saved):,}",
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
        return output_stream

    def generate_ld_program_certificate(self):
        template_pdf = os.path.join(
            "axis", "home", "static", "templates", "2020_scoring_path_template.pdf"
        )

        hirl_project = self.home_status.customer_hirl_project

        try:
            final_qa = self.home_status.qastatus_set.get(
                requirement__type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE
            )
        except QAStatus.DoesNotExist:
            final_qa = None

        customer_hirl_ld_star_path = None

        if final_qa:
            certification_level = final_qa.hirl_certification_level_awarded
            # certification level is the same as our file name
            customer_hirl_ld_star_path = os.path.join(
                "axis",
                "home",
                "static",
                "images",
                "customer_hirl_ld_report",
                f"{certification_level}.png",
            )

        address_line1 = self.home_status.home.street_line1
        if self.home_status.home.street_line2:
            address_line1 += " {}".format(self.home_status.home.street_line2)

        address_line2 = "{} {}".format(
            self.home_status.home.city.as_simple_string(), self.home_status.home.zipcode
        )

        with io.open(template_pdf, "rb") as template_file:
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=(11 * inch, 17 * inch))

            # draw stars
            if customer_hirl_ld_star_path:
                can.drawImage(
                    customer_hirl_ld_star_path,
                    x=6.3 * inch,
                    y=5.9 * inch,
                    width=300,
                    height=66,
                    mask="auto",
                )

            # title
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.314, 0.322, 0.314)
            can.drawRightString(
                x=10.5 * inch,
                y=5.52 * inch,
                text="THIS DEVELOPMENT HAS MET THE STRINGENT REQUIREMENTS OF THE",
            )
            can.drawRightString(
                x=10.5 * inch, y=5.22 * inch, text="ICC 700-2020 NATIONAL GREEN BUILDING STANDARD"
            )

            base_y = 4.25
            # address line 1
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text=address_line1.upper())

            base_y = base_y - 0.3
            # address line 2
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text=address_line2.upper())

            base_y = 3.25

            # built by label
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.314, 0.322, 0.314)
            can.drawRightString(x=10.5 * inch, y=base_y * inch, text="BUILT BY:")

            # builder organization name
            base_y = base_y - 0.30
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)

            can.drawRightString(
                x=10.5 * inch,
                y=base_y * inch,
                text=hirl_project.registration.developer_organization.name.upper(),
            )

            # developer organization address
            base_y = base_y - 0.30
            can.setFont("MuseoSans-100", 14)
            can.setFillColorRGB(0.505, 0.670, 0.239)
            if hirl_project.registration.developer_organization.city:
                can.drawRightString(
                    x=10.5 * inch,
                    y=base_y * inch,
                    text=hirl_project.registration.developer_organization.city.as_simple_string().upper(),
                )

            certification_number = self.home_status.customer_hirl_project.certification_counter

            can.setFont("MuseoSans-500", 18)
            can.setFillColorRGB(0, 0, 0)
            can.drawRightString(
                x=10.5 * inch, y=1.75 * inch, text="Certificate #{}".format(certification_number)
            )

            # certification date
            can.setFont("MuseoSans-100", 11)
            can.setFillColorRGB(0, 0, 0)
            can.drawCentredString(
                x=5.27 * inch,
                y=1.9 * inch,
                text=self.home_status.certification_date.strftime("%B %d, %Y"),
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
        return output_stream

    def generate_ld_program_letter_certificate(self):
        output = PdfWriter()

        ld_letter_cls = CustomerHIRLLDProgramLetterCertificate(home_status=self.home_status)
        letter_pdf_data = ld_letter_cls.generate()
        letter_pdf = PdfReader(letter_pdf_data)
        for page_num in range(len(letter_pdf.pages)):
            output.add_page(letter_pdf.pages[page_num])

        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)

        return output_stream

    @cached_property
    def _is_legacy_project(self):
        try:
            self.home_status.annotations.get(type__slug="certified-nat-gbs")
            return True
        except ObjectDoesNotExist:
            return False
