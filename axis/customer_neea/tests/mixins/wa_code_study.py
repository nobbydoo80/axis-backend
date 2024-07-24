"""wa_code_study.py - Axis"""

__author__ = "Steven K"
__date__ = "7/20/21 09:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.core import management

from axis.core.tests.test_views import DevNull
from .base import CustomerNEEABaseTestMixin

log = logging.getLogger(__name__)


class WaCodeStudyProgramTestMixin(CustomerNEEABaseTestMixin):
    @classmethod
    def setUpTestData(cls):
        from axis.geocoder.models import Geocode
        from axis.home.tests.factories import custom_home_factory
        from axis.home.tests.factories import eep_program_custom_home_status_factory
        from axis.eep_program.models import EEPProgram
        from axis.company.models import Company
        from axis.annotation.models import Type as AnnotationType
        from axis.annotation.models import Annotation
        from django.contrib.contenttypes.models import ContentType

        super(WaCodeStudyProgramTestMixin, cls).setUpTestData()
        management.call_command(
            "build_program", "-p", "wa-code-study", "--no_close_dates", stdout=DevNull()
        )

        program = EEPProgram.objects.first()
        rater = Company.objects.get(slug="wa-code-study-rater")

        addr = {
            "street_line1": "4905 N Oberlin St",
            "street_line2": None,
            "city": cls.city,
            "state": "OR",
            "zipcode": "97203",
        }
        matches = Geocode.objects.get_matches(raw_address=None, **addr)
        assert len(matches) == 1, "Bad geocode we need one we got {} - {}".format(
            len(matches), addr
        )
        addr.update({"geocode": True, "builder_org": cls.builder.company})
        home = custom_home_factory(**addr)

        stat = eep_program_custom_home_status_factory(home=home, eep_program=program, company=rater)

        dwelling_type = AnnotationType.objects.get(slug="dwelling-type")
        option_one = AnnotationType.objects.get(slug="efficient-building-envelope")
        option_two = AnnotationType.objects.get(slug="efficient-building-air-leakage")
        option_three = AnnotationType.objects.get(slug="efficient-building-hvac")
        option_four = AnnotationType.objects.get(slug="efficient-building-hvac-distribution")
        option_five_a = AnnotationType.objects.get(slug="efficient-building-water-heating-5a")
        option_five_bc = AnnotationType.objects.get(slug="efficient-building-water-heating-5bc")
        option_five_d = AnnotationType.objects.get(slug="efficient-building-water-heating-5d")
        option_six = AnnotationType.objects.get(slug="efficient-building-renewable-energy")
        AnnotationType.objects.get(slug="wa-code-study-score")

        Annotation.objects.create(
            type=dwelling_type,
            content="Small Dwelling",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_one,
            content="1a",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_two,
            content="2a",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_three,
            content="3a",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_four,
            content="4",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_five_a,
            content="5a",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_five_bc,
            content="5c",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_five_d,
            content="5d",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )

        Annotation.objects.create(
            type=option_six,
            content="1",
            content_type=ContentType.objects.get_for_model(stat),
            object_id=stat.id,
        )
