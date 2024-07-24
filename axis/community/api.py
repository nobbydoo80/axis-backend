"""api.py: Django community"""


__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.db.models import Q
from rest_framework import viewsets

from axis.examine.api.restframework import ExamineViewSetAPIMixin
from axis.relationship.models import Relationship
from .models import Community
from .serializers import CommunitySerializer


class CommunityViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = Community
    queryset = model.objects.select_related("city", "county", "metro")
    serializer_class = CommunitySerializer

    def get_examine_machinery_classes(self):
        from .views.examine import CommunityExamineMachinery

        return {
            None: CommunityExamineMachinery,
        }

    def _save(self, serializer):
        instance = serializer.save()
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=instance, direct_relation=self.request.company
        )

    perform_create = _save
    perform_update = _save


class UnattachedCommunityViewSet(viewsets.ReadOnlyModelViewSet):
    model = Community
    queryset = model.objects.select_related("city", "county", "metro")
    serializer_class = CommunitySerializer

    def filter_queryset(self, queryset):
        company = self.request.company
        counties = company.counties.all()
        countries = company.countries.exclude(abbr="US")
        attached_ids = list(
            Community.objects.filter_by_company(company, show_attached=True).values_list(
                "id", flat=True
            )
        )
        return queryset.filter(Q(county__in=counties) | Q(city__country__in=countries)).exclude(
            id__in=attached_ids
        )
