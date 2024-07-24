"""user.py: """


from django.apps import apps
from django.contrib.auth import get_user_model
from django.urls import reverse

from axis.examine import PrimaryMachinery
from axis.core.api import UserViewSet
from axis.core.forms import UserChangeForm, BaseUserChangeForm

__author__ = "Artem Hruzd"
__date__ = "11/20/2019 16:06"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


User = get_user_model()
customer_hirl_app = apps.get_app_config("customer_hirl")


class UserExamineMachinery(PrimaryMachinery):
    model = User
    form_class = UserChangeForm
    api_provider = UserViewSet
    type_name = "user"

    detail_template = "examine/user/user_detail.html"
    form_template = "examine/user/user_form.html"

    can_add_new = False

    def get_form_class(self):
        request = self.context.get("request")
        if request and (
            request.user.is_superuser
            or request.user == self.instance
            or (request.user.is_company_admin and request.user.company == self.instance.company)
        ):
            return UserChangeForm
        return BaseUserChangeForm

    def get_default_actions(self, instance):
        """Return default actions with contextual additions"""

        actions = super(UserExamineMachinery, self).get_default_actions(instance)

        if (
            self.context.get("request").user.is_superuser
            or self.context.get("request").user == self.instance
        ):
            actions.insert(
                0,
                self.Action(
                    "Change password",
                    instruction=None,
                    href=reverse("password_change"),
                    type="link",
                    is_mode=True,
                ),
            )

        return actions
