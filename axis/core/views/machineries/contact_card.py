"""contact_cards.py: """

__author__ = "Artem Hruzd"
__date__ = "05/17/2021 20:38"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.core.api import (
    ContactCardViewSet,
    ContactCardPhoneViewSet,
    ContactCardEmailViewSet,
)
from axis.core.models import ContactCard, ContactCardPhone, ContactCardEmail
from axis.examine import PanelMachinery
from axis.core.forms import ContactCardForm, ContactCardEmailForm, ContactCardPhoneForm


class ContactCardExamineMachinery(PanelMachinery):
    model = ContactCard
    form_class = ContactCardForm
    type_name = "contact_card"
    api_provider = ContactCardViewSet

    region_template = "examine/contact_card/contact_card_region.html"
    detail_template = "examine/contact_card/contact_card_detail.html"

    def get_helpers(self, instance):
        helpers = super(ContactCardExamineMachinery, self).get_helpers(instance)
        kwargs = {"context": self.context}

        helpers["machineries"] = {}
        phones = instance.phones.all() if instance.pk else []
        machinery = ContactCardPhoneExamineMachinery(objects=phones, **kwargs)
        helpers["machineries"][machinery.type_name_slug] = machinery.get_summary()

        emails = instance.emails.all() if instance.pk else []
        machinery = ContactCardEmailExamineMachinery(objects=emails, **kwargs)
        helpers["machineries"][machinery.type_name_slug] = machinery.get_summary()
        return helpers

    def get_region_dependencies(self):
        return {
            "company_new": [
                {
                    "field_name": "id",
                    "serialize_as": "company",
                }
            ],
        }


class ContactCardReadOnlyExamineMachinery(ContactCardExamineMachinery):
    can_add_new = False
    region_template = "examine/contact_card/contact_card_region_readonly.html"
    detail_template = "examine/contact_card/contact_card_detail_readonly.html"

    def can_edit_object(self, instance, user=None):
        return False

    def can_delete_object(self, instance, user=None):
        return False

    def get_helpers(self, instance):
        helpers = super(ContactCardReadOnlyExamineMachinery, self).get_helpers(instance)
        kwargs = {"context": self.context}

        helpers["machineries"] = {}
        machinery = ContactCardPhoneReadOnlyExamineMachinery(
            objects=instance.phones.all(), **kwargs
        )
        helpers["machineries"][machinery.type_name_slug] = machinery.get_summary()

        machinery = ContactCardEmailReadonlyExamineMachinery(
            objects=instance.emails.all(), **kwargs
        )
        helpers["machineries"][machinery.type_name_slug] = machinery.get_summary()
        return helpers

    def get_region_dependencies(self):
        return {
            "company_new": [
                {
                    "field_name": "id",
                    "serialize_as": "company",
                }
            ],
        }


class ContactCardPhoneExamineMachinery(PanelMachinery):
    model = ContactCardPhone
    form_class = ContactCardPhoneForm
    type_name = "contact_card_phone"
    api_provider = ContactCardPhoneViewSet

    region_template = "examine/contact_card/contact_card_phone_region.html"

    def get_visible_fields(self, instance, form):
        return ["phone", "description"]

    def get_region_dependencies(self):
        return {
            "contact_card": [
                {
                    "field_name": "id",
                    "serialize_as": "contact",
                }
            ],
        }

    def get_object_name(self, instance):
        return ""


class ContactCardPhoneReadOnlyExamineMachinery(ContactCardPhoneExamineMachinery):
    can_add_new = False
    region_template = "examine/contact_card/contact_card_phone_region_readonly.html"

    def get_new_region_endpoint(self):
        return None

    def can_edit_object(self, instance, user=None):
        return False

    def can_delete_object(self, instance, user=None):
        return False


class ContactCardEmailExamineMachinery(PanelMachinery):
    model = ContactCardEmail
    form_class = ContactCardEmailForm
    type_name = "contact_card_email"
    api_provider = ContactCardEmailViewSet

    region_template = "examine/contact_card/contact_card_email_region.html"

    def get_visible_fields(self, instance, form):
        return ["email", "description"]

    def get_region_dependencies(self):
        return {
            "contact_card": [
                {
                    "field_name": "id",
                    "serialize_as": "contact",
                }
            ],
        }

    def get_object_name(self, instance):
        return ""


class ContactCardEmailReadonlyExamineMachinery(ContactCardEmailExamineMachinery):
    can_add_new = False
    region_template = "examine/contact_card/contact_card_email_region_readonly.html"

    def get_new_region_endpoint(self):
        return None

    def can_edit_object(self, instance, user=None):
        return False

    def can_delete_object(self, instance, user=None):
        return False
