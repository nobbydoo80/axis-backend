"""permissions.py: """

__author__ = "Artem Hruzd"
__date__ = "07/23/2020 20:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.apps import apps
from rest_framework.permissions import BasePermission

from axis.company.models import Company
from axis.customer_hirl.models import HIRLProjectRegistration, BuilderAgreement

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLCompanyMemberPermission(BasePermission):
    """Allows access only to HIRL company members"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.company
            and request.user.company.company_type == Company.PROVIDER_COMPANY_TYPE
            and request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
        )


class HIRLCompanyAdminMemberPermission(BasePermission):
    """Allows access only to HIRL company members"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.company
            and request.user.company.company_type == Company.PROVIDER_COMPANY_TYPE
            and request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
            and request.user.is_company_admin
        )


class HIRLProjectViewPermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        if request.user.is_superuser:
            return True

        if request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return True

        if request.user.company.company_type in [
            Company.BUILDER_COMPANY_TYPE,
            Company.ARCHITECT_COMPANY_TYPE,
            Company.DEVELOPER_COMPANY_TYPE,
            Company.COMMUNITY_OWNER_COMPANY_TYPE,
        ]:
            return True
        if request.user.company.company_type in [
            Company.PROVIDER_COMPANY_TYPE,
            Company.RATER_COMPANY_TYPE,
        ]:
            return request.user.company.sponsors.filter(
                slug=customer_hirl_app.CUSTOMER_SLUG
            ).exists()
        return False


class HIRLProjectCreatePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False
        if request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return True
        if request.user.company.company_type in [
            Company.PROVIDER_COMPANY_TYPE,
            Company.RATER_COMPANY_TYPE,
        ]:
            is_sponsoring_by_hirl = request.user.company.sponsors.filter(
                slug=customer_hirl_app.CUSTOMER_SLUG
            ).exists()

            return is_sponsoring_by_hirl
        return False


class HIRLProjectUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False
        return True

    def has_object_permission(self, request, view, hirl_project):
        return hirl_project.can_edit(user=request.user)


class HIRLProjectDeletePermission(BasePermission):
    """
    1. HIRL Company members and Project owners can delete project with `NEW` state
    """

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        return True

    def has_object_permission(self, request, view, hirl_project):
        if request.user.company:
            if (
                request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
                and request.user.is_company_admin
            ) or request.user.is_superuser:
                return True
            if request.user.company == hirl_project.registration.registration_user.company:
                if hirl_project.registration.state == HIRLProjectRegistration.NEW_STATE:
                    return True
        return False


class HIRLProjectRegistrationViewPermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        if request.user.is_superuser:
            return True

        if request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return True

        if request.user.company.company_type in [
            Company.BUILDER_COMPANY_TYPE,
            Company.ARCHITECT_COMPANY_TYPE,
            Company.DEVELOPER_COMPANY_TYPE,
            Company.COMMUNITY_OWNER_COMPANY_TYPE,
        ]:
            return True
        if request.user.company.company_type in [
            Company.PROVIDER_COMPANY_TYPE,
            Company.RATER_COMPANY_TYPE,
        ]:
            return request.user.company.sponsors.filter(
                slug=customer_hirl_app.CUSTOMER_SLUG
            ).exists()
        return False


class HIRLProjectRegistrationCreatePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False
        if request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG:
            return True
        if request.user.company.company_type in [
            Company.PROVIDER_COMPANY_TYPE,
            Company.RATER_COMPANY_TYPE,
        ]:
            is_sponsoring_by_hirl = request.user.company.sponsors.filter(
                slug=customer_hirl_app.CUSTOMER_SLUG
            ).exists()

            return is_sponsoring_by_hirl
        return False


class HIRLProjectRegistrationUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False
        return True

    def has_object_permission(self, request, view, hirl_project_registration):
        return hirl_project_registration.can_edit(user=request.user)


class HIRLProjectRegistrationDeletePermission(BasePermission):
    """
    1. HIRL Company members and Project owners can delete project with `NEW` state
    """

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        return True

    def has_object_permission(self, request, view, hirl_project_registration):
        if request.user.company:
            if (
                request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
                and request.user.is_company_admin
            ) or request.user.is_superuser:
                return True

            if request.user.company == hirl_project_registration.registration_user.company:
                if hirl_project_registration.state == HIRLProjectRegistration.NEW_STATE:
                    return True
        return False


class HIRLVerifierAgreementUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        return True

    def has_object_permission(self, request, view, verifier_agreement):
        if request.user.company:
            if (
                request.user.company == verifier_agreement.verifier.company
                or request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
                or request.user.is_superuser
            ):
                return True
        return False


class HIRLVerifierAgreementDeletePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        return True

    def has_object_permission(self, request, view, verifier_agreement):
        if request.user.company:
            if (
                request.user.company == verifier_agreement.verifier.company
                or request.user.company.slug == customer_hirl_app.CUSTOMER_SLUG
                or request.user.is_superuser
            ):
                return True

        return False


class HIRLClientAgreementEditPermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        return True

    def has_object_permission(self, request, view, client_agreement: BuilderAgreement):
        return client_agreement.can_be_edited(user=request.user)


class HIRLClientAgreementDeletePermission(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated and request.user.company):
            return False

        return True

    def has_object_permission(self, request, view, client_agreement: BuilderAgreement):
        return client_agreement.can_be_deleted(user=request.user)
