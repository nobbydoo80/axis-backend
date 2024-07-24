__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers

from axis.company.models import COMPANY_MODELS_MAP
from axis.company.models import Company
from axis.company.serializers import CompanyInfoSerializer
from axis.eep_program.models import EEPProgram
from axis.geocoder.models import Geocode
from axis.geographic.models import City
from axis.hes.serializers import HESCredentialsSerializer
from axis.home.models import EEPProgramHomeStatus
from axis.relationship.utils import modify_relationships
from axis.user_management.models import Training, TrainingStatus, Accreditation, InspectionGrade
from .forms import UserTrainingForm
from .models import ContactCard, ContactCardPhone, ContactCardEmail
from .simple_history_utils import get_revision_delta
from .utils import collect_nested_object_list, get_frontend_url

get_model = apps.get_model
User = get_user_model()
user_management_app = apps.get_app_config("user_management")


class HistorySerializer(serializers.ModelSerializer):
    history_object = serializers.ReadOnlyField()
    delta = serializers.SerializerMethodField()

    # Meta will be filled in when subclassed dynamically in core/api.py

    def get_delta(self, obj):
        if not hasattr(self, "_iter"):
            historical_model = self.Meta.model
            self._model = get_model(
                historical_model._meta.app_label,
                historical_model.__name__.replace("Historical", ""),
            )
            self._objects = list(self._model.history.filter(history_id=obj.id).values())
            self._iter = 0
        delta = get_revision_delta(self._model, self._objects, self._iter)
        self._iter += 1
        return delta


class RelationshipsSerializer(serializers.ModelSerializer):
    """
    Serializer that targets a model using ``axis.company.models.RelationshipUtilsMixin``, where
    a serialization is available for the company relationships, and supports saving changes to those
    relationships using methods on that model.
    """

    # Meta will be filled in when subclassed dynamically in core/api.py

    company_types = [
        "builder",
        "rater",
        "provider",
        "eep",
        "hvac",
        "qa",
        "general",
        "gas_utility",
        "electric_utility",
        "architect",
        "developer",
        "communityowner",
    ]

    def __init__(self, *args, **kwargs):
        self.company_types = kwargs.pop("company_types", None) or self.company_types
        super(RelationshipsSerializer, self).__init__(*args, **kwargs)

    def get_fields(self):
        """Provide the company types requested by the viewset (or the default set of them all)."""

        # Start a fields dictionary from scratch so that the lack of a Meta.fields specification
        # doesn't pull in all naturally occuring fields on the underlying model when calling super()
        fields = {
            # These must be declared inside the dynamic fields getter because grafting them from
            # self._declared_fields causes them to redo their field.bind(), which raises errors
            # that aren't easy to avoid.
            "id": serializers.IntegerField(read_only=True),
            "names": RelatedCompanyNameField(),
            "urls": RelatedCompanyUrlField(),
        }
        singular_types = ["builder", "gas", "electric"]
        for company_type in self.company_types:
            many = True
            if company_type.split("_", 1)[0] in singular_types:
                many = False
            fields[company_type] = RelatedCompanyField(
                many=many, company_type=company_type, required=False, allow_null=True
            )
        return fields

    def create(self, validated_data):
        instance = super(RelationshipsSerializer, self).create(validated_data)
        instance._relationship_data = validated_data.copy()
        return instance

    def update(self, instance, validated_data):
        instance = super(RelationshipsSerializer, self).update(instance, validated_data)
        instance._relationship_data = validated_data.copy()
        return instance

    def save(self, **kwargs):
        """Handles the stored references to relationship targets."""
        instance = super(RelationshipsSerializer, self).save(**kwargs)
        request = self.context["request"]
        creating = self.context["creating"] == "true"
        merged_data = instance.get_orgs(use_lists=True)
        for k, v in instance._relationship_data.items():
            if creating:
                if isinstance(v, QuerySet):
                    # Fold existing and new together
                    merged_data[k] = list(set(merged_data.setdefault(k, []) + list(v)))
                elif v:
                    # Overwrite with new
                    merged_data[k] = v

            else:
                # Submitted data trumps existing data
                merged_data[k] = v

        modify_relationships(instance, merged_data, request.user, request=request)


class RelatedCompanyNameField(serializers.ReadOnlyField):
    """Converts the object's relationships queryset into a dict of company_id:company__name"""

    def get_attribute(self, obj):
        return dict(obj.relationships.values_list("company_id", "company__name"))


class RelatedCompanyUrlField(serializers.ReadOnlyField):
    """Converts the object's relationships queryset into a dict of company_id:company_url"""

    def get_attribute(self, obj):
        return {
            id: get_frontend_url("company", company_type, "detail", id)
            for id, company_type in obj.relationships.values_list(
                "company_id", "company__company_type"
            )
        }


class RelatedCompanyField(serializers.Field):
    many = False

    def __init__(self, *args, **kwargs):
        self.company_type = kwargs.pop("company_type")
        self.many = kwargs.pop("many", False)
        model_meta = COMPANY_MODELS_MAP[self.company_type]._meta
        if self.many:
            kwargs["label"] = model_meta.verbose_name_plural
        else:
            kwargs["label"] = model_meta.verbose_name

        self.company_generic_type = self.company_type
        if self.company_type.split("_", 1)[0] in ("gas", "electric"):
            self.company_generic_type = "utility"

        super(RelatedCompanyField, self).__init__(*args, **kwargs)

    def get_attribute(self, obj):
        return obj.relationships.filter_by_company_type(self.company_generic_type)

    def to_representation(self, value):
        if value:
            filter_kwargs = {}
            if self.company_generic_type == "utility":
                # Make sure we pull back out only the relevant ones
                naming_shift = {
                    "electric_utility": "utilitysettings__is_electric_utility",
                    "gas_utility": "utilitysettings__is_gas_utility",
                }
                filter_kwargs[naming_shift[self.company_type]] = True
            ids = list(value.get_orgs(self.company_generic_type, ids_only=True, **filter_kwargs))
        else:
            ids = []
        if not self.many:
            if len(ids):
                return ids[0]
            return None
        return ids

    def to_internal_value(self, value):
        if value:
            if self.many:
                return Company.objects.filter(id__in=value)
            return Company.objects.get(id=value)
        if self.many:
            return []
        return None


class UserSerializerMixin(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=32)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=32)
    email = serializers.EmailField(required=True, allow_blank=False)
    work_phone = serializers.CharField(required=True, allow_blank=False)

    username = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    company_name = serializers.ReadOnlyField(source="company.name")
    company_type = serializers.ReadOnlyField(source="company.company_type")
    company_street_line1 = serializers.ReadOnlyField(source="company.street_line1")
    company_street_line2 = serializers.ReadOnlyField(source="company.street_line2")
    company_city_name = serializers.ReadOnlyField(source="company.city.as_string")
    company_zipcode = serializers.ReadOnlyField(source="company.zipcode")

    company_shipping_geocode = serializers.ReadOnlyField(source="company.shipping_geocode")
    company_shipping_geocode_street_line1 = serializers.ReadOnlyField(
        source="company.shipping_geocode.raw_street_line1"
    )
    company_shipping_geocode_street_line2 = serializers.ReadOnlyField(
        source="company.shipping_geocode.raw_street_line2"
    )
    company_shipping_geocode_city_name = serializers.ReadOnlyField(
        source="company.shipping_geocode.raw_city.name"
    )
    company_shipping_geocode_zipcode = serializers.ReadOnlyField(
        source="company.shipping_geocode.raw_zipcode"
    )

    mailing_geocode_exists = serializers.ReadOnlyField(source="mailing_geocode")
    mailing_geocode_street_line1 = serializers.CharField(
        source="mailing_geocode.raw_street_line1", max_length=100, required=False, allow_blank=True
    )
    mailing_geocode_street_line2 = serializers.CharField(
        source="mailing_geocode.raw_street_line2", max_length=100, required=False, allow_blank=True
    )
    mailing_geocode_zipcode = serializers.CharField(
        source="mailing_geocode.raw_zipcode", max_length=15, required=False, allow_blank=True
    )
    mailing_geocode_city = serializers.PrimaryKeyRelatedField(
        source="mailing_geocode.raw_city", queryset=City.objects.all(), required=False
    )
    mailing_geocode_city_display = serializers.ReadOnlyField(source="mailing_geocode.raw_city.name")

    shipping_geocode_street_line1 = serializers.CharField(
        source="shipping_geocode.raw_street_line1", max_length=100, required=False, allow_blank=True
    )
    shipping_geocode_street_line2 = serializers.CharField(
        source="shipping_geocode.raw_street_line2", max_length=100, required=False, allow_blank=True
    )
    shipping_geocode_zipcode = serializers.CharField(
        source="shipping_geocode.raw_zipcode", max_length=15, required=False, allow_blank=True
    )
    shipping_geocode_city = serializers.PrimaryKeyRelatedField(
        source="shipping_geocode.raw_city",
        required=False,
        allow_null=True,
        queryset=City.objects.all(),
    )
    shipping_geocode_city_display = serializers.ReadOnlyField(
        source="shipping_geocode.raw_city.name"
    )
    shipping_geocode_exists = serializers.ReadOnlyField(source="shipping_geocode")

    def validate(self, data):
        if data.get("mailing_geocode"):
            mailing_geocode = {
                "raw_street_line1": data["mailing_geocode"].get("raw_street_line1", ""),
                "raw_street_line2": data["mailing_geocode"].get("raw_street_line2", ""),
                "raw_zipcode": data["mailing_geocode"].get("raw_zipcode", ""),
                "raw_city": data["mailing_geocode"].get("raw_city", None),
            }
            if all(
                [
                    mailing_geocode["raw_street_line1"],
                    mailing_geocode["raw_zipcode"],
                    mailing_geocode["raw_city"],
                ]
            ):
                mailing_geocode[
                    "raw_address"
                ] = "{raw_street_line1} {raw_street_line2} " "{raw_zipcode} {raw_city}".format(
                    **mailing_geocode
                )
                data["mailing_geocode"] = mailing_geocode
            else:
                if (
                    mailing_geocode["raw_street_line1"]
                    or mailing_geocode["raw_city"]
                    or mailing_geocode["raw_zipcode"]
                ):
                    raise serializers.ValidationError("Mailing address is required")
                data["mailing_geocode"] = None

        # check if we have all shipping_geocode then address will be different than mailing
        # in other case remove shipping_geocode to make it None in db
        if data.get("shipping_geocode"):
            shipping_geocode = {
                "raw_street_line1": data["shipping_geocode"].get("raw_street_line1", ""),
                "raw_street_line2": data["shipping_geocode"].get("raw_street_line2", ""),
                "raw_zipcode": data["shipping_geocode"].get("raw_zipcode", ""),
                "raw_city": data["shipping_geocode"].get("raw_city", None),
            }
            if all(
                [
                    shipping_geocode["raw_street_line1"],
                    shipping_geocode["raw_zipcode"],
                    shipping_geocode["raw_city"],
                ]
            ):
                shipping_geocode[
                    "raw_address"
                ] = "{raw_street_line1} {raw_street_line2} " "{raw_zipcode} {raw_city}".format(
                    **shipping_geocode
                )
                data["shipping_geocode"] = shipping_geocode
            else:
                if (
                    shipping_geocode["raw_street_line1"]
                    or shipping_geocode["raw_city"]
                    or shipping_geocode["raw_zipcode"]
                ):
                    raise serializers.ValidationError("Different shipping address is required")
                data["shipping_geocode"] = None

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        mailing_geocode_data = validated_data.get("mailing_geocode")
        if mailing_geocode_data:
            mailing_geocode, created = Geocode.objects.get_or_create(
                immediate=True, **mailing_geocode_data
            )

            validated_data["mailing_geocode"] = mailing_geocode

        shipping_geocode_data = validated_data.get("shipping_geocode")
        if shipping_geocode_data:
            shipping_geocode, created = Geocode.objects.get_or_create(
                immediate=True, **shipping_geocode_data
            )
            validated_data["shipping_geocode"] = shipping_geocode

        user = super(UserSerializerMixin, self).update(instance, validated_data)
        return user


class UserSerializerMeta(object):
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
        "company_name",
        "company_type",
        "company_street_line1",
        "company_street_line2",
        "company_city_name",
        "company_zipcode",
        "company",
        "timezone_preference",
        "mailing_geocode_exists",
        "mailing_geocode_street_line1",
        "mailing_geocode_street_line2",
        "mailing_geocode_zipcode",
        "mailing_geocode_city",
        "mailing_geocode_city_display",
        "shipping_geocode_exists",
        "shipping_geocode_street_line1",
        "shipping_geocode_street_line2",
        "shipping_geocode_zipcode",
        "shipping_geocode_city",
        "shipping_geocode_city_display",
        "company_shipping_geocode",
        "company_shipping_geocode_street_line1",
        "company_shipping_geocode_street_line2",
        "company_shipping_geocode_city_name",
        "company_shipping_geocode_zipcode",
    )


class UserSerializer(UserSerializerMixin):
    """
    Contains full information about user
    """

    is_company_admin = serializers.ReadOnlyField()
    rater_roles_display = serializers.SerializerMethodField()

    hes_username = serializers.CharField(
        source="hes_credentials.username", allow_blank=True, allow_null=True
    )
    hes_password = serializers.CharField(
        source="hes_credentials.password", allow_blank=True, allow_null=True
    )

    class Meta(UserSerializerMeta):
        fields = UserSerializerMeta.fields + (
            "rater_roles",
            "rater_roles_display",
            "rater_id",
            "signature_image",
            "resnet_username",
            "resnet_password",
            "hes_username",
            "hes_password",
            "is_company_admin",
        )
        read_only_fields = ["signature_image"]

    def create(self, validated_data):
        raise NotImplementedError

    def validate_hes_username(self, value):
        if value is None:
            return ""
        return value

    def validate_hes_password(self, value):
        if value is None:
            return ""
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        hes_credentials_data = validated_data.pop("hes_credentials", None)
        hes_credentials = None

        user = super(UserSerializer, self).update(instance, validated_data)

        if hes_credentials_data:
            if hasattr(user, "hes_credentials"):
                hes_credentials = user.hes_credentials

            hes_credentials_data["user"] = user.id
            hes_credentials_data["company"] = user.company_id
            hes_serializer = HESCredentialsSerializer(
                instance=hes_credentials, data=hes_credentials_data
            )
            hes_serializer.is_valid(raise_exception=True)
            hes_serializer.save()
        return user

    def get_rater_roles_display(self, user):
        return ", ".join(user.rater_roles.values_list("title", flat=True))


class BasicUserSerializer(UserSerializerMixin):
    """
    Hide user secrets like rater_username, rater_password, etc.
    """

    class Meta(UserSerializerMeta):
        pass


class FlatUserSerializer(serializers.ModelSerializer):
    """
    Contains flat company fields that allows to fetch all users faster
    """

    company_id = serializers.ReadOnlyField(source="company.pk")
    company_name = serializers.ReadOnlyField(source="company.name")
    company_type = serializers.ReadOnlyField(source="company.company_type")

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
            "work_phone",
            "is_active",
            "is_public",
            "company_id",
            "company_name",
            "company_type",
        )


class UserInfoSerializer(serializers.ModelSerializer):
    """
    UserInfoSerializer is a part of build_serializer_field_from_spec function
    that perform some work that is hard to understand
    """

    company = serializers.ReadOnlyField(source="company.pk")
    name = serializers.ReadOnlyField(source="get_full_name")
    company_info = CompanyInfoSerializer(source="company")

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "username",
            "first_name",
            "last_name",
            "email",
            "title",
            "company",
            "company_info",
        )

    ref_name = "LegacyUserInfoSerializer"


class ContactCardSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    company_type_display = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = ContactCard
        fields = (
            "id",
            "first_name",
            "last_name",
            "title",
            "company",
            "user",
            "description",
            "name",
            "company_type_display",
            "company_name",
        )

    def get_name(self, contact_card):
        return contact_card.get_name()

    def get_company_type_display(self, contact_card):
        if contact_card.user_id and contact_card.user.company:
            return contact_card.user.company.get_company_type_display()
        elif contact_card.company_id:
            return contact_card.company.get_company_type_display()
        return ""

    def get_company_name(self, contact_card):
        if contact_card.user_id and contact_card.user.company:
            return contact_card.user.company.name
        elif contact_card.company_id:
            return contact_card.company.name
        return ""


class ContactCardPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCardPhone
        fields = ("id", "phone", "description", "contact")


class ContactCardEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCardEmail
        fields = ("id", "email", "description", "contact")


class UserTrainingStatusCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name",
        )


class UserTrainingStatusSerializer(serializers.ModelSerializer):
    company = UserTrainingStatusCompanySerializer()

    class Meta:
        model = TrainingStatus
        fields = "__all__"


class UserTrainingSerializer(serializers.ModelSerializer):
    training_statuses = serializers.SerializerMethodField()
    certificate_raw = serializers.CharField(required=False, write_only=True)
    certificate_raw_name = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Training
        exclude = ("statuses", "trainee")
        read_only_fields = [
            "certificate",
        ]

    # flake8: noqa: F841
    def validate(self, attrs):
        # do this hack to require document when we create it
        # but also allow send patch requests without document
        document_raw = attrs.pop("certificate_raw", None)
        document_raw_name = attrs.pop("certificate_raw_name", None)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        trainee_id = self.context["request"].data["trainee_id"]
        trainee = User.objects.get(id=trainee_id)
        user = self.context["request"].user

        validated_data["trainee"] = trainee
        instance = super(UserTrainingSerializer, self).create(validated_data)
        form = UserTrainingForm(self.context["request"].data, instance=instance, raw_file_only=True)
        form.save()

        for (
            applicable_company_slug,
            applicable_programs,
        ) in user_management_app.TRAINING_APPLICABLE_REQUIREMENTS.items():
            sponsor_company = Company.objects.get(slug=applicable_company_slug)
            if trainee.company.is_sponsored_by(
                company_slugs=[
                    sponsor_company.slug,
                ]
            ):
                program = (
                    EEPProgram.objects.filter_by_company(trainee.company)
                    .filter(slug__in=applicable_programs)
                    .first()
                )
                if program:
                    training_status = TrainingStatus(training=instance, company=sponsor_company)
                    training_status.save()

                    if user.company == program.owner:
                        training_status.approve(user=user)
                        training_status.save()

        return instance

    def get_training_statuses(self, obj):
        user = self.context["request"].user
        training_statuses = obj.trainingstatus_set.all()
        if user.id != obj.trainee_id and not user.is_superuser:
            training_statuses = training_statuses.filter(company=user.company)
        training_statuses = training_statuses.select_related("company")
        return UserTrainingStatusSerializer(training_statuses, many=True).data


class UserAccreditationSerializer(serializers.ModelSerializer):
    expiration_date = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    display_name = serializers.ReadOnlyField(source="get_name_display")
    role_display = serializers.ReadOnlyField(source="get_role_display")
    state_display = serializers.ReadOnlyField(source="get_state_display")
    accreditation_cycle_display = serializers.ReadOnlyField(
        source="get_accreditation_cycle_display"
    )

    class Meta:
        model = Accreditation
        exclude = ("trainee", "approver", "state_changed_at")

    @transaction.atomic
    def create(self, validated_data):
        trainee_id = self.context["request"].data["trainee_id"]
        trainee = User.objects.get(id=trainee_id)

        validated_data["approver"] = self.context["request"].user
        validated_data["trainee"] = trainee
        instance = super(UserAccreditationSerializer, self).create(validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data["approver"] = self.context["request"].user
        if instance.state != validated_data["state"]:
            validated_data["state_changed_at"] = timezone.now()

        return super(UserAccreditationSerializer, self).update(instance, validated_data)

    def get_expiration_date(self, obj):
        return obj.get_expiration_date()

    def get_is_expired(self, obj):
        return obj.is_expired()


class UserCertificationMetricSerializer(serializers.ModelSerializer):
    eep_program_display = serializers.ReadOnlyField(source="eep_program.name")
    name_display_link = serializers.SerializerMethodField()
    home_display = serializers.ReadOnlyField(source="home.get_home_address_display")
    home_link = serializers.HyperlinkedRelatedField(
        read_only=True, source="home", view_name="home:view"
    )

    class Meta:
        model = EEPProgramHomeStatus
        fields = (
            "eep_program",
            "eep_program_display",
            "name_display_link",
            "home",
            "home_display",
            "home_link",
            "certification_date",
        )

    def _display_user_link(self, user, role):
        return '<a href="{}" target="_blank">{}({})</a>'.format(
            reverse("profile:detail", kwargs={"pk": user.pk}), user.get_full_name(), role
        )

    def get_name_display_link(self, obj):
        names = []
        if obj.rater_of_record:
            names.append(self._display_user_link(user=obj.rater_of_record, role="Rater of Record"))
        if obj.energy_modeler:
            names.append(self._display_user_link(user=obj.energy_modeler, role="Energy Modeler"))
        names += [
            self._display_user_link(user=user, role="Field Inspector")
            for user in obj.field_inspectors.all()
        ]
        return ", ".join(names)


class UserInspectionGradeSerializer(serializers.ModelSerializer):
    grade_display = serializers.SerializerMethodField()
    inspection_grade_type = serializers.SerializerMethodField()
    numeric_grade = serializers.IntegerField(min_value=0, allow_null=False, required=True)
    letter_grade = serializers.ChoiceField(
        choices=InspectionGrade.LETTER_GRADE_CHOICES, allow_null=False, required=True
    )
    content_object_display = serializers.SerializerMethodField()
    object_link = serializers.ReadOnlyField(source="get_inspection_grade_link")

    class Meta:
        model = InspectionGrade
        fields = (
            "id",
            "graded_date",
            "content_object_display",
            "object_link",
            "qa_status",
            "letter_grade",
            "numeric_grade",
            "notes",
            "grade_display",
            "inspection_grade_type",
        )

    def get_fields(self):
        fields = super(UserInspectionGradeSerializer, self).get_fields()
        user = self.context["request"].user
        if (
            not user.company
            or user.company.inspection_grade_type == Company.LETTER_INSPECTION_GRADE
        ):
            fields.pop("numeric_grade")
        else:
            fields.pop("letter_grade")
        return fields

    def get_inspection_grade_type(self, obj):
        if self.context["request"].user and self.context["request"].user.company:
            return self.context["request"].user.company.inspection_grade_type
        return Company.LETTER_INSPECTION_GRADE

    def get_grade_display(self, obj):
        if not hasattr(obj, "user"):
            return None
        return obj.display_grade()

    def get_content_object_display(self, obj):
        if not obj or not obj.pk:
            return ""
        if getattr(obj, "qa_status", None):
            return f"{obj.qa_status.home_status} {obj.qa_status.requirement.get_type_display()}"
        return ""

    @transaction.atomic
    def create(self, validated_data):
        user_id = self.context["request"].data["user_id"]
        user = User.objects.get(id=user_id)

        validated_data["user"] = user
        validated_data["approver"] = self.context["request"].user
        instance = super(UserInspectionGradeSerializer, self).create(validated_data)
        return instance


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        # FIXME: ContentTypeResource refers to field 'content_type'
        fields = ("name", "app_label", "model")


class NestedObjectsSerializer(serializers.Serializer):
    related_objects = serializers.SerializerMethodField()

    def get_related_objects(self, obj):
        def nested_dict(obj):
            return {
                "text": "{}".format(obj),
                "url": getattr(obj, "get_absolute_url", lambda: None)(),
            }

        return collect_nested_object_list(obj, format_callback=nested_dict)
