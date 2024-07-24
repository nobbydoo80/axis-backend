"""find_verifier.py: """

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 20:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib.auth import get_user_model
from rest_framework import serializers

from axis.customer_hirl.models import VerifierAgreement, ProvidedService

from axis.company.models import Company
from axis.geographic.api_v3.serializers import CitySerializer
from axis.user_management.models import Accreditation

User = get_user_model()


class HIRLFindVerifierAccreditationListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.exclude(state=Accreditation.INACTIVE_STATE)
        return super(HIRLFindVerifierAccreditationListSerializer, self).to_representation(data)

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class HIRLFindVerifierAccreditationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accreditation
        list_serializer_class = HIRLFindVerifierAccreditationListSerializer
        fields = (
            "id",
            "name",
            "accreditation_id",
            "role",
            "state",
            "state_changed_at",
            "updated_at",
            "created_at",
        )


class HIRLFindVerifierCompanyInfoSerializer(serializers.ModelSerializer):
    city_info = CitySerializer(source="city", read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "slug",
            "street_line1",
            "street_line2",
            "state",
            "metro",
            "latitude",
            "longitude",
            "zipcode",
            "city",
            "city_info",
            "confirmed_address",
            "address_override",
            "geocode_response",
            "home_page",
        )


class HIRLFindVerifierProvidedServiceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvidedService
        fields = ("id", "name", "slug", "order", "last_update", "created_at")


class HIRLFindVerifierVerifierAgreementInfoSerializer(serializers.ModelSerializer):
    provided_services = HIRLFindVerifierProvidedServiceInfoSerializer(many=True)

    class Meta:
        model = VerifierAgreement
        fields = ("id", "state", "us_states", "provided_services")


class HIRLFindVerifierSerializer(serializers.ModelSerializer):
    company_info = HIRLFindVerifierCompanyInfoSerializer(source="company", read_only=True)
    customer_hirl_enrolled_verifier_agreements_info = (
        HIRLFindVerifierVerifierAgreementInfoSerializer(
            source="customer_hirl_enrolled_verifier_agreements", many=True, read_only=True
        )
    )
    accreditations_info = HIRLFindVerifierAccreditationInfoSerializer(
        source="accreditations", many=True, read_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "title",
            "department",
            "work_phone",
            "cell_phone",
            "fax_number",
            "alt_phone",
            "is_active",
            "company",
            "company_info",
            "customer_hirl_enrolled_verifier_agreements",
            "customer_hirl_enrolled_verifier_agreements_info",
            "accreditations",
            "accreditations_info",
        )
