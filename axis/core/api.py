"""api.py: ViewSet definitions for axis we don't control"""


import json
import logging
from functools import partial
from itertools import chain

from celery.app import app_or_default
from django.apps import apps
from django.conf import settings
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import serialize as django_serialize
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.timezone import now
from impersonate.helpers import check_allow_for_user
from impersonate.signals import session_begin, session_end
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from zdesk import Zendesk, get_id_from_url

from axis.annotation.api import (
    AnnotationViewSet,
    BaseContentTypeAnnotationViewSet,
    BaseFieldAnnotationsViewSet,
)
from axis.community.models import Community
from axis.company.models import Company
from axis.core.messages import TrainingCreatedStatusCompanyMessage
from axis.core.models import RecentlyViewed, ContactCard, ContactCardPhone, ContactCardEmail
from axis.customer_hirl.models import HIRLUserProfile
from axis.customer_hirl.serializers import HIRLUserProfileSerializer
from axis.examine.api.restframework import ExamineViewSetAPIMixin, ExamineRestFrameworkJSONRenderer
from axis.home.models import Home, EEPProgramHomeStatus
from axis.incentive_payment.models import IncentiveDistribution
from axis.subdivision.models import Subdivision
from axis.user_management.models import Training, Accreditation, InspectionGrade
from axis.core.serializers import ContactCardPhoneSerializer, ContactCardEmailSerializer

from .serializers import (
    UserSerializer,
    BasicUserSerializer,
    FlatUserSerializer,
    UserTrainingSerializer,
    UserAccreditationSerializer,
    UserCertificationMetricSerializer,
    UserInspectionGradeSerializer,
    ContentTypeSerializer,
    RelationshipsSerializer,
    NestedObjectsSerializer,
    ContactCardSerializer,
)
from axis.core.views.machinery import object_relationships_machinery_factory

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)
User = get_user_model()


class UserViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = User
    queryset = model.objects.all().select_related("company")

    def get_queryset(self):
        queryset = super(UserViewSet, self).get_queryset()
        return queryset.filter_by_user(user=self.request.user)

    def get_serializer_class(self):
        user = self.get_object()
        if (
            self.request.user.is_superuser
            or self.request.user == user
            or (self.request.user.is_company_admin and self.request.user.company == user.company)
        ):
            return UserSerializer
        return BasicUserSerializer

    def get_serializer(self, *args, **kwargs):
        # do this hack because examine view call `get_serializer_class` without kwargs
        # and we need to define kwargs['pk'] for self.get_object() method
        if kwargs.get("instance"):
            self.kwargs["pk"] = kwargs["instance"].pk
        return super(UserViewSet, self).get_serializer(*args, **kwargs)

    def get_examine_machinery_classes(self):
        from .views.machineries import UserExamineMachinery

        return {
            "UserExamineMachinery": UserExamineMachinery,
        }

    def get_latest_homes(self, company):
        """Return the latest homes by a company"""
        results = []
        try:
            homes = company.relationships.get_homes().order_by("-modified_date")[:10]
            home_id_city_dict = dict(homes.values_list("id", "city__name"))
            home_id_subdivision_dict = dict(homes.values_list("id", "subdivision__name"))
            for home in homes:
                url = "<a href='{}'>{}</a>".format(
                    home.get_absolute_url(), home.get_home_address_display()
                )
                if home_id_subdivision_dict.get(home.id) and home_id_city_dict.get(home.id):
                    addr = "{}, {}".format(
                        home_id_subdivision_dict[home.id], home_id_city_dict[home.id]
                    )
                else:
                    addr = home_id_city_dict.get(home.id, "")
                results.append({"url": url, "address": addr})
        except (AttributeError, ObjectDoesNotExist):
            pass
        return results

    @action(detail=True)
    def latest_stats(self, request, pk=None, *args, **kwargs):
        # FIXME: what to do with these returns?
        if not hasattr(self.request.user, "company") or self.request.user.company is None:
            return
        if self.request.user.company.company_type == "builder":
            return

        company = self.request.user.company

        ytd_certified = EEPProgramHomeStatus.objects.get_ytd_certified_count(company)
        prior_year_certified = EEPProgramHomeStatus.objects.get_prior_year_certified_count(company)
        mtd_certified = EEPProgramHomeStatus.objects.get_mtd_certified_count(company)
        prior_month_certified = EEPProgramHomeStatus.objects.get_prior_month_certified_count(
            company
        )
        stats_count = EEPProgramHomeStatus.objects.get_status_counts(company)

        data = {
            "latest_homes": self.get_latest_homes(company),
            "ytd_certified_count": ytd_certified,
            "prior_year_certified_count": prior_year_certified,
            "mtd_certified_count": mtd_certified,
            "prior_month_certified_count": prior_month_certified,
            "stats_count": stats_count,
        }

        return Response(data)

    @action(detail=True)
    def error_test(self, request, pk=None, *args, **kwargs):
        # Simply test out our errors to make sure that we can hit an error and verify it shows up
        # in logs.

        log.error("Error API Test")

        try:
            User.objects.get(id=2222222)
        except:  # noqa: E722
            log.exception("API Handled Error")

        data = User.objects.get(id=4444444)
        return Response(data)

    @action(detail=False)
    def impersonate_list(self, request, *args, **kwargs):
        qs = User.objects.filter(is_superuser=False, is_active=True).select_related("company")
        serializer = FlatUserSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def impersonate_start(self, request, *args, **kwargs):
        impersonate_user = self.get_object()
        if check_allow_for_user(request, impersonate_user):
            request.session["_impersonate"] = impersonate_user.pk
            request.session.modified = True
            session_begin.send(
                sender=None,
                impersonator=request.user,
                impersonating=impersonate_user,
                request=request,
            )
            if hasattr(request, "jwt"):
                refresh_token = RefreshToken.for_user(impersonate_user)
                refresh_token["impersonator"] = self.request.user.pk

                data = {
                    "refresh": "{}".format(refresh_token),
                    "access": "{}".format(refresh_token.access_token),
                }
                return Response(data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def impersonate_stop(self, request, *args, **kwargs):
        impersonating = request.session.pop("_impersonate", None)
        jwt_impersonator = None
        if hasattr(request, "jwt"):
            try:
                jwt_impersonator = User.objects.get(pk=request.jwt.get("impersonator"))
            except User.DoesNotExist:
                raise ValidationError("{impersonator} not found")

        if impersonating:
            request.session.modified = True
            session_end.send(
                sender=None,
                impersonator=request.impersonator,
                impersonating=impersonating,
                request=request,
            )
        if jwt_impersonator:
            refresh_token = RefreshToken.for_user(jwt_impersonator)
            data = {
                "refresh": "{}".format(refresh_token),
                "access": "{}".format(refresh_token.access_token),
            }
            return Response(data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AxisTokenObtainPairView(TokenObtainPairView):
    """
    Extend TokenObtainPairView by adding functionality to
    create impersonation token based on user session
    """

    def post(self, request, *args, **kwargs):
        """Upon successful login, ensure the user session is initialized."""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        login(request, serializer.user)

        if request.user.is_authenticated and "_impersonate" in request.session:
            new_user_id = request.session["_impersonate"]
            if isinstance(new_user_id, User):
                # Edge case for issue 15
                new_user_id = new_user_id.pk
            try:
                new_user = User.objects.get(pk=new_user_id)
            except User.DoesNotExist:
                return
            refresh_token = RefreshToken.for_user(new_user)
            refresh_token["impersonator"] = self.request.user.pk

            data = {
                "refresh": "{}".format(refresh_token),
                "access": "{}".format(refresh_token.access_token),
            }
            return Response(data)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserTrainingViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Training
    queryset = Training.objects.all()
    serializer_class = UserTrainingSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.machineries import UserTrainingExamineMachinery

        return UserTrainingExamineMachinery

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        for training_status in serializer.instance.trainingstatus_set.all():
            self._send_new_training_created_message(
                training=serializer.instance, status_company=training_status.company
            )
        return self._build_examine_response(
            serializer.instance, created=True, headers=headers, status=status.HTTP_201_CREATED
        )

    def _send_new_training_created_message(self, training, status_company):
        TrainingCreatedStatusCompanyMessage().send(
            company=status_company,
            context={
                "trainee": training.trainee,
                "url": reverse_lazy("profile:detail", kwargs={"pk": training.trainee.pk}),
                "training": training,
            },
        )


class UserAccreditationViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Accreditation
    queryset = Accreditation.objects.all()
    serializer_class = UserAccreditationSerializer

    def get_examine_machinery_classes(self):
        from .views.machineries import UserAccreditationExamineMachinery

        return {"UserAccreditationExamineMachinery": UserAccreditationExamineMachinery}


class UserCertificationMetricViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = EEPProgramHomeStatus
    queryset = EEPProgramHomeStatus.objects.all()
    serializer_class = UserCertificationMetricSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.machineries import UserCertificationMetricExamineMachinery

        return UserCertificationMetricExamineMachinery


class UserInspectionGradeViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = InspectionGrade
    queryset = InspectionGrade.objects.all()
    serializer_class = UserInspectionGradeSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.machineries import UserInspectionGradeExamineMachinery

        return UserInspectionGradeExamineMachinery


class HIRLUserProfileViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = HIRLUserProfile
    queryset = HIRLUserProfile.objects.all()
    serializer_class = HIRLUserProfileSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        from .views.machineries import HIRLUserProfileExamineMachinery

        return HIRLUserProfileExamineMachinery


class ContactCardViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = ContactCard
    queryset = ContactCard.objects.all()
    serializer_class = ContactCardSerializer

    def get_examine_machinery_classes(self, raise_exception=True):
        from .views.machineries import (
            ContactCardExamineMachinery,
            ContactCardReadOnlyExamineMachinery,
        )

        return {
            None: ContactCardExamineMachinery,
            "ContactCardExamineMachinery": ContactCardExamineMachinery,
            "ContactCardReadOnlyExamineMachinery": ContactCardReadOnlyExamineMachinery,
        }


class ContactCardPhoneViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = ContactCardPhone
    queryset = ContactCardPhone.objects.all()
    serializer_class = ContactCardPhoneSerializer

    def get_examine_machinery_classes(self, raise_exception=True):
        from .views.machineries import (
            ContactCardPhoneExamineMachinery,
            ContactCardPhoneReadOnlyExamineMachinery,
        )

        return {
            None: ContactCardPhoneExamineMachinery,
            "ContactCardPhoneExamineMachinery": ContactCardPhoneExamineMachinery,
            "ContactCardPhoneReadOnlyExamineMachinery": ContactCardPhoneReadOnlyExamineMachinery,
        }


class ContactCardEmailViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = ContactCardEmail
    queryset = ContactCardEmail.objects.all()
    serializer_class = ContactCardEmailSerializer

    def get_examine_machinery_classes(self, raise_exception=True):
        from .views.machineries import (
            ContactCardEmailExamineMachinery,
            ContactCardEmailReadonlyExamineMachinery,
        )

        return {
            None: ContactCardEmailExamineMachinery,
            "ContactCardEmailExamineMachinery": ContactCardEmailExamineMachinery,
            "ContactCardEmailReadonlyExamineMachinery": ContactCardEmailReadonlyExamineMachinery,
        }


class RecentItemViewSet(viewsets.ReadOnlyModelViewSet):
    model = RecentlyViewed

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        object_type = self.request.query_params.get("object_type")
        if not object_type:
            raise ValueError("{object_type} is not provided")
        limit = int(self.request.query_params.get("limit", 5))
        queryset = self.get_queryset()
        ct_map = {
            "company": Company,
            "incentive_payment": IncentiveDistribution,
            "subdivision": Subdivision,
            "community": Community,
            "home": Home,
        }

        try:
            queryset = queryset.filter(
                content_type=ContentType.objects.get_for_model(ct_map[object_type])
            )
        except KeyError:
            return Response([])

        queryset = queryset.order_by("-updated_at")
        queryset = queryset[:limit]

        results = []
        if object_type == "company":
            for instance in queryset:
                try:
                    results.append(
                        {
                            "pk": instance.pk,
                            "name": instance.content_object.name,
                            "url": instance.content_object.get_absolute_url(),
                        }
                    )
                except AttributeError:
                    pass
        elif object_type == "incentive_payment":
            for instance in queryset:
                try:
                    results.append(
                        {
                            "pk": instance.pk,
                            "name": instance.content_object.customer.name,
                            "url": instance.content_object.get_absolute_url(),
                        }
                    )
                except AttributeError:
                    pass
        elif object_type == "subdivision":
            for instance in queryset:
                try:
                    results.append(
                        {
                            "pk": instance.pk,
                            "name": instance.content_object.name,
                            "url": instance.content_object.get_absolute_url(),
                        }
                    )
                except AttributeError:
                    pass
        elif object_type == "community":
            for instance in queryset:
                try:
                    results.append(
                        {
                            "pk": instance.pk,
                            "name": instance.content_object.name,
                            "url": instance.content_object.get_absolute_url(),
                        }
                    )
                except AttributeError:
                    pass
        elif object_type == "home":
            for instance in queryset:
                try:
                    results.append(
                        {
                            "pk": instance.pk,
                            "name": instance.content_object.get_home_address_display(),
                            "url": instance.content_object.get_absolute_url(),
                        }
                    )
                except AttributeError:
                    pass
        return Response(results)


class ContentTypeViewSet(viewsets.ModelViewSet):
    model = ContentType
    queryset = model.objects.all()
    serializer_class = ContentTypeSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(**self.request.query_params.dict())


class DumpDataView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [JSONRenderer]

    def get(self, request, label, pk):
        collector = NestedObjects(using="default")
        collector.collect([self.get_object()])
        objects = list(chain.from_iterable(collector.data.values()))

        fixture_json = json.loads(django_serialize("json", objects))
        response = Response(fixture_json)
        response["Content-Disposition"] = "attachment; filename={label}-{pk}_{date}.json".format(
            label=label.replace(".", "-").lower(), pk=pk, date=now().date().strftime("%Y-%m-%d")
        )
        return response

    def get_object(self):
        model_class = apps.get_model(self.kwargs["label"])
        return model_class.objects.get(pk=self.kwargs["pk"])


class CeleryJobsViewSet(viewsets.GenericViewSet):
    @action(detail=True)
    def queues(self, request, *args, **kwargs):
        app = app_or_default()
        inspect = app.control.inspect()
        return Response(inspect.active_queues())

    @action(detail=True)
    def active(self, request, *args, **kwargs):
        app = app_or_default()
        inspect = app.control.inspect()
        return inspect.active()

    @action(detail=True)
    def reserved(self, request, *args, **kwargs):
        app = app_or_default()
        inspect = app.control.inspect()
        return inspect.reserved()

    @action(detail=True)
    def scheduled(self, request, *args, **kwargs):
        app = app_or_default()
        inspect = app.control.inspect()
        return inspect.scheduled()

    @action(detail=True)
    def revoked(self, request, *args, **kwargs):
        app = app_or_default()
        inspect = app.control.inspect()
        return inspect.revoked()

    @action(detail=True)
    def stats(self, request, *args, **kwargs):
        app = app_or_default()
        inspect = app.control.inspect()
        return inspect.revoked()

    @action(detail=True)
    def status(self, request, *args, **kwargs):
        app = app_or_default()
        inspect = app.control.inspect()
        return inspect.revoked()


class ZendeskViewSet(ExamineViewSetAPIMixin, viewsets.GenericViewSet):
    client_url_string = "http://support.pivotalenergysolutions.com/requests/{id}"

    @action(detail=False, methods=["post"])
    def new_ticket(self, request, *args, **kwargs):
        data = {"request": request.data}
        zendesk_client = Zendesk(
            "https://pivotalenergysolutions.zendesk.com",
            zdesk_email=settings.ZENDESK_AGENT_EMAIL,
            zdesk_password=settings.ZENDESK_AGENT_PASSWORD,
        )

        response = zendesk_client.request_create(data)
        ticket_id = get_id_from_url(response)
        response = zendesk_client.request_show(ticket_id)

        response["request"]["api_url"] = response["request"]["url"]
        response["request"]["url"] = self.client_url_string.format(id=ticket_id)

        return Response(response)


class _BaseRelationshipsViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    """
    Generic Relationships viewset, not to be used directly, but subclassed to provide a target
    model class.
    """

    # If there are ever Relationship api modifications, they can be made here and will influence
    # all such generated viewsets.

    # An explicit set of types can be declared on a subclass to change how the serializer manages
    # the company type fields.
    # For sanity, this should match the same declaration on the RelationshipsSerializer class.
    # This one will trump the serializer version, and specifying GET-style query_params on the url
    # will trump this list (sent by configuring a RelationshipExamineMachinery.company_types).
    company_types = [
        "builder",
        "rater",
        "provider",
        "eep",
        "hvac",
        "qa",
        "general",
        "gas_utility",
        "electric_utility",
        "architect",
        "developer",
        "communityowner",
    ]

    def get_serializer_class(self):
        class Meta:
            model = self.model

        serializer_name = str("{}RelationshipsSerializer".format(self.model.__name__))
        return type(
            serializer_name,
            (RelationshipsSerializer,),
            {
                "Meta": Meta,
            },
        )

    # Generic *args **kwargs version of normal method so that we can pass configuration to the
    # serializer class init.
    def get_serializer(self, *args, **kwargs):
        """Ensures serializer is informed of requested company_type list."""
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        kwargs["company_types"] = self.get_company_types()
        kwargs["context"]["creating"] = self.request.query_params.get("creating")
        return serializer_class(*args, **kwargs)

    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import HomeRelationshipsExamineMachinery

        machinery_factory = partial(
            object_relationships_machinery_factory,
            self.model,
            company_types=self.get_company_types(),
        )
        return {
            None: machinery_factory(),
            "HomeRelationshipsExamineMachinery": machinery_factory(
                bases=(HomeRelationshipsExamineMachinery,)
            ),
        }

    def get_queryset(self):
        return self.model.objects.all()

    def get_company_types(self):
        """Filters the original set of company types by a query_params list of target fields."""
        field_names = self.request.query_params.getlist("fields")
        if field_names:
            fields = list(set(field_names) & set(self.company_types))
        else:
            fields = self.company_types
        return fields

    def _save(self, serializer):
        from axis.home.models import Home
        from axis.home.tasks import update_home_states

        instance = serializer.save()
        if isinstance(instance, Home):
            for homestatus_id in list(instance.homestatuses.values_list("id", flat=True)):
                update_home_states(
                    eepprogramhomestatus_id=homestatus_id, user_id=self.request.user.id
                )

    perform_create = _save
    perform_update = _save


class _BaseRelatedObjectsViewSet(viewsets.ModelViewSet):
    renderer_classes = (ExamineRestFrameworkJSONRenderer,)
    # I don't necessarily want this in play on this particular viewset,
    # but html view is dangerous here
    serializer_class = NestedObjectsSerializer

    def get_queryset(self):
        return self.model.objects.all()


# Auto-generated viewsets for Historical models and other annotation/relationship data
simplehistory_viewsets = {}
relationship_viewsets = {}
relatedobjects_viewsets = {}
annotations_viewsets = {}
typedannotations_viewsets = {}
fieldannotations_viewsets = {}
for model in apps.get_models():
    # if model.__name__.startswith("Historical"):
    #     underlying_model_name = model.__name__.replace("Historical", "")
    #     HistoricalViewSet = type(str("%sViewSet" % model.__name__), (_BaseHistoricalViewSet,), {
    #         'model': model,
    #         'queryset': model.objects.all(),
    #         'underyling_model': apps.get_model(model._meta.app_label, underlying_model_name),
    #     })
    #     simplehistory_viewsets[underlying_model_name] = HistoricalViewSet

    if hasattr(model, "relationships"):
        RelationshipsViewSet = type(
            str("%sRelationshipsViewSet" % model.__name__),
            (_BaseRelationshipsViewSet,),
            {
                "model": model,
                "queryset": model.objects.all(),
            },
        )
        relationship_viewsets[model.__name__] = RelationshipsViewSet

    if not model.__name__.startswith("Historical"):
        RelatedObjectsViewSet = type(
            str("%sRelatedObjectsViewSet" % model.__name__),
            (_BaseRelatedObjectsViewSet,),
            {
                "model": model,
                "queryset": model.objects.all(),
            },
        )
        relatedobjects_viewsets[model.__name__] = RelatedObjectsViewSet

        GenericAnnotationViewSet = type(
            str("%sAnnotationsViewSet" % model.__name__),
            (AnnotationViewSet,),
            {
                "object_model": model,
            },
        )
        annotations_viewsets[model.__name__] = GenericAnnotationViewSet

        ContentTypeAnnotationViewSet = type(
            str("%sAnnotationsViewSet" % model.__name__),
            (BaseContentTypeAnnotationViewSet,),
            {
                "model": model,
                "queryset": model.objects.all(),
            },
        )
        typedannotations_viewsets[model.__name__] = ContentTypeAnnotationViewSet

        FieldAnnotationsViewSet = type(
            str("%sFieldAnnotationsViewSet" % model.__name__),
            (BaseFieldAnnotationsViewSet,),
            {
                "model": model,
                "queryset": model.objects.all(),
            },
        )
        fieldannotations_viewsets[model.__name__] = FieldAnnotationsViewSet
