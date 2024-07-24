"""inspection_grading.py: """

from django.apps import apps
from django.utils import timezone

from axis.core.api import UserInspectionGradeViewSet
from axis.core.forms import UserInspectionGradeForm
from axis.examine import PanelMachinery
from axis.user_management.models import InspectionGrade

__author__ = "Artem Hruzd"
__date__ = "11/28/2019 15:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

user_management_app = apps.get_app_config("user_management")


class UserInspectionGradeExamineMachinery(PanelMachinery):
    model = InspectionGrade
    form_class = UserInspectionGradeForm
    type_name = "user_inspection_grade"
    api_provider = UserInspectionGradeViewSet

    regionset_template = "examine/user/inspection_grade_regionset.html"
    region_template = "examine/user/inspection_grade_region_panel.html"
    detail_template = "examine/user/inspection_grade_detail_default.html"

    def get_new_region_endpoint(self):
        """
        Allow create inspection grades for superusers
        or company admins for own company if company_type in
        INSPECTION_GRADE_APPLICABLE_COMPANY_TYPES and
        allow non company qa users create grades for raters
        :return: endpoint url to create Inspection Grading or None
        """
        request = self.context.get("request", None)
        user = self.context.get("user", None)

        if not request or not user:
            return None

        new_region_endpoint = super(
            UserInspectionGradeExamineMachinery, self
        ).get_new_region_endpoint()
        if (
            request.user.is_superuser
            or request.user.company.slug
            in user_management_app.INSPECTION_GRADE_APPLICABLE_COMPANIES_SLUGS
            or (
                user.company
                and user.company.company_type == "rater"
                and user.company != request.user.company
                and request.user.company.company_type == "qa"
            )
        ):
            return new_region_endpoint
        return None

    def get_region_dependencies(self):
        return {
            "user": [
                {
                    "field_name": "id",
                    "serialize_as": "user_id",
                }
            ],
        }

    def get_form_kwargs(self, instance):
        kwargs = super(UserInspectionGradeExamineMachinery, self).get_form_kwargs(instance)
        request = self.context.get("request", None)
        kwargs["user"] = request.user
        if instance and not instance.graded_date:
            graded_datetinme = timezone.now()
            if request.user and request.user.timezone_preference:
                graded_datetinme = graded_datetinme.astimezone(request.user.timezone_preference)
            kwargs["initial"] = {"graded_date": graded_datetinme.date()}
        return kwargs

    def get_summary(self):
        summary = super(UserInspectionGradeExamineMachinery, self).get_summary()
        summary["user_full_name"] = self.context["user"].get_full_name()
        return summary
