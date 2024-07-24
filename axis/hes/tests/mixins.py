import logging

from axis.annotation.models import Type as AnnotationType
from axis.annotation.tests.test_mixins import AnnotationMixin
from axis.checklist.collection.test_mixins import CollectionRequestMixin
from axis.company.models import Company
from axis.customer_eto.tests.program_checks.test_eto_2020 import ETO2020ProgramTestMixin
from axis.eep_program.models import EEPProgram
from axis.hes.tests.factories import HESCredentialFactory
from axis.hes.apps import HESConfig
from axis.home.models import EEPProgramHomeStatus
from axis.qa.models import QARequirement
from axis.remrate_data.tests.factories import simulation_factory as rem_simulation_factory
from simulation.models import Simulation

__author__ = "Steven K"
__date__ = "11/22/2019 12:27"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class HESTestMixin(ETO2020ProgramTestMixin):
    home_status: EEPProgramHomeStatus
    sim: Simulation

    @classmethod
    def setUpTestData(cls):
        super(HESTestMixin, cls).setUpTestData()

        cls.sim = cls.home_status.floorplan.simulation

        HESCredentialFactory(
            user=cls.home_status.company.users.filter(is_company_admin=True).first()
        )
        peci_admin = Company.objects.get(slug="peci").users.get(is_company_admin=True)
        HESCredentialFactory(user=peci_admin)

        rem_simulation_factory(company__name="unrelated__rater")
        EEPProgram.objects.filter(slug="eto-2020").update(
            require_model_file=False,
            program_close_date=None,
            program_submit_date=None,
            program_end_date=None,
        )

        QARequirement.objects.filter(eep_program__slug="eto-2020").delete()

        AnnotationType.objects.get(slug="hpxml_gbr_id")
        AnnotationType.objects.get(slug=HESConfig.ORIENTATION_ANNOTATION_SLUG)
        annotation_mixin = AnnotationMixin()
        annotation_mixin.add_annotation(
            content="1234567", type_slug="hpxml_gbr_id", content_object=cls.home_status
        )
        annotation_mixin.add_annotation(
            content="north",
            type_slug=HESConfig.ORIENTATION_ANNOTATION_SLUG,
            content_object=cls.home_status,
        )

        answer_data = {
            "primary-heating-equipment-type": {"input": "Gas Furnace", "comment": "Something."},
            "is-adu": {"input": "No"},
            "builder-payment-redirected": {"input": "No"},
            "eto-additional-incentives": {"input": "No"},
            "smart-thermostat-brand": {"input": "N/A"},
            "has-gas-fireplace": {"input": "No fireplace"},
            "has-battery-storage": {"input": "No"},
            "ceiling-r-value": {"input": "20"},
            "equipment-furnace": {"input": "FOOAR"},
            "equipment-water-heater": {"input": "FOOBAR"},
            "equipment-gas-tank-water-heater-serial-number": {"input": "FOOBAR"},
            "equipment-ventilation-balanced": {"input": "No"},
            "equipment-refrigerator": {"input": "FOOBAR"},
            "equipment-dishwasher": {"input": "FOOBAR"},
            "equipment-heating-other-type": {"input": "FOOBAR"},
            "equipment-heating-other-brand": {"input": "FOOBAR"},
            "equipment-heating-other-model-number": {"input": "FOOBAR"},
            "equipment-heat-pump-water-heater-serial-number": {"input": "FOOBAR"},
        }
        collection_mixin = CollectionRequestMixin()
        for measure, answer in answer_data.items():
            collection_mixin.add_collected_input(
                measure_id=measure, value=answer, home_status=cls.home_status
            )

        missing_checks = [x for x in cls.home_status.report_eligibility_for_certification() if x]
        if missing_checks:
            print(
                "** Warning! Failing ETO-2020 Certification Eligibility Requirements:\n  - "
                + "\n  - ".join(missing_checks)
                + "\n** End Warning\n"
            )
