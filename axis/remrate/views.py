"""views.py: Django remrate"""


import logging

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    LegacyAxisDatatableView,
    AxisCreateView,
    AxisUpdateView,
    AxisDeleteView,
)
from .forms import RemRateUserCreateForm, RemRateUserUpdateForm
from .models import RemRateUser

from axis.remrate.utils import RemrateUserAccountsManager
from django.db import transaction

__author__ = "Steven Klass"
__date__ = "1/17/12 9:17 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RemRateUserUrlMixin(object):
    """Fetches the correctly reversed urls for models.RemRateUser"""

    def get_add_url(self, **kwargs):
        return reverse("remrate:user:add", kwargs=kwargs)

    def get_cancel_url(self, **kwargs):
        return reverse("remrate:user:list")


class RemRateUserListView(AuthenticationMixin, RemRateUserUrlMixin, LegacyAxisDatatableView):
    permission_required = "remrate.add_remrateuser"
    model = RemRateUser

    datatable_options = {
        "columns": [
            ("Username", "username"),
            ("Password (Decrypted)", "password"),
            ("Last Used", "last_used"),
            "Delete",
        ],
    }

    def get_datatable_options(self):
        options = self.datatable_options.copy()
        options["columns"] = options["columns"][:]

        if not self.request.user.is_superuser:
            options["columns"].pop(1)
        return options

    def get_queryset(self):
        return self.model.objects.filter_by_user(user=self.request.user)

    def get_column_Delete_data(self, instance, *args, **kwargs):
        url = reverse("remrate:user:delete", kwargs={"pk": instance.pk})
        return '<a href="{}" class="btn btn-danger">Delete</a>'.format(url)


class RemRateUserCreateView(AuthenticationMixin, RemRateUserUrlMixin, AxisCreateView):
    permission_required = "remrate.add_remrateuser"
    model = RemRateUser
    form_class = RemRateUserCreateForm

    success_url = reverse_lazy("remrate:user:list")
    success_message = "Account for {object.username} has been created successfully."

    def get_form_kwargs(self):
        kwargs = super(RemRateUserCreateView, self).get_form_kwargs()
        kwargs.update({"company": self.request.user.company})
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            obj = form.save()

        with RemrateUserAccountsManager() as manager:
            manager.create_new_user(obj.username, form.cleaned_data["new_password2"])

        self.add_success_message(form)
        return HttpResponseRedirect(self.success_url)


class RemRateUserUpdateView(AuthenticationMixin, RemRateUserUrlMixin, AxisUpdateView):
    permission_required = "remrate.change_remrateuser"
    model = RemRateUser
    form_class = RemRateUserUpdateForm

    success_url = reverse_lazy("remrate:user:list")
    success_message = "Password change for {object.username} will be available within 24 hours."

    def get_queryset(self):
        return RemRateUser.objects.filter_by_user(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super(RemRateUserUpdateView, self).get_form_kwargs()
        kwargs.update({"company": self.request.user.company})
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            obj = form.save()

        with RemrateUserAccountsManager() as manager:
            manager.update_user_password(obj.username, form.cleaned_data["new_password2"])

        self.add_success_message(form)
        return HttpResponseRedirect(self.success_url)


class RemRateUserDeleteView(AuthenticationMixin, RemRateUserUrlMixin, AxisDeleteView):
    permission_required = "remrate.delete_remrateuser"

    delete_message = "The REM/Rate™ User account for {object} will be deleted within 24 hours."

    def get_queryset(self):
        return RemRateUser.objects.filter_by_user(user=self.request.user)

    def form_valid(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        with transaction.atomic():
            self.object.save()

        with RemrateUserAccountsManager() as manager:
            manager.delete_user(self.object.username)

        self.add_delete_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("remrate:user:list")
