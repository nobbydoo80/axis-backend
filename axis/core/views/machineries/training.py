"""training.py: """

from django.apps import apps

from axis.core.api import UserTrainingViewSet
from axis.core.forms import UserTrainingForm
from axis.examine import PanelMachinery
from axis.user_management.models import Training

__author__ = "Artem Hruzd"
__date__ = "11/28/2019 13:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

user_management_app = apps.get_app_config("user_management")


class UserTrainingExamineMachinery(PanelMachinery):
    model = Training
    form_class = UserTrainingForm
    type_name = "user_training"
    api_provider = UserTrainingViewSet

    regionset_template = "examine/user/training_regionset_panel.html"
    region_template = "examine/user/training_region_panel.html"
    detail_template = "examine/user/training_detail_default.html"

    def get_new_region_endpoint(self):
        request = self.context.get("request", None)
        user = self.context.get("user", None)

        if not request or not user:
            return None

        new_region_endpoint = super(UserTrainingExamineMachinery, self).get_new_region_endpoint()
        if (
            request.user.is_superuser
            or user.company == request.user.company
            or request.user.company.slug in user_management_app.TRAINING_APPLICABLE_COMPANIES_SLUGS
        ):
            return new_region_endpoint
        return None

    def get_region_dependencies(self):
        return {
            "user": [
                {
                    "field_name": "id",
                    "serialize_as": "trainee_id",
                }
            ],
        }
