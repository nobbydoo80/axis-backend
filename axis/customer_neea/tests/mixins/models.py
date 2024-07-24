"""models.py - Axis"""

__author__ = "Steven K"
__date__ = "7/20/21 09:20"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from axis.customer_neea.tests.mixins.base import CustomerNEEABaseTestMixin

log = logging.getLogger(__name__)


class CustomerNEEAModelTestMixin(CustomerNEEABaseTestMixin):
    @classmethod
    def setUpTestData(cls):
        super(CustomerNEEAModelTestMixin, cls).setUpTestData()

        from axis.eep_program.models import EEPProgram
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory
        from axis.home.tests.factories import custom_home_factory
        from axis.floorplan.tests.factories import floorplan_with_remrate_factory
        from axis.geocoder.models import Geocode

        basic_eep_program_checklist_factory(
            slug="neea-energy-star-v3",
            min_hers_score=0,
            max_hers_score=100,
            rater_incentive_dollar_value=0,
            owner=cls.neea,
            is_active=True,
            builder_incentive_dollar_value=0,
            program_start_date=datetime.datetime(2012, 4, 1),
            require_builder_relationship=True,
            require_builder_assigned_to_home=True,
            require_hvac_relationship=True,
            require_hvac_assigned_to_home=True,
            require_utility_relationship=True,
            require_utility_assigned_to_home=True,
            require_rater_relationship=True,
            require_rater_assigned_to_home=True,
            require_provider_relationship=True,
            require_provider_assigned_to_home=True,
            program_end_date=datetime.datetime(2016, 4, 30),
            name="Northwest ENERGY STAR Version 3: Prescriptive",
            require_rem_data=False,
            no_close_dates=True,
        )

        basic_eep_program_checklist_factory(
            slug="neea-energy-star-v3-performance",
            min_hers_score=61,
            max_hers_score=100,
            rater_incentive_dollar_value=0,
            owner=cls.neea,
            is_active=True,
            builder_incentive_dollar_value=0,
            program_start_date=datetime.datetime(2012, 4, 1),
            require_builder_relationship=True,
            require_builder_assigned_to_home=True,
            require_hvac_relationship=True,
            require_hvac_assigned_to_home=True,
            require_utility_relationship=True,
            require_utility_assigned_to_home=True,
            require_rater_relationship=True,
            require_rater_assigned_to_home=True,
            require_provider_relationship=True,
            require_provider_assigned_to_home=True,
            program_end_date=datetime.datetime(2016, 4, 30),
            name="Northwest ENERGY STAR Version 3: Performance",
            require_rem_data=True,
            no_close_dates=True,
        )

        basic_eep_program_checklist_factory(
            slug="neea-performance-2015",
            min_hers_score=61,
            max_hers_score=100,
            rater_incentive_dollar_value=0,
            owner=cls.neea,
            is_active=True,
            builder_incentive_dollar_value=0,
            program_start_date=datetime.datetime(2015, 6, 1),
            require_builder_relationship=True,
            require_builder_assigned_to_home=True,
            require_hvac_relationship=True,
            require_hvac_assigned_to_home=True,
            require_utility_relationship=True,
            require_utility_assigned_to_home=True,
            require_rater_relationship=True,
            require_rater_assigned_to_home=True,
            require_provider_relationship=True,
            require_provider_assigned_to_home=True,
            name="NEEA 2015 ENERGY STAR® V3 Rev 8 Single-Family / Multi-Family",
            require_rem_data=True,
            no_close_dates=True,
        )

        basic_eep_program_checklist_factory(
            slug="neea-prescriptive-2015",
            min_hers_score=0,
            max_hers_score=100,
            rater_incentive_dollar_value=0,
            owner=cls.neea,
            is_active=True,
            builder_incentive_dollar_value=0,
            program_start_date=datetime.datetime(2015, 6, 1),
            require_builder_relationship=True,
            require_builder_assigned_to_home=True,
            require_hvac_relationship=True,
            require_hvac_assigned_to_home=True,
            require_utility_relationship=True,
            require_utility_assigned_to_home=True,
            require_rater_relationship=True,
            require_rater_assigned_to_home=True,
            require_provider_relationship=True,
            require_provider_assigned_to_home=True,
            name="NEEA 2015 ENERGY STAR® V3 Rev 8 Multi-Family",
            require_rem_data=False,
            no_close_dates=True,
        )

        basic_eep_program_checklist_factory(slug="neea-unk", owner=cls.neea, no_close_dates=True)

        assert EEPProgram.objects.count() == 5
        assert EEPProgram.objects.filter_by_user(cls.neea.users.first()).count() == 5
        assert EEPProgram.objects.filter_by_user(cls.ber_user).count() == 3
        assert EEPProgram.objects.filter_by_user(cls.ea_user).count() == 3
        assert EEPProgram.objects.filter_by_user(cls.unk_bldr).count() == 0
        assert EEPProgram.objects.filter_by_user(cls.unk_hvac).count() == 0

        floorplan_with_remrate_factory(
            owner=cls.ea_user.company,
            name="floorplan",
            remrate_target__company=cls.ea_user.company,
            remrate_target__energystar__energy_star_v2p5_pv_score=75,
        )

        # These need to align verbatim to what is in the xls.
        addrs = [
            {
                "street_line1": "4905 N Oberlin St",
                "street_line2": None,
                "city": cls.city,
                "state": "OR",
                "zipcode": "97203",
            },
            {
                "street_line1": "612 North Shaver St",
                "street_line2": None,
                "city": cls.city,
                "state": "OR",
                "zipcode": "97227",
            },
            {
                "street_line1": "234 SW Salmon St",
                "street_line2": None,
                "city": cls.city,
                "state": "OR",
                "zipcode": "97204",
            },
        ]

        for addr, builder in zip(
            addrs, [cls.builder.company, cls.unk_bldr.company, cls.unk_bldr.company]
        ):
            matches = Geocode.objects.get_matches(raw_address=None, **addr)
            err = "Bad geocode we need one we got {} - {}".format(len(matches), addr)
            assert len(matches) == 1, err
            addr.update({"geocode": True, "builder_org": builder})
            custom_home_factory(**addr)
