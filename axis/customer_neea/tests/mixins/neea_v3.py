"""neea_v3.py - Axis"""

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
from axis.customer_neea.rtf_calculator.constants.default import (
    ELECTRIC_RESISTANCE,
    NONE_LABEL,
    DRYER_TIER_2_LABEL,
)
from axis.customer_neea.rtf_calculator.constants.neea_v3 import (
    NEEA_HEATING_SYSTEM_CONFIGS,
)
from axis.customer_neea.strings import NEEA_BPA_2021_CHECKSUMS
from simulation.enumerations import (
    FuelType,
    WaterHeaterStyle,
    HotWaterEfficiencyUnit,
    WaterHeaterLiquidVolume,
    HeatingEfficiencyUnit,
    DistributionSystemType,
    SourceType,
    FoundationType,
    Location,
    AnalysisType,
    ResidenceType,
    VentilationRateUnit,
    MechanicalVentilationType,
    HeatingCoolingCapacityUnit,
)
from .base import CustomerNEEABaseTestMixin

log = logging.getLogger(__name__)


class NEEAV3ProgramTestMixin(CustomerNEEABaseTestMixin):
    @property
    def floorplan_factory_kwargs(self):
        checksum, udrh = next(
            (
                (x, y)
                for x, y in NEEA_BPA_2021_CHECKSUMS
                if y.startswith("WAPerfPath-ElecZonal-ElecDHW-Medium_")
            )
        )
        owner = self.ber_user.company if hasattr(self, "ber_user") else None
        builder = self.builder.company if hasattr(self, "builder") else None
        city = self.city if hasattr(self, "city") else None

        return dict(
            owner=owner,
            use_udrh_simulation=True,
            simulation__pct_improvement=21.0,
            simulation__conditioned_area=2150.0,
            simulation__source_type=SourceType.REMRATE_SQL,
            simulation__version="16.0.6",
            simulation__flavor="Rate",
            simulation__design_model=AnalysisType.WA_2021_ZONAL_MEDIUM_EHEW_DESIGN,
            simulation__reference_model=AnalysisType.WA_2021_ZONAL_MEDIUM_EHEW_REFERENCE,
            simulation__residence_type=ResidenceType.SINGLE_FAMILY_DETACHED,
            simulation__location__climate_zone__zone="4",
            simulation__location__climate_zone__moisture_regime="C",
            simulation__location__weather_station="Eugene",
            simulation__analysis__source_qualifier=checksum,  # Zonal!
            simulation__analysis__source_name=udrh,  # Zonal!
            simulation__heater__fuel=FuelType.ELECTRIC,
            simulation__heater__efficiency_unit=HeatingEfficiencyUnit.AFUE,
            simulation__heater__capacity_unit=HeatingCoolingCapacityUnit.KBTUH,
            simulation__water_heater__style=WaterHeaterStyle.CONVENTIONAL,
            simulation__water_heater__fuel=FuelType.ELECTRIC,
            simulation__water_heater__efficiency=0.92,
            simulation__water_heater__efficiency_unit=HotWaterEfficiencyUnit.ENERGY_FACTOR,
            simulation__water_heater__tank_units=WaterHeaterLiquidVolume.GALLON,
            simulation__mechanical_ventilation__type=MechanicalVentilationType.SUPPLY_ONLY,
            simulation__mechanical_ventilation__hour_per_day=24.0,
            simulation__mechanical_ventilation__ventilation_rate=3500.0,
            simulation__mechanical_ventilation__ventilation_rate_unit=VentilationRateUnit.CFM,
            simulation__distribution_system__system_type=DistributionSystemType.RADIANT,
            simulation__appliances__refrigerator_consumption=700,
            simulation__appliances__refrigerator_location=Location.CONDITIONED_SPACE,
            simulation__appliances__dishwasher_consumption=300,
            simulation__appliances__clothes_washer_efficiency=0.5,
            simulation__appliances__clothes_washer_label_electric_consumption=500,
            simulation__appliances__clothes_dryer_efficiency=2.5,
            simulation__appliances__clothes_dryer_location=Location.CONDITIONED_SPACE,
            simulation__air_conditioner_count=0,
            simulation__utility_rate_fuel__electric={"name": "PAC-Jan2021"},
            simulation__utility_rate_fuel__natural_gas={"name": "NWN_OR-Jan2021"},
            subdivision__builder_org=builder,
            subdivision__city=city,
            subdivision__name="Subdivision",
        )

    @classmethod
    def setUpTestData(cls):
        super(NEEAV3ProgramTestMixin, cls).setUpTestData()
        from django.contrib.contenttypes.models import ContentType
        from axis.annotation.models import Type as AnnotationType
        from axis.annotation.models import Annotation
        from axis.company.tests.factories import qa_organization_factory
        from axis.company.models import Company
        from axis.eep_program.models import EEPProgram
        from axis.floorplan.tests.factories import (
            floorplan_with_simulation_factory,
            add_dummy_blg_data_file,
        )
        from axis.geocoder.models import Geocode
        from axis.home.tests.factories import eep_program_custom_home_status_factory, home_factory
        from axis.home.models import EEPProgramHomeStatus
        from axis.relationship.models import Relationship
        from axis.relationship.utils import create_or_update_spanning_relationships

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
            "build_program", "-p", "neea-bpa-v3", "--no_close_dates", stdout=DevNull()
        )
        neea_bpa = EEPProgram.objects.get(slug="neea-bpa-v3")

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

        data = NEEAV3ProgramTestMixin().floorplan_factory_kwargs

        data["owner"] = cls.ber_user.company
        data["subdivision__city"] = cls.city
        data["subdivision__builder_org"] = cls.builder.company

        floorplan = floorplan_with_simulation_factory(**data)
        assert str(floorplan.simulation.location.climate_zone) == "4C"
        assert str(floorplan.simulation.climate_zone) == "4C"

        assert floorplan.simulation.air_source_heat_pumps.count() == 0  # PSE Check
        assert floorplan.simulation.ground_source_heat_pumps.count() == 0  # PSE Check
        assert floorplan.simulation.water_heaters.heat_pumps().count() == 0  # PSE Check

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

        create_or_update_spanning_relationships(cls.ber_user.company, home_status.home)
        create_or_update_spanning_relationships(cls.builder.company, home_status.home)
        create_or_update_spanning_relationships(cls.ea_user.company, home_status.home)
        create_or_update_spanning_relationships(cls.electricity_provider, home_status.home)
        create_or_update_spanning_relationships(cls.gas_provider, home_status.home)
        create_or_update_spanning_relationships(cls.hvac.company, home_status.home)

        home_status = EEPProgramHomeStatus.objects.get(eep_program__slug="neea-bpa-v3")
        home_rels = list(
            home_status.home.relationships.all().values_list("company__slug", flat=True)
        )
        assert cls.qa.slug not in home_rels
        assert cls.cr_qa.slug not in home_rels

        project_start = AnnotationType.objects.get(slug="project-start-nr")
        Annotation.objects.create(
            type=project_start,
            content="7-1-2021",
            content_type=ContentType.objects.get_for_model(home_status),
            object_id=home_status.id,
        )

        expected = {
            "neea-heating_system_config": NEEA_HEATING_SYSTEM_CONFIGS[1],
            "neea-heating_source": "Zonal Electric",
            "neea-water_heater_tier": ELECTRIC_RESISTANCE,
            "neea_refrigerators_installed": NONE_LABEL,
            "estar_dishwasher_installed": "No",
            "neea_clothes_washer_installed": NONE_LABEL,
            "neea-clothes_dryer_tier": DRYER_TIER_2_LABEL,
            "smart_thermostat_installed": "Yes",
            "neea-major-load-equipment": "No",
            "bpa_upload_docs": "No",
            "hvac-combo": "XXX",
            "hvac-cooling-combo": "XXX",
            "water-heater-combo": "XXX",
            "ventilation-combo": "XXX",
            "range-oven-combo": "XXX",
            "solar-combo": "XXX",
            "house-fans-combo": "XXX",
            "hrv-combo": "XXX",
            "smart-thermostat-combo": "XXX",
            "clothes-dryer-combo": "XXX",
            "other-combo": "XXX",
            "neea-electric_meter_number": "XXX",
            "neea-gas_meter_number": "XXX",
            "neea-program_redirected": "No",
            "neea-hvac-distributor": "No",
        }

        for measure, data in expected.items():
            CollectedInputMixin().add_collected_input(home_status, measure, data)

        # Note the is commented b/c the Yes on smart thermostat will trigger smart-tstat-combo
        unanswered = list(home_status.get_unanswered_questions().values_list("measure", flat=True))
        assert len(unanswered) == 0, f"Missing questions: {','.join(unanswered)}"

        missing_checks = home_status.report_eligibility_for_certification()
        if missing_checks:
            msg = "** Warning! Failing NEEA BPA V3 Certification Eligibility Requirements:\n  - "
            print(msg + "\n  - ".join(missing_checks) + "\n** End Warning\n")
