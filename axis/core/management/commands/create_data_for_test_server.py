# -*- coding: utf-8 -*-
"""create_data_for_test_server.py: """

__author__ = "Artem Hruzd"
__date__ = "10/25/2022 19:12"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.conf import settings
from django.contrib.auth import get_user_model
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from axis.customer_hirl.models import HIRLUserProfile
from axis.customer_hirl.tests.factories import builder_agreement_factory
from axis.company.models import AltName, SponsorPreferences, Company
from axis.company.tests.factories import (
    builder_organization_factory,
    provider_organization_factory,
    rater_organization_factory,
)
from axis.core.tests.factories import (
    builder_user_factory,
    rater_user_factory,
    provider_user_factory,
)
from axis.customer_hirl.tests.factories import coi_document_factory, verifier_agreement_factory
from axis.customer_hirl.verifier_agreements.states import VerifierAgreementStates
from axis.geographic.models import County, Country
from axis.geographic.tests.factories import real_city_factory
from axis.relationship.models import Relationship
from axis.user_management.models import Accreditation
from axis.user_management.tests.factories import accreditation_factory

User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class Command(BaseCommand):
    help = """
    Test Servers only: Create test objects for test servers.
    """

    DATASETS = [
        "bob_customer_hirl",
    ]

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--dataset",
            dest="dataset",
            required=True,
            help=f"Choose dataset name, based on your requirements. "
            f"Available options: {self.DATASETS}",
        )

    def handle(self, *args, **options):
        if settings.SERVER_TYPE == settings.PRODUCTION_SERVER_TYPE:
            raise CommandError("Command is not available on production")

        dataset = options["dataset"]

        getattr(self, f"_{dataset}")()

    def _bob_customer_hirl(self):
        """
        Create:
        - AAA Green Builders
        - ABC Energy Ratings
        """
        try:
            customer_hirl_company = customer_hirl_app.get_customer_hirl_provider_organization()
        except Company.DoesNotExist:
            customer_hirl_company = provider_organization_factory(
                name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
            )
        test_slug = "bob_customer_hirl"
        default_user_password = "P@$$W0rd1900"
        charleston_city = real_city_factory(name="Charleston", state="SC")

        self.stdout.write(self.style.SUCCESS(f"{customer_hirl_company}"))

        self.stdout.write(self.style.SUCCESS(f"----Users"))
        self.stdout.write(self.style.SUCCESS(f"--------Robert Burns"))
        rburns_ngbs = provider_user_factory(
            first_name="Robert",
            last_name="Burns",
            username="rburnsNGBS",
            email="rburns@pivotalenergysolutions.com",
            work_phone="(480) 440-0345",
            company=customer_hirl_company,
            is_company_admin=True,
            is_active=True,
            is_approved=True,
            is_public=True,
        )
        self.stdout.write(self.style.SUCCESS(f"--------NGBS QA 1"))
        ngbs_qa_1 = provider_user_factory(
            first_name="NGBS",
            last_name="QA 1",
            username="ngbs_qa_1",
            email="NGBSqa1@example.com",
            work_phone="(480) 440-0345",
            company=customer_hirl_company,
            is_company_admin=True,
            is_active=True,
            is_approved=True,
            is_public=False,
        )
        self.stdout.write(self.style.SUCCESS(f"------------HIRLUserProfile"))
        HIRLUserProfile.objects.update_or_create(user=ngbs_qa_1, defaults=dict(is_qa_designee=True))
        self.stdout.write(self.style.SUCCESS(f"Done"))

        aaa_green_builders_name = "AAA Green Builders"
        self.stdout.write(self.style.SUCCESS(f"Creating {aaa_green_builders_name}"))
        aaa_green_builders = builder_organization_factory(
            name=aaa_green_builders_name,
            street_line1="456 Main St",
            city=charleston_city,
            zipcode="29407",
            office_phone="(480) 440-0345",
            default_email="NGBSbuilder@gmail.com",
            home_page="",
        )

        aaa_green_builders.slug = f"{test_slug}_aaa_green_builders"
        aaa_green_builders.auto_add_direct_relationships = True

        aaa_green_builders.save()

        self.stdout.write(self.style.SUCCESS(f"----Counties and countries"))
        counties = County.objects.filter(
            state__in=[
                "MA",
                "SC",
            ]
        )
        aaa_green_builders.counties.add(*counties)

        countries = Country.objects.filter(
            abbr__in=[
                "US",
                "PR",
            ]
        )
        aaa_green_builders.countries.add(*countries)
        self.stdout.write(self.style.SUCCESS(f"----Alternative names"))

        AltName.objects.update_or_create(
            company=aaa_green_builders, defaults=dict(name="AAA Green Builders of SC")
        )

        self.stdout.write(self.style.SUCCESS(f"----Sponsor Preferences"))
        SponsorPreferences.objects.update_or_create(
            sponsor=customer_hirl_company,
            sponsored_company=aaa_green_builders,
            defaults=dict(
                can_edit_profile=True, can_edit_identity_fields=True, notify_sponsor_on_update=True
            ),
        )

        self.stdout.write(self.style.SUCCESS(f"----Certificate Of Insurance"))
        aaa_green_builders.coi_documents.all().delete()
        coi_document_factory(company=aaa_green_builders, description="Auto generated")
        coi_document_factory(company=aaa_green_builders, description="Auto generated")

        self.stdout.write(self.style.SUCCESS(f"----Customer HIRL Client Agreement"))
        builder_agreement_factory(owner=customer_hirl_company, company=aaa_green_builders)
        self.stdout.write(self.style.SUCCESS(f"----Users"))
        self.stdout.write(self.style.SUCCESS("--------Pat Johnson"))
        pat_johnson = builder_user_factory(
            company=aaa_green_builders,
            username=f"{test_slug}_pat_johnson",
            first_name="Pat",
            last_name="Johnson",
            title="AXIS Administrator",
            email="NGBSbuilder@gmail.com",
            work_phone="(480) 440-0345",
            is_company_admin=True,
            is_approved=True,
            is_active=True,
            department="",
            is_public=True,
            is_staff=False,
            is_superuser=False,
            timezone_preference="America/New_York",
        )
        pat_johnson.set_password(default_user_password)

        self.stdout.write(self.style.SUCCESS(f"Done"))

        zzz_green_builders_name = "ZZZ Green Builders"
        self.stdout.write(self.style.SUCCESS(f"Creating {zzz_green_builders_name}"))
        zzz_green_builders = builder_organization_factory(
            name=zzz_green_builders_name,
            street_line1="789 Main St.",
            city=charleston_city,
            zipcode="99999",
            office_phone="",
            default_email="",
            home_page="",
        )

        zzz_green_builders.slug = f"{test_slug}_zzz_green_builders"
        zzz_green_builders.auto_add_direct_relationships = True

        zzz_green_builders.save()

        self.stdout.write(self.style.SUCCESS(f"----Counties and countries"))
        counties = County.objects.filter(
            state__in=[
                "SC",
            ]
        )
        zzz_green_builders.counties.add(*counties)

        countries = Country.objects.filter(
            abbr__in=[
                "US",
                "PR",
            ]
        )
        zzz_green_builders.countries.add(*countries)

        self.stdout.write(self.style.SUCCESS(f"----Sponsor Preferences"))
        SponsorPreferences.objects.update_or_create(
            sponsor=customer_hirl_company,
            sponsored_company=zzz_green_builders,
            defaults=dict(
                can_edit_profile=True, can_edit_identity_fields=True, notify_sponsor_on_update=True
            ),
        )

        self.stdout.write(self.style.SUCCESS(f"----Certificate Of Insurance"))
        zzz_green_builders.coi_documents.all().delete()
        coi_document_factory(company=zzz_green_builders, description="Auto generated")
        coi_document_factory(company=zzz_green_builders, description="Auto generated")

        self.stdout.write(self.style.SUCCESS(f"----Customer HIRL Client Agreement"))
        builder_agreement_factory(owner=customer_hirl_company, company=zzz_green_builders)
        self.stdout.write(self.style.SUCCESS(f"----Users"))
        self.stdout.write(self.style.SUCCESS("--------Harper Thomas"))
        harper_thomas = builder_user_factory(
            company=zzz_green_builders,
            username=f"{test_slug}_harper_thomas",
            first_name="Harper",
            last_name="Thomas",
            title="AXIS Administrator",
            email="bob@rburnsconsulting.com",
            work_phone="(888) 888-8888",
            is_company_admin=True,
            is_approved=True,
            is_active=True,
            department="",
            is_public=False,
            is_staff=False,
            is_superuser=False,
            timezone_preference="America/New_York",
        )
        harper_thomas.set_password(default_user_password)

        self.stdout.write(self.style.SUCCESS(f"Done"))

        abc_energy_ratings_name = "ABC Energy Ratings"
        self.stdout.write(self.style.SUCCESS(f"Creating {abc_energy_ratings_name}"))
        abc_energy_ratings = builder_organization_factory(
            name=abc_energy_ratings_name,
            street_line1="123 King St",
            city=charleston_city,
            zipcode="29401",
            office_phone="(480) 440-0345",
            default_email="admin@abc.com",
            home_page="",
        )

        abc_energy_ratings.slug = f"{test_slug}_abc_energy_ratings"
        abc_energy_ratings.auto_add_direct_relationships = True

        abc_energy_ratings.save()

        self.stdout.write(self.style.SUCCESS(f"----Counties and countries"))
        counties = County.objects.filter(
            state__in=[
                "GA",
                "SC",
            ]
        )
        abc_energy_ratings.counties.add(*counties)

        countries = Country.objects.filter(
            abbr__in=[
                "US",
                "PR",
            ]
        )
        abc_energy_ratings.countries.add(*countries)

        self.stdout.write(self.style.SUCCESS(f"----Sponsor Preferences"))
        SponsorPreferences.objects.update_or_create(
            sponsor=customer_hirl_company,
            sponsored_company=abc_energy_ratings,
            defaults=dict(
                can_edit_profile=True, can_edit_identity_fields=True, notify_sponsor_on_update=True
            ),
        )

        self.stdout.write(self.style.SUCCESS(f"----Certificate Of Insurance"))
        abc_energy_ratings.coi_documents.all().delete()
        coi_document_factory(
            company=abc_energy_ratings, document=__file__, description="Auto generated"
        )
        coi_document_factory(
            company=abc_energy_ratings, document=__file__, description="Auto generated"
        )

        self.stdout.write(self.style.SUCCESS(f"----Users"))

        self.stdout.write(self.style.SUCCESS("--------Remi Smith"))
        remi_smith = rater_user_factory(
            company=abc_energy_ratings,
            username=f"{test_slug}_remi_smith",
            first_name="Remi",
            last_name="Smith",
            title="AXIS Administrator",
            email="ngbsverifier@gmail.com",
            work_phone="(201) 555-0123",
            is_company_admin=True,
            is_approved=True,
            is_active=True,
            department="",
            is_public=False,
            is_staff=False,
            is_superuser=False,
            timezone_preference="America/New_York",
        )
        remi_smith.set_password(default_user_password)

        self.stdout.write(self.style.SUCCESS("------------Accreditations"))
        remi_smith.accreditations.all().delete()

        accreditation_factory(
            name=Accreditation.NGBS_2020_NAME,
            trainee=remi_smith,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            name=Accreditation.NGBS_2015_NAME,
            trainee=remi_smith,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            name=Accreditation.NGBS_2012_NAME,
            trainee=remi_smith,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            name=Accreditation.MASTER_VERIFIER_NAME,
            trainee=remi_smith,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            name=Accreditation.NGBS_WRI_VERIFIER_NAME,
            trainee=remi_smith,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            name=Accreditation.NGBS_GREEN_FIELD_REP_NAME,
            trainee=remi_smith,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )
        self.stdout.write(self.style.SUCCESS("------------Verifier Agreement"))
        remi_smith.customer_hirl_enrolled_verifier_agreements.all().delete()
        verifier_agreement_factory(
            owner=customer_hirl_company,
            verifier=remi_smith,
            state=VerifierAgreementStates.COUNTERSIGNED,
        )

        self.stdout.write(self.style.SUCCESS("--------Angel Davis"))
        angel_davis = rater_user_factory(
            company=abc_energy_ratings,
            username=f"{test_slug}_angel_davis",
            first_name="Angel",
            last_name="Davis",
            title="AXIS Administrator",
            email="ABCadmin2@example.com",
            work_phone="(480) 440-0345",
            is_company_admin=True,
            is_approved=True,
            is_active=True,
            department="",
            is_public=False,
            is_staff=False,
            is_superuser=False,
            timezone_preference="America/New_York",
        )
        angel_davis.set_password(default_user_password)

        self.stdout.write(self.style.SUCCESS("--------Rory Thompson"))
        rory_thompson = rater_user_factory(
            company=abc_energy_ratings,
            username=f"{test_slug}_rory_thompson",
            first_name="Rory",
            last_name="Thompson",
            title="AXIS Administrator",
            email="NGBSverifier@gmail.com",
            work_phone="(888) 888-8888",
            is_company_admin=False,
            is_approved=True,
            is_active=True,
            department="",
            is_public=False,
            is_staff=False,
            is_superuser=False,
            timezone_preference="America/New_York",
        )
        rory_thompson.set_password(default_user_password)
        self.stdout.write(self.style.SUCCESS("------------Accreditations"))
        rory_thompson.accreditations.all().delete()

        accreditation_factory(
            name=Accreditation.NGBS_2015_NAME,
            trainee=rory_thompson,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )
        accreditation_factory(
            name=Accreditation.MASTER_VERIFIER_NAME,
            trainee=rory_thompson,
            company=customer_hirl_company,
            approver=rburns_ngbs,
            state=Accreditation.ACTIVE_STATE,
        )

        self.stdout.write(self.style.SUCCESS("--------Jordan Jones"))
        jordan_jones = rater_user_factory(
            company=abc_energy_ratings,
            username=f"{test_slug}_jordan_jones",
            first_name="Jordan",
            last_name="Jones",
            title="AXIS Administrator",
            email="ngbsverifier@gmail.com",
            work_phone="(888) 888-8888",
            is_company_admin=False,
            is_approved=True,
            is_active=True,
            department="",
            is_public=False,
            is_staff=False,
            is_superuser=False,
            timezone_preference="America/New_York",
        )
        jordan_jones.set_password(default_user_password)

        self.stdout.write(self.style.SUCCESS("------------Verifier Agreement"))
        jordan_jones.customer_hirl_enrolled_verifier_agreements.all().delete()
        verifier_agreement_factory(
            owner=customer_hirl_company,
            verifier=jordan_jones,
            state=VerifierAgreementStates.EXPIRED,
        )

        self.stdout.write(self.style.SUCCESS(f"Done"))

        self.stdout.write(self.style.SUCCESS(f"Create Relationships"))
        Relationship.objects.create_mutual_relationships(
            aaa_green_builders, abc_energy_ratings, customer_hirl_company
        )
        self.stdout.write(self.style.SUCCESS(f"Done"))
