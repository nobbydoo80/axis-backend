"""api.py: sudivision data"""


import logging

from django.db.models import Q
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from axis.examine.api.restframework import ExamineViewSetAPIMixin
from .models import Subdivision, EEPProgramSubdivisionStatus
from .serializers import SubdivisionSerializer, SubdivisionEEPProgramSerializer


__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class SubdivisionViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Subdivision
    queryset = model.objects.all()
    serializer_class = SubdivisionSerializer

    def filter_queryset(self, queryset):
        return Subdivision.objects.filter_by_user(self.request.user, show_attached=True)

    def get_examine_machinery_classes(self):
        from .views.examine import SubdivisionExamineMachinery

        return {
            None: SubdivisionExamineMachinery,
        }

    def _save(self, serializer):
        """Generate relationships for the builder org."""

        obj = serializer.save()

        # This doesn't happen automatically because we're letting the subdivision worry about the
        # association, since it's an FK on the model.
        obj.set_builder(obj.builder_org, user=self.request.user)

    perform_create = _save
    perform_update = _save

    @action(detail=False, methods=["post"])
    def validate(self, request, *args, **kwargs):
        machinery = self.get_machinery(None, create_new=True)
        form = machinery.form_class(self.request.user, data=request.data)
        if form.is_valid():
            return Response()
        else:
            return Response(form.errors, status=400)

    @action(detail=True, methods=["get"])
    def eto_compliance_document(self, request, *args, **kwargs):
        """Download current ETO City Of Hillsboro compliance document."""

        try:
            signing_pass = int(request.query_params.get("round"))
        except Exception as error:  # pylint: disable=broad-except
            signing_pass = None
        else:
            error = None
        if signing_pass is None or signing_pass not in (1, 2):
            return Response(
                {"message": "Unknown signing round", "exception": error},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = self.request.user

        instance = self.get_object()
        queryset = instance.permitandoccupancysettings_set.filter(company=request.company)

        if signing_pass == 1:
            queryset = queryset.filter(signed_building_permit=None)
            for settings_obj in queryset:
                try:
                    settings_obj.post_building_permit(user)
                except Exception as error:  # pylint: disable=broad-except
                    log.info(
                        "Document not posted (may not be a real error): %(error)s",
                        error,
                    )

        elif signing_pass == 2:
            queryset = queryset.filter(signed_certificate_of_occupancy=None)
            for settings_obj in queryset:
                try:
                    settings_obj.post_certificate_of_occupancy(user)
                except Exception as error:  # pylint: disable=broad-except
                    log.info(
                        "Document not posted (may not be a real error): %(error)s",
                        error,
                    )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def eto_compliance_option(self, request, *args, **kwargs):
        """Update ETO City Of Hillsboro compliance option."""

        from axis.customer_eto.serializers import PermitAndOccupancySettingsSerializer

        obj = self.get_object()
        if obj is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        user = self.request.user

        settings, _ = obj.permitandoccupancysettings_set.get_or_create(
            owner=user.company, subdivision=obj
        )
        serializer = PermitAndOccupancySettingsSerializer(instance=settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UnattachedSubdivisionViewSet(viewsets.ReadOnlyModelViewSet):
    model = Subdivision
    queryset = model.objects.all()
    serializer_class = SubdivisionSerializer

    def filter_queryset(self, queryset):
        company = self.request.company
        counties = company.counties.all()
        countries = company.countries.exclude(abbr="US")
        attached_ids = list(
            Subdivision.objects.filter_by_user(self.request.user, show_attached=True).values_list(
                "id", flat=True
            )
        )
        return queryset.filter(Q(county__in=counties) | Q(city__country__in=countries)).exclude(
            id__in=attached_ids
        )


class SubdivisionEEPProgramViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = EEPProgramSubdivisionStatus  # Subdivision.eep_programs.through
    queryset = model.objects.all()
    serializer_class = SubdivisionEEPProgramSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        # Avoid circular import
        from .views.examine import ProgramsExamineMachinery

        return ProgramsExamineMachinery
