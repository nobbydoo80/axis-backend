"""apps.py: """


from dateutil.relativedelta import relativedelta
from django.conf import settings

from axis.core.platform import PlatformAppConfig

__author__ = "Artem Hruzd"
__date__ = "11/28/2019 14:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


user_management_settings = getattr(settings, "USER_MANAGEMENT", {})


class UserManagementTrainingConfig(PlatformAppConfig):
    """Training platform config"""

    # Make sure that you will run track_training_statuses
    # management command after you modify this requirements
    TRAINING_APPLICABLE_REQUIREMENTS = user_management_settings.get(
        "TRAINING_APPLICABLE_REQUIREMENTS",
        {
            "provider-washington-state-university-extension-ene": [
                "wsu-hers-2020",
            ],
            "provider-home-innovation-research-labs": [
                "ngbs-sf-new-construction-2020-new",
                "ngbs-sf-new-construction-2020",
                "ngbs-mf-new-construction-2020",
                "ngbs-sf-new-construction-2015-new",
            ],
        },
    )
    TRAINING_APPLICABLE_PROGRAMS = sorted(
        {x for v in TRAINING_APPLICABLE_REQUIREMENTS.values() for x in v}
    )
    TRAINING_APPLICABLE_COMPANIES_SLUGS = list(TRAINING_APPLICABLE_REQUIREMENTS.keys())

    # date from training date when training status state will set to expire
    TRAINING_CYCLE = user_management_settings.get("TRAINING_CYCLE", relativedelta(years=3))


class UserManagementAccreditationConfig(PlatformAppConfig):
    """Accreditation platform config"""

    ACCREDITATION_APPLICABLE_COMPANIES_SLUGS = [
        "provider-washington-state-university-extension-ene",
        "provider-home-innovation-research-labs",
    ]


class UserManagementCertificationMetricConfig(PlatformAppConfig):
    """Certification metric platform config"""

    CERTIFICATION_METRIC_APPLICABLE_COMPANIES_SLUGS = [
        "provider-washington-state-university-extension-ene",
        "provider-home-innovation-research-labs",
    ]


class UserManagementInspectionGradeConfig(PlatformAppConfig):
    """Inspection grade platform config"""

    INSPECTION_GRADE_APPLICABLE_COMPANIES_SLUGS = [
        "provider-washington-state-university-extension-ene",
        "provider-home-innovation-research-labs",
    ]


class UserManagementConfig(PlatformAppConfig):
    """User Management platform config"""

    name = "axis.user_management"

    extensions = PlatformAppConfig.extensions + (
        UserManagementTrainingConfig,
        UserManagementAccreditationConfig,
        UserManagementCertificationMetricConfig,
        UserManagementInspectionGradeConfig,
    )
