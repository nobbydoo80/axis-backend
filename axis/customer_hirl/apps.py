__author__ = "Autumn Valenta"
__date__ = "10/10/2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

from django.conf import settings
from django.contrib.auth import get_user_model

from axis.core import customers
from infrastructure.utils import symbol_by_name
from .builder_agreements import BuilderEnrollmentConfig
from .verifier_agreements import VerifierEnrollmentConfig

settings = getattr(settings, "CUSTOMER_HIRL", {})


class ProjectConfig(customers.ExtensionConfig):
    """NGBS Project platform config"""

    HIRL_PROJECT_ENABLED = settings.get("HIRL_PROJECT_ENABLED", False)

    LAND_DEVELOPMENT_PROGRAM_LIST = [
        "ngbs-land-development-2020-new",
    ]

    HIRL_PROJECT_EEP_PROGRAM_MF_NEW_CONSTRUCTION_SLUGS = [
        "ngbs-mf-new-construction-2020-new",
        "ngbs-mf-new-construction-2015-new",
        "ngbs-mf-new-construction-2012-new",
    ]

    HIRL_PROJECT_EEP_PROGRAM_SF_NEW_CONSTRUCTION_SLUGS = [
        "ngbs-sf-new-construction-2020-new",
        "ngbs-sf-new-construction-2015-new",
        "ngbs-sf-new-construction-2012-new",
    ]

    HIRL_PROJECT_EEP_PROGRAM_MF_REMODEL_SLUGS = [
        "ngbs-mf-whole-house-remodel-2020-new",
        "ngbs-mf-whole-house-remodel-2015-new",
        "ngbs-mf-whole-house-remodel-2012-new",
    ]

    HIRL_PROJECT_EEP_PROGRAM_SF_REMODEL_SLUGS = [
        "ngbs-sf-whole-house-remodel-2020-new",
        "ngbs-sf-whole-house-remodel-2015-new",
        "ngbs-sf-whole-house-remodel-2012-new",
    ]

    HIRL_PROJECT_EEP_PROGRAM_WRI_SF_SLUGS = [
        "ngbs-sf-wri-2021",
    ]

    HIRL_PROJECT_EEP_PROGRAM_WRI_MF_SLUGS = [
        "ngbs-mf-wri-2021",
    ]

    WRI_PROGRAM_LIST = HIRL_PROJECT_EEP_PROGRAM_WRI_SF_SLUGS + HIRL_PROJECT_EEP_PROGRAM_WRI_MF_SLUGS

    HIRL_PROJECT_EEP_PROGRAM_SF_CERTIFIED_SLUGS = [
        "ngbs-sf-certified-2020-new",
    ]

    # Settings
    HIRL_PROJECT_EEP_PROGRAM_SLUGS = (
        HIRL_PROJECT_EEP_PROGRAM_SF_CERTIFIED_SLUGS
        + HIRL_PROJECT_EEP_PROGRAM_SF_NEW_CONSTRUCTION_SLUGS
        + HIRL_PROJECT_EEP_PROGRAM_MF_NEW_CONSTRUCTION_SLUGS
        + HIRL_PROJECT_EEP_PROGRAM_MF_REMODEL_SLUGS
        + HIRL_PROJECT_EEP_PROGRAM_SF_REMODEL_SLUGS
        + WRI_PROGRAM_LIST
        + LAND_DEVELOPMENT_PROGRAM_LIST
    )

    HIRL_PROJECT_LEGACY_EEP_PROGRAM_SLUGS = [
        "ngbs-sf-certified-2020",
        "ngbs-mf-new-construction-2020",
        "ngbs-green-subdivision-2020",
        "ngbs-sf-new-construction-2020",
        "ngbs-sf-whole-house-remodel-2020",
        "ngbs-mf-remodel-building-2020",
        "ngbs-mf-new-construction-2015",
        "ngbs-mf-remodel-building-2015",
        "ngbs-sf-whole-house-remodel-2015",
        "ngbs-sf-new-construction-2015",
        "ngbs-mf-new-construction-2012",
        "ngbs-sf-new-construction-2012",
        "ngbs-mf-remodel-building-2012",
        "ngbs-sf-whole-house-remodel-2012",
        "ngbs-mf-whole-house-remodel-2012",
        "ngbs-single-family-new-construction",
        "ngbs-multi-unit-new-construction",
    ]

    # Invoice fee constants
    ACCESSORY_STRUCTURE_SEEKING_CERTIFICATION_FEE = 150
    ACCESSORY_DWELLING_UNIT_STRUCTURE_CERTIFICATION_FEE = 0
    COMMERCIAL_SPACE_CORE_AND_SHELL_CERTIFICATION_FEE = 500
    COMMERCIAL_SPACE_FULL_FITTED_CERTIFICATION_FEE = 1000

    MAX_APPEALS_FEE_PER_REGISTRATION = 10000
    DEFAULT_APPEALS_FEE_LABEL = "Appeals Fees"
    DEFAULT_APPEALS_SINGLE_FAMILY_FEE = 500
    DEFAULT_APPEALS_MULTI_FAMILY_FEE = 1000
    DEFAULT_APPEALS_ACCESSORY_STRUCTURE_FEE = 500
    DEFAULT_APPEALS_DWELLING_UNIT_STRUCTURE_FEE = 500
    DEFAULT_APPEALS_COMMERCIAL_SPACE_FEE = 0

    DEFAULT_LAND_DEVELOPMENT_ALL_HOMES_SEEKING_CERTIFICATION_FEE = 0

    DEFAULT_LAND_DEVELOPMENT_CERTIFICATION_FEE = 4000
    DEFAULT_LAND_DEVELOPMENT_MORE_THAN_100_LOTS_CERTIFICATION_FEE = 6500

    DEFAULT_LAND_DEVELOPMENT_LETTER_OF_APPROVAL_CERTIFICATION_FEE = 2500

    DEFAULT_LOA_FEE_LABEL = "Letter Of Approval Fees"

    MF_VOLUME_DISCOUNT_9_BUILDINGS_FEE = 200
    MF_VOLUME_DISCOUNT_20_BUILDINGS_FEE = 150
    MF_VOLUME_DISCOUNT_50_BUILDINGS_FEE = 125

    BUILD_TO_RENT_FEE = 125

    WATER_SENSE_PROGRAM_LIST = [
        "ngbs-sf-new-construction-2020-new",
        "ngbs-mf-new-construction-2020-new",
        "ngbs-sf-whole-house-remodel-2020-new",
        "ngbs-mf-whole-house-remodel-2020-new",
        "ngbs-sf-certified-2020-new",
    ]

    WRI_SEEKING_PROGRAM_LIST = [
        "ngbs-sf-new-construction-2020-new",
        "ngbs-mf-new-construction-2020-new",
        "ngbs-sf-certified-2020-new",
    ]

    REQUIRE_ROUGH_INSPECTION_PROGRAM_LIST = [
        "ngbs-sf-whole-house-remodel-2020-new",
        "ngbs-mf-whole-house-remodel-2020-new",
        "ngbs-sf-whole-house-remodel-2015-new",
        "ngbs-mf-whole-house-remodel-2015-new",
    ]

    # This is a number represent last legacy NGBS certificate
    # Seed NGBS certification counter for certificates at 28476
    # (that should be the first certificate number
    # assigned for any NGBS project certified within AXIS)
    LEGACY_PROJECT_CERTIFICATION_COUNTER = 28475


class CustomerHIRLConfig(customers.CustomerAppConfig):
    """Customer HIRL configuration.

    Uses: Builder Enrollment
    """

    name = "axis.customer_hirl"
    CUSTOMER_SLUG = "provider-home-innovation-research-labs"

    # NGBS database program name as key and AXIS Program slug as value
    NGBS_PROGRAM_NAMES = {
        "2012 Basement  Remodel": "ngbs-basement-remodel-2012",
        "2012 Bathroom Remodel": "ngbs-bathroom-remodel-2012",
        "2012 Green Subdivision": "ngbs-green-subdivision-2012",
        "2012 Kitchen Remodel": "ngbs-kitchen-remodel-2012",
        "2012 MF New Construction": "ngbs-mf-new-construction-2012",
        "2012 MF Remodel Building": "ngbs-mf-remodel-building-2012",
        "2012 SF New Construction": "ngbs-sf-new-construction-2012",
        "2012 SF Whole House Remodel": "ngbs-sf-whole-house-remodel-2012",
        "2012 Small Addition": "ngbs-small-addition-2012",
        "2015 MF New Construction": "ngbs-mf-new-construction-2015",
        "2015 SF New Construction": "ngbs-sf-new-construction-2015",
        "Green Building Renovations with Additions < 75%": "ngbs-green-building-renovations-with-additions-75",
        "Green Remodel Renovations with Additions < 75%": "ngbs-green-remodel-renovations-with-additions-75",
        "Green Subdivision": "ngbs-green-subdivision",
        "Multi-Unit  Green Building Renovation": "ngbs-multi-unit-green-building-renovation",
        "Multi-Unit Green Remodel Renovation": "ngbs-multi-unit-green-remodel-renovation",
        "Multi-Unit New Construction": "ngbs-multi-unit-new-construction",
        "Renovations with Addition >= 75%": "ngbs-renovations-with-addition-75",
        "Single-Family Additions < 75%": "ngbs-single-family-additions-75-1",
        "Single-Family Additions >= 75%": "ngbs-single-family-additions-75-2",
        "Single-Family Green Building Renovation": "ngbs-single-family-green-building-renovation",
        "Single-Family Green Remodel Renovation": "ngbs-single-family-green-remodel-renovation",
        "Single-Family New Construction": "ngbs-single-family-new-construction",
        "2015 MF Remodel Building": "ngbs-mf-remodel-building-2015",
        "2015 SF Kitchen Remodel": "ngbs-sf-kitchen-remodel-2015",
        "2015 SF Whole House Remodel": "ngbs-sf-whole-house-remodel-2015",
        "2020 MF New Construction": "ngbs-mf-new-construction-2020",
        "2020 SF New Construction": "ngbs-sf-new-construction-2020",
        "2020 SF Whole House Remodel": "ngbs-sf-whole-house-remodel-2020",
        "2020 Green Subdivision": "ngbs-green-subdivision-2020",
        "2020 MF Remodel Building": "ngbs-mf-remodel-building-2020",
        "2020 SF Certified Path": "ngbs-sf-certified-2020",
    }

    REMODEL_PROGRAMS = [
        "ngbs-basement-remodel-2012",
        "ngbs-bathroom-remodel-2012",
        "ngbs-kitchen-remodel-2012",
        "ngbs-mf-remodel-building-2012",
        "ngbs-sf-whole-house-remodel-2012",
        "ngbs-small-addition-2012",
        "ngbs-mf-remodel-building-2015",
        # Missing 2015 Bathroom Remodel
        "ngbs-sf-kitchen-remodel-2015",
        # Missing 2015 Small Addition
        "ngbs-sf-whole-house-remodel-2015",
        "ngbs-sf-whole-house-remodel-2020",
        "ngbs-green-building-renovations-with-additions-75",
        "ngbs-green-remodel-renovations-with-additions-75",
        "ngbs-multi-unit-green-building-renovation",
        "ngbs-multi-unit-green-remodel-renovation",
        "ngbs-single-family-additions-75-1",
        "ngbs-single-family-green-building-renovation",
        "ngbs-single-family-green-remodel-renovation",
        # NOT LISTED in the original document TODO CONFIRM THESE BELONG HERE
        "ngbs-mf-whole-house-remodel-2012-new",
        "ngbs-sf-whole-house-remodel-2012-new",
        "ngbs-mf-whole-house-remodel-2015-new",
        "ngbs-sf-whole-house-remodel-2015-new",
        "ngbs-mf-whole-house-remodel-2020-new",
        "ngbs-sf-whole-house-remodel-2020-new",
        "ngbs-mf-remodel-building-2020",
    ]

    GREEN_SUBDIVISION_PROGRAMS = [
        "ngbs-green-subdivision",
        "ngbs-green-subdivision-2012",
        "ngbs-green-subdivision-2020",
    ]

    # url to verifier resources FlatPage for HIRL customer
    VERIFIER_RESOURCES_PAGE_URL = "/verifier/resources/"
    BUILDER_CENTRAL_PAGE_URL = "/builder/central/"

    # Until we go live leave as None
    # When we go live all of the envelopes will need to be bulk moved to this users account
    DOCUSIGN_USER_ID = "8c33bf6e-80bc-4270-981a-fdf3d647ddba"
    DOCUSIGN_ACCOUNT_ID = "8119ce76-e875-42eb-af24-b358bcb955f1"
    # For beta and local Docusign testing
    # DOCUSIGN_USER_ID = None
    # DOCUSIGN_ACCOUNT_ID = None

    extensions = customers.CustomerAppConfig.extensions + (
        BuilderEnrollmentConfig,
        VerifierEnrollmentConfig,
        ProjectConfig,
    )

    def get_customer_hirl_provider_organization(self):
        from axis.company.models import Company

        return Company.objects.get(slug=self.CUSTOMER_SLUG)

    def get_accounting_users(self):
        """
        Special NGBS Users that have extra permissions and notifications
        for some Invoicing actions
        :return: list of User objects
        """
        user_model = get_user_model()
        return user_model.objects.filter(
            email__in=[
                "lmarchman@homeinnovation.com",
                "khall@homeinnovation.com",
                "cwasser@homeinnovation.com",
                "kjerald@homeinnovation.com",
                "rburns@pivotalenergysolutions.com",
                "mgozum@homeinnovation.com",
            ],
            company__slug=self.CUSTOMER_SLUG,
        )

    @property
    def eep_programs(self):
        """Supported programs for program builder"""
        return [
            symbol_by_name(f"{self.name}.eep_programs:NGBS2015MFRemodelBuildingLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2015KitchenRemodelLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2015SFWholeHouseRemodelLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2020GreenSubdivisionLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2020MFNewConstructionLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2020MFRemodelLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2020SFCertifiedlLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2020SFNewConstructionLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBS2020SFWholeHouseRemodelLegacy"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSMFNewConstruction2012"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSMFNewConstruction2015"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSMFNewConstruction2020"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSMFWholeHouseRemodel2012"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSMFWholeHouseRemodel2015"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSMFWholeHouseRemodel2020"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFCertified2020"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFNewConstruction2012"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFNewConstruction2015"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFNewConstruction2020"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFWholeHouseRemodel2012"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFWholeHouseRemodel2015"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFWholeHouseRemodel2020"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSSFWRI2021"),
            symbol_by_name(f"{self.name}.eep_programs:NGBSMFWRI2021"),
        ]
