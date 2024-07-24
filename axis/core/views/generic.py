"""generic.py: Generics"""

import logging
import hashlib
import json

from datatableview.views import DatatableMixin
from datatableview.views.legacy import LegacyDatatableMixin
from django.contrib import messages
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from extra_views import InlineFormSetView, CreateWithInlinesView, UpdateWithInlinesView

from axis.examine import ExamineMixin
from ..datatables import *
from ..utils import collect_nested_object_list

__author__ = "Autumn Valenta"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)

# Try to use this sparingly.  The _find_url() function below will try to reverse a model's url based
# on its app_label as a namespace, but sometimes we don't control the model and its url mappings
# (for example, the User model or a third-party app).
# Use this mapping to provide urls that don't fit into our namespace pattern.
# Apps that we own, yet don't use namespaces, should be updated instead of being added to this map.
URL_OVERRIDES = {
    # Maps a model label to a dict of the url types.
    "someapp.Model": {
        # Each url type maps to an iterable: ["url_name", kwargs], where kwargs is a dict of url
        # kwargs required to reverse the url name.  At runtime, the "pk" kwarg will be provided.
        # Used for list view
        # 'add': ["auth_user_add", {}],
        # Used for detail view
        # 'update': ["auth_user_update", {}],
        # 'delete': ["auth_user_delete", {}],
        # Used for cancel buttons
        # 'view': ["auth_user_view", {}],
        # 'list': ["auth_user_list", {}],
    }
}


def _find_url(model, name, url_kwargs={}):
    """Temporary utility until all of our axis are using namespaces."""
    app_label = model._meta.app_label
    model_name = model._meta.model_name

    model_label = "{app}.{model}".format(app=app_label, model=model_name)
    if model_label in URL_OVERRIDES:
        url_name, kwargs = URL_OVERRIDES[model_label][name]
        kwargs.update(url_kwargs)
        return reverse(url_name, kwargs=kwargs)

    url = None
    for url_name in ["{app}:{model}:{name}", "{app}:{name}", "{model}:{name}"]:
        try:
            url = reverse(
                url_name.format(app=app_label, model=model_name, name=name), kwargs=url_kwargs
            )
        except:
            continue
        else:
            break
    else:
        msg = (
            "Modern namespaced url {app}:{model}:{name}, {app}:{name}, or {model}:{name} not"
            " available for model {app}.{model}: {kwargs!r}".format(
                app=app_label, model=model_name, name=name, kwargs=url_kwargs
            )
        )
        log.info(msg)
        # raise Exception(msg)
    return url


class AxisGenericMixin(object):
    def _get_model(self):
        if hasattr(self, "model") and self.model:
            return self.model
        if hasattr(self, "get_form_class") and hasattr(self.get_form_class(), "_meta"):
            return self.get_form_class()._meta.model
        if hasattr(self, "get_queryset"):
            return self.get_queryset().model
        raise Exception("Can't find a model on {}.".format(self.__class__.__name__))


class AxisFormMessagingMixin(object):
    success_message = "Successfully saved <em>{object}</em>."
    error_message = "Please correct the errors shown below."

    def form_valid(self, form):
        response = super(AxisFormMessagingMixin, self).form_valid(form)
        self.add_success_message(form)
        return response

    def form_invalid(self, form):
        response = super(AxisFormMessagingMixin, self).form_invalid(form)
        self.add_error_message(form)
        return response

    def add_success_message(self, form):
        message = self.get_success_message(form)
        if message is not None:
            messages.success(self.request, message)

    def add_error_message(self, form):
        message = self.get_error_message(form)
        if message is not None:
            messages.error(self.request, message)

    def get_success_message(self, form):
        message = self.success_message
        if message is not None:
            kwargs = {"object": form.instance}
            return message.format(**kwargs)

    def get_error_message(self, form):
        message = self.error_message
        if message is not None:
            kwargs = {"object": form.instance}
            return message.format(**kwargs)


class AxisDeleteMessagingMixin(object):
    delete_message = "Successfully deleted <em>%(object)s</em>."

    def post(self, request, *args, **kwargs):
        self.object_repr = "{}".format(self.get_object())
        response = super(AxisDeleteMessagingMixin, self).post(request, *args, **kwargs)
        self.add_delete_message()
        return response

    def add_delete_message(self):
        message = self.get_delete_message()
        if message is not None:
            messages.success(self.request, message)

    def get_delete_message(self):
        message = self.delete_message
        if message is not None:
            kwargs = {"object": self.object_repr}
            return message.format(**kwargs)


class AxisConfirmMessagingMixin(object):
    confirm_message = "Success."

    def post(self, request, *args, **kwargs):
        self.object_repr = repr(self.get_object())
        response = super(AxisConfirmMessagingMixin, self).post(request, *args, **kwargs)
        message = self.get_confirm_message()
        if message is not None:
            messages.success(request, message)
        return response

    def get_confirm_message(self):
        return self.confirm_message


class AxisListView(AxisGenericMixin, ListView):
    """Adds context variables for content type name and the url for adding a new instance."""

    show_add_button = True

    def get_add_url(self):
        return _find_url(self._get_model(), "add", self.get_add_url_kwargs())

    def get_add_url_kwargs(self, **kwargs):
        """Returns the kwargs necessary to reverse the "add" url."""
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AxisListView, self).get_context_data(**kwargs)
        model = self._get_model()

        if self.show_add_button:
            if hasattr(model, "can_be_added"):
                can_add = model.can_be_added(self.request.user)
            else:
                app_label = model._meta.app_label
                model_name = model._meta.model_name.lower()
                perm = "{app}.add_{model}".format(app=app_label, model=model_name)
                log.warning(
                    "%(app)s.%(model)s has no 'can_be_added()' method.  Attempting "
                    "to derive creation permission from perm label %(perm)s",
                    {"app": app_label, "model": model_name, "perm": perm},
                )
                can_add = self.request.user.has_perm(perm)
            add_url = self.get_add_url()
        else:
            can_add = False
            add_url = None

        context.update(
            {
                "verbose_name_plural": model._meta.verbose_name_plural,
                "can_add": can_add,
                "add_url": add_url,
            }
        )
        return context


class AxisDatatableView(DatatableMixin, AxisListView):
    def get_datatable(self, **kwargs):
        datatable = super(AxisDatatableView, self).get_datatable(**kwargs)
        columns = [(name, repr(column)) for name, column in datatable.columns.items()]
        identifier = hashlib.sha256(repr(columns).encode("utf-8")).hexdigest()
        datatable.identifier = identifier
        return datatable

    def prevision_kwargs(self, **kwrgs):
        kwargs = {}
        for k, v in kwrgs.items():
            k = k[:-2] if k.endswith("[]") else k

            if v in ["", "undefined", [""], ["undefined"]]:
                v = None
            elif v in ["true", "on", ["true"], ["on"]]:
                v = True
            elif v in ["false", "off", ["false"], ["off"]]:
                v = False
            elif isinstance(v, (list, tuple)) and len(v) == 1:
                v = v[0]
            elif isinstance(v, tuple) and len(v) > 1:
                v = list(v)

            if k not in kwargs:
                kwargs[k] = v
            else:
                if kwargs[k] is None:
                    kwargs[k] = v
                elif isinstance(kwargs[k], (list, tuple)):
                    v = [v] if not isinstance(v, list) else v
                    kwargs[k] += v
                else:
                    existing = [kwargs[k]] if not isinstance(kwargs[k], list) else kwargs[k]
                    v = [v] if not isinstance(v, list) else v
                    kwargs[k] = existing + v
        # print("*x"*10)
        # pprint.pprint(kwargs)
        return kwargs


class AxisFilterView(FormMixin, AxisDatatableView):
    """Combination datatable and filter form view."""

    template_name = "base_filter_list.html"
    fields = "__all__"
    exclude = None
    initial = {}

    filters = {}

    IGNORE_RAW_VALUES = (
        "",
        "off",
    )
    IGNORE_CLEANED_VALUES = ("", False, None)

    def is_ajax(self):
        """Return boolean for platform ajax mechanism or a `'ajax'` query param."""

        return self.request.headers.get(
            "x-requested-with"
        ) == "XMLHttpRequest" or self.request.GET.get("ajax")

    def get_queryset(self):
        """Return empty queryset unless `is_ajax()` is True.  Calls `filter_queryset()`"""

        if self.is_ajax():
            return self.filter_queryset(queryset=self.model.objects.all())
        return self.model.objects.none()

    def get_filters(self):
        """Return form's `cleaned_data` merged over `self.filters`."""

        filter_form = self.get_form()
        if not filter_form.is_valid():
            log.error(
                "%(classname)s: filter validation errors: %(errors)s",
                dict(classname=self.__class__.__name__, errors=filter_form.errors),
            )
        log.info(filter_form.cleaned_data, extra={"status": "cleaned"})

        filters = dict(
            self.filters or {},
            **{
                k: v
                for k, v in filter_form.cleaned_data.items()
                if v not in self.IGNORE_CLEANED_VALUES
            },
        )
        log.info(filters, extra={"status": "processed"})

        return filters

    def filter_queryset(self, queryset, **kwargs):
        """Restrict base `queryset` and apply form's filter values.

        `filter_by_user()`/`filter_by_company()`
        """

        if hasattr(queryset, "filter_by_user"):
            queryset = queryset.filter_by_user(self.request.user, **kwargs)
        elif hasattr(queryset, "filter_by_company"):
            queryset = queryset.filter_by_company(self.request.company, **kwargs)

        filters = self.get_filters()
        queryset = queryset.filter(
            *(Q(**{k: v}) for k, v in filters.items() if v not in self.IGNORE_CLEANED_VALUES)
        )

        return queryset

    def get_initial(self):
        """Supply a dict clone of `self.request.GET`."""

        return self.request.GET.dict()

    def get_form_kwargs(self):
        """For ajax, send the request query params as `data`."""

        kwargs = super(AxisFilterView, self).get_form_kwargs()

        # Like a form view does on POST, load the GET data for ajax requests, so that the filter
        # form is a validation hint about the same data powering the table filter.
        if self.is_ajax():
            kwargs["data"] = {
                k: v for k, v in self.request.GET.items() if v not in self.IGNORE_RAW_VALUES
            }

        return kwargs

    def get_form_class(self):
        """Return supplied `form_class` or build one based on `model`."""

        if self.form_class:
            return self.form_class
        return modelform_factory(self.model, fields=self.fields, exclude=self.exclude)

    def get_form(self, form_class=None):  # pylint: disable=arguments-differ
        """Return form instance with each field's `initial` set to its value in query params."""

        form = super(AxisFilterView, self).get_form()

        for name, field in form.fields.items():
            form.fields[name].initial = self.request.GET.get(name, self.initial.get(name))

        return form


class LegacyAxisDatatableView(LegacyDatatableMixin, AxisListView):
    def get_datatable(self, **kwargs):
        datatable = super(LegacyAxisDatatableView, self).get_datatable(**kwargs)
        columns = [(name, repr(column)) for name, column in datatable.columns.items()]
        identifier = hashlib.sha256(repr(columns).encode("utf-8")).hexdigest()
        datatable.identifier = identifier
        return datatable

    def prevision_kwargs(self, **kwrgs):
        kwargs = {}
        for k, v in kwrgs.items():
            k = k[:-2] if k.endswith("[]") else k

            if v in ["", "undefined", [""], ["undefined"]]:
                v = None
            elif v in ["true", "on", ["true"], ["on"]]:
                v = True
            elif v in ["false", "off", ["false"], ["off"]]:
                v = False
            elif isinstance(v, (list, tuple)) and len(v) == 1:
                v = v[0]
            elif isinstance(v, tuple) and len(v) > 1:
                v = list(v)

            if k not in kwargs:
                kwargs[k] = v
            else:
                if kwargs[k] is None:
                    kwargs[k] = v
                elif isinstance(kwargs[k], (list, tuple)):
                    v = [v] if not isinstance(v, list) else v
                    kwargs[k] += v
                else:
                    existing = [kwargs[k]] if not isinstance(kwargs[k], list) else kwargs[k]
                    v = [v] if not isinstance(v, list) else v
                    kwargs[k] = existing + v
        # print("*x"*10)
        # pprint.pprint(kwargs)
        return kwargs


class AxisDetailMixin(AxisGenericMixin):
    show_edit_button = True
    show_delete_button = True

    def get_edit_url(self):
        return _find_url(self._get_model(), "update", self.get_edit_url_kwargs(pk=self.object.id))

    def get_delete_url(self):
        return _find_url(self._get_model(), "delete", self.get_delete_url_kwargs(pk=self.object.id))

    def get_edit_url_kwargs(self, **kwargs):
        """Returns the kwargs necessary to reverse the "add" url."""
        return kwargs

    def get_delete_url_kwargs(self, **kwargs):
        """Returns the kwargs necessary to reverse the "add" url."""
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AxisDetailMixin, self).get_context_data(**kwargs)
        model = self._get_model()

        if self.show_edit_button:
            can_edit = self.object.can_be_edited(self.request.user)
            edit_url = self.get_edit_url()
        else:
            can_edit = False
            edit_url = None

        if self.show_delete_button:
            can_delete = self.object.can_be_deleted(self.request.user)
            delete_url = self.get_delete_url()
        else:
            can_delete = False
            delete_url = None

        context.update(
            {
                "verbose_name": model._meta.verbose_name,
                "can_edit": can_edit,
                "can_delete": can_delete,
                "edit_url": edit_url,
                "delete_url": delete_url,
            }
        )

        if hasattr(self.object, "relationships"):
            from axis.relationship.models import Relationship

            try:
                relationship = self.object.relationships.get(company_id=self.request.company.id)
            except (Relationship.DoesNotExist, Relationship.MultipleObjectsReturned, ValueError):
                pass
            else:
                if not relationship.is_attached:
                    url_kwargs = {
                        "app_label": model._meta.app_label,
                        "model": model._meta.model_name,
                        "object_id": self.object.id,
                    }
                    add_url = reverse("apiv2:relationship-add", kwargs=url_kwargs)
                    context.update(
                        {
                            "relationship_not_attached": True,
                            "can_edit": False,
                            "can_delete": False,
                            "relationship_url": add_url,
                        }
                    )

        return context


class AxisDetailView(AxisDetailMixin, DetailView):
    pass


class AxisInlineFormSetView(AxisDetailMixin, InlineFormSetView):
    pass


class AxisFormMixin(AxisFormMessagingMixin, AxisGenericMixin):
    show_cancel_button = True

    def get_cancel_url(self):
        """Derives the url to return to if the user presses a Cancel button."""
        if self.show_cancel_button:
            if self.object and self.object.pk:
                view_type = "view"
                view_kwargs = {"pk": self.object.pk}
            else:
                view_type = "list"
                view_kwargs = {}
            model = self._get_model()
            cancel_url = _find_url(model, view_type, self.get_cancel_url_kwargs(**view_kwargs))
        else:
            cancel_url = None

        return cancel_url

    def get_cancel_url_kwargs(self, **kwargs):
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AxisFormMixin, self).get_context_data(**kwargs)
        model = self._get_model()
        context.update(
            {"cancel_url": self.get_cancel_url(), "verbose_name": model._meta.verbose_name}
        )
        return context


class AxisCreateView(AxisFormMixin, CreateView):
    pass


class AxisCreateWithInlinesView(AxisFormMixin, CreateWithInlinesView):
    pass


class AxisUpdateView(AxisFormMixin, UpdateView):
    pass


class AxisUpdateWithInlinesView(AxisFormMixin, UpdateWithInlinesView):
    pass


class AxisExamineMixin(AxisDetailMixin, ExamineMixin):
    pass


class AxisExamineView(AxisExamineMixin, DetailView):
    show_edit_button = False
    show_delete_button = False


class AxisDeleteView(AxisDeleteMessagingMixin, AxisGenericMixin, DeleteView):
    show_cancel_button = True

    def get_cancel_url(self):
        if self.show_cancel_button:
            model = self._get_model()
            cancel_url = _find_url(model, "view", self.get_cancel_url_kwargs(pk=self.object.pk))
        else:
            cancel_url = None
        return cancel_url

    def get_cancel_url_kwargs(self, **kwargs):
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AxisDeleteView, self).get_context_data(**kwargs)
        model = self._get_model()
        context.update(
            {
                "verbose_name": model._meta.verbose_name,
                "cancel_url": self.get_cancel_url(),
            }
        )

        context["deleted_objects"] = collect_nested_object_list(self.object)
        return context


class AxisConfirmView(AxisConfirmMessagingMixin, AxisGenericMixin, DeleteView):
    """Provides a confirmation-based workflow using the built-in ``DeleteView`` class."""

    show_cancel_button = True

    def post(self, request, *args, **kwargs):
        return self.confirm(request, *args, **kwargs)

    def get_cancel_url(self):
        raise NotImplementedError("Please explicitly define a get_cancel_url()")

    def get_cancel_url_kwargs(self, **kwargs):
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AxisConfirmView, self).get_context_data(**kwargs)
        if self.show_cancel_button:
            context["cancel_url"] = self.get_cancel_url()
        return context


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs["content_type"] = "application/json"
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = {
                "pk": self.object.pk,
            }
            return self.render_to_json_response(data)
        else:
            return response
