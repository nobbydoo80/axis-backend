__author__ = "Artem Hruzd"
__date__ = "09/30/2020 17:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from axis.core.api_v3.viewsets import (
    UserViewSet,
    UserNestedHistoryViewSet,
    MetricsViewSet,
    FlatpageViewSet,
    FrontendLoggerViewSet,
    ContactCardViewSet,
    ZendeskViewSet,
    RaterRoleViewSet,
    CeleryTaskViewSet,
)
from axis.customer_hirl.api_v3.viewsets.verifier_agreement import NestedVerifierAgreementViewSet
from axis.messaging.api_v3.viewsets import (
    NestedMessageViewSet,
    NestedMessagingPreferenceViewSet,
    NestedDigestPreferenceViewSet,
)
from axis.user_management.api_v3.viewsets import NestedAccreditationViewSet


class CoreRouter:
    @staticmethod
    def register(router):
        # users
        users_router = router.register(r"users", UserViewSet, "users")
        # messaging
        users_router.register(
            r"messages",
            NestedMessageViewSet,
            "user-messages",
            parents_query_lookups=[
                "user_id",
            ],
        )
        users_router.register(
            r"messaging_preference",
            NestedMessagingPreferenceViewSet,
            "user-messaging_preference",
            parents_query_lookups=[
                "user_id",
            ],
        )
        users_router.register(
            r"digest_preference",
            NestedDigestPreferenceViewSet,
            "user-digest_preference",
            parents_query_lookups=[
                "user_id",
            ],
        )

        # user_management
        users_router.register(
            r"accreditations",
            NestedAccreditationViewSet,
            "user-accreditations",
            parents_query_lookups=[
                "trainee_id",
            ],
        )

        users_router.register(
            r"verifier_agreements",
            NestedVerifierAgreementViewSet,
            "user-verifier_agreements",
            parents_query_lookups=[
                "verifier_id",
            ],
        )

        users_router.register(
            r"history", UserNestedHistoryViewSet, "user-history", parents_query_lookups=["id"]
        )
        # stats
        router.register(r"stats", MetricsViewSet, "stats")
        router.register(r"flatpages", FlatpageViewSet, "flatpages")
        # frontend logging
        router.register(r"frontend_logger", FrontendLoggerViewSet, r"frontend_logger")

        router.register(r"contact_cards", ContactCardViewSet, "contact_cards")

        router.register(r"zendesk", ZendeskViewSet, "zendesk")
        router.register(r"task", CeleryTaskViewSet, "task")

        router.register(
            "rater_roles",
            RaterRoleViewSet,
            "rater_roles",
        )
