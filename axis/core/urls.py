"""views.py: Django core urls"""

from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetView,
    PasswordResetDoneView,
)
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from tensor_registration.views import TensorLoginView

from .api import AxisTokenObtainPairView
from .forms import AxisSetPasswordForm, AxisPasswordChangeForm, AxisPasswordResetForm
from .views import (
    SearchListView,
    AjaxLoginView,
    ProfileListView,
    LocalStorageResetView,
    HistoryDataTableView,
    ApproveTensorAccount,
    NewsListView,
    ContactView,
    ContactSuccessView,
    EnableBetaView,
    landing,
    superuser,
    UserExamineView,
)

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]


profile_urls = (
    [
        path("", ProfileListView.as_view(), name="list"),
        path("public/", ProfileListView.as_view(is_public=True), name="public_list"),
        path(
            "<int:pk>/",
            include(
                [
                    path("", UserExamineView.as_view(), name="detail"),
                ]
            ),
        ),
    ],
    "profile",
)

auth_urls = (
    [
        path("ajax-login/", AjaxLoginView.as_view(), name="ajax-login"),
        path("login/", TensorLoginView.as_view(), name="login"),
        path(
            "tensor/approve/<int:pk>/",
            ApproveTensorAccount.as_view(),
            name="approve_tensor_account",
        ),
        path(
            "logout/",
            LogoutView.as_view(template_name="registration/logout.html", next_page="/"),
            name="logout",
        ),
    ],
    "auth",
)

reset_password_urls = [
    path(
        "password_change/",
        PasswordChangeView.as_view(form_class=AxisPasswordChangeForm),
        name="password_change",
    ),
    path("password_change/done/", PasswordChangeDoneView.as_view(), name="password_change_done"),
    path(
        "password_reset/",
        PasswordResetView.as_view(form_class=AxisPasswordResetForm),
        name="password_reset",
    ),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(form_class=AxisSetPasswordForm),
        name="password_reset_confirm",
    ),
    path("reset/done/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

superuser_urls = [
    path("system-messenger/", superuser.SystemMessengerView.as_view(), name="system_messenger"),
    path("logs/", superuser.DumpRecentLogView.as_view()),
    path("query/", superuser.BaseQueryView.as_view()),
    path("toggle/beta/", EnableBetaView.as_view(), name="toggle_beta"),
    # History datatable views.  We put them on the url tree as if they were part of the axis
    # responsible for those models.
    path(
        "history/<str:app_label>/<str:model>/<str:field>/<str:constraint>",
        HistoryDataTableView.as_view(),
        name="history_list",
    ),
    path(
        "home/status/history/",
        superuser.ModelHistoryView.as_view(model="home.EEPProgramHomeStatus"),
    ),
    path("sampleset/history/", superuser.ModelHistoryView.as_view(model="sampling.SampleSet")),
    path("community/history/", superuser.ModelHistoryView.as_view(model="community.Community")),
    # Debug views
    path("headers.html", superuser.DumpRequestHeadersView.as_view()),
    path("exception/", superuser.ExceptionTestView.as_view(), name="exception_test"),
]

jwt_urls = (
    [
        path("token/", AxisTokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    ],
    "jwt",
)

urlpatterns = [
    path("core/search/", SearchListView.as_view(), name="basic_search"),
    path("news/", NewsListView.as_view(), name="news"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("contact-success/", ContactSuccessView.as_view(), name="contact_success"),
    path("reset-table-settings/", LocalStorageResetView.as_view()),
    path("profile/", include(profile_urls)),
    path("", include(reset_password_urls)),
    path("accounts/", include(auth_urls)),
    path("index/", landing.HomeDashboardRoutingView.as_view(), name="nocache_home"),
    path("", landing.HomeDashboardRoutingView.as_view(), name="home"),
    path("jwt/", include(jwt_urls)),
    path("", include(superuser_urls)),
]
