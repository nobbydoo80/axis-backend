"""router.py: """

from axis.messaging.api_v3.viewsets import MessageViewSet

__author__ = "Artem Hruzd"
__date__ = "09/30/2020 18:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class MessagingRouter:
    @staticmethod
    def register(router):
        # messaging app
        messaging_router = router.register(r"messages", MessageViewSet, "messages")
