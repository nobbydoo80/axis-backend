from django.urls import path, include, re_path

from axis.certification.api.urls import urlpatterns as certification_urls
from axis.checklist.api import QuestionViewSet, AnswerViewSet
from axis.home.api import HomeViewSet, HomeStatusExportFieldsFormAPIView
from axis.incentive_payment.api import IncentivePaymentControlCenterEndpoint
from axis.qa.api import QAStatusViewSet
from axis.relationship.api import RelationshipViewSet
from .router import api_router
from ..api import UserViewSet, CeleryJobsViewSet, DumpDataView

# Mount extensions
from . import base, company, floorplan, home, checklist
from .customers import aps, eto, neea, hirl

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]

# QA Status
qa_status_get_multiple_status = QAStatusViewSet.as_view({"get": "list"})

# User
user_lasest_stats = UserViewSet.as_view({"get": "latest_stats"})
error_test = UserViewSet.as_view({"get": "error_test"})

# Checklist
question_list = QuestionViewSet.as_view({"get": "list"})
question_detail = QuestionViewSet.as_view({"get": "retrieve"})
home_status_question = HomeViewSet.as_view({"get": "questions"})
get_question = QuestionViewSet.as_view({"get": "retrieve"})
answer_question = AnswerViewSet.as_view({"get": "retrieve", "post": "create", "delete": "destroy"})
delete_question = AnswerViewSet.as_view({"delete": "destroy"})
# Incentive Payment
ipp_datatable = IncentivePaymentControlCenterEndpoint.as_view({"get": "get_datatable"})
ipp_form = IncentivePaymentControlCenterEndpoint.as_view(
    {"get": "get_form", "post": "advance_state"}
)
# Relationships
relationship_discover = RelationshipViewSet.as_view({"get": "discover"})
relationship_add = RelationshipViewSet.as_view({"post": "add"})
relationship_reject = RelationshipViewSet.as_view({"post": "reject"})
relationship_delete = RelationshipViewSet.as_view({"post": "delete"})


# Checklist URLS - HomeStatusViewSet, QuestionViewSet, AnswerViewSet
checklist_urls = [
    path("", home_status_question),
    path("questions/", home_status_question),
    path(
        "<int:eep_program_id>/",
        include(
            [
                path("", home_status_question),
                path("questions/", home_status_question, {"readonly": True}),
                path("questions/<int:question_id>/", get_question, name="question"),
                path("questions/<int:question_id>/answer/", answer_question, name="answer"),
            ]
        ),
    ),
    path("questions/<int:question_id>/", get_question, name="question"),
    path("questions/<int:question_id>/answer/", answer_question, name="answer"),
]

relationship_urls = [
    path(
        "<str:app_label>/<str:model>/discover/",
        relationship_discover,
        name="relationship-company-discover",
    ),
    path(
        "<str:app_label>/<str:model>/add/<int:company_id>/<int:object_id>/",
        relationship_add,
        name="relationship-company-add",
    ),
    path(
        "<str:app_label>/<str:model>/delete/<int:company_id>/<int:object_id>/",
        relationship_delete,
        name="relationship-company-delete",
    ),
    path(
        "<str:app_label>/<str:model>/add/<int:object_id>/",
        relationship_add,
        name="relationship-add",
    ),
    path(
        "<str:app_label>/<str:model>/reject/<int:object_id>/",
        relationship_reject,
        name="relationship-reject",
    ),
    path(
        "<str:app_label>/<str:model>/delete/<int:object_id>/",
        relationship_delete,
        name="relationship-delete",
    ),
]


urlpatterns = [
    re_path(r"^dumpdata/(?P<label>.+\..+)/(?P<pk>\d+)/$", DumpDataView.as_view(), name="dumpdata"),
    # User
    path("latest_stats/", user_lasest_stats, name="api_dispatch_detail"),
    path("error_test/", error_test, name="error_test"),
    # QA Status - QAStatusViewSet
    re_path(
        r"^qa_status/set/(?P<pk_list>\w[\w/;-]*)/full_status/$",
        qa_status_get_multiple_status,
        name="qa_status-multiple-progress",
    ),
    # Checklist urls
    path("checklist/<int:pk>/", include(checklist_urls)),
    # Relationship urls
    path("relationship/", include(relationship_urls)),
    # IPP urls
    path("ipp/datatable/<str:datatable>/", ipp_datatable, name="ipp-datatable"),
    path("ipp/form/<str:form>/", ipp_form, name="ipp-form"),
    # Celery Stuff
    path("tasks/queues/", CeleryJobsViewSet.as_view({"get": "queues"}), name="celery_queues"),
    path("tasks/active/", CeleryJobsViewSet.as_view({"get": "queues"}), name="celery_active"),
    path("tasks/reserved/", CeleryJobsViewSet.as_view({"get": "queues"}), name="celery_reserved"),
    path("tasks/scheduled/", CeleryJobsViewSet.as_view({"get": "queues"}), name="celery_scheduled"),
    path("tasks/revoked/", CeleryJobsViewSet.as_view({"get": "queues"}), name="celery_revoked"),
    path("tasks/stats/", CeleryJobsViewSet.as_view({"get": "queues"}), name="celery_stats"),
    path(
        "task/status/<uuid:uuid>/", CeleryJobsViewSet.as_view({"get": "status"}), name="task_status"
    ),
    path("home/status/report/export_fields/", HomeStatusExportFieldsFormAPIView.as_view()),
    path("RESO/", include("axis.reso.api_urls")),
]


# Modularized to app's api urls
for urls in [certification_urls]:
    urlpatterns.extend(urls)


app_name = "apiv2"
urlpatterns += api_router.urls
