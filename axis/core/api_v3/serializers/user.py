"""user.py: """

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 20:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from axis.customer_hirl.serializers import (
    HIRLUserProfileSerializer,
)

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    """Contains only basic information about user."""

    company_info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "company",
            "company_info",
            "is_company_admin",
            "is_superuser",
            "is_active",
            "is_approved",
        )
        ref_name = "NewUserInfoSerializer"

    def get_company_info(self, user: User):
        from axis.company.api_v3.serializers import CompanyInfoSerializer

        return CompanyInfoSerializer(instance=user.company).data


class UserSerializer(serializers.ModelSerializer):
    """
    Contains full information about user
    """

    first_name = serializers.CharField(required=True, allow_blank=False, max_length=32)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=32)
    email = serializers.EmailField(required=True, allow_blank=False)
    work_phone = serializers.CharField(required=True, allow_blank=False)
    company_info = serializers.SerializerMethodField()
    active_customer_hirl_verifier_agreements_count = serializers.IntegerField(
        read_only=True, help_text="How many active Verifier Agreements user have"
    )
    customer_hirl_project_accreditations_count = serializers.IntegerField(
        read_only=True,
        help_text="How many active Agreements user have for 2020 and 2015 NGBS Programs",
    )
    timezone_preference = serializers.CharField()
    hirl_user_profile = HIRLUserProfileSerializer(source="hirluserprofile")

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "last_login",
            "email",
            "title",
            "department",
            "work_phone",
            "cell_phone",
            "fax_number",
            "alt_phone",
            "is_active",
            "is_public",
            "is_approved",
            "is_company_admin",
            "is_superuser",
            "is_staff",
            "show_beta",
            "company",
            "company_info",
            "timezone_preference",
            "rater_roles",
            "rater_id",
            "signature_image",
            "resnet_username",
            "resnet_password",
            "hirl_user_profile",
            # computed
            "active_customer_hirl_verifier_agreements_count",
            "customer_hirl_project_accreditations_count",
        )
        read_only_fields = [
            "username",
            "is_active",
            "is_approved",
            "is_superuser",
            "is_staff",
            "is_approved",
        ]
        ref_name = "AxisUserSerializer"

    def update(self, instance, validated_data):
        hirluserprofile_data = validated_data.pop("hirluserprofile", None)

        instance = super(UserSerializer, self).update(instance, validated_data)

        if hirluserprofile_data:
            for field, value in hirluserprofile_data.items():
                setattr(instance.hirluserprofile, field, value)
            instance.hirluserprofile.save()
        return instance

    def get_company_info(self, user: User):
        from axis.company.api_v3.serializers import CompanyInfoSerializer

        return CompanyInfoSerializer(instance=user.company).data


class BasicUserSerializer(serializers.ModelSerializer):
    """
    Hide user secrets like rater_username, rater_password, etc.
    """

    first_name = serializers.CharField(required=True, allow_blank=False, max_length=32)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=32)
    email = serializers.EmailField(required=True, allow_blank=False)
    work_phone = serializers.CharField(required=True, allow_blank=False)
    company_info = serializers.SerializerMethodField()
    active_customer_hirl_verifier_agreements_count = serializers.IntegerField(
        read_only=True, help_text="How many active Verifier Agreements user have"
    )
    customer_hirl_project_accreditations_count = serializers.IntegerField(
        read_only=True,
        help_text="How many active Agreements user have for 2020 and 2015 NGBS Programs",
    )
    timezone_preference = serializers.CharField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "last_login",
            "email",
            "title",
            "department",
            "work_phone",
            "cell_phone",
            "fax_number",
            "alt_phone",
            "is_active",
            "is_public",
            "is_company_admin",
            "is_approved",
            "company",
            "company_info",
            "timezone_preference",
            # computed
            "active_customer_hirl_verifier_agreements_count",
            "customer_hirl_project_accreditations_count",
        )
        read_only_fields = ["username", "is_active", "is_approved"]

    def get_company_info(self, user: User):
        from axis.company.api_v3.serializers import CompanyInfoSerializer

        return CompanyInfoSerializer(instance=user.company).data


class ImpersonationUserSerializer(serializers.Serializer):
    impersonated = UserSerializer()
    user = UserSerializer()
    csrftoken = serializers.CharField()
    session_key = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, max_length=30)
    password = serializers.CharField(required=True, max_length=30)
    confirmed_password = serializers.CharField(required=True, max_length=30)

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("Wrong password")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data.get("confirmed_password") != data.get("password"):
            raise serializers.ValidationError(
                {"confirmed_password": "Password must be confirmed correctly."}
            )

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    @property
    def data(self):
        return {}
