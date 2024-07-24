"""green_energy_badge.py: """

__author__ = "Artem Hruzd"
__date__ = "04/08/2021 17:37"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from axis.company.tests.factories import provider_organization_factory, builder_organization_factory
from axis.core.tests.testcases import AxisTestCase
from axis.customer_hirl.models import HIRLGreenEnergyBadge
from axis.customer_hirl.models import HIRLProjectRegistration
from axis.customer_hirl.tests.factories import (
    hirl_project_factory,
    hirl_green_energy_badge_factory,
    hirl_project_registration_factory,
)
from axis.eep_program.tests.factories import basic_eep_program_factory

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLGreenEnergyBadgeTests(AxisTestCase):
    def test_filter_by_eep_program(self):
        # creating badges
        net_zero_energy = hirl_green_energy_badge_factory(
            name="Net Zero Energy", slug="net_zero_energy"
        )
        resilience = hirl_green_energy_badge_factory(name="Resilience", slug="resilience")
        smart_home = hirl_green_energy_badge_factory(name="Smart Home", slug="smart_home")
        universal_design = hirl_green_energy_badge_factory(
            name="Universal Design", slug="universal_design"
        )
        wellness = hirl_green_energy_badge_factory(name="Wellness", slug="wellness")
        zero_water = hirl_green_energy_badge_factory(name="Zero Water", slug="zero_water")

        # map program slugs to expected badges
        data = {
            "ngbs-sf-new-construction-2020-new": [
                net_zero_energy,
                resilience,
                smart_home,
                universal_design,
                wellness,
                zero_water,
            ],
            "ngbs-mf-new-construction-2020-new": [
                net_zero_energy,
                resilience,
                smart_home,
                universal_design,
                wellness,
                zero_water,
            ],
            "ngbs-sf-whole-house-remodel-2020-new": [
                net_zero_energy,
                resilience,
                smart_home,
                universal_design,
                wellness,
            ],
            "ngbs-mf-whole-house-remodel-2020-new": [
                net_zero_energy,
                resilience,
                smart_home,
                universal_design,
                wellness,
            ],
            "ngbs-sf-certified-2020-new": [],
            "ngbs-sf-new-construction-2015-new": [],
            "ngbs-mf-new-construction-2015-new": [],
            "ngbs-sf-whole-house-remodel-2015-new": [],
            "ngbs-mf-whole-house-remodel-2015-new": [],
        }

        # iterate our mapped dict, create program and filter badges by program
        for program_slug, expected_badges in data.items():
            basic_eep_program_factory(name=program_slug, slug=program_slug)
            badges = HIRLGreenEnergyBadge.objects.filter_by_eep_program(slug=program_slug)

            self.assertListEqual(list(badges), expected_badges)

    def test_calculate_cost(self):
        eep_program = basic_eep_program_factory(
            name="SF 2020 New Construction",
            customer_hirl_certification_fee=100,
            customer_hirl_per_unit_fee=10,
        )
        provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )

        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program, project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE
        )
        sf_project = hirl_project_factory(
            street_line1="479 Washington St", registration=sf_registration
        )
        hirl_green_energy_badge = hirl_green_energy_badge_factory(name="Test Badge", cost=10)

        self.assertEqual(
            hirl_green_energy_badge.calculate_cost(
                hirl_project_registration_type=sf_project.registration.project_type,
                is_accessory_structure=sf_project.is_accessory_structure,
                is_accessory_dwelling_unit=sf_project.is_accessory_dwelling_unit,
                builder_organization=sf_project.registration.builder_organization,
                story_count=sf_project.story_count,
            ),
            10,
        )

        # test discount
        builder_organization = builder_organization_factory(slug="builder-neal-communities")
        sf_registration = hirl_project_registration_factory(
            eep_program=eep_program,
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
        )
        sf_project = hirl_project_factory(
            street_line1="479 Washington St", registration=sf_registration
        )
        wellness_green_energy_badge = hirl_green_energy_badge_factory(
            name="Wellness", slug="wellness", cost=100
        )

        self.assertEqual(
            wellness_green_energy_badge.calculate_cost(
                hirl_project_registration_type=sf_project.registration.project_type,
                is_accessory_structure=sf_project.is_accessory_structure,
                is_accessory_dwelling_unit=sf_project.is_accessory_dwelling_unit,
                builder_organization=sf_project.registration.builder_organization,
                story_count=sf_project.story_count,
            ),
            0,
        )

        mf_registration = hirl_project_registration_factory(
            eep_program=eep_program, project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE
        )

        mf_project = hirl_project_factory(
            street_line1="480 Washington St", registration=mf_registration, story_count=2
        )

        self.assertEqual(
            hirl_green_energy_badge.calculate_cost(
                hirl_project_registration_type=mf_project.registration.project_type,
                is_accessory_structure=mf_project.is_accessory_structure,
                is_accessory_dwelling_unit=mf_project.is_accessory_dwelling_unit,
                builder_organization=mf_project.registration.builder_organization,
                story_count=mf_project.story_count,
            ),
            20,
        )

        mf_project.story_count = 4
        mf_project.save()

        self.assertEqual(
            hirl_green_energy_badge.calculate_cost(
                hirl_project_registration_type=mf_project.registration.project_type,
                is_accessory_structure=mf_project.is_accessory_structure,
                is_accessory_dwelling_unit=mf_project.is_accessory_dwelling_unit,
                builder_organization=mf_project.registration.builder_organization,
                story_count=mf_project.story_count,
            ),
            60,
        )
