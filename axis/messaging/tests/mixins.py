"""fixturecompilers.py: """


from axis.company.tests.factories import (
    rater_organization_factory,
    provider_organization_factory,
)
from axis.core.tests.factories import (
    rater_admin_factory,
    rater_user_factory,
    provider_admin_factory,
    provider_user_factory,
    general_super_user_factory,
)
from axis.messaging.tests.factories import message_factory, messaging_preference_factory

__author__ = "Artem Hruzd"
__date__ = "05/20/2020 19:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class MessagingTestMixin:
    @classmethod
    def setUpTestData(cls):
        momentum_company = rater_organization_factory(name="momentum")
        rater_admin = rater_admin_factory(company=momentum_company)
        rater_common_user = rater_user_factory(company=momentum_company)

        energy_inspector_company = provider_organization_factory(name="energy_inspector")
        provider_admin = provider_admin_factory(company=energy_inspector_company)
        provider_common_user = provider_user_factory(company=energy_inspector_company)

        superuser = general_super_user_factory()

        # create few default messages for every user
        for user in [
            rater_admin,
            rater_common_user,
            provider_admin,
            provider_common_user,
            superuser,
        ]:
            message_factory(user=user, level="debug", alert_read=False)
            message_factory(user=user, level="info", email_read=False)
            message_factory(user=user, level="warning", alert_read=True, email_read=True)
            message_factory(user=user, level="error", alert_read=False, email_read=False)

            messaging_preference_factory(user=user, message_name="AxisCommonMessage")
            messaging_preference_factory(user=user, message_name="AxisRequiredMessage")
            messaging_preference_factory(user=user, message_name="AxisCompanyTypeMessage")
            messaging_preference_factory(user=user, message_name="AxisCompanySlugMessage")

        # create few messages that sent from superuser
        for user in [
            rater_admin,
            rater_common_user,
            provider_admin,
            provider_common_user,
        ]:
            message_factory(
                user=user,
                sender=superuser,
                level="info",
                alert_read=False,
                email_read=False,
            )
            message_factory(
                user=user,
                sender=superuser,
                level="error",
                alert_read=True,
                email_read=False,
            )
            message_factory(
                user=user,
                sender=superuser,
                level="warning",
                alert_read=False,
                email_read=True,
            )
