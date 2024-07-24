"""contact_card.py: """

__author__ = "Artem Hruzd"
__date__ = "05/12/2021 12:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import transaction
from rest_framework import serializers

from axis.core.api_v3.serializers import UserInfoSerializer
from axis.core.models import ContactCardPhone, ContactCard, ContactCardEmail


class ContactCardPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCardPhone
        fields = ("id", "contact", "phone", "description")
        read_only_fields = ("contact",)


class ContactCardEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactCardEmail
        fields = ("id", "contact", "email", "description")
        read_only_fields = ("contact",)


class ContactCardSerializer(serializers.ModelSerializer):
    phones = ContactCardPhoneSerializer(many=True)
    emails = ContactCardEmailSerializer(many=True)
    user_info = UserInfoSerializer(source="user", read_only=True)
    company_info = serializers.SerializerMethodField()
    name = serializers.CharField(source="get_name", read_only=True)

    class Meta:
        model = ContactCard
        fields = (
            "id",
            "description",
            "phones",
            "emails",
            "user",
            "user_info",
            "company",
            "company_info",
            "name",
            "first_name",
            "last_name",
            "title",
            "protected",
        )
        read_only_fields = ("protected",)

    def validate(self, attrs):
        if self.instance and self.instance.protected:
            raise serializers.ValidationError({"user": "You cannot modify protected contact"})
        return super(ContactCardSerializer, self).validate(attrs)

    def create(self, validated_data):
        phones_data = validated_data.pop("phones")
        emails_data = validated_data.pop("emails")
        contact_card = ContactCard.objects.create(**validated_data)
        for phone_data in phones_data:
            ContactCardPhone.objects.create(contact=contact_card, **phone_data)
        for email_data in emails_data:
            ContactCardEmail.objects.create(contact=contact_card, **email_data)
        return contact_card

    def get_company_info(self, contact_card: ContactCard):
        from axis.company.api_v3.serializers import CompanyInfoSerializer

        return CompanyInfoSerializer(instance=contact_card.company).data

    @transaction.atomic
    def update(self, instance, validated_data):
        phones_data = validated_data.pop("phones")
        emails_data = validated_data.pop("emails")

        self._nested_data_update(
            lines_data=phones_data, instance=instance, related_name="phones", model=ContactCardPhone
        )

        self._nested_data_update(
            lines_data=emails_data, instance=instance, related_name="emails", model=ContactCardEmail
        )
        return super(ContactCardSerializer, self).update(instance, validated_data)

    def _nested_data_update(self, instance, lines_data, related_name, model):
        # get all nested objects related with this instance and make a dict(id, object)
        lines_dict = dict((i.id, i) for i in getattr(instance, related_name).all())

        for line_data in lines_data:
            line_data_id = line_data.pop("id", None)
            if line_data_id:
                # if exists id remove from the dict and update
                line = lines_dict.pop(line_data_id)
                for key, value in line_data.items():
                    setattr(line, key, value)
                line.save()
            else:
                # else create a new object
                model.objects.create(contact=instance, **line_data)

        # delete remaining elements because they're not present in call
        for line in lines_dict.values():
            if line.id:
                line.delete()
