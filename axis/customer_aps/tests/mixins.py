"""fixturecompilers.py: Django customer_aps"""


__author__ = "Steven Klass"
__date__ = "4/14/14 3:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import logging

from django.core import management

from axis.company.models import Company
from axis.core.tests.test_views import DevNull
from axis.geographic.tests.factories import real_city_factory
from axis.customer_aps.utils import geolocate_apshome


log = logging.getLogger(__name__)


class CustomerAPSModelTestMixin:
    @classmethod
    def _add_users_and_base_stuff(cls):
        from axis.company.models import SponsorPreferences, Company
        from axis.core.tests.factories import provider_admin_factory, utility_admin_factory
        from axis.relationship.models import Relationship

        city = real_city_factory("Gilbert", "AZ")
        real_city_factory("Mesa", "AZ")

        aps_user = utility_admin_factory(
            company__is_eep_sponsor=True,
            company__electricity_provider=True,
            company__gas_provider=False,
            company__slug="aps",
            company__city=city,
            company__name="APS",
        )

        aps = aps_user.company
        aps.update_permissions("customer_aps")

        efl_user = provider_admin_factory(
            company__name="EFL",
            company__slug="efl",
            company__city=city,
        )
        ei_user = provider_admin_factory(
            company__name="EI",
            company__slug="energy-inspectors",
            company__city=city,
        )
        provider_admin_factory(
            company__name="BAD",
            company__slug="bad",
            username="bad_user",
            company__city=city,
        )

        SponsorPreferences.objects.get_or_create(sponsor=aps, sponsored_company=ei_user.company)
        SponsorPreferences.objects.get_or_create(sponsor=aps, sponsored_company=efl_user.company)

        assert Company.objects.get(slug="efl").sponsors.count() == 1
        assert Company.objects.get(slug="energy-inspectors").sponsors.count() == 1

        Relationship.objects.create_mutual_relationships(aps, ei_user.company)
        Relationship.objects.create_mutual_relationships(aps, efl_user.company)

    @classmethod
    def setUpTestData(cls):
        from axis.company.models import Company
        from axis.eep_program.models import EEPProgram
        from axis.customer_aps.utils import geolocate_apshome
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory
        from axis.home.tests.factories import certified_custom_home_with_checklist_factory
        from axis.home.models import EEPProgramHomeStatus

        cls.city = real_city_factory("Gilbert", "AZ")
        cls._add_users_and_base_stuff()

        cls.aps = Company.objects.get(slug="aps")
        cls.aps_user = cls.aps.users.get()
        cls.efl = Company.objects.get(slug="efl")
        cls.efl_user = cls.efl.users.get()
        cls.ei = Company.objects.get(slug="energy-inspectors")
        cls.ei_user = cls.ei.users.get()
        cls.bad_user = Company.objects.get(slug="bad").users.get()

        aps_v3 = basic_eep_program_checklist_factory(
            slug="aps-energy-star-v3-2018",
            min_hers_score=-1,
            max_hers_score=100,
            rater_incentive_dollar_value=0,
            owner=cls.aps,
            is_active=True,
            builder_incentive_dollar_value=500,
            program_visibility_date=datetime.datetime(2018, 1, 1),
            program_start_date=datetime.datetime(2018, 4, 1),
            name="APS ENERGY STAR V3 2018",
            require_rem_data=True,
            no_close_dates=True,
        )

        basic_eep_program_checklist_factory(
            slug="aps-energy-star-v3-hers-60-2018",
            min_hers_score=0,
            max_hers_score=-1,
            rater_incentive_dollar_value=0,
            owner=cls.aps,
            is_active=True,
            builder_incentive_dollar_value=1000,
            program_visibility_date=datetime.datetime(2018, 1, 1),
            program_start_date=datetime.datetime(2018, 4, 1),
            name="APS ENERGY STAR V3 2018 HERS 60",
            require_rem_data=True,
            no_close_dates=True,
        )

        assert EEPProgram.objects.count() == 2, "Wrong Programs expected 2"
        assert EEPProgram.objects.filter_by_user(cls.aps_user).count() == 2, (
            "Wrong APS Users " "expected 4"
        )
        assert (
            EEPProgram.objects.filter_by_user(cls.ei_user).count() >= 2
        ), "Wrong EI Users expected 2"
        assert (
            EEPProgram.objects.filter_by_user(cls.efl_user).count() >= 2
        ), "Wrong EFL Users expected 2"
        assert (
            EEPProgram.objects.filter_by_user(cls.bad_user).count() == 0
        ), "Wrong BAD Users expected 0"

        floorplan = floorplan_with_remrate_factory(
            owner=cls.efl_user.company,
            subdivision=False,
            name="floorplan75",
            remrate_target__company=cls.efl_user.company,
            remrate_target__energystar__energy_star_v3p1_pv_score=64,
            remrate_target__site__climate_zone="2B",
        )

        assert floorplan.remrate_target.site.climate_zone == "2B", "Wrong Climate Zone"

        stat = certified_custom_home_with_checklist_factory(
            eep_program=aps_v3,
            company=cls.efl_user.company,
            home__city=cls.city,
            home__builder_org__city=cls.city,
            home__builder_org__name="builder",
            home__street_line1="124 E. Olive Avenue",
            home__street_line2=None,
            home__state="AZ",
            home__lot_number="123",
            home__zipcode="85234",
            home__geocode=True,
            floorplan=floorplan,
            certify=False,
        )

        assert stat.home.climate_zone.zone == 2, "Wrong Climate Zone 2!={}".format(
            stat.home.climate_zone.zone
        )
        assert set((EEPProgram.objects.values_list("slug", flat=True))) == {
            "aps-energy-star-v3-2018",
            "aps-energy-star-v3-hers-60-2018",
        }

        stat.home._generate_utility_type_hints(None, None, True)
        assert stat.get_electric_company().slug == "aps", "Wrong Electric Company"

        aps_home = {
            "premise_id": "138521283",
            "raw_lot_number": None,
            "raw_street_number": "124",
            "raw_prefix": "E",
            "raw_street_name": "OLIVE",
            "raw_suffix": "AVE",
            "raw_street_line_2": None,
            "raw_city": "GILBERT",
            "raw_state": "AZ",
            "raw_zip": "85234",
        }
        matches = geolocate_apshome(**aps_home)
        assert len(matches) == 1, "Bad geocode we need one we got {}".format(len(matches))
        assert stat.pct_complete == 100, "Bad PCT Complete: {}".format(stat.pct_complete)
        assert stat.is_eligible_for_certification(), "Expected it to ready to certify"
        assert Company.objects.count() == 5, "Incorrect Companies: {}".format(
            Company.objects.values("name", "slug")
        )
        assert EEPProgramHomeStatus.objects.count() == 1, "Incorrect Stats: {}".format(
            EEPProgramHomeStatus.objects.count()
        )


class CustomerAPS2019ModelTestMixin(CustomerAPSModelTestMixin):
    """APS 2019 PROGRAMS"""

    @classmethod
    def setUpTestData(cls):
        from axis.eep_program.models import EEPProgram
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory
        from axis.home.tests.factories import certified_custom_home_with_checklist_factory

        cls.city = real_city_factory("Gilbert", "AZ")

        cls._add_users_and_base_stuff()

        cls.aps = Company.objects.get(slug="aps")
        cls.aps_user = cls.aps.users.get()
        cls.efl = Company.objects.get(slug="efl")
        cls.efl_user = cls.efl.users.get()
        cls.ei = Company.objects.get(slug="energy-inspectors")
        cls.ei_user = cls.ei.users.get()
        cls.bad_user = Company.objects.get(slug="bad").users.get()

        from django_input_collection.models import CollectionRequest

        collection_request = CollectionRequest.objects.create(
            max_instrument_inputs=None, max_instrument_inputs_per_user=None
        )

        eep_program = EEPProgram.objects.create(
            name="APS ENERGY STAR V3 2019",
            owner=cls.aps,
            opt_in=False,
            min_hers_score=0,
            max_hers_score=100,
            per_point_adder=0.0,
            builder_incentive_dollar_value=200.0,
            rater_incentive_dollar_value=0.0,
            collection_request=collection_request,
            enable_standard_disclosure=False,
            require_floorplan_approval=True,
            comment="APS ENERGY STAR V3 2019",
            require_input_data=True,
            require_rem_data=False,
            require_model_file=False,
            require_ekotrope_data=False,
            manual_transition_on_certify=False,
            require_rater_of_record=False,
            require_builder_assigned_to_home=True,
            require_builder_relationship=True,
            require_hvac_assigned_to_home=False,
            require_hvac_relationship=False,
            require_utility_assigned_to_home=True,
            require_utility_relationship=False,
            require_rater_assigned_to_home=False,
            require_rater_relationship=False,
            require_provider_assigned_to_home=True,
            require_provider_relationship=True,
            require_qa_assigned_to_home=False,
            require_qa_relationship=False,
            allow_sampling=True,
            allow_metro_sampling=True,
            require_resnet_sampling_provider=False,
            is_legacy=False,
            is_public=False,
            program_visibility_date=datetime.date(2018, 11, 1),
            program_start_date=datetime.date(2018, 11, 1),
            program_close_warning_date=datetime.date(2019, 11, 1),
            program_close_warning="No new homes allowed after Dec 31 2019",
            program_close_date=datetime.date(2020, 1, 1),
            program_end_date=datetime.date(2020, 3, 1),
            is_active=True,
            is_qa_program=False,
            slug="aps-energy-star-v3-2019",
        )

        management.call_command(
            "build_program",
            "-p",
            "aps-energy-star-2019-tstat",
            "--no_close_dates",
            stdout=DevNull(),
        )
        management.call_command(
            "build_program",
            "-p",
            "aps-energy-star-2019-tstat-addon",
            "--no_close_dates",
            stdout=DevNull(),
        )

        for program in EEPProgram.objects.all():
            program.program_close_warning_date = None
            program.program_close_date = None
            program.program_end_date = None
            program.save()

        floorplan = floorplan_with_remrate_factory(
            owner=cls.efl_user.company,
            subdivision=False,
            name="floorplan75",
            remrate_target__company=cls.efl_user.company,
            remrate_target__energystar__energy_star_v3p1_pv_score=64,
            remrate_target__site__climate_zone="2B",
        )

        assert floorplan.remrate_target.site.climate_zone == "2B", "Wrong Climate Zone"

        stat = certified_custom_home_with_checklist_factory(
            eep_program=eep_program,
            company=cls.efl_user.company,
            home__city=cls.city,
            home__builder_org__city=cls.city,
            home__builder_org__name="builder",
            home__street_line1="124 E. Olive Avenue",
            home__street_line2=None,
            home__state="AZ",
            home__lot_number="123",
            home__zipcode="85234",
            home__geocode=True,
            floorplan=floorplan,
            certify=False,
        )

        assert stat.home.climate_zone.zone == 2, "Wrong Climate Zone 2!={}".format(
            stat.home.climate_zone.zone
        )

        stat.home._generate_utility_type_hints(None, None, True)
        assert stat.get_electric_company().slug == "aps", "Wrong Electric Company"

        aps_home = {
            "premise_id": "138521283",
            "raw_lot_number": None,
            "raw_street_number": "124",
            "raw_prefix": "E",
            "raw_street_name": "OLIVE",
            "raw_suffix": "AVE",
            "raw_street_line_2": None,
            "raw_city": "GILBERT",
            "raw_state": "AZ",
            "raw_zip": "85234",
        }
        matches = geolocate_apshome(**aps_home)
        assert len(matches) == 1, "Bad geocode we need one we got {}".format(len(matches))
        assert stat.pct_complete == 100, "Bad PCT Complete: {}".format(stat.pct_complete)
        try:
            assert stat.is_eligible_for_certification(), "Expected it to ready to certify"
        except AssertionError:
            import pprint

            for k, v in stat.get_progress_analysis()["requirements"].items():
                if v["status"] is False:
                    print(k)
                    pprint.pprint(v)
            raise


class CustomerAPSBulkHomeTests(CustomerAPSModelTestMixin):
    """APS Bulks stuff"""

    @classmethod
    def setUpTestData(cls):
        super(CustomerAPSBulkHomeTests, cls).setUpTestData()

        from axis.company.models import Company, BuilderOrganization
        from axis.geocoder.models import Geocode
        from axis.customer_aps.utils import geolocate_apshome
        from axis.home.tests.factories import custom_home_factory
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory
        from axis.scheduling.models import ConstructionStage

        ConstructionStage.objects.create(name="Started", is_public=True, order=1)

        # These need to align verbatim to what is in the xls.
        from axis.geographic.models import City

        addrs = [
            {
                "street_line1": "124 E. Olive Avenue",
                "street_line2": None,
                "city": City.objects.get(name="Gilbert"),
                "state": "AZ",
                "zipcode": "85234",
                "lot_number": "123",
            },
            {
                "street_line1": "350 West Horseshoe Ave",
                "street_line2": None,
                "city": City.objects.get(name="Gilbert"),
                "state": "AZ",
                "zipcode": "85233",
                "lot_number": "456",
            },
            {
                "street_line1": "291 S Park Grove Lane",
                "street_line2": None,
                "city": City.objects.get(name="Gilbert"),
                "state": "AZ",
                "zipcode": "85296",
                "lot_number": "789",
            },
        ]

        for addr in addrs:
            matches = Geocode.objects.get_matches(raw_address=None, **addr)
            assert len(matches) == 1, "Bad geocode we need one we got {}".format(len(matches))
            addr.update(
                {
                    "geocode": True,
                    "builder_org": Company.objects.filter(
                        company_type=Company.BUILDER_COMPANY_TYPE
                    ).get(),
                }
            )
            custom_home_factory(**addr)

        aps_homes_addrs = [
            {
                "premise_id": "138521283",
                "raw_lot_number": None,
                "raw_street_number": "124",
                "raw_prefix": "E",
                "raw_street_name": "OLIVE",
                "raw_suffix": "AVE",
                "raw_street_line_2": None,
                "raw_city": "GILBERT",
                "raw_state": "AZ",
                "raw_zip": "85234",
            },
            {
                "premise_id": "214611288",
                "raw_lot_number": None,
                "raw_street_number": "350",
                "raw_prefix": "W",
                "raw_street_name": "HORSESHOE",
                "raw_suffix": "AVE",
                "raw_street_line_2": None,
                "raw_city": "GILBERT",
                "raw_state": "AZ",
                "raw_zip": "85233",
            },
            {
                "premise_id": "322112282",
                "raw_lot_number": "14",
                "raw_street_number": "291",
                "raw_prefix": "S",
                "raw_street_name": "PARK GROVE",
                "raw_suffix": "LN",
                "raw_street_line_2": None,
                "raw_city": "GILBERT",
                "raw_state": "AZ",
                "raw_zip": "85296",
            },
        ]

        for addr in aps_homes_addrs:
            matches = geolocate_apshome(**addr)
            print(matches)
            assert len(matches) == 1, "Bad geocode we need one we got {}".format(len(matches))

        efl = Company.objects.get(slug="efl")
        fp = floorplan_with_remrate_factory(
            owner=efl,
            name="floorplan50",
            remrate_target__company=efl,
            remrate_target__energystar__energy_star_v3p2_pv_score=50,
            remrate_target__site__climate_zone="2B",
        )

        from axis.eep_program.models import EEPProgram

        assert (
            fp.get_hers_score_for_program(EEPProgram.objects.filter(owner__slug="aps").last()) == 50
        )

        fp = floorplan_with_remrate_factory(
            owner=efl,
            name="floorplan",
            remrate_target__company=efl,
            remrate_target__energystar__energy_star_v3p2_pv_score=64,
            remrate_target__site__climate_zone="2B",
        )

        assert (
            fp.get_hers_score_for_program(EEPProgram.objects.filter(owner__slug="aps").last()) == 64
        )
