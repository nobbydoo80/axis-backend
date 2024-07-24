from unittest.mock import patch

from django.test import TestCase

from axis.core.tests.client import AxisClient
from axis.core.tests.factories import provider_admin_factory, rater_admin_factory
from axis.home.tests.factories import certified_custom_home_with_basic_eep_factory
from ..views.examine import user_can_submit_to_resnet_registry

__author__ = "Michael Jeffrey"
__date__ = "3/6/17 10:19 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


# We're not building out simulation data, but we still want to certify homes that 'require' it.
@patch(
    "axis.home.models.EEPProgramHomeStatus.get_model_data_status", return_value=None, autospec=True
)
class RESNETTests(TestCase):
    client_class = AxisClient

    def get_hers_based_home_status(self, certify, company=None, rater_of_record=None):
        kwargs = {"certify": certify, "eep_program__require_rem_data": True}
        if company:
            kwargs["company"] = company
        if rater_of_record:
            kwargs["rater_of_record"] = rater_of_record

        return certified_custom_home_with_basic_eep_factory(**kwargs)

    def get_non_hers_based_home_status(self, certify, company, rater_of_record=None):
        kwargs = {"certify": certify}
        if company:
            kwargs["company"] = company
        if rater_of_record:
            kwargs["rater_of_record"] = rater_of_record
        return certified_custom_home_with_basic_eep_factory(**kwargs)

    def get_rater(self, rater_id=True):
        return rater_admin_factory(rater_id="123456" if rater_id else None)

    def no_rater_id(self, user):
        user.rater_id = None
        user.save()
        return user

    def test_uncertified_home_cannot_submit_to_registry(self, *args):
        provider_user = provider_admin_factory()
        uncertified_home_stat = self.get_hers_based_home_status(False, provider_user.company)

        self.assertEqual(
            user_can_submit_to_resnet_registry(uncertified_home_stat, provider_user), False
        )

    def test_certified_home_no_rater_of_record_cannot_submit_to_registry(self, *args):
        provider_user = provider_admin_factory()
        certified_home_stat = self.get_hers_based_home_status(True, provider_user.company)
        certified_home_stat.rater_of_record = None
        certified_home_stat.save()
        self.assertEqual(
            user_can_submit_to_resnet_registry(certified_home_stat, provider_user), False
        )

    def test_certified_home_rater_of_record_no_rater_id_cannot_submit_to_registry(self, *args):
        provider_user = provider_admin_factory()
        rater_user = self.get_rater(rater_id=False)
        certified_home_stat = self.get_hers_based_home_status(
            True, provider_user.company, rater_user
        )

        self.assertEqual(
            user_can_submit_to_resnet_registry(certified_home_stat, provider_user), False
        )

    def test_certified_home_rater_of_record_rater_id_non_hers_program_cannot_submit_to_registry(
        self, *args
    ):
        provider_user = provider_admin_factory()
        rater_user = self.get_rater()
        rater_user.rater_id = None
        rater_user.save()
        certified_home_stat = self.get_non_hers_based_home_status(
            True, provider_user.company, rater_user
        )

        self.assertEqual(
            user_can_submit_to_resnet_registry(certified_home_stat, provider_user), False
        )

    def test_certified_home_rater_of_record_rater_id_hers_program_can_submit_to_registry(
        self, *args
    ):
        provider_user = provider_admin_factory()
        rater_user = self.get_rater()
        certified_home_stat = self.get_hers_based_home_status(
            True, provider_user.company, rater_user
        )

        self.assertEqual(
            user_can_submit_to_resnet_registry(certified_home_stat, provider_user), True
        )

    @patch("axis.home.utils.submit_home_status_to_registry.delay")
    def test_provider_with_auto_submit_flag_submits_home_to_registry_on_certification(
        self, registry_mock, *args
    ):
        provider_user = provider_admin_factory(company__auto_submit_to_registry=True)
        rater_user = self.get_rater()
        home_stat = self.get_hers_based_home_status(True, provider_user.company, rater_user)

        registry_mock.assert_called_once_with(home_stat.id, provider_user.id)

    @patch("axis.home.utils.submit_home_status_to_registry")
    def test_provider_with_auto_submit_flag_cannot_submit_home_with_no_rater_of_record(
        self, registry_mock, *args
    ):
        provider_user = provider_admin_factory(company__auto_submit_to_registry=True)
        self.get_hers_based_home_status(True, provider_user.company)

        registry_mock.assert_not_called()

    @patch("axis.home.utils.submit_home_status_to_registry")
    def test_provider_with_auto_submit_flag_cannot_submit_home_with_rater_of_record_no_rater_id(
        self, registry_mock, *args
    ):
        provider_user = provider_admin_factory(company__auto_submit_to_registry=True)
        rater_user = self.get_rater(rater_id=False)
        self.get_hers_based_home_status(True, provider_user.company, rater_user)

        registry_mock.assert_not_called()

    @patch("axis.home.utils.submit_home_status_to_registry")
    def test_provider_with_auto_submit_flag_cannot_submit_non_hers_program(
        self, registry_mock, *args
    ):
        provider_user = provider_admin_factory(company__auto_submit_to_registry=True)
        rater_user = self.get_rater()
        self.get_non_hers_based_home_status(True, provider_user.company, rater_user)

        registry_mock.assert_not_called()

    @patch("axis.home.utils.submit_home_status_to_registry")
    def test_provider_without_auto_submit_flag_does_not_submit_home_to_registry_on_certification(
        self, registry_mock, *args
    ):
        provider_user = provider_admin_factory(company__auto_submit_to_registry=False)
        rater_user = self.get_rater()
        self.get_hers_based_home_status(True, provider_user.company, rater_user)

        registry_mock.assert_not_called()
