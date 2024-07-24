import logging

from django.core.exceptions import ValidationError
from django.db.models import Manager
from rest_framework import serializers

from axis.company.models import Contact
from django.contrib.auth import get_user_model
from axis.eep_program.models import EEPProgram
from axis.geographic.models import City
from ... import models
from ...api.serializers import (
    WorkflowStatusSerializer,
    CertifiableObjectSerializer,
    PreliminaryValidationWorkflowStatusSerializer,
)

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class FullChildListSerializer(serializers.ListSerializer):
    """
    Creates a new instance of the child serializer for every instance so that they can derive fields
    dynamically based on an instance they receive at initialization (instead of statelessly sending)
    a different instance to its to_representation() over and over).
    """

    def to_representation(self, data):
        iterable = data.all() if isinstance(data, Manager) else data
        data = []
        for item in iterable:
            child = self.child.__class__(item, context=self.context)
            data.append(child.data)

        return data


class ProgramSerializer(serializers.Serializer):
    ProgramName = serializers.CharField()


class AddressSerializer(serializers.Serializer):
    # TRC sends all of these blank when the Address itself is missing on the parent serializer
    Street1 = serializers.CharField(allow_blank=True)
    Street2 = serializers.CharField(allow_blank=True)
    City = serializers.CharField(allow_blank=True)
    State = serializers.CharField(allow_blank=True)
    PostalCode = serializers.CharField(allow_blank=True)


class UserSerializer(serializers.Serializer):
    ContactId = serializers.CharField()
    FirstName = serializers.CharField()
    LastName = serializers.CharField()
    Email = serializers.CharField()
    Telephone = serializers.CharField(allow_blank=True)


class ContactPersonSerializer(serializers.Serializer):
    ContactId = serializers.CharField()
    FirstName = serializers.CharField()
    LastName = serializers.CharField()
    Email = serializers.CharField()
    Telephone = serializers.CharField()
    Address = AddressSerializer()


class ContactCompanySerializer(serializers.Serializer):
    CompanyId = serializers.CharField()
    Name = serializers.CharField()
    Website = serializers.CharField(allow_blank=True)
    MainPhone = serializers.CharField(allow_blank=True)
    Address = AddressSerializer()

    # TRC sends these, but the contacts are also represented at the top level of the JSON structure
    # regardless of there being a company involved or not.
    # PrimaryContact = ContactPersonSerializer()
    # ProjectContact = ContactPersonSerializer()


class ProjectLocationSerializer(serializers.Serializer):
    Name = serializers.CharField()
    Address = AddressSerializer()


class ImportSerializer(serializers.Serializer):
    """Translates TRC import request to format required by the core serializers."""

    TrcProjectId = serializers.CharField()
    ProjectName = serializers.CharField()
    ProjectNumber = serializers.CharField(allow_blank=True)
    ProjectStatus = serializers.CharField()
    ConstructionType = serializers.CharField()
    Program = ProgramSerializer()
    NumberOfBuildings = serializers.IntegerField(allow_null=True)
    NumberOfUnits = serializers.IntegerField(allow_null=True)
    LeadContactDateTime = serializers.DateTimeField(allow_null=True)
    PreQualDateTime = serializers.DateTimeField(allow_null=True)
    EnergyContact = UserSerializer()
    ProjectLocation = ProjectLocationSerializer()
    CustomerCompany = ContactCompanySerializer()
    CustomerContact = ContactPersonSerializer()
    PayeeCompany = ContactCompanySerializer()
    PayeeContact = ContactPersonSerializer()

    # Generic data getters based on incoming data
    def _determine_axis_city(self, data):
        queryset = City.objects.filter_by_user(self.context["request"].user)
        queryset = queryset.filter(
            **{
                "name": data["City"],
                "county__state": data["State"],
            }
        )

        city = queryset.first()  # FIXME: Not sure if this is aggressive enough

        return city

    def _determine_eep_program(self, data):
        """Inspection EEPProgram's workflow_default_settings json data for its 'type'."""
        construction_type = None
        if data["ConstructionType"] == "New Construction":
            construction_type = "new_construction"
        else:
            construction_type = "retrofit"

        user = self.context["request"].user
        queryset = EEPProgram.objects.filter(owner=user.company).exclude(workflow=None)
        for eep_program in queryset.only("id", "workflow", "workflow_default_settings"):
            if eep_program.workflow_default_settings["type"] == construction_type:
                return eep_program
        return None

    def _determine_user(self, contact_data):
        """Uses contact_data for a User lookup.  May return None if the user can't be resolved."""
        if not contact_data.get("ContactId"):
            return None

        company = self.context["request"].user.company
        lookup_kwargs = {
            "company": company,
            "identifiers__type": "trc",
            "identifiers__id": contact_data["ContactId"],
        }

        user = User.objects.filter(**lookup_kwargs)
        if user.count() == 0:
            # Determine if the identifier is just not set up or if there is no match at all
            lookup_kwargs = {
                "company": company,
                "email__iexact": contact_data["Email"],
            }
            user = User.objects.filter(**lookup_kwargs)
            log.info(
                "TRC identifier %r appears not to be in use within Axis yet; falling back to "
                "email lookup: %r",
                contact_data["ContactId"],
                lookup_kwargs,
            )

        # Turn 'user' from queryset (possibly empty) to a single instance
        if user.count() == 1:
            user.update(
                **{
                    "first_name": contact_data["FirstName"],
                    "last_name": contact_data["LastName"],
                    "work_phone": contact_data["Telephone"],
                    # The only user they send us right now doesn't carry an 'Address' section.
                    # Enable this if that changes.
                    #
                    # 'street_line1': contact_data['Address']['Street1'],
                    # 'street_line2': contact_data['Address']['Street2'],
                    # 'city': self._determine_axis_city(contact_data['Address']),
                    # 'zipcode': contact_data['Address']['PostalCode'],
                }
            )
            user = user.first()
            trc_id = user.get_remote_identifier("trc")
            if trc_id is None:
                user.set_remote_identifier("trc", contact_data["ContactId"])
            elif trc_id != contact_data["ContactId"]:
                raise ValidationError(
                    "TRC identifier %r does not match existing identifier %r for "
                    "the same user lookup: %r"
                    % (
                        contact_data["ContactId"],
                        trc_id,
                        lookup_kwargs,
                    )
                )
        else:
            if user.count() > 1:
                user_ids = map(str, user.values_list("id", flat=True))
                log.warning(
                    "Unable to disambiguate specified user between ids [%s]: %r",
                    ", ".join(user_ids),
                    lookup_kwargs,
                )
            user = self._get_default_user(company)
            if user:
                log.warning(
                    "Defaulting to user id=%s (%s) for missing user: %r",
                    user.id,
                    "{}".format(user),
                    lookup_kwargs,
                )
            else:
                log.error(
                    "Can't find a default user to substitute for unresolvable user details: %r",
                    lookup_kwargs,
                )

        return user

    def _get_default_user(self, company):
        try:
            user = User.objects.get(company=company, first_name="Mekha", last_name="Abraham")
        except User.DoesNotExist:
            user = None
        return user

    def _get_and_update_contact(self, lookup_kwargs, update, remote_id):
        contact, _ = Contact.objects.get_or_create(**lookup_kwargs)

        for k, v in update.items():
            setattr(contact, k, v)
        contact.save()

        trc_id = contact.get_remote_identifier("trc")
        if trc_id is None:
            contact.set_remote_identifier("trc", remote_id)

        return contact

    def _determine_contact_company(self, contact_data):
        """Uses lookup_kwargs for a get_or_create() call.  contact_data is 'defaults'."""
        if not contact_data.get("CompanyId"):
            return None

        lookup_kwargs = {
            "company": self.context["request"].user.company,
            "type": "company",
            "identifiers__type": "trc",
            "identifiers__id": contact_data["CompanyId"],
        }
        contact = self._get_and_update_contact(
            lookup_kwargs,
            update={
                "first_name": contact_data["Name"],
                "description": contact_data["Website"],
                "phone": contact_data["MainPhone"],
                "street_line1": contact_data["Address"]["Street1"] or None,
                "street_line2": contact_data["Address"]["Street2"] or None,
                "city": self._determine_axis_city(contact_data["Address"]),
                "state": contact_data["Address"]["State"] or None,
                "zipcode": contact_data["Address"]["PostalCode"] or None,
            },
            remote_id=contact_data["CompanyId"],
        )

        return contact

    def _determine_contact_person(self, contact_data):
        """Uses lookup_kwargs for a get_or_create() call.  contact_data is 'defaults'."""
        if not contact_data.get("ContactId"):
            return None

        lookup_kwargs = {
            "company": self.context["request"].user.company,
            "type": "person",
            "identifiers__type": "trc",
            "identifiers__id": contact_data["ContactId"],
        }
        contact = self._get_and_update_contact(
            lookup_kwargs,
            update={
                "first_name": contact_data["FirstName"],
                "last_name": contact_data["LastName"],
                "email": contact_data["Email"],
                "phone": contact_data["Telephone"],
                "street_line1": contact_data["Address"]["Street1"] or None,
                "street_line2": contact_data["Address"]["Street2"] or None,
                "city": self._determine_axis_city(contact_data["Address"]),
                "state": contact_data["Address"]["State"] or None,
                "zipcode": contact_data["Address"]["PostalCode"] or None,
            },
            remote_id=contact_data["ContactId"],
        )

        return contact

    # Higher concepts that use the generic getters
    def _determine_energy_advisor(self, data):
        return self._determine_user(data["EnergyContact"])

    def _determine_payee_company(self, data):
        return self._determine_contact_company(data["PayeeCompany"])

    def _determine_payee_contact(self, data):
        return self._determine_contact_person(data["PayeeContact"])

    def _determine_customer_company(self, data):
        return self._determine_contact_company(data["CustomerCompany"])

    def _determine_customer_contact(self, data):
        return self._determine_contact_person(data["CustomerContact"])

    # Main validation
    def validate(self, data):
        # Sanity note: If this serializer doesn't validate and all you're getting is
        # "non_field_errors" with errors it won't let you match to a field, it's because these outer
        # customer serializers validated fine but the inner Axis ones did not.  The Axis ones are
        # using field names that don't appear on the TRC serializers, so they're forced into a
        # generic error slot when we try copying them into the validation error dict.
        #
        # Inspect the individual inner serializer.error dicts near the end of this method to figure
        # out what's going wrong with the way we setup up the serializers.

        def _id_or_None(obj):
            if obj:
                return obj.id
            return None

        def _date_or_None(datetime):
            if datetime:
                return datetime.date()
            return None

        misc_errors = {}  # Field errors that the serializers won't raise for us

        # CertifiableObject
        object_data = {
            "project_id": data["TrcProjectId"],
            "project_name": data["ProjectName"],
            "project_number": data["ProjectNumber"],
            "project_street1": data["ProjectLocation"]["Address"]["Street1"],
            "project_street2": data["ProjectLocation"]["Address"]["Street2"],
            "project_city": data["ProjectLocation"]["Address"]["City"],
            "project_state": data["ProjectLocation"]["Address"]["State"],
            "project_zip": data["ProjectLocation"]["Address"]["PostalCode"],
        }

        # This doesn't work; we need to add a serializer field such as 'raw' to hold this so that it
        # doesn't just get stripped away during validation.
        # # WorkflowStatus
        # # Throw everything else sent to us into the data field so we don't lose anything we didn't
        # # correctly interpret.
        # status_data = data.copy()

        status_data = {}
        eep_program = self._determine_eep_program(data)
        try:
            energy_advisor = self._determine_energy_advisor(data)
        except ValidationError as e:
            energy_advisor = None
            misc_errors["energy_advisor"] = e.messages
        status_data.update(
            {
                "eep_program": _id_or_None(eep_program),  # None means error later
                "energy_advisor": _id_or_None(energy_advisor),
                "payee_company": _id_or_None(self._determine_payee_company(data)),
                "payee_contact": _id_or_None(self._determine_payee_contact(data)),
                "customer_company": _id_or_None(self._determine_customer_company(data)),
                "customer_contact": _id_or_None(self._determine_customer_contact(data)),
                "number_of_buildings": data["NumberOfBuildings"],
                "number_of_units": data["NumberOfUnits"],
                "lead_contact_date": _date_or_None(data["LeadContactDateTime"]),
                "pre_qual_start_date": _date_or_None(data["PreQualDateTime"]),
            }
        )

        self.obj_serializer = CertifiableObjectSerializer(
            data=object_data,
            context={
                "type": "project",
                "request": self.context["request"],
            },
        )
        self.prelim_status_serializer = PreliminaryValidationWorkflowStatusSerializer(
            data=status_data,
            context={
                "type": "project",
                "request": self.context["request"],
                "workflow": eep_program.workflow,
                "json_fields_settings": eep_program.workflow_default_settings,
            },
        )
        self.status_serializer = WorkflowStatusSerializer(
            data=status_data,
            context={
                "type": "project",
                "request": self.context["request"],
                "workflow": eep_program.workflow,
                "json_fields_settings": eep_program.workflow_default_settings,
            },
        )

        # Joint validation
        error = ValidationError({})
        error.error_dict.update(misc_errors)
        if not self.obj_serializer.is_valid():
            error.error_dict.update(self.obj_serializer.errors)
        if not self.prelim_status_serializer.is_valid():
            error.error_dict.update(self.prelim_status_serializer.errors)

        if len(error.error_dict):
            # Errors with field names not on the top-level serializer get lost in a non_field_errors
            # key with no hint about where they came from.  Thanks DRF.
            # Store the errors as generated and return that as the response payload instead of what
            # the serializer coerced into field-errors vs non-field-errors.
            self.raw_errors = error.error_dict

            # Raise all validation errors together
            raise error

        return data

    def save(self, **kwargs):
        certifiable_object = self.obj_serializer.save()

        # Note that we're assuming status_serializer is valid because prelim_status_serializer
        # passed validation.  This real serializer needs more info to be fully valid, which we
        # provide now.
        self.status_serializer.initial_data["certifiable_object"] = certifiable_object.id
        self.status_serializer.is_valid(raise_exception=True)
        workflow_status = self.status_serializer.save()
        workflow_status.set_remote_identifier("trc", certifiable_object.settings["project_id"])

        return workflow_status


class SummarySerializer(WorkflowStatusSerializer):
    certifiable_object = CertifiableObjectSerializer()  # We want a fully nested repr
    changed_date = serializers.SerializerMethodField()

    class Meta:
        list_serializer_class = FullChildListSerializer
        model = models.WorkflowStatus
        fields = (
            "id",
            "owner",
            "owner_info",
            "workflow",
            "eep_program",
            "eep_program_info",
            "certifiable_object",
            "state",
            "state_description",
            "data",
            "completion_date",
            "changed_date",
        )
        read_only_fields = ("workflow", "state", "completion_date", "changed_date")

    def get_changed_date(self, instance):
        most_recent_modified_date = list(
            sorted(
                [
                    instance.modified_date,
                    instance.certifiable_object.modified_date,
                ]
            )
        )[-1]
        return most_recent_modified_date
