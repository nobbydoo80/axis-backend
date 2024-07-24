"""Base API endpoints"""

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.utils.text import slugify

from analytics.api import AnalyticsViewSet

from axis.hes.api import HESSimulationStatusViewSet

from axis.annotation.api import AnnotationTypeViewSet, AnnotationViewSet
from axis.builder_agreement.api import BuilderAgreementViewSet
from axis.community.api import CommunityViewSet
from axis.company.api import FindBuilderViewSet, FindProviderViewSet, FindVerifierViewSet
from axis.ekotrope.api import HousePlanViewSet
from axis.eep_program.api import EEPProgramViewSet

from axis.filehandling.api import FileHandlingViewSet, customerdocument_viewset_factory
from axis.geocoder.api import GeocodeViewSet
from axis.geographic.api import (
    UnrestrictedCityViewSet,
    UnrestrictedCountyViewSet,
    ClimateZoneViewSet,
)
from axis.incentive_payment.api import (
    IncentivePaymentStatusViewSet,
    IncentiveDistributionViewSet,
    IPPItemViewSet,
)
from axis.qa.api import QAStatusViewSet, QANoteViewSet, QARequirementViewSet, ObservationTypeViewSet
from axis.relationship.api import RelationshipViewSet
from axis.scheduling.api import TaskTypeViewSet, TaskViewSet, TaskUserViewSet
from axis.subdivision.api import SubdivisionViewSet, SubdivisionEEPProgramViewSet
from axis.sampleset.api import SampleSetViewSet, SampleSetHomeStatusViewSet
from axis.messaging.api import MessageViewSet, MessagingPreferenceViewSet, WebsocketControlViewSet
from axis.equipment.api import EquipmentSponsorStatusViewSet
from axis.user_management.api import TrainingStatusViewSet, AccreditationViewSet, TrainingViewSet
from axis.core.api import (
    HIRLUserProfileViewSet,
    RecentItemViewSet,
    ContactCardPhoneViewSet,
    ContactCardEmailViewSet,
)
from ..api import (
    UserViewSet,
    ContentTypeViewSet,
    UserTrainingViewSet,
    UserAccreditationViewSet,
    UserCertificationMetricViewSet,
    UserInspectionGradeViewSet,
    ContactCardViewSet,
    ZendeskViewSet,
    simplehistory_viewsets,
    relationship_viewsets,
    relatedobjects_viewsets,
    annotations_viewsets,
    typedannotations_viewsets,
    fieldannotations_viewsets,
)
from .router import api_router

# Core

api_router.register(r"user", UserViewSet, "user")
api_router.register(r"user_training", UserTrainingViewSet, "user_training")
api_router.register(r"user_accreditation", UserAccreditationViewSet, "user_accreditation")
api_router.register(
    r"user_certification_metric", UserCertificationMetricViewSet, "user_certification_metric"
)
api_router.register(r"user_inspection_grade", UserInspectionGradeViewSet, "user_inspection_grade")
api_router.register(r"hirl_user_profile", HIRLUserProfileViewSet, "hirl_user_profile")

api_router.register(r"contact_cards", ContactCardViewSet, "contact_card")
api_router.register(r"contact_card_phones", ContactCardPhoneViewSet, "contact_card_phone")
api_router.register(r"contact_card_emails", ContactCardEmailViewSet, "contact_card_email")

api_router.register(r"recent_items", RecentItemViewSet, "recent_item")
api_router.register(
    r"messaging/websocket/(?P<session_key>[^/]+)", WebsocketControlViewSet, "messaging_websocket"
)
api_router.register(r"messages/preferences", MessagingPreferenceViewSet, "messages_preferences")
api_router.register(r"messages", MessageViewSet, "messages")
api_router.register(r"zendesk", ZendeskViewSet, "zendesk")

# Generic
api_router.register(r"asynchronous_document", FileHandlingViewSet, "asynchronous_document")
api_router.register(r"content_type", ContentTypeViewSet, "content_type")
api_router.register(r"relationship", RelationshipViewSet, "relationship")
api_router.register(r"annotation", AnnotationViewSet, "annotation")
api_router.register(r"annotation_type", AnnotationTypeViewSet, "annotation_type")

# Geographic
api_router.register(r"geocode", GeocodeViewSet, "geocode")
api_router.register(r"city", UnrestrictedCityViewSet, "city")
api_router.register(r"climate_zone", ClimateZoneViewSet, "climate_zone")
api_router.register(r"county", UnrestrictedCountyViewSet, "county")
api_router.register(r"metro", UnrestrictedCityViewSet, "metro")

# Simulation
api_router.register(r"ekotrope/houseplan", HousePlanViewSet, "houseplan")

# Equipment

api_router.register(
    "equipment_sponsor_status", EquipmentSponsorStatusViewSet, "equipment_sponsor_status"
)

api_router.register(r"hes", HESSimulationStatusViewSet, "hes")

# User management

api_router.register("training", TrainingViewSet, "training")

api_router.register("training_status", TrainingStatusViewSet, "training_status")

api_router.register("accreditation", AccreditationViewSet, "accreditation")

# Scheduling

api_router.register(r"scheduling/task", TaskViewSet, "task")
api_router.register(r"scheduling/home_task", TaskViewSet, "home_task")
api_router.register(r"scheduling/user_task", TaskUserViewSet, "user_task")

api_router.register(r"scheduling/task_type", TaskTypeViewSet, "task_type")

# Misc
api_router.register(
    r"builderagreement/documents",
    customerdocument_viewset_factory("builder_agreement.builderagreement"),
    "builderagreement_documents",
)
api_router.register(r"builder_agreement", BuilderAgreementViewSet, "builder_agreement")

# Frontends
api_router.register(r"find_builder", FindBuilderViewSet, "find_builder")
api_router.register(r"find_provider", FindProviderViewSet, "find_provider")
api_router.register(r"find_verifier", FindVerifierViewSet, "find_verifier")

# Uncategorized, should be broken up into organizational modules
api_router.register(r"community", CommunityViewSet, "community")
api_router.register(
    r"subdivision/documents",
    customerdocument_viewset_factory("subdivision.subdivision"),
    "subdivision_documents",
)
api_router.register(
    r"subdivision/programs", SubdivisionEEPProgramViewSet, "subdivision_eep_programs"
)
api_router.register(r"subdivision", SubdivisionViewSet, "subdivision")
api_router.register(r"eep_program", EEPProgramViewSet, "eep_program")
api_router.register(r"sampleset", SampleSetViewSet, "sampleset")
api_router.register(r"samplesethomestatus", SampleSetHomeStatusViewSet, "samplesethomestatus")
api_router.register(
    r"incentive_distribution", IncentiveDistributionViewSet, "incentive_distribution"
)
api_router.register(
    r"incentive_payment_status", IncentivePaymentStatusViewSet, "incentive_payment_status"
)
api_router.register(r"ippitem", IPPItemViewSet, "ippitem")
api_router.register(r"qa/requirement", QARequirementViewSet, "qa_requirement")
api_router.register(r"qa/note", QANoteViewSet, "qa_note")
api_router.register(
    r"qa_note/documents", customerdocument_viewset_factory("qa.qanote"), "qanote_documents"
)
api_router.register(r"qa/status", QAStatusViewSet, "qa_status")
api_router.register(r"qa/observation_type", ObservationTypeViewSet, "observation_type")
api_router.register(
    r"qa_status/documents", customerdocument_viewset_factory("qa.qastatus"), "qastatus_documents"
)

api_router.register(r"analytics", AnalyticsViewSet, "analytics")

# # Dynamically generated SimpleHistory viewsets
for model_name, HistoricalViewSet in simplehistory_viewsets.items():
    model_url = slugify("{}".format(model_name))
    api_router.register(
        r"%s/history" % (model_url,),
        HistoricalViewSet,
        "historical_%s" % (model_url,),
    )

# Dynamically generated Relationship viewsets
for model_name, RelationshipsViewSet in relationship_viewsets.items():
    model_url = slugify("{}".format(model_name))
    api_router.register(
        r"%s/relationships" % (model_url,),
        RelationshipsViewSet,
        "%s_relationships" % (model_url,),
    )

# Dynamically generated related object viewsets
for model_name, RelatedObjectsViewSet in relatedobjects_viewsets.items():
    model_url = slugify("{}".format(model_name))
    api_router.register(
        r"%s/related" % (model_url,),
        RelatedObjectsViewSet,
        "%s_relatedobjects" % (model_url,),
    )

# Dynamically generated annotations viewsets
for model_name, AnnotationsViewSet in annotations_viewsets.items():
    model_url = slugify("{}".format(model_name))
    api_router.register(
        r"%s/annotations" % (model_url,),
        AnnotationsViewSet,
        "%s_annotations" % (model_url,),
    )

# Dynamically generated typed annotations viewsets
for model_name, AnnotationsViewSet in typedannotations_viewsets.items():
    model_url = slugify("{}".format(model_name))
    api_router.register(
        r"%s/typedannotations" % (model_url,),
        AnnotationsViewSet,
        "%s_typedannotations" % (model_url,),
    )

# Dynamically generated field annotations viewsets
for model_name, FieldAnnotationsViewSet in fieldannotations_viewsets.items():
    model_url = slugify("{}".format(model_name))
    api_router.register(
        r"%s/field-annotations" % (model_url,),
        FieldAnnotationsViewSet,
        "%s_fieldannotations" % (model_url,),
    )
