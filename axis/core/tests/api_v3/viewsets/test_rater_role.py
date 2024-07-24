"""test_rater_role.py: """

__author__ = "Artem Hruzd"
__date__ = "05/11/2022 17:13"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.urls import reverse_lazy

from axis.core.models import RaterRole
from axis.core.tests.factories import rater_user_factory
from axis.core.tests.testcases import ApiV3Tests


class TestRaterRoleViewset(ApiV3Tests):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.energy_modeler_rater_role = RaterRole.objects.create(
            title="Energy Modeler", slug="energy_modeler_rater_role", is_hidden=False
        )
        cls.verifier_rater_role = RaterRole.objects.create(
            title="Energy Modeler", slug="verifier_rater_role", is_hidden=False
        )
        cls.qa_rater_role = RaterRole.objects.create(
            title="Energy Modeler", slug="qa_rater_role", is_hidden=False
        )

    def test_list(self):
        rater_user = rater_user_factory()
        rater_user.rater_roles.add(self.energy_modeler_rater_role)

        url = reverse_lazy("api_v3:rater_roles-list")

        data = self.list(url=url, user=rater_user)
        self.assertEqual(len(data), RaterRole.objects.count())

        with self.subTest("Filter by user id"):
            url = f"{url}?user={rater_user.id}"
            data = self.list(url=url, user=rater_user)
            self.assertEqual(len(data), rater_user.rater_roles.all().count())
