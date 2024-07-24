"""urls.py: """


from django.urls import path, include

from .views import (
    VerifierAgreementExamineView,
    VerifierAgreementFilterView,
    ActiveVerifierAgreementEnrollmentRedirectView,
    VerifierAgreementInitiateNew,
)

__author__ = "Artem Hruzd"
__date__ = "04/16/2020 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


urlpatterns = [
    path(
        "verifier_agreements/",
        include(
            (
                [
                    path(
                        "enroll/",
                        ActiveVerifierAgreementEnrollmentRedirectView.as_view(),
                        name="enroll",
                    ),
                    path("", VerifierAgreementFilterView.as_view(), name="list"),
                    path(
                        "enroll/create/",
                        VerifierAgreementExamineView.as_view(enrollment_mode=True, create_new=True),
                        name="add",
                    ),
                    path(
                        "<int:pk>/",
                        VerifierAgreementExamineView.as_view(agreement_mode=True),
                        name="examine",
                    ),
                    path(
                        "initiate_new/", VerifierAgreementInitiateNew.as_view(), name="initiate_new"
                    ),
                ],
                "verifier_agreements",
            )
        ),
    ),
]
