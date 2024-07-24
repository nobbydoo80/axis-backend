"""mixins.py - Axis"""

__author__ = "Steven K"
__date__ = "2/7/22 15:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from axis.checklist.tests.factories import (
    question_choice_factory,
    question_factory,
    checklist_factory,
)
from axis.company.models import Company
from axis.core.tests.factories import (
    eep_admin_factory,
    builder_admin_factory,
    provider_admin_factory,
    rater_admin_factory,
    general_admin_factory,
    qa_admin_factory,
)
from axis.eep_program.tests.factories import (
    basic_eep_program_checklist_factory,
    basic_eep_program_factory,
)
from axis.geographic.tests.factories import real_city_factory
from axis.home.models import EEPProgramHomeStatus
from axis.home.tests.factories import (
    certified_custom_home_with_basic_eep_factory,
    eep_program_home_status_factory,
    home_factory,
)
from axis.relationship.models import Relationship
from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory

log = logging.getLogger(__name__)


class CertificationTestMixin:
    @classmethod
    def setUpTestData(cls):
        city = real_city_factory(name="Gilbert", state="AZ")

        eep_admin = eep_admin_factory(company__city=city)
        builder_admin = builder_admin_factory(company__city=city)
        builder_org = Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE).get(
            id=builder_admin.company.id
        )

        provider_admin_0 = provider_admin_factory(company__city=city)
        rater_admin_0 = rater_admin_factory(company__city=city)

        companies = [
            builder_admin.company,
            eep_admin.company,
            provider_admin_0.company,
            rater_admin_0.company,
        ]
        Relationship.objects.create_mutual_relationships(*companies)

        fail_kw = {"document_required": False, "photo_required": False, "comment_required": True}
        na_kw = {"display_as_failure": True, "comment_required": True}
        pass_fail = [
            question_choice_factory(choice="Pass", choice_order=1),
            question_choice_factory(choice="Fail", choice_order=2, **fail_kw),
            question_choice_factory(choice="N/A", choice_order=3, **na_kw),
        ]

        basic_questions = [
            question_factory(
                question="Describe the front door",
                priority=1,
                allow_bulk_fill=True,
            ),
            question_factory(
                question="Verify the front door is on.",
                priority=2,
                allow_bulk_fill=True,
                question_choices=pass_fail,
            ),
            question_factory(
                question="Enter the date the door was installed",
                priority=3,
                allow_bulk_fill=True,
                type="date",
            ),
            question_factory(
                question="How many panels is the door",
                priority=4,
                allow_bulk_fill=True,
                type="integer",
            ),
            question_factory(
                question="What is the thickness of the door",
                priority=4,
                allow_bulk_fill=True,
                type="float",
                unit="inches",
            ),
        ]
        clists = [
            checklist_factory(
                name="Test Basic 5",
                questions=basic_questions,
                public=True,
            )
        ]
        basic_eep = basic_eep_program_checklist_factory(
            name="Single Checklist - Basic",
            max_hers_score=False,
            allow_sampling=True,
            required_checklists=clists,
            builder_incentive_dollar_value=0,
            owner=eep_admin.company,
            no_close_dates=True,
        )

        stat_0 = certified_custom_home_with_basic_eep_factory(
            company=provider_admin_0.company,
            eep_program=basic_eep,
            pct_complete=100,
            certify=False,
            home__lot_number="0ABC",
            home__builder_org=builder_org,
            home__street_line1="1 Should Pass",
            home__city=city,
        )
        assert stat_0.is_eligible_for_certification(), "Stat should be ready"

        stat_1 = certified_custom_home_with_basic_eep_factory(
            company=rater_admin_0.company,
            eep_program=basic_eep,
            pct_complete=100,
            certify=False,
            home__lot_number="1ABC",
            home__builder_org=builder_org,
            home__street_line1="1 rater_not pass",
            home__city=city,
        )

        Relationship.objects.validate_or_create_relations_to_entity(
            stat_1.home, provider_admin_0.company
        )

        # Now sampling stuffs
        sampleset = sampleset_with_subdivision_homes_factory(
            eepprogramhomestatus__company=rater_admin_0.company,
            eep_program=basic_eep,
            subdivision__builder_org=builder_org,
            subdivision__city=city,
            home__city=city,
            pct_complete=100,
            num_test_homes=3,
            revision=3,
            owner=rater_admin_0.company,
            alt_name="passing ss",
            num_homes=7,
        )

        for ss_stat in sampleset.samplesethomestatus_set.current():
            Relationship.objects.validate_or_create_relations_to_entity(
                ss_stat.home_status.home, provider_admin_0.company
            )
        assert (
            EEPProgramHomeStatus.objects.filter(state="complete").count() == 0
        ), "Certified homes?"
        assert (
            EEPProgramHomeStatus.objects.filter(certification_date__isnull=False).count() == 0
        ), "Certified Homes?"

        # A certified sampleset
        sampleset = sampleset_with_subdivision_homes_factory(
            eepprogramhomestatus__company=rater_admin_0.company,
            eep_program=basic_eep,
            subdivision__builder_org=builder_org,
            subdivision__city=city,
            home__city=city,
            pct_complete=100,
            num_test_homes=3,
            num_homes=5,
            revision=3,
            owner=rater_admin_0.company,
            alt_name="certified ss",
            certifier=provider_admin_0,
            certify=True,
        )
        assert (
            EEPProgramHomeStatus.objects.filter(state="complete").count() == 5
        ), "5 Certified homes?"
        assert (
            EEPProgramHomeStatus.objects.filter(certification_date__isnull=False).count() == 5
        ), "5 Certified Homes?"

        for ss_stat in sampleset.samplesethomestatus_set.current():
            Relationship.objects.validate_or_create_relations_to_entity(
                ss_stat.home_status.home, provider_admin_0.company
            )

        stat = eep_program_home_status_factory(
            company=rater_admin_0.company,
            eep_program=basic_eep,
            home__street_line1="1 uncertified way",
            home__subdivision__builder_org=builder_org,
            home__subdivision__city=city,
            home__city=city,
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            stat.home, provider_admin_0.company
        )

        # Late edition
        clists = [
            checklist_factory(
                name="Test Basic 3",
                questions=basic_questions[:3],
                public=True,
            )
        ]
        basic_eep_1 = basic_eep_program_checklist_factory(
            name="Single Checklist - Abbreviated",
            max_hers_score=False,
            allow_sampling=True,
            required_checklists=clists,
            builder_incentive_dollar_value=0,
            owner=eep_admin.company,
            no_close_dates=True,
        )

        stat = eep_program_home_status_factory(
            company=rater_admin_0.company,
            eep_program=basic_eep_1,
            home__street_line1="2 similar eep",
            home__subdivision__builder_org=builder_org,
            home__subdivision__city=city,
            home__city=city,
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            stat.home, provider_admin_0.company
        )

        # Finally Reverse this
        sampleset = sampleset_with_subdivision_homes_factory(
            eepprogramhomestatus__company=rater_admin_0.company,
            eep_program=basic_eep_1,
            subdivision__builder_org=builder_org,
            subdivision__city=city,
            home__city=city,
            pct_complete=100,
            num_test_homes=1,
            num_homes=2,
            revision=2,
            owner=rater_admin_0.company,
            alt_name="short ss",
            certifier=provider_admin_0,
            certify=True,
        )
        for ss_stat in sampleset.samplesethomestatus_set.current():
            Relationship.objects.validate_or_create_relations_to_entity(
                ss_stat.home_status.home, provider_admin_0.company
            )


class EEPProgramHomeStatusManagerTestMixin:
    @classmethod
    def setUpTestData(cls):
        city = real_city_factory(name="Turpin", state="OK")

        eep_user = eep_admin_factory(company__city=city, company__name="EEP1")
        eep_user_2 = eep_admin_factory(company__city=city, company__name="EEP2")
        general_user = general_admin_factory(company__city=city, company__name="General1")
        rater_user = rater_admin_factory(company__city=city, company__name="Rater1")
        provider_user = provider_admin_factory(company__city=city, company__name="Provider1")
        qa_user = qa_admin_factory(company__city=city, company__name="QA1")

        companies = [
            eep_user.company,
            general_user.company,
            rater_user.company,
            provider_user.company,
            qa_user.company,
        ]
        Relationship.objects.create_mutual_relationships(*companies)
        Relationship.objects.create_mutual_relationships(eep_user_2.company, general_user.company)

        unrestricted_eep = basic_eep_program_factory(
            name="Unrestricted Program 1", owner=eep_user.company, no_close_dates=True
        )
        restricted_eep = basic_eep_program_factory(
            name="Restricted Program 1",
            owner=eep_user.company,
            viewable_by_company_type="qa, provider",
            no_close_dates=True,
        )
        extra_eep = basic_eep_program_factory(
            name="Unrelated Unrestricted Program 1", owner=eep_user_2.company, no_close_dates=True
        )
        # Create Home stats
        home = home_factory(city=city)
        eep_program_home_status_factory(
            company=provider_user.company, eep_program=unrestricted_eep, home=home
        )
        eep_program_home_status_factory(
            company=provider_user.company, eep_program=restricted_eep, home=home
        )

        extra_home = home_factory(city=city)
        eep_program_home_status_factory(
            company=general_user.company, eep_program=extra_eep, home=extra_home
        )

        # Create relationships to home
        for company in companies:
            Relationship.objects.validate_or_create_relations_to_entity(home, company)


class HomeViewTestsMixins:
    """Fixture for Home View tests"""

    @classmethod
    def setUpTestData(cls):
        """Fixture populate method"""

        from axis.company.models import Company
        from axis.subdivision.models import Subdivision
        from axis.eep_program.models import EEPProgram
        from axis.floorplan.models import Floorplan

        from axis.relationship.models import Relationship
        from axis.relationship.utils import create_or_update_spanning_relationships

        from .factories import certified_home_with_checklist_factory, home_factory
        from axis.home.models import Home, EEPProgramHomeStatus
        from axis.company.tests.mixins import CompaniesAndUsersTestMixin

        cls.city = real_city_factory("Gilbert", "AZ")

        companies = CompaniesAndUsersTestMixin().build_company_relationships(
            city=cls.city,
            include_types=["builder", "eep", "provider", "rater", "general", "utility"],
        )

        assert Company.objects.all().count() == 12, "Company count mismatch {}".format(
            Company.objects.all().count()
        )

        from axis.subdivision.tests.factories import subdivision_factory

        subdivision = subdivision_factory(
            builder_org=Company.objects.get(id=companies["builder"].id), city=cls.city
        )
        # Need a couple homes..
        certifying_user = companies["provider"].users.filter(is_company_admin=True).first()
        kw = {}
        for idx in range(4):
            certify = True if idx < 1 else False
            pct_complete = 100 if idx < 2 else 75
            stat = certified_home_with_checklist_factory(
                eep_program__owner=companies["eep"],
                company=companies["rater"],
                home__subdivision=subdivision,
                home__street_line1=f"331{6+idx} E. Maplewood St",
                home__street_line2="",
                home__zipcode="85297",
                home__city=subdivision.city,
                pct_complete=pct_complete,
                certify=certify,
                certifying_user=certifying_user,
                **kw,
            )
            kw["eep_program"] = stat.eep_program
            kw["floorplan"] = stat.floorplan
            for company in companies.values():
                # Adds all parent relationships.
                create_or_update_spanning_relationships(company, stat)
                # TODO Fix this parent should be catching the subdivision no?
                Relationship.objects.validate_or_create_relations_to_entity(
                    stat.home.subdivision, company
                )

            for company in companies.values():
                Relationship.objects.validate_or_create_relations_to_entity(stat.home, company)

        home = home_factory(
            subdivision=subdivision,
            city=cls.city,
            street_line1="3330 E. Maplewood St",
            street_line2="",
            zipcode="85297",
        )
        Relationship.objects.validate_or_create_relations_to_entity(home, companies["rater"])

        assert Company.objects.all().count() == 12, "Company count mismatch {}".format(
            Company.objects.all().count()
        )
        assert Home.objects.all().count() == 5, "Homes.. {}".format(Home.objects.all().count())
        assert (
            EEPProgramHomeStatus.objects.filter(state="complete").count() == 1
        ), "1 Certified {}".format(EEPProgramHomeStatus.objects.filter(state="complete").count())
        assert Subdivision.objects.all().count() == 1, "Subdivisions {}".format(
            Subdivision.objects.all().count()
        )
        assert EEPProgram.objects.all().count() == 1, "Programs {}".format(
            EEPProgram.objects.all().count()
        )
        assert Floorplan.objects.all().count() == 1, "Floorplans {}".format(
            Floorplan.objects.all().count()
        )
        assert EEPProgramHomeStatus.objects.filter_by_company(companies["provider"]).count() == 4
        "Provider Relationships.. {}".format(
            EEPProgramHomeStatus.objects.filter_by_company(companies["provider"]).count()
        )
        assert (
            EEPProgramHomeStatus.objects.filter(
                pct_complete__gte=99.9, certification_date__isnull=True
            ).count()
            == 1
        )


class HostStatusReportMixin:
    @classmethod
    def setUpTestData(cls):
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.home.tests.factories import (
            home_factory,
            eep_program_home_status_factory,
            certified_custom_home_with_basic_eep_factory,
        )
        from axis.core.tests.factories import rater_user_factory, provider_admin_factory
        from axis.company.tests.factories import builder_organization_factory
        from axis.home.models import EEPProgramHomeStatus
        from axis.incentive_payment.models import IncentivePaymentStatus
        from axis.relationship.models import Relationship

        certifier = provider_admin_factory(username="certifier")

        user = rater_user_factory(username="tester")
        user.company.is_eep_sponsor = True
        user.company.save()
        builder = builder_organization_factory(name="Test Builder")

        sub_1 = subdivision_factory(builder_org=builder)
        sub_2 = subdivision_factory()
        eep_1 = basic_eep_program_factory(owner=user.company, no_close_dates=True)
        eep_2 = basic_eep_program_factory(owner=user.company, no_close_dates=True)

        stats_for_ipp = []
        for _ in range(3):
            home = home_factory(subdivision=sub_1, builder_org=builder)
            program = eep_program_home_status_factory(
                home=home, company=user.company, eep_program=eep_1
            )
            stats_for_ipp.append(program)

        assert builder.relationships.count() > 3, "there are not home attached to this builder"

        for _ in range(3):
            home = home_factory(subdivision=sub_2)
            program = eep_program_home_status_factory(
                home=home, company=user.company, eep_program=eep_2
            )
            stats_for_ipp.append(program)

        # filter by certification ------------------------------------------------------------------
        # Rater cannot certify own stat. Has to have a relationship with a provider
        Relationship.objects.create_mutual_relationships(user.company, certifier.company)
        certified_custom_home_with_basic_eep_factory(
            company=user.company, certifying_user=certifier, eep_program__no_close_dates=True
        )
        home = certified_custom_home_with_basic_eep_factory(
            company=user.company, certifying_user=certifier, eep_program__no_close_dates=True
        )

        # move some of the certification dates to the past
        home.certification_date -= datetime.timedelta(days=3)
        home.save()

        # filter by state --------------------------------------------------------------------------
        home = home_factory()
        eep_program_home_status_factory(
            home=home, company=user.company, eep_program__no_close_dates=True
        )

        home = home_factory()
        stat = eep_program_home_status_factory(
            home=home, company=user.company, eep_program__no_close_dates=True
        )
        stat.created_date -= datetime.timedelta(days=3)
        stat.save()

        certified_custom_home_with_basic_eep_factory(
            certify=False,
            company=user.company,
            certifying_user=certifier,
            eep_program__no_close_dates=True,
        )

        # transitioning eep ------------------------------------------------------------------------
        pending_inspection = []
        inspection = ["inspection_transition"]
        qa_pending = inspection + ["qa_transition"]
        certification_pending = qa_pending + ["certification_transition"]
        complete = certification_pending + ["completion_transition"]
        abandoned = ["to_abandoned_transition"]
        failed = ["to_failed_transition"]

        state_transitions = [
            pending_inspection,
            inspection,
            qa_pending,
            certification_pending,
            complete,
            abandoned,
            failed,
        ]

        kwargs = {"city": home.city}

        EEPProgramHomeStatus.objects.create(eep_program=eep_1, home=home, company=user.company)

        stats = []
        for i, flow in enumerate(state_transitions):
            home = home_factory(subdivision=sub_1, **kwargs)
            home2 = home_factory(subdivision=sub_2, **kwargs)

            stat = EEPProgramHomeStatus.objects.create(
                eep_program=eep_1, home=home, company=user.company
            )
            stat2 = EEPProgramHomeStatus.objects.create(
                eep_program=eep_2, home=home2, company=user.company
            )

            stats.append(stat)

            stats_for_ipp.append(stat)
            stats_for_ipp.append(stat2)

            for step in flow:
                stat.make_transition(step)
                stat2.make_transition(step)

        for stat in stats:
            for history in stat.state_history.all():
                history.start_time -= datetime.timedelta(days=3)
                history.save()

        # transitioning ipp ------------------------------------------------------------------------
        ipps = []
        for stat in stats_for_ipp:
            ipps.append(IncentivePaymentStatus.objects.create(home_status=stat, owner=user.company))

        start = []
        ipp_payment_requirements = ["pending_requirements"]
        ipp_payment_failed_requirements = ["failed_requirements"]
        ipp_failed_restart = ipp_payment_failed_requirements + ["corrected_requirements"]
        ipp_payment_automatic_requirements = ipp_payment_requirements + [
            "pending_automatic_requirements"
        ]
        payment_pending = ipp_payment_automatic_requirements + ["pending_payment_requirements"]
        complete = payment_pending + ["pending_complete"]

        state_transitions = [
            start,
            ipp_payment_requirements,
            ipp_payment_failed_requirements,
            ipp_failed_restart,
            ipp_payment_automatic_requirements,
            payment_pending,
            complete,
        ]

        for i, ipp in enumerate(ipps):
            flow = state_transitions[i % len(state_transitions)]
            for step in flow:
                ipp.make_transition(step)

        # transitioning qastatus -------------------------------------------------------------------
        in_progress = ["received_to_in_progress"]
        complete = in_progress + ["in_progress_to_complete"]
        correction_required = in_progress + ["in_progress_to_correction_required"]
        correction_received = correction_required + ["correction_required_to_correction_received"]

        state_transitions = [in_progress, complete, correction_required, correction_received]

        from axis.qa.models import QAStatus, QARequirement

        provider_user = provider_admin_factory()
        requirement = QARequirement.objects.create(
            qa_company=provider_user.company, eep_program=eep_1
        )
        for i, stat in enumerate(stats_for_ipp):
            flow = state_transitions[i % len(state_transitions)]
            qa = QAStatus.objects.create(
                owner=user.company, requirement=requirement, home_status=stat
            )

            for step in flow:
                qa.make_transition(step)
