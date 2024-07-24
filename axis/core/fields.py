"""fields.py: Core Fields"""


import logging
import uuid
from collections import namedtuple

import cryptography.fernet
from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import CharField, Field
from django.urls import reverse_lazy, reverse
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from hashid_field import Hashid
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class AxisJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Hashid):
            return str(obj)
        return super(AxisJSONEncoder, self).default(obj)


class AxisJSONRenderer(JSONRenderer):
    encoder_class = AxisJSONEncoder


class AxisJSONField(models.JSONField):
    def __init__(
        self,
        verbose_name=None,
        name=None,
        encoder=None,
        decoder=None,
        **kwargs,
    ):
        if not encoder:
            encoder = AxisJSONEncoder
        super().__init__(
            verbose_name=verbose_name,
            name=name,
            encoder=encoder,
            decoder=decoder,
            **kwargs,
        )


class UUIDField(models.CharField):
    """A zero-configuration uuid field."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 64)
        kwargs.setdefault("blank", True)
        super(UUIDField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if add and not value:
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        return super(models.CharField, self).pre_save(model_instance, add)


# namedtuple class for get_results() to return.
AutoFieldResultsTuple = namedtuple("AutoFieldResultsTuple", ("error", "has_more", "results"))


class ViewSetMixin(object):
    """Uses the ``get_results()`` method to ask an api ModelResource for its objects."""

    page_length = 20
    viewset_class = None

    def __init__(self, viewset_class=None, *args, **kwargs):
        if viewset_class:
            self.viewset_class = viewset_class
        if self.viewset_class is None:
            raise ValueError("Must specify viewset_class on Widget or as init kwarg")
        super(ViewSetMixin, self).__init__(*args, **kwargs)

    def get_queryset(self):
        viewset = self.viewset_class()
        return viewset.get_queryset()

    def filter_queryset(self, request, term, queryset):
        queryset = self.get_queryset()

        # Correctly restrict the queryset based on user/company/etc
        viewset = self.viewset_class()
        viewset.request = request
        queryset = viewset.filter_queryset(queryset)

        # Let django_select2 build its Q() objects for word filters
        return super(ViewSetMixin, self).filter_queryset(term, queryset)

    # # This is ignored due to a bug in django_select2.
    # # https://github.com/applegrew/django-select2/issues/34
    # # We are currently relying on our patched branch at:
    # # https://github.com/pivotal-energy-solutions/django-select2
    # def get_val_txt(self, value):
    #     """ Looks up the ``value`` id from the ModelResource's model. """
    #     try:
    #         obj = self.queryset.model.objects.get(pk=int(value))
    #         return self.label_from_instance(obj)
    #     except (ValueError, TypeError):
    #         return None

    @classmethod
    def get_reverse_data(cls, term="", page=1):
        """Testing utility to return the GET data required to send an ajax query to the field."""
        instance = cls()
        instance.build_attrs({})
        instance.set_to_cache()
        return {
            "field_id": instance.widget_id,
            "term": term,
            "page": page,
        }


class ApiModelSelect2Widget(ViewSetMixin, ModelSelect2Widget):
    pass


class ApiModelSelect2MultipleWidget(ViewSetMixin, ModelSelect2MultipleWidget):
    pass


class BaseApiModelChoiceField(object):
    """
    Formfield that stands in for ModelChoiceField and reads the model and queryset from the viewset,
    saving the repetition of declaring it on the form.  The default widget is our matching
    API-variant django_select2 widget.
    """

    widget_class = None

    def __init__(self, viewset_class=None, *args, **kwargs):
        widget = kwargs.get("widget")
        if viewset_class is None and widget is None:
            raise ValueError("Need one of 'viewset_class' or 'widget'")
        if viewset_class is None:
            viewset_class = widget.viewset_class

        viewset = viewset_class()  # not sending a 'request' object; no reference available for it
        queryset = viewset.get_queryset()
        if viewset.paginator and viewset.paginator.page_size:
            self.widget_class.max_results = viewset.paginator.page_size
        if widget is None:
            raise KeyError("widget_class is undefined")
            # kwargs['widget'] = widget_class(viewset_class)

        # Send the implicit queryset declared by the viewset
        super(BaseApiModelChoiceField, self).__init__(queryset=queryset, *args, **kwargs)


class ApiModelChoiceField(BaseApiModelChoiceField, forms.ModelChoiceField):
    widget_class = ApiModelSelect2Widget


class ApiModelMultipleChoiceField(BaseApiModelChoiceField, forms.ModelMultipleChoiceField):
    widget_class = ApiModelSelect2MultipleWidget


# FIXME: This is broke.  Don't know where we're going with it yet
class UnattachedOrNewMixin(object):
    """
    When added to one of the ApiModelSelect2Widget subclasses, this mixin augments the field with a
    special ajax responder.  When the user searches for a string, the widget will offer back their
    string as a new "creation" option (which allows them to continue filling out the form). However,
    if they select an existing result from the ajax response, they are redirected through a
    relationship addition.

    This mixin requires that the template is including ``{{ STATIC_URL }}js/dynamic_add.js``, and
    that the template calls the initialization javascript function ``dynamic_get_or_create()`` in
    the document.ready handler.

    Forms that use fields generated with this mixin should be implementing
    ``axis.core.forms.DynamicGetOrCreateMixin`` as well, which auto-destroys the complex widget if
    the form is in an UpdateView, returning it to a simple CharField.
    """

    def build_attrs(self, *args, **kwargs):
        # FIXME: ???
        # kwargs['attrs'].update({
        #     'placeholder': "Enter name or search for existing",
        # })

        # Generate the relationship:add url
        model = self.viewset_class.model
        app_label = model._meta.app_label
        model = model._meta.model_name
        url = reverse_lazy("relationship:add", kwargs={"app_label": app_label, "model": model})
        self.relationship_add_url = url

        return super(UnattachedOrNewMixin, self).build_attrs(*args, **kwargs)

    # def get_val_txt(self, value):
    #     """
    #     Allows an invalid value to come through anyway.  This is necessary for adhoc creation.
    #     """
    #     txt = super(UnattachedOrNewMixin, self).get_val_txt(value)
    #
    #     # If the value failed to validate normally, let it through anyway
    #     if txt is None and value:
    #         return value
    #     return txt
    #
    # def validate(self, value):
    #     """ Validates only basic required flag.  Newly created values won't be in the queryset. """
    #     if value in validators.EMPTY_VALUES and self.required:
    #         raise forms.ValidationError(self.error_messages['required'])


# rest_framework fields. These are not for native forms.
class ManyToManyNameField(serializers.Field):
    def __init__(self, field_lookup, id_field="id", name_field="name"):
        super(ManyToManyNameField, self).__init__()
        self.field_lookup = field_lookup
        self.id_field = id_field
        self.name_field = name_field

    def field_to_native(self, obj, field_name):
        if obj.pk:
            return dict(getattr(obj, self.field_lookup).values_list(self.id_field, self.name_field))
        return {}


class ManyToManyUrlField(serializers.Field):
    def __init__(self, field_lookup, reverse_lookup, id_field="id"):
        super(ManyToManyUrlField, self).__init__()
        self.field_lookup = field_lookup
        self.reverse_lookup = reverse_lookup
        self.id_field = id_field

    def field_to_native(self, obj, field_name):
        if obj.pk:
            ids = getattr(obj, self.field_lookup).values_list(self.id_field, flat=True)
            return {id: reverse(self.reverse_lookup, kwargs={"pk": id}) for id in ids}
        return {}


# Note this was shamelessly pulled from
# https://gitlab.com/lansharkconsulting/django/django-encrypted-model-fields


def parse_key(key):
    """If the key is a string we need to ensure that it can be decoded"""
    return cryptography.fernet.Fernet(key)


def get_crypter():
    """Get the Crypter"""
    configured_keys = getattr(settings, "FIELD_ENCRYPTION_KEY", None)

    if configured_keys is None:
        raise ImproperlyConfigured("FIELD_ENCRYPTION_KEY must be defined in settings")

    try:
        # Allow the use of key rotation
        if isinstance(configured_keys, (tuple, list)):
            keys = [parse_key(k) for k in configured_keys]
        else:
            # else turn the single key into a list of one
            keys = [
                parse_key(configured_keys),
            ]
    except Exception as e:
        raise ImproperlyConfigured("FIELD_ENCRYPTION_KEY defined incorrectly: {}".format(str(e)))

    if len(keys) == 0:
        raise ImproperlyConfigured("No keys defined in setting FIELD_ENCRYPTION_KEY")

    return cryptography.fernet.MultiFernet(keys)


CRYPTER = None


def encrypt_str(s):
    """Encrypt String"""
    global CRYPTER
    if CRYPTER is None:
        CRYPTER = get_crypter()
    return CRYPTER.encrypt(s.encode("utf-8"))


def decrypt_str(t):
    """Decrypt String"""
    global CRYPTER
    if CRYPTER is None:
        CRYPTER = get_crypter()
    return CRYPTER.decrypt(t.encode("utf-8")).decode("utf-8")


def calc_encrypted_length(n):
    """Calculates the characters necessary to hold an encrypted string of # n bytes"""
    return len(encrypt_str("a" * n))


class EncryptedMixin(Field):
    """Encryption Mixin"""

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, (bytes, str)):
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            if len(value):
                try:
                    value = decrypt_str(value)
                except cryptography.fernet.InvalidToken:
                    key = settings.FIELD_ENCRYPTION_KEY[0:8] + "..."
                    log.warning(
                        f"InvalidToken. Possible incorrect FIELD_ENCRYPTION_KEY {key} - {value}"
                    )
        return super(EncryptedMixin, self).to_python(value)

    def from_db_value(self, value, *args, **kwargs):
        return self.to_python(value)

    def get_db_prep_save(self, value, connection):
        value = super(EncryptedMixin, self).get_db_prep_save(value, connection)

        if value is None:
            return value
        # decode the encrypted value to a unicode string, else this breaks in pgsql
        return (encrypt_str(str(value))).decode("utf-8")

    def get_internal_type(self):
        return "TextField"

    def deconstruct(self):
        name, path, args, kwargs = super(EncryptedMixin, self).deconstruct()

        if "max_length" in kwargs:
            del kwargs["max_length"]

        return name, path, args, kwargs


class EncryptedCharField(EncryptedMixin, CharField):
    """Encrypted field"""

    pass
