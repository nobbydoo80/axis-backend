"""similar_homes: Django Get similar Homes"""
import datetime
import logging

from django.db.models import Q, Count, IntegerField
from django.utils.timezone import now
from simulation.models import Simulation

from axis.customer_eto.models import FastTrackSubmission
from axis.home.models import EEPProgramHomeStatus

__author__ = "Steven K"
__date__ = "08/30/2019 10:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def get_similar_homes(
    home_status_id,
    simulation_id,
    simulation_square_footage,
    simulation_climate_zone_id,
    percent_improvement,
    analysis_type,
):
    """Provides the baseline of similar homes"""

    _completed_homes = EEPProgramHomeStatus.objects.filter(state="complete")
    completed_homes = set(_completed_homes.values_list("pk", flat=True))

    similar_last_eighteen_months = _completed_homes.filter(
        certification_date__gte=now() - datetime.timedelta(days=365 * 1.5)
    )
    similar_last_eighteen_months = set(similar_last_eighteen_months.values_list("pk", flat=True))

    try:
        simulation = Simulation.objects.get(id=simulation_id)
    except Simulation.DoesNotExist:
        return {
            "similar_total_simulation_ids": [],
            "similar_insulation_simulation_ids": [],
            "similar_heating_simulation_ids": [],
            "similar_hot_water_simulation_ids": [],
            "similar_total_simulation_last_18mo_ids": [],
            "similar_insulation_simulation_last_18mo_ids": [],
            "similar_heating_simulation_last_18mo_ids": [],
            "similar_hot_water_simulation_last_18mo_ids": [],
        }

    similar_percent_improvement = set()
    if percent_improvement is not None:
        low = percent_improvement - 0.05
        high = percent_improvement + 0.05
        x = FastTrackSubmission.objects.filter(
            percent_improvement__gte=low, percent_improvement__lt=high
        )
        similar_percent_improvement = set(x.values_list("home_status_id", flat=True))
        similar_percent_improvement = similar_percent_improvement.intersection(completed_homes)
    log.debug(
        "Similar ETO Only Percent Improvement home status entries: %d",
        len(list(similar_percent_improvement)),
    )

    similar_square_footages = set()
    if simulation_square_footage is not None:
        _similar = Simulation.objects.filter(simulation.get_similar_conditioned_area_queryset())
        _similar.values_list("pk", flat=True)
        x = EEPProgramHomeStatus.objects.filter(floorplan__simulation_id__in=_similar)
        similar_square_footages = set(x.values_list("pk", flat=True))
        similar_square_footages = similar_square_footages.intersection(completed_homes)
    log.debug("Similar Square Footage home status entries: %d", len(list(similar_square_footages)))

    similar_climate_zones = set()
    if simulation_climate_zone_id is not None:
        x = EEPProgramHomeStatus.objects.filter(
            floorplan__simulation__location__climate_zone_id=simulation_climate_zone_id
        )
        similar_climate_zones = set(x.values_list("pk", flat=True))
        similar_climate_zones = similar_climate_zones.intersection(completed_homes)
    log.debug("Similar Climate home status entries: %d", len(list(similar_climate_zones)))

    _similar = Simulation.objects.filter(simulation.get_similar_heated_queryset())

    total_systems = simulation.mechanical_equipment.filter(heating_percent_served__gt=0).count()
    _similar = Simulation.objects.filter(simulation.get_similar_heated_queryset()).distinct()
    _similar = (
        Simulation.objects.filter(pk__in=_similar.values_list("pk", flat=True))
        .annotate(
            total_systems=Count(
                "mechanical_equipment",
                filter=Q(mechanical_equipment__heating_percent_served__gt=0),
            )
        )
        .filter(total_systems=total_systems)
    )
    similar_heating_systems = set(
        EEPProgramHomeStatus.objects.filter(
            floorplan__simulation_id__in=_similar.values_list("pk", flat=True)
        ).values_list("pk", flat=True)
    )
    similar_heating_systems = similar_heating_systems.intersection(completed_homes)
    log.debug("Similar Heated home status entries: %d", len(list(similar_heating_systems)))

    total_systems = simulation.mechanical_equipment.filter(
        water_heater_percent_served__gt=0
    ).count()
    _similar = Simulation.objects.filter(simulation.get_similar_hot_water_queryset())
    _similar = (
        Simulation.objects.filter(pk__in=_similar.values_list("pk", flat=True))
        .annotate(
            total_systems=Count(
                "mechanical_equipment",
                filter=Q(mechanical_equipment__water_heater_percent_served__gt=0),
            )
        )
        .filter(total_systems=total_systems)
    )
    similar_hot_water_systems = set(
        EEPProgramHomeStatus.objects.filter(
            floorplan__simulation_id__in=_similar.values_list("pk", flat=True)
        ).values_list("pk", flat=True)
    )
    similar_hot_water_systems = similar_hot_water_systems.intersection(completed_homes)
    log.debug("Similar Hot Water home status entries: %d", len(list(similar_hot_water_systems)))

    _similar = Simulation.objects.filter(simulation.get_similar_fuels_queryset())
    similar_fuel_types = set(
        EEPProgramHomeStatus.objects.filter(
            floorplan__simulation_id__in=_similar.values_list("pk", flat=True)
        ).values_list("pk", flat=True)
    )
    similar_fuel_types = similar_fuel_types.intersection(completed_homes)
    log.debug("Similar Fuel homes: %d", len(list(similar_fuel_types)))

    data = {
        "similar_total_simulation_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages,
                similar_climate_zones,
                similar_fuel_types,
                similar_heating_systems,
                similar_hot_water_systems,
            )
        ),
        "similar_total_simulation_last_18mo_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages,
                similar_climate_zones,
                similar_fuel_types,
                similar_heating_systems,
                similar_hot_water_systems,
                similar_last_eighteen_months,
            )
        ),
        "similar_insulation_simulation_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages,
                similar_climate_zones,
            )
        ),
        "similar_insulation_simulation_last_18mo_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages, similar_climate_zones, similar_last_eighteen_months
            )
        ),
        "similar_heating_simulation_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages,
                similar_climate_zones,
                similar_heating_systems,
            )
        ),
        "similar_heating_simulation_last_18mo_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages,
                similar_climate_zones,
                similar_heating_systems,
                similar_last_eighteen_months,
            )
        ),
        "similar_hot_water_simulation_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages, similar_climate_zones, similar_hot_water_systems
            )
        ),
        "similar_hot_water_simulation_last_18mo_ids": list(
            set(similar_percent_improvement).intersection(
                similar_square_footages,
                similar_climate_zones,
                similar_hot_water_systems,
                similar_last_eighteen_months,
            )
        ),
    }

    result = {}
    for key, sids in data.items():
        vals = EEPProgramHomeStatus.objects.filter(id__in=sids)
        vals = vals.values_list("floorplan__simulation_id", flat=True)
        result[key] = list(set([x for x in vals if x is not None]))
        log.debug("Narrowed '%s' to %d items", key, len(result[key]))
    return result
