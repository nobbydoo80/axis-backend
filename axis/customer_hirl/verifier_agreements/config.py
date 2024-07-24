"""config.py: """


from django.conf import settings

from axis.core import customers

__author__ = "Artem Hruzd"
__date__ = "04/16/2020 16:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


settings = getattr(settings, "CUSTOMER_HIRL", {})


# pylint: disable=invalid-name
class VerifierEnrollmentConfig(customers.ExtensionConfig):
    """NGBS Builder Enrollment platform config"""

    VERIFIER_AGREEMENT_ENROLLMENT_ENABLED = settings.get(
        "VERIFIER_AGREEMENT_ENROLLMENT_ENABLED", False
    )

    # Configuration
    VERIFIER_AGREEMENT_COUNTER_SIGNING_USERNAME = settings.get(
        "VERIFIER_AGREEMENT_COUNTER_SIGNING_USERNAME", "NGBSadmin1"
    )
