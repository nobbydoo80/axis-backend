import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from axis.core.utils import make_safe_field, RemoteIdentifiersMixin
from axis.core.utils import values_to_dict
from axis.customer_eto.models import ETOAccount
from axis.customer_eto.serializers import PermitAndOccupancySettingsFieldsMixin
from axis.eep_program.models import EEPProgram
from axis.equipment.models import Equipment, EquipmentSponsorStatus
from axis.geocoder.models import Geocode
from axis.geographic.models import City, SUPPORTED_COUNTRIES
from axis.relationship.models import Relationship
from .managers import build_company_aliases
from .models import Company, AltName, SponsorPreferences, Contact
from .utils import can_view_or_edit_eto_account, can_edit_eto_ccb_number

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()
equipment_app = apps.get_app_config("equipment")


class CompanySerializer(PermitAndOccupancySettingsFieldsMixin, serializers.ModelSerializer):
    """Read/write serializer for new and existing companies."""

    # Virtual fields
    axis_id = make_safe_field(serializers.CharField)(source="get_id", read_only=True)
    city_name = make_safe_field(serializers.CharField)(source="city.name", read_only=True)
    city_url = make_safe_field(serializers.CharField)(
        source="city.get_absolute_url", read_only=True
    )
    state_name = make_safe_field(serializers.CharField)(source="get_state_display", read_only=True)
    hquito_accredited_name = make_safe_field(serializers.CharField)(
        source="get_hquito_accredited_display", read_only=True
    )
    utility_types = make_safe_field(serializers.CharField)(
        source="get_utility_type", required=False, read_only=True
    )
    altnames = serializers.SerializerMethodField()
    office_phone = PhoneNumberField(required=False)

    # ETO Permit and Occupancy fields
    reeds_crossing_compliance_option = serializers.SerializerMethodField()
    rosedale_parks_compliance_option = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "address_override",
            "auto_add_direct_relationships",
            "company_type",
            "default_email",
            "description",
            "home_page",
            "is_active",
            "is_customer",
            "is_eep_sponsor",
            "is_public",
            "name",
            "office_phone",
            "slug",
            "state",
            "street_line1",
            "street_line2",
            "zipcode",
            "city",
            # Hidden fields
            "id",
            "geocode_response",
            "confirmed_address",
            "latitude",
            "longitude",
            # Related fields
            "altnames",
            "altname_set",
            "sponsors",
            "resnet",
            # Provider specific fields
            "provider_id",
            "auto_submit_to_registry",
            "is_sample_eligible",
            # Rater specific fields
            "certification_number",
            # HVAC specific fields
            "hquito_accredited",
            # Utility specific fields
            "electricity_provider",
            "gas_provider",
            "water_provider",
            # Virtual fields
            "axis_id",
            "city_name",
            "city_url",
            "state_name",
            "hquito_accredited_name",
            "utility_types",
            # ETO Permit and Occupancy fields
            "reeds_crossing_compliance_option",
            "rosedale_parks_compliance_option",
        )

        read_only_fields = (
            "company_type",
            "slug",
            # Related fields
            "altname_set",
            "sponsors",
            "resnet",
        )

    def __init__(self, *args, **kwargs):
        super(CompanySerializer, self).__init__(*args, **kwargs)
        # if self.context.get("request") and self.context.get("company_type"):
        #     self._configure_extra_fields()

    # def _configure_extra_fields(self):
    #     # Singleobject behavior
    #     self._org = None
    #     if not isinstance(self.instance, list):
    #         for company_type, org_model in COMPANY_MODELS_MAP.items():
    #             if not company_type or "_utility" in company_type:
    #                 continue  # skip vanilla Company model and split utilities
    #             try:
    #                 self._org = getattr(self.instance, "{}organization".format(company_type))
    #             except:  # noqa: E722
    #                 pass
    #             else:
    #                 field_mapping = serializers.ModelSerializer.serializer_field_mapping
    #                 for f in self._org._meta.local_fields:
    #                     if f.name == "company_ptr":
    #                         continue
    #                     field_class = field_mapping[f.__class__]
    #                     self.fields[f.name] = field_class()
    #
    #         user = self.context["request"].user
    #         if not can_edit_hquito_status(user, self.instance, self.context["company_type"]):
    #             self.fields.pop("hquito_accredited", None)
    #
    #     if self._org:
    #         self.Meta.model = self._org.__class__
    #     else:
    #         self.Meta.model = COMPANY_MODELS_MAP[self.context["company_type"]]
    #
    #     # I do not understand how it is possible that this isn't being set by default by DRF.
    #     if "provider_id" in self.fields:
    #         self.fields["provider_id"].allow_null = True
    #     if "certification_number" in self.fields:
    #         self.fields["certification_number"].allow_null = True

    def get_altnames(self, instance: "company.Company") -> dict:
        if instance and instance.pk:
            qs = instance.altname_set.values("id", "name")
            return values_to_dict(qs, "id", "name")
        return {}

    def to_internal_value(self, data):
        value = super(CompanySerializer, self).to_internal_value(data)
        value["company_type"] = data["company_type"]
        value["state"] = data["state"]
        return value

    def validate(self, data):
        query_string = Q(
            street_line1=data["street_line1"],
            street_line2=data["street_line2"],
            city=data["city"],
            state=data["city"].county.state if data["city"].county else None,
            company_type=data["company_type"],
            zipcode=data["zipcode"],
        )
        query_string |= Q(office_phone=data["office_phone"], company_type=data["company_type"])

        similar = self.Meta.model.objects.filter(query_string, name__iexact=data["name"])

        if self.instance and not isinstance(self.instance, list) and self.instance.pk:
            similar = similar.exclude(id=self.instance.id)

        query_string = Q(
            name__iexact=data["name"],
            city=data["city"],
            state=data["city"].county.state if data["city"].county else None,
            company_type=data["company_type"],
        )
        check_unique_constraint = self.Meta.model.objects.filter(query_string)
        if self.instance:
            check_unique_constraint = check_unique_constraint.exclude(pk=self.instance.pk)

        if similar.count() or check_unique_constraint.count():
            model_name = self.Meta.model._meta.verbose_name
            if (
                similar.filter(name__iexact=data.get("name")).count()
                or check_unique_constraint.count()
            ):
                err = "A {model} already exists with the name '{name}'".format(
                    model=model_name, name=data["name"]
                )
                raise serializers.ValidationError(err)

        return data

    def create(self, validated_data):
        if not self.context.get("request") and not self.context.get("company_type"):
            raise serializers.ValidationError("company_type or request not found in context")
        instance = super(CompanySerializer, self).create(validated_data)

        self.instance = instance
        # self._configure_extra_fields()  # This create() fires before __init__() finishes

        # for k in self.fields:
        #     # Make sure request.data extra fields like utility flags make it to the object.
        #     # This checks if 'k' is missing, is a setting on the Org, and was not originally
        #     # included in Meta.fields (was a core Company field).
        #     # What is left should be Org-specific fields that were added during the
        #     # '_configure_extra_fields()' step but were excluded from validated_data because of
        #     # '_configure_extra_fields()' running late.
        #     if k not in validated_data and hasattr(self._org, k) and k not in self.Meta.fields:
        #         setattr(instance, k, self.context["request"].data.get(k, None))

        Relationship.objects.validate_or_create_relations_to_entity(
            entity=instance, direct_relation=self.context["request"].user.company
        )

        self._update_eto_account(instance)

        return instance

    def update(self, instance, validated_data):
        instance = super(CompanySerializer, self).update(instance, validated_data)
        self._update_eto_account(instance)
        return instance

    def _update_eto_account(self, instance):
        user = self.context["request"].user
        data = self.context["request"].data

        can_edit_account = can_view_or_edit_eto_account(user, instance.company_type)
        can_edit_ccb = can_edit_eto_ccb_number(user, instance.company_type)
        will_update_account_number = can_edit_account and "eto_account" in data
        will_update_ccb_number = can_edit_ccb and "ccb_number" in data

        if will_update_account_number or will_update_ccb_number:
            # Avoid creating excess blank ETOAccounts by doing it only when an update will occur.
            try:
                instance.eto_account
            except:  # noqa: E722
                # Assign the result to the object so that we don't have to re-fetch the company
                # to have to recognize the new object.
                instance.eto_account = ETOAccount.objects.create(company=instance)

            if will_update_account_number:
                instance.eto_account.account_number = data["eto_account"]
            if will_update_ccb_number:
                instance.eto_account.ccb_number = data["ccb_number"]
            instance.eto_account.save()


class CompanyInfoSerializer(serializers.ModelSerializer):
    url = make_safe_field(serializers.ReadOnlyField)(source="get_absolute_url")

    class Meta:
        model = Company
        fields = ("id", "name", "company_type", "url")
        ref_name = "legacy_CompanyInfoSerializer"


class CompanyEEPProgramSerializer(serializers.ModelSerializer):
    eep_programs = serializers.SerializerMethodField()
    ignored_eep_programs = serializers.SerializerMethodField()
    eep_programs_data = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ("id", "eep_programs", "eep_programs_data", "ignored_eep_programs")
        read_only_fields = ("id",)

    def get_eep_programs(self, obj):
        return list(
            EEPProgram.objects.filter_by_company(obj)
            .exclude(
                id__in=list(
                    obj.ignored_eep_programs_during_home_status_creation.values_list(
                        "id", flat=True
                    )
                )
            )
            .values_list("id", flat=True)
        )

    def get_ignored_eep_programs(self, obj):
        return list(
            obj.ignored_eep_programs_during_home_status_creation.values_list("id", flat=True)
        )

    def get_eep_programs_data(self, obj):
        return {
            program.pk: {"name": "{}".format(program), "url": program.get_absolute_url()}
            for program in EEPProgram.objects.filter_by_company(obj)
        }

    def update(self, instance, validated_data):
        programs_ids = self.initial_data.get("eep_programs", [])

        viewable_programs = EEPProgram.objects.filter_by_company(instance).exclude(
            id__in=programs_ids
        )
        instance.ignored_eep_programs_during_home_status_creation = viewable_programs

        return super(CompanyEEPProgramSerializer, self).update(instance, validated_data)


class CompanyUsersSerializer(serializers.ModelSerializer):
    admins = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    users_data = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ("id", "admins", "users", "users_data")
        read_only_fields = ("id",)

    def get_admins(self, obj):
        if obj.pk:
            return list(obj.get_admins().values_list("id", flat=True))
        return []

    def get_users(self, obj):
        if obj.pk:
            return list(obj.get_users().values_list("id", flat=True))
        return []

    def get_users_data(self, company):
        users_data = {}
        request_user = self.context["request"].user

        if company.pk:
            if not (
                request_user.is_superuser or request_user.company.id == request_user.company.id
            ) and not request_user.company.has_mutual_relationship(company):
                return users_data

            for user in company.users.all():
                users_data[user.pk] = {
                    "name": "{}".format(user),
                    "url": user.get_absolute_url(),
                    "is_admin": user.is_company_admin,
                    "is_customer": company.is_customer,
                    "is_active": user.is_active,
                    "is_public": True,
                }

        return users_data

    def update(self, instance, validated_data):
        # user = self.context["request"].user

        # We inspect self.initial_data instead of validated_data because our admins/users fields
        # are actually readonly and so don't appear in validated_data.  This is done because we
        # don't want 'users' to overwrite instance.users directly, since 'admins' needs to be added
        # to it.
        users = set(self.initial_data.get("users", []))
        admins = set(
            User.objects.filter(
                id__in=self.initial_data.get("admins", []), company=instance
            ).values_list("id", flat=True)
        )
        admin_diff = set(instance.get_admins().values_list("id", flat=True)) - admins
        # move removed admins to users
        users = users.union(admin_diff)
        #
        # if user.id not in admins:
        #     if user.company and instance.id == user.company.id:
        #         admins.add(user.id)
        # else:
        #     if user.company is None or instance.id != user.company.id:
        #         admins.remove(user.id)
        #
        # if user.id not in users:
        #     if user.company and instance.id == user.company.id:
        #         users.add(user.id)
        # else:
        #     if user.company is None or instance.id != user.company.id:
        #         users.remove(user.id)

        users = User.objects.filter(id__in=list(admins.union(users)))
        admins = User.objects.filter(id__in=list(admins))

        User.objects.update_users_for_company(users=users, admins=admins, company=instance)

        return instance


class CompanyCountiesSerializer(serializers.ModelSerializer):
    from axis.geographic.models import County

    counties_data = make_safe_field(serializers.SerializerMethodField)()
    counties = serializers.PrimaryKeyRelatedField(
        many=True, allow_empty=True, queryset=County.objects.all()
    )

    class Meta:
        model = Company
        fields = ("id", "counties", "counties_data")
        read_only_fields = ("id",)

    def get_counties_data(self, obj):
        return {county.pk: {"name": f"{county}"} for county in obj.counties.all()}

    def update(self, instance, validated_data):
        instance = super(CompanyCountiesSerializer, self).update(instance, validated_data)
        user = self.context["request"].user
        company = user.company

        counties = self.initial_data.get("counties", [])

        if not len(counties):
            from axis.geographic.models import County

            counties = [
                int(x)
                for x in County.objects.filter(state=self.instance.state).values_list(
                    "id", flat=True
                )
            ]

        if not user.is_superuser and company.city.county.id not in counties:
            counties.append(company.city.county.id)

        if not user.is_superuser and instance.city.county.id not in counties:
            counties.append(instance.city.county.id)

        instance.counties.clear()
        instance.counties.add(*counties)

        return instance


class CompanyCountriesSerializer(serializers.ModelSerializer):
    from axis.geographic.models import Country

    countries_data = make_safe_field(serializers.SerializerMethodField)()
    countries = serializers.PrimaryKeyRelatedField(
        many=True, allow_empty=True, queryset=Country.objects.filter(abbr__in=SUPPORTED_COUNTRIES)
    )

    class Meta:
        model = Company
        fields = ("id", "countries", "countries_data")
        read_only_fields = ("id",)

    def get_countries_data(self, obj):
        return {
            country.pk: {"name": f"{country.name}, ({country.abbr})"}
            for country in obj.countries.all()
        }

    def update(self, instance, validated_data):
        instance = super(CompanyCountriesSerializer, self).update(instance, validated_data)
        user = self.context["request"].user
        company = user.company

        countries = self.initial_data.get("countries", [])

        if not len(countries):
            countries = [self.instance.city.country.pk]

        if not user.is_superuser and company.city.country.id not in countries:
            countries.append(company.city.country.id)

        instance.countries.clear()
        instance.countries.add(*countries)

        return instance


class CompanyEquipmentSponsorStatusCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name")


class CompanyEquipmentSponsorStatusSerializer(serializers.ModelSerializer):
    company = CompanyEquipmentSponsorStatusCompanySerializer()

    class Meta:
        model = EquipmentSponsorStatus
        fields = "__all__"


class CompanyEquipmentSerializer(serializers.ModelSerializer):
    equipment_type_display = serializers.ReadOnlyField(source="get_equipment_type_display")
    calibration_cycle_display = serializers.ReadOnlyField(source="get_calibration_cycle_display")
    expiration_date = serializers.ReadOnlyField(source="get_expiration_date")
    is_expired = serializers.ReadOnlyField()
    assignees_display = serializers.SerializerMethodField()
    company_sponsor_status = serializers.SerializerMethodField()
    calibration_documentation_raw = serializers.CharField(required=False, write_only=True)
    calibration_documentation_raw_name = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Equipment
        fields = (
            "id",
            "equipment_type",
            "brand",
            "equipment_model",
            "serial",
            "description",
            "calibration_date",
            "calibration_cycle",
            "calibration_company",
            "assignees",
            "notes",
            "expired_equipment",
            "updated_at",
            "created_at",
            "equipment_type_display",
            "calibration_cycle_display",
            "expiration_date",
            "is_expired",
            "assignees_display",
            "company_sponsor_status",
            "calibration_documentation_raw",
            "calibration_documentation_raw_name",
        )
        read_only_fields = (
            "expired_equipment",
            "company_sponsor_status",
            "sponsors",
            "owner_company",
            "calibration_documentation",
        )
        extra_kwargs = {"assignees": {"allow_empty": True}}

    def validate(self, attrs):
        # do this hack to require document when we create it
        # but also allow send patch requests without document
        document_raw = attrs.pop("calibration_documentation_raw", None)
        document_raw_name = attrs.pop("calibration_documentation_raw_name", None)
        if not self.instance and (not document_raw or not document_raw_name):
            raise serializers.ValidationError(
                {"calibration_documentation": "This field is required"}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        from axis.company.forms import CompanyEquipmentForm

        owner_company_id = self.context["request"].data["owner_company"]
        owner_company = Company.objects.get(id=owner_company_id)
        user = self.context["request"].user

        validated_data["owner_company"] = owner_company
        instance = super(CompanyEquipmentSerializer, self).create(validated_data)
        form = CompanyEquipmentForm(
            self.context["request"].data, instance=instance, raw_file_only=True
        )
        form.save()

        for (
            applicable_company_slug,
            applicable_programs,
        ) in equipment_app.EQUIPMENT_APPLICABLE_REQUIREMENTS.items():
            program = (
                EEPProgram.objects.filter_by_company(owner_company)
                .filter(slug__in=applicable_programs)
                .first()
            )
            if program:
                equipment_sponsor_status = EquipmentSponsorStatus(
                    equipment=instance, company=Company.objects.get(slug=applicable_company_slug)
                )
                equipment_sponsor_status.save()

                if user.company.company_type == "provider" or user.company == program.owner:
                    equipment_sponsor_status.active(user=user)
                    equipment_sponsor_status.save()

        return instance

    def get_company_sponsor_status(self, obj):
        user = self.context["request"].user
        equipment_sponsor_statuses = []
        if obj.pk:
            equipment_sponsor_statuses = obj.equipmentsponsorstatus_set.all()
            if user.company_id != obj.owner_company_id and not user.is_superuser:
                equipment_sponsor_statuses = equipment_sponsor_statuses.filter(
                    company=self.context["request"].user.company
                )
            equipment_sponsor_statuses = equipment_sponsor_statuses.select_related("company")
        return CompanyEquipmentSponsorStatusSerializer(equipment_sponsor_statuses, many=True).data

    def get_assignees_display(self, obj):
        if not obj.pk:
            return ""
        names = [
            '<a href="{}">{}</a>'.format(
                reverse("profile:detail", kwargs={"pk": user.pk}), user.get_full_name()
            )
            for user in obj.assignees.all()
        ]
        return ", ".join(names)


class CompanyDescriptionSerializer(serializers.ModelSerializer):
    inspection_grade_type_display = serializers.ReadOnlyField(
        source="get_inspection_grade_type_display"
    )

    class Meta:
        model = Company
        fields = (
            "id",
            "description",
            "auto_add_direct_relationships",
            "display_raw_addresses",
            "inspection_grade_type",
            "inspection_grade_type_display",
            "logo",
        )
        read_only_fields = (
            "id",
            "auto_add_direct_relationships",
            "display_raw_addresses",
            # make image fields as read only because of AjaxBase64FileFormMixin
            "logo",
        )

    def update(self, instance, validated_attrs):
        data = self.context["request"].data

        if not instance.auto_add_direct_relationships and instance.is_eep_sponsor:
            pass  # frankly, this IF statement is clearer to read this way
        else:
            if "auto_add_direct_relationships" in data:
                instance.auto_add_direct_relationships = data["auto_add_direct_relationships"]

        if instance.id == self.context["request"].company.id:
            if "display_raw_addresses" in data:
                instance.display_raw_addresses = data["display_raw_addresses"]

        return super(CompanyDescriptionSerializer, self).update(instance, validated_attrs)


class CompanyShippingAddressSerializer(serializers.ModelSerializer):
    city_name = serializers.ReadOnlyField(source="city.as_string")

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

    class Meta:
        model = Company
        fields = (
            "street_line1",
            "street_line2",
            "city_name",
            "zipcode",
            "shipping_geocode_exists",
            "shipping_geocode_street_line1",
            "shipping_geocode_street_line2",
            "shipping_geocode_zipcode",
            "shipping_geocode_city",
            "shipping_geocode_city_display",
        )
        read_only_fields = (
            "street_line1",
            "street_line2",
            "city_name",
            "zipcode",
        )

    def validate(self, data):
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

    def create(self, validated_data):
        shipping_geocode_data = validated_data.get("shipping_geocode")
        if shipping_geocode_data:
            shipping_geocode, created = Geocode.objects.get_or_create(
                immediate=True, **shipping_geocode_data
            )
            validated_data["shipping_geocode"] = shipping_geocode

        instance = super(CompanyShippingAddressSerializer, self).create(validated_data)
        return instance

    def update(self, instance, validated_data):
        shipping_geocode_data = validated_data.get("shipping_geocode")
        if shipping_geocode_data:
            shipping_geocode, created = Geocode.objects.get_or_create(
                immediate=True, **shipping_geocode_data
            )
            validated_data["shipping_geocode"] = shipping_geocode
        return super(CompanyShippingAddressSerializer, self).update(instance, validated_data)


class CompanyCOISerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "worker_compensation_insurance")


class AltNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AltName
        fields = ("id", "company", "name")
        read_only_fields = ("id",)

    def validate(self, data):
        name = data.get("name")
        aliases = build_company_aliases()

        if name.lower() in aliases.keys():
            company = Company.objects.get(id=aliases[name.lower()])
            url = '<a href="{}">{}</a>'.format(company.get_absolute_url(), company)
            err = "This alias is already assigned or exists with {}".format(url)
            raise serializers.ValidationError(err)

        similar = self.Meta.model.objects.filter(name__iexact=data["name"])

        if self.instance and not isinstance(self.instance, list) and self.instance.pk:
            similar = similar.exclude(id=self.instance.id)

        if similar.count():
            model_name = self.Meta.model._meta.verbose_name
            if similar.filter(name__iexact=data.get("name")).count():
                err = "A {model} already exists with the name '{name}'".format(
                    model=model_name, name=data["name"]
                )
                raise serializers.ValidationError(err)

        return data


class SponsorPreferencesSerializer(serializers.ModelSerializer):
    sponsored_company_name = serializers.SerializerMethodField()
    sponsored_company_url = serializers.SerializerMethodField()

    class Meta:
        model = SponsorPreferences
        fields = (
            "id",
            "sponsored_company",
            "sponsor",
            "can_edit_profile",
            "can_edit_identity_fields",
            "notify_sponsor_on_update",
            # Virtual fields
            "sponsored_company_name",
            "sponsored_company_url",
        )
        read_only_fields = ("id", "sponsor", "sponsored_company_name", "sponsored_company_url")

    def get_sponsored_company_name(self, obj):
        if obj.pk:
            return "{}".format(obj.sponsored_company)
        return None

    def get_sponsored_company_url(self, obj):
        if obj.pk:
            return obj.sponsored_company.get_absolute_url()
        return None


class ContactSerializer(RemoteIdentifiersMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="as_string", read_only=True)
    address = serializers.SerializerMethodField()

    # Allow blank/null
    zipcode = serializers.CharField(
        max_length=15, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = Contact
        fields = (
            "id",
            "first_name",
            "last_name",
            "description",
            "street_line1",
            "street_line2",
            "city",
            "state",
            "zipcode",
            "phone",
            "email",
            "type",
            # Virtual fields
            "name",
            "address",
        )

    def get_address(self, instance):
        if instance.pk:
            return instance.get_address().replace("\n", "<br>")

    def validate(self, data):
        data = super(ContactSerializer, self).validate(data)

        contact_type = self.context["request"].query_params.get("type")
        if contact_type is not None:
            data["type"] = contact_type
        else:
            is_company = self.context["request"].data.get("is_company", False)
            if is_company is not None:
                data["type"] = "company" if is_company else "person"

        return data
