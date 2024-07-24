"""placedmodels.py: Temporary geographic models"""


import six
from django.db import models
from django.db.models.base import ModelBase

from localflavor.us.models import USStateField

from .utils.legacy import (
    get_address_designator,
    save_geocoded_model,
    load_geocode_response_data,
    denormalize_related_references,
)
from . import strings

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class PlaceSynchronizationMixin(object):
    """Synchronization logic for PlacedModels to update their Place FKs"""

    def save(self, *args, **kwargs):
        """
        Keeps data in sync with related Place.

        Note that to have a two way sync we need a way to tell either party
        when it is being updated by the other, to avoid recursion. So we add
        a kwarg that lets us do just that. If a sublcass of this has overridden
        its save method, its signature must be changed to allow for this kwarg.

        """
        # If save is being called because the related Place called it, we will
        # skip the data updating.
        if not kwargs.pop("saved_from_place", False):
            save_geocoded_model(self)
            self.update_to_place()
            self.place.save(saved_from_placed_object=True)

        return super(PlaceSynchronizationMixin, self).save(*args, **kwargs)

    @classmethod
    def DENORMALIZED_PLACE_FIELDS(cls):
        """Transitional property to allow automatic nomination of applicable Place fields."""
        return []

    def update_from_place(self):
        if self.place is None:
            self.create_place()

        for field in self.DENORMALIZED_PLACE_FIELDS():
            setattr(self, field, getattr(self.place, field, None))

    def update_to_place(self):
        if self.place is None:
            self.create_place()

        for field in self.DENORMALIZED_PLACE_FIELDS():
            setattr(self.place, field, getattr(self, field, None))

    def create_place(self):
        from .models import Place

        try:
            self.place, create = Place.objects.get_or_create(
                **{f: getattr(self, f, None) for f in self.DENORMALIZED_PLACE_FIELDS()}
            )
        except Place.MultipleObjectsReturned:
            self.place = list(
                Place.objects.filter(
                    **{f: getattr(self, f, None) for f in self.DENORMALIZED_PLACE_FIELDS()}
                )
            )[-1]


class PlacedModel(PlaceSynchronizationMixin, models.Model):
    """Core place information common to all geocoded models."""

    place = models.ForeignKey(
        "geographic.Place",
        null=True,
        blank=True,
        related_name="%(class)s_set",
        on_delete=models.SET_NULL,
    )
    geocode_response = models.ForeignKey(
        "geocoder.GeocodeResponse",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The response this place was constructed from.",
    )

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    state = USStateField(
        null=True, editable=False, verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_STATE
    )
    metro = models.ForeignKey(
        "geographic.Metro",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_METRO,
    )
    climate_zone = models.ForeignKey(
        "geographic.ClimateZone", editable=False, blank=True, null=True, on_delete=models.SET_NULL
    )

    confirmed_address = models.BooleanField(default=False)
    address_override = models.BooleanField(
        verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_ADDRESS_OVERRIDE,
        help_text=strings.PLACEDMODEL_HELP_TEXT_ADDRESS_OVERRIDE,
        default=False,
    )

    class Meta:
        abstract = True

    @classmethod
    def DENORMALIZED_PLACE_FIELDS(cls):
        """Transitional property to allow automatic nomination of applicable Place fields."""
        fields = super(PlacedModel, cls).DENORMALIZED_PLACE_FIELDS()
        fields.extend(
            [
                "geocode_response",
                "latitude",
                "longitude",
                "state",
                "metro",
                "climate_zone",
                "confirmed_address",
                "address_override",
            ]
        )
        return fields

    def get_geocoding_type(self):
        """Indicates which type of geocoding logic is required for the templates."""
        return self._meta.model_name.lower()

    def get_address_designator(self):
        return get_address_designator(self)

    def denormalize_related_references(self):
        """Copies FKs from related fields to local ones."""
        denormalize_related_references(self)

    def load_geocode_response_data(self):
        """Transplants raw geocoder data to the Place or PlacedModel."""
        load_geocode_response_data(self)


class GeneralPlacedModelType(ModelBase):
    """
    Your developers regret to inform you that a metaclass was required to solve this problem:

    Some of our legacy geo-aware models had FKs to common models, but with varying options, such as
    ``null`` being sometimes True, sometimes False.

    This metaclass intercepts Model creation at the earliest stage of definition.  It adds the items
    contained in DYNAMIC_FIELDS to that model as fields, but with options customized by the model.

    For example, the PlacedModel can't define a ``city`` field that is null=True for some subclasses
    and null=False for others.  Configuration options on PlacedModel, such as ``CITY_IS_NULLABLE``,
    allows this metaclass to inspect the new model and decide if the city should be null=True or
    null=False.
    """

    # These fields will be created on PlacedModel subclasses based on options given by those
    # subclasses.
    DYNAMIC_FIELDS = [
        (
            "city",
            models.ForeignKey,
            ("geographic.City",),
            {
                "help_text": strings.PLACEDMODEL_HELP_TEXT_CITY,
                "verbose_name": strings.PLACEDMODEL_VERBOSE_NAME_CITY,
                "on_delete": models.CASCADE,
            },
        ),
        (
            "county",
            models.ForeignKey,
            ("geographic.County",),
            {
                "help_text": strings.PLACEDMODEL_HELP_TEXT_COUNTY,
                "verbose_name": strings.PLACEDMODEL_VERBOSE_NAME_COUNTY,
                "on_delete": models.CASCADE,
            },
        ),
    ]
    # Options that will be looked up on the PlacedModel subclass for customization.
    # The "%s" will be filled in with the field's uppercased name, such as CITY_IS_NULLABLE.
    # "help_text" will always be read from the "geographic.strings" module.
    DYNAMIC_OPTIONS = {
        "null": "%s_IS_NULLABLE",
        "blank": "%s_IS_NULLABLE",
    }

    def __new__(cls, name, bases, attrs):
        """Inject dynamic field options according to PlacedModel subclass options."""
        super_new = super(GeneralPlacedModelType, cls).__new__

        # Little bit of internal Django logic from ModelBase, which skips the primary base class
        # when processing metaclass logic.  In this case, we want to skip PlacedModel.
        parents = [
            b
            for b in bases
            if isinstance(b, GeneralPlacedModelType)
            and not (b.__name__ == "NewBase" and b.__mro__ == (b, object))
        ]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # MODEL_NAME = cls.__name__.upper()

        # Iterate DYNAMIC_FIELDS and inspect associated options
        for field_name, FieldClass, args, kwargs in cls.DYNAMIC_FIELDS:
            assert not hasattr(
                cls, field_name
            ), "%s should not define a field called %s!  GeneralPlacedModel will handle this." % (
                name,
                field_name,
            )

            FIELD_NAME = field_name.upper()
            for opt_name, attr in cls.DYNAMIC_OPTIONS.items():
                attr = attr % FIELD_NAME
                default_value = getattr(GeneralPlacedModel, attr)
                kwargs[opt_name] = attrs.get(attr, default_value)
            attrs[field_name] = FieldClass(*args, **kwargs)

        return super_new(cls, name, bases, attrs)


class GeneralPlacedModel(six.with_metaclass(GeneralPlacedModelType, PlacedModel)):
    """Non-specific address locations, such as communities, subdivisions, cities, etc"""

    # The NULLABLE options are used with caution; legacy models sometimes used False, so these
    # settings help us maintain those db column definitions without side effects.
    # One day these should be removed and all PlacedModel subclasses should be uniformly defined.
    # If GeneralPlacedModelType can be removed in the future, these fields can be defined properly
    # (as per AddressedPlacedModel) up in the basic "PlacedModel".
    CITY_IS_NULLABLE = True
    COUNTY_IS_NULLABLE = True

    cross_roads = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_CROSS_ROADS,
        help_text=strings.PLACEDMODEL_HELP_TEXT_CROSS_ROADS,
    )
    is_multi_family = models.BooleanField(
        default=False,
        verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_MULTI_FAMILY,
        help_text=strings.PLACE_HELP_TEXT_MULTI_FAMILY,
    )

    class Meta:
        abstract = True

    @classmethod
    def DENORMALIZED_PLACE_FIELDS(cls):
        """Transitional property to allow automatic nomination of applicable Place fields."""
        fields = super(GeneralPlacedModel, cls).DENORMALIZED_PLACE_FIELDS()
        fields.extend(["city", "county", "is_multi_family", "cross_roads"])
        return fields


class AddressedPlacedModel(PlacedModel):
    """Geocoded model that has a street address."""

    street_line1 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=strings.HOME_VERBOSE_NAME_STREET_LINE1,
        help_text=strings.HOME_HELP_TEXT_STREET_LINE1,
    )
    street_line2 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=strings.HOME_VERBOSE_NAME_STREET_LINE2,
        help_text=strings.HOME_HELP_TEXT_STREET_LINE2,
    )
    zipcode = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name=strings.HOME_VERBOSE_NAME_ZIPCODE,
        help_text=strings.HOME_HELP_TEXT_ZIPCODE,
    )

    # These get defined separately here because of the special handling via metaclass that
    # GeneralPlaceModel requires.  If GeneralPlacedModelType can be removed in the future, these
    # fields can be put up in the basic "PlacedModel" fields.
    city = models.ForeignKey(
        "geographic.City",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=strings.HOME_VERBOSE_NAME_CITY,
        help_text=strings.HOME_HELP_TEXT_CITY,
    )

    class Meta:
        abstract = True

    @classmethod
    def DENORMALIZED_PLACE_FIELDS(cls):
        """Transitional property to allow automatic nomination of applicable Place fields."""
        fields = super(AddressedPlacedModel, cls).DENORMALIZED_PLACE_FIELDS()
        fields.extend(["street_line1", "street_line2", "zipcode", "city"])
        return fields


class LotAddressedPlacedModel(AddressedPlacedModel):
    """Locations described by specific street address, as opposed to cross-roads."""

    lot_number = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=strings.HOME_VERBOSE_NAME_LOT_NUMBER,
        help_text=strings.HOME_HELP_TEXT_LOT_NUMBER,
    )
    county = models.ForeignKey(
        "geographic.County",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_COUNTY,
    )
    is_multi_family = models.BooleanField(
        default=False,
        verbose_name=strings.PLACEDMODEL_VERBOSE_NAME_MULTI_FAMILY,
        help_text=strings.PLACE_HELP_TEXT_MULTI_FAMILY,
    )

    class Meta:
        abstract = True

    @classmethod
    def DENORMALIZED_PLACE_FIELDS(cls):
        """Transitional property to allow automatic nomination of applicable Place fields."""
        fields = super(LotAddressedPlacedModel, cls).DENORMALIZED_PLACE_FIELDS()
        fields.extend(["lot_number", "is_multi_family"])
        return fields
