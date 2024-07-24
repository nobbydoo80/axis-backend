import json
import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from axis.filehandling.models import DOCUMENT_TYPES
from axis.filehandling.utils import get_mimetype_category
from ..forms import AjaxBase64FileFormMixin
from ..utils import ExamineJSONEncoder

__author__ = "Autumn Valenta"
__date__ = "10/17/14 3:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = []

log = logging.getLogger(__name__)


class ExamineRestFrameworkJSONRenderer(JSONRenderer):
    encoder_class = ExamineJSONEncoder


class ExamineViewSetAPIMixin(object):
    """
    ViewSet support mixin that provides tools that help a normal model viewset respond appropriately
    for the AxisExamineView to work.
    """

    renderer_classes = (ExamineRestFrameworkJSONRenderer,)
    examine_machinery_class = None
    examine_machinery_classes = None  # dict of names to classes

    @action(detail=True)
    def region(self, request, *args, **kwargs):
        """Serializes the region object and return as JSON."""
        machinery_class = self.examine_machinery_class
        try:
            self.object = self.get_object()
            region = self.get_region(examine_machinery_class=machinery_class, instance=self.object)
        except AttributeError as err:
            if self.get_object() is not None:
                log.exception(
                    "Houston we have a problem with %r and %r -- %r",
                    machinery_class,
                    self.get_object(),
                    err,
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(region)

    @action(detail=False)
    def new_region(self, request, *args, **kwargs):
        """Serializes a fresh region object with an unsaved object and return as JSON."""
        machinery_class = self.examine_machinery_class
        self.object = self.get_object()
        region = self.get_region(examine_machinery_class=machinery_class, instance=self.object)
        return Response(region)

    def get_object(self):
        """Imitate default APIView behavior, but allow for unspecified pk conditions."""
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup = self.kwargs.get(lookup_url_kwarg, None)

        if lookup is None:
            # Normally this is a configuration error, but if the view is a @action(detail=False),
            # then we will generate an unsaved blank object.
            return queryset.model()

        return super(ExamineViewSetAPIMixin, self).get_object()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        handle_documents = False
        machinery_class = self.get_examine_machinery_class()
        if machinery_class:
            machinery = self.get_machinery(
                instance=(getattr(self, "model", None) or self.get_queryset().model)()
            )
            form_class = machinery.get_form_class()
            handle_documents = AjaxBase64FileFormMixin in form_class.__mro__ and any(
                [
                    request.data.get("{name}_raw".format(name=name))
                    for name in form_class._raw_source_fields
                ]
            )

        if handle_documents:
            self.pre_validate_documents(machinery)
        self.perform_create(serializer)
        if handle_documents:
            self.save_documents(machinery, instance=serializer.instance)

        headers = self.get_success_headers(serializer.data)
        return self._build_examine_response(
            serializer.instance, created=True, headers=headers, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        handle_documents = False
        machinery_class = self.get_examine_machinery_class()
        if machinery_class:
            machinery = self.get_machinery(instance)
            form_class = machinery.get_form_class()
            handle_documents = AjaxBase64FileFormMixin in form_class.__mro__ and any(
                [
                    request.data.get("{name}_raw".format(name=name))
                    for name in form_class._raw_source_fields
                ]
            )

        if handle_documents:
            self.pre_validate_documents(machinery)
        self.perform_update(serializer)
        if handle_documents:
            self.save_documents(machinery, instance=serializer.instance)

        return self._build_examine_response(instance)

    def destroy(self, request, *args, **kwargs):
        self.object = self.get_object()
        machinery_class = self.get_examine_machinery_class(raise_exception=False)
        if machinery_class:
            machinery = self.get_machinery(self.object)
            success_url = machinery.get_delete_success_url()
        else:
            success_url = None

        super(ExamineViewSetAPIMixin, self).destroy(request, *args, **kwargs)

        if success_url:
            return Response({"url": success_url}, status=status.HTTP_200_OK)
        return Response(status.HTTP_204_NO_CONTENT)

    def pre_validate_documents(self, machinery):
        form_class = machinery.get_form_class()
        content_types = getattr(machinery, "valid_content_types", form_class.valid_content_types)
        document_fields = form_class._raw_source_fields
        document_form = form_class(
            data=self.request.data,
            user=self.request.user,
            raw_file_only=True,
            valid_content_types=content_types,
        )
        if not document_form.is_valid():
            errors = document_form.errors
            for name in document_fields:
                name_raw = "{name}_raw".format(name=name)
                if name_raw in errors:
                    errors[name] = errors.pop(name_raw)
            raise ValidationError(errors)  # bad request
        return document_form

    def save_documents(self, machinery, instance, **kwargs):
        kwargs["user"] = self.request.user
        form_class = machinery.get_form_class()
        content_types = getattr(machinery, "valid_content_types", form_class.valid_content_types)
        document_fields = form_class._raw_source_fields
        document_form = form_class(
            data=self.request.data,
            raw_file_only=True,
            valid_content_types=content_types,
            instance=instance,
            **kwargs,
        )
        if not document_form.is_valid():
            raise ValidationError(document_form.errors)
        document_form.save()

        if not hasattr(instance, "filesize"):
            return

        # Alter file info fields now that file is concrete
        for name in document_fields:
            if document_form.cleaned_data.get(name):
                instance.filesize = document_form.cleaned_data[name].size
                if not instance.type:
                    type_category = get_mimetype_category(instance.filename)
                    instance.type = dict(DOCUMENT_TYPES).get(type_category, name).lower()
                instance.save()

    def _build_examine_response(self, instance, created=False, **response_kwargs):
        region = self.get_region(self.examine_machinery_class, instance=instance)
        return Response(region, **response_kwargs)

    def get_machinery_context(self, **kwargs):
        """
        Returns the GET parameter context data in the request for instantiating the examine
        machinery.
        """
        context = {
            "request": self.request,
        }

        def load_value(v):
            """Lightweight json deserialization for GET parameters"""
            if v in {"true", "false", "null"}:
                return json.loads(v)
            try:
                float(v)
            except ValueError:
                return v
            else:
                return json.loads(v)

        for k, v_list in iter(self.request.query_params.lists()):
            v_list = list(map(load_value, v_list))
            if len(v_list) == 1:
                v = v_list[0]
            else:
                v = v_list
            context[k] = v
        context.update(kwargs)
        return context

    def get_examine_machinery_class(self, raise_exception=True):
        machinery_class = self.examine_machinery_class
        machinery_classes = self.get_examine_machinery_classes()

        machinery_name = self.request.query_params.get("machinery", None)
        machinery_class = machinery_classes.get(machinery_name)

        if machinery_class:
            return machinery_class

        if None in machinery_classes:
            return machinery_classes[None]

        if raise_exception:
            raise ValueError(
                "%s must provide 'examine_machinery_class' or return one from"
                " 'get_examine_machinery_class()'" % (self.__class__.__name__,)
            )

        return None

    def get_examine_machinery_classes(self):
        return self.examine_machinery_classes or {}

    def get_machinery(self, instance, machinery_class=None, create_new=False, **kwargs):
        """Instantiates and returns the machinery instance."""
        kwargs["context"] = self.get_machinery_context(**(kwargs.get("context") or {}))
        if machinery_class is None:
            machinery_class = self.get_examine_machinery_class()
        return machinery_class(instance=instance, create_new=create_new, **kwargs)

    def get_region(self, examine_machinery_class, instance=None, **kwargs):
        """Returns a region for the target object."""
        create_new = (instance.pk is None) and ("pk" not in self.kwargs)
        machinery = self.get_machinery(
            instance, machinery_class=examine_machinery_class, create_new=create_new, **kwargs
        )

        # If the machinery is hijacking the meaning of its get_objects() method, it is possible that
        # an empty list is returned at this stage, so we'll allow None to be returned.  This will
        # create an empty response serialization.
        regions = machinery.get_regions()
        if regions:
            return regions[0]
        return None
