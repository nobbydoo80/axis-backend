""" Messaging api endpoints """


import datetime
import logging
import operator
from datetime import timedelta
from functools import reduce
from importlib import import_module

import dateutil.parser
import requests
from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.db.models import Q, Subquery, OuterRef
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Subquery, OuterRef
from .models import Message, MessagingPreference, DigestPreference, UserSession
from .serializers import MessageSerializer
from .utils import (
    send_email,
    send_read_receipts,
    requeue_read_receipts_for_destination,
    get_digest_report,
    get_simple_hostname,
    get_preferences_report,
    get_user_message_preference,
)

__author__ = "Autumn Valenta"
__date__ = "3/3/15 1:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


# TODO: Power from a pre-declared DatatableOptions
class DatatableViewSetMixin(object):
    """Adds an endpoint to be directly usable in a datatables.js implementation."""

    top_level = None  # placeholder allowing us to use in link/action decorator

    columns = [
        "level",
        "title",
        "content",
        "category",
        "date_created",
        "date_sent",
    ]

    def filter_queryset(self, queryset):
        queryset = super(DatatableViewSetMixin, self).filter_queryset(queryset)

        search = self.request.query_params.get("search[value]")
        if search:
            search = search.strip()
            queries = [
                Q(title__icontains=search),
                Q(content__icontains=search),
                Q(category__icontains=search),
            ]
            try:
                date_search = dateutil.parser.parse(search)
            except (ValueError, TypeError) as e:
                queries.extend(
                    [
                        Q(level__icontains=search),
                    ]
                )
            else:
                tz = self.request.user.timezone_preference
                date_search = date_search.date()
                queries.extend(
                    [
                        Q(
                            date_created__range=(
                                datetime.datetime.combine(date_search, datetime.time.min).replace(
                                    tzinfo=tz
                                ),
                                datetime.datetime.combine(date_search, datetime.time.max).replace(
                                    tzinfo=tz
                                ),
                            )
                        ),
                        Q(
                            date_sent__range=(
                                datetime.datetime.combine(date_search, datetime.time.min).replace(
                                    tzinfo=tz
                                ),
                                datetime.datetime.combine(date_search, datetime.time.max).replace(
                                    tzinfo=tz
                                ),
                            )
                        ),
                    ]
                )
            queryset = queryset.filter(reduce(operator.or_, queries))

        try:
            order_index = int(self.request.query_params["order[0][column]"])
            order_direction = self.request.query_params["order[0][dir]"]
            sort_column = self.columns[order_index]
        except:
            sort_column = "date_created"
            order_direction = "desc"
        queryset = queryset.order_by(
            "%s%s" % (("-" if order_direction == "desc" else ""), sort_column)
        )

        return queryset

    @action(detail=False)
    def datatable(self, request, *args, **kwargs):
        queryset = self.model.objects.filter(user=request.user).select_related("user")
        total_records = queryset.count()
        queryset = self.filter_queryset(queryset)
        total_records_filtered = queryset.count()

        # Late paging
        try:
            start_offset = int(self.request.query_params.get("start", 0))
            page_length = int(self.request.query_params.get("length", 25))
            end_offset = start_offset + page_length
            queryset = queryset[start_offset:end_offset]
        except:
            pass

        data = {
            "draw": self.request.query_params.get("draw"),
            "recordsTotal": total_records,
            "recordsFiltered": total_records_filtered,
            "data": [self.serializer_class(obj).data for obj in queryset],
        }
        return Response(data)


class MessageViewSet(DatatableViewSetMixin, viewsets.ModelViewSet):
    model = Message
    queryset = model.objects.all()
    serializer_class = MessageSerializer

    def filter_queryset(self, queryset):
        params = self.request.query_params.dict()
        if params.get("sent"):
            queryset = self.get_sent_messages()

        queryset = super(MessageViewSet, self).filter_queryset(queryset)

        valid_fields = set(f.name for f in self.model._meta.get_fields())
        provided_fields = set(params.keys())
        queryset = queryset.filter(user=self.request.user).filter(
            **{k: params[k] for k in provided_fields.intersection(valid_fields) if params[k]}
        )

        if params.get("date_created_start"):
            try:
                date_created_start = dateutil.parser.parse(params["date_created_start"])
                queryset = queryset.filter(date_created__gte=date_created_start)
            except:
                pass
        if params.get("date_created_end"):
            try:
                date_created_end = dateutil.parser.parse(params["date_created_end"])
                queryset = queryset.filter(date_created__lte=date_created_end)
            except:
                pass
        if params.get("date_alerted_start"):
            try:
                date_alerted_start = dateutil.parser.parse(params["date_alerted_start"])
                queryset = queryset.filter(date_alerted__gte=date_alerted_start)
            except:
                pass
        if params.get("date_alerted_end"):
            try:
                date_alerted_end = dateutil.parser.parse(params["date_alerted_end"])
                queryset = queryset.filter(date_alerted__lte=date_alerted_end)
            except:
                pass

        if params.get("delivery_type"):
            delivery_type = params["delivery_type"]
            if delivery_type == "alerts":
                queryset = queryset.exclude(date_alerted=None)
            elif delivery_type == "alerts_only":
                queryset = queryset.exclude(date_alerted=None).filter(date_sent=None)
            elif delivery_type == "email":
                queryset = queryset.exclude(date_sent=None)

        return queryset.exclude(date_alerted=None)

    def get_sent_messages(self):
        # queryset = self.model.objects.filter()
        queryset = Message.objects.filter(user=self.request.user)
        return queryset.exclude(date_alerted=None)

    @action(detail=False, methods=["post"])
    def pull(self, request, *args, **kwargs):
        mundane = ~Q(level="system")
        recent_system = Q(level="system", date_alerted__gte=now() - timedelta(days=7))
        queryset = (
            self.model.objects.filter(mundane | recent_system, alert_read=False, user=request.user)
            .select_related("user")
            .order_by("id")
        )

        # Get Message_name List
        message_name_queryset = MessagingPreference.objects.filter(
            receive_notification=True, user=request.user
        ).values_list("message_name", flat=True)

        # Filter list.
        message_name_list = list(message_name_queryset)
        queryset = queryset.filter(modern_message__in=message_name_list)

        # Use built-in pagination to enforce a limit on the number of returned objects.
        # We don't expect the client to use any kind of specific page number, we just want to get
        # the leading head of results from page 1.
        page = self.paginate_queryset(queryset)
        if page is not None:
            objects = page
        else:
            objects = queryset
        serializer = self.get_serializer(objects, many=True)

        # Bake response, THEN update date_alerted field
        response = self.paginator.get_paginated_response(serializer.data)
        queryset = queryset.filter(date_alerted__isnull=True).update(date_alerted=now())

        return response

    @action(detail=False, methods=["get", "post"])
    def mark_all_read(self, request, *args, **kwargs):
        # Update queryset using the client's latest known message as a cutoff for marking "all" as
        # read.  This defeats race conditions that the client doesn't know about.
        self.model.objects.filter(user=request.user, alert_read=False).update(alert_read=True)

        # Post internally to private API to generate read receipts for client websockets
        # This will not happen for messages marked as read that were undelivered because of a large
        # backlog, since the client doesn't have a record of them anyway.
        server_type = settings.SERVER_TYPE
        http_prefix = "https://"
        if server_type == settings.PRODUCTION_SERVER_TYPE:
            server_type = "axis"
        domain = server_type + ".pivotalenergy.net"

        if server_type == "dev":
            http_prefix = "http://"
            domain = "localhost:{port}".format(port=request.META.get("SERVER_PORT", "8000"))

        private_api_url = reverse(
            "apiv2:messaging_websocket-bulk-read",
            kwargs={
                "session_key": request.session.session_key,
            },
        )
        try:
            response = requests.post(
                http_prefix + domain + private_api_url,
                headers={
                    "Authorization": "Token " + Token.objects.get(user__username="websocket").key,
                },
            )
        except Exception as e:
            log.error(
                "Something extremely wrong just happened. %s" % e,
                exc_info=1,
                extra={"request": self.request},
            )
            return Response("unknown error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("", status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def read(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.alert_read = True
        obj.save()
        return Response("", status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def email(self, request, *args, **kwargs):
        obj = self.get_object()
        send_email(obj)
        return Response("", status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def digest_all(self, request, *args, **kwargs):
        report, start, end = get_digest_report(user_id=None)
        return Response(report)

    @action(detail=True)
    def digest(self, request, pk, *args, **kwargs):
        report, start, end = get_digest_report(user_id=pk)
        return Response(report)

    def preform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessagingPreferenceViewSet(viewsets.ModelViewSet):
    model = MessagingPreference
    queryset = model.objects.all()

    top_level = None  # placeholder allowing us to use in link/action decorator

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    @action(detail=False, methods=["get", "post"])
    def digest(self, request, *args, **kwargs):
        preference, created = DigestPreference.objects.get_or_create(user=request.user)
        if request.method == "GET":
            response = {
                "threshold": preference.threshold,
            }
        else:
            preference.threshold = request.data.get("threshold", preference.threshold)
            preference.save()
            response = ""
        return Response(response)

    # FIXME: I dunno why I didn't use a serializer to get this report GET/POST stuff done
    @action(detail=False, methods=["get", "post"])
    def report(self, request, *args, **kwargs):
        if request.method == "GET":
            response = get_preferences_report(request.user, trimmed=True, json_safe=True)
        else:
            self._set_preferences(request.data)
            response = ""
        return Response(response)

    def _set_preferences(self, data):
        from .forms import MessagingPreferenceForm

        # Iterate existing preferences in order to inspect ``data``, so that we can avoid trusting
        # the data to claim which preference pk is being altered.
        existing_preferences = {p.id: p for p in self.request.user.messagingpreference_set.all()}
        existing_report = get_preferences_report(self.request.user)
        for category, preferences in existing_report.items():
            if category not in data:
                continue
            for message_class, preference in preferences.items():
                new_preference = data[category].get(message_class.__name__)
                if not new_preference:
                    continue

                preference_obj = None
                if preference["id"]:
                    preference_obj = existing_preferences[preference["id"]]

                form = MessagingPreferenceForm(new_preference, instance=preference_obj)
                config = form.save(commit=False)
                config.user = self.request.user
                config.category = category or ""
                config.message_name = message_class.__name__
                config.save()


# PRIVATE API FOR NODEJS SERVER
class WebsocketControlViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    top_level = None  # placeholder to allow our custom router to use kwarg in link() decorator

    @action(detail=True)  # POST
    def read(self, request, session_key, pk, *args, **kwargs):
        if not request.user.username == "websocket":
            return Response("", status=status.HTTP_403_FORBIDDEN)

        # NOTE: pk gets reused here as a list if called from bulk_read()
        if not isinstance(pk, list):
            id_list = [pk]
        else:
            id_list = pk

        # Although we received an explicit session_key, we need to broaden the delivery of read
        # receipts to other sessions the user may be holding active across devices.

        # This could normally be a .get() instead of .filter(), but when a superuser impersonates
        # someone, the superuser's session key remains active and is in fact reused in the table
        # under the impersonated user's id.
        # We can't just filter away user__is_superuser=False, because the impersonated person might
        # also be a superuser...
        # The impersonator will always have begun their session BEFORE the impersonated entry, so
        # we will get the one with the highest autoincrementing pk and treat that as the definitive
        # record pointing the user_id we're believe owns the message pks in question.
        # The user_id can't be wrong with this strategy, because there will only ever be 1 or 2
        # entries in UserSession with the same user_id and session_key combination.
        usersession = UserSession.objects.filter(session=session_key).order_by("-id").first()
        if usersession is None:
            return Response("bad session", status=status.HTTP_400_BAD_REQUEST)
        session_keys = UserSession.objects.filter(user=usersession.user).values_list(
            "session", flat=True
        )

        for session_key in session_keys:
            session = SessionStore(session_key=session_key)
            if "websocket_ids" not in session:
                session["websocket_ids"] = {}
            self._purge_stale_sockets(session)
            for host in set(map(lambda d: d["host"], session["websocket_ids"].values())):
                if host == get_simple_hostname():
                    send_read_receipts(id_list, session_key=session_key)
                else:
                    requeue_read_receipts_for_destination(host, id_list, session_key=session_key)
            session.save()
        return Response("read %s: %r" % (id_list, session["websocket_ids"]))

    @action(detail=False, methods=["get", "post"])
    def bulk_read(self, request, session_key, *args, **kwargs):
        try:
            id_list = list(map(int, request.query_params.getlist("id")))
        except:
            return Response("no ids")
        return self.read(request, session_key, pk=id_list, *args, **kwargs)

    @action(detail=True)  # PUT
    def start(self, request, session_key, pk, *args, **kwargs):
        if not request.user.username == "websocket":
            return Response("", status=status.HTTP_403_FORBIDDEN)
        session = SessionStore(session_key=session_key)
        if "websocket_ids" not in session:
            session["websocket_ids"] = {}
        session["websocket_ids"][pk] = {
            "date": str(now()),
            "host": request.query_params.get("host"),
        }
        self._purge_stale_sockets(session)
        try:
            session.save()
        except UpdateError:
            msg = "Unable to update session %(pk)s - key %(key)s"
            log.warning(msg, {"pk": pk, "key": session_key})
            return Response(msg % {"pk": pk, "key": session_key}, status=500)
        # print('--- START', list(session['websocket_ids']))
        return Response("started %s: %r" % (pk, session["websocket_ids"]))

    @action(detail=True)  # DELETE
    def end(self, request, session_key, pk, *args, **kwargs):
        if not request.user.username == "websocket":
            return Response("", status=status.HTTP_403_FORBIDDEN)
        session = SessionStore(session_key=session_key)
        if "websocket_ids" not in session:
            session["websocket_ids"] = {}
        session["websocket_ids"].pop(pk, None)
        self._purge_stale_sockets(session)
        try:
            session.save()
        except UpdateError:
            msg = "Unable to update session %(pk)s - key %(key)s"
            log.warning(msg, {"pk": pk, "key": session_key})
            return Response(msg % {"pk": pk, "key": session_key}, status=500)
        # print('--- END', list(session['websocket_ids']))
        return Response("ended %s: %r" % (pk, session["websocket_ids"]))

    def _purge_stale_sockets(self, session):
        save_required = False
        for k, data in list(session["websocket_ids"].items()):
            # DEPRECATION WARNING: We expect all future sessions to be tracked by a date which was
            # saved as a JSON string, but old sessions suddenly revive and cause us problems.
            if isinstance(data["date"], datetime.datetime):
                # Legacy pickling serialization
                date = data["date"]
                data["date"] = str(date)
                save_required = True

            date = dateutil.parser.parse(data["date"])
            if now() - date > settings.MESSAGING_SOCKET_AGE_LIMIT:
                del session["websocket_ids"][k]
                save_required = True

        if save_required:
            try:
                session.save()
            except UpdateError:
                msg = "Unable to _purge_stale_sockets session %(session)s"
                log.warning(msg, {"session": session})
