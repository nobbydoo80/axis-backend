"""frontend_logger.py"""

from django.urls import reverse_lazy

from axis.core.tests.factories import rater_user_factory
from axis.core.tests.testcases import ApiV3Tests

__author__ = "Rajesh Pethe"
__date__ = "07/01/2020 14:16"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Rajesh Pethe",
    "Steven Klass",
]


class TestFrontendLoggerViewSet(ApiV3Tests):
    def test_logger_as_anonymous_user(self):
        url = reverse_lazy("api_v3:frontend_logger-list")

        with self.assertLogs(
            logger="axis.core.api_v3.serializers.frontend_log", level="CRITICAL"
        ) as cm:
            _ = self.create(
                url=url,
                user=None,
                data={"level": "CRITICAL", "msg": "Test CRITICAL message", "extra": {}},
            )
            self.assertIn(
                "CRITICAL:"
                "axis.core.api_v3.serializers.frontend_log:"
                "Frontend message: User AnonymousUser "
                "Message: Test CRITICAL message Extra: {}",
                cm.output,
            )

    def test_logger_as_rater_user(self):
        rater_user = rater_user_factory()
        url = reverse_lazy("api_v3:frontend_logger-list")

        with self.assertLogs(
            logger="axis.core.api_v3.serializers.frontend_log", level="CRITICAL"
        ) as cm:
            _ = self.create(
                url=url,
                user=rater_user,
                data={"level": "CRITICAL", "msg": "Test CRITICAL message", "extra": {}},
            )
            self.assertIn(
                f"CRITICAL:"
                f"axis.core.api_v3.serializers.frontend_log:"
                f"Frontend message: User {rater_user} "
                f"Message: Test CRITICAL message Extra: {{}}",
                cm.output,
            )
