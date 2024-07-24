"""api.py: Django filehandling"""

import logging
from collections import defaultdict
from itertools import starmap

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.utils import timezone


from rest_framework import viewsets, serializers, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from axis.core.utils import make_safe_field
from axis.core.utils import randomize_filename
from axis.examine.api.restframework import ExamineViewSetAPIMixin
from .models import AsynchronousProcessedDocument, CustomerDocument, DOCUMENT_TYPES
from .views import colored_state
from .forms import CustomerDocumentForm
from .utils import get_mimetype_category

__author__ = "Steven Klass"
__date__ = "3/4/14 1:19 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
filehandling_app = apps.get_app_config("filehandling")


def customerdocument_viewset_factory(model):
    if isinstance(model, str):
        model = apps.get_model(*model.split(".", 1))
    ViewSet = type(
        str("%sCustomerDocumentViewSet" % (model.__name__,)),
        (CustomerDocumentViewSet,),
        {"object_model": model},
    )
    return ViewSet


class FileHandlingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsynchronousProcessedDocument
        fields = "__all__"


class FileHandlingViewSet(viewsets.ReadOnlyModelViewSet):
    model = AsynchronousProcessedDocument
    queryset = AsynchronousProcessedDocument.objects.filter(result__isnull=False)
    serializer_class = FileHandlingSerializer

    def get_latest_from_dict(self, results):
        try:
            latest = results["latest"]
            if isinstance(latest, logging.LogRecord):
                latest = latest.getMessage()
        except (KeyError, TypeError):
            latest = ""
        return latest

    def get_row_logs(self, key, value):
        has_errors = value.pop("has_errors")
        return {"row": key, "logs": value, "has_errors": has_errors}

    def get_chrono_split_by_minute(self, chronological):
        temp = defaultdict(list)
        for string in chronological:
            split = string.index("]") + 1
            key = string[:split]
            message = string[split:]
            temp[key].append(message)
        return temp

    @action(detail=True)
    def chronological(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        try:
            data = obj.result["chronological"]
        except KeyError:
            data = {"response": "to new for that"}
        else:
            temp = self.get_chrono_split_by_minute(data)
            return Response(temp)

        return Response(data)

    @action(detail=True)
    def row_context(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        try:
            data = obj.result["by_context_row"]
        except KeyError:
            data = {"response": "we don't have that key"}
        else:
            temp = list(starmap(self.get_row_logs, iter(data.items())))
            return Response(temp)

        return Response(data)

    @action(detail=True)
    def results(self, request, pk=None, *args, **kwargs):
        obj = self.get_object()
        results = obj.result.copy()
        if results.get("latest"):
            del results["latest"]

        by_context_row = list(starmap(self.get_row_logs, results.get("by_context_row", {}).items()))
        results["by_context_row"] = sorted(by_context_row, key=lambda context: str(context["row"]))
        results["chronological"] = self.get_chrono_split_by_minute(results.get("chronological", []))

        if not isinstance(results.get("result"), str):
            results["result"] = "{}".format(results.get("result", "No Results"))

        return Response(results)

    @action(detail=True)
    def latest(self, request, pk=None, *args, **kwargs):
        # default to not complete and get object
        data = {"complete": False}
        obj = self.get_object()

        # what's the latest
        data["latest"] = self.get_latest_from_dict(obj.result)

        obj.update_results()

        data["state"] = colored_state(obj.get_state())
        if obj.final_status in ["SUCCESS", "FAILURE"]:
            data["complete"] = True

        return Response(data)


class CustomerDocumentSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(read_only=True)
    filetype = serializers.CharField(read_only=True)
    url = make_safe_field(serializers.CharField)(source="document.url", read_only=True)
    preview_link = serializers.SerializerMethodField()

    class Meta:
        model = CustomerDocument

        # "document" is readonly while we are the only ones using the api... we only send
        # document_raw.  This serializer should be updated to transition "raw" base64 the way the
        # HomeDocumentForm does.
        fields = (
            "id",
            "company",
            "document",
            "type",
            "description",
            "content_type",
            "object_id",
            "is_public",
            "is_active",
            "login_required",
            "created_on",
            "last_update",
            "filesize",
            # Virtual
            "filename",
            "filetype",
            "url",
            "preview_link",
        )
        read_only_fields = (
            "id",
            "company",
            "document",
            "content_type",
            "filesize",
            "type",
        )

    def get_preview_link(self, instance: CustomerDocument) -> str:
        url = instance.get_preview_link()
        if "request" in self.context:
            return self.context["request"].build_absolute_uri(url)
        return url


class CustomerDocumentValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDocument
        fields = ("type", "description", "is_public", "login_required", "is_active")


class CustomerDocumentViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = CustomerDocument
    serializer_class = CustomerDocumentSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("object_id",)

    object_model = None  # content_object's Model, filled in by factory
    content_type = None

    def upload_to(self, company, filename):
        return "documents/{company_type}/{company_id}/{filename}".format(
            company_type=company.company_type,
            company_id=company.id,
            filename=randomize_filename(filename),
        )

    @action(detail=False, methods=["post"])
    def validate(self, request, *args, **kwargs):
        data = request.data
        serializer = CustomerDocumentValidationSerializer(data=data)
        form = CustomerDocumentForm(data=data, raw_file_only=True)
        if serializer.is_valid() and form.is_valid():
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        errors = dict(serializer.errors, **form.errors)
        return Response(errors, status_code)

    @action(detail=True, methods=["post"])
    def signing_url(self, *args, **kwargs):
        instance = self.get_object()
        return Response(
            {
                "url": instance.get_signing_url(
                    self.request.user,
                    key=self.request.query_params.get("document"),
                    postback_url="{prefix}{url}".format(
                        prefix=settings.DOCUSIGN_POSTBACK_PREFIX,
                        url=self.request.path + "-callback",
                    ),
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[
            permissions.AllowAny,
        ],
    )
    def docusign_callback(self, *args, **kwargs):
        """Create a customer document and call an fsm transition on the waiting content_object."""
        instance = self.get_object()
        signed_document = self.request.FILES["document"]
        date = timezone.now().date()

        obj = instance.content_object
        user_id = obj.data["user_id"]
        user = get_user_model().objects.get(pk=user_id)

        result_key = self.request.query_params.get("document")
        filename = obj.data[result_key]["return_filename"]

        # FIXME: Not ideal. We'll need a way to get this from a common instance method
        if result_key == "unsigned_upload_result":
            signing_transition = obj.sign
        elif result_key == "countersigning_upload_result":
            signing_transition = obj.countersign
        elif result_key == "document_result":
            signing_transition = obj.sign
        else:
            raise ValueError("Unknown document parameter given: %r" % (result_key,))

        # Create a clone of the CustomerDocument, with selective updates
        instance.pk = None
        instance.description = "Via DocuSign ({date})".format(date=date)
        instance.document.name = default_storage.save(
            self.upload_to(
                user.company,
                "{filename}({date}).pdf".format(filename=filename, date=date),
            ),
            signed_document,
        )
        instance.save()

        # Transition with the new customer_document id remembered as the signed document
        signing_transition(instance.pk)
        obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = self.model.objects.all()
        ct = ContentType.objects.get_for_model(self.object_model)
        queryset = queryset.filter(content_type=ct)
        return queryset

    def get_examine_machinery_classes(self):
        from axis.customer_hirl.models import (
            BuilderAgreement as HIRLBuilderAgreement,
            VerifierAgreement as HIRLVerifierAgreement,
        )

        from axis.home.models import Home
        from axis.subdivision.models import Subdivision
        from axis.floorplan.models import Floorplan
        from axis.company.models import Company
        from axis.builder_agreement.models import BuilderAgreement
        from axis.checklist.models import CollectedInput, Answer, QAAnswer
        from axis.qa.models import QAStatus, QANote
        from axis.qa.views.examine import QADocumentBase
        from axis.qa.views import QADocumentCustomerHIRLBase
        from axis.home.views.machineries import HomeDocumentAgreementBase
        from axis.customer_hirl.builder_agreements.examine.base import (
            NGBSDocumentAgreementBase,
        )
        from .machinery import customerdocument_machinery_factory

        return {
            "HomeCustomerDocumentMachinery": customerdocument_machinery_factory(
                Home,
                allow_multiple=True,
                bases=(HomeDocumentAgreementBase,),
            ),
            "SubdivisionCustomerDocumentMachinery": customerdocument_machinery_factory(Subdivision),
            "FloorplanCustomerDocumentMachinery": customerdocument_machinery_factory(Floorplan),
            "CompanyCustomerDocumentMachinery": customerdocument_machinery_factory(Company),
            "BuilderAgreementCustomerDocumentMachinery": customerdocument_machinery_factory(
                BuilderAgreement
            ),
            "QAStatusCustomerDocumentMachinery": customerdocument_machinery_factory(
                QAStatus, bases=(QADocumentBase,)
            ),
            "QANoteCustomerDocumentMachinery": customerdocument_machinery_factory(
                QANote, bases=(QADocumentBase,)
            ),
            "QADocumentCustomerHIRLMachinery": customerdocument_machinery_factory(
                QAStatus,
                machinery_name="QADocumentCustomerHIRLMachinery",
                bases=(QADocumentCustomerHIRLBase,),
            ),
            "HIRLBuilderAgreementCustomerDocumentMachinery": customerdocument_machinery_factory(
                HIRLBuilderAgreement,
                allow_delete=False,
                bases=(NGBSDocumentAgreementBase,),
                # Avoid model name clash with only model.__name__ available for hinting
                machinery_name="HIRLBuilderAgreementCustomerDocumentMachinery",
                dependency_name="hirl_builder_agreement",
                api_name="hirl_builder_agreement_documents",
            ),
            "HIRLVerifierAgreementCustomerDocumentMachinery": customerdocument_machinery_factory(
                HIRLVerifierAgreement,
                allow_delete=False,
                bases=(NGBSDocumentAgreementBase,),
                # Avoid model name clash with only model.__name__ available for hinting
                machinery_name="HIRLVerifierAgreementCustomerDocumentMachinery",
                dependency_name="hirl_verifier_agreement",
                api_name="hirl_verifier_agreement_documents",
            ),
            # FIXME: Make this work without a machinery?
            # Hacks for special behavior that aren't really machinery names
            "input-collection": customerdocument_machinery_factory(CollectedInput),
            "answer": customerdocument_machinery_factory(Answer),
            "qaanswer": customerdocument_machinery_factory(QAAnswer),
        }

    def _save(self, serializer):
        # pre-save
        machinery_class = self.get_examine_machinery_class()
        form_class = machinery_class.form_class
        valid_content_types = machinery_class.valid_content_types
        document_form = form_class(
            data=self.request.data,
            raw_file_only=True,
            valid_content_types=valid_content_types,
        )
        if not document_form.is_valid():
            errors = document_form.errors
            if "document_raw" in errors:
                errors["document"] = errors.pop("document_raw")
            raise ValidationError(errors)  # bad request

        # save
        obj = serializer.save(
            **{
                "company": self.request.user.company,
                "content_type": ContentType.objects.get_for_model(self.object_model),
                "object_id": int(self.request.data["object_id"]),
            }
        )

        # post-save
        document_form = form_class(
            data=self.request.data,
            instance=obj,
            raw_file_only=True,
            valid_content_types=valid_content_types,
        )
        document_form.save()

        if document_form.cleaned_data.get("document"):
            obj.filesize = document_form.cleaned_data["document"].size
            if not obj.type:
                type_category = get_mimetype_category(obj.filename)  # property of saved instance
                obj.type = dict(DOCUMENT_TYPES).get(type_category, "document").lower()
            obj.save()

    def perform_create(self, serializer):
        self._save(serializer)

    def perform_update(self, serializer):
        self._save(serializer)
