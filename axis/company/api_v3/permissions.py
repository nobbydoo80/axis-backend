"""Api V3 company permission classes."""

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 12:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from rest_framework.permissions import BasePermission

from axis.company.models import Company


class CompanyRetrievePermission(BasePermission):
    """
    Allow to view company for everyone except for Users from same company type.
    Users can view own companies
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.company)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if obj.id == request.user.company.id:
            return True
        if obj.company_type != request.user.company.company_type:
            return True
        return False


class CompanyUpdatePermission(BasePermission):
    """
    Combination of multiple Permission classes resolve issue with bitwise logic:
    https://github.com/encode/django-rest-framework/issues/7117

    Allow access:
    Superusers
    Company admin if company without company admins
    Company admins from this company
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.company)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if request.user.is_company_admin and not bool(obj.get_admins().count()):
            return True
        if request.user.is_company_admin and obj.id == request.user.company.id:
            return True
        return False


class NestedCompanyUpdatePermission(CompanyUpdatePermission):
    def has_permission(self, request, view):
        parents_query_dict = view.get_parents_query_dict()
        try:
            company_id = int(parents_query_dict["company_id"])
        except (KeyError, ValueError):
            return False
        company = Company.objects.get(id=company_id)
        has_permission = super(NestedCompanyUpdatePermission, self).has_permission(request, view)
        has_object_permission = super(NestedCompanyUpdatePermission, self).has_object_permission(
            request, view, company
        )
        return has_permission and has_object_permission

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CompanyHasAdminMembersPermission(BasePermission):
    """Allows access only if Company has any members."""

    def has_object_permission(self, request, view, obj):
        return bool(obj.get_admins().count())


class CompanyTypeMemberPermission(BasePermission):
    @property
    def company_type(self):
        raise NotImplementedError

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.company
            and request.user.company.company_type == self.company_type
        )


class CompanyTypeAdminMemberPermission(CompanyTypeMemberPermission):
    @property
    def company_type(self):
        raise NotImplementedError

    def has_permission(self, request, view):
        has_permission = super(CompanyTypeAdminMemberPermission, self).has_permission(request, view)
        return has_permission and request.user.is_company_admin


class BuilderCompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.BUILDER_COMPANY_TYPE


class BuilderCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.BUILDER_COMPANY_TYPE


class ArchitectCompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.ARCHITECT_COMPANY_TYPE


class ArchitectCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.ARCHITECT_COMPANY_TYPE


class DeveloperCompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.DEVELOPER_COMPANY_TYPE


class DeveloperCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.DEVELOPER_COMPANY_TYPE


class CommunityOwnerCompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.COMMUNITY_OWNER_COMPANY_TYPE


class CommunityOwnerCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.COMMUNITY_OWNER_COMPANY_TYPE


class RaterCompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.RATER_COMPANY_TYPE


class RaterCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.RATER_COMPANY_TYPE


class QACompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.QA_COMPANY_TYPE


class QACompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.QA_COMPANY_TYPE


class ProviderCompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.PROVIDER_COMPANY_TYPE


class ProviderCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.PROVIDER_COMPANY_TYPE


class EEPCompanyAdminMemberPermission(CompanyTypeAdminMemberPermission):
    company_type = Company.PROVIDER_COMPANY_TYPE


class EEPCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.PROVIDER_COMPANY_TYPE


class HVACCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.HVAC_COMPANY_TYPE


class UtilityCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.UTILITY_COMPANY_TYPE


class GeneralCompanyMemberPermission(CompanyTypeMemberPermission):
    company_type = Company.GENERAL_COMPANY_TYPE


class NestedCompanyHasAdminMembersPermission(BasePermission):
    """Allows access only if Company has any members. Using in nested routers"""

    def has_permission(self, request, view):
        parents_query_dict = view.get_parents_query_dict()
        try:
            company_id = int(parents_query_dict["company_id"])
        except (KeyError, ValueError):
            return False
        company = Company.objects.get(id=company_id)
        return bool(company.get_admins().count())


class NestedIsCompanyMemberPermission(BasePermission):
    """Allows access only to Company members. Using in nested routers"""

    def has_permission(self, request, view):
        parents_query_dict = view.get_parents_query_dict()
        try:
            company_id = int(parents_query_dict["company_id"])
        except (KeyError, ValueError):
            return False
        return request.user.company and request.user.company.id == company_id


class IsCompanyAdminMemberPermission(BasePermission):
    """Allows access only to Company is_company_admin members."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.company
            and request.user.is_company_admin
            and obj.id == request.user.company.id
        )


class AltNameUpdatePermission(BasePermission):
    """
    Allow access:
    Superusers
    Company admin if company without company admins
    Company admins from this company
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.company)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if request.user.is_company_admin and not bool(obj.company.get_admins().count()):
            return True
        if request.user.is_company_admin and obj.company.id == request.user.company.id:
            return True
        return False


class SponsorPreferencesUpdatePermission(BasePermission):
    """
    Allow access:
    Superusers
    Company admin if company without company admins
    Company admins from this company
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.company)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if request.user.is_company_admin and obj.sponsor.id == request.user.company.id:
            return True
        return False


class UsersCompanyOwnsObjectPermission(BasePermission):
    """
    Allows access:
      SuperUsers
    And
      Any company admin user who belongs to Object's Company.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.company)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return (
            request.user.company
            and request.user.is_company_admin
            and obj.company
            and obj.company.id == request.user.company.id
        )
