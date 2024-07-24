"""home_status_export.py - Axis"""

import logging

from django.core.management import BaseCommand

from axis.customer_hirl.models import Certification
from axis.customer_neea.neea_data_report.models import NEEACertification
from axis.geocoder.models import Geocode
from axis.geographic.models import City
from axis.geographic.utils.city import resolve_city
from axis.home.models import Home

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "3/11/21 11:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class Command(BaseCommand):
    help = "Fix bad home states on imported certs"
    requires_system_checks = []

    def find_incorrect_matches_for_certs(self, certifications, expected_programs):
        unavailable, corrected = [], []
        for cert in certifications:
            home = cert.home
            if cert.state_abbreviation == home.state:
                continue

            programs_slugs = cert.home.homestatuses.values_list("eep_program__slug", flat=True)
            if home.homestatuses.count() > 1:
                log.warning("Multiples found on cert %s" % cert.id)
                continue
            if programs_slugs[0] not in expected_programs:
                log.warning("Unexpected program %s found on cert %s" % (programs_slugs[0], cert.id))
                continue

            try:
                corrected_city = resolve_city(
                    name=getattr(cert, "city"),
                    county=getattr(cert, "county"),
                    state_abbreviation=getattr(cert, "state"),
                    country=getattr(cert, "country"),
                )
            except ValueError as err:
                log.error(err)
                corrected_city = home.city

            update_kwargs = {}
            if corrected_city != home.city:
                update_kwargs["city_id"] = corrected_city.id
            if corrected_city.county != home.county:
                update_kwargs["county_id"] = corrected_city.county_id
            if corrected_city.county.metro_id != home.metro_id:
                update_kwargs["metro_id"] = corrected_city.county.metro_id
            if corrected_city.county.state != home.state:
                assert cert.state_abbreviation.lower() == corrected_city.county.state.lower()
                update_kwargs["state"] = corrected_city.county.state

            if update_kwargs:
                log.info("%s → %s %r", home.city, corrected_city, update_kwargs)
                Home.objects.filter(id=home.id).update(**update_kwargs)
                corrected.append(home.id)
            else:
                unavailable.append(cert.id)

        print(
            len(unavailable),
            "/",
            certifications.count(),
            "Certs were not corrected",
            len(corrected),
            "Corrected",
        )
        return unavailable

    def find_incorrect_expected_states_for_program(self, program):
        homes = Home.objects.filter(
            homestatuses__eep_program__slug=program, customer_neea_certification__isnull=True
        ).exclude(state__in=["ID", "MT", "OR", "WA"])

        unavail = []
        corrected = []
        for home in homes:
            if home.homestatuses.count() > 1:
                log.warning("Multiples found on home %s" % home.id)

            cities = City.objects.filter(
                name=home.city.name, county__state__in=["ID", "MT", "OR", "WA"]
            )
            city_states = list(set(cities.values_list("county__state", flat=True)))
            update_kwargs = {}

            if len(city_states) == 1:
                raw_address = "%s %s, %s, %s" % (
                    home.street_line1,
                    home.city.name,
                    city_states[0],
                    home.zipcode,
                )
            else:
                raw_address = "%s %s, %s" % (home.street_line1, home.city.name, home.zipcode)

            matches = Geocode.objects.get_matches(
                raw_address=raw_address, entity_type="street_address"
            )
            matches = (
                matches.confirmed().statistically_likely(return_higest=True).logically_reduce()
            )

            update_kwargs = {}
            if matches.count() == 1:
                try:
                    corrected_city = matches[0].get_normalized_fields()["city"]
                except KeyError:
                    corrected_city = home.city

                if corrected_city != home.city:
                    update_kwargs["city_id"] = corrected_city.id
                if corrected_city.county != home.county:
                    update_kwargs["county_id"] = corrected_city.county_id
                if corrected_city.county.metro_id != home.metro_id:
                    update_kwargs["metro_id"] = corrected_city.county.metro_id
                if corrected_city.county.state != home.state:
                    update_kwargs["state"] = corrected_city.county.state

                if not update_kwargs:
                    unavail.append(home.id)
                else:
                    log.info("%s → %s %r", home.city, corrected_city, update_kwargs)
                    Home.objects.filter(id=home.id).update(**update_kwargs)
                    corrected.append(home.id)
            else:
                log.warning("Multiple results found for %s %s" % (home.id, home.state))
                unavail.append(home.id)

        print(
            len(unavail),
            "/",
            homes.count(),
            "Certs were not corrected",
            len(corrected),
            "Corrected",
        )
        return unavail

    def handle(self, *args, **options):
        certs = NEEACertification.objects.filter(home__isnull=False)
        bad = self.find_incorrect_matches_for_certs(
            certs, expected_programs=["resnet-registry-data"]
        )
        print("%d NEEA Certs unable to be fixed or no changes: %r" % (len(bad), bad))

        bad = self.find_incorrect_expected_states_for_program("resnet-registry-data")
        print("%d NEEA Homes unable to be fixed multiple options: %r" % (len(bad), bad))

        certs = Certification.objects.filter(home__isnull=False)
        programs = [
            "ngbs-basement-remodel-2012",
            "ngbs-single-family-additions-75-1",
            "ngbs-green-subdivision",
            "ngbs-sf-new-construction-2015",
            "ngbs-green-building-renovations-with-additions-75",
            "ngbs-small-addition-2012",
            "ngbs-single-family-additions-75-2",
            "ngbs-single-family-new-construction",
            "ngbs-multi-unit-green-building-renovation",
            "ngbs-mf-remodel-building-2012",
            "ngbs-green-remodel-renovations-with-additions-75",
            "ngbs-kitchen-remodel-2012",
            "ngbs-bathroom-remodel-2012",
            "ngbs-renovations-with-addition-75",
            "ngbs-multi-unit-green-remodel-renovation",
            "ngbs-mf-new-construction-2015",
            "ngbs-single-family-green-building-renovation",
            "ngbs-sf-whole-house-remodel-2012",
            "ngbs-mf-new-construction-2012",
            "ngbs-green-subdivision-2012",
            "ngbs-single-family-green-remodel-renovation",
            "ngbs-multi-unit-new-construction",
            "ngbs-sf-new-construction-2012",
        ]

        bad = self.find_incorrect_matches_for_certs(certs, expected_programs=programs)
        print("%d HIRL Certs unable to be fixed or no changes: %r" % (len(bad), bad))
