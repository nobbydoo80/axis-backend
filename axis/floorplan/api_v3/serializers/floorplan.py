__author__ = "Artem Hruzd"
__date__ = "08/27/2020 22:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import datetime

from rest_framework import serializers
from django.core.exceptions import ValidationError

from axis.company.api_v3.serializers import CompanyInfoSerializer
from axis.floorplan.models import Floorplan
from simulation.serializers.rem.blg import get_blg_simulation_from_floorplan
from simulation.serializers.rem.blg import SimulationSerializer as SimulationBLGSerializer
from .simulation import SimulationSerializer, SimulationFlatSerializer


class FloorplanSerializerMixin(metaclass=serializers.SerializerMetaclass):
    owner_info = CompanyInfoSerializer(read_only=True, source="owner")
    simulation_info = SimulationSerializer(read_only=True, source="simulation")
    homes_count = serializers.IntegerField(read_only=True)


class FloorplanInfoSerializer(FloorplanSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Floorplan
        fields = (
            "id",
            "name",
            "number",
            "square_footage",
            "is_custom_home",
            "owner",
            "owner_info",
            "type",
            "is_active",
            "slug",
            "modified_date",
            "created_date",
        )


class FloorplanMeta:
    """
    Base Meta model for Floorplan with common fields
    """

    model = Floorplan
    fields = (
        "id",
        "name",
        "number",
        "square_footage",
        "is_custom_home",
        "comment",
        "owner",
        "owner_info",
        "type",
        "remrate_data_file",
        "simulation",
        "simulation_info",
        "homes_count",
        # Misc
        "is_active",
        "slug",
        "modified_date",
        "created_date",
        "is_restricted",
    )
    read_only_fields = ("slug", "modified_date", "owner", "created_date")


class BasicFloorplanSerializer(FloorplanSerializerMixin, serializers.ModelSerializer):
    """Basic control of Floorplan instance."""

    class Meta(FloorplanMeta):
        read_only_fields = FloorplanMeta.read_only_fields + ("is_active",)


class FloorplanSerializer(FloorplanSerializerMixin, serializers.ModelSerializer):
    """Allows full control of Floorplan instance."""

    class Meta(FloorplanMeta):
        pass

    def create(self, validated_data):
        try:
            instance = Floorplan.objects.create(**validated_data)
        except ValidationError as error:
            raise serializers.ValidationError({"non_field_errors": [error.message]})

        return instance

    def update(self, instance, validated_data):
        if instance.is_restricted:
            errors = []
            for key in ["name", "number", "remrate_target", "simulation", "ekotrope_houseplan"]:
                if getattr(instance, key) != validated_data.get(key):
                    errors.append(key)
            if errors:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            f"Floorplan is restricted - unable to edit fields {', '.join(errors)}"
                        ]
                    }
                )

        for field, value in validated_data.items():
            setattr(instance, field, value)

        try:
            instance.save()
        except ValidationError as error:
            raise serializers.ValidationError({"non_field_errors": [error.message]})

        return instance


class FloorplanFlatListSerializer(serializers.ModelSerializer):
    """Flat, only needed data from floorplan and simulation"""

    homes_count = serializers.IntegerField(read_only=True)
    simulation_info = SimulationFlatSerializer(read_only=True, source="simulation")

    class Meta:
        model = Floorplan
        fields = (
            "id",
            "name",
            "homes_count",
            "remrate_target",
            "ekotrope_houseplan",
            "simulation_info",
            "created_date",
        )


class FloorplanFromBlgSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        """
        :param validated_data:
        :return: Floorplan with BLG Simulation
        """
        floorplan = Floorplan.objects.create(**validated_data)
        simulation = get_blg_simulation_from_floorplan(floorplan)
        floorplan.simulation = simulation
        floorplan.save()

        return floorplan

    def update(self, instance, validated_data):
        raise NotImplementedError

    def validate(self, attrs):
        blg_data = attrs["file"].read().decode("iso-8859-1")
        serializer = SimulationBLGSerializer(data=blg_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        number = data["project"]["source_extra"].get("rating_number") or str(datetime.date.today())
        attrs = {
            "owner": self.context["request"].user.company,
            "name": data["name"],
            "number": number,
            "square_footage": data["conditioned_area"],
            "remrate_data_file": attrs["file"],
            "type": Floorplan.INPUT_DATA_TYPE_BLG_DATA,
        }

        if Floorplan.objects.filter(
            owner=attrs["owner"], name=attrs["name"], number=number
        ).exists():
            raise ValidationError(
                {
                    "floorplan": f"Floorplan with name {attrs['name']!r} and {attrs['number']!r} already exists!"
                }
            )

        return attrs
