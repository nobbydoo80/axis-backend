"""views.py: Django relationship"""

import json
import logging
from collections import defaultdict, OrderedDict
from operator import attrgetter

import datatableview.helpers
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse, NoReverseMatch

from axis.company.models import Company
from axis.company.strings import COMPANY_TYPES_MAPPING, COMPANY_TYPES_PLURAL
from axis.core.mixins import AuthenticationMixin
from axis.core.views.generic import (
    AxisListView,
    LegacyAxisDatatableView,
    AxisCreateView,
    AxisDeleteView,
)
from axis.home.models import Home
from axis.relationship.utils import create_or_update_spanning_relationships
from .forms import RelationshipForm
from .messages import (
    RelationshipCreatedMessage,
    RelationshipDeletedMessage,
    RelationshipRemovedMessage,
)
from .models import Relationship

__author__ = "Steven Klass"
__date__ = "8/21/12 8:35 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# Used for dynamic redirects after a successful POST operation
POTENTIAL_LIST_VIEWS = (
    "{model}:list",
    "{model}_list",
    "{model}_list_view",
    "home",
)


def get_redirect_url(model_name):
    for url in POTENTIAL_LIST_VIEWS:
        try:
            url = url.format(model=model_name)
            return reverse(url)
        except NoReverseMatch:
            pass


class RelationshipListView(AuthenticationMixin, LegacyAxisDatatableView):
    """Lists all relationships for a given object."""

    template_name = "relationship/relationship_list.html"
    show_add_button = False

    datatable_options = {
        "columns": [
            ("Company", "company", datatableview.helpers.link_to_model(key=attrgetter("company"))),
            "Delete",
            ("Is customer", "is_customer", datatableview.helpers.make_boolean_checkmark),
            ("Is owned", "is_owned", datatableview.helpers.make_boolean_checkmark),
            ("Is attached", "is_attached", datatableview.helpers.make_boolean_checkmark),
            ("Is viewable", "is_viewable", datatableview.helpers.make_boolean_checkmark),
            ("Is reportable", "is_reportable", datatableview.helpers.make_boolean_checkmark),
            ("Calc Attached", "calc_attached"),
            ("Calc Accepted", "calc_accepted"),
        ]
    }

    def has_permission(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return Relationship.objects.filter(
            content_type=self._get_content_type(), object_id=self.kwargs["object_id"]
        )

    def preload_record_data(self, obj):
        return {"relationships": self.get_object().relationships.all()}

    def get_column_Delete_data(self, obj, *args, **kwargs):
        delete = "-"
        if obj.can_be_deleted(self.request.user):
            delete = '<a href="{}"><i class="fa fa-trash-o"></i></a>'.format(
                reverse("relationship:delete_id", kwargs={"pk": obj.id})
            )
        return delete

    def get_column_calc_attached_data(self, obj, relationships, *args, **kwargs):
        show_attached = relationships.show_attached()
        return datatableview.helpers.make_boolean_checkmark(obj in show_attached)

    def get_column_calc_accepted_data(self, obj, relationships, *args, **kwargs):
        accepted = relationships.get_accepted_companies()
        return datatableview.helpers.make_boolean_checkmark(obj.company in accepted)

    def _get_content_type(self):
        if hasattr(self, "content_type") and self.content_type is not None:
            return self.content_type
        if self.kwargs["app_label"] == "company" and self.kwargs["model"] in COMPANY_TYPES_MAPPING:
            self.kwargs["model"] = "company"
        self.content_type = ContentType.objects.get(
            app_label=self.kwargs["app_label"], model=self.kwargs["model"]
        )
        return self.content_type

    def get_object(self):
        """Gets the target object specified by the url kwargs."""
        if hasattr(self, "object"):
            return self.object
        content_type = self._get_content_type()
        self.object = content_type.get_object_for_this_type(pk=self.kwargs["object_id"])
        return self.object

    def get_context_data(self, **kwargs):
        context = super(RelationshipListView, self).get_context_data(**kwargs)
        context.update({k: self.kwargs[k] for k in ["app_label", "model", "object_id"]})
        context["object"] = self.get_object()
        return context


class RelationshipSideBarListView(AuthenticationMixin, AxisListView):
    """This is used for sidebars to show the associated relationships"""

    permission_required = "home.view_home"

    def _get_content_type(self):
        if hasattr(self, "content_type") and self.content_type is not None:
            return self.content_type
        if self.kwargs["app_label"] == "company" and self.kwargs["model"] in COMPANY_TYPES_MAPPING:
            self.kwargs["model"] = "company"
        self.content_type = ContentType.objects.get(
            app_label=self.kwargs["app_label"], model=self.kwargs["model"]
        )
        return self.content_type

    def get_queryset(self):
        return Relationship.objects.filter(
            content_type=self._get_content_type(), object_id=self.kwargs["object_id"]
        )

    def get_serialized_data(self):
        results = defaultdict(list)

        program_owners = []
        # Currently only want to duplicate Program Sponsors/Owners for the Home Detail Page.
        if self._get_content_type() == ContentType.objects.get_for_model(Home):
            for relationship in self.get_queryset():
                if relationship.content_object:
                    filtered_statuses = relationship.content_object.homestatuses.filter_by_user(
                        self.request.user
                    )
                    program_owners = list(
                        filtered_statuses.values_list("eep_program__owner__id", flat=True)
                    )

        for object in self.get_queryset():
            if object.company.company_type != "eep":
                if object.company.id in program_owners and object not in results["eep"]:
                    results["eep"].append(object)
            results[object.company.company_type].append(object)

        final = OrderedDict()
        href_template = '<a href="{}">{}</a>'
        my_comp_ids = self.request.user.company.relationships.get_companies(ids_only=True)
        my_comp_ids = list(my_comp_ids) + [self.request.user.company.id]
        for co_type, (single, plural) in COMPANY_TYPES_PLURAL.items():
            if co_type not in results.keys():
                continue
            name = plural
            if len(results.get(co_type, [])) == 1:
                name = single
            final[name] = []
            for object in results.get(co_type, []):
                has_rel = True if object.company.id in my_comp_ids else False
                href = href_template.format(
                    object.company.get_absolute_url(), "{}".format(object.company)
                )
                if co_type == self.request.user.company.company_type:
                    href = "{}".format(object.company)
                    has_rel = True
                add_url = reverse(
                    "relationship:add_id",
                    kwargs={
                        "model": "company",
                        "app_label": "company",
                        "object_id": object.company.id,
                    },
                )
                add_href = href_template.format(
                    add_url,
                    '<i class="fa fa-plus-square" data-toggle="tooltip" title="Add an '
                    'association to this company"></i>',
                )

                direct_href, delete_href = "", ""
                if self.request.user.is_superuser:
                    _href = '<a url="{}" class="{}" href="#">{}</a>'
                    kwrgs = self.kwargs.copy()
                    kwrgs.update({"company_id": object.company.id})
                    delete_url = reverse("apiv2:relationship-company-delete", kwargs=kwrgs)
                    direct_url = reverse("apiv2:relationship-company-add", kwargs=kwrgs)
                    direct_href = _href.format(
                        direct_url,
                        "direct_relationship",
                        '<i class="fa fa-plus" data-toggle="tooltip" '
                        'title="Add a direct association for this company"></i>',
                    )

                    delete_href = _href.format(
                        delete_url,
                        "delete_relationship",
                        '<i class="fa fa-trash-o" data-toggle="tooltip" '
                        'title="Delete an association for this company"></i>',
                    )

                final[name].append(
                    {
                        "url": object.company.get_absolute_url(),
                        "href": href,
                        "name": "{}".format(object.company),
                        "add_href": add_href if not has_rel else "",
                        "is_owned": object.is_owned,
                        "auto_add": object.company.auto_add_direct_relationships,
                        "has_relation_with_requester": has_rel,
                        "direct_href": direct_href,
                        "delete_href": delete_href,
                    }
                )
        return final

    def get(self, request, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return HttpResponse(
                json.dumps(self.get_serialized_data()), content_type="application/json"
            )
        return HttpResponseForbidden()


class RelationshipCreateView(LoginRequiredMixin, AxisCreateView):
    template_name = "relationship/relationship_form.html"
    form_class = RelationshipForm
    show_cancel_button = False  # Showing this button is too hard with dynamic urls

    def get_queryset(self):
        """Narrow this based on your company"""
        company = self.request.user.company
        return Relationship.objects.filter_by_company(company)

    def get(self, request, *args, **kwargs):
        """Hijack the the get for simple create views.."""
        if kwargs.get("model") and kwargs.get("app_label") and kwargs.get("object_id"):
            return self.create(request, **kwargs)
        else:
            log.info("Post..")
            return super(RelationshipCreateView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        """Try your best to get a sane return"""
        if "go_to_detail" in self.request.POST and hasattr(self, "target_object"):
            return self.target_object.get_absolute_url()
        model = self.kwargs["model"]
        if model == "company":
            co_type = Company.objects.get(pk=self.kwargs["object_id"]).company_type
            return reverse("company:list", kwargs={"type": co_type})
        return get_redirect_url(model)

    def create(self, request, *args, **kwargs):
        """This will remove a relationship to an object

        Couple notes:
            Setting `is_attached = False` removes it from all views.  The relationship is broken
            Setting `is_viewable = False` removes the view from views. It's still there for
            reporting to others and search
        """
        content_type = ContentType.objects.get(
            app_label=self.kwargs["app_label"], model=self.kwargs["model"]
        )

        self.object, create = Relationship.objects.get_or_create_direct(
            company=self.request.user.company,
            content_type=content_type,
            object_id=self.kwargs["object_id"],
        )
        self.object.is_attached = True
        self.object.is_viewable = True
        self.object.is_reportable = True
        self.object.is_owned = True
        self.object.save()

        # Force a save which will ripple any post save relationship creations to happen.
        try:
            self.target_object = content_type.get_object_for_this_type(pk=self.kwargs["object_id"])
            create_or_update_spanning_relationships(
                self.request.user.company, self.target_object, skip_implied=True, push_down=True
            )
        except Exception as err:
            self.target_object = None
            # if self.kwargs['app_label'] != "company":
            log.error(
                "Unable to create parent relationships for %s [%s] to %s [%s] - %s",
                self.request.user,
                self.request.user.id,
                self.kwargs["model"],
                self.kwargs["object_id"],
                err,
            )

        if self.target_object:
            RelationshipCreatedMessage(url=self.target_object.get_absolute_url()).send(
                context={
                    "action": "Created" if create else "Updated",
                    "company": str(self.object.company),
                    "object": str(self.target_object),
                    "assigning_company": str(request.user.company),
                },
                company=self.object.company,
            )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        log.warning(form.errors)
        return super(RelationshipCreateView, self).form_invalid(form)

    def form_valid(self, form):
        """Create the relationship"""
        if form.cleaned_data.get("object") and not self.kwargs.get("object_id"):
            self.kwargs["object_id"] = form.cleaned_data.get("object")
        return self.create(self.request, **self.kwargs)


class RelationshipDeleteView(LoginRequiredMixin, AxisDeleteView):
    def get_queryset(self):
        """Narrow this based on your company"""
        company = self.request.user.company
        return Relationship.objects.filter_by_company(company, show_attached=True)

    def _is_company_relationship(self):
        return any(
            [
                self.kwargs["app_label"] == self.kwargs["model"] == "company",
                self.kwargs["app_label"] == "company"
                and self.kwargs["model"].endswith("organization"),
            ]
        )

    def get_object(self, queryset=None, return_qs=False):
        """Get the object"""
        if queryset is None:
            queryset = self.get_queryset()
        content_types = ContentType.objects.filter(
            app_label=self.kwargs["app_label"], model=self.kwargs["model"]
        )

        if self._is_company_relationship():
            content_types = ContentType.objects.filter(
                Q(app_label=self.kwargs["app_label"], model=self.kwargs["model"])
                | Q(app_label=self.kwargs["app_label"], model__endswith="organization")
            ).exclude(model__icontains="historical")

        queryset = queryset.filter(
            company=self.request.user.company,
            content_type__in=content_types,
            object_id=self.kwargs["object_id"],
        )
        try:
            obj = queryset.get()
        except Relationship.MultipleObjectsReturned:
            for obj in queryset.all():
                if obj.content_type.app_label != "company":
                    raise
                if obj.content_type.model != "company" and not obj.content_type.model.endswith(
                    "organization"
                ):
                    raise
            if return_qs:
                return queryset
            raise
        except Relationship.DoesNotExist:
            raise Http404(
                ("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return queryset if return_qs else obj

    def get(self, request, *args, **kwargs):
        """HiJack the the get for simply remove views.."""
        if kwargs.get("pk") and kwargs.get("delete"):
            return self.full_delete_by_id(request, *args, **kwargs)
        if not kwargs.get("object_id"):
            return super(RelationshipDeleteView, self).get(request, *args, **kwargs)
        else:
            if self.kwargs.get("reject"):
                return self.reject(request, *args, **kwargs)
            return self.remove(request, *args, **kwargs)

    def get_success_url(self):
        """Try your best to get a sane return"""

        if self._is_company_relationship():
            target_object = ContentType.objects.get(
                app_label="company", model="company"
            ).get_object_for_this_type(pk=self.object.object_id)
            return reverse("company:list", kwargs={"type": target_object.company_type})
        return get_redirect_url(self.kwargs["model"])

    def remove(self, request, *args, **kwargs):
        """This is what normally happens - the relationship exists but is no longer viewable."""
        try:
            self.object = self.get_object()
        except MultipleObjectsReturned:
            self.objects = self.get_object(return_qs=True)
            self.object = self.objects.get(
                content_type__app_label="company", content_type__model="company"
            )
            self.objects.update(
                is_owned=True, is_attached=True, is_viewable=False, is_reportable=False
            )
        else:
            self.object.is_owned = True
            self.object.is_attached = True
            self.object.is_viewable = False
            self.object.is_reportable = False
            self.object.save()

        # Force a save which will ripple any post save relationship creations to happen.
        target_object = self.object.get_content_object()
        target_object.save()

        RelationshipRemovedMessage(url=target_object.get_absolute_url()).send(
            context={"company": str(self.object.company), "object": str(target_object)},
            company=self.object.company,
        )
        return HttpResponseRedirect(self.get_success_url())

    def reject(self, request, *args, **kwargs):
        """When someone indirectly adds me and I don't agree with it I don't want the
        relationship to exist.  This is effectively a block."""
        try:
            self.object = self.get_object()
        except MultipleObjectsReturned:
            self.objects = self.get_object(return_qs=True)
            self.objects.update(
                is_owned=True, is_attached=False, is_viewable=False, is_reportable=False
            )
            msg = "Relationships between {} has been rejected.".format(
                ", ".join(list(self.objects))
            )
        else:
            self.object.is_owned = True
            self.object.is_attached = False
            self.object.is_viewable = False
            self.object.is_reportable = False
            self.object.save()
            msg = "Relationship between {} has been rejected.".format(self.object)

        messages.info(request, msg)
        log.info(msg)
        return HttpResponseRedirect(self.get_success_url())

    def delete(self, request, *args, **kwargs):
        """This is the big daddy and shouldn't be used.

        Couple notes:
            Setting `is_attached = False` removes it from all views.  The relationship is broken
            Setting `is_viewable = False` removes the view from views. It's still there for
            reporting to others and search
        """
        self.object = self.get_object()
        target_object = self.object.get_content_object()
        self.object.delete()

        RelationshipDeletedMessage(url=target_object.get_absolute_url()).send(
            context={"company": str(self.object.company), "object": str(target_object)},
            company=self.object.company,
        )

        return HttpResponseRedirect(self.get_success_url())

    def full_delete_by_id(self, request, *args, **kwargs):
        """This is the big daddy and shouldn't be used.

        Couple notes:
            Setting `is_attached = False` removes it from all views.  The relationship is broken
            Setting `is_viewable = False` removes the view from views. It's still there for
            reporting to others and search
        """
        try:
            obj = Relationship.objects.get(id=self.kwargs.get("pk"))
        except Relationship.DoesNotExist:
            raise Http404(
                ("No %(verbose_name)s found matching the query")
                % {"verbose_name": Relationship._meta.verbose_name}
            )

        target_object = obj.get_content_object()
        obj.delete()

        RelationshipDeletedMessage(url=target_object.get_absolute_url()).send(
            context={"company": str(obj.company), "object": str(target_object)},
            company=self.object.company,
        )

        return HttpResponseRedirect(self.get_success_url())


class AssociationDashboardView(LoginRequiredMixin, LegacyAxisDatatableView):
    template_name = "association/associations_dashboard.html"

    datatable_options = {
        "columns": [
            (
                "Home",
                "eepprogramhomestatus__home",
                datatableview.helpers.link_to_model(key=attrgetter("eepprogramhomestatus.home")),
            ),
            ("Program", "eepprogramhomestatus__eep_program__name"),
            ("Shared To", ["user__username", "company__name"], "get_share_target"),
            ("Active", "is_active", datatableview.helpers.make_boolean_checkmark),
            ("Accepted", "is_accepted", datatableview.helpers.make_boolean_checkmark),
            ("Hidden", "is_hidden", datatableview.helpers.make_boolean_checkmark),
            ("Owner", "owner__name", datatableview.helpers.link_to_model(key=attrgetter("owner"))),
        ],
        # TODO: Replace with real UI filter
        "search_fields": [
            "eepprogramhomestatus__home__state",
            "eepprogramhomestatus__eep_program__name",
            "company__company_type",
        ],
    }

    def get_datatable_options(self):
        options = self.datatable_options.copy()

        if not self.request.user.is_superuser:
            options["columns"] = options["columns"][:]
            options["columns"].pop(-1)

        return options

    def get_queryset(self):
        # For today, this app's scope is just homestatuses, so we'll get sloppy here
        from axis.home.models import EEPProgramHomeStatus

        Association = EEPProgramHomeStatus.associations.rel.related_model
        return Association.objects.filter_by_user(self.request.user)

    def get_share_target(self, instance, *args, **kwargs):
        target = instance.user or instance.company
        text = "{} ({})".format(target.user, target.user.company) if instance.user else None
        return datatableview.helpers.link_to_model(target, text)
