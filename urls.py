__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

import sys

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views as fp_views
from django.contrib.flatpages.views import flatpage
from django.urls import include, path, re_path
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve
from django_zendesk.views import authorize, authorize_jwt
from drf_yasg import openapi
from drf_yasg.views import get_schema_view, UI_RENDERERS
from rest_framework import permissions
from rest_framework_extensions.routers import ExtendedDefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from tensor_registration.views import TensorAnonymousRegistrationView

from axis.annotation.api_v3.router import AnnotationRouter
from axis.community.api_v3.router import CommunityRouter
from axis.company.api_v3.router import CompanyRouter
from axis.core.api_fasttrack import api_router as fasttrack_api
from axis.core.api_v3.renderer import AxisSwaggerUIRenderer
from axis.core.api_v3.router import CoreRouter
from axis.core.api_v3.viewsets import (
    MenuAPIView,
    AxisTokenObtainPairView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from axis.core.forms import CustomTensorAnonymousRegistrationForm
from axis.core.views import ApiAutoResponseView
from axis.customer_aps.api_v3.router import CustomerAPSRouter
from axis.customer_eto.api_v3.router import CustomerETORouter
from axis.customer_hirl.api_v3.router import CustomerHIRLRouter
from axis.eep_program.api_v3.router import EEPProgramRouter
from axis.filehandling.api_v3.router import FileHandlingRouter
from axis.floorplan.api_v3.router import FloorplanRouter
from axis.geocoder.api_v3.router import GeocoderRouter
from axis.geographic.api_v3.router import GeographicRouter
from axis.home.api_v3.router import HomeRouter
from axis.invoicing.api_v3.router import InvoiceRouter
from axis.messaging.api_v3.router import MessagingRouter
from axis.qa.api_v3.router import QARouter
from axis.relationship.api_v3.router import RelationshipRouter
from axis.rpc.api_v3.router import RPCRouter
from axis.scheduling.api_v3.router import SchedulingRouter
from axis.subdivision.api_v3.router import SubdivisionRouter
from axis.user_management.api_v3.router import UserManagementRouter
from axis.equipment.api_v3.router import EquipmentRouter


# API v3
# put this to top to be catchable by DRF Browsable API

router = ExtendedDefaultRouter()

CoreRouter.register(router)
SubdivisionRouter.register(router)
CompanyRouter.register(router)
CommunityRouter.register(router)
EEPProgramRouter.register(router)
CustomerETORouter.register(router)
CustomerHIRLRouter.register(router)
GeographicRouter.register(router)
HomeRouter.register(router)
FloorplanRouter.register(router)
RelationshipRouter.register(router)
MessagingRouter.register(router)
GeocoderRouter.register(router)
FileHandlingRouter.register(router)
CustomerAPSRouter.register(router)
QARouter.register(router)
InvoiceRouter.register(router)
SchedulingRouter.register(router)
UserManagementRouter.register(router)
RPCRouter.register(router)
EquipmentRouter.register(router)
AnnotationRouter.register(router)

api_v3_urlpatterns = [
    path(
        "api/v3/",
        include(
            (
                router.urls
                + [
                    path("token/", AxisTokenObtainPairView.as_view(), name="token_obtain_pair"),
                    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
                    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
                    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
                    path(
                        "password/reset/confirm/",
                        PasswordResetConfirmView.as_view(),
                        name="password_reset_confirm",
                    ),
                    path("menu/", MenuAPIView.as_view(), name="menu"),
                ],
                "api_v3",
            )
        ),
    ),
]

# Update drf-yasg UI_RENDERERS list
UI_RENDERERS["axis-swagger"] = (AxisSwaggerUIRenderer,)

schema_view = get_schema_view(
    openapi.Info(title="AXIS API", default_version="v3"),
    patterns=api_v3_urlpatterns,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("docs/api/v3/", schema_view.with_ui("axis-swagger"), name="api_v3_swagger"),
    path("docs/redoc/api/v3/", schema_view.with_ui("redoc"), name="api_v3_redoc"),
]

urlpatterns += api_v3_urlpatterns

urlpatterns += [
    path("", include("axis.frontend.urls")),
    path("select2/fields/auto.json", ApiAutoResponseView.as_view(), name="django_select2-json"),
    path("", include("django_states.urls")),
    path("", include("axis.core.urls")),
    # override tensor anonymous registration form with our custom form
    path(
        "auth/register/ex",
        TensorAnonymousRegistrationView.as_view(form_class=CustomTensorAnonymousRegistrationForm),
        name="register_anonymous",
    ),
    path("auth/", include("tensor_registration.urls")),
    path("impersonate/", include("axis.impersonate.urls")),
    path("messaging/", include("axis.messaging.urls")),
    path("geographic/", include("axis.geographic.urls")),
    path("search/", include("axis.search.urls")),
    path("aps/", include("axis.customer_aps.urls")),
    path("builder_agreement/", include("axis.builder_agreement.urls")),
    path("certification/", include("axis.certification.urls")),
    path("checklist/", include("axis.checklist.urls")),
    path("community/", include("axis.community.urls")),
    path("aps/", include("axis.customer_aps.urls")),
    path("ea/", include("axis.customer_earth_advantage.urls")),
    path("ai/", include("axis.customer_appraisal_institute.urls")),
    path("eto/", include("axis.customer_eto.urls")),
    path("equipment/", include("axis.equipment.urls")),
    path("user_management/", include("axis.user_management.urls")),
    path("neea/", include("axis.customer_neea.urls")),
    path("hi/", include("axis.customer_hirl.urls")),
    path("wsu/", include("axis.customer_wsu.urls")),
    path("company/", include("axis.company.urls")),
    path("eep_program/", include("axis.eep_program.urls")),
    # epa_registry pending deprecation
    # path("epa_registry/", include("axis.epa_registry.urls")),
    path("file-operation/", include("axis.filehandling.urls")),
    path("floorplan/", include("axis.floorplan.urls")),
    path("home/", include("axis.home.urls")),
    path("ipp/", include("axis.incentive_payment.urls")),
    path("qa/", include("axis.qa.urls")),
    path("relationship/", include("axis.relationship.urls")),
    path("remrate/", include("axis.remrate.urls")),
    path("remrate_data/", include("axis.remrate_data.urls")),
    path("reso/", include("axis.reso.urls")),
    path("report/", include("axis.report.urls")),
    path("sampling/", include("axis.sampleset.urls")),
    path("scheduling/", include("axis.scheduling.urls")),
    path("subdivision/", include("axis.subdivision.urls")),
    path("app_metrics/", include("app_metrics.urls")),
    path("zendesk/", authorize),
    path("services/zendesk_auth/", authorize_jwt),
    path("analytics/", include("analytics.urls")),
    path("admin/", admin.site.urls),
    path("", include("axis.examine.urls")),
    path("api/input-collection/", include("django_input_collection.api.restframework.urls")),
    path("api/projecttracking/", include(fasttrack_api.urls)),
    path("api/v2/", include("axis.core.api_v2.urls")),
    path("api/v2/auth/", include(("rest_framework.urls", "apiv2_auth"))),
    path("openid/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("status.html", TemplateView.as_view(template_name="status.html"), name="status"),
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.ico", permanent=True)),
]

# Flatpages
urlpatterns += [
    path("info", flatpage, {"url": "/info/"}, name="info"),
    path("about", flatpage, {"url": "/about/"}, name="about"),
    path("products", flatpage, {"url": "/products/"}, name="products"),
    path("products/builder", flatpage, {"url": "/products/builder/"}, name="builder_products"),
    path(
        "products/utility_program_sponsors",
        flatpage,
        {"url": "/products/utility_program_sponsors/"},
        name="utility_products",
    ),
    path(
        "products/raters_providers",
        flatpage,
        {"url": "/products/raters_providers/"},
        name="rater_products",
    ),
    path("pricing", flatpage, {"url": "/pricing/"}, name="pricing"),
    re_path(r"(?P<url>public\-|site\-.*/)$", fp_views.flatpage),
]

if settings.DEBUG:
    # Media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Technical outputs
    urlpatterns += [
        path("403/", TemplateView.as_view(template_name="403.html")),
        path("404/", TemplateView.as_view(template_name="404.html")),
        path("500/", TemplateView.as_view(template_name="500.html")),
        path("update.html", TemplateView.as_view(template_name="update.html")),
    ]

# Testserver Statics
# This is automatically done by Django when settings.DEBUG is True, however with
# `settings.testserver`, DEBUG will be False.  This also means we can't directly use the static()
# url helper, since it returns an empty list if DEBUG isn't enabled.
if "testserver" in sys.argv:
    urlpatterns += [
        re_path(
            r"{STATIC_URL}(?P<path>.*)$".format(STATIC_URL=settings.STATIC_URL.lstrip("/")),
            serve,
            {"document_root": settings.STATIC_ROOT, "show_indexes": True},
        ),
    ]
