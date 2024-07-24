""" Messaging system urls """


import logging

from django.urls import path

from . import views

__author__ = "Autumn Valenta"
__date__ = "2015-03-04 2:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app_name = "messaging"

urlpatterns = [
    path("", views.MessagingListView.as_view(), name="list"),
    path(
        "unsubscribe/<uidb64>/<token>/<mnameb64>",
        views.UnsubscribeEmailView.as_view(),
        name="unsubscribe_email",
    ),
    path("test/", views.MessagingTestGenerationView.as_view(), name="test"),
    path("test/digest/<int:pk>/", views.MessagingTestDigestView.as_view(), name="digest"),
    path("test/email/<int:pk>/", views.MessagingTestEmailView.as_view(), name="email"),
    path("websockets/", views.WebsocketIDListView.as_view(), name="websockets"),
]
