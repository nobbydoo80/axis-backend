"""Examine rest_framework serializers"""


import logging

from rest_framework import serializers
from django_input_collection.api.restframework import serializers as collection_serializers

from django.contrib.auth import get_user_model
from axis.filehandling.api import CustomerDocumentSerializer
from ... import models


__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)
User = get_user_model()


# CollectionRequest
class CollectionRequestSerializer(collection_serializers.CollectionRequestSerializer):
    """Adds homestatus and program ids to serialization."""

    Meta = collection_serializers.CollectionRequestSerializer.Meta
    Meta.queryset = Meta.model.objects.select_related("eepprogram", "eepprogramhomestatus")

    eep_program_id = serializers.SerializerMethodField()
    home_status_id = serializers.PrimaryKeyRelatedField(
        source="eepprogramhomestatus", read_only=True, allow_null=True
    )

    def get_eep_program_id(self, instance):
        """Provides the underlying program id even when a homestatus is set."""
        eep_program = getattr(instance, "eepprogram", None)
        if eep_program:
            return eep_program.id
        return instance.eepprogramhomestatus.eep_program_id


# Instrument
class InputBreakdownSerializer(serializers.Serializer):
    """
    Takes a queryset of inputs on an instrument and calls get_breakdown() on it according to the
    given ``field`` name.
    """

    def __init__(self, field, *args, **kwargs):
        super(InputBreakdownSerializer, self).__init__(*args, **kwargs)
        self.field = field

    def to_representation(self, queryset):
        """Groups inputs by initialized `field` name's unique values."""

        breakdown = queryset.get_breakdown(self.field)
        sub_serializer = InputSerializer(many=True, context=self.context)
        for value, sub_queryset in breakdown.items():
            breakdown[value] = sub_serializer.to_representation(sub_queryset)
        return breakdown


class InstrumentListSerializer(collection_serializers.CollectionInstrumentListSerializer):
    collectedinput_set = serializers.SerializerMethodField()

    def get_collectedinput_set(self, obj):
        # TODO - This is ripe for queryset minimization
        queryset = (
            self.context["collector"]
            .get_inputs(measure=obj.measure_id, cooperative_requests=True)
            .select_related("user", "instrument")
        )
        serializer = InputBreakdownSerializer("user_role", instance=queryset, context=self.context)
        return serializer.data

    def to_representation(self, data):
        # We need to bake in read_only into this data set.
        data = super(InstrumentListSerializer, self).to_representation(data)

        from axis.home.models import EEPProgramHomeStatus

        collector = self.context["collector"]

        try:
            status = EEPProgramHomeStatus.objects.get(
                collection_request_id=collector.collection_request
            )
            read_only = status.state == "complete"
        except (EEPProgramHomeStatus.DoesNotExist, AttributeError):
            read_only = False

        for item in data:
            item["read_only"] = read_only
        return data


class InstrumentSerializer(collection_serializers.CollectionInstrumentSerializer):
    """Returns collectedinput_set as a user-role breakdown."""

    class Meta(collection_serializers.CollectionInstrumentSerializer.Meta):
        """Meta Options"""

        fields = collection_serializers.CollectionInstrumentSerializer.Meta.fields + [
            "read_only",
        ]
        list_serializer_class = InstrumentListSerializer

    # Serialization override
    collectedinput_set = serializers.SerializerMethodField()

    def get_collectedinput_set(self, obj):
        queryset = self.context["collector"].get_inputs(
            measure=obj.measure_id, cooperative_requests=True
        )
        serializer = InputBreakdownSerializer("user_role", instance=queryset, context=self.context)
        return serializer.data

    # Access control hint
    read_only = serializers.SerializerMethodField()

    def get_read_only(self, obj):
        """Get read only status"""
        return False
        # collector = self.context['collector']
        # user_role = collector.get_user_role(collector.user)
        # return user_role != collector.user_role


# Input
class UserInfoSerializer(serializers.ModelSerializer):
    """User Info serializer"""

    full_name = serializers.CharField(source="get_full_name")

    class Meta:
        """Meta Options"""

        model = User
        fields = ("id", "full_name")


class InputSerializer(collection_serializers.CollectedInputSerializer):
    """Input serializer"""

    class Meta(collection_serializers.CollectedInputSerializer.Meta):
        """Meta Options"""

        include_write = collection_serializers.CollectedInputSerializer.Meta.include_write + (
            "expected_documents",
        )

    # Richer info for fields already on the serializer
    user = UserInfoSerializer(read_only=True)
    customer_documents = CustomerDocumentSerializer(many=True, read_only=True)

    expected_documents = serializers.ListField(
        child=serializers.CharField(), write_only=True, default=[]
    )


class InputInstrumentSerializer(InputSerializer):
    """Response serialization is always the parent instrument's serialization."""

    Meta = InputSerializer.Meta

    def to_representation(self, instance):
        """Dict representation"""
        collector = self.context["collector"]
        instrument = instance.instrument
        activated_instruments = collector.get_active_conditional_instruments(instrument)
        instruments = [instrument] + activated_instruments
        instrument_serializer = InstrumentSerializer(
            many=True,
            **{
                "instance": instruments,
                "context": self.context,
            },
        )
        return instrument_serializer.data

    @property
    def data(self):
        """The data - return the to representation"""
        # super() assumes the to_representation() will always be a dict because this is not a
        # ListSerializer, and will try to wrap it in a dict helper that we don't care about.
        return self.to_representation(self.instance)

    def save(self, **kwargs):
        """Save it"""
        obj = super(InputInstrumentSerializer, self).save()
        # This needs a leading debouncer.  Rapid input entry will trigger needless updates
        obj.home_status.validate_references()
        return obj
