"""router.py: """

__author__ = "Artem Hruzd"
__date__ = "11/19/2021 7:45 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.user_management.api_v3.viewsets import AccreditationViewSet, InspectionGradeViewSet


class UserManagementRouter:
    @staticmethod
    def register(router):
        accreditations_router = router.register(
            r"accreditations",
            AccreditationViewSet,
            "accreditations",
        )

        inspection_grade_router = router.register(
            r"inspection_grades",
            InspectionGradeViewSet,
            "inspection_grades",
        )
