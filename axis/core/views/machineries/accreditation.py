"""accreditation.py: """

__author__ = "Artem Hruzd"
__date__ = "11/28/2019 15:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from rest_framework.reverse import reverse_lazy

from axis.core.api import UserAccreditationViewSet
from axis.core.forms import UserAccreditationForm
from axis.examine import PanelMachinery
from axis.user_management.models import Accreditation

customer_hirl_app = apps.get_app_config("customer_hirl")
user_management_app = apps.get_app_config("user_management")


class UserAccreditationExamineMachinery(PanelMachinery):
    model = Accreditation
    form_class = UserAccreditationForm
    type_name = "user_accreditation"
    api_provider = UserAccreditationViewSet

    regionset_template = "examine/user/accreditation_regionset_panel.html"
    region_template = "examine/user/accreditation_region_panel.html"
    detail_template = "examine/user/accreditation_detail_default.html"

    def get_new_region_endpoint(self):
        if (
            self.context["request"].user.is_superuser
            or self.context["request"].user.company.slug
            in user_management_app.ACCREDITATION_APPLICABLE_COMPANIES_SLUGS
        ):
            return super(UserAccreditationExamineMachinery, self).get_new_region_endpoint()
        return None

    def get_form_kwargs(self, instance):
        kwargs = super(UserAccreditationExamineMachinery, self).get_form_kwargs(instance)
        kwargs["company"] = self.context["request"].user.company
        return kwargs

    def get_region_dependencies(self):
        return {
            "user": [
                {
                    "field_name": "id",
                    "serialize_as": "trainee_id",
                }
            ],
        }

    def get_static_actions(self, instance):
        actions = super(UserAccreditationExamineMachinery, self).get_static_actions(instance)

        user = self.context["request"].user
        if instance.pk and user:
            if (
                user.is_superuser
                or instance.trainee == user
                or (
                    instance.approver.company
                    and instance.approver.company.slug == customer_hirl_app.CUSTOMER_SLUG
                )
            ):
                if instance.name in [
                    Accreditation.MASTER_VERIFIER_NAME,
                    Accreditation.NGBS_2020_NAME,
                    Accreditation.NGBS_2015_NAME,
                    Accreditation.NGBS_2012_NAME,
                    Accreditation.NGBS_GREEN_FIELD_REP_NAME,
                    Accreditation.NGBS_WRI_VERIFIER_NAME,
                ]:
                    if not instance.is_expired() and instance.state in [
                        Accreditation.PROBATION_NEW_STATE,
                        Accreditation.ACTIVE_STATE,
                        Accreditation.PROBATION_DISCIPLINARY_STATE,
                    ]:
                        actions.append(
                            self.Action(
                                "Generate certificate",
                                icon="file",
                                style="primary",
                                instruction=None,
                                type="link",
                                attrs={"target": "_blank"},
                                href=reverse_lazy(
                                    "api_v3:accreditations-generate-certificate",
                                    kwargs={"pk": instance.pk},
                                ),
                            )
                        )
        return actions
