"""permissions.py: """


from axis.company.api_v3.permissions import (
    IsCompanyAdminMemberPermission,
    NestedIsCompanyMemberPermission,
    NestedCompanyHasAdminMembersPermission,
    CompanyHasAdminMembersPermission,
    BuilderCompanyAdminMemberPermission,
    BuilderCompanyMemberPermission,
)
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.core.tests.testcases import ApiV3Tests

__author__ = "Artem Hruzd"
__date__ = "03/20/2020 13:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class MockRequest:
    pass


class MockNestedCompanyView:
    def get_parents_query_dict(self):
        return {}


class CompanyPermissionsTestCase(CompaniesAndUsersTestMixin, ApiV3Tests):
    include_company_types = ["builder"]
    include_unrelated = False
    include_noperms = False

    def setUp(self):
        self.mock_request = MockRequest()
        self.mock_nested_company_view = MockNestedCompanyView()

    def test_is_company_admin_member_returns_true(self):
        user = self.get_admin_user(company_type="builder")
        self.mock_request.user = user
        permission = IsCompanyAdminMemberPermission()
        result = permission.has_object_permission(self.mock_request, None, user.company)
        self.assertTrue(result)

    def test_company_has_admin_members_returns_true(self):
        user = self.get_admin_user(company_type="builder")
        self.mock_request.user = user
        permission = CompanyHasAdminMembersPermission()
        result = permission.has_object_permission(self.mock_request, None, user.company)
        self.assertTrue(result)

    def test_builder_organization_is_company_admin_member_returns_true(self):
        user = self.get_admin_user(company_type="builder")
        self.mock_request.user = user
        permission = BuilderCompanyAdminMemberPermission()
        result = permission.has_permission(self.mock_request, None)
        self.assertTrue(result)

    def test_builder_organization_member_returns_true(self):
        user = self.get_admin_user(company_type="builder")
        self.mock_request.user = user
        permission = BuilderCompanyMemberPermission()
        result = permission.has_permission(self.mock_request, None)
        self.assertTrue(result)

    def test_nested_is_company_admin_member_returns_true(self):
        user = self.get_admin_user(company_type="builder")
        self.mock_request.user = user
        self.mock_nested_company_view.get_parents_query_dict = lambda: {
            "company_id": user.company.id
        }
        permission = NestedIsCompanyMemberPermission()
        result = permission.has_permission(self.mock_request, self.mock_nested_company_view)
        self.assertTrue(result)

        result = permission.has_object_permission(
            self.mock_request, self.mock_nested_company_view, user.company
        )
        self.assertTrue(result)

    def test_nested_company_has_admin_members_returns_true(self):
        user = self.get_admin_user(company_type="builder")
        self.mock_request.user = user
        self.mock_nested_company_view.get_parents_query_dict = lambda: {
            "company_id": user.company.id
        }
        permission = NestedCompanyHasAdminMembersPermission()
        result = permission.has_permission(self.mock_request, self.mock_nested_company_view)
        self.assertTrue(result)
        result = permission.has_object_permission(
            self.mock_request, self.mock_nested_company_view, user.company
        )
        self.assertTrue(result)
