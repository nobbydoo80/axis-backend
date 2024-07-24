"""signals.py: Django core"""


import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.sites.models import Site
from django_registration.signals import user_activated, user_registered
from tensor_registration.views import (
    AnonymousTensorActivationView,
    TensorAuthenticatedActivationView,
)

__author__ = "Steven Klass"
__date__ = "1/16/17 16:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.company.models import CompanyAccess, CompanyRole

log = logging.getLogger(__name__)
User = get_user_model()


def register_signals():
    """Nested to avoid tangling import during initial load."""
    post_save.connect(handler_update_user_groups, sender=User)


# pylint: disable=inconsistent-return-statements
def handler_update_user_groups(sender, instance, raw=False, **kwargs):
    """Triggers Group updates for the user."""

    if raw and instance.get_all_permissions():
        return
    from .tasks import update_user_groups

    return update_user_groups.delay(user_id=instance.id)


@receiver(user_activated, sender=AnonymousTensorActivationView)
def anonymous_user_activation_notification(sender, user, request, **kwargs):
    """
    After account activation notify company admins and pivotal support about approving user
    :param sender: TensorActivationView
    :param user: User object
    :param request: view request object
    :param kwargs: Contains additional information about signal object
    """
    from django.contrib.sites.shortcuts import get_current_site
    from .messages import (
        TensorAnonymousActivationMessage,
        TensorAnonymousActivationWithoutCompanyMessage,
    )

    request_protocol = "https" if request.is_secure() else "http"

    site = get_current_site(request)
    site_domain = site.domain

    approval_url = "{}://{}{}".format(
        request_protocol,
        site_domain,
        reverse("auth:approve_tensor_account", kwargs={"pk": user.pk}),
    )

    user_profile_url = "{}://{}{}".format(
        request_protocol,
        site_domain,
        reverse("profile:detail", kwargs={"pk": user.pk}),
    )

    msg_context = {
        "user_fullname": f"{user.first_name} {user.last_name}",
        "user_title": user.title,
        "user_email": user.email,
        "user_work_phone": str(user.work_phone),
        "user_cell_phone": str(user.cell_phone),
        "user_profile_url": user_profile_url,
        "user_domain": f"https://{user.email.split('@')[-1]}",
        "approval_url": approval_url,
        "company": "" if not user.company else user.company.name,
        "user": user,
    }

    if user.company:
        # If the user has chosen a company, message all its admins
        company_admins = User.objects.filter(
            Q(company=user.company, is_company_admin=True)
            | Q(company__slug="pivotal-energy-solutions", is_staff=True),
            is_active=True,
        )
        TensorAnonymousActivationMessage().send(users=company_admins, context=msg_context)
    else:
        company_admins = User.objects.filter(
            company__slug="pivotal-energy-solutions", is_superuser=True
        )

        TensorAnonymousActivationWithoutCompanyMessage().send(
            users=company_admins,
            context=msg_context,
        )


@receiver(user_activated, sender=TensorAuthenticatedActivationView)
def authenticated_user_activated_notification(sender, user, request, **kwargs):
    """
    User activate their account that was created by company admin or superuser
    :param sender: TensorAuthenticatedActivationView
    :param user: User object
    :param request: view request object
    :param kwargs: Contains additional information about signal object
    """
    from .messages import TensorAuthenticatedUserApproveMessage

    company_admins = User.objects.filter(
        Q(company=user.company, is_company_admin=True, is_active=True) | Q(is_staff=True)
    )
    msg_context = {
        "user_fullname": f"{user.first_name} {user.last_name}",
        "user_email": user.email,
    }

    TensorAuthenticatedUserApproveMessage().send(users=company_admins, context=msg_context)


@receiver(user_registered)
def user_registered_additional_setup(sender, user, request, **kwargs):
    """
    Additional configuration after user registration
    https://django-registration.readthedocs.io/en/3.2/signals.html
    :param sender: Any
    :param user: User object
    :param request: view request object
    :param kwargs: Contains additional information about signal object
    :return:
    """
    if request:
        current_site = request.current_site
    else:
        current_site = Site.objects.filter(id=settings.SITE_ID).first()

    user.site = current_site
    user.save()

    if user.company:
        company_access, created = CompanyAccess.objects.update_or_create(
            user=user, company=user.company
        )
        is_company_admin_role, created = CompanyRole.objects.get_or_create(
            slug="is_company_admin", defaults={"name": "Is Company Admin"}
        )
        if user.is_company_admin:
            company_access.roles.add(is_company_admin_role)
        else:
            company_access.roles.remove(is_company_admin_role)
