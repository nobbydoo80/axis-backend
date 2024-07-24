"""test_utils.py - axis"""

__author__ = "Steven K"
__date__ = "7/20/22 10:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.test import TestCase

from axis.company.models import Company
from axis.company.tests.factories import base_company_factory
from axis.geographic.tests.factories import real_city_factory
from axis.geographic.utils.country import resolve_country
from axis.home.tasks import associate_nightly_companies_to_homestatuses
from axis.home.tests.factories import eep_program_custom_home_status_factory
from axis.home.utils import associate_companies_to_homestatuses

log = logging.getLogger(__name__)


class HomeUtilsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = real_city_factory("Ames", "IA")
        for slug in ["neea", "buildingnc", "eto", "rater", "builder"]:
            company = base_company_factory(
                name=slug.capitalize(),
                city=cls.city,
                slug=slug,
                company_type="general" if slug not in ["rater", "builder"] else slug,
            )
            setattr(cls, slug, company)
        cls.home_status = eep_program_custom_home_status_factory(
            company=cls.rater,
            floorplan__owner=cls.rater,
            eep_program__name="ESTAR",
            eep_program__slug="energy-star-version-31-rev-08",
            eep_program__owner=cls.buildingnc,
            home__builder_org=cls.builder,
            home__city=cls.city,
        )
        cls.home = cls.home_status.home
        cls.pr = resolve_country("PR")

    def test_setup(self):
        for slug in ["neea", "buildingnc", "eto", "rater", "builder"]:
            self.assertEqual(Company.objects.get(slug=slug).countries.count(), 1)
            self.assertEqual(Company.objects.get(slug=slug).counties.count(), 1)

    def test_associations(self):
        """Primarily for test coverage"""
        self.assertIsNone(associate_nightly_companies_to_homestatuses())

    def test_associate_companies_to_homestatuses(self):
        # We expect 3 relationships by default
        self.assertEqual(self.home_status.home.relationships.count(), 3)
        expected = {self.rater.pk, self.builder.pk, self.buildingnc.pk}
        values = set(self.home_status.home.relationships.values_list("company", flat=True))
        self.assertEqual(expected, values)

        # No associations
        self.assertEqual(self.home_status.associations.count(), 0)

        associate_companies_to_homestatuses(
            [self.eto.slug, self.neea.slug], [self.home_status.eep_program.slug]
        )

        self.assertEqual(self.home_status.associations.count(), 2)

    def test_associate_companies_to_homestatuses_wrong_location(self):
        """Verify that that if the company cares about outside of US"""

        self.neea.counties.clear()
        self.neea.countries.add(self.pr)
        self.neea.refresh_from_db()

        # We expect 3 relationships by default
        self.assertEqual(self.home_status.associations.count(), 0)

        associate_companies_to_homestatuses(
            [self.eto.slug, self.neea.slug], [self.home_status.eep_program.slug]
        )

        self.assertEqual(self.home_status.associations.count(), 1)
        self.assertEqual(self.home_status.associations.get().company.pk, self.eto.pk)

    def test_associate_companies_to_homestatuses_country_location(self):
        """Verify that that home is outside of the US we catch it."""
        self.neea.counties.clear()
        self.neea.countries.add(self.pr)

        self.city.country = self.pr
        self.city.county = None
        self.city.save()
        self.city.refresh_from_db()

        # We expect 3 relationships by default
        self.assertEqual(self.home_status.associations.count(), 0)

        associate_companies_to_homestatuses(
            [self.eto.slug, self.neea.slug], [self.home_status.eep_program.slug]
        )

        self.assertEqual(self.home_status.associations.count(), 1)
        self.assertEqual(self.home_status.associations.get().company.pk, self.neea.pk)
