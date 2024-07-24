"""models.py: Django """


__author__ = "Steven Klass"
__date__ = "4/17/13 9:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timezone import now

from axis.company.models import Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.geocoder.api_v3.serializers import GeocodeMatchesSerializer
from axis.home import strings
from axis.home.tasks import certify_single_home
from axis.relationship.models import Relationship
from ..factories import certified_custom_home_with_basic_eep_factory
from ...models import EEPProgramHomeStatus, Home, HomePhoto
from ...signals import eep_program_certified

log = logging.getLogger(__name__)
User = get_user_model()


class HomeModelTests(AxisTestCase):
    """Test out homes app"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        """Fixture populate method"""
        from axis.core.tests.factories import (
            rater_admin_factory,
            provider_admin_factory,
            builder_admin_factory,
            qa_admin_factory,
            general_admin_factory,
            eep_admin_factory,
            utility_admin_factory,
            hvac_admin_factory,
        )
        from axis.home.tests.factories import certified_home_with_checklist_factory
        from axis.geographic.tests.factories import real_city_factory

        city = real_city_factory("Gilbert", "AZ")

        builder = builder_admin_factory(username="builder_1", company__city=city)
        builder_org = Company.objects.get(id=builder.company.id)

        rater_1 = rater_admin_factory(username="rater_1", company__city=city)
        provider_admin_factory(
            username="provider_1",
            company__provider_id="102-4321",
            company__city=city,
        )
        eep_1 = eep_admin_factory(
            username="eep_1",
            company__is_eep_sponsor=True,
            company__city=city,
        )
        utility_admin_factory(
            username="utility_1",
            company__city=city,
            company__electricity_provider=True,
            company__gas_provider=False,
            company__water_provider=False,
        )
        hvac_admin_factory(username="hvac_1", company__city=city)
        qa_admin_factory(username="qa_1", company__city=city)
        general_admin_factory(username="general_1", company__city=city)

        home_kwargs = {
            "company": rater_1.company,
            "eep_program__owner": eep_1.company,
            "home__subdivision__builder_org": builder_org,
            "home__city": city,
            "certify": False,
            "eep_program__no_close_dates": True,
        }
        home_status_1 = certified_home_with_checklist_factory(**home_kwargs)

        assert home_status_1.company == rater_1.company, "hs1 wrong company"
        assert home_status_1.eep_program.owner == eep_1.company, "hs1 wrong eep_program owner"
        assert home_status_1.home.get_builder().id == builder.company.id, "hs1 wrong builder"
        assert home_status_1.state == "certification_pending", "hs1 wrong state"
        assert home_status_1.is_eligible_for_certification(), "hs1 not eligible for certification"
        assert home_status_1.pct_complete == 100, "hs1 not 100 pct_complete"

        rater_2 = rater_admin_factory(username="rater_2", company__city=city)
        provider_admin_factory(
            username="provider_2", company__provider_id="102-4322", company__city=city
        )
        eep_2 = eep_admin_factory(
            username="eep_2", company__is_eep_sponsor=True, company__city=city
        )
        utility_admin_factory(
            username="utility_2",
            company__city=city,
            company__electricity_provider=False,
            company__gas_provider=True,
            company__water_provider=False,
        )
        hvac_admin_factory(username="hvac_2", company__city=city)
        qa_admin_factory(username="qa_2", company__city=city)
        general_admin_factory(username="general_2", company__city=city)

        home_status_2 = certified_home_with_checklist_factory(
            company=rater_2.company,
            eep_program__owner=eep_2.company,
            home=home_status_1.home,
            pct_complete=33,
            eep_program__no_close_dates=True,
        )

        assert home_status_2.company == rater_2.company, "hs2 wrong company"
        assert home_status_2.eep_program.owner == eep_2.company, "hs2 wrong eep_program owner"
        assert home_status_2.home.get_builder() == builder.company, "hs2 wrong builder"
        assert home_status_2.state == "inspection", "hs2 wrong state"
        assert not (home_status_2.is_eligible_for_certification()), "hs2 eligible for certification"
        assert home_status_2.pct_complete != 100, "hs2 100 pct_complete"

        builder = builder_admin_factory(username="builder_3", company__city=city)
        builder_org = Company.objects.get(id=builder.company.id)

        rater_3 = rater_admin_factory(username="rater_3", company__city=city)

        home_status_3 = certified_home_with_checklist_factory(
            company=rater_3.company,
            eep_program__owner=eep_1.company,
            home__subdivision__builder_org=builder_org,
            home__city=city,
            eep_program__no_close_dates=True,
            certify=False,
        )

        assert home_status_3.company == rater_3.company, "hs3 wrong company"
        assert home_status_3.eep_program.owner == eep_1.company, "hs3 wrong eep_program owner"
        assert home_status_3.home.get_builder().id == builder.company.id, "hs3 wrong builder"
        assert home_status_3.state == "certification_pending", "hs3 wrong state"
        assert home_status_3.is_eligible_for_certification(), "hs3 not eligible for certification"
        assert home_status_3.pct_complete == 100, "hs3 not 100 pct_complete"

        home_status_4 = certified_home_with_checklist_factory(
            company=rater_3.company,
            eep_program__owner=eep_1.company,
            home=home_status_3.home,
            pct_complete=33,
            eep_program__no_close_dates=True,
        )

        assert home_status_4.company == rater_3.company, "hs4 wrong company"
        assert home_status_4.eep_program.owner == eep_1.company, "hs4 wrong eep_program owner"
        assert home_status_4.home.get_builder().id == builder.company.id, "hs4 wrong builder"
        assert home_status_4.state == "inspection", "hs4 wrong state"
        assert not (home_status_4.is_eligible_for_certification()), "hs4 eligible for certification"
        assert home_status_4.pct_complete != 100, "hs4 100 pct_complete"

        rater_5 = rater_admin_factory(username="rater_5", company__city=city)
        provider_5 = provider_admin_factory(
            username="provider_5", company__provider_id="102-4325", company__city=city
        )
        eep_5 = eep_admin_factory(
            username="eep_5", company__is_eep_sponsor=True, company__city=city
        )

        # TODO REPLACE ME with a Sampleset factory!

        from axis.relationship.models import Relationship
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory
        from axis.sampleset.tests.factories import empty_sampleset_factory

        subdivision = subdivision_factory(builder_org=builder_org, city=city)
        Relationship.objects.create_mutual_relationships(
            rater_5.company, provider_5.company, eep_5.company, builder.company
        )
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, rater_5.company)
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, provider_5.company)
        Relationship.objects.validate_or_create_relations_to_entity(subdivision, eep_5.company)

        eep_program = basic_eep_program_checklist_factory(
            owner=eep_5.company, require_resnet_sampling_provider=True, no_close_dates=True
        )

        home_status_5 = certified_home_with_checklist_factory(
            company=rater_5.company,
            eep_program=eep_program,
            home__subdivision=subdivision,
            home__city=city,
            certify=False,
            certifying_user=provider_5,
        )

        sampleset = empty_sampleset_factory(owner=rater_5.company)
        sampleset.add_home_status(home_status_5, is_test_home=True, revision=0)

        assert home_status_5.company == rater_5.company, "hs5 wrong company"
        assert home_status_5.eep_program.owner == eep_5.company, "hs5 wrong eep_program owner"
        assert (
            home_status_5.eep_program.require_resnet_sampling_provider
        ), "hs5 require_resnet_sampling_provider"
        assert home_status_5.home.get_builder().id == builder.company.id, "hs5 wrong builder"
        assert home_status_5.state == "certification_pending", "hs5 wrong state"
        assert not (home_status_5.is_eligible_for_certification()), "hs5 eligible for certification"
        assert home_status_5.pct_complete == 100, "hs5 not 100 pct_complete"

        # assert Company.objects.all().count() == 20, \
        #     "expected {} companies, found {}".format(20, Company.objects.count())

        from axis.home.models import Home, EEPProgramHomeStatus

        assert Home.objects.all().count() == 3, "expected {} homes, found {}".format(
            3, Home.objects.count()
        )
        assert (
            EEPProgramHomeStatus.objects.all().count() == 5
        ), "expected {} home stats, found {}".format(5, EEPProgramHomeStatus.objects.count())
        assert home_status_1.state == "certification_pending", "hs1 wrong state"
        assert home_status_2.state == "inspection", "hs2 wrong state"
        assert home_status_3.state == "certification_pending", "hs3 wrong state"
        assert home_status_4.state == "inspection", "hs4 wrong state"
        assert home_status_5.state == "certification_pending", "hs5 wrong state"

        from axis.eep_program.models import EEPProgram

        assert EEPProgram.objects.all().count() == 5, "expected {} Programs, found {}".format(
            5, EEPProgramHomeStatus.objects.count()
        )

        assert (
            rater_1.company != rater_2.company != rater_3.company != rater_5.company
        ), "rater1, rater2, rater3, rater5 share company"
        assert eep_1.company != eep_2.company != eep_5.company, "eep1, eep2, eep5 share company"

    def test_certification_signal_test(self):
        """Test that a certification signal happens"""

        # FIXME: Failing test. Signal wants a rater_XXXX user, but gets a provider_XXXX user
        def receiver(sender, **kwargs):
            """Helping method"""
            self.assertIn("user", kwargs)
            self.assertEqual(kwargs["user"].username.startswith("provider"), True)
            self.assertIn("instance", kwargs)
            self.assertIsInstance(kwargs["instance"], EEPProgramHomeStatus)
            received_signals.append(kwargs.get("signal"))

        received_signals = []
        eep_program_certified.connect(receiver, sender=EEPProgramHomeStatus)

        # Not loading from a fixture.  It's too complicated to freeze this without certification
        certified_custom_home_with_basic_eep_factory()

        self.assertEqual(len(received_signals), 1)
        self.assertEqual(received_signals, [eep_program_certified])

    def _setup_single_home_dual_program_dual_raters(self, stat_2_pct_complete=33, **kwargs):
        """Test will setup a single home with two independent programs by two different raters"""

        self.rater_1 = self.user_model.objects.get(username="rater_1")
        self.home_status_1 = EEPProgramHomeStatus.objects.get(company=self.rater_1.company)
        self.eep_org_1 = self.home_status_1.eep_program.owner
        self.eep_1 = self.eep_org_1.users.all().get()

        self.rater_2 = self.user_model.objects.get(username="rater_2")
        self.home_status_2 = EEPProgramHomeStatus.objects.get(company=self.rater_2.company)
        self.eep_org_2 = self.home_status_2.eep_program.owner
        self.eep_2 = self.eep_org_2.users.all().get()

        self.home = self.home_status_1.home
        for idx in range(1, 3):
            relationships = [
                getattr(self, "rater_{}".format(idx)).company,
                getattr(self, "eep_{}".format(idx)).company,
                self.home.get_builder(),
            ]
            for item in ["provider", "hvac", "utility", "qa", "eep", "general", "builder"]:
                if kwargs.get("add_{}_{}".format(item, idx), False):
                    if idx == 2 and item == "builder":
                        continue
                    co_user = self.user_model.objects.get(username="{}_{}".format(item, idx))
                    Relationship.objects.validate_or_create_relations_to_entity(
                        self.home, co_user.company
                    )
                    relationships.append(co_user.company)
                    if item not in ["eep", "builder"]:
                        setattr(self, "{}_org_{}".format(item, idx), co_user.company)
                    if item != "builder":
                        setattr(self, "{}_{}".format(item, idx), co_user)
                    else:
                        setattr(self, "{}".format(item), co_user)
            Relationship.objects.create_mutual_relationships(*relationships)
            # print("Added {} User - {} - {}").format(item.capitalize(), user, user.company)

    def test_single_home_multiple_rater_relationships(self):  # pylint: disable=R0915
        """
        Test will verify the ability to add two programs onto a single home from two
        different raters.  Questions should not collide
        """

        # Methods which should work -these are in context stuff
        kwargs = {
            "add_provider_1": True,
            "add_utility_1": True,
            "add_hvac_1": True,
            "add_qa_1": True,
            "add_eep_1": True,
            "add_provider_2": True,
            "add_utility_2": True,
            "add_hvac_2": True,
            "add_qa_2": True,
            "add_eep_2": True,
            "add_builder_1": True,
            "add_builder_2": True,
        }
        self._setup_single_home_dual_program_dual_raters(**kwargs)

        # RATER 1 =================================================
        statuses = self.home.get_home_status_breakdown(self.rater_1)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, True)

        self.assertIn(self.home_status_1, statuses.stats_all)
        self.assertIn(self.home_status_1, statuses.stats_can_edit)

        # RATER 2 =================================================
        statuses = self.home.get_home_status_breakdown(self.rater_2)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, True)

        self.assertIn(self.home_status_2, statuses.stats_can_edit)
        self.assertIn(self.home_status_2, statuses.stats_all)

        self.assertEqual(self.home.get_builder().users.count(), 1)

        # BUILDER =================================================
        statuses = self.home.get_home_status_breakdown(self.builder)
        self.assertEqual(statuses.stats_count, 2)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 2)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertEqual(self.home.is_home_certified(self.builder.company), False)

        # EEP 1 =================================================
        statuses = self.home.get_home_status_breakdown(self.eep_1)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_1, statuses.stats_all)
        self.assertIn(self.home_status_1, statuses.stats_can_view)

        # EEP 2 =================================================
        statuses = self.home.get_home_status_breakdown(self.eep_2)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_2, statuses.stats_all)
        self.assertIn(self.home_status_2, statuses.stats_can_view)

        # UTILITY 1 =================================================
        statuses = self.home.get_home_status_breakdown(self.utility_1)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_1, statuses.stats_all)
        self.assertIn(self.home_status_1, statuses.stats_can_view)

        # UTILITY 2 =================================================
        statuses = self.home.get_home_status_breakdown(self.utility_2)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_2, statuses.stats_all)
        self.assertIn(self.home_status_2, statuses.stats_can_view)

        # HVAC 1 =================================================
        statuses = self.home.get_home_status_breakdown(self.hvac_1)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_1, statuses.stats_all)
        self.assertIn(self.home_status_1, statuses.stats_can_view)

        # HVAC 2 =================================================
        statuses = self.home.get_home_status_breakdown(self.hvac_2)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_2, statuses.stats_all)
        self.assertIn(self.home_status_2, statuses.stats_can_view)

        # QA 1 =================================================
        statuses = self.home.get_home_status_breakdown(self.qa_1)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_1, statuses.stats_all)
        self.assertIn(self.home_status_1, statuses.stats_can_view)

        # QA 2 =================================================
        statuses = self.home.get_home_status_breakdown(self.qa_2)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_2, statuses.stats_all)
        self.assertIn(self.home_status_2, statuses.stats_can_view)

        # PROVIDER 1 =================================================
        statuses = self.home.get_home_status_breakdown(self.provider_1)
        self.assertIn(self.provider_1.company, self.rater_1.company.relationships.get_companies())
        self.assertIn(self.rater_1.company, self.provider_1.company.relationships.get_companies())
        self.assertGreater(EEPProgramHomeStatus.objects.filter_by_user(self.provider_1).count(), 0)

        self.assertEqual(statuses.stats_count, 1)

        try:
            self.assertEqual(len(statuses.stats_can_certify), 1)
        except AssertionError:
            import pprint

            for stat in statuses.stats_all:
                print(stat)
                for k, v in stat.get_progress_analysis()["requirements"].items():
                    if v["status"] is False:
                        print(k)
                        pprint.pprint(v)
            raise

        self.assertEqual(len(statuses.stats_can_certify), 1)
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_1, statuses.stats_all)
        self.assertIn(self.home_status_1, statuses.stats_can_certify)

        # PROVIDER 2 =================================================
        statuses = self.home.get_home_status_breakdown(self.provider_2)
        self.assertEqual(statuses.stats_count, 1)

        self.assertEqual(len(statuses.stats_can_certify), 0)
        self.assertEqual(len(statuses.stats_can_edit), 0)
        self.assertEqual(len(statuses.stats_can_view), 1)
        self.assertEqual(len(statuses.stats_completed), 0)
        self.assertEqual(statuses.has_checklist, False)

        self.assertIn(self.home_status_2, statuses.stats_all)
        self.assertIn(self.home_status_2, statuses.stats_can_view)

    def test_single_home_multiple_rater_can_access_own_stats(self):
        """
        Test will verify the ability to add two programs onto a single home from two different
        rater. And each rater can only view their program
        """

        self._setup_single_home_dual_program_dual_raters()

        # Rater 1
        statuses = self.home.get_home_status_breakdown(self.rater_1)
        self.assertEqual(statuses.stats_count, 1)
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertEqual(statuses.stats_can_edit[0], self.home_status_1)

        # Rater 2
        statuses = self.home.get_home_status_breakdown(self.rater_2)
        self.assertEqual(statuses.stats_count, 1)
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertEqual(statuses.stats_can_edit[0], self.home_status_2)

    def test_single_home_multiple_rater_provider_can_access_both(self):
        """
        Test will verify the ability to add two programs onto a single home from two different
        raters. And the provider can access both.
        """

        self._setup_single_home_dual_program_dual_raters(add_provider_1=True)

        # Provider 1
        statuses = self.home.get_home_status_breakdown(self.provider_1)

        # verify relationships
        self.assertIn(self.provider_1.company, self.rater_1.company.relationships.get_companies())
        self.assertIn(self.rater_1.company, self.provider_1.company.relationships.get_companies())

        self.assertGreater(EEPProgramHomeStatus.objects.filter_by_user(self.provider_1).count(), 0)

        self.assertEqual(statuses.stats_count, 1)
        self.assertEqual(len(statuses.stats_can_certify), 1)
        self.assertEqual(statuses.stats_can_certify[0], self.home_status_1)
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertEqual(len(statuses.stats_can_view), 1)

    def test_single_home_multiple_rater_provider_relation(self):
        """
        Test will verify the ability to add two programs onto a single home from two
        different raters.  Questions should not collide
        """

        self._setup_single_home_dual_program_dual_raters(add_provider_1=True)

        # Get a relationship with the EEP's
        Relationship.objects.validate_or_create_relations_to_entity(
            self.provider_org_1, self.eep_org_2
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            self.eep_org_2, self.provider_org_1
        )

        Relationship.objects.validate_or_create_relations_to_entity(
            self.provider_org_1, self.home_status_2.company
        )

        # Must be a mutual relationship
        statuses = self.home.get_home_status_breakdown(self.provider_1)
        # Can certify/edit/view from first relationship
        self.assertEqual(len(statuses.stats_can_certify), 1)
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertEqual(len(statuses.stats_can_view), 1)

        # Make a mutual relationship
        Relationship.objects.validate_or_create_relations_to_entity(
            self.home_status_2.company, self.provider_org_1
        )

        statuses = self.home.get_home_status_breakdown(self.provider_1)
        self.assertEqual(statuses.stats_count, 2)

        # Provider can still only certify 1, second stat is not ready for certification
        self.assertEqual(len(statuses.stats_can_certify), 1)
        self.assertIn(self.home_status_1, statuses.stats_can_certify)

        # Provider can still only edit 1, second stat is not ready for certification
        self.assertEqual(len(statuses.stats_can_edit), 1)
        self.assertIn(self.home_status_1, statuses.stats_can_edit)

        # Provider can view both because of new mutual relationship
        self.assertEqual(len(statuses.stats_can_view), 2)
        self.assertIn(self.home_status_1, statuses.stats_can_view)
        self.assertIn(self.home_status_2, statuses.stats_can_view)

    def test_single_home_multiple_programs_only_certified_answers_get_locked(self):
        """
        Verify that one company can add 2 programs to a home, and when one program gets certified
        only the questions for that program are locked. While questions from the uncertified
        program remain untouched.
        """

        rater = self.user_model.objects.get(username="rater_3")
        provider = self.user_model.objects.get(username="provider_1")

        home_stat_1 = EEPProgramHomeStatus.objects.filter(
            company=rater.company, pct_complete=100
        ).first()
        home_stat_2 = (
            EEPProgramHomeStatus.objects.filter(company=rater.company)
            .exclude(id=home_stat_1.id)
            .first()
        )

        Relationship.objects.validate_or_create_relations_to_entity(rater.company, provider.company)
        Relationship.objects.validate_or_create_relations_to_entity(provider.company, rater.company)

        self.assertNotEqual(home_stat_1.state, "complete")
        self.assertNotEqual(home_stat_2.state, "complete")

        self.assertIsNone(home_stat_1.certification_date)
        self.assertIsNone(home_stat_2.certification_date)

        # Make sure none of the answers are locked.
        self.assertNotIn(
            True, home_stat_1.get_answers_for_home().values_list("confirmed", flat=True)
        )
        self.assertNotIn(
            True, home_stat_2.get_answers_for_home().values_list("confirmed", flat=True)
        )

        certify_single_home(provider, home_stat_1, now())
        home_stat_1 = EEPProgramHomeStatus.objects.get(id=home_stat_1.id)
        home_stat_2 = EEPProgramHomeStatus.objects.get(id=home_stat_2.id)

        self.assertIsNotNone(home_stat_1.certification_date)
        self.assertIsNone(home_stat_2.certification_date)

        self.assertEqual(home_stat_1.state, "complete")
        self.assertNotEqual(home_stat_2.state, "complete")

        # Make sure only the certified program answers are locked
        self.assertNotIn(
            False, home_stat_1.get_answers_for_home().values_list("confirmed", flat=True)
        )
        self.assertNotIn(
            True, home_stat_2.get_answers_for_home().values_list("confirmed", flat=True)
        )

    def test_resnet_sample_provider_requirements(self):
        """Test for report_eligibility_for_certification"""
        from axis.resnet.tests.factories import resnet_company_factory

        rater = self.user_model.objects.get(username="rater_5")
        provider = self.user_model.objects.get(username="provider_5")

        home_status = EEPProgramHomeStatus.objects.get(company=rater.company)
        self.assertEqual(home_status.is_eligible_for_certification(), False)
        results = home_status.report_eligibility_for_certification()
        self.assertEqual(len(results), 1)
        self.assertIn(
            "requires sampled projects to be certified by RESNET Sampling approved", results[0]
        )

        resnet_company_factory(company=provider.company, is_sampling_provider=True)
        self.assertEqual(home_status.is_eligible_for_certification(), True)


class HomeModelMethodsTests(AxisTestCase):
    """Test defined custom methods for the Home model"""

    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        """Fixture populate method"""
        from axis.geographic.tests.factories import (
            real_city_factory,
        )
        from axis.core.tests.factories import builder_admin_factory
        from axis.company.tests.factories import builder_organization_factory
        from axis.core.tests.factories import basic_user_factory, general_super_user_factory
        from axis.subdivision.tests.factories import subdivision_factory
        from axis.home.models import Home, EEPProgramHomeStatus
        from axis.sampleset.tests.factories import sampleset_with_subdivision_homes_factory
        from axis.sampleset.models import SampleSetHomeStatus
        from axis.core.tests.factories import (
            eep_admin_factory,
            general_admin_factory,
            rater_admin_factory,
            provider_admin_factory,
            qa_admin_factory,
        )
        from axis.eep_program.tests.factories import basic_eep_program_factory
        from axis.home.tests.factories import eep_program_home_status_factory, home_factory
        from axis.relationship.models import Relationship
        import operator
        from axis.incentive_payment.tests.factories import (
            basic_incentive_payment_status_factory,
            basic_pending_builder_incentive_distribution_factory,
        )

        city = real_city_factory("Gilbert", "AZ")
        home_kwargs = {
            "city": city,
            "street_line1": "123 street line 1",
            "street_line2": "# 123",
            "zipcode": "12345",
            "state": "AZ",
            "lot_number": "123",
        }
        # users
        basic_user_factory(username="mob")
        general_super_user_factory(username="gimerique", company__city=city)
        builder_user = builder_admin_factory(
            username="builder_1",
            company__name="Builder1",
            company__city=city,
        )
        rater_user = rater_admin_factory(company__name="Rater1", company__city=city)

        # really basic home
        Home(slug="home-alone", **home_kwargs).save()

        subdivision_factory(name="subdivision-101", city=city)

        # really basic home with a relationship with builder and no Subdivision
        home_alone2 = Home(slug="home-alone2", **home_kwargs)
        home_alone2.save()
        Relationship.objects.validate_or_create_relations_to_entity(
            home_alone2, builder_user.company
        )

        subdivision = subdivision_factory(city=city)
        home_sub = Home(slug="home-sub", subdivision=subdivision, **home_kwargs)
        home_sub.save()
        user_home_sub = builder_admin_factory(
            username="home_sub_builder_1", company=home_sub.get_builder()
        )
        Relationship.objects.validate_or_create_relations_to_entity(home_sub, user_home_sub.company)

        subdivision = subdivision_factory(city=city)
        home_sub_stats = Home(slug="home-sub-homestatus", subdivision=subdivision, **home_kwargs)
        home_sub_stats.save()
        user_home_sub_stats = builder_admin_factory(
            username="home_sub_stats_builder_1", company=home_sub_stats.get_builder()
        )
        eep_program1 = basic_eep_program_factory(name="EEP1", no_close_dates=True, owner__city=city)
        EEPProgramHomeStatus(
            eep_program=eep_program1, home=home_sub_stats, company=home_sub_stats.get_builder()
        ).save()
        Relationship.objects.validate_or_create_relations_to_entity(
            home_sub_stats, user_home_sub_stats.company
        )

        subdivision = subdivision_factory(city=city)
        home_sub_mult = Home(
            slug="home-sub-mult-homestatus", subdivision=subdivision, **home_kwargs
        )
        home_sub_mult.save()
        user = builder_admin_factory(
            username="home_sub_stats_builder_2", company=home_sub_mult.get_builder()
        )
        rater_co = rater_user.company
        eep_program2 = basic_eep_program_factory(name="EEP2", owner=rater_co, no_close_dates=True)
        EEPProgramHomeStatus(
            eep_program=eep_program2, home=home_sub_mult, company=home_sub_mult.get_builder()
        ).save()
        eep_program3 = basic_eep_program_factory(name="EEP3", owner=rater_co, no_close_dates=True)
        EEPProgramHomeStatus(
            eep_program=eep_program3, home=home_sub_mult, company=home_sub_mult.get_builder()
        ).save()
        eep_program4 = basic_eep_program_factory(name="EEP4", no_close_dates=True, owner__city=city)
        builder_org = builder_organization_factory(city=city)
        EEPProgramHomeStatus(
            eep_program=eep_program4, home=home_sub_mult, company=builder_org
        ).save()
        Relationship.objects.validate_or_create_relations_to_entity(home_sub_mult, user.company)
        Relationship.objects.validate_or_create_relations_to_entity(home_sub_mult, rater_co)

        # SampleSetHomeStatus
        eep_user = eep_admin_factory(company__name="EEP5", company__city=city)
        eep_user_2 = eep_admin_factory(company__name="EEP6", company__city=city)
        eep_user_3 = eep_admin_factory(company__name="EEP7", company__city=city)
        general_user = general_admin_factory(company__name="General1", company__city=city)
        rater_user2 = rater_admin_factory(company__name="Rater2", company__city=city)
        provider_user = provider_admin_factory(company__name="Provider1", company__city=city)
        qa_user = qa_admin_factory(company__name="QA1", company__city=city)

        # Create mutual relationships
        users_companies = list(
            map(
                operator.attrgetter("company"),
                [eep_user, general_user, rater_user2, provider_user, qa_user],
            )
        )
        Relationship.objects.create_mutual_relationships(*users_companies)
        Relationship.objects.create_mutual_relationships(eep_user_2.company, general_user.company)

        eep_program5 = basic_eep_program_factory(name="EEP5", owner=rater_co, no_close_dates=True)
        rater_user3 = rater_admin_factory(company__name="Rater3", company__city=city)

        unrestricted_eep = basic_eep_program_factory(
            name="Unrestricted Program 1", owner=eep_user.company, no_close_dates=True
        )

        # Create Home stats. this home has two sampleset, 1 with incentive and the other without.
        home = home_factory(slug="home-sampling-1", city=city, subdivision__city=city)
        home_status = eep_program_home_status_factory(
            company=provider_user.company, eep_program=unrestricted_eep, home=home
        )
        # Create relationships to home
        for company in users_companies:
            Relationship.objects.validate_or_create_relations_to_entity(home, company)

        sampleset = sampleset_with_subdivision_homes_factory(
            eep_program=eep_program5,
            owner=rater_user3.company,
            home__city=city,
            subdivision__city=city,
        )
        SampleSetHomeStatus.objects.create(
            sampleset=sampleset,
            home_status=home_status,
            revision=1,
            is_active=True,
            is_test_home=True,
        )
        kwargs = {"home_status": home_status, "state": "complete"}
        basic_incentive_payment_status_factory(**kwargs)

        restricted_eep = basic_eep_program_factory(
            name="Restricted Program 1",
            owner=eep_user.company,
            viewable_by_company_type="qa, provider",
            no_close_dates=True,
        )

        home_status2 = eep_program_home_status_factory(
            company=provider_user.company, eep_program=restricted_eep, home=home
        )
        SampleSetHomeStatus.objects.create(
            sampleset=sampleset,
            home_status=home_status2,
            revision=1,
            is_active=True,
            is_test_home=True,
        )

        basic_eep_program_factory(
            name="Unrelated Unrestricted Program 1", owner=eep_user_2.company, no_close_dates=True
        )

        basic_pending_builder_incentive_distribution_factory(
            company=eep_user_3.company, customer=builder_user.company, ipp_count=3
        )
        cls.watertown = real_city_factory("Watertown", "WI")

    def setUp(self):
        """Prepares the test fixture."""
        from axis.geographic.models import City

        self.city = City.objects.get(name="Gilbert")
        self.county = self.city.county
        self.builder = self.get_admin_user("builder")
        self.builder_company = self.builder.company

        self.home_kwargs = {
            "city": self.city,
            "street_line1": "123 street line 1",
            "zipcode": "12345",
            "state": "AZ",
        }
        self.base_kwargs = self.home_kwargs.copy()
        self.base_kwargs.update(
            {
                "lot_number": "lot",
                "county": self.county,
                "builder": self.builder_company,
                "user": self.builder,
            }
        )

    def tearDown(self):
        """Tests tear down"""

    def test__str__(self):
        """Test __str__"""
        home = Home.objects.first()
        expected = home.get_home_address_display()
        self.assertEqual(expected, str(home))

    def test_save_no_slug(self):
        """Test save(). Home does not have a slug"""
        from axis.core.utils import slugify_uniquely

        home = Home(**self.home_kwargs)
        slug = slugify_uniquely(home.get_home_address_display()[:60], home.__class__)
        home.save()
        self.assertEqual(slug, home.slug)

    def test_save_slug_provided(self):
        """Test save(). Home does not have a slug"""
        from axis.core.utils import slugify_uniquely

        SLUG = "my-home-slug"
        home = Home(slug=SLUG, **self.home_kwargs)
        home.save()
        slug = slugify_uniquely(home.get_home_address_display()[:60], home.__class__)
        self.assertNotEqual(slug, home.slug)
        self.assertEqual(SLUG, home.slug)

    def test_save_street_line1_profile(self):
        """Test save()"""
        from axis.customer_hirl.utils import profile_address

        home = Home(**self.home_kwargs)
        home.save()
        expected = profile_address(home.street_line1)
        self.assertEqual(expected, home.street_line1_profile)

    def test_get_absolute_url(self):
        """Test get_absolute_url()"""
        from django.urls import reverse

        home = Home.objects.first()
        absolute_url = home.get_absolute_url()
        expected_url = reverse("home:view", kwargs={"pk": home.id})
        self.assertEqual(expected_url, absolute_url)

    def test_can_be_added(self):
        """Test can_be_added"""

        user = User.objects.get(company__name="Builder1")
        self.assertTrue(user.has_perm("home.add_home"))
        can_be_added = Home.can_be_added(user)
        self.assertTrue(can_be_added)

    def test_can_be_added_user_with_no_perms(self):
        """Test model's can_be_added method"""

        user = User.objects.get(username="mob")
        self.assertFalse(user.has_perm("home.add_home"))
        can_be_added = Home.can_be_added(user)
        self.assertFalse(can_be_added)

    def test_can_be_edited_by_superuser(self):
        """Test can_be_edited"""

        user = User.objects.get(username="gimerique")
        home = Home.objects.first()
        can_be_edited = home.can_be_edited(user)
        self.assertTrue(can_be_edited)

    def test_can_be_edited(self):
        """Test can_be_edited. user has change_home permission"""
        # home = Home.objects.first()
        # user = User.objects.filter(company=home.get_builder()).first()
        home = Home.objects.get(slug="home-alone2")
        user = User.objects.get(username="builder_1")
        can_be_edited = home.can_be_edited(user)
        self.assertTrue(can_be_edited)

    def test_can_be_edited_no_perm(self):
        """Test can_be_edited. user has NO change_home permission"""

        home = Home.objects.first()
        user = User.objects.get(username="mob")
        can_be_edited = home.can_be_edited(user)
        self.assertFalse(can_be_edited)

    def test_can_be_deleted_with_superuser(self):
        """Test can_be_deleted. user is superuser. Expected result True"""

        user = User.objects.get(username="gimerique")
        home = Home.objects.first()
        can_be_deleted = home.can_be_deleted(user)
        self.assertTrue(can_be_deleted)

    def test_can_be_deleted_no_relations(self):
        """Test can_be_deleted. home has no relations. Expected result False"""
        user = User.objects.order_by("id").first()
        home = Home.objects.get(slug="home-alone")
        relations = home.relationships.filter(is_owned=True).exclude(
            company__auto_add_direct_relationships=True
        )
        relations_count = len(set(relations.values_list("company__id", flat=True)))
        self.assertEqual(0, relations_count)
        relations_count = len(set(home.homestatuses.values_list("company__id", flat=True)))
        self.assertEqual(0, relations_count)
        can_be_deleted = home.can_be_deleted(user)
        self.assertFalse(can_be_deleted)

    def test_can_be_deleted_(self):
        """
        Test can_be_deleted. home has Exactly 1 relation and there are no homestatus_owners.
        Expected result True
        """
        user = User.objects.get(username="home_sub_builder_1")
        home = Home.objects.get(slug="home-sub")
        company = user.company
        relations = home.relationships.filter(is_owned=True).exclude(
            company__auto_add_direct_relationships=True
        )
        relations_count = len(set(relations.values_list("company__id", flat=True)))
        self.assertEqual(1, relations_count)
        self.assertEqual(relations[0].company, company)
        homestatus_owners_count = len(home.eep_programs.values_list("owner__id", flat=True))
        self.assertEqual(0, homestatus_owners_count)
        can_be_deleted = home.can_be_deleted(user)
        self.assertTrue(can_be_deleted)

    def test_can_be_deleted_2(self):
        """
        Test can_be_deleted. home has Exactly 1 relation and is related to a home_status.
        all home_status involved belong to the user
        Expected result True
        """
        user = User.objects.get(username="home_sub_stats_builder_1")
        home = Home.objects.get(slug="home-sub-homestatus")

        self.assertEqual(1, len(home.homestatuses.values_list("company__id", flat=True)))
        relations = home.relationships.filter(is_owned=True).exclude(
            company__auto_add_direct_relationships=True
        )
        relations_count = len(set(relations.values_list("company__id", flat=True)))
        self.assertEqual(1, relations_count)
        self.assertEqual(relations[0].company, user.company)
        homestatus_owners_count = len(home.eep_programs.values_list("owner__id", flat=True))
        self.assertEqual(1, homestatus_owners_count)
        can_be_deleted = home.can_be_deleted(user)
        self.assertTrue(can_be_deleted)

    def test_can_be_deleted_3(self):
        """
        Test can_be_deleted. home has more than 1 relation and is related to a home_status.
        all home_status involved belong to the user
        Expected result True
        """
        user = User.objects.get(username="home_sub_stats_builder_2")
        home = Home.objects.get(slug="home-sub-mult-homestatus")

        relations = home.relationships.filter(is_owned=True).exclude(
            company__auto_add_direct_relationships=True
        )
        relations_count = len(set(relations.values_list("company__id", flat=True)))
        self.assertGreater(relations_count, 1)
        can_be_deleted = home.can_be_deleted(user)
        self.assertTrue(can_be_deleted)

    def test_can_be_deleted_recently_created(self):
        """
        Test can_be_deleted. home's created recently within the first 300 seconds,
        can be deleted no questions asked. Expected result True
        """

        user = User.objects.get(company__name="Builder1")
        home_status = EEPProgramHomeStatus.objects.first()
        home = EEPProgramHomeStatus.objects.first().home
        home.created_date = datetime.datetime.now(datetime.timezone.utc)
        home.save()
        # There is no real history we don't export it.
        can_be_deleted = home.can_be_deleted(user)
        self.assertTrue(can_be_deleted)

        # If we did it all then we should be able to nuke it.
        home.history.all().update(history_user=user)
        can_be_deleted = home.can_be_deleted(user)
        self.assertTrue(can_be_deleted)

        user = (
            User.objects.exclude(company__in=[user.company, home_status.eep_program.owner])
            .filter(is_superuser=False)
            .last()
        )
        can_be_deleted = home.can_be_deleted(user)
        try:
            self.assertFalse(can_be_deleted)
        except AssertionError:
            reason = home.get_reason_cannot_be_deleted(user)
            print(f"The home reports the following reason that it cannot be deleted: '{reason}'")

            print("Should be True")
            print("user.company", user.company is not None)
            print("Should be False")
            print("user.is_customer_hirl_company_member", user.is_customer_hirl_company_member())
            print(
                "user.is_sponsored_by_company(HIRL)",
                user.is_sponsored_by_company(
                    company="provider-home-innovation-research-labs", only_sponsor=True
                ),
            )
            seconds_since_create = (
                datetime.datetime.now(datetime.timezone.utc) - home.created_date
            ).seconds
            print("Should be True")
            print(f"{seconds_since_create=} <= {5*60}", seconds_since_create <= 5 * 60)
            users = list(
                set(filter(None, home.history.all().values_list("history_user", flat=True)))
            )
            print("Should be False")
            print(
                f"Users {users=} should be either none or {user.company_id=}",
                not users or users == [user.id],
            )
            print("User is super", user.is_superuser)

            relations = home.relationships.filter(is_owned=True).exclude(
                company__auto_add_direct_relationships=True
            )
            relations_ids = set(relations.values_list("company__id", flat=True))
            relations_count = len(relations_ids)

            homestatus_companies = set(home.homestatuses.values_list("company__id", flat=True))
            eep_owners = set(home.eep_programs.values_list("owner__id", flat=True))

            print("Should be False")
            print(
                f"Relations count {relations_count} and relations.company == {user.company_id}",
                relations_count == 1 and relations[0].company == user.company_id,
            )
            print(
                f"Relation_ids {relations_ids=} - {eep_owners=} = {user.company_id}",
                relations_ids - eep_owners == {user.company_id},
            )

            raise

    def test_can_be_deleted_not_so_recently_created(self):
        """
        Test can_be_deleted. home's created recently within the first 300 seconds,
        can be deleted no questions asked. Expected result False
        """

        home = EEPProgramHomeStatus.objects.first().home
        home.created_date = datetime.datetime(2015, 1, 8, 11, 00, tzinfo=datetime.timezone.utc)
        home.save()
        user = User.objects.get(company__name="Builder1")
        can_be_deleted = home.can_be_deleted(user)
        self.assertFalse(can_be_deleted)

    def test_should_send_relationship_notification(self):
        """
        Test should_send_relationship_notification.
        home is not custom_home. Expected result False
        """
        home_status = EEPProgramHomeStatus.objects.first()
        home = home_status.home
        home.is_custom_home = False
        self.assertFalse(home.is_custom_home)
        result = home.should_send_relationship_notification(home_status.company)
        self.assertFalse(result)

    def test_should_send_relationship_notification_false(self):
        """Test should_send_relationship_notification. home is custom_home. Expected result True"""
        home_status = EEPProgramHomeStatus.objects.first()
        home = home_status.home
        home.is_custom_home = True
        home.save()
        self.assertTrue(home.is_custom_home)
        result = home.should_send_relationship_notification(home_status.company)
        self.assertTrue(result)

    def test_get_builder_from_relationship(self):
        """
        Test get_builder().
        Home first tries to grab the builder from a relationship, if doesn't find one,
        then checks for subdivision, it tries to grab it from there (subdivision.builder_org).
        """
        builder_co = User.objects.get(username="builder_1").company
        home = Home.objects.get(slug="home-alone2")
        self.assertIsNone(home.subdivision)
        result = home.get_builder()
        self.assertEqual(builder_co, result)

    def test_get_builder_from_subdivision(self):
        """
        Test get_builder().
        Home first tries to grab the builder from a relationship, if doesn't find one,
        then if it has a subdivision, it tries to grab it from there (subdivision.builder_org).
        """
        from axis.subdivision.models import Subdivision

        home = Home.objects.get(slug="home-alone")
        subdivision = Subdivision.objects.first()
        home.subdivision = subdivision
        home.save()
        self.assertEqual(0, home.relationships.filter(company__company_type="builder").count())
        result = home.get_builder()
        self.assertEqual(subdivision.builder_org, result)

    def test_get_builder(self):
        """
        Test get_builder().
        Home first tries to grab the builder from a relationship, if doesn't find one,
        then if it has a subdivision, it tries to grab it from there (subdivision.builder_org).
        Expected result builder from relationship
        """
        from axis.subdivision.models import Subdivision

        home = Home.objects.get(slug="home-sub")
        home.subdivision = Subdivision.objects.get(name="subdivision-101")
        self.assertIsNotNone(home.subdivision)
        builder_co = User.objects.get(username="home_sub_builder_1").company
        result = home.get_builder()
        self.assertEqual(1, home.relationships.filter(company__company_type="builder").count())
        self.assertNotEqual(home.subdivision.builder_org, result)
        self.assertEqual(builder_co, result)

    def test_get_id(self):
        """Test get_id"""
        home = EEPProgramHomeStatus.objects.first().home
        result = home.get_id()
        expected = "{:06}".format(home.id)
        self.assertEqual(expected, result)

    def test_get_home_address_display_raw_addresses(self):
        """This will prove that when a company wants to display the raw address the
        get_home_address_display will do the right thing
        """
        from axis.company.models import Company

        data = {
            "street_line1": "200 North Church Street",
            "city": self.watertown.pk,
            "zipcode": "53094",
        }

        serializer = GeocodeMatchesSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        gecode, created = serializer.save()
        google = gecode.responses.get(engine="Google")
        self.assertEqual(google.geocode.pk, gecode.pk)

        # Highjack this a bit otherwise save will align the data.
        Home.objects.filter(id=Home.objects.first().id).update(geocode_response=google)
        home = Home.objects.first()

        # The default is to show the geocoded address
        company = Company.objects.first()
        company.display_raw_addresses = False
        company.save()

        result = home.get_home_address_display_parts(
            company=company, raw=False, include_city_state_zip=True
        )
        self.assertEqual(result.street_line1, home.street_line1)
        self.assertEqual(result.street_line2, home.street_line2)
        self.assertEqual(result.city, home.city.name)
        self.assertEqual(result.state, home.state)
        self.assertEqual(result.zipcode, home.zipcode)

        self.assertNotEqual(result.street_line1, gecode.raw_street_line1)
        self.assertNotEqual(result.street_line2, gecode.raw_street_line2)
        self.assertNotEqual(result.city, gecode.raw_city)
        self.assertNotEqual(result.state, gecode.raw_city.state)
        self.assertNotEqual(result.zipcode, gecode.raw_zipcode)

        # Now the user wants to see the raw address.
        company.display_raw_addresses = True
        company.save()

        result = home.get_home_address_display_parts(
            company=company, raw=False, include_city_state_zip=True
        )

        self.assertNotEqual(result.street_line1, home.street_line1)
        self.assertNotEqual(result.street_line2, home.street_line2)
        self.assertNotEqual(result.city, home.city.name)
        self.assertNotEqual(result.state, home.state)
        self.assertNotEqual(result.zipcode, home.zipcode)

        self.assertEqual(result.street_line1, gecode.raw_street_line1)
        self.assertEqual(result.street_line2, gecode.raw_street_line2)
        self.assertEqual(result.city, gecode.raw_city.name)
        self.assertEqual(result.state, gecode.raw_city.state)
        self.assertEqual(result.zipcode, gecode.raw_zipcode)

        # Verify that without a company a straight raw we get the same result
        result = home.get_home_address_display_parts(raw=True, include_city_state_zip=True)
        self.assertNotEqual(result.street_line1, home.street_line1)
        self.assertNotEqual(result.street_line2, home.street_line2)
        self.assertNotEqual(result.city, home.city.name)
        self.assertNotEqual(result.state, home.state)
        self.assertNotEqual(result.zipcode, home.zipcode)

        self.assertEqual(result.street_line1, gecode.raw_street_line1)
        self.assertEqual(result.street_line2, gecode.raw_street_line2)
        self.assertEqual(result.city, gecode.raw_city.name)
        self.assertEqual(result.state, gecode.raw_city.state)
        self.assertEqual(result.zipcode, gecode.raw_zipcode)

    def test_get_home_address_display_parts_defaults(self):
        """
        Test get_home_address_display_parts with defaults:
        include_lot_number=True, include_confirmed=False, include_city_state_zip=False, raw=False,
        company=None
        """
        home = Home.objects.first()
        result = home.get_home_address_display_parts()
        self.assertEqual(home.street_line1, result.street_line1)
        self.assertEqual(home.street_line2, result.street_line2)
        self.assertEqual(home.lot_number, result.lot_number)
        self.assertEqual("", result.city)
        self.assertEqual("", result.state)
        self.assertEqual("", result.zipcode)
        self.assertEqual("", result.confirmed_designator)

    def test_get_home_address_display_parts_lot_number_not_included(self):
        """
        Test get_home_address_display_parts with:
        include_lot_number=False, include_confirmed=False, include_city_state_zip=False, raw=False,
        company=None
        """
        home = Home.objects.first()
        result = home.get_home_address_display_parts(include_lot_number=False)
        self.assertEqual(home.street_line1, result.street_line1)
        self.assertEqual(home.street_line2, result.street_line2)
        self.assertEqual("", result.lot_number)
        self.assertEqual("", result.city)
        self.assertEqual("", result.state)
        self.assertEqual("", result.zipcode)
        self.assertEqual("", result.confirmed_designator)

    def test_get_home_address_display_parts_include_confirmed(self):
        """
        Test get_home_address_display_parts with:
        include_lot_number=True, include_confirmed=True, include_city_state_zip=False, raw=False,
        company=None
        """
        home = Home.objects.first()
        Home.objects.filter(id=home.id).update(confirmed_address=True)
        home = Home.objects.get(id=home.id)
        result = home.get_home_address_display_parts(include_confirmed=True)
        self.assertEqual(home.street_line1, result.street_line1)
        self.assertEqual(home.street_line2, result.street_line2)
        self.assertEqual(home.lot_number, result.lot_number)
        self.assertEqual("", result.city)
        self.assertEqual("", result.state)
        self.assertEqual("", result.zipcode)
        self.assertEqual("\u25e6", result.confirmed_designator)

    def test_get_home_address_display_parts_include_city_state_zip(self):
        """
        Test get_home_address_display_parts with:
        include_lot_number=True, include_confirmed=False, include_city_state_zip=True, raw=False,
        company=None
        """
        home = Home.objects.first()
        Home.objects.filter(id=home.id).update(confirmed_address=True)
        home = Home.objects.get(id=home.id)
        result = home.get_home_address_display_parts(include_city_state_zip=True)
        self.assertEqual(home.street_line1, result.street_line1)
        self.assertEqual(home.street_line2, result.street_line2)
        self.assertEqual(home.lot_number, result.lot_number)
        self.assertEqual(home.city.name, result.city)
        self.assertEqual(home.state, result.state)
        self.assertEqual(home.zipcode, result.zipcode)
        self.assertEqual("", result.confirmed_designator)

    def test_get_home_address_display_defaults(self):
        """
        Test get_home_address_display with defaults:
        include_lot_number=True, include_confirmed=False, include_city_state_zip=False, raw=False,
        company=None
        """
        home = Home.objects.last()
        result = home.get_home_address_display()
        city_state_zip = ""
        confirmed_designator = ""
        expected = "{}{}{}{}{}".format(
            home.street_line1,
            ", {}".format(home.street_line2),
            city_state_zip,
            ", (Lot: {})".format(home.lot_number),
            confirmed_designator,
        )
        self.assertEqual(expected, result)

    def test_get_home_address_display_defaults_lot_number_not_included(self):
        """
        Test get_home_address_display with:
        include_lot_number=False, include_confirmed=False, include_city_state_zip=False, raw=False,
        company=None
        """
        home = Home.objects.first()
        result = home.get_home_address_display(include_lot_number=False)
        city_state_zip = ""
        confirmed_designator = ""
        lot_number = ""
        expected = "{}{}{}{}{}".format(
            home.street_line1,
            ", {}".format(home.street_line2),
            city_state_zip,
            lot_number,
            confirmed_designator,
        )
        self.assertEqual(expected, result)

    def test_get_home_address_display_defaults_include_confirmed(self):
        """
        Test get_home_address_display with:
        include_lot_number=True, include_confirmed=True, include_city_state_zip=False, raw=False,
        company=None
        """
        home = Home.objects.first()
        Home.objects.filter(id=home.id).update(confirmed_address=True)
        home = Home.objects.get(id=home.id)
        result = home.get_home_address_display(include_confirmed=True)
        city_state_zip = ""
        confirmed_designator = " ◦"
        expected = "{}{}{}{}{}".format(
            home.street_line1,
            ", {}".format(home.street_line2),
            city_state_zip,
            ", (Lot: {})".format(home.lot_number),
            confirmed_designator,
        )
        self.assertEqual(expected, result)

    def test_get_home_address_display_defaults_include_city_state_zip(self):
        """
        Test get_home_address_display with:
        include_lot_number=True, include_confirmed=False, include_city_state_zip=True, raw=False,
        company=None
        """
        home = Home.objects.last()
        Home.objects.filter(id=home.id).update(confirmed_address=True)
        home = Home.objects.get(id=home.id)
        result = home.get_home_address_display(include_city_state_zip=True)
        city_state_zip = ", {}, {}, {}".format(home.city.name, home.state, home.zipcode)
        confirmed_designator = ""
        expected = "{}{}{}{}{}".format(
            home.street_line1,
            ", {}".format(home.street_line2),
            city_state_zip,
            ", (Lot: {})".format(home.lot_number),
            confirmed_designator,
        )
        self.assertEqual(expected, result)

    def test_get_addr_defaults(self):
        """
        Test get_addr with defaults:
        include_city_state_zip=False, include_id=False, raw=False, company=None
        """
        home = Home.objects.last()
        expected = home.get_home_address_display(
            include_lot_number=False, include_city_state_zip=False
        )
        result = home.get_addr()
        self.assertEqual(expected, result)

    def test_get_addr_include_city_state_zip(self):
        """
        Test get_addr with:
        include_city_state_zip=True, include_id=False, raw=False, company=None
        """
        home = Home.objects.last()
        include_city_state_zip = True
        expected = home.get_home_address_display(
            include_lot_number=False, include_city_state_zip=include_city_state_zip
        )
        result = home.get_addr(include_city_state_zip=include_city_state_zip)
        self.assertEqual(expected, result)

    def test_get_eto_region_name_for_zipcode_has_eto_program(self):
        """
        Test get_eto_region_name_for_zipcode.
        home_status eep_program's slug is/starts with 'eto' AND
        user's company slug is in ('eto', 'peci', 'csg-qa')
        """
        from axis.eep_program.models import EEPProgram
        from axis.company.models import Company

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(slug="eto")
        home = EEPProgramHomeStatus.objects.get(id=home_status.id).home
        home.zipcode = "97756"  # this zipcode belongs to region 8 - 'Central - 8'
        user = User.objects.filter(company__isnull=False).first()
        Company.objects.filter(id=user.company.id).update(slug="eto")
        user = User.objects.get(id=user.id)
        result = home.get_eto_region_name_for_zipcode(user)
        self.assertIsNotNone(result)
        self.assertEqual("Central - 8", result)

    def test_get_eto_region_name_for_zipcode_superuser(self):
        """
        Test get_eto_region_name_for_zipcode.
        home_status eep_program's slug is/starts with 'eto' AND
        user's superuser
        """
        from axis.eep_program.models import EEPProgram
        from axis.core.tests.factories import general_super_user_factory

        user = general_super_user_factory()
        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(slug="eto")
        home = EEPProgramHomeStatus.objects.get(id=home_status.id).home
        home.zipcode = "97756"  # this zipcode belongs to region 8 - 'Central - 8'
        result = home.get_eto_region_name_for_zipcode(user)
        self.assertIsNotNone(result)
        self.assertEqual("Central - 8", result)

    def test_get_eto_region_name_user_can_not_see_region(self):
        """
        Test get_eto_region_name_for_zipcode.
        user.company slug is NOT in ('eto', 'peci', 'csg-qa') and is NOT superuser
        Expected result None
        """
        from axis.eep_program.models import EEPProgram

        home_status = EEPProgramHomeStatus.objects.first()
        EEPProgram.objects.filter(id=home_status.eep_program.id).update(slug="eto")
        home = EEPProgramHomeStatus.objects.get(id=home_status.id).home
        user = User.objects.filter(company__isnull=False).first()
        result = home.get_eto_region_name_for_zipcode(user)
        self.assertIsNone(result)

    def test_get_eto_region_name_not_eto_program(self):
        """
        Test get_eto_region_name_for_zipcode
        home_status eep_program's slug NOT 'eto' or starts with 'eto'
        """
        from axis.company.models import Company

        home = (
            EEPProgramHomeStatus.objects.filter(
                ~Q(eep_program__slug="eto") | ~Q(eep_program__slug__startswith="eto-")
            )
            .first()
            .home
        )
        user = User.objects.filter(company__isnull=False).first()
        Company.objects.filter(id=user.company.id).update(slug="eto")
        user = User.objects.get(id=user.id)
        result = home.get_eto_region_name_for_zipcode(user)
        self.assertIsNone(result)

    def test_get_eep_program_stats(self):
        """Test get_eep_program_stats. eep_program=None"""
        user = User.objects.get(username="home_sub_stats_builder_1")
        home = Home.objects.get(slug="home-sub-homestatus")
        result = home.get_eep_program_stats(user, eep_program=None)
        self.assertIsNotNone(result)
        expected = EEPProgramHomeStatus.objects.filter(company=user.company)
        self.assertEqual(expected.count(), result.count())

    def test_get_eep_program_stats_with_eep_program(self):
        """Test get_eep_program_stats() eep_program is NOT None"""
        from axis.eep_program.models import EEPProgram

        user = User.objects.get(username="home_sub_stats_builder_2")
        home = Home.objects.get(slug="home-sub-mult-homestatus")
        eep_program = EEPProgram.objects.get(name="EEP3")
        result = home.get_eep_program_stats(user, eep_program=eep_program)
        self.assertIsNotNone(result)
        total_company_homestatuses = EEPProgramHomeStatus.objects.filter(company=user.company)
        self.assertGreater(total_company_homestatuses.count(), result.count())

    def test_is_home_certified_false(self):
        """Test is_home_certified. Expected result False, since home is not part of a program"""
        home = Home.objects.get(slug="home-sub-homestatus")
        company = home.get_builder()
        stats = EEPProgramHomeStatus.objects.filter_by_company(company, home=home)
        self.assertGreater(stats.count(), 0)
        result = home.is_home_certified(company)
        self.assertFalse(result)

    def test_is_home_certified_true(self):
        """Test is_home_certified. Expected result True, Homestatuses have certification_date"""
        home = Home.objects.get(slug="home-sub-homestatus")
        company = home.get_builder()
        stats = EEPProgramHomeStatus.objects.filter_by_company(company, home=home)
        self.assertGreater(stats.count(), 0)
        stats.update(certification_date=now())
        result = home.is_home_certified(company)
        self.assertTrue(result)

    def test_has_sampling_lock_true_no_incentive_payment_and_cert_date(self):
        """
        Test has_sampling_lock. Expected result True because:
        home status No Incentive Payment Status and a cert date.
        """
        EEPProgramHomeStatus.objects.filter(eep_program__name="Restricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Restricted Program 1")
        home = home_status.home
        result = home.has_sampling_lock()
        self.assertTrue(result)

    def test_has_sampling_lock_true_ipp_failed_restart_state(self):
        """
        Test has_sampling_lock. Expected result True because:
        home status Incentive Payment Status is 'ipp_failed_restart' and a cert date.
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="ipp_failed_restart")
        self.assertEqual(ips_queryset.first().state, "ipp_failed_restart")

        home = home_status.home
        result = home.has_sampling_lock()
        self.assertTrue(result)

    def test_has_sampling_lock_true_payment_pending_state(self):
        """
        Test has_sampling_lock. Expected result True because:
        home status Incentive Payment Status is 'payment_pending' and a cert date.
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="payment_pending")
        self.assertEqual(ips_queryset.first().state, "payment_pending")

        home = home_status.home
        result = home.has_sampling_lock()
        self.assertTrue(result)

    def test_has_sampling_lock_true_resubmit_failed_state(self):
        """
        Test has_sampling_lock. Expected result True because:
        home status Incentive Payment Status is 'resubmit-failed' and a cert date.
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="resubmit-failed")
        self.assertEqual(ips_queryset.first().state, "resubmit-failed")

        home = home_status.home
        result = home.has_sampling_lock()
        self.assertTrue(result)

    def test_has_sampling_lock_true_pending_requirements_state(self):
        """
        Test has_sampling_lock. Expected result True because:
        home status Incentive Payment Status is 'ipp_payment_requirements' and a cert date.
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="ipp_payment_requirements")
        self.assertEqual(ips_queryset.first().state, "ipp_payment_requirements")

        home = home_status.home
        result = home.has_sampling_lock()
        self.assertTrue(result)

    def test_has_sampling_lock_false_ips_start_state(self):
        """
        Test has_sampling_lock.
        Expected result False because incentivepaymentstatus__state = 'start'
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="start")
        self.assertEqual(ips_queryset.first().state, "start")

        home = home_status.home
        result = home.has_sampling_lock()
        self.assertFalse(result)

    def test_has_sampling_lock_false_ips_failed_requirements_state(self):
        """
        Test has_sampling_lock. Expected result False because:
        incentivepaymentstatus__state = 'ipp_payment_failed_requirements'
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="ipp_payment_failed_requirements")
        self.assertEqual(ips_queryset.first().state, "ipp_payment_failed_requirements")

        home = home_status.home
        result = home.has_sampling_lock()
        self.assertFalse(result)

    def test_has_sampling_lock_false_no_cert_date(self):
        """Test has_sampling_lock. Expected result False because has no cert date."""
        EEPProgramHomeStatus.objects.filter(eep_program__name="Restricted Program 1").update(
            certification_date=None
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Restricted Program 1")
        home = home_status.home
        result = home.has_sampling_lock()
        self.assertFalse(result)

    def test_has_sampling_lock_false_no_sampleset(self):
        """Test has_sampling_lock. Expected result False because it does NOT have samplesets"""
        from axis.sampleset.models import SampleSetHomeStatus

        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="EEP4")
        home = home_status.home
        samplesets_count = (
            SampleSetHomeStatus.objects.current()
            .filter(home_status__in=home.homestatuses.all(), is_test_home=True)
            .count()
        )
        self.assertEqual(0, samplesets_count)
        result = home.has_sampling_lock()
        self.assertFalse(result)

    def test_has_locked_homestatuses_include_samplesets_true(self):
        """
        Test has_locked_homestatuses(include_samplesets=True).
        this test scenario is very similar to
        test_has_sampling_lock_true_no_incentive_payment_and_cert_date.
        """
        EEPProgramHomeStatus.objects.filter(eep_program__name="Restricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Restricted Program 1")
        home = home_status.home
        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertTrue(result)

    def test_has_locked_homestatuses_ipp_failed_restart_state(self):
        """
        Test has_locked_homestatuses
        this test scenario is very similar to test_has_sampling_lock_true_ipp_failed_restart_state
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="ipp_failed_restart")
        self.assertEqual(ips_queryset.first().state, "ipp_failed_restart")

        home = home_status.home
        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertTrue(result)

    def test_has_locked_homestatuses_payment_pending_state(self):
        """
        Test has_locked_homestatuses
        this test scenario is very similar to test_has_sampling_lock_true_payment_pending_state
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="payment_pending")
        self.assertEqual(ips_queryset.first().state, "payment_pending")

        home = home_status.home
        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertTrue(result)

    def test_has_locked_homestatuses_resubmit_failed_state(self):
        """
        Test has_locked_homestatuses
        this test scenario is very similar to test_has_sampling_lock_true_resubmit_failed_state
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="resubmit-failed")
        self.assertEqual(ips_queryset.first().state, "resubmit-failed")

        home = home_status.home
        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertTrue(result)

    def test_has_locked_homestatuses_ipp_payment_requirements_state(self):
        """
        Test has_locked_homestatuses
        this test scenario is very similar to test_has_sampling_lock_true_pending_requirements_state
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        EEPProgramHomeStatus.objects.filter(eep_program__name="Unrestricted Program 1").update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        ips_queryset = IncentivePaymentStatus.objects.filter(home_status=home_status)
        ips_queryset.update(state="ipp_payment_requirements")
        self.assertEqual(ips_queryset.first().state, "ipp_payment_requirements")

        home = home_status.home
        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertTrue(result)

    def test_has_locked_homestatuses_true_certified_with_no_incentives(self):
        """
        Test has_locked_homestatuses(include_samplesets=False).
        Expected result True since home is/has:
        certification_date AND has no incentives (IncentivePaymentStatus)
        """
        eep_program_name = "Restricted Program 1"
        EEPProgramHomeStatus.objects.filter(eep_program__name=eep_program_name).update(
            certification_date=now()
        )
        has_no_incentives = Q(incentivepaymentstatus__isnull=True)
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
        home = home_status.home
        number_no_incentives = home.homestatuses.filter(has_no_incentives).distinct().count()
        self.assertTrue(number_no_incentives)
        result = home.has_locked_homestatuses(include_samplesets=False)
        self.assertTrue(result)

    def test_has_locked_homestatuses_true_eto_programs_with_no_incentives(self):
        """
        Test has_locked_homestatuses(include_samplesets=False).
        Expected result True since home is/has:
        'eep_program__owner__slug': 'eto,
        'state': 'certification_pending'
        AND
        has no incentives (IncentivePaymentStatus)
        """
        from axis.eep_program.models import EEPProgram
        from axis.company.models import Company

        slugs = ["eto-2019", "eto-2020", "eto-2021", "eto-2022"]
        eep_program_name = "Restricted Program 1"
        EEPProgramHomeStatus.objects.filter(eep_program__name=eep_program_name).update(
            certification_date=None, state="certification_pending"
        )
        Company.objects.filter(id=EEPProgram.objects.get(name=eep_program_name).owner.id).update(
            slug="eto"
        )

        for slug in slugs:
            EEPProgram.objects.filter(name=eep_program_name).update(slug=slug)
            has_no_incentives = Q(incentivepaymentstatus__isnull=True)
            home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
            home = home_status.home
            number_no_incentives = home.homestatuses.filter(has_no_incentives).distinct().count()
            self.assertTrue(number_no_incentives)
            result = home.has_locked_homestatuses(include_samplesets=False)
            assertion_error_message = (
                "has_locked_homestatuses(include_samplesets=False), "
                "with eep_program__slug:'{}', "
                "eep_program__name:'{}', "
                "and incentivepaymentstatus__isnull=True,"
                "should return True".format(slug, eep_program_name)
            )
            self.assertTrue(result, assertion_error_message)

    def test_has_locked_homestatuses_eto_programs_and_certification_date(self):
        """
        Test has_locked_homestatuses(include_samplesets=False).
        Expected result True dince home is/has:
        certification_date
        AND
        IncentivePaymentStatus state is in ['ipp_failed_restart', 'payment_pending',
        'resubmit-failed', 'ipp_payment_requirements']
        """
        from axis.incentive_payment.models import IncentivePaymentStatus

        eep_program_name = "Unrestricted Program 1"
        EEPProgramHomeStatus.objects.filter(eep_program__name=eep_program_name).update(
            certification_date=now()
        )
        has_incentives = Q(incentivepaymentstatus__isnull=False)
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
        home = home_status.home
        number_incentives = home.homestatuses.filter(has_incentives).distinct().count()
        self.assertTrue(number_incentives)
        valid_states = [
            "ipp_failed_restart",
            "payment_pending",
            "resubmit-failed",
            "ipp_payment_requirements",
        ]
        for state in valid_states:
            IncentivePaymentStatus.objects.filter(home_status=home_status).update(state=state)
            result = home.has_locked_homestatuses(include_samplesets=False)
            assertion_error_message = (
                "has_locked_homestatuses(include_samplesets=False), "
                "with home_status state:'{}', "
                "eep_program__name:'{}', "
                "and incentivepaymentstatus__isnull=True,"
                "should return True".format(state, eep_program_name)
            )
            self.assertTrue(result, assertion_error_message)

    def test_has_locked_homestatuses_eto_programs_with_valid_incentives_states(self):
        """
        Test has_locked_homestatuses(include_samplesets=False).
        'eep_program__owner__slug': 'eto',
        'state': 'certification_pending'
        AND
        IncentivePaymentStatus state is in ['ipp_failed_restart', 'payment_pending',
        'resubmit-failed', 'ipp_payment_requirements']
        """
        from axis.company.models import Company
        from axis.eep_program.models import EEPProgram
        from axis.incentive_payment.models import IncentivePaymentStatus

        slugs = ["eto-2019", "eto-2020", "eto-2021", "eto-2022"]
        valid_states = [
            "ipp_failed_restart",
            "payment_pending",
            "resubmit-failed",
            "ipp_payment_requirements",
        ]
        eep_program_name = "Unrestricted Program 1"
        EEPProgramHomeStatus.objects.filter(eep_program__name=eep_program_name).update(
            certification_date=None, state="certification_pending"
        )

        Company.objects.filter(id=EEPProgram.objects.get(name=eep_program_name).owner.id).update(
            slug="eto"
        )

        for slug in slugs:
            EEPProgram.objects.filter(name=eep_program_name).update(slug=slug)
            has_incentives = Q(incentivepaymentstatus__isnull=False)
            home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
            home = home_status.home
            number_incentives = home.homestatuses.filter(has_incentives).distinct().count()
            self.assertTrue(number_incentives)
            for state in valid_states:
                IncentivePaymentStatus.objects.filter(home_status=home_status).update(state=state)
                result = home.has_locked_homestatuses(include_samplesets=False)
                assertion_error_message = (
                    "has_locked_homestatuses(include_samplesets=False), "
                    "with eep_program__slug:'{}', "
                    "with home_status state:'{}', "
                    "eep_program__name:'{}', "
                    "and incentivepaymentstatus__isnull=True,"
                    "should return True".format(slug, state, eep_program_name)
                )
                self.assertTrue(result, assertion_error_message)

    def test_has_locked_homestatuses_false_without_samplesets_1(self):
        """
        Test has_locked_homestatuses(include_samplesets=True).
        home_status has no certification_date AND its eep_program slug not in ['eto-2017',
        'eto-2018', 'eto-2019'] AND state is NOT 'certification_pending'
        Expected result False
        """
        from axis.sampleset.models import SampleSetHomeStatus

        eep_program_name = "EEP4"
        EEPProgramHomeStatus.objects.filter(eep_program__name=eep_program_name).update(
            certification_date=None, state="correction_required"
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
        home = home_status.home
        samplesets_count = (
            SampleSetHomeStatus.objects.current()
            .filter(home_status__in=home.homestatuses.all(), is_test_home=True)
            .count()
        )
        self.assertEqual(0, samplesets_count)

        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertFalse(result)

    def test_has_locked_homestatuses_false_without_samplesets_2(self):
        """
        Test has_locked_homestatuses(include_samplesets=True).
        home_status has incentivepaymentstatus with state = 'start'
        Expected result False
        """
        from axis.sampleset.models import SampleSetHomeStatus
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        eep_program_name = "EEP4"
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
        kwargs = {"home_status": home_status, "state": "start"}
        basic_incentive_payment_status_factory(**kwargs)
        home = home_status.home
        samplesets_count = (
            SampleSetHomeStatus.objects.current()
            .filter(home_status__in=home.homestatuses.all(), is_test_home=True)
            .count()
        )
        self.assertEqual(0, samplesets_count)

        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertFalse(result)

    def test_has_locked_homestatuses_false_without_samplesets_3(self):
        """
        Test has_locked_homestatuses(include_samplesets=True).
        home_status has incentivepaymentstatus with state = 'ipp_payment_failed_requirements'
        Expected result False
        """
        from axis.sampleset.models import SampleSetHomeStatus
        from axis.incentive_payment.tests.factories import basic_incentive_payment_status_factory

        eep_program_name = "EEP4"
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
        kwargs = {"home_status": home_status, "state": "ipp_payment_failed_requirements"}
        basic_incentive_payment_status_factory(**kwargs)
        home = home_status.home
        samplesets_count = (
            SampleSetHomeStatus.objects.current()
            .filter(home_status__in=home.homestatuses.all(), is_test_home=True)
            .count()
        )
        self.assertEqual(0, samplesets_count)

        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertFalse(result)

    def test_has_locked_homestatuses_false_without_certification_date(self):
        """
        Test has_locked_homestatuses(include_samplesets=True).
        home_status has samplesets, but no certification date
        Expected result False
        """
        from axis.sampleset.models import SampleSetHomeStatus

        eep_program_name = "Restricted Program 1"
        EEPProgramHomeStatus.objects.filter(eep_program__name=eep_program_name).update(
            certification_date=None
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
        home = home_status.home
        samplesets_count = (
            SampleSetHomeStatus.objects.current()
            .filter(home_status__in=home.homestatuses.all(), is_test_home=True)
            .count()
        )
        self.assertGreater(samplesets_count, 0)
        result = home.has_locked_homestatuses(include_samplesets=True)
        self.assertFalse(result)

    def test_has_locked_homestatuses_false_with_cert_date_and_incentive_payment(self):
        """
        Test has_locked_homestatuses(include_samplesets=True).
        home_status has samplesets AND a certification date AND IncentivePaymentStatus
        IncentivePaymentStatus state is in ['start', 'ipp_payment_failed_requirements']
        Expected result False
        """
        from axis.sampleset.models import SampleSetHomeStatus
        from axis.incentive_payment.models import IncentivePaymentStatus

        eep_program_name = "Unrestricted Program 1"
        states = ["start", "ipp_payment_failed_requirements"]
        EEPProgramHomeStatus.objects.filter(eep_program__name=eep_program_name).update(
            certification_date=now()
        )
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=eep_program_name)
        home = home_status.home
        samplesets_count = (
            SampleSetHomeStatus.objects.current()
            .filter(home_status__in=home.homestatuses.all(), is_test_home=True)
            .count()
        )
        self.assertGreater(samplesets_count, 0)
        for state in states:
            IncentivePaymentStatus.objects.filter(home_status=home_status).update(state=state)
            result = home.has_locked_homestatuses(include_samplesets=True)
            self.assertFalse(result)

    def test_pre_relationship_modification_data_changing_builders_for_subdivision(self):
        """
        Test pre_relationship_modification_data.
        for this test case home has subdivision and this subdivision has an explicit builder
        (i.e. subdivision.builder_org is NOT None). also, home is flagged as custom home.
        """
        from axis.company.models import Company
        from axis.messaging.models import Message
        from django.test.client import RequestFactory

        user_to_link = User.objects.filter(company__name="EEP5").first()
        builder_user = User.objects.get(username="builder_1")
        builder_co = builder_user.company
        companies = list(Company.objects.filter(name="Rater3"))
        user = User.objects.order_by("id").first()
        data = {"builder": builder_co}
        home = Home.objects.get(slug="home-sub")
        home.is_custom_home = True
        home.users.add(user_to_link)
        home.save()
        self.assertTrue(home.is_custom_home)

        request = RequestFactory().get("/")
        request.user = User.objects.order_by("id").last()
        home.pre_relationship_modification_data(data, "ids", companies, user, request)

        mod_home = Home.objects.get(slug="home-sub")
        self.assertFalse(mod_home.is_custom_home)
        msg = Message.objects.last()
        self.assertEqual(request.user, msg.user)

        self.assertEqual(msg.title, "Home and Subdivision Builder mismatch")

        msg = Message.objects.first()
        self.assertEqual(msg.title, "Attached User To Home without Company association")

    def test_pre_relationship_modification_data_changing_builders_for_subdivision_logged(self):
        """
        Test pre_relationship_modification_data.
        for this test case home has subdivision and this subdivision has an explicit builder
        (i.e. subdivision.builder_org is NOT None). also, home is flagged as custom home.
        """
        from axis.company.models import Company
        from axis.messaging.models import Message

        user_to_link = User.objects.filter(company__name="EEP5").first()
        builder_user = User.objects.get(username="builder_1")
        builder_co = builder_user.company
        companies = list(Company.objects.filter(name="Rater3"))
        user = User.objects.order_by("id").first()
        data = {"builder": builder_co}
        home = Home.objects.get(slug="home-sub")
        home.is_custom_home = True
        home.users.add(user_to_link)
        home.save()
        self.assertTrue(home.is_custom_home)

        home.pre_relationship_modification_data(data, "ids", companies, user)
        # since there's no request, the error is only logged
        messages = Message.objects.all()
        self.assertEqual(0, messages.count())

        mod_home = Home.objects.get(slug="home-sub")
        self.assertFalse(mod_home.is_custom_home)

    @patch("axis.relationship.models.Relationship.can_be_deleted")
    def test_pre_relationship_modification_data_home_association_removal_error(
        self, can_be_deleted
    ):
        """Test pre_relationship_modification_data"""
        from axis.company.models import Company
        from axis.messaging.models import Message
        from django.test.client import RequestFactory

        can_be_deleted.return_value = False

        companies = list(Company.objects.filter(name="Rater3"))
        user = User.objects.order_by("id").first()
        # data = {'builder': None}
        data = {}
        home = Home.objects.get(slug="home-sub")
        home.is_custom_home = True
        home.save()
        self.assertTrue(home.is_custom_home)

        request = RequestFactory().get("/")
        request.user = User.objects.order_by("id").last()
        home.pre_relationship_modification_data(data, "ids", companies, user, request)

        message = Message.objects.first()
        self.assertEqual(message.title, "Home Association Removal Error")

    @patch("axis.relationship.models.Relationship.can_be_deleted")
    def test_pre_relationship_modification_data_association_removal_error_logged(
        self, can_be_deleted
    ):
        """Test pre_relationship_modification_data"""
        from axis.company.models import Company
        from axis.messaging.models import Message

        can_be_deleted.return_value = False

        companies = list(Company.objects.filter(name="Rater3"))
        user = User.objects.order_by("id").first()
        # data = {'builder': None}
        data = {}
        home = Home.objects.get(slug="home-sub")
        home.is_custom_home = True
        home.save()
        self.assertTrue(home.is_custom_home)

        home.pre_relationship_modification_data(data, "ids", companies, user)
        # since there's no request, the error is only logged
        messages = Message.objects.all()
        self.assertEqual(0, messages.count())

    @patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus."
        "is_eligible_for_certification"
    )
    @patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_user_certify")
    @patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_be_edited")
    def test_get_home_status_breakdown(
        self, is_eligible_for_certification, can_user_certify, can_be_edited
    ):
        """Test get_home_status_breakdown using default arguments (as_dict=False)"""

        is_eligible_for_certification.return_value = True
        can_user_certify.return_value = True
        can_be_edited.return_value = True

        user = User.objects.get(company__name="EEP5")
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Unrestricted Program 1")
        home = home_status.home
        result = home.get_home_status_breakdown(user)

        breakdown_objs = [
            "stats_count",
            "stats_all",
            "stats_can_edit",
            "stats_can_view",
            "stats_can_transition_to_certify",
            "stats_can_certify",
            "stats_completed",
            "has_checklist",
        ]
        for item in breakdown_objs:
            self.assertTrue(hasattr(result, item))
        self.assertTrue(result.stats_count)
        self.assertTrue(len(result.stats_can_edit))
        self.assertTrue(len(result.stats_can_view))
        self.assertTrue(len(result.stats_can_certify))
        self.assertFalse(len(result.stats_can_transition_to_certify))
        self.assertFalse(len(result.stats_completed))
        self.assertFalse(result.has_checklist)

    @patch(
        "axis.home.models.eep_program_home_status.EEPProgramHomeStatus."
        "is_eligible_for_certification"
    )
    @patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_user_certify")
    @patch("axis.home.models.eep_program_home_status.EEPProgramHomeStatus.can_be_edited")
    def test_get_home_status_breakdown_dict_returned(
        self, is_eligible_for_certification, can_user_certify, can_be_edited
    ):
        """Test get_home_status_breakdown"""

        is_eligible_for_certification.return_value = True
        can_user_certify.return_value = True
        can_be_edited.return_value = True

        user = User.objects.get(company__name="EEP5")
        program_name = "Unrestricted Program 1"
        EEPProgramHomeStatus.objects.filter(eep_program__name=program_name).update(state="complete")
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=program_name)
        home = home_status.home
        result = home.get_home_status_breakdown(user, as_dict=True)

        breakdown_objs = [
            "stats_count",
            "stats_all",
            "stats_can_edit",
            "stats_can_view",
            "stats_can_transition_to_certify",
            "stats_can_certify",
            "stats_completed",
            "has_checklist",
        ]
        for item in breakdown_objs:
            self.assertIn(item, result)
        self.assertTrue(result["stats_count"])
        self.assertTrue(len(result["stats_can_edit"]))
        self.assertTrue(len(result["stats_can_view"]))
        self.assertTrue(len(result["stats_can_certify"]))
        self.assertFalse(len(result["stats_can_transition_to_certify"]))
        self.assertTrue(len(result["stats_completed"]))
        self.assertFalse(result["has_checklist"])

    def test_get_current_stage_user_none(self):
        """Test get_current_stage. scenario where user is None. expected result None"""
        home = Home.objects.first()
        result = home.get_current_stage(user=None)
        self.assertIsNone(result)

    def test_get_current_stage_none(self):
        """Test get_current_stage"""
        user = User.objects.get(company__name="EEP5")
        program_name = "Unrestricted Program 1"
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=program_name)
        home = home_status.home
        result = home.get_current_stage(user)
        self.assertIsNone(result)

    def test_get_current_stage_construnction_stage(self):
        """Test get_current_stage"""
        from axis.scheduling.models import ConstructionStage

        cs = ConstructionStage(name="Not Started", is_public=True, order=0)
        cs.save()
        user = User.objects.get(company__name="Provider1")
        program_name = "Unrestricted Program 1"
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=program_name)
        home = home_status.home
        result = home.get_current_stage(user)
        self.assertIsNotNone(result)
        self.assertEqual(result.stage, cs)
        self.assertEqual(result.home, home)
        self.assertEqual(result.company, user.company)

    def test_get_current_stage_construnction_status(self):
        """Test get_current_stage"""
        from axis.scheduling.models import ConstructionStatus, ConstructionStage

        ConstructionStage(name="Not Started", is_public=True, order=0).save()
        stage = ConstructionStage(name="Started", is_public=True, order=1)
        stage.save()
        user = User.objects.get(company__name="Provider1")
        builder = User.objects.get(username="builder_1")
        program_name = "Unrestricted Program 1"
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=program_name)
        home = home_status.home
        ConstructionStatus(
            company=home_status.company, stage=stage, home=home, start_date=now(), user=builder
        ).save()
        result = home.get_current_stage(user)
        self.assertIsNotNone(result)
        self.assertEqual(result.stage, stage)
        self.assertEqual(result.home, home)
        self.assertEqual(result.company, user.company)

    def test_get_ipp_payments_user_company_is_eep_sponsor(self):
        """
        Test get_ipp_payments.
        this method will return IncentiveDistribution objects filter by either company or customer
        for home. case 1 happens when user's company is_eep_sponsor is False,
        otherwise case 2 will occur.
        """
        from axis.incentive_payment.models import IncentiveDistribution, IPPItem

        user_company = User.objects.get(company__name="EEP7")
        self.assertTrue(user_company.company.is_eep_sponsor)
        incentive_dist = IncentiveDistribution.objects.first()
        ipp_item = IPPItem.objects.filter(incentive_distribution=incentive_dist).first()
        home_status = ipp_item.home_status
        home = home_status.home
        result = home.get_ipp_payments(user_company)
        self.assertTrue(result.count())

    def test_get_ipp_payments_user_company_is_not_eep_sponsor(self):
        """
        Test get_ipp_payments.
        this method will return IncentiveDistribution objects filter by either company or customer
        for home. case 1 happens when user's company is_eep_sponsor is False,
        otherwise case 2 will occur.
        """
        from axis.incentive_payment.models import IncentiveDistribution, IPPItem

        user_customer = User.objects.get(company__name="Builder1")
        self.assertFalse(user_customer.company.is_eep_sponsor)

        incentive_dist = IncentiveDistribution.objects.first()
        ipp_item = IPPItem.objects.filter(incentive_distribution=incentive_dist).first()
        home_status = ipp_item.home_status
        home = home_status.home
        result = home.get_ipp_payments(user_customer)
        self.assertTrue(result.count())

    def test_get_ipp_payments_empty(self):
        """
        Test get_ipp_payments.
        this method will return IncentiveDistribution objects filter by either company or customer
        for home. case 1 happens when user's company is_eep_sponsor is False,
        otherwise case 2 will occur.
        """
        from axis.incentive_payment.models import IncentiveDistribution, IPPItem

        user_company = User.objects.get(company__name="EEP5")
        self.assertTrue(user_company.company.is_eep_sponsor)
        incentive_dist = IncentiveDistribution.objects.first()
        ipp_item = IPPItem.objects.filter(incentive_distribution=incentive_dist).first()
        home_status = ipp_item.home_status
        home = home_status.home
        result = home.get_ipp_payments(user_company)
        self.assertFalse(result.count())

    def test_get_ipp_annotations_(self):
        """Test get_ipp_annotations"""
        user_company = User.objects.get(company__name="EEP7")
        home_status = EEPProgramHomeStatus.objects.filter(
            eep_program__owner=user_company.company
        ).first()
        home = home_status.home
        result = home.get_ipp_annotations(user_company)
        self.assertTrue(result.count())

    def test_get_ipp_annotations_none(self):
        """Test get_ipp_annotations"""

        user = User.objects.get(company__name="EEP5")
        program_name = "Unrestricted Program 1"
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name=program_name)
        home = home_status.home
        result = home.get_ipp_annotations(user)
        self.assertFalse(result.count())

    def test_get_answers_(self):
        """Test get_answers"""
        from axis.checklist.tests.factories import question_factory, answer_factory

        home = Home.objects.get(slug="home-sampling-1")
        question = question_factory()
        user = User.objects.order_by("id").first()
        answer_factory(question, home, user)
        answers = home.get_answers()
        self.assertTrue(answers.count())

    def test_get_answers_none(self):
        """Test get_answers"""

        home = Home.objects.get(slug="home-sampling-1")
        answers = home.get_answers()
        self.assertFalse(answers.count())

    def test_get_qa_statuses(self):
        """Test get_qa_statuses"""
        from axis.qa.models import QARequirement, QAStatus

        qa_user = User.objects.get(company__name="QA1")
        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Restricted Program 1")
        home = home_status.home
        requirement = QARequirement.objects.create(
            qa_company=qa_user.company,
            gate_certification=True,
            eep_program=home_status.eep_program,
            coverage_pct=0.51,
        )

        QAStatus.objects.create(
            owner=qa_user.company, requirement=requirement, home_status=home_status
        )

        result = home.get_qa_statuses()
        self.assertTrue(result.count())

    def test_get_qa_statuses_none_found(self):
        """Test get_qa_statuses"""

        home_status = EEPProgramHomeStatus.objects.get(eep_program__name="Restricted Program 1")
        home = home_status.home

        result = home.get_qa_statuses()
        self.assertFalse(result.count())

    def test_get_permit_and_occupancy_settings(self):
        """Test get_permit_and_occupancy_settings"""
        from axis.customer_eto.models import PermitAndOccupancySettings

        user = User.objects.get(company__name="Provider1")
        home = Home.objects.get(slug="home-sampling-1")
        PermitAndOccupancySettings.objects.create(owner=user.company, home=home)

        result = home.get_permit_and_occupancy_settings(user.company)
        expected = ["company", "subdivision", "home", "owner", "data"]
        for item in expected:
            self.assertIn(item, result)

    def test_get_references(self):
        """
        Test get_references.
        makes sure output generated by this method matches the given home data (dictionary)
        """
        home = Home.objects.get(slug="home-sampling-1")
        result = home.get_references()

        references = [
            "home__city_id",
            "home__county_id",
            "home__us_state",
            "home__climate_zone",
            "relationship_ids",
            "builder_id",
            "electric_utility_id",
            "gas_utility_id",
        ]
        for reference in references:
            self.assertIn(reference, result)

        relationships = home.relationships.values_list("id", flat=True)
        self.assertEqual(home.city.id, result[references[0]])
        self.assertEqual(home.county.id, result[references[1]])
        self.assertEqual(home.state, result[references[2]])
        self.assertEqual(str(home.county.climate_zone), result[references[3]])
        self.assertEqual(len(relationships), len(result[references[4]]))
        self.assertEqual(home.get_builder().id, result[references[5]])
        self.assertIsNone(result[references[6]])
        self.assertIsNone(result[references[7]])

    def test_get_preview_photo(self):
        home = Home.objects.first()
        home_photo = HomePhoto.objects.create(home=home, is_primary=True)

        self.assertEqual(home.get_preview_photo(), home_photo)
