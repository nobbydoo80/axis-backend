__author__ = "Artem Hruzd"
__date__ = "05/24/2021 6:54 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from .project import HIRLProjectAdmin, HIRLGreenEnergyBadgeAdmin, HIRLProjectRegistrationAdmin
from .verifier_agreement import VerifierAgreementAdmin, ProvidedServiceAdmin
from .admin import (
    HIRLBuilderOrganizationAdmin,
    HIRLRaterOrganizationAdmin,
    HIRLRaterUserAdmin,
    HIRLBuilderAgreementStatusTabularInlineAdmin,
    HIRLBuilderAgreementStatusAdmin,
    HIRLVerifierAgreementStatusAdmin,
    HIRLBuilderInsuranceTabularInlineAdmin,
    HIRLBuilderInsuranceAdmin,
    HIRLVerifierInsuranceAdmin,
    HIRLVerifierAccreditationStatusAdmin,
    HIRLProjectContactAdmin,
    HIRLProjectArchitectAdmin,
    HIRLProjectOwnerAdmin,
    HIRLProjectDeveloperAdmin,
)
from .builder_agreement import BuilderAgreementAdmin
from .certification import HIRLLegacyCertificationAdmin
from .client import HIRLCompanyClientAdmin
