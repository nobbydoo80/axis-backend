"""views.py: Django scheduling"""


from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import CreateView, DeleteView, DetailView
from axis.core.mixins import AuthenticationMixin

from axis.scheduling.forms import ConstructionStageForm
from axis.scheduling.models import ConstructionStage

__author__ = "Gaurav Kapoor"
__date__ = "6/25/12 9:38 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Gaurav Kapoor",
    "Steven Klass",
]


class ConstructionStageCreateView(AuthenticationMixin, CreateView):
    """Create view for a Construction Stage"""

    template_name = "scheduling/constructionstage_form.html"
    form_class = ConstructionStageForm
    permission_required = "scheduling.add_constructionstage"

    def get_queryset(self):
        """Update the rating  organization"""
        return ConstructionStage.objects.filter_by_user(user=self.request.user)

    def form_valid(self, form):
        super(ConstructionStageCreateView, self).form_valid(form)
        self.object.group = self.request.user.company.group
        self.object.owner = self.request.user.company
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ConstructionStageDeleteView(AuthenticationMixin, DeleteView):
    """Update view for a Construction Stage"""

    permission_required = "scheduling.delete_constructionstage"

    def get_queryset(self):
        """Update the rating  organization"""
        return ConstructionStage.objects.filter_by_user(user=self.request.user)

    def get_success_url(self):
        return reverse("construction_stage_list")


class ConstructionStageDetailView(AuthenticationMixin, DetailView):
    """Detail view for a Construction Stage"""

    permission_required = "scheduling.view_constructionstage"

    def get_queryset(self):
        """Update the rating  organization"""
        return ConstructionStage.objects.filter_by_user(user=self.request.user)

    def get_context_data(self, **kwargs):
        """Add in the delete capability"""
        context = super(ConstructionStageDetailView, self).get_context_data(**kwargs)
        context["can_delete"] = context["can_edit"] = False
        if not self.object.is_public and self.object.owner == self.request.user.company:
            if not self.object.home_set.count():
                context["can_delete"] = True
                context["can_edit"] = True
        return context


class ConstructionStageListView(AuthenticationMixin, ListView):
    """Detail view for a Construction Stage"""

    permission_required = "scheduling.view_constructionstage"

    def get_queryset(self):
        """Update the rating  organization"""
        return ConstructionStage.objects.filter_by_user(user=self.request.user)


class ConstructionStageUpdateView(AuthenticationMixin, UpdateView):
    """Update view for a Construction Stage"""

    form_class = ConstructionStageForm
    permission_required = "scheduling.change_constructionstage"

    def get_queryset(self):
        """Update the rating  organization"""
        return ConstructionStage.objects.filter_by_user(user=self.request.user)

    def form_valid(self, form):
        super(ConstructionStageUpdateView, self).form_valid(form)
        self.object.group = self.request.user.company.group
        self.object.owner = self.request.user.company
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
