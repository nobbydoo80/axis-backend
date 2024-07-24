__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


from django.contrib.auth import get_user_model
from django.db.models import Q
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import viewsets, serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from axis.company.serializers import CompanyEEPProgramSerializer
from axis.examine.api.restframework import ExamineViewSetAPIMixin
from .models import (
    BuilderOrganization,
    RaterOrganization,
    ProviderOrganization,
    Company,
)

User = get_user_model()


class BaseOrganizationViewSetMixin(ExamineViewSetAPIMixin):
    model = Company
    company_type = None

    def get_queryset(self):
        qs = self.model.objects.all()
        if self.company_type:
            qs = qs.filter(company_type=self.company_type)
        return qs

    def filter_queryset(self, queryset):
        return queryset.filter_by_user(self.request.user)

    @action(detail=True)
    def users(self, request, *args, **kwargs):
        queryset = self.get_object().users.all()
        data = {
            "users": [(user.pk, user.get_full_name()) for user in queryset],
        }
        return Response(data)

    @action(detail=True, methods=["post"])
    def eto_compliance_option(self, request, *args, **kwargs):
        """Update ETO City Of Hillsboro compliance option."""

        from axis.customer_eto.serializers import PermitAndOccupancySettingsSerializer

        obj = self.get_object()
        if obj is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        user = self.request.user

        settings, _ = obj.permitandoccupancysettings_set.get_or_create(
            owner=user.company, company=obj
        )
        serializer = PermitAndOccupancySettingsSerializer(instance=settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class BaseUnattachedOrganizationViewSetMixin(ExamineViewSetAPIMixin):
    company_type = None

    def filter_queryset(self, queryset):
        company = self.request.user.company
        counties = company.counties.all()
        countries = company.countries.exclude(abbr="US")
        attached_ids = Company.objects.filter_by_company(
            company, include_self=True, show_attached=True
        ).values_list("id", flat=True)
        return Company.objects.filter(
            Q(counties__in=counties) | Q(countries__in=countries),
            company_type=self.company_type,
            is_active=True,
        ).exclude(id__in=list(attached_ids))


class BuilderOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.BUILDER_COMPANY_TYPE


class UnattachedBuilderOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, BuilderOrganizationViewSet
):
    company_type = Company.BUILDER_COMPANY_TYPE


class RaterOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.RATER_COMPANY_TYPE


class UnattachedRaterOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, RaterOrganizationViewSet
):
    company_type = Company.RATER_COMPANY_TYPE


class ProviderOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.PROVIDER_COMPANY_TYPE


class UnattachedProviderOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, ProviderOrganizationViewSet
):
    company_type = Company.PROVIDER_COMPANY_TYPE


class EepOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.EEP_COMPANY_TYPE


class UnattachedEepOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, EepOrganizationViewSet
):
    company_type = Company.EEP_COMPANY_TYPE


class HvacOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.HVAC_COMPANY_TYPE


class UnattachedHvacOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, HvacOrganizationViewSet
):
    company_type = Company.HVAC_COMPANY_TYPE


class UtilityOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.UTILITY_COMPANY_TYPE


class UnattachedUtilityOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, UtilityOrganizationViewSet
):
    company_type = Company.UTILITY_COMPANY_TYPE


class QaOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.QA_COMPANY_TYPE


class UnattachedQaOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, QaOrganizationViewSet
):
    company_type = Company.QA_COMPANY_TYPE


class GeneralOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.GENERAL_COMPANY_TYPE


class UnattachedGeneralOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, GeneralOrganizationViewSet
):
    company_type = Company.GENERAL_COMPANY_TYPE


class ArchitectOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.ARCHITECT_COMPANY_TYPE


class UnattachedArchitectOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, ArchitectOrganizationViewSet
):
    company_type = Company.ARCHITECT_COMPANY_TYPE


class DeveloperOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.DEVELOPER_COMPANY_TYPE


class UnattachedDeveloperOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, DeveloperOrganizationViewSet
):
    company_type = Company.DEVELOPER_COMPANY_TYPE


class CommunityOwnerOrganizationViewSet(BaseOrganizationViewSetMixin, viewsets.ModelViewSet):
    company_type = Company.COMMUNITY_OWNER_COMPANY_TYPE


class UnattachedCommunityOwnerOrganizationViewSet(
    BaseUnattachedOrganizationViewSetMixin, CommunityOwnerOrganizationViewSet
):
    company_type = Company.COMMUNITY_OWNER_COMPANY_TYPE


class CompanyEEPProgramViewSet(viewsets.ModelViewSet):
    model = Company
    queryset = model.objects.all()
    serializer_class = CompanyEEPProgramSerializer

    def _handle_program_for_home_status_creation(self, program_id, method):
        """
        Determines if we need to add or remove a company from the opt-in-out-list
        based on the program.
        """
        from axis.eep_program.models import EEPProgram

        program = EEPProgram.objects.get(id=program_id)
        company = self.get_object()

        if program.opt_in:
            method = "add" if method == "approve" else "remove"
        else:
            method = "add" if method == "ignore" else "remove"

        getattr(program.opt_in_out_list, method)(company)

        return Response()

    @action(detail=True, methods=["post"])
    def ignore_program_for_home_status_creation(self, request, *args, **kwargs):
        return self._handle_program_for_home_status_creation(request.data["program_id"], "ignore")

    @action(detail=True, methods=["post"])
    def approve_program_for_home_status_creation(self, request, *args, **kwargs):
        return self._handle_program_for_home_status_creation(request.data["program_id"], "approve")


def findcompany_serializer_factory(OrgModel):
    class FindOrgSerializer(serializers.ModelSerializer):
        city = serializers.CharField(source="city.name")
        phone_number = PhoneNumberField(source="office_phone", required=False)
        email_address = serializers.CharField(source="default_email", required=False)
        website = serializers.CharField(source="home_page", required=False)

        class Meta:
            model = OrgModel
            fields = (
                "id",
                "name",
                "street_line1",
                "street_line2",
                "city",
                "state",
                "zipcode",
                "phone_number",
                "email_address",
                "website",
            )

    return FindOrgSerializer


class FindOrgFilterMixin(object):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def filter_queryset(self, queryset):
        params = self.request.query_params.dict()
        serializer = self.get_serializer()
        valid_fields = set(serializer.fields.keys())
        provided_fields = set(params.keys())
        intersection = list(f for f in provided_fields if f.split("__")[0] in valid_fields)

        # Naive little replacer for our custom serializer names -> ORM names
        replacements = {
            "city": "city__name",
            "phone_number": "office_phone",
            "email_adress": "default_email",
            "website": "home_page",
            "partner_since_date": "agreement_start_date",
            "hundred_percent_builder": "commitment",
        }
        query_data = {}
        for i, item in enumerate(intersection):
            bits = item.split("__")
            for j, lookup in enumerate(bits):
                if lookup in replacements:
                    lookup = replacements[lookup]
                bits[j] = lookup

            lookup = "__".join(bits)
            query_data[lookup] = params[item].strip()
        queryset = queryset.filter_by_user(self.request.user).filter(**query_data)
        return queryset


class FindBuilderViewSet(FindOrgFilterMixin, viewsets.ReadOnlyModelViewSet):
    model = BuilderOrganization
    queryset = model.objects.all()
    serializer_class = findcompany_serializer_factory(BuilderOrganization)


class FindProviderViewSet(FindOrgFilterMixin, viewsets.ReadOnlyModelViewSet):
    model = ProviderOrganization
    queryset = model.objects.all()
    serializer_class = findcompany_serializer_factory(ProviderOrganization)


class FindVerifierViewSet(FindOrgFilterMixin, viewsets.ReadOnlyModelViewSet):
    model = RaterOrganization
    queryset = model.objects.all()
    serializer_class = findcompany_serializer_factory(RaterOrganization)
