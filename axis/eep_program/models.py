"""models.py: Django eep_program"""

import datetime
import inspect
import logging
import re
from builtins import tuple
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from simple_history.models import HistoricalRecords
from simulation.enumerations import FuelType, SourceType

from axis.certification.utils import (
    PassingStatusTuple,
    FailingStatusTuple,
    WarningStatusTuple,
    requirement_test,
)
from axis.company.models import Company
from axis.core.fields import AxisJSONField
from axis.core.utils import slugify_uniquely, LONG_DASHES
from axis.customer_aps.strings import APS_PROGRAM_SLUGS
from axis.customer_eto.calculator.eps import ETO_GEN2
from ..customer_eto.calculator.eps.base import EPSInputException
from axis.customer_eto.calculator.eps.utils import QUESTION_SLUG_DATA
from axis.customer_eto.strings import (
    ETO_2019_CHECKSUMS,
    ETO_PROGRAM_SLUGS,
    ETO_2020_CHECKSUMS,
    ETO_2021_CHECKSUMS,
    ETO_FIRE_2021_CHECKSUMS,
    ETO_2023_CHECKSUMS,
)
from axis.customer_neea.strings import NEEA_BPA_2019_CHECKSUMS, NEEA_BPA_2021_CHECKSUMS
from axis.customer_neea.utils import NEEA_PROGRAM_SLUGS, NEEA_BPA_SLUGS
from axis.home import strings as home_strings
from axis.user_management.models import Accreditation
from . import strings
from .managers import EEPProgramQuerySet

__author__ = "Steven Klass"
__date__ = "3/2/12 11:27 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from ..customer_eto.enumerations import PrimaryHeatingEquipment2020, YesNo

from ..customer_neea.rtf_calculator.constants.neea_v3 import (
    REFRIGERATOR_BOTTOM_FREEZER_LABEL,
    REFRIGERATOR_SIDE_FREEZER_LABEL,
    REFRIGERATOR_OTHER_FREEZER_LABEL,
    CLOTHES_WASHER_TOP_LABEL,
    CLOTHES_WASHER_SIDE_LABEL,
)

log = logging.getLogger(__name__)


class EEPProgram(models.Model):
    """This is used to identify Programs and the target hers scores for each Program."""

    name = models.CharField(max_length=64)
    is_qa_program = models.BooleanField(default=False)

    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE, blank=True, null=True)
    opt_in = models.BooleanField(default=False)
    opt_in_out_list = models.ManyToManyField(
        "company.Company", related_name="eep_programs_opted_in_out_of", blank=True
    )

    workflow = models.ForeignKey(
        "certification.Workflow", blank=True, null=True, on_delete=models.SET_NULL
    )
    workflow_default_settings = AxisJSONField(default=dict)

    certifiable_by = models.ManyToManyField(
        "company.Company", related_name="eep_programs_can_certify", blank=True
    )
    viewable_by_company_type = models.CharField(max_length=70, null=True, blank=True)

    # TODO DEPRECATE THESE THREE FIELDS - They are super misleading.
    min_hers_score = models.IntegerField("Min HERs Score", default=0)
    max_hers_score = models.IntegerField("Max HERs Score", default=100)
    per_point_adder = models.DecimalField(
        "Per/Point Adder", max_digits=10, decimal_places=2, default=0.0
    )

    builder_incentive_dollar_value = models.DecimalField(
        "Builder Incentive", max_digits=10, decimal_places=2, default=0.0
    )
    rater_incentive_dollar_value = models.DecimalField(
        "Rater Incentive", max_digits=10, decimal_places=2, default=0.0
    )

    collection_request = models.OneToOneField(
        "django_input_collection.CollectionRequest",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    required_checklists = models.ManyToManyField("checklist.CheckList", blank=True)
    enable_standard_disclosure = models.BooleanField(default=False)
    require_floorplan_approval = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    require_input_data = models.BooleanField(
        "Require simulation data (Rem SQL OR Eko)", default=True
    )
    require_rem_data = models.BooleanField("Require REM/Rate™ SQL Data (Exclusive)", default=False)
    require_model_file = models.BooleanField("Require REM/Rate™ Model BLG File", default=False)
    require_ekotrope_data = models.BooleanField("Require Ekotrope Data (Exclusive)", default=False)

    # DEPRECATED
    allow_rem_input = models.BooleanField("DEPRECATED Enable REM/Rate™ attachments", default=True)
    allow_ekotrope_input = models.BooleanField(
        "DEPRECATED Enable Ekotrope attachments", default=False
    )

    manual_transition_on_certify = models.BooleanField(
        "Manually transition to certified state", default=False
    )  # Click to Certify

    require_rater_of_record = models.BooleanField(default=False)
    require_energy_modeler = models.BooleanField(default=False)
    require_field_inspector = models.BooleanField(default=False)

    require_builder_relationship = models.BooleanField(default=True)
    require_builder_assigned_to_home = models.BooleanField(default=True)
    require_hvac_relationship = models.BooleanField(default=False)
    require_hvac_assigned_to_home = models.BooleanField(default=False)
    require_utility_relationship = models.BooleanField(default=False)
    require_utility_assigned_to_home = models.BooleanField(default=False)

    require_architect_relationship = models.BooleanField(default=False)
    require_architect_assigned_to_home = models.BooleanField(default=False)
    require_developer_relationship = models.BooleanField(default=False)
    require_developer_assigned_to_home = models.BooleanField(default=False)
    require_communityowner_relationship = models.BooleanField(default=False)
    require_communityowner_assigned_to_home = models.BooleanField(default=False)

    require_rater_relationship = models.BooleanField(default=False)
    require_rater_assigned_to_home = models.BooleanField(default=False)
    require_provider_relationship = models.BooleanField(default=False)
    require_provider_assigned_to_home = models.BooleanField(default=False)
    require_qa_relationship = models.BooleanField(default=False)
    require_qa_assigned_to_home = models.BooleanField(default=False)

    allow_sampling = models.BooleanField("Allow RESNET Sampling", default=True)
    allow_metro_sampling = models.BooleanField("Allow RESNET Metro Sampling", default=True)
    require_resnet_sampling_provider = models.BooleanField(
        "Require RESNET Sampling Provider", default=False
    )

    is_legacy = models.BooleanField(default=False)  # Flags old data for special handling
    is_public = models.BooleanField(default=False)

    program_visibility_date = models.DateField(
        "Visibility date",
        default=datetime.date.today,
        help_text="Date program is available for use on a home.",
    )
    program_start_date = models.DateField(
        "Start date",
        default=datetime.date.today,
        help_text="First date a program can be submitted for certification.",
    )
    program_close_date = models.DateField(
        "Close date",
        blank=True,
        null=True,
        help_text="Last day program can be added to home.",
    )
    program_submit_date = models.DateField(
        "Submission date",
        blank=True,
        null=True,
        help_text="Last day the home can be submitted for certification.",
    )
    program_end_date = models.DateField(
        "End date",
        blank=True,
        null=True,
        help_text="Last day program can be certified.",
    )

    program_close_warning_date = models.DateField("Close warning date", blank=True, null=True)
    program_close_warning = models.TextField(blank=True, null=True)

    program_submit_warning_date = models.DateField("Submit warning date", blank=True, null=True)
    program_submit_warning = models.TextField(blank=True, null=True)

    required_annotation_types = models.ManyToManyField("annotation.Type", blank=True)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    is_multi_family = models.BooleanField(
        default=False,
        help_text="Indicates that this program " "is using for Multi Family homes",
    )

    metrics = models.ManyToManyField("analytics.Metric", related_name="programs")

    # customer HIRL
    customer_hirl_certification_fee = models.DecimalField(
        default=0.00,
        max_digits=9,
        decimal_places=2,
        verbose_name="Base Certification Fee",
        help_text="Certification Fee that is adding "
        "to Invoice Item Group when CUSTOMER HIRL creating Project. "
        "ATTENTION: This is a base value that "
        "affects on ALL certification fees for this program. "
        "Fees calculation performs in method `calculate_certification_fees_cost()`",
    )

    customer_hirl_per_unit_fee = models.DecimalField(
        default=0.00,
        max_digits=9,
        decimal_places=2,
        verbose_name="Base Per Unit Fee",
        help_text="Per Unit Fee that is adding "
        "to Invoice Item Group when CUSTOMER HIRL creating Project. "
        "ATTENTION: This is a base value that affects on ALL unit fees for this program.",
    )

    objects = EEPProgramQuerySet.as_manager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Program"
        unique_together = (("name", "owner"),)
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """If we didn't get a slug give it now."""
        if not self.slug:
            self.slug = slugify_uniquely(self.name, self.__class__)

        # All forms want to set this value as a blank string, which breaks out filtering in many places
        if self.viewable_by_company_type is not None and len(self.viewable_by_company_type) == 0:
            self.viewable_by_company_type = None

        super(EEPProgram, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("eep_program:view", kwargs={"pk": self.pk})

    def natural_key(self):
        return (self.name, self.owner.slug)

    def get_checklist_question_set(self):
        """Return the set of questions in the checklist"""
        from axis.checklist.models import Question

        return Question.objects.filter_by_eep(self).prefetch_related("question_choice")

    def requires_floorplan(self):
        """Indicates that this EEPProgram will require Floorplan data."""
        return (
            self.require_input_data
            or self.require_rem_data
            or self.require_model_file
            or self.require_ekotrope_data
        )

    def is_claimable(self, user):
        claimable = False
        if user.company.is_eep_sponsor:
            claimable = True
        else:
            claimable_companies = Company.objects.unclaimed_companies(
                company=user.company, include_self=True
            )
            if self.owner == user.company and user.company in claimable_companies.all():
                claimable = True
        return claimable

    def is_hers_based_program(self):
        sims_requried = (
            self.require_input_data or self.require_rem_data or self.require_ekotrope_data
        )
        changed_hers = self.max_hers_score != 100 or self.min_hers_score != 0
        return changed_hers and sims_requried

    def requires_manual_floorplan_approval(self, company=None, user=None):
        """
        Returns a boolean indicating that the given ``company`` must have floorplans activated by
        the program owner.  If no such action is required, ``False`` is returned.
        """

        # --------------------
        # This was the code that used this method to correctly set the approval flag:
        #
        # subdivision = homestatus.home.subdivision
        # eep_program = homestatus.eep_program
        # manual_approval = eep_program.requires_manual_floorplan_approval(self.request.company)
        # floorplan.floorplanapproval_set.get_or_create(
        #     subdivision=self.homestatus.home.subdivision,
        #     defaults={
        #         'is_approved': (not manual_approval),
        #         'approved_by': None,
        #     })
        # --------------------

        assert any([company, user]), "Must provide one of: company, user"

        if not self.require_floorplan_approval:
            return False

        if user:
            # Since we already know the approval-required flag is True, a superuser might not have
            # any owned relationships and should be put through directly.
            if user.is_superuser:
                return True

            company = user.company

        from axis.relationship.models import Relationship

        direct_relation_to_owner = Relationship.objects.get_reversed_companies(company).filter(
            id=self.owner_id
        )

        # Return True if ``company`` and the program owner are directly related, implying that
        # the owner intends to gate the approval floorplans added by ``company``.
        return direct_relation_to_owner.exists()

    @classmethod
    def can_be_added(self, user):
        if user.company.is_eep_sponsor or user.is_superuser or user.company.company_type == "eep":
            return True
        if user.company.company_type in ["rater", "provider", "hvac"]:
            if user.is_company_admin and user.company.is_customer:
                return True
        return False

    def can_be_edited(self, user):
        from axis.subdivision.models import Subdivision
        from axis.home.models import EEPProgramHomeStatus

        if user.is_superuser:
            return True

        if (
            not Subdivision.objects.filter(eep_programs=self).count()
            and not EEPProgramHomeStatus.objects.filter(eep_program=self).count()
            and self.is_claimable(user)
        ):
            return True

    def can_be_deleted(self, user):
        return self.can_be_edited(user)

    def user_can_certify(self, user):
        if self.certifiable_by.count() == 0:
            if user.company.company_type == "provider":
                return True
            return False  # Utilities and possible others should not automatically be allowed
            # certification rights.

        return self.certifiable_by.filter(id=user.company.id).exists()

    def hirl_program_have_accreditation_for_user(self, user):
        """
        Check whether CUSTOMER HIRL Users have accreditation for current Program
        :param user: User object
        :return: Boolean
        """
        accreditation_program_requirements = {
            "ngbs-sf-new-construction-2020-new": Q(name=Accreditation.NGBS_2020_NAME),
            "ngbs-mf-new-construction-2020-new": Q(name=Accreditation.NGBS_2020_NAME),
            "ngbs-sf-whole-house-remodel-2020-new": Q(name=Accreditation.NGBS_2020_NAME),
            "ngbs-mf-whole-house-remodel-2020-new": Q(name=Accreditation.NGBS_2020_NAME),
            "ngbs-sf-certified-2020-new": Q(name=Accreditation.NGBS_2020_NAME),
            "ngbs-sf-new-construction-2015-new": Q(name=Accreditation.NGBS_2015_NAME),
            "ngbs-mf-new-construction-2015-new": Q(name=Accreditation.NGBS_2015_NAME),
            "ngbs-sf-whole-house-remodel-2015-new": Q(name=Accreditation.NGBS_2015_NAME),
            "ngbs-mf-whole-house-remodel-2015-new": Q(name=Accreditation.NGBS_2015_NAME),
            "ngbs-sf-new-construction-2012-new": Q(name=Accreditation.NGBS_2012_NAME),
            "ngbs-mf-new-construction-2012-new": Q(name=Accreditation.NGBS_2012_NAME),
            "ngbs-sf-whole-house-remodel-2012-new": Q(name=Accreditation.NGBS_2012_NAME),
            "ngbs-mf-whole-house-remodel-2012-new": Q(name=Accreditation.NGBS_2012_NAME),
            "ngbs-sf-wri-2021": Q(name=Accreditation.NGBS_WRI_VERIFIER_NAME),
            "ngbs-mf-wri-2021": Q(name=Accreditation.NGBS_WRI_VERIFIER_NAME),
            "ngbs-land-development-2020-new": Q(name=Accreditation.NGBS_2020_NAME),
        }

        accreditation_exists = (
            user.accreditations.filter(accreditation_program_requirements[self.slug])
            .exclude(state=Accreditation.INACTIVE_STATE)
            .exists()
        )
        return accreditation_exists

    def get_rater_program(self):
        if not self.is_qa_program:
            return self
        slug = re.sub(r"-qa$", "", self.slug)
        return EEPProgram.objects.filter(slug="{slug}".format(slug=slug)).first()

    def get_qa_program(self):
        if self.is_qa_program:
            return self
        return EEPProgram.objects.filter(slug="{self.slug}-qa".format(self=self)).first()

    def alter_certification_requirements(self, requirement_tests, references=None):
        """
        Hook for adding/removing tests from the certification chain, based on the program.  Tests
        should be callbacks to methods named after the pattern "get_FOO_status()".

        Test callbacks should accept ``**kwargs`` so that pre-crunched data can be sent to the
        method.  Check the homestatus "get_certification_test_kwargs()" method for the set of
        kwargs.
        """

        requirement_tests.extend(
            [
                self.get_program_certification_eligibility,
                self.get_std_protocol_percent_improvement_status,
                self.get_resnet_approved_provider_status,
                self.get_aps_double_payment_status,
                self.get_aps_calculator_status,
                self.get_eps_calculator_status,
                self.get_eto_builder_account_number_status,
                self.get_eto_rater_account_number_status,
                self.get_eto_2017_answer_sets,
                self.get_eto_legacy_builder_incentive_status,
                self.get_neea_utilities_satisfied_status,
                self.get_neea_invalid_program_status,
                self.get_hquito_accrediation_status,
                self.get_nwesh_invalid_qa_program_status,
                self.get_generic_singlefamily_support,
                self.get_generic_us_state_eligibility,
                self.get_min_max_simulation_version,
                self.get_simulation_udrh_check,
                self.get_simulation_flavor_status,
                self.get_remrate_flavor_status,
                self.get_remrate_version_status,
                self.get_built_green_annotations_status,
                self.get_pnw_utility_required_status,
                self.get_water_heater_status,
                self.get_duct_system_test_status,
                self.get_ventilation_type_status,
                self.get_neea_checklist_type_matches_remrate_status,
                self.get_neea_checklist_water_heater_matches_remrate_status,
                self.get_neea_bpa_refrigerator_installed_status,
                self.get_neea_bpa_clothes_washer_installed_status,
                self.get_neea_bpa_clothes_dryer_installed_status,
                self.get_neea_bpa_dishwasher_installed_status,
                self.get_neea_bpa_checklist_smart_thermostat_installed_status,
                self.get_neea_bpa_remrate_version_status,
                self.get_program_end_warning_status,
                self.get_eto_no_multifamily,
                self.get_eto_2018_oven_fuel_type,
                self.get_eto_2018_dryer_attributes,
                self.get_eto_heat_pump_water_heater_status,
                self.get_eto_percent_improvement_oregon,
                self.get_eto_percent_improvement_washington,
                self.get_eto_primary_heating_fuel_type,
                self.get_eto_min_program_version,
                self.get_remrate_udhr_check,
                self.get_eto_2019_approved_utility_electric_utility,
                self.get_eto_2019_approved_utility_gas_utility,
                self.get_aps_2019_estar_check,
                self.get_built_green_wa_electric_utility_required_status,
                self.get_built_green_wa_gas_utility_required_status,
                self.get_wa_code_annotation_dwelling_status,
                self.get_wa_code_opt_1_status,
                self.get_wa_code_opt_2_status,
                self.get_wa_code_opt_3_status,
                self.get_wa_code_opt_4_status,
                self.get_wa_code_opt_5a_status,
                self.get_wa_code_opt_5bc_status,
                self.get_wa_code_opt_5d_status,
                self.get_wa_code_opt_6_status,
                self.get_wa_code_bathroom_status,
                self.get_wa_code_warning_status,
                self.get_wa_code_damper_status,
                self.get_eto_approved_utility_gas_utility,
                self.get_eto_approved_utility_electric_utility,
                self.get_eto_gas_heated_utility_check,
                self.get_eto_electric_heated_utility_check,
                self.get_eto_revised_primary_heating_fuel_type,
                self.get_neea_v3_availability_check,
                self.get_neea_v3_refrigerator_installed_status,
                self.get_neea_v3_clothes_washer_installed_status,
                self.get_wcc_builder_incentive_status,
                self.get_eto_builder_incentive_status,
                self.get_eto_fire_rebuild_checks,
            ]
        )

        if references is None:
            return requirement_tests

        requirement_tests_final = []
        for test in requirement_tests:
            required_args = inspect.getfullargspec(test).args
            if set(required_args).intersection(set(references)):
                requirement_tests_final.append(test)

        return requirement_tests_final

    def validate_references(self):
        for home_status in self.homestatuses.all():
            home_status.validate_references()

    def get_program_certification_eligibility(self, home_status, edit_url, **kwargs):
        # If no testing is required by the program, hide this test status from the results
        if home_status.certification_date:
            return None

        today = kwargs.get("today") or datetime.date.today()
        end_date = self.program_end_date if self.program_end_date else today
        if self.program_start_date <= today <= end_date:
            return None

        if self.program_start_date > today:
            msg = home_strings.PROGRAM_TOO_EARLY.format(
                program=self,
                date=formats.date_format(self.program_start_date, "SHORT_DATE_FORMAT"),
            )
        elif self.program_end_date < today:
            msg = home_strings.PROGRAM_TOO_LATE.format(
                program=self,
                date=formats.date_format(self.program_end_date, "SHORT_DATE_FORMAT"),
            )
        return FailingStatusTuple(data=None, message=msg, url=edit_url)

    # Certification status tests specific to the program
    @requirement_test("Verify Standard Protocol % Improvement", eep_program=NEEA_BPA_SLUGS)
    def get_std_protocol_percent_improvement_status(self, home_status, edit_url, **kwargs):
        """Blocks certification if the Percent Improvement is < 10%"""
        calculations = home_status.standardprotocolcalculator_set.first()

        if not calculations:
            return None

        if calculations.revised_percent_improvement < 0.10:
            return FailingStatusTuple(
                data=calculations.revised_percent_improvement,
                message=home_strings.PERCENT_IMPROVEMENT_TOO_LOW,
                url=edit_url,
            )
        return PassingStatusTuple(data=calculations.revised_percent_improvement)

    def get_resnet_approved_provider_status(self, home_status, edit_url, **kwargs):
        """Returns a good status if the provider is resnet sampling approved"""

        # If no testing is required by the program, hide this test status from the results
        if home_status.get_sampleset() is None or self.require_resnet_sampling_provider is False:
            return None

        providers = home_status.get_providers()
        provider_ids = list(set(p.id for p in providers))  # providers may be a list, not queryset

        unapproved_providers = Company.objects.filter(
            Q(resnet__isnull=True) | Q(resnet__is_sampling_provider=False),
            id__in=[x.id for x in providers],
            company_type=Company.PROVIDER_COMPANY_TYPE,
        )
        unapproved_provider_ids = list(set(unapproved_providers.values_list("id", flat=True)))

        # At least a provider is approved - We aren't sure which it is yet.
        if len(provider_ids) > len(unapproved_provider_ids):
            return PassingStatusTuple(data=None)

        href = '<a href="{url}" target="_blank">{name}</a>'
        unnaproved_provider_strings = []
        for i in unapproved_providers:
            unnaproved_provider_strings.append(
                href.format(url=i.get_absolute_url(), name="{}".format(i))
            )

        msg = home_strings.UNAPPROVED_RESNET_PROVIDERS.format(
            program=home_status.eep_program,
            providers=", ".join(unnaproved_provider_strings),
        )
        return FailingStatusTuple(data=None, message=mark_safe(msg), url=edit_url)

    @requirement_test("Verify EPS Calculator", eep_program=["eto-2017", "eto-2018"])
    def get_eps_calculator_status(
        self,
        home_status,
        checklist_url,
        edit_url,
        companies_edit_url,
        input_values,
        **kwargs,
    ):
        """Returns a good status if the required questions are answered for the calculator."""

        if self.collection_request:
            return

        # Allow separate utility requirement to report an issue
        has_electric = home_status.get_electric_company()
        has_gas = home_status.get_gas_company()
        if not (has_gas or has_electric):
            return None

        # Allow separate REM/Rate requirement to report an issue
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        if home_status.floorplan.remrate_target.export_type != 4:
            msg = home_strings.ETO_BAD_REMRATE_TYPE
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

        missing, err = [], None

        ANS_SLUGS = QUESTION_SLUG_DATA.get(home_status.eep_program.slug, {})
        if not input_values.get(ANS_SLUGS.get("ETO_HEAT_TYPE_QUESTION_SLUG")):
            missing.append("Primary Heating Equipment")

        if home_status.eep_program.slug not in ETO_GEN2:
            if not input_values.get(ANS_SLUGS.get("ETO_WATER_HEATER_EF_QUESTION_SLUG")):
                missing.append("Primary Water Heater EF")
            if not input_values.get(ANS_SLUGS.get("ETO_WATER_HEATER_TYPE_SLUG")):
                missing.append("Water Heater Type")
            if not input_values.get(ANS_SLUGS.get("ETO_PATHWAY_QUESTION_SLUG")):
                missing.append("Pathway")

        if len(missing) or err:
            missing = ", ".join(missing)
            other_error = " {}.".format(err) if err else ""
            msg = home_strings.MISSING_ETO_CALCULATION_REQUIREMENTS.format(
                missing=missing, other_errors=other_error
            )
            if not len(missing) and err:
                msg = err
            return FailingStatusTuple(data=None, message=msg, url=checklist_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify ETO 2017 Answers", eep_program="eto-2017")
    def get_eto_2017_answer_sets(self, home_status, checklist_url, input_values, **kwargs):
        missing = []

        def measure_values(measures):
            return {
                measure: input_values.get(measure)
                for measure in measures
                if measure in input_values
            }

        if not measure_values(
            [
                "eto-slab_perimeter_r_value",
                "eto-slab_under_insulation_r_value",
                "eto-framed_floor_r_value",
            ]
        ):
            missing.append("Floor or Slab Insulation R values")

        if not measure_values(
            ["eto-flat_ceiling_r_value-2017", "eto-vaulted_ceiling_r_value-2017"]
        ):
            missing.append("Vaulted or Flat ceiling Insulation R values")

        if not measure_values(
            [
                "eto-primary_heat_afue",
                "eto-primary_heat_hspf-2016",
                "eto-primary_heat_cop-2016",
            ]
        ):
            missing.append("Heating AFUE, HSPF or COP values")

        if len(missing):
            return FailingStatusTuple(data=None, message="; ".join(missing), url=checklist_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify APS double payments", eep_program=APS_PROGRAM_SLUGS)
    def get_aps_double_payment_status(self, home_status, **kwargs):
        """Checks to make sure that double paymens won't occur"""
        # Only applicable to the APS program
        if home_status.state == "abandoned":
            return None
        from axis.home.models import EEPProgramHomeStatus

        stats = EEPProgramHomeStatus.objects.filter(
            home=home_status.home, eep_program__owner=home_status.eep_program.owner
        ).exclude(id=home_status.id)
        stats = stats.exclude(state="abandoned")
        if stats.count():
            msg = home_strings.DUPLICATE_APS_PROGRAMS.format(
                program=stats[0].eep_program.name,
                new_program=home_status.eep_program.name,
            )
            return FailingStatusTuple(data=None, message=msg, url=None)
        try:
            if home_status.home.apshome and home_status.home.apshome.legacyapshome_set.count():
                msg = home_strings.LEGACY_APS_HOME.format(new_program=home_status.eep_program.name)
                return FailingStatusTuple(data=None, message=msg, url=None)
        except ObjectDoesNotExist:
            pass
        return PassingStatusTuple(data=None)

    @requirement_test("Verify APS double payments", eep_program=APS_PROGRAM_SLUGS[4:])
    def get_aps_calculator_status(self, home_status, edit_url, **kwargs):
        """Checks to make sure the optimal EEP Program has been selected."""

        if home_status.state == "complete":
            return PassingStatusTuple(data=None)

        from axis.customer_aps.aps_calculator import APSInputException
        from axis.customer_aps.aps_calculator.calculator import APSCalculator

        try:
            calc = APSCalculator(home_status_id=home_status.id)
        except APSInputException as err:
            return FailingStatusTuple(data=None, message="{}".format(err), url=None)
        if calc.warnings:
            return WarningStatusTuple(message=", ".join(calc.warnings), data=None, url=None)
        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify ETO Builder Account", eep_program=ETO_PROGRAM_SLUGS + ["washington-code-credit"]
    )
    def get_eto_builder_account_number_status(self, home_status, companies_edit_url, **kwargs):
        """
        Returns a good status if the home's builder an as ETOAccount object.  Test is skipped if the
        program is not ETO.
        """

        from axis.customer_eto.models import ETOAccount

        builder = home_status.home.get_builder()
        if not builder:
            msg = home_strings.MISSING_BUILDER_BASIC
            return FailingStatusTuple(data=None, message=msg, url=companies_edit_url)

        url = reverse("company:view", kwargs={"type": builder.company_type, "pk": builder.pk})
        try:
            account_number = builder.eto_account.account_number
            if account_number in [None, ""]:
                raise ETOAccount.DoesNotExist
        except ETOAccount.DoesNotExist:
            msg = home_strings.MISSING_ETO_ACCOUNT_NUMBER.format(
                program=self, company=builder, company_type=builder.company_type
            )
            return FailingStatusTuple(data=None, message=msg, url=url)

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify ETO Rater Account", eep_program=ETO_PROGRAM_SLUGS + ["washington-code-credit"]
    )
    def get_eto_rater_account_number_status(self, home_status, **kwargs):
        """
        Returns a good status if the home's builder an as ETOAccount object.  Test is skipped if the
        program is not ETO.
        """

        from axis.customer_eto.models import ETOAccount

        rater = home_status.company

        url = reverse("company:view", kwargs={"type": rater.company_type, "pk": rater.pk})
        try:
            account_number = rater.eto_account.account_number
            if account_number in [None, ""]:
                raise ETOAccount.DoesNotExist
        except ETOAccount.DoesNotExist:
            msg = home_strings.MISSING_ETO_ACCOUNT_NUMBER.format(
                program=self, company=rater, company_type=rater.company_type
            )
            return FailingStatusTuple(data=None, message=msg, url=url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify NEEA Utilities", eep_program=NEEA_PROGRAM_SLUGS)
    def get_neea_utilities_satisfied_status(
        self,
        home_status,
        home_edit_url,
        companies_edit_url,
        annotations_edit_url,
        input_values,
        collector=None,
        **kwargs,
    ):
        """
        Returns a good status if the home's assigned utility companies validates against the pre-set
        list of okay conditions.
        """

        home = home_status.home

        gas_utility = home.get_gas_company()
        electric_utility = home.get_electric_company()

        if home_status.floorplan:
            rem_simulation = home_status.floorplan.remrate_target
        else:
            rem_simulation = None

        try:
            heat_source = home_status.annotations.get(type__slug="heat-source")
        except ObjectDoesNotExist:
            # This check was implemented as an annotation first
            # Then moved to a checklist questions.
            heat_source = input_values.get("neea-heating_source")
            if heat_source is None:
                # Still be unassigned, can't verify utility assignments.
                msg = home_strings.NEEA_HEAT_TYPE_NOT_PROVIDED
                return FailingStatusTuple(data=None, message=msg, url=annotations_edit_url)
            heat_source = LONG_DASHES.sub("-", heat_source)
        except MultipleObjectsReturned as e:
            # Make sure we can't go bellies up and 500
            log.error(str(e))
            # Remove all but the latest value we have for the annotation
            _duplicates = home_status.annotations.filter(type__slug="heat-source").order_by("-id")
            heat_source = _duplicates[0]
            _duplicates.exclude(id=heat_source.id).delete()
        else:
            heat_source = LONG_DASHES.sub("-", heat_source.content)

        # Possible values of the "Primary Heat Source" annotation, mapped to utility requirements.
        requirements_by_heat_source = {
            "Heat Pump": {
                "electric": True,
                "gas": False,
            },
            "Heat Pump - Geothermal": {
                "electric": True,
                "gas": False,
            },
            "Heat Pump - w/ Gas Backup": {
                "electric": True,
                "gas": True,
            },
            "Heat Pump - Mini Split": {
                "electric": True,
                "gas": False,
            },
            "Gas with AC": {
                "electric": True,
                "gas": True,
            },
            "Gas No AC": {
                "electric": True,
                "gas": True,
            },
            "Zonal Electric": {
                "electric": True,
                "gas": False,
            },
            "Propane, Oil, or Wood": {
                "electric": True,
                "gas": False,
            },
            "Heat Pump - Geothermal/Ground Source": {
                "electric": True,
                "gas": False,
            },
            "Hydronic Radiant Electric Boiler": {
                "electric": True,
                "gas": False,
            },
            "Hydronic Radiant Gas Boiler": {
                "electric": False,
                "gas": True,
            },
            "Hydronic Radiant Heat Pump": {
                "electric": True,
                "gas": False,
            },
        }

        if heat_source not in requirements_by_heat_source:
            return FailingStatusTuple(
                data=heat_source,
                message="Unknown heat source",
                url=annotations_edit_url,
            )

        requirements = requirements_by_heat_source[heat_source]
        if requirements["electric"] and requirements["gas"]:
            if not all({gas_utility, electric_utility}):
                msg = home_strings.NEEA_ELECTRIC_AND_GAS_UTILITIES_REQUIRED
                msg = msg.format(heat_source=heat_source)
                return FailingStatusTuple(data=heat_source, message=msg, url=companies_edit_url)

        elif requirements["electric"] and not electric_utility:
            msg = home_strings.NEEA_ELECTRIC_UTILITY_REQUIRED
            msg = msg.format(heat_source=heat_source)
            return FailingStatusTuple(data=heat_source, message=msg, url=companies_edit_url)

        elif requirements["gas"] and not gas_utility:
            msg = home_strings.NEEA_GAS_UTILITY_REQUIRED
            msg = msg.format(heat_source=heat_source)
            return FailingStatusTuple(data=heat_source, message=msg, url=companies_edit_url)

        # This will take verify our simulation data.
        if rem_simulation:
            dominant = rem_simulation.installedequipment_set.get_dominant_values(rem_simulation.id)
            heating = dominant[rem_simulation.id]["dominant_heating"]["fuel"]
            heating = heating.lower() if heating else ""
            hot_water = dominant[rem_simulation.id]["dominant_hot_water"]["fuel"]
            hot_water = hot_water.lower() if hot_water else ""
            gas_required = "gas" in heating or "gas" in hot_water
            if gas_required and not gas_utility:
                log.info("Hot Water: %s Heating: %s", hot_water, heating)
                msg = home_strings.NEEA_GAS_UTILITY_REQUIRED
                heat_source = []
                if "gas" in heating:
                    heat_source.append("Heating")
                if "gas" in hot_water:
                    heat_source.append("Hot Water")
                msg = msg.format(heat_source=", ".join(heat_source))
                return FailingStatusTuple(data=heat_source, message=msg, url=companies_edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify HQUITO Accreditation", eep_program=NEEA_PROGRAM_SLUGS)
    def get_hquito_accrediation_status(
        self, home_status, home_edit_url, companies_edit_url, **kwargs
    ):
        """
        Returns a good status if the home's HVAC Contractor is accredited or not.
        """

        if "2015" not in self.slug:
            return

        home = home_status.home
        hvac_company = home.get_hvac_company()

        if not hvac_company:
            # This should be captured under the fact that the HVAC is required.
            return

        try:
            status = hvac_company.hquito_accredited
            status_string = hvac_company.get_hquito_accredited_display()
        except (AttributeError, ObjectDoesNotExist):
            msg = home_strings.INVALID_HVAC_COMPANY.format(company=hvac_company)
            return FailingStatusTuple(data=None, message=msg, url=companies_edit_url)

        from axis.company.tasks import send_hquito_notification_message

        if status is None:
            msg = home_strings.FAILING_HQUITO_STATUS.format(
                company=hvac_company, program="{}".format(self)
            )
            url = hvac_company.get_absolute_url()
            send_hquito_notification_message.delay(hvac_company.id, status_string)
            return FailingStatusTuple(data=None, message=mark_safe(msg), url=url)

        elif status is False:
            msg = home_strings.FAILING_HQUITO_STATUS.format(
                company=hvac_company, program="{}".format(self)
            )
            send_hquito_notification_message.delay(hvac_company.id, status_string)
            return FailingStatusTuple(data=None, message=mark_safe(msg), url=companies_edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify Invalid Program",
        eep_program=["neea-energy-star-v3", "neea-energy-star-v3-performance"] + NEEA_BPA_SLUGS,
    )
    def get_neea_invalid_program_status(
        self, home_status, home_edit_url, companies_edit_url, **kwargs
    ):
        """
        Returns a good status if the home's HVAC Contractor is accredited or not.
        """

        # Prevent any already selected
        is_multi_family = home_status.home.is_multi_family
        if home_status.eep_program.slug == "neea-energy-star-v3":  # Prescriptive
            if home_status.state == "complete":
                return
            if (
                not is_multi_family
                and home_status.created_date
                > datetime.datetime(2015, 7, 1).replace(tzinfo=datetime.timezone.utc)
                and home_status.state != "complete"
            ):
                msg = home_strings.NEEA_INVALID_PROGRAM.format(program=self)
                return FailingStatusTuple(data=None, message=msg, url=home_edit_url)
            if not is_multi_family:
                msg = home_strings.PRESCRIPTIVE_REQUIRES_MULTIFAMILY
                return FailingStatusTuple(data=None, message=msg, url=home_edit_url)
        elif home_status.eep_program.slug == "neea-energy-star-v3-performance":  # Performance
            if is_multi_family:
                msg = home_strings.PERFORMANCE_REQUIRES_NON_MULTIFAMILY
                return FailingStatusTuple(data=None, message=msg, url=home_edit_url)
        elif home_status.eep_program.slug == "utility-incentive-v1-multifamily":
            if not is_multi_family:
                msg = home_strings.GENERIC_REQUIRES_MULTIFAMILY
                return FailingStatusTuple(data=None, message=msg, url=home_edit_url)
        elif home_status.eep_program.slug in NEEA_BPA_SLUGS:
            if is_multi_family:
                msg = home_strings.GENERIC_REQUIRES_SINGLEFAMILY
                return FailingStatusTuple(data=None, message=msg, url=home_edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify NWESH Invalid QA Program",
        eep_program=[
            "northwest-energy-star-version-3-2014-qa",
            "northwest-energy-star-version-3-2014-full-qa",
            "neea-energy-star-v3-qa",
            "northwest-energy-star-v3-r8-qa-short",
            "northwest-energy-star-v3-r8-qa-long",
        ],
    )
    def get_nwesh_invalid_qa_program_status(self, home_status, home_edit_url, **kwargs):
        legacy_qa = [
            "northwest-energy-star-version-3-2014-qa",
            "northwest-energy-star-version-3-2014-full-qa",
            "neea-energy-star-v3-qa",
        ]
        current_qa = [
            "northwest-energy-star-v3-r8-qa-short",
            "northwest-energy-star-v3-r8-qa-long",
        ]

        legacy_nwesh = ["neea-energy-star-v3", "neea-energy-star-v3-performance"]
        current_nwesh = ["neea-performance-2015", "neea-prescriptive-2015"]

        from axis.home.models import EEPProgramHomeStatus

        if self.slug in legacy_qa:
            stats = EEPProgramHomeStatus.objects.filter(
                eep_program__slug__in=legacy_nwesh, home=home_status.home
            )
            bad_stats = EEPProgramHomeStatus.objects.filter(
                eep_program__slug__in=current_nwesh, home=home_status.home
            )
            correct_programs = EEPProgram.objects.filter(slug__in=current_qa)
        else:
            stats = EEPProgramHomeStatus.objects.filter(
                eep_program__slug__in=current_nwesh, home=home_status.home
            )
            bad_stats = EEPProgramHomeStatus.objects.filter(
                eep_program__slug__in=legacy_nwesh, home=home_status.home
            )
            correct_programs = EEPProgram.objects.filter(slug__in=legacy_nwesh)

        # If we are using the wrong QA Program - Change the QA Program
        if not stats.count() and bad_stats.count():
            program = bad_stats.first().eep_program
            qa_programs = ",".join(["{}".format(x) for x in correct_programs])
            msg = home_strings.BAD_NWESH_QA_PROGRAM.format(qa_programs=qa_programs, program=program)
            return FailingStatusTuple(data=None, message=msg, url=home_edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify Single Family Suport",
        eep_program=["neea-efficient-homes", "washington-code-credit"],
    )
    def get_generic_singlefamily_support(
        self, home_status, home_edit_url, companies_edit_url, **kwargs
    ):
        """
        Returns a good status if the home is single family.
        """

        # Prevent any already selected
        is_multi_family = home_status.home.is_multi_family
        if is_multi_family:
            msg = home_strings.ONLY_SINGLE_FAMILY_ALLOWED.format(program=self)
            return FailingStatusTuple(data=None, message=msg, url=home_edit_url)
        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify State Eligibility",
        eep_program=["washington-code-credit", "eto-2022"],
    )
    def get_generic_us_state_eligibility(
        self, home_status, home_edit_url, companies_edit_url, **kwargs
    ):
        """
        Returns a good status if the home sits in the approved us states.
        """
        lookup = {"washington-code-credit": ["WA"], "eto-2022": ["OR", "ID", "WA"]}

        # Prevent any already selected
        valid_states = lookup[home_status.eep_program.slug]
        if home_status.home.state not in valid_states:
            msg = (
                f"Program {home_status.eep_program!r} is only allowed in {', '.join(valid_states)}."
            )
            return FailingStatusTuple(data=None, message=msg, url=home_edit_url)
        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify REMRate Flavor",
        eep_program=[
            "utility-incentive-v1-single-family",
            "eto-2016",
            "eto-2017",
            "neea-bpa",
        ],
    )
    def get_remrate_flavor_status(self, home_status, edit_url, companies_edit_url, **kwargs):
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        northwest_only_programs = [
            "utility-incentive-v1-single-family",
            "eto-2016",
            "eto-2017",
        ]
        if self.slug in northwest_only_programs:
            if home_status.floorplan.remrate_target.flavor.strip() not in [
                "Northwest",
                "Washington",
            ]:
                msg = home_strings.NWESH_NEW_HOMES_PROGRAM_REM_FLAVOR_REQUIREMENT.format(
                    program="{}".format(home_status.eep_program),
                    accepted_flavor="Northwest",
                )
                return FailingStatusTuple(data=None, message=msg, url=edit_url)

        # Bob foresees adding a flavor validation to some national programs as well.
        national_only_programs = NEEA_BPA_SLUGS
        if self.slug in national_only_programs:
            if home_status.floorplan.remrate_target.flavor.strip() not in [
                "",
                "None",
                "Rate",
            ]:
                msg = home_strings.NWESH_NEW_HOMES_PROGRAM_REM_FLAVOR_REQUIREMENT.format(
                    program="{}".format(home_status.eep_program),
                    accepted_flavor="National",
                )
                return FailingStatusTuple(data=None, message=msg, url=edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify Simulation Flavor", eep_program=["neea-bpa-v3"])
    def get_simulation_flavor_status(self, home_status, edit_url, **_kwargs):
        """Verify the simulation flavors exists"""

        eep_program_choices = {
            "neea-bpa-v3": ["Rate"],
        }

        if not home_status.floorplan or not home_status.floorplan.simulation:
            return None

        simulation = home_status.floorplan.simulation
        if simulation.source_type != SourceType.REMRATE_SQL:
            return

        valid_flavors = eep_program_choices.get(home_status.eep_program.slug)
        map_data = {"Rate": "National"}
        if simulation.flavor not in valid_flavors:
            msg = (
                f"Program {self} only allows rating data from the following flavors or "
                f"RemRate: {', '.join([map_data.get(x, x) for x in valid_flavors])}"
            )
            return FailingStatusTuple(data=None, message=msg, url=edit_url)
        return PassingStatusTuple(data=None)

    @requirement_test("Verify REM/Rate version", eep_program="utility-incentive-v1-single-family")
    def get_remrate_version_status(self, home_status, edit_url, companies_edit_url, **kwargs):
        applicable_programs = ["utility-incentive-v1-single-family"]

        if self.slug not in applicable_programs:
            return None

        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        version = home_status.floorplan.remrate_target.numerical_version
        program = "{}".format(home_status.eep_program)
        # This program allows versions 14.0 - 14.6.4
        # That includes all current version of REM - v14
        if self.slug == "utility-incentive-v1-single-family":
            if version.major != 14 or version.minor not in range(7):
                msg = home_strings.NWESH_NEW_HOMES_PROGRAM_REM_VERSION_REQUIREMENT.format(
                    program=program, versions="14.6 - 14.6.4"
                )
                return FailingStatusTuple(data=None, message=msg, url=edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify REM/Rate version", eep_program=["neea-bpa"])
    def get_neea_bpa_remrate_version_status(self, home_status, edit_url, **kwargs):
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        start_transition_date = kwargs.get("start_transition_date", datetime.date(2019, 3, 1))
        end_transition_date = kwargs.get("end_transition_date", datetime.date(2019, 10, 1))

        version = home_status.floorplan.remrate_target.numerical_version
        program = "{}".format((home_status.eep_program))

        passing_version = version == (15, 7, 1)
        versions = "15.7.1"
        if datetime.date.today() < start_transition_date:
            passing_version = version == (15, 3, 0)
            versions = "15.3"
        elif start_transition_date < datetime.date.today() < end_transition_date:
            passing_version = version == (15, 7, 1) or version == (15, 3, 0)
            versions = "15.3 or 15.7.1"

        # Only check this if we are in pre-certification_pending state.
        if passing_version or home_status.state in [
            "certification_pending",
            "complete",
        ]:
            return PassingStatusTuple(data=version)

        msg = home_strings.NWESH_NEW_HOMES_PROGRAM_REM_VERSION_REQUIREMENT.format(
            program=program, versions=versions
        )
        return FailingStatusTuple(data=None, message=msg, url=edit_url)

    @requirement_test(
        "Verify Built Green Annotation",
        eep_program=[
            "built-green-tri-cities",
            "built-green-tri-cities1",
            "built-green-tri-cities-4",
        ],
    )
    def get_built_green_annotations_status(self, home_status, annotations_edit_url, **kwargs):
        annotations = [
            "built-green-house-size-multiplier",
            "built-green-points-section-1",
            "built-green-points-section-2",
            "built-green-points-section-3",
            "built-green-points-section-4",
            "built-green-points-section-5",
            "built-green-points-section-6",
            "built-green-points-section-7",
            "built-green-certification-level",
            "energy-star-certification",
        ]
        done = home_status.annotations.filter(type__slug__in=annotations).count()
        if done < len(annotations):
            return FailingStatusTuple(
                data=None,
                message="Please fill out {} annotations to continue".format(
                    len(annotations) - done
                ),
                url=annotations_edit_url,
            )

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify PNW Required Utilities",
        eep_program=["eto-2017", "eto-2018", "eto-2020"],
    )
    def get_pnw_utility_required_status(
        self, home, home_status, companies_edit_url, input_values, **kwargs
    ):
        # DEPRECATION NOTICE
        # Note that this has been deprecated by two other tests.
        # 1. get_floorplan_simulation_status - Checks to ensure that your checklist response
        #    (primary-heating-equipment-type) is represented in the simulation data
        # 2. get_simulation_electric_utility_status - That checks to make sure that
        #      if your simulation uses a fuel you have the appropriate company.
        # 3. NEEA

        # NOTE: NEEA programs are to be handled by get_neea_utilities_satisfied_status(), which
        # operates a little differently based on what kind of heat source the checklist data
        # declares.

        # Anything non-None in here will trigger a failure
        result_list = []

        if self.slug in ["eto-2017", "eto-2018", "eto-2020"]:
            electric_company = home_status.get_electric_company()
            if not electric_company:
                result_list.append("An electric utility must be assigned.")
            else:
                result_list.append(None)

        if self.slug in ["eto-2018", "eto-2020"]:
            primary_heat_type = input_values.get("primary-heating-equipment-type")
            if primary_heat_type:
                requires_gas_utility = "Gas" in primary_heat_type
                if requires_gas_utility:
                    gas_company = home_status.get_gas_company()
                    if not gas_company:
                        result_list.append(
                            "Heating equipment '{}' requires a gas utility be assigned.".format(
                                primary_heat_type
                            )
                        )
                    else:
                        result_list.append(None)

        error_list = list(filter(None, result_list))
        if error_list:
            if len(error_list) == 1:
                msg = error_list[0]
                message_list = None
            else:
                msg = "{} utility requirements:".format(self)
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(error_list))

            return FailingStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(error_list),
                total_weight=len(result_list),
                url=companies_edit_url,
            )
        return PassingStatusTuple(data=None)

    @requirement_test("Verify Water Heater", eep_program=["neea-bpa"])
    def get_water_heater_status(self, home_status, edit_url, **kwargs):
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        simulation = home_status.floorplan.remrate_target
        if (
            simulation.hotwaterheater_set.filter(type__in=[5, 21]).count()
            or simulation.integratedspacewaterheater_set.count()
        ):
            msg = "Ground Source Heat Pump Water Heaters OR Integrated Space Water Heaters are not allowed"
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify Duct System", eep_program=NEEA_BPA_SLUGS)
    def get_duct_system_test_status(self, home_status, edit_url, **kwargs):
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        simulation = home_status.floorplan.remrate_target
        if simulation.ductsystem_set.filter(
            Q(leakage_tightness_test=4) | Q(leakage_test_exemption=True)
        ).count():
            msg = "Duct System Testing is Required - No exemptions allowed"
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Verify Ventilation Type", eep_program=NEEA_BPA_SLUGS)
    def get_ventilation_type_status(self, home_status, edit_url, **kwargs):
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        simulation = home_status.floorplan.remrate_target
        if simulation.infiltration.mechanical_vent_type == 4:
            msg = "Mechanical Ventilation System for IAQ cannot be Air Cycler"
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

        return PassingStatusTuple(data=None)

    @requirement_test("Percent Improvement OR", eep_program=["eto-2018", "eto-2019", "eto-2020"])
    def get_eto_percent_improvement_oregon(self, home, home_status, **kwargs):
        # DEPRECATION NOTICE
        # This has been superceded by get_eto_builder_incentive_status if you don't meet %
        # improvement you wont get an incentive..
        if home.state != "OR":
            return None

        from axis.home.utils import get_eps_data

        data = {}
        try:
            data = get_eps_data(home_status)
            pct_improvement = data["percent_improvement"] * 100.0
        except KeyError as err:
            log.debug("Unexpected KeyError raised getting eps data - %s", err)
            if "errors" in data:
                return FailingStatusTuple(
                    message="Unable to calculate EPS", data=data["errors"], url=None
                )
            return None
        except Exception as err:
            log.debug("Unexpected Exception raised getting eps data - %s", err)
            return FailingStatusTuple(message="Unable to calculate EPS", data=f"{err}", url=None)

        # ZD13329: 2019 program has moved to using a uniform 10% model across both states,
        # but older program shouldn't reflect the new real-time check.
        target_pct_improvement = 10.0
        if home_status.certification_date or self.slug != "eto-2019":
            target_pct_improvement = 8.0

        if pct_improvement < target_pct_improvement:
            return FailingStatusTuple(
                message=strings.ETO_2018_IMPROVEMENT_FAILURE.format(
                    min_pct=int(target_pct_improvement)
                ),
                data=pct_improvement,
                url=None,
            )
        elif pct_improvement < 10.0:
            return WarningStatusTuple(
                message=strings.ETO_2018_IMPROVEMENT_QA_WARNING,
                data=pct_improvement,
                url=None,
            )
        return PassingStatusTuple(pct_improvement)

    @requirement_test("Percent Improvement WA", eep_program=["eto-2018", "eto-2019", "eto-2020"])
    def get_eto_percent_improvement_washington(self, home, home_status, input_values, **kwargs):
        # DEPRECATION NOTICE
        # This has been superceded by get_eto_builder_incentive_status if you don't meet %
        # improvement you wont get an incentive..

        if home.state != "WA":
            return None

        from axis.home.utils import get_eps_data

        data = None
        pct_improvement = 0.0
        try:
            data = get_eps_data(home_status)
            pct_improvement = data["percent_improvement"] * 100.0
        except KeyError as err:
            log.debug("Unexpected KeyError raised getting WA eps data - %s", err)
            if "errors" in data:
                return FailingStatusTuple(
                    message="Unable to calculate WA EPS", data=data["errors"], url=None
                )
            return None
        except EPSInputException as err:
            log.error("EPSInputException raised eto_percent_improvement_washington - %r", err)
            return FailingStatusTuple(message="Unable to calculate EPS", data=err.args[1], url=None)
        except Exception as err:
            log.error(
                "Exception raised eto_percent_improvement_washington - %r in %r",
                err,
                data,
            )
            return None

        heating_type = input_values.get("primary-heating-equipment-type")
        if heating_type and "electric" in heating_type.lower():
            return PassingStatusTuple(pct_improvement)

        if pct_improvement < 10.0:
            return FailingStatusTuple(
                message=strings.ETO_2018_IMPROVEMENT_FAILURE.format(min_pct=10),
                data=pct_improvement,
                url=None,
            )
        return PassingStatusTuple(pct_improvement)

    @requirement_test("Multifamily", eep_program=["eto-2018"])
    def get_eto_no_multifamily(self, home, home_status, **kwargs):
        if home.is_multi_family:
            return FailingStatusTuple(
                message=strings.ETO_NO_MULTIFAMILY_HOME,
                data="home",
                url=kwargs["home_edit_url"],
            )

        floorplan = home_status.floorplan
        if not floorplan:
            return None

        try:
            building_type = floorplan.remrate_target.building.building_info.type
            rem_is_multifamily = building_type == 6  # HOME_TYPES: "Multi-family, whole building"
        except AttributeError:
            pass
        else:
            if rem_is_multifamily:
                return FailingStatusTuple(
                    message=strings.ETO_NO_MULTIFAMILY_REM,
                    data="rem",
                    url=kwargs["edit_url"],
                )
        return None

    @requirement_test("REM range/oven fuel type", eep_program="eto-2018")
    def get_eto_2018_oven_fuel_type(self, home, home_status, input_values, **kwargs):
        floorplan = home_status.floorplan
        if not floorplan or not floorplan.remrate_target:
            return None

        heating_type = input_values.get("primary-heating-equipment-type")
        if not heating_type:
            return None

        oven_fuel_type = floorplan.remrate_target.building.lightsandappliance.oven_fuel
        heating_type_category = None
        if heating_type.startswith("Gas") or heating_type == "Other Gas":
            heating_type_category = 1  # FUEL_TYPES: "Natural gas"
        elif heating_type.startswith("Electric") or heating_type == "Other Electric":
            heating_type_category = 4  # FUEL_TYPES: "Electric"

        if oven_fuel_type != heating_type_category:
            msg = "Oven Fuel of %s does not match primary heating fuel of %s"
            return FailingStatusTuple(
                message=msg
                % (
                    floorplan.remrate_target.building.lightsandappliance.get_oven_fuel_display(),
                    heating_type,
                ),
                data=(oven_fuel_type, heating_type),
                url=kwargs["checklist_url"],
            )
        return None

    @requirement_test("REM primary heating fuel type", eep_program=["eto-2018", "eto-2019"])
    def get_eto_primary_heating_fuel_type(self, home, home_status, input_values, **kwargs):
        floorplan = home_status.floorplan
        if not floorplan or not floorplan.remrate_target:
            return None

        heating_type = input_values.get("primary-heating-equipment-type")
        if not heating_type:
            return None

        target_id = floorplan.remrate_target.id
        dominant = floorplan.remrate_target.installedequipment_set.get_dominant_values(target_id)[
            target_id
        ]

        primary_heating_fuel = dominant["dominant_heating"]["fuel"]

        has_issue = False
        is_dual = heating_type == "Dual Fuel Heat Pump"
        if primary_heating_fuel in ["Natural gas", "Propane", "Fuel oil"]:
            if "Gas" not in heating_type and not is_dual:
                has_issue = True
        if primary_heating_fuel in ["Electric"]:
            if "Electric" not in heating_type and not is_dual:
                has_issue = True

        if has_issue:
            oven_fuel_name = (
                floorplan.remrate_target.building.lightsandappliance.get_oven_fuel_display()
            )
            msg = strings.ETO_2018_HEATING_FUEL_MISMATCH.format(
                rem_fuel=oven_fuel_name, checklist_fuel=heating_type
            )
            return FailingStatusTuple(
                message=msg,
                data=(primary_heating_fuel, heating_type),
                url=kwargs["checklist_url"],
            )
        return None

    @requirement_test(
        "Simulation primary heating fuel type alignment",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"],
    )
    def get_eto_revised_primary_heating_fuel_type(self, home_status, input_values, **kwargs):
        """Verifies the checklist aligns with the rem rate data."""
        if home_status.floorplan is None or home_status.floorplan.simulation is None:
            return None

        heating_type = input_values.get("primary-heating-equipment-type")
        if not heating_type:
            return None

        simulation = home_status.floorplan.simulation
        try:
            primary_heating_fuel = simulation.dominant_heating_equipment.fuel
        except AttributeError:
            msg = "Unable to identify dominant heating fuel"
            return FailingStatusTuple(message=msg, url=kwargs["checklist_url"], data=None)

        gas_equipment = [
            PrimaryHeatingEquipment2020.GAS_FIREPLACE.value,
            PrimaryHeatingEquipment2020.GAS_UNIT_HEATER.value,
            PrimaryHeatingEquipment2020.GAS_FURNACE.value,
            PrimaryHeatingEquipment2020.GAS_BOILER.value,
            PrimaryHeatingEquipment2020.OTHER_GAS.value,
        ]
        electric_equipment = [
            PrimaryHeatingEquipment2020.DUCTED_ASHP.value,
            PrimaryHeatingEquipment2020.MINI_SPLIT_NON_DUCTED.value,
            PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED.value,
            PrimaryHeatingEquipment2020.MINI_SPLIT_MIXED.value,
            PrimaryHeatingEquipment2020.GSHP.value,
            PrimaryHeatingEquipment2020.ELECTRIC_RESISTANCE.value,
            PrimaryHeatingEquipment2020.OTHER_ELECTRIC.value,
            PrimaryHeatingEquipment2020.DFHP.value,
        ]

        has_issue = False
        if (
            primary_heating_fuel in [FuelType.NATURAL_GAS, FuelType.PROPANE, FuelType.OIL]
            and heating_type not in gas_equipment
        ):
            has_issue = True
        elif primary_heating_fuel in [FuelType.ELECTRIC] and heating_type not in electric_equipment:
            has_issue = True

        if has_issue:
            msg = strings.ETO_HEATING_FUEL_MISMATCH.format(
                simulation_fuel=primary_heating_fuel.replace("_", " ").capitalize(),
                checklist_fuel=heating_type,
            )
            return FailingStatusTuple(
                message=msg,
                data=(primary_heating_fuel, heating_type),
                url=kwargs["checklist_url"],
            )

        return PassingStatusTuple(data=None)

    @requirement_test("REM clothes dryer", eep_program="eto-2018")
    def get_eto_2018_dryer_attributes(self, home, home_status, input_values, **kwargs):
        floorplan = home_status.floorplan
        if not floorplan or not floorplan.remrate_target:
            return None

        lights_and_appliance = floorplan.remrate_target.building.lightsandappliance

        failures = []

        def check_location():
            dryer_location = lights_and_appliance.clothes_dryer_location
            if dryer_location != 1:  # LIGHT_APP_LOCATIONS: "Conditioned"
                failures.append(strings.ETO_2018_DRYER_LOCATION_NOT_CONDITIONED)

        def check_fuel():
            primary_heating_fuel = input_values.get("primary-heating-equipment-type")

            if not primary_heating_fuel:
                return

            dryer_fuel = lights_and_appliance.clothes_dryer_fuel

            # These are the only two categories of fuel represented in the 2018 primary heating
            # fuel question.
            valid_fuels = {
                1: "gas",  # FUEL_TYPES: "Natural gas"
                2: "gas",  # FUEL_TYPES: "Propane"
                3: "gas",  # FUEL_TYPES: "Fuel oil"
                4: "electric",  # FUEL_TYPES: "Electric"
            }

            fuel_keyword = valid_fuels.get(dryer_fuel, "")
            if fuel_keyword not in primary_heating_fuel.lower():
                failures.append(
                    strings.ETO_2018_DRYER_FUEL_MISMATCH.format(
                        **{
                            "dryer_fuel": lights_and_appliance.get_clothes_dryer_fuel_display(),
                            "checklist_fuel": primary_heating_fuel,
                        }
                    )
                )

        def check_ef():
            dryer_ef = lights_and_appliance.clothes_dryer_energy_factor
            if dryer_ef != 3.01:
                failures.append(strings.ETO_2018_DRYER_EF_NOT_3_01)

        checks = [
            check_location,
            check_fuel,
            check_ef,
        ]
        total_weight = len(checks)

        for check in checks:
            check()

        if failures:
            if len(failures) == 1:
                message = failures[0]
                message_list = None
            else:
                message = "Incorrect REM values"
                message_list = """<ul><li>{}</li><ul>""".format("""</li><li>""".join(failures))
            return FailingStatusTuple(
                message=message,
                data=message_list,
                show_data=bool(message_list),
                weight=len(failures),
                total_weight=total_weight,
                url=None,
            )

        return None

    @requirement_test("Heat pump water heater serial number", eep_program=["eto-2017", "eto-2018"])
    def get_eto_heat_pump_water_heater_status(
        self, home, home_status, checklist_url, input_values, **kwargs
    ):
        floorplan = home_status.floorplan
        if not floorplan or not floorplan.remrate_target:
            return None

        HEAT_PUMP_TYPE = 4  # H2O_HEATER_TYPES "Heat pump"
        IMPLEMENTATION_CHANGE_DATE = datetime.date(2018, 4, 1)
        heat_pump = floorplan.remrate_target.installedequipment_set.filter(
            hot_water_heater__type=HEAT_PUMP_TYPE
        ).first()

        if not heat_pump:
            return None  # Requirement doesn't apply

        # When a heat pump is present, require the optional checklist question for its serial number
        answer = input_values.get("heat-pump-water-heater-serial-number")
        if answer:
            return PassingStatusTuple(data=answer)

        failure_type = FailingStatusTuple
        msg = strings.ETO_HEAT_PUMP_WATER_HEATER_SERIAL_NUMBER_REQUIRED

        # Demote to a warning if the home was moved to qa_pending before this test's implementation
        # date.  Note that we look for the last occurence of this transition in case it got reset
        # and placed back into qa_pending after the concerned date marker.  Also note that this
        # transition may exist even though the home went back to inspection but hasn't re-entered
        # qa_pending.
        if home_status.state != "inspection":
            qa_pending_transition = (
                home_status.state_history.filter(to_state="qa_pending")
                .order_by("start_time")
                .last()
            )
            if qa_pending_transition:
                transition_date = qa_pending_transition.start_time.date()
                if transition_date and transition_date < IMPLEMENTATION_CHANGE_DATE:
                    failure_type = WarningStatusTuple

        return failure_type(message=msg, data=None, url=checklist_url)

    @requirement_test("Program ending")
    def get_program_end_warning_status(self, home, home_status, **kwargs):
        eep_program = home_status.eep_program
        submit_date = eep_program.program_submit_date
        warn_date = eep_program.program_submit_warning_date
        if all([submit_date, warn_date]) and warn_date <= now().date():
            msg = strings.PROGRAM_SUBMIT_DATE_APPROACHING
            msg = msg.format(
                program_name=eep_program.name,
                date=eep_program.program_submit_date.strftime("%B %d, %Y"),
            )
            return WarningStatusTuple(message=msg, data=eep_program.program_submit_date, url=None)
        end_date = eep_program.program_end_date
        warn_date = eep_program.program_close_warning_date
        if all([end_date, warn_date]) and warn_date <= now().date():
            msg = strings.PROGRAM_END_DATE_APPROACHING
            msg = msg.format(
                program_name=eep_program.name,
                date=eep_program.program_end_date.strftime("%B %d, %Y"),
            )
            return WarningStatusTuple(message=msg, data=eep_program.program_end_date, url=None)
        return None

    @requirement_test("Verify checklist heat-source", eep_program=NEEA_BPA_SLUGS)
    def get_neea_checklist_type_matches_remrate_status(
        self, home, home_status, input_values, **kwargs
    ):
        if home_status.certification_date or home_status.floorplan is None:
            return None

        heat_source = input_values.get("neea-heating_source")
        if heat_source is None:
            return None

        heat_source = LONG_DASHES.sub("-", heat_source)

        if home_status.floorplan:
            simulation = home_status.floorplan.remrate_target
        else:
            return None

        if simulation is None:
            return None

        dominant = simulation.installedequipment_set.get_dominant_values(simulation.id)[
            simulation.id
        ]

        heating = dominant["dominant_heating"]
        cooling = dominant["dominant_cooling"]

        msg = "Primary heating type '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(heating["type"], heat_source)

        if heat_source == "Heat Pump":
            if "heat pump" not in heating["type"].lower() and "air" not in heating["type"].lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source in [
            "Heat Pump - Geothermal",
            "Heat Pump - Geothermal/Ground Source",
        ]:
            if "Ground-source heat pump".lower() not in heating["type"].lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Heat Pump - w/ Gas Backup":
            if heating["type"].lower() != "Dual Fuel heat Pump".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            # TODO FUEL CHECK

        elif heat_source == "Heat Pump - Mini Split":
            if "heat pump".lower() not in heating["type"].lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Gas with AC":
            if "Fuel-fired air distribution".lower() not in heating["type"].lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if "gas" not in heating["fuel"]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if cooling["type"] is None:
                _msg = "Air Conditioner is not present in REM/Rate but checklist answer indicates {}".format(
                    heat_source
                )
                return FailingStatusTuple(message=_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Gas No AC":
            if "Fuel-fired air distribution".lower() not in heating["type"].lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if "gas" not in heating["fuel"]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if cooling["type"] is not None:
                _msg = "Air Conditioner is present in REM/Rate but checklist answer indicates {}".format(
                    heat_source
                )
                return FailingStatusTuple(message=_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Zonal Electric":
            if "Electric baseboard or radiant".lower() not in heating["type"].lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if heating["fuel"] != "Electric":
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Propane, Oil, or Wood":
            if (
                "Fuel-fired unit heater".lower() not in heating["type"].lower()
                and "Fuel-fired unvented unit heater".lower() not in heating["type"].lower()
            ):
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if heating["fuel"] not in ["Propane", "Fuel oil", "Wood"]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Hydronic Radiant Electric Boiler":
            if (
                "Hydronic Ground-source heat pump".lower() not in heating["type"].lower()
                and "Electric hydronic distribution".lower() not in heating["type"].lower()
            ):
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if heating["fuel"] != "Electric":
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Hydronic Radiant Gas Boiler":
            if (
                "Hydronic Ground-source heat pump".lower() not in heating["type"].lower()
                and "Fuel-fired hydronic distribution".lower() not in heating["type"].lower()
            ):
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if heating["fuel"] != "Natural gas":
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif heat_source == "Hydronic Radiant Heat Pump":
            if (
                "Hydronic Ground-source heat pump".lower() not in heating["type"].lower()
                and "Electric baseboard or radiant".lower() not in heating["type"].lower()
            ):
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
        else:
            log.error(
                "Unable to verify heat source answer for %s of %s",
                home_status.id,
                heat_source,
            )

        return PassingStatusTuple(data=None)

    @requirement_test("Verify checklist water heater", eep_program=NEEA_BPA_SLUGS)
    def get_neea_checklist_water_heater_matches_remrate_status(
        self, home, home_status, input_values, **kwargs
    ):
        if home_status.certification_date:
            return None

        water_heater = input_values.get("neea-water_heater_tier")
        if not water_heater:
            return None

        water_heater = LONG_DASHES.sub("-", water_heater)

        if home_status.floorplan:
            simulation = home_status.floorplan.remrate_target
        else:
            return None

        if simulation is None:
            return None

        dominant = simulation.installedequipment_set.get_dominant_values(simulation.id)[
            simulation.id
        ]

        water = dominant.get("dominant_hot_water")

        msg = "Primary water heater '{}' in REM/Rate does not align with checklist answer of '{}'"
        fail_msg = msg.format(water["type"], water_heater)

        if water.get("type") is None or water.get("fuel") is None:
            return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        if water_heater == "Electric Resistance":
            if water["type"].lower() != "Conventional".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() != "Electric".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif water_heater in ["HPWH Tier 1", "HPWH Tier 2", "HPWH Tier 3"]:
            if "heat pump" not in water["type"].lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() != "Electric".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif water_heater == "Gas Conventional EF < 0.67":
            if water["type"].lower() != "Conventional".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() not in ["Natural gas".lower()]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["energy_factor"] >= 0.67:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif water_heater == "Gas Conventional EF ≥ 0.67":
            if water["type"].lower() != "Conventional".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() not in ["Natural gas".lower()]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if 0.70 > water["energy_factor"] < 0.67:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif water_heater == "Gas Conventional EF ≥ 0.70":
            if water["type"].lower() != "Conventional".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() not in ["Natural gas".lower()]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["energy_factor"] < 0.70:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif water_heater == "Gas Tankless EF ≥ 0.82":
            if water["type"].lower() != "Instant water heater".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() not in ["Natural gas".lower()]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["energy_factor"] < 0.82:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        elif water_heater == "Gas Tankless EF ≥ 0.90":
            if water["type"].lower() != "Instant water heater".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() not in ["Natural gas".lower()]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["energy_factor"] < 0.90:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
        elif water_heater == "Propane Tankless":
            if water["type"].lower() != "Instant water heater".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() not in ["Propane".lower()]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
        elif water_heater == "Propane Tank":
            if water["type"].lower() == "Instant water heater".lower():
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
            if water["fuel"].lower() not in ["Propane".lower()]:
                return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])
        else:
            return FailingStatusTuple(message=fail_msg, data=None, url=kwargs["checklist_url"])

        return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify Refrigerator Brand & Model Number",
        eep_program=["neea-bpa"],
        ignore_before="2018-07-23",
    )
    def get_neea_bpa_refrigerator_installed_status(self, home, home_status, input_values, **kwargs):
        if home_status.certification_date:
            return None

        source_question_slug = "estar_std_refrigerators_installed"
        source_question_value = "Yes"
        required_question_slug = "refrigerator-combo"
        fail_msg = "Brand & Model Number are required if an ENERGY STAR refrigerator is installed."
        fail_url = kwargs["checklist_url"]

        source_value = input_values.get(source_question_slug)
        if source_value != source_question_value:
            return None

        required_value = input_values.get(required_question_slug)
        if not required_value:
            return FailingStatusTuple(message=fail_msg, data=None, url=fail_url)

        return PassingStatusTuple(data=required_value)

    @requirement_test("Verify Refrigerator Brand & Model Number", eep_program=["neea-bpa-v3"])
    def get_neea_v3_refrigerator_installed_status(self, home, home_status, input_values, **kwargs):
        source_question_slug = "neea_refrigerators_installed"
        source_question_values = [
            REFRIGERATOR_BOTTOM_FREEZER_LABEL,
            REFRIGERATOR_SIDE_FREEZER_LABEL,
            REFRIGERATOR_OTHER_FREEZER_LABEL,
        ]
        required_question_slug = "refrigerator-combo"
        fail_msg = "Brand & Model Number are required if an ENERGY STAR refrigerator is installed."
        fail_url = kwargs["checklist_url"]

        source_value = input_values.get(source_question_slug)
        if source_value not in source_question_values:
            return None

        required_value = input_values.get(required_question_slug)
        if not required_value:
            return FailingStatusTuple(message=fail_msg, data=None, url=fail_url)

        return PassingStatusTuple(data=required_value)

    @requirement_test(
        "Verify Clothes Washer Brand & Model Number",
        eep_program=["neea-bpa"],
        ignore_before="2018-07-23",
    )
    def get_neea_bpa_clothes_washer_installed_status(
        self, home, home_status, input_values, **kwargs
    ):
        if home_status.certification_date:
            return None

        source_question_slug = "estar_front_load_clothes_washer_installed"
        source_question_value = "Yes"
        required_question_slug = "clothes-washer-combo"
        fail_msg = (
            "Brand & Model Number are required if an ENERGY STAR clothes washer is installed."
        )
        fail_url = kwargs["checklist_url"]

        source_value = input_values.get(source_question_slug)
        if source_value != source_question_value:
            return None

        required_value = input_values.get(required_question_slug)
        if not required_value:
            return FailingStatusTuple(message=fail_msg, data=None, url=fail_url)

        return PassingStatusTuple(data=required_value)

    @requirement_test(
        "Verify Clothes Washer Brand & Model Number",
        eep_program=["neea-bpa-v3"],
    )
    def get_neea_v3_clothes_washer_installed_status(
        self, home, home_status, input_values, **kwargs
    ):
        if home_status.certification_date:
            return None

        source_question_slug = "neea_clothes_washer_installed"
        source_question_values = [CLOTHES_WASHER_TOP_LABEL, CLOTHES_WASHER_SIDE_LABEL]
        required_question_slug = "clothes-washer-combo"
        fail_msg = (
            "Brand & Model Number are required if an ENERGY STAR clothes washer is installed."
        )
        fail_url = kwargs["checklist_url"]

        source_value = input_values.get(source_question_slug)
        if source_value not in source_question_values:
            return None

        required_value = input_values.get(required_question_slug)
        if not required_value:
            return FailingStatusTuple(message=fail_msg, data=None, url=fail_url)

        return PassingStatusTuple(data=required_value)

    @requirement_test(
        "Verify Clothes Dryer Brand & Model Number",
        eep_program=NEEA_BPA_SLUGS,
        ignore_before="2018-07-23",
    )
    def get_neea_bpa_clothes_dryer_installed_status(
        self, home, home_status, input_values, **kwargs
    ):
        if home_status.certification_date:
            return None

        source_question_slug = "neea-clothes_dryer_tier"
        source_question_values = ["ENERGY STAR®", "Tier 2", "Tier 3"]
        required_question_slug = "clothes-dryer-combo"
        fail_msg = "Brand & Model Number are required if clothes dryer is one of: ENERGY STAR®, Tier2, or Tier 3."
        fail_url = kwargs["checklist_url"]

        source_value = input_values.get(source_question_slug)
        if source_value not in source_question_values:
            return None

        required_value = input_values.get(required_question_slug)
        if not required_value:
            return FailingStatusTuple(message=fail_msg, data=None, url=fail_url)

        return PassingStatusTuple(data=required_value)

    @requirement_test(
        "Verify Dishwasher Brand & Model Number",
        eep_program=NEEA_BPA_SLUGS,
        ignore_before="2018-07-23",
    )
    def get_neea_bpa_dishwasher_installed_status(self, home, home_status, input_values, **kwargs):
        if home_status.certification_date:
            return None

        source_question_slug = "estar_dishwasher_installed"
        source_question_value = "Yes"
        required_question_slug = "dishwasher-combo"
        fail_msg = "Brand & Model Number are required if an ENERGY STAR dishwasher is installed."
        fail_url = kwargs["checklist_url"]

        source_value = input_values.get(source_question_slug)
        if source_value != source_question_value:
            return None

        required_value = input_values.get(required_question_slug)
        if not required_value:
            return FailingStatusTuple(message=fail_msg, data=None, url=fail_url)

        return PassingStatusTuple(data=required_value)

    @requirement_test("Verify Smart Thermostat Brand & Model Number", eep_program=NEEA_BPA_SLUGS)
    def get_neea_bpa_checklist_smart_thermostat_installed_status(
        self, home, home_status, input_values, **kwargs
    ):
        if home_status.certification_date:
            return None

        source_question_slug = "smart_thermostat_installed"
        source_question_value = "Yes"
        required_question_slug = "smart-thermostat-combo"
        fail_msg = "Brand & Model Number are required if smart thermostat is installed."
        fail_url = kwargs["checklist_url"]

        source_value = input_values.get(source_question_slug)
        if source_value != source_question_value:
            return None

        required_value = input_values.get(required_question_slug)
        if not required_value:
            return FailingStatusTuple(message=fail_msg, data=None, url=fail_url)

        return PassingStatusTuple(data=required_value)

    @requirement_test(
        "Check incentive requirements",
        eep_program=["eto-2018", "eto-2019", "eto-2020"],
        ignore_before="2018-09-09",
    )
    def get_eto_legacy_builder_incentive_status(self, home_status, edit_url, **kwargs):
        """Blocks certification if the Percent Improvement is < 10% or if no builder incentive"""
        # Deprecation NOTICE
        # Replaced get_eto_builder_incentive_status

        from axis.home.utils import get_eps_data

        builder_incentive = 0.0
        try:
            data = get_eps_data(home_status)
            builder_incentive = data["builder_incentive"]
        except EPSInputException as err:
            return FailingStatusTuple(message="Unable to calculate EPS", data=err.args[1], url=None)
        except Exception as err:
            log.debug("Unable to get EPS - %s", err)

        if builder_incentive > 0.0:
            return PassingStatusTuple(data=builder_incentive)

        return FailingStatusTuple(
            data=builder_incentive,
            message=home_strings.BUILDER_INCENTIVE_TOO_LOW,
            url=edit_url,
        )

    @requirement_test("Verify REM/Rate version", eep_program=["eto-2019"])
    def get_eto_min_program_version(self, home, home_status, **kwargs):
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        try:
            version_obj = home_status.floorplan.remrate_target.numerical_version
        except AttributeError:
            log.warning(
                "Unable to get simulation numerical_version from floorplan %d",
                home_status.floorplan,
            )
            return FailingStatusTuple(
                message=strings.ETO_REM_DATA_VERSION, data=None, url=kwargs["edit_url"]
            )
        data_version = (version_obj.major, version_obj.minor, version_obj.sub)
        if data_version != (15, 7, 1):
            return FailingStatusTuple(
                message=strings.ETO_REM_DATA_VERSION,
                data=data_version,
                url=kwargs["edit_url"],
            )

        try:
            flavor = home_status.floorplan.remrate_target.flavor
        except AttributeError:
            log.warning(
                "Unable to get simulation flavor from floorplan %d",
                home_status.floorplan,
            )
            return FailingStatusTuple(
                message=strings.ETO_REM_DATA_VERSION, data=None, url=kwargs["edit_url"]
            )

        if flavor.lower() != "rate":
            return FailingStatusTuple(
                message=strings.ETO_REM_DATA_VERSION, data=None, url=kwargs["edit_url"]
            )

        return PassingStatusTuple(data=data_version)

    @requirement_test(
        "Verify Simulation version",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022", "neea-bpa-v3"],
    )
    def get_min_max_simulation_version(self, home_status, **kwargs):
        """Verify that for the program we meet the minimums"""

        eep_program_vals = {
            "eto-2020": {"min_rem_version": "15.7.1", "min_ekotrope_version": "3.0.0"},
            "eto-2021": {"min_rem_version": "15.7.1", "min_ekotrope_version": "3.0.0"},
            "eto-fire-2021": {
                "min_rem_version": "15.7.1",
                "min_ekotrope_version": "3.0.0",
                "max_rem_version": "15.7.1",
                "max_ekotrope_version": "3.0.0",
            },
            "eto-2022": {
                "min_rem_version": "16.0.6",
                "min_ekotrope_version": "3.1.1",
                "max_rem_version": "16.0.6",
                "max_ekotrope_version": "4.0.1",
            },
            "neea-bpa-v3": {
                "min_rem_version": "16.0.6",
                "max_rem_version": "16.0.6",
            },
        }

        if not home_status.floorplan or not home_status.floorplan.simulation:
            return None

        simulation = home_status.floorplan.simulation
        target = eep_program_vals.get(self.slug)

        if target is None:
            return None

        tool = f"{simulation.get_source_type_display()} {simulation.version}"
        value = []
        if "min_rem_version" in target or "min_ekotrope_version" in target:
            if not simulation.meets_min_version(
                rem_version=target.get("min_rem_version"),
                ekotrope_version=target.get("min_ekotrope_version"),
            ):
                if target.get("min_rem_version"):
                    flag = ">="
                    if target["min_rem_version"] == target.get("max_rem_version"):
                        flag = "=="
                    value.append(f"REM {flag} {target['min_rem_version']}")
                if target.get("min_ekotrope_version"):
                    flag = ">="
                    if target["min_ekotrope_version"] == target.get("max_ekotrope_version"):
                        flag = "=="
                    value.append(f"Ekotrope {flag} {target['min_ekotrope_version']}")
                return FailingStatusTuple(
                    message=f"Simulation data must be {' or '.join(value)}. You gave {tool}",
                    data=simulation.numerical_version,
                    url=kwargs["edit_url"],
                )

        if "max_rem_version" in target or "max_ekotrope_version" in target:
            if not simulation.meets_max_version(
                rem_version=target.get("max_rem_version"),
                ekotrope_version=target.get("max_ekotrope_version"),
            ):
                if target.get("max_rem_version"):
                    flag = "<="
                    if target["max_rem_version"] == target.get("min_rem_version"):
                        flag = "=="

                    value.append(f"REM {flag} {target['max_rem_version']}")
                if target.get("max_ekotrope_version"):
                    flag = "<="
                    if target["max_ekotrope_version"] == target.get("min_ekotrope_version"):
                        flag = "=="
                    value.append(f"Ekotrope {flag} {target['max_ekotrope_version']}")

                return FailingStatusTuple(
                    message=f"Simulation data must be {' or '.join(value)}. You gave {tool}",
                    data=simulation.numerical_version,
                    url=kwargs["edit_url"],
                )

        return PassingStatusTuple(data=simulation.numerical_version)

    @requirement_test("Verify REM/Rate UDRH", eep_program=["eto-2019", "neea-bpa"])
    def get_remrate_udhr_check(self, home_status, edit_url, **kwargs):
        if not home_status.floorplan or not home_status.floorplan.remrate_target:
            return None

        version = home_status.floorplan.remrate_target.numerical_version
        if version != (15, 7, 1):
            return None

        checksum_to_file = dict(ETO_2020_CHECKSUMS)
        if home_status.eep_program.slug == "eto-2019":
            checksum_to_file = dict(ETO_2019_CHECKSUMS)
        elif home_status.eep_program.slug in NEEA_BPA_SLUGS:
            checksum_to_file = dict(NEEA_BPA_2019_CHECKSUMS)

        valid_checksums = checksum_to_file.keys()

        try:
            checksum = home_status.floorplan.remrate_target.udrh_checksum
        except AttributeError:
            log.warning(
                "Unable to get simulation udrh_checksum from floorplan %d",
                home_status.floorplan,
            )
            return FailingStatusTuple(
                data=None, message=strings.FAILING_UDRH_CHECKSUM, url=edit_url
            )

        if checksum not in valid_checksums:
            return FailingStatusTuple(
                data=None, message=strings.FAILING_UDRH_CHECKSUM, url=edit_url
            )

        try:
            udrh_filename = home_status.floorplan.remrate_target.udrh_filename
        except AttributeError:
            log.warning(
                "Unable to get simulation udrh_checksum from floorplan %d",
                home_status.floorplan,
            )
            return FailingStatusTuple(
                data=None, message=strings.FAILING_UDRH_CHECKSUM, url=edit_url
            )

        valid_filenames = checksum_to_file[checksum]
        if not isinstance(valid_filenames, tuple):
            valid_filenames = (valid_filenames,)
        if udrh_filename not in valid_filenames:
            return FailingStatusTuple(
                data=None,
                message=strings.FAILING_UDRH_FILE.format(file=checksum_to_file[checksum]),
                url=edit_url,
            )

        return PassingStatusTuple(data=checksum)

    @requirement_test(
        "Verify Simulation UDRH",
        eep_program=["eto-2020", "eto-2021", "neea-bpa-v3", "eto-fire-2021", "eto-2022"],
    )
    def get_simulation_udrh_check(self, home_status, edit_url, **kwargs):
        """Verifies that our program UDRH Checksums have not been messed with"""

        eep_program_choices = {
            "eto-2020": ETO_2020_CHECKSUMS,
            "eto-2021": ETO_2021_CHECKSUMS,
            "eto-fire-2021": ETO_FIRE_2021_CHECKSUMS,
            "neea-bpa-v3": NEEA_BPA_2021_CHECKSUMS,
            "eto-2022": ETO_2023_CHECKSUMS,
        }
        if not home_status.floorplan or not home_status.floorplan.simulation:
            return None

        simulation = home_status.floorplan.simulation
        if simulation.source_type != SourceType.REMRATE_SQL or simulation.analyses.first() is None:
            return

        checksums = eep_program_choices.get(home_status.eep_program.slug)
        valid_checksums = [checksum for checksum, filenames in checksums]
        checksum = simulation.analyses.first().source_qualifier

        if checksum not in valid_checksums:
            return FailingStatusTuple(
                data=None, message=strings.FAILING_UDRH_CHECKSUM, url=edit_url
            )

        valid_filenames = []
        for chksum, filenames in checksums:
            if not isinstance(filenames, (list, tuple)):
                filenames = [filenames]
            for filename in filenames:
                valid_filenames.append((filename, chksum))

        udrh_filename = simulation.analyses.first().source_name
        if udrh_filename not in dict(valid_filenames).keys():
            msg = (
                f"Incorrect UDRH associated to checksum {checksum}.  This is verified via checksum."
            )
            return FailingStatusTuple(
                data=None,
                message=msg,
                url=edit_url,
            )

        valid_checksum = dict(valid_filenames).get(udrh_filename)
        if checksum != valid_checksum:
            msg = f"Incorrect UDRH checksum associated with {udrh_filename}"
            return FailingStatusTuple(data=udrh_filename, message=msg, url=edit_url)

        return PassingStatusTuple(data=checksum)

    def _verify_approved_utility(self, home_status, utility, label, edit_url, program_slug=None):
        from axis.customer_eto.eep_programs.eto_2022 import (
            ETO_2023_FUEL_RATES,
            ETO_2023_FUEL_RATES_WA_OVERRIDE,
        )

        fuel_rates = dict(ETO_2023_FUEL_RATES)
        if home_status.home.state == "WA":
            fuel_rates.update(dict(ETO_2023_FUEL_RATES_WA_OVERRIDE))

        if program_slug == "eto-2021":
            from axis.customer_eto.eep_programs.eto_2021 import (
                ETO_2021_FUEL_RATES,
                ETO_2021_FUEL_RATES_WA_OVERRIDE,
            )

            fuel_rates = dict(ETO_2021_FUEL_RATES)
            if home_status.home.state == "WA":
                fuel_rates.update(dict(ETO_2021_FUEL_RATES_WA_OVERRIDE))

        elif program_slug == "eto-2020":
            from axis.customer_eto.calculator.eps.constants.eto_2020 import (
                ETO_2020_FUEL_RATES,
                ETO_2020_FUEL_RATES_WA_OVERRIDE,
            )

            fuel_rates = dict(ETO_2020_FUEL_RATES)
            if home_status.home.state == "WA":
                fuel_rates.update(dict(ETO_2020_FUEL_RATES_WA_OVERRIDE))

        elif program_slug == "eto-2019":
            from axis.customer_eto.calculator.eps import (
                ETO_2019_FUEL_RATES,
                ETO_2019_FUEL_RATES_WA_OVERRIDE,
            )

            fuel_rates = dict(ETO_2019_FUEL_RATES)
            if home_status.home.state == "WA":
                fuel_rates.update(dict(ETO_2019_FUEL_RATES_WA_OVERRIDE))

        if utility:
            if fuel_rates.get(utility.slug) is None:
                return FailingStatusTuple(
                    data=None,
                    message=strings.ETO_ALLOWED_UTILITY_COMPANIES.format(
                        company=utility, type=label
                    ),
                    url=edit_url,
                )
            return PassingStatusTuple(data=None)

    @requirement_test(
        "Verify Gas Utility Company matches REM/Rate Fuel Rate", eep_program="eto-2019"
    )
    def get_eto_2019_approved_utility_gas_utility(self, home_status, edit_url, **kwargs):
        return self._verify_approved_utility(
            home_status, home_status.get_gas_company(), "Gas", edit_url, "eto-2019"
        )

    @requirement_test(
        "Verify Electric Utility Company matches REM/Rate Fuel Rate",
        eep_program="eto-2019",
    )
    def get_eto_2019_approved_utility_electric_utility(self, home_status, edit_url, **kwargs):
        return self._verify_approved_utility(
            home_status,
            home_status.get_electric_company(),
            "Electric",
            edit_url,
            "eto-2019",
        )

    @requirement_test("Simulation passes ENERGY STAR", eep_program="aps-energy-star-v3-2019")
    def get_aps_2019_estar_check(self, home_status, edit_url, **kwargs):
        """Blocks certification if the ENERGY STAR Does not pass"""

        if not home_status.floorplan:
            return None

        if home_status.floorplan.remrate_target:
            message = strings.APS_2019_FAILING_REM_ESTAR
            passes_estar = home_status.floorplan.simulation_passes_energy_star_v3
        elif home_status.floorplan.ekotrope_houseplan:
            message = strings.APS_2019_FAILING_EKOTROPE_ESTAR
            passes_estar = home_status.floorplan.simulation_passes_energy_star_v3
        else:
            return None

        if passes_estar:
            return PassingStatusTuple(data=passes_estar)

        return WarningStatusTuple(data=None, message=message, url=edit_url)

    @requirement_test(
        "Electric Utility Required",
        eep_program=["built-green-wa-performance", "built-green-wa-prescriptive"],
    )
    def get_built_green_wa_electric_utility_required_status(
        self, home, home_status, companies_edit_url, **kwargs
    ):
        """Verify the unconditional electric utility requirement."""

        electric_utility = home.get_electric_company()
        if not electric_utility:
            return FailingStatusTuple(
                message="A electric utility is required.",
                url=companies_edit_url,
                data=None,
            )

        return PassingStatusTuple(data=electric_utility.id)

    @requirement_test("Gas Utility Required", eep_program=["built-green-wa-performance"])
    def get_built_green_wa_gas_utility_required_status(
        self, home, home_status, companies_edit_url, **kwargs
    ):
        """Verify the gas utility requirement for the floorplan's REM data."""

        if not home_status.floorplan:
            return None

        simulation = home_status.floorplan.remrate_target
        if not simulation:
            return None

        gas_utility = home.get_gas_company()
        has_space_gas_or_water_heating = simulation.installedequipment_set.filter(
            system_type__in=[1, 7]
        )  # 'Space Heating', 'Integrated Space/Water Heating'
        if not gas_utility and has_space_gas_or_water_heating:
            return FailingStatusTuple(
                message="A gas utility is required when gas spacing heating or water heating is present.",
                url=companies_edit_url,
                data=None,
            )

        return PassingStatusTuple(data=gas_utility.id)

    @requirement_test("Energy Code Dwelling Size Validations", eep_program=["wa-code-study"])
    def get_wa_code_annotation_dwelling_status(
        self, home_status, input_values, checklist_url, **kwargs
    ):
        """Verify the dwelling annotation match the checklist responses"""

        annotation = home_status.annotations.filter(type__slug="dwelling-type")

        collected_data = input_values.get("home-size")

        if not annotation.exists() or not collected_data:
            return
        annotation = annotation.get().content.lower()
        err = None

        if int(collected_data) > 5000 and "large" not in annotation:
            err = ">5000 sq ft you must select large dwelling type"
        elif 5000 >= int(collected_data) >= 1500 and "medium" not in annotation:
            err = ">= 1500 sq ft you must select medium dwelling type"
        elif int(collected_data) < 1500 and "small" not in annotation:
            err = "<1500 sq ft you must select small dwelling type"

        if err:
            return WarningStatusTuple(
                message=err, url=checklist_url, data=None, weight=1, total_weight=1
            )
        return PassingStatusTuple(data=annotation, weight=1, total_weight=1)

    @requirement_test("Energy Code Option 1 Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_1_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option 1"""
        annotation = home_status.annotations.filter(type__slug="efficient-building-envelope")

        foundation_type = input_values.get("foundation-type")
        foundation_r_value = input_values.get("home-foundation-r-value")
        floor_r_value = input_values.get("home-floor-r-value")
        window_u_value = input_values.get("home-window-u-value")
        meets_ceiling_req = input_values.get("meets-wa-code-ceiling-requirements")
        meets_below_grade = input_values.get("meets-wa-code-qty-below-grade-wall")
        meets_above_grade = input_values.get("meets-wa-code-above-grade-wall-requirements")

        if not annotation.exists():
            return
        annotation = annotation.get().content.lower()
        errors = []

        def check_foundation():
            """Level 3 Slab foundation check"""
            if foundation_type and foundation_type in [
                "Slab on Grade",
                "Below Grade Slab",
            ]:
                if foundation_r_value and float(foundation_r_value) < 10.0:
                    err = "%s requires %s of R-Value >= 10.0" % (
                        annotation,
                        foundation_type,
                    )
                    errors.append(err)

        def check_floor_r_value():
            """Level 3 Floor R-Value check"""
            if floor_r_value and float(floor_r_value) < 38.0:
                err = "%s requires %s R-Value >= 38.0" % (annotation, "floor")
                errors.append(err)

        def check_window_u_value():
            """Level 3 Window U-Value check"""
            data_map = {"1a": 0.28, "1b": 0.25, "1c": 0.22, "1d": 0.24}
            if window_u_value and float(window_u_value) > data_map[annotation]:
                err = "%s requires Window U-Value <= %s" % (
                    annotation,
                    data_map[annotation],
                )
                errors.append(err)

        def ceiling_check_yes_value():
            """Level 3 yes validations"""
            if meets_ceiling_req and meets_ceiling_req != "Yes":
                err = "%s requires Energy Credit Option 1C check to be 'Yes'"
                errors.append(err % annotation)

        def below_yes_value():
            """Level 3 yes validations"""
            if meets_below_grade and meets_below_grade != "Yes":
                err = "%s requires Meeting Below Grade Wall Requirements to be 'Yes'"
                errors.append(err % annotation)

        def above_yes_value():
            """Level 3 yes validations"""
            if meets_above_grade and meets_above_grade != "Yes":
                err = "%s requires Meeting Above Grade Wall Requirements to be 'Yes'"
                errors.append(err % annotation)

        checks = []
        if annotation == "1a":
            checks.append(check_foundation)
            checks.append(check_floor_r_value)
            checks.append(check_window_u_value)
        elif annotation == "1b":
            checks.append(check_foundation)
            checks.append(check_floor_r_value)
            checks.append(check_window_u_value)
            checks.append(below_yes_value)
            checks.append(above_yes_value)
        elif annotation == "1c":
            checks.append(check_foundation)
            checks.append(check_floor_r_value)
            checks.append(check_window_u_value)
            checks.append(ceiling_check_yes_value)
            checks.append(below_yes_value)
            checks.append(above_yes_value)
        elif annotation == "1d":
            checks.append(check_window_u_value)

        if not checks:
            return

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 1 Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))
            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Energy Code Option 2 Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_2_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option 2"""
        annotation = home_status.annotations.filter(type__slug="efficient-building-air-leakage")

        infiltration_ach = input_values.get("home-infiltration-ach")
        vent_type = input_values.get("home-ventilation-type")
        fan_rating = input_values.get("home-ventilation-fan-rating")
        sensible_heat = input_values.get("home-ventilation-sensible-heat-recovery-rating")

        if not annotation.exists():
            return
        annotation = annotation.get().content.lower()
        errors = []

        def check_infiltration():
            """Level 3 Infiltration check"""
            data_map = {"2a": 3.0, "2b": 2.0, "2c": 1.5}
            if infiltration_ach and float(infiltration_ach) > data_map[annotation]:
                err = "%s requires Air Infiltration <= %s" % (
                    annotation,
                    data_map[annotation],
                )
                errors.append(err)

        def check_fan_rating():
            """Level 3 Fan rating check"""
            if vent_type and vent_type == "High Efficiency Fan":
                if fan_rating and float(fan_rating) < 0.35:
                    err = "%s %s CFM must be >= 0.35" % (annotation, vent_type)
                    errors.append(err)

        def check_sensible_heat_rating():
            """Level 3 Sensible heat recovery rating"""
            data_map = {"2b": 0.70, "2c": 0.85}
            if vent_type and vent_type == "HRV":
                if sensible_heat and float(sensible_heat) < data_map[annotation]:
                    err = "%s %s Sensisble heat rating must be >= %s" % (
                        annotation,
                        vent_type,
                        data_map[annotation],
                    )
                    errors.append(err)

        checks = []
        if annotation == "2a":
            checks.append(check_infiltration)
            checks.append(check_fan_rating)
        elif annotation == "2b":
            checks.append(check_infiltration)
            checks.append(check_sensible_heat_rating)
        elif annotation == "2c":
            checks.append(check_infiltration)
            checks.append(check_sensible_heat_rating)

        if not checks:
            return

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 2 Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Energy Code Option 3 Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_3_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option 3"""
        annotation = home_status.annotations.filter(type__slug="efficient-building-hvac")

        primary_heating = input_values.get("home-primary-heating")
        ashp_hspf = input_values.get("home-ashp-hspf")
        furnace_afue = input_values.get("home-furnace-afue")
        boiler_afue = input_values.get("home-boiler-afue")
        gshp_cop = input_values.get("home-gshp-cop")
        ductless_serving = input_values.get("home-ductless-hp-ele-resistance-serving-largest-zone")

        if not annotation.exists():
            return
        annotation = annotation.get().content.lower()
        errors = []

        def check_ashp_hspf():
            """Level 3 AHSP HSPF check"""
            if primary_heating and primary_heating == "Air Source Heat Pump":
                if ashp_hspf and float(ashp_hspf) < 9.0:
                    err = "%s ASHP HSPF >= 9.0" % annotation
                    errors.append(err)

        def check_furnace_afue():
            """Level 3 Furnace AFUE check"""
            if primary_heating and primary_heating in [
                "Gas Furnace",
                "Propane Furnace",
            ]:
                if furnace_afue and float(furnace_afue) < 94.0:
                    err = "%s %s AFUE >= 94.0" % (annotation, primary_heating)
                    errors.append(err)

        def check_boiler_afue():
            """Level 3 Boiler AFUE check"""
            if primary_heating and primary_heating in ["Gas Boiler", "Propane Boiler"]:
                if boiler_afue and float(boiler_afue) < 92.0:
                    err = "%s %s AFUE >= 92.0" % (annotation, primary_heating)
                    errors.append(err)

        def check_gshp_cop():
            """Level 3 GHSP COP check"""
            if primary_heating and primary_heating == "Ground Source Heat Pump":
                if gshp_cop and float(gshp_cop) < 3.3:
                    err = "%s %s COP >= 3.3" % (annotation, primary_heating)
                    errors.append(err)

        def check_ductless_serving():
            """Level 3 Ductless serving largest zone check"""
            if primary_heating and primary_heating == "Ductless Heat Pump with Electric Resistance":
                if ductless_serving and ductless_serving != "Yes":
                    err = "Ductless Heat Pump servicing the largest zone must be Yes"
                    errors.append(err)

        checks = []
        if annotation == "3a":
            checks.append(check_furnace_afue)
            checks.append(check_boiler_afue)
        elif annotation == "3b":
            checks.append(check_ashp_hspf)
        elif annotation == "3c":
            checks.append(check_gshp_cop)
        elif annotation == "3d":
            checks.append(check_ductless_serving)

        if not checks:
            return

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 3 Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Energy Code Option 4 Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_4_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option 4"""

        annotation = home_status.annotations.filter(
            type__slug="efficient-building-hvac-distribution"
        )
        meet_duct_requirement = input_values.get("meets-wa-code-duct-requirements")
        primary_heating = input_values.get("home-primary-heating")
        duct_location = input_values.get("home-duct-primary-location")
        furnace_afue = input_values.get("home-furnace-afue")
        boiler_afue = input_values.get("home-boiler-afue")

        if not annotation.exists():
            return
        annotation = annotation.get().content.lower()
        errors = []

        def duct_location_check():
            """Level 3 duct location check"""
            if primary_heating and primary_heating in [
                "Gas Furnace",
                "Propane Furnace",
            ]:
                if duct_location and duct_location != "Conditioned Space":
                    err = "%s requires ducts to all be in 'Conditioned Space'"
                    errors.append(err % annotation)

        def meet_requirement():
            """Level 3 Requirements check"""
            if meet_duct_requirement and meet_duct_requirement != "Yes":
                err = "%s requires that all ducts meet energy credit option 4 to be 'Yes'"
                errors.append(err % annotation)

        def check_furnace_afue():
            """Level 3 Furnace AFUE check"""
            if primary_heating and primary_heating in [
                "Gas Furnace",
                "Propane Furnace",
            ]:
                if furnace_afue and float(furnace_afue) < 80.0:
                    err = "%s %s AFUE >= 80.0" % (annotation, primary_heating)
                    errors.append(err)

        def check_boiler_afue():
            """Level 3 Boiler AFUE check"""
            if primary_heating and primary_heating in ["Gas Boiler", "Propane Boiler"]:
                if boiler_afue and float(boiler_afue) < 80.0:
                    err = "%s %s AFUE >= 80.0" % (annotation, primary_heating)
                    errors.append(err)

        checks = []
        if annotation == "4":
            checks.append(duct_location_check)
            checks.append(meet_requirement)
            checks.append(check_furnace_afue)
            checks.append(check_boiler_afue)

        if not checks:
            return

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 4 Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Energy Code Option 5a Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_5a_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option ba"""

        annotation = home_status.annotations.filter(
            type__slug="efficient-building-water-heating-5a"
        )

        showerhead_rate = input_values.get("showerhead-flow-rate")
        faucet_rate = input_values.get("kitchen-faucet-flow-rate")
        bathroom_rate = input_values.get("bathroom-faucet-flow-rate")

        meet_showerhead = input_values.get("meets-wa-code-shower-head-requirements")

        if not annotation.exists():
            return
        annotation = annotation.get().content.lower()
        errors = []

        def showerhead_check():
            """Level 3 Showerhead check"""
            if float(showerhead_rate) > 1.75:
                err = "%s requires showerhead rate GPM < 1.75"
                errors.append(err % annotation)

        def faucet_check():
            """Level 3 faucet check"""
            if float(faucet_rate) > 1.75:
                err = "%s requires kitchen faucet rate GPM < 1.75"
                errors.append(err % annotation)

        def bathroom_check():
            """Level 3 bathroom check"""
            if float(bathroom_rate) > 1.0:
                err = "%s requires bathroom faucent rate GPM < 1.0"
                errors.append(err % annotation)

        def meet_showerhead_requirement():
            """Level 3 showerhead requirements check"""
            if meet_showerhead and meet_showerhead != "Yes":
                err = (
                    "%s requires Meet kitchen, bathroom, and showerheads"
                    " requirements to be 'Yes'"
                )
                errors.append(err % annotation)

        checks = []
        if annotation == "5a":
            if showerhead_rate and showerhead_rate != "Other":
                checks.append(showerhead_check)
            if faucet_rate and faucet_rate != "Other":
                checks.append(faucet_check)
            if bathroom_rate and bathroom_rate != "Other":
                checks.append(bathroom_check)
            checks.append(meet_showerhead_requirement)

        if not checks:
            return

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 5a Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Energy Code Option 5b/c Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_5bc_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option 4"""

        annotation = home_status.annotations.filter(
            type__slug="efficient-building-water-heating-5bc"
        )
        hot_water_type = input_values.get("home-primary-hot-water-type")
        hot_water_gas_ef = input_values.get("home-primary-hot-water-gas-ef")
        hot_water_hp_ef = input_values.get("home-primary-hot-water-hp-ef")

        meets_solar = input_values.get("meets-wa-code-solar-water-requirements")
        meets_neea = input_values.get("meets-neea-hp-requirements")

        primary_heating = input_values.get("home-primary-heating")
        gshp_cop = input_values.get("home-gshp-cop")

        if not annotation.exists():
            return
        annotation = annotation.get().content.lower()
        errors = []

        def check_gshp_cop():
            """Level 3 GHSP COP check"""
            if primary_heating and primary_heating == "Ground Source Heat Pump":
                if gshp_cop and float(gshp_cop) < 3.3:
                    err = "%s %s COP >= 3.3" % (annotation, primary_heating)
                    errors.append(err)

        def gas_hot_water_ef_check():
            """Level 3 duct Gas EF check"""
            data_map = {"5b": 0.74, "5c": 0.91}
            gas_types = ("Gas conventional", "Ground Source Heat Pump", "Gas Tankless")
            if hot_water_type and hot_water_type in gas_types:
                if hot_water_gas_ef and float(hot_water_gas_ef) < data_map[annotation]:
                    err = "%s %s Gas EF must be  >= %s"
                    errors.append(err % (annotation, hot_water_type, data_map[annotation]))

        def hp_hot_water_ef_check():
            """Level 3 duct heat pump EF check"""
            if hot_water_type and hot_water_type == "Heat Pump Water Heater":
                if hot_water_hp_ef and float(hot_water_hp_ef) < 2.0:
                    err = "%s %s Heat Pump EF must be  >= 2.0"
                    errors.append(err % (annotation, hot_water_type))

        def meet_solar_requirement():
            """Level 3 Solar Requirements check"""
            if hot_water_type and hot_water_type == "Solar":
                if meets_solar and meets_solar != "Yes":
                    err = "%s requires Meet Solar energy credit option to be 'Yes'"
                    errors.append(err % annotation)

        def meet_neea_requirement():
            """Level 3 NEEA Requirements check"""
            if hot_water_type and hot_water_type == "Heat Pump Water Heater":
                if meets_neea and meets_neea != "Yes":
                    err = "%s requires Meet NEEA energy credit option to be 'Yes'"
                    errors.append(err % annotation)

        checks = []
        if annotation == "5b":
            checks.append(gas_hot_water_ef_check)
            checks.append(check_gshp_cop)
        elif annotation == "5c":
            checks.append(gas_hot_water_ef_check)
            checks.append(hp_hot_water_ef_check)
            checks.append(meet_solar_requirement)
            checks.append(meet_neea_requirement)

        if not checks:
            return

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 5b/c Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Energy Code Option 5d Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_5d_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option 4"""

        annotation = home_status.annotations.filter(
            type__slug="efficient-building-water-heating-5d"
        )

        meet_dwhr = input_values.get("meets-wa-code-drain-water-requirements")

        if not annotation.exists():
            return
        annotation = annotation.get().content.lower()
        errors = []

        def meet_dwhr_requirement():
            """Level 3 Drain water heat recover check"""
            if meet_dwhr and meet_dwhr != "Yes":
                err = "%s requires Meet Drain water heat requirements to be 'Yes'"
                errors.append(err % annotation)

        checks = []

        if annotation == "5d":
            checks.append(meet_dwhr_requirement)

        if not checks:
            return

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 5d Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Energy Code Option 6 Validations", eep_program=["wa-code-study"])
    def get_wa_code_opt_6_status(self, home_status, input_values, checklist_url, **kwargs):
        """Does all level 3 checks for energy code option 6"""

        annotation = home_status.annotations.filter(
            type__slug="efficient-building-renewable-energy"
        )
        meet_requirements = input_values.get("meets-wa-code-energy-credit-option")

        if not annotation.exists():
            return

        annotation = annotation.get().content.lower()
        if annotation and int(annotation) == 0:
            return
        errors = []

        def meet_requirement():
            """Level 3 Requirements check"""
            if meet_requirements and meet_requirements != "Yes":
                err = (
                    "%s requires renewable energy system meeting the requirements of "
                    "energy credit option to be 'Yes'"
                )
                errors.append(err % annotation)

        checks = [meet_requirement]

        for check in checks:
            check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Energy Credit Option 6 Checks:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=annotation, weight=len(checks), total_weight=len(checks))

    @requirement_test("Bathroom CFM efficacy check", eep_program=["wa-code-study"])
    def get_wa_code_bathroom_status(self, home_status, input_values, checklist_url, **kwargs):
        """Verifies two checklist options"""

        fan_cfm = input_values.get("home-bathroom-fan-cfm")
        fan_efficacy = input_values.get("home-bathroom-fan-efficacy")

        if fan_cfm is None or fan_efficacy is None:
            return

        try:
            fan_cfm = int(fan_cfm)
            fan_efficacy = float(fan_efficacy)
        except TypeError:
            log.error(
                "Unable to convert to values Fan CFM:%s %s Fan Efficacy: %s",
                fan_cfm,
                fan_efficacy,
            )
            return

        err = None
        if 10 < fan_cfm < 90:
            if fan_efficacy < 1.4:
                err = "Bathroom fan efficacy must be less than 1.4 for a fan CFM of %s" % fan_cfm
        if fan_cfm >= 90:
            if fan_efficacy < 2.8:
                err = "Bathroom fan efficacy must be less than 2.8 for a fan CFM of %s" % fan_cfm

        if err:
            return WarningStatusTuple(message=err, url=checklist_url, data=fan_efficacy)
        return PassingStatusTuple(data=fan_efficacy, weight=1, total_weight=1)

    @requirement_test("Mechanical Damper check", eep_program=["wa-code-study"])
    def get_wa_code_damper_status(self, home_status, input_values, checklist_url, **kwargs):
        """Verifies two checklist options"""

        fan_wired = input_values.get("home-ventilation-fan-wired-damper")
        has_ecm = input_values.get("home-primary-heating-has-ecm")

        if fan_wired is None or fan_wired != "Yes":
            return

        err = None
        if has_ecm != "Yes":
            err = "When using a mechanical Damper you must use an ECM"

        if err:
            return WarningStatusTuple(message=err, url=checklist_url, data=has_ecm)
        return PassingStatusTuple(data=has_ecm, weight=1, total_weight=1)

    @requirement_test("Validation Warnings", eep_program=["wa-code-study"])
    def get_wa_code_warning_status(self, home_status, input_values, checklist_url, **kwargs):
        """Verifies two checklist options"""

        lighting = input_values.get("home-lighting-meets-efficacy")
        rated_gasketed = input_values.get("home-recessed-lighting-rated")
        r10_board = input_values.get("home-primary-hot-water-r10-board")

        labels = {
            "home-size": "Home Size",
            "home-foundation-r-value": "Foundation R-Value",
            "home-foundation-slab-depth": "Foundation slab depth",
            "home-below-grade-walls-ext-r-value": "Below grade walls exterior R-value",
            "home-below-grade-walls-int-r-value": "Below grade walls interior R-value",
            "home-below-grade-walls-cavity-r-value": "Below grade walls Cavity R-value",
            "home-floor-r-value": "Floors R-value",
            "home-above-grade-walls-cavity-r-value": "Above grade walls cavity R-value",
            "home-window-u-value": "Window U-Value",
            "home-skylight-u-value": "Skylight U-Value",
            "home-infiltration-ach": "Infiltration ACH",
            "home-bathroom-fan-cfm": "Bathroom Fan CFM",
            "home-ashp-lock-out-temp": "ASHP Lock-Out Temp",
            "home-ashp-hspf": "ASHP HSPF",
            "home-furnace-afue": "Furnace AFUE",
            "home-boiler-afue": "Boiler AFUE",
            "home-duct-r-value": "Duct R-Value",
            "home-primary-hot-water-pipe-r-value": "Primary hot water pipe R-Value",
            "home-duct-leakage-with-air-handler": "Duct Leakage Test with Air Handler",
            "home-duct-leakage-without-air-handler": "Duct Leakage Test without Air Handler",
        }

        errors = []

        def meet_lighting(*_args):
            """Level 3 Requirements check"""
            if lighting and lighting == "No":
                err = "75% of lighting high efficacy has NOT been met"
                errors.append(err)

        def meet_rated_gasketed(*_args):
            """Level 3 Requirements check"""
            if rated_gasketed and rated_gasketed == "No":
                err = "Recessed lighting is NOT ASTM rated or gasketed"
                errors.append(err)

        def meet_r10_board(*_args):
            """Level 3 Requirements check"""
            if r10_board and r10_board == "No":
                err = "R-10 insulation board has NOT been installed"
                errors.append(err)

        def check_min(input_name, value):
            """Check Min Value"""
            input_value = input_values.get(input_name)
            if input_value and float(input_value) < value:
                errors.append("%s is less than minimum value" % labels.get(input_name, input_name))

        def check_max(input_name, value):
            """Check Max Value"""
            input_value = input_values.get(input_name)
            if input_value and float(input_value) > value:
                errors.append(
                    "%s is greater than maximum value" % labels.get(input_name, input_name)
                )

        def check_home(input_name, pct):
            """Check Max value against home size"""
            home_size = input_values.get("home-size")
            input_value = input_values.get(input_name)
            try:
                home_size = float(home_size)
                input_value = float(input_value)
            except TypeError:
                return
            if input_value > home_size * pct:
                errors.append(
                    "%s is greater than maximum value" % labels.get(input_name, input_name)
                )

        checks = [
            meet_lighting,
            meet_rated_gasketed,
            meet_r10_board,
            (check_min, ("home-size", 500)),
            (check_min, ("home-foundation-r-value", 10)),
            (check_min, ("home-foundation-slab-depth", 2)),
            (check_min, ("home-below-grade-walls-ext-r-value", 10)),
            (check_min, ("home-below-grade-walls-int-r-value", 15)),
            (check_min, ("home-below-grade-walls-cavity-r-value", 21)),
            (check_min, ("home-floor-r-value", 30)),
            (check_min, ("home-above-grade-walls-cavity-r-value", 21)),
            (check_max, ("home-window-u-value", Decimal("0.30"))),
            (check_max, ("home-skylight-u-value", Decimal("0.50"))),
            (check_max, ("home-infiltration-ach", Decimal("5.0"))),
            (check_min, ("home-bathroom-fan-cfm", 10)),
            (check_min, ("home-ashp-lock-out-temp", 35)),
            (check_min, ("home-ashp-hspf", Decimal("8.2"))),
            (check_min, ("home-furnace-afue", 80)),
            (check_min, ("home-boiler-afue", 8)),
            (check_min, ("home-duct-r-value", 8)),
            (check_min, ("home-primary-hot-water-pipe-r-value", 3)),
            (check_home, ("home-duct-leakage-with-air-handler", 0.04)),
            (check_home, ("home-duct-leakage-without-air-handler", 0.03)),
        ]

        for check in checks:
            if isinstance(check, (list, tuple)):
                check[0](*check[1])
            else:
                check()

        if errors:
            if len(errors) == 1:
                msg = errors[0]
                message_list = None
            else:
                msg = "Validation Warnings:"
                message_list = """<ul><li>{}</li></ul>""".format("""</li><li>""".join(errors))

            return WarningStatusTuple(
                message=msg,
                data=message_list,
                show_data=bool(message_list),
                weight=len(errors),
                total_weight=len(checks),
                url=checklist_url,
            )

        return PassingStatusTuple(data=None, weight=len(checks), total_weight=len(checks))

    @requirement_test(
        "Verify Gas Utility Company matches Simulation Fuel Rate",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"],
    )
    def get_eto_approved_utility_gas_utility(self, home_status, edit_url, **kwargs):
        return self._verify_approved_utility(
            home_status,
            home_status.get_gas_company(),
            "Gas",
            edit_url,
            home_status.eep_program.slug,
        )

    @requirement_test(
        "Verify Electric Utility Company matches Simulation Fuel Rate",
        eep_program=["eto-2020", "eto-2021", "eto-fire-2021", "eto-2022"],
    )
    def get_eto_approved_utility_electric_utility(self, home_status, edit_url, **kwargs):
        return self._verify_approved_utility(
            home_status,
            home_status.get_electric_company(),
            "Electric",
            edit_url,
            home_status.eep_program.slug,
        )

    @requirement_test("Verify Gas Homes have a utility", eep_program="eto-2020")
    def get_eto_gas_heated_utility_check(self, home_status, input_values, edit_url, **kwargs):
        # Deprecation Notice
        # This is covered by get_eto_revised_primary_heating_fuel_type
        # I don't know of any requirement for ONLY NWN.  They will only pay on these but still.
        home = home_status.home
        primary_heat_type = input_values.get("primary-heating-equipment-type")

        gas_utility = home.get_gas_company()
        if primary_heat_type is None:
            return

        if "gas" in primary_heat_type.lower():
            if gas_utility is None:
                msg = "Gas heated homes must have a gas utility."
                return FailingStatusTuple(data=None, message=msg, url=edit_url)

            if gas_utility.slug not in ["nw-natural-gas", "cascade-gas", "avista"]:
                msg = "Gas heated homes are only supported by NWN, CASCADE, or Avista"
                return FailingStatusTuple(data=None, message=msg, url=edit_url)
            return PassingStatusTuple(data=None, weight=1, total_weight=1)

    @requirement_test("Verify Electric Homes only have PGE or PAC", eep_program="eto-2020")
    def get_eto_electric_heated_utility_check(self, home_status, input_values, edit_url, **kwargs):
        # Deprecation Notice
        # This is covered by get_eto_revised_primary_heating_fuel_type
        # I don't know of any requirement for ONLY these.  They will only pay on these but still.

        home = home_status.home
        primary_heat_type = input_values.get("primary-heating-equipment-type")

        electric_utility = home.get_electric_company()
        if primary_heat_type is None:
            return

        if electric_utility is None:
            msg = "You must have an electric utility."
            return FailingStatusTuple(data=None, message=msg, url=edit_url)

        if "electric" in primary_heat_type.lower():
            if electric_utility.slug not in ["pacific-power", "portland-electric"]:
                msg = "Electrically heated homes are only supported by PAC or PGE"
                return FailingStatusTuple(data=None, message=msg, url=edit_url)
            return PassingStatusTuple(data=None, weight=1, total_weight=1)

    # @requirement_test("Program availability date check", eep_program="neea-bpa")
    # def get_neea_v2_closure_check(self, home_status, edit_url, **_kwargs):
    #     """NEEA V2 has state specific submit / end dates"""
    #
    #     home = home_status.home
    #     if home.state not in ["ID", "WA", "OR"]:
    #         return None
    #
    #     from django.apps import apps
    #
    #     config = apps.get_app_config("customer_neea")
    #
    #     submit_date = config.NEEA_V2_OR_SUBMIT_DATE
    #     certification_date = config.NEEA_V2_OR_CERTIFICATION_DATE
    #
    #     if home.state == "WA":
    #         submit_date = config.NEEA_V2_WA_SUBMIT_DATE
    #         certification_date = config.NEEA_V2_WA_CERTIFICATION_DATE
    #     elif home.state == "ID":
    #         submit_date = config.NEEA_V2_ID_SUBMIT_DATE
    #         certification_date = config.NEEA_V2_OR_CERTIFICATION_DATE
    #
    #     warning_submit_date = submit_date - datetime.timedelta(days=14)
    #     today = datetime.date.today()
    #
    #     if home_status.state == "inspection" and today > submit_date:
    #         submit_str = formats.date_format(submit_date, "SHORT_DATE_FORMAT")
    #         msg = f"{self} in {home.state} cannot be submitted after {submit_str}"
    #         return FailingStatusTuple(data=submit_date, message=msg, url=edit_url)
    #     if home_status.state == "certification_pending" and today > certification_date:
    #         submit_str = formats.date_format(certification_date, "SHORT_DATE_FORMAT")
    #         msg = f"{self} in {home.state} needed to be certified by on {submit_str}.  Shift to V3"
    #         return FailingStatusTuple(data=submit_date, message=msg, url=edit_url)
    #
    #     if today > warning_submit_date:
    #         submit_str = formats.date_format(warning_submit_date, "SHORT_DATE_FORMAT")
    #         msg = f"{self} in {home.state} cannot be submitted after {submit_str}"
    #         return WarningStatusTuple(message=msg, data=warning_submit_date, url=None)
    #
    #     return PassingStatusTuple(data=None, weight=1, total_weight=1)

    @requirement_test("Program availability date check", eep_program="neea-bpa-v3")
    def get_neea_v3_availability_check(self, home_status, edit_url, **kwargs):
        """NEEA V3 has state specific availability dates"""
        home = home_status.home
        if home.state not in ["ID", "WA", "OR"]:
            return None

        from django.apps import apps

        config = apps.get_app_config("customer_neea")

        available_date = config.NEEA_V3_OR_AVAILABLE_DATE
        if home.state == "WA":
            available_date = config.NEEA_V3_WA_AVAILABLE_DATE
        elif home.state == "ID":
            available_date = config.NEEA_V3_ID_AVAILABLE_DATE

        today = kwargs.get("_today", datetime.date.today())
        if today < available_date:
            submit_str = formats.date_format(available_date, "SHORT_DATE_FORMAT")
            msg = f"{self} in {home.state} is not available to submit until {submit_str}"
            return WarningStatusTuple(message=msg, data=available_date, url=edit_url)

        return PassingStatusTuple(data=None, weight=1, total_weight=1)

    @requirement_test(
        "Check Washington Code Credit Incentive", eep_program=["washington-code-credit"]
    )
    def get_wcc_builder_incentive_status(self, home_status, edit_url, **kwargs):
        """Blocks certification calculator is invalid or if no builder incentive"""

        from axis.customer_eto.api_v3.serializers import WashingtonCodeCreditCalculatorSerializer

        serializer = WashingtonCodeCreditCalculatorSerializer(data={"home_status": home_status.id})
        if not serializer.is_valid(raise_exception=False):
            # These are already obvious to the user
            if set(serializer.errors.keys()) == {"annotations", "checklist_questions"}:
                return None
            return FailingStatusTuple(message="Unable to run Calculator", data=None, url=None)

        instance = serializer.save()
        if instance.builder_incentive > 0.0:
            return PassingStatusTuple(data=instance.builder_incentive)

        msg = "Project does not currently qualify for an incentive"
        return FailingStatusTuple(
            data=instance.builder_incentive,
            message=msg,
            url=edit_url,
        )

    @requirement_test(
        "Check EPS Incentive",
        eep_program=[
            "eto-2021",
            "eto-fire-2021",
            "eto-2022",
        ],
    )
    def get_eto_builder_incentive_status(self, home_status, edit_url, **kwargs):
        """Blocks certification calculator is invalid or if no builder incentive"""

        from axis.customer_eto.api_v3.serializers import EPS2021CalculatorSerializer
        from axis.customer_eto.api_v3.serializers import EPSFire2021CalculatorSerializer
        from axis.customer_eto.api_v3.serializers import EPS2022CalculatorSerializer

        serializer_choices = {
            "eto-2021": EPS2021CalculatorSerializer,
            "eto-fire-2021": EPSFire2021CalculatorSerializer,
            "eto-2022": EPS2022CalculatorSerializer,
        }
        serializer_class = serializer_choices.get(home_status.eep_program.slug)

        if home_status.eep_program.slug == "eto-2022" and home_status.home.state == "WA":
            serializer_class = EPS2021CalculatorSerializer

        serializer = serializer_class(data={"home_status": home_status.id})
        if not serializer.is_valid(raise_exception=False):
            # These are already obvious to the user
            if set(serializer.errors.keys()) == {"simulation", "checklist_questions"}:
                return None
            return FailingStatusTuple(message="Unable to run Calculator", data=None, url=None)

        instance = serializer.save()
        if instance.builder_incentive > 0.0:
            return PassingStatusTuple(data=instance.builder_incentive)

        msg = "Project does not currently qualify for an incentive"
        return FailingStatusTuple(
            data=instance.builder_incentive,
            message=msg,
            url=edit_url,
        )

    @requirement_test("Check Fire Rebuild Qualifications", eep_program=["eto-fire-2021"])
    def get_eto_fire_rebuild_checks(self, home_status, edit_url, input_values, **kwargs):
        """Blocks certification calculator is invalid or if no builder incentive"""

        qualified = input_values.get("fire-rebuild-qualification")
        if qualified is not None and qualified != YesNo.YES.value:
            return FailingStatusTuple(
                data=qualified,
                message="Home is not eligible for the program - Must be Fire Rebuild",
                url=edit_url,
            )

        if home_status.home.state != "OR":
            return FailingStatusTuple(
                data=qualified,
                message="Home is not eligible for the program - only OR homes qualify",
                url=edit_url,
            )

        return PassingStatusTuple(data={"state": home_status.home.state, "qualified": qualified})
