"""neea_v2.py - Axis"""

__author__ = "Steven K"
__date__ = "7/20/21 09:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.core import management

from axis.checklist.tests.mixins import CollectedInputMixin
from axis.core.tests.test_views import DevNull
from .base import CustomerNEEABaseTestMixin

log = logging.getLogger(__name__)


class NEEAV2ProgramTestMixin(CustomerNEEABaseTestMixin):
    @classmethod
    def setUpTestData(cls):
        super(NEEAV2ProgramTestMixin, cls).setUpTestData()
        from django.contrib.contenttypes.models import ContentType
        from axis.annotation.models import Type as AnnotationType
        from axis.annotation.models import Annotation
        from axis.company.tests.factories import qa_organization_factory
        from axis.company.models import Company
        from axis.customer_neea.rtf_calculator.constants.default import (
            NEEA_WATER_HEATER_TIER_MAP,
        )
        from axis.eep_program.models import EEPProgram
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory
        from axis.floorplan.tests.factories import (
            floorplan_with_remrate_factory,
            add_dummy_blg_data_file,
        )
        from axis.geocoder.models import Geocode
        from axis.home.tests.factories import eep_program_custom_home_status_factory, home_factory
        from axis.home.models import EEPProgramHomeStatus
        from axis.relationship.models import Relationship
        from axis.relationship.utils import create_or_update_spanning_relationships
        from axis.remrate_data.tests.factories import udrh_simulation_factory

        cls.cr_qa = qa_organization_factory(
            slug="clearesult-qa",
            is_customer=True,
            name="Clear Result QA",
            city=cls.city,
        )

        cls.qa = qa_organization_factory(
            slug="qa-pacific-power-qa-wa",
            is_customer=True,
            name="Pacific Power QA",
            city=cls.city,
        )

        Relationship.objects.create_mutual_relationships(
            cls.neea,
            cls.ea_user.company,
            cls.ber_user.company,
            cls.electricity_provider,
            cls.gas_provider,
            cls.builder.company,
            cls.hvac.company,
            cls.qa,
        )

        Relationship.objects.create_mutual_relationships(
            cls.neea,
            cls.ea_user.company,
            cls.ber_user.company,
            cls.electricity_provider,
            cls.gas_provider,
            cls.builder.company,
            cls.hvac.company,
            cls.cr_qa,
        )

        management.call_command(
            "build_program", "-p", "neea-bpa", "--no_close_dates", stdout=DevNull()
        )
        neea_bpa = EEPProgram.objects.get()

        from axis.qa.models import QARequirement

        qa_types = [
            QARequirement.FILE_QA_REQUIREMENT_TYPE,
            QARequirement.FIELD_QA_REQUIREMENT_TYPE,
            QARequirement.PROGRAM_REVIEW_QA_REQUIREMENT_TYPE,
        ]
        for qa_type in qa_types:
            for company in [cls.cr_qa, cls.qa]:
                req = QARequirement.objects.create(
                    qa_company=Company.objects.get(id=company.id),
                    eep_program=neea_bpa,
                    type=qa_type,
                    gate_certification=1,
                    coverage_pct=0,
                )
                if company.id == cls.qa.id:
                    req.required_companies.add(Company.objects.get(id=cls.electricity_provider.id))

        basic_eep_program_checklist_factory(slug="neea-unk", owner=cls.neea, no_close_dates=True)

        assert EEPProgram.objects.count() == 2
        assert EEPProgram.objects.filter_by_user(cls.neea.users.first()).count() == 2
        assert EEPProgram.objects.filter_by_user(cls.ber_user).count() == 2
        assert EEPProgram.objects.filter_by_user(cls.ea_user).count() == 2
        assert EEPProgram.objects.filter_by_user(cls.unk_bldr).count() == 0

        udrh_filename = "OR Perf Path Zonal 2019-Final.udr"
        udrh_checksum = "3A9D8804"
        simulation = udrh_simulation_factory(
            site__site_label="Portland, OR",
            version="15.7.1",
            flavor="Rate",
            hot_water__type=3,
            hot_water__fuel_type=1,
            hot_water__energy_factor=0.91,
            air_conditioning__fuel_type=4,
            air_conditioning__type=1,
            heating__fuel_type=1,
            infiltration__mechanical_vent_type=2,
            hers__score=60,
            duct_system__leakage_test_exemption=False,
            duct_system__leakage_tightness_test=1,
            udrh_filename=udrh_filename,
            udrh_checksum=udrh_checksum,
            percent_improvement=0.21,
            company=cls.ea_user.company,
        )
        assert simulation.has_heat_pumps() is False  # PSE Check
        assert simulation.has_heat_pump_water_heaters() is False  # PSE Check

        err = "Percent improvement %.2f" % simulation.results.udrh_percent_improvement
        assert simulation.results.udrh_percent_improvement > 0.20, err

        floorplan = floorplan_with_remrate_factory(
            owner=cls.ea_user.company,
            remrate_target=simulation,
            subdivision__builder_org=Company.objects.filter(
                company_type=Company.BUILDER_COMPANY_TYPE
            ).get(id=cls.builder.company.id),
            subdivision__city=cls.city,
            subdivision__name="SubdivisionName",
        )
        add_dummy_blg_data_file(floorplan)

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
        addr.update({"geocode": True, "builder_org": cls.builder})
        home = home_factory(
            subdivision=floorplan.subdivision_set.first(),
            is_multi_family=False,
            **addr,
        )

        assert home.county.pnwzone is not None

        home_status = eep_program_custom_home_status_factory(
            home=home, floorplan=floorplan, eep_program=neea_bpa, company=cls.ea_user.company
        )

        assert EEPProgramHomeStatus.objects.count() == 1

        create_or_update_spanning_relationships(cls.ber_user.company, home_status.home)
        create_or_update_spanning_relationships(cls.builder.company, home_status.home)
        create_or_update_spanning_relationships(cls.ea_user.company, home_status.home)
        create_or_update_spanning_relationships(cls.electricity_provider, home_status.home)
        create_or_update_spanning_relationships(cls.gas_provider, home_status.home)
        create_or_update_spanning_relationships(cls.hvac.company, home_status.home)

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug="neea-bpa")
        home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )
        assert cls.qa.slug not in home_rels
        assert cls.cr_qa.slug not in home_rels

        project_start = AnnotationType.objects.get(slug="project-start-nr")
        Annotation.objects.create(
            type=project_start,
            content="12-01-2019",
            content_type=ContentType.objects.get_for_model(home_status),
            object_id=home_status.id,
        )

        water_tiers = dict(NEEA_WATER_HEATER_TIER_MAP)

        expected = {
            "neea-heating_system_config": {"input": "Central"},
            "neea-heating_source": {"input": "Heat Pump"},
            "neea-water_heater_tier": {"input": water_tiers["gas_tankless_ef_gte_0p9"]},
            "estar_std_refrigerators_installed": {"input": "No"},
            "estar_dishwasher_installed": {"input": "No"},
            "estar_front_load_clothes_washer_installed": {"input": "No"},
            "neea-clothes_dryer_tier": {"input": "None"},
            "cfl_installed": {"input": "5"},
            "led_installed": {"input": 5},
            "total_installed_lamps": {"input": "1009"},
            "smart_thermostat_installed": {"input": "Yes"},
            "qty_shower_head_1p5": {"input": "1"},
            "qty_shower_head_1p75": {"input": "0"},
            "neea-major-load-equipment": {"input": "No"},
            "bpa_upload_docs": {"input": "No"},
            "hvac-combo": {"input": "XXX"},
            "hvac-cooling-combo": {"input": "XXX"},
            "water-heater-combo": {"input": "XXX"},
            "ventilation-combo": {"input": "XXX"},
            # 'refrigerator-combo': {'input': 'XXX'},
            # 'clothes-washer-combo': {'input': 'XXX'},
            # 'clothes-dryer-combo': {'input': 'XXX'},
            # 'dishwasher-combo': {'input': 'XXX'},
            "range-oven-combo": {"input": "XXX"},
            "solar-combo": {"input": "XXX"},
            "house-fans-combo": {"input": "XXX"},
            "hrv-combo": {"input": "XXX"},
            # 'heat-pump-water-heater-serial-number': {'input': 'XXX'},
            "smart-thermostat-combo": {"input": "XXX"},
            "other-combo": {"input": "XXX"},
            "neea-electric_meter_number": {"input": "XXX"},
            "neea-gas_meter_number": {"input": "XXX"},
            # 'heat-pump-heater-serial-number': {'input': 'XXX'},
            "neea-program_redirected": {"input": "No"},
        }

        # Note the is commented b/c the Yes on smart thermostat will trigger smart-tstat-combo
        # unanswered = list(home_status.get_unanswered_questions().values_list('measure',
        # flat=True))
        # assert set(unanswered) == set(list(expected.keys())), \
        #     'SetUp - Initial expected is wrong {}'.format(
        #         set(unanswered).symmetric_difference(set(expected.keys())))

        for measure, data in expected.items():
            CollectedInputMixin().add_collected_input(home_status, measure, data)

        missing_checks = home_status.report_eligibility_for_certification()
        if missing_checks:
            msg = "** Warning! Failing NEEA BPA Certification Eligibility Requirements:\n  - "
            print(msg + "\n  - ".join(missing_checks) + "\n** End Warning\n")
