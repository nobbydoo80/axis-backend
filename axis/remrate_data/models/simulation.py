"""RemRate Models suitable for use by Axis """


import datetime
import hashlib
import logging
import operator
from collections import namedtuple

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.urls import reverse
from simple_history.models import HistoricalRecords

from ..managers import SimulationManager
from ..strings import EXPORT_TYPES

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

SIMULATION_EXPORT_PAIRS = (
    (3, 2),
    (5, 4),
    (6, 7),
    (8, 9),
    (10, 11),
    (12, 13),
    (14, 15),
    (16, 17),
    (18, 19),
    (20, 21),
    (22, 23),
    (24, 25),
    (26, 27),
    (28, 29),
    (30, 31),
    (32, 33),
    (34, 35),
    (36, 37),
    (38, 39),
    (40, 41),
    (42, 43),
    (44, 45),
    (46, 47),
    (48, 49),
    (50, 51),
    (52, 53),
)

REFERENCE_MODELS = [x[0] for x in SIMULATION_EXPORT_PAIRS]
DESIGN_MODELS = [x[1] for x in SIMULATION_EXPORT_PAIRS]


class Simulation(models.Model):
    """The Simulation Table"""

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE, blank=True, null=True)
    remrate_user = models.ForeignKey(
        "remrate.RemRateUser", blank=True, null=True, on_delete=models.SET_NULL
    )
    _source_result_number = models.IntegerField(db_column="lBldgRunNo")
    simulation_date = models.DateTimeField(
        max_length=93,
        db_column="sBRDate",
        default=datetime.datetime(1900, 1, 1, 0, 0).replace(tzinfo=datetime.timezone.utc),
        null=True,
    )
    version = models.CharField(max_length=120, db_column="sBRProgVer", blank=True, null=True)
    flavor = models.CharField(max_length=255, db_column="SBRProgFlvr", blank=True)
    rating_number = models.CharField(max_length=93, db_column="sBRRateNo", blank=True, null=True)
    building_run_flag = models.CharField(max_length=90, db_column="sBRFlag", blank=True, null=True)
    export_type = models.IntegerField(db_column="lBRExpTpe", choices=EXPORT_TYPES, default=0)
    number_of_runs = models.IntegerField(
        null=True,
        db_column="nInstance",
        blank=True,
    )

    udrh_filename = models.CharField(max_length=255, db_column="sBRUdrName", blank=True, null=True)
    udrh_checksum = models.CharField(max_length=255, db_column="sBRUdrChk", blank=True, null=True)

    references = models.ManyToManyField("self", symmetrical=False, related_name="base_building")
    similar = models.ManyToManyField("self")

    objects = SimulationManager()
    history = HistoricalRecords()  # This is only here to track deletions.

    class Meta:
        verbose_name = "REM/Rate Data Set"

    @property
    def building_name(self):
        """Returns the building name"""
        return self.building.project.name

    @property
    def axis_id(self):
        """Returns the zero'd out ID"""
        return "{:06}".format(self.id)

    def __str__(self):
        return self.as_string()

    def as_string(self):
        """Returns a label b/c we used __str__ in a serializer before"""
        if self.rating_number:
            rating_number = self.rating_number
        elif hasattr(self, "building") and self.building:
            rating_number = self.building
        else:
            rating_number = "Unknown"

        version = " (v{})".format(self.version) if self.version else ""

        exp_type = ""
        if self.export_type and self.export_type != 1:
            exp_type = " [{}]".format(self.get_export_type_display())

        simulation_date = self.simulation_date.strftime("%m/%d/%Y") if self.simulation_date else ""
        return "{} {}{}{}".format(rating_number, simulation_date, version, exp_type)

    def get_full_name(self):
        """Returns the full name"""
        name = []
        if self.building.project.name not in [None, ""]:
            name.append(self.building.project.name)
        if self.building.project.builder_model not in [None, ""]:
            if self.building.project.builder_model not in name:
                name.append(self.building.project.builder_model)
        if self.rating_number not in [None, ""]:
            name.append(self.rating_number)
        return ", ".join(name)

    def get_absolute_url(self):
        """Return the url for this model"""
        return reverse("floorplan:input:remrate", kwargs={"pk": self.pk})

    def can_be_deleted(self, user):
        """Can we delete this"""
        if user.is_superuser:
            return True
        try:
            payments = self.floorplan.homestatuses.filter(
                Q(incentivepaymentstatus__isnull=True)
                | ~Q(
                    incentivepaymentstatus__state__in=["start", "ipp_payment_failed_requirements"]
                ),
                certification_date__isnull=False,
            )
            if payments.count():
                return False
        except (AttributeError, ObjectDoesNotExist):
            pass

        if user.is_company_admin and user.company == self.company:
            return True
        return False

    def can_be_edited(self, **_unused):  # pylint: disable=no-self-use
        """Can never be edited"""
        return False

    def get_total_duct_leakage(self):
        """Get the total duct leakage for a simulation"""
        values = {}
        for duct in self.ductsystem_set.all():
            label = "{} {}".format(duct.get_leakage_unit_display(), duct.get_leakage_type_display())
            if label not in values.keys():
                values[label] = 0
            values[label] += duct.total_leakage
        values = sorted(
            [(k, v) for k, v in values.items()], key=operator.itemgetter(1), reverse=True
        )
        return ["{:.2f} {}".format(val[1], val[0]) for val in values if val[1] > 0]

    def get_floorplan_data_dict(self):
        """Get me a dictionary of the data to be used to automatically create the floorplan"""
        return {
            "name": self.building_name,
            "number": self.axis_id,
            "owner": self.company,
            "square_footage": self.buildinginfo.conditioned_area,
            "remrate_target": self,
        }

    def get_installed_equipment(self, pretty=False):
        """Return a nice list of all installed equipment - TODO: Deprecate me."""
        val = []
        for inst_eqip in self.installedequipment_set.order_by("system_type", "qty_installed"):
            inst_eqip.equipment = inst_eqip.get_equipment()
            val.append(inst_eqip)
        if not pretty:
            return val
        final = []
        for obj in val:
            data = {
                "system_type_name": obj.get_system_type_display(),
                "quantity": obj.qty_installed,
                "fuel_type_name": obj.equipment.get_fuel_type_display(),
                "type_name": None,
                "output_capacity": None,
                "efficiency": None,
                "efficiency_unit": None,
                "tank_size": None,
                "energy_factor": None,
            }
            if hasattr(obj.equipment, "get_type_display"):
                data["type_name"] = obj.equipment.get_type_display()

            if hasattr(obj.equipment, "output_capacity"):
                data["output_capacity"] = obj.equipment.output_capacity

            if hasattr(obj.equipment, "efficiency"):
                data["efficiency"] = obj.equipment.efficiency

            if hasattr(obj.equipment, "efficiency_unit"):
                data["efficiency_unit"] = obj.equipment.get_efficiency_unit_display()

            if hasattr(obj.equipment, "tank_size"):
                data["tank_size"] = obj.equipment.tank_size

            if hasattr(obj.equipment, "energy_factor"):
                data["energy_factor"] = obj.equipment.energy_factor
            final.append(data)
        return final

    def photovoltaics(self):
        """Gets a list of PV stuff"""
        return self.photovoltaic_set.filter(area__gt=0)

    def _get_similar(self):
        """Return all similar homes"""
        if not hasattr(self, "building") or self.building is None:
            log.warning("Skipping %s based on missing building data", self)
            return Simulation.objects.none()
        if not hasattr(self.building, "building_info") or self.building.building_info is None:
            log.warning("Skipping %s based on missing building info data", self)
            return Simulation.objects.none()
        # One week window on either side..
        start_date = self.building.created_on - datetime.timedelta(days=7)
        end_date = self.building.created_on + datetime.timedelta(days=7)
        return Simulation.objects.filter(
            company=self.company,
            remrate_user=self.remrate_user,
            rating_number=self.rating_number,
            building__created_on__gte=start_date,
            building__building_info__volume=self.building.building_info.volume,
            building__building_info__conditioned_area=self.building.building_info.conditioned_area,
            building__building_info__type=self.building.building_info.type,
            building__building_info__house_level_type=self.building.building_info.house_level_type,
            building__building_info__number_stories=self.building.building_info.number_stories,
            building__building_info__foundation_type=self.building.building_info.foundation_type,
            building__building_info__number_bedrooms=self.building.building_info.number_bedrooms,
            building__building_info__num_units=self.building.building_info.num_units,
            building__building_info__year_built=self.building.building_info.year_built,
            building__building_info__thermal_boundary=self.building.building_info.thermal_boundary,
        ).filter(building__created_on__lte=end_date)

    def assign_references_and_similar(
        self, dry_run=False, clear_existing=False, only_affect_self=False
    ):
        """Bi-directionally assign references and similar homes.

        Any "reference" home will get bound to the default simulation (export type = 1)
        Any "design" home will only get bound to the pairing reference

        """
        objects = self._meta.model.objects.filter_similar(self, include_self=True)
        # log.debug("Object IDs:  %r", objects.values_list('pk', flat=True))
        _reference, _similar = [], []
        for obj in objects:
            reportable = obj.pk == self.pk

            if only_affect_self and obj.pk != self.pk:
                continue

            if clear_existing:
                obj.references.clear()
                obj.similar.clear()

            for sim in obj._meta.model.objects.filter_similar(obj, include_self=False):
                if sim.pk != obj.pk:
                    if reportable:
                        # log.debug("    - SIMILAR %s %s", obj.pk, sim.pk)
                        _similar.append(sim.pk)
                    # else:
                    #     log.debug("    - SIMILAR %s %s", obj.pk, sim.pk)
                    if not dry_run:
                        # log.debug("      ADDED")
                        obj.similar.add(sim)

            for ref in obj._meta.model.objects.filter_references(obj):
                if reportable:
                    # log.debug("    - REF %s %s", obj.pk, ref.pk)
                    _reference.append(ref.pk)
                # else:
                #     log.debug("    - REF %s %s", obj.pk, ref.pk)
                if not dry_run:
                    # log.debug("      ADDED")
                    obj.references.add(ref)

        if _reference or _similar:
            if not dry_run:
                return "Assigned {} references and {} similar models to {}".format(
                    len(_reference), len(_similar), self
                )
            return _similar, _reference
        if not dry_run:
            return None
        return _similar, _reference

    def compare_to_home_status(self, home_status, **kwargs):  # noqa: MC0001
        """Compare simulation to a home status"""
        dates = [home_status.modified_date]

        try:
            home_status.floorplan.modified_date.strftime("%d-%b-%Y %H:%M:%S")
            dates.append(home_status.floorplan.modified_date)
        except AttributeError:
            return {"success": [], "warning": [], "error": []}

        try:
            dates.append(home_status.home.answer_set.order_by("modified_date").last().modified_date)
        except AttributeError:
            pass

        try:
            dates.append(
                home_status.collectedinput_set.order_by("date_modified").last().date_modified
            )
        except AttributeError:
            pass

        last_modified = max(dates).strftime("%d-%b-%Y %H:%M:%S")

        if home_status.eep_program.owner.slug == "eto":
            from axis.customer_eto.utils import (
                get_remdata_compare_fields,
                get_eto_remdata_compare_fields,
            )

            if home_status.eep_program.slug in ["eto", "eto-2017", "eto-2018"]:
                kwargs.update(get_remdata_compare_fields(home_status))
            else:
                kwargs.update(get_eto_remdata_compare_fields(home_status))

        kwargs_hash = hashlib.sha1("{}".format(kwargs).encode("utf-8")).hexdigest()

        cache_key = hashlib.sha1(
            "blg_data_{}_{}_{}_{}".format(
                home_status.id, home_status.floorplan.id, last_modified, kwargs_hash
            ).encode("utf-8")
        ).hexdigest()

        issues = cache.get(cache_key, {})
        if issues:
            return issues

        issues = {"success": [], "warning": [], "error": []}
        try:
            _issues = self.building.project.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        try:
            _issues = self.site.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        try:
            _issues = self.building.building_info.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        try:
            _issues = self.window_set.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        try:
            _issues = self.skylight_set.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        try:
            _issues = self.lightsandappliance.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        try:
            _issues = self.installedequipment_set.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        try:
            _issues = self.infiltration.compare_to_home_status(home_status, **kwargs)
            for k, v in _issues.items():
                issues[k] += v
        except ObjectDoesNotExist:
            pass

        _issues = self.generalmechanicalequipment_set.compare_to_home_status(home_status, **kwargs)
        for k, v in _issues.items():
            issues[k] += v

        _issues = self.utilityrate_set.compare_to_home_status(home_status, **kwargs)
        for k, v in _issues.items():
            issues[k] += v

        total = issues["success"] + issues["warning"] + issues["error"]
        log.info(
            "BLG Data - Total: %s Success: %s Warnings: %s, Errors: %s",
            len(total),
            len(issues["success"]),
            len(issues["warning"]),
            len(issues["error"]),
        )

        cache.set(cache_key, issues, 60 * 30)
        return issues

    # noinspection PyPep8Naming
    def overall_enclosure_UA(self):  # pylint: disable=invalid-name
        """Determined via the following formula:
        UA = AG Floor (Uo*A) + Ceiling ( Uo*A) + AG Wall (Uo*A) + Window (Uo*A) + Door (Uo*A)
        """
        return (
            self.framefloor_set.get_total_u_value() * self.framefloor_set.get_total_area()
            + self.roof_set.get_total_u_value() * self.roof_set.get_total_area()
            + self.abovegradewall_set.get_total_u_value() * self.abovegradewall_set.get_total_area()
            + self.window_set.get_total_u_value() * self.window_set.get_total_area()
            + self.door_set.get_total_u_value() * self.door_set.get_total_area()
        )

    @property
    def numerical_version(self):
        """Provide a numerical version"""
        Version = namedtuple("Version", ["major", "minor", "sub"])  # pylint: disable=invalid-name
        major, minor, sub = 0, 0, 0
        if self.version:
            data = str(self.version).split(".")
            if data:
                major = int(data[0])
            if len(data) > 1:
                minor = int(data[1])
            if len(data) > 2:
                try:
                    sub = int(data[2])
                except ValueError:
                    sub = data[2]
        return Version(major, minor, sub)

    def get_possible_front_orientations(self, only_primary=True):
        """Return the possible orientations for this building"""
        max_orientation_combinations = 8
        # If it's an end unit orientation can only be on one of three sides:
        if self.building.building_info.type in [2, 4, 7]:
            max_orientation_combinations = 6

        # if it's an inside unit orientation only has two directions.
        if self.building.building_info.type in [3, 5]:
            max_orientation_combinations = 4

        # Window Orientations - This is where we get our orientations from..
        window_orientations = set()
        for window in self.window_set.order_by("pk"):
            if window.orientation:
                window_orientations.add(window.get_orientation_display().lower())
                # If we are an inside unit we can add the opposite window..
                if self.building.building_info.type in [2, 4, 7]:
                    opposites = dict(
                        [
                            (1, "North"),
                            (7, "Northeast"),
                            (8, "East"),
                            (9, "Southeast"),
                            (5, "South"),
                            (4, "Southwest"),
                            (3, "West"),
                            (2, "Northwest"),
                        ]
                    )
                    window_orientations.add(opposites.get(window.orientation).lower())

        full_orientations = ["north", "south", "east", "west"]
        half_orientations = ["northeast", "southeast", "southwest", "northwest"]
        if not set(half_orientations).intersection(window_orientations):
            max_orientation_combinations /= 2

        if len(window_orientations) == max_orientation_combinations:
            if only_primary:
                return [x for x in list(window_orientations) if x in full_orientations]
            return list(window_orientations)

        if len(window_orientations) > max_orientation_combinations:
            msg = (
                "Windows have more orientations (%s) that what's logically "
                "possible %d on REM ID: %s"
            )
            log.info(msg, ", ".join(window_orientations), max_orientation_combinations, self.pk)
            if only_primary:
                return [x for x in list(window_orientations) if x in full_orientations]
            return list(window_orientations)

        # This is the tough one. We don't have enough windows to actually determine
        # which orientations are valid
        orientations = full_orientations[:]
        if set(half_orientations).intersection(window_orientations):
            orientations += half_orientations

        if only_primary:
            orientations = [x for x in orientations if x in full_orientations]

        log.debug("Orientations for %s are %s", self, ", ".join(orientations))
        return list(orientations)

    def has_conventional_natural_gas_water_heater(self):
        return self.hotwaterheater_set.filter(fuel_type=1, type=1).exists()

    def has_instant_natural_gas_water_heater(self):
        return self.hotwaterheater_set.filter(fuel_type=1, type=3).exists()

    def has_heat_pumps(self):
        try:
            return self.installedequipment_set.get_heat_pumps().exists()
        except AttributeError:
            return False

    def has_heat_pump_water_heaters(self):
        try:
            return self.hotwaterheater_set.filter(type__in=[4, 5]).exists()
        except AttributeError:
            return False

    def get_validation_errors(self):
        errors = []
        companion_sim = None
        if self.export_type in DESIGN_MODELS:
            if self.references.count() == 0:
                errors.append("Missing Reference model for %s" % self.get_export_type_display())
            elif self.references.count() > 1:
                companion_sim = self.references.last()
            else:
                companion_sim = self.references.get()

        if self.export_type in REFERENCE_MODELS:
            if self.base_building.count() == 0:
                errors.append("Missing Design model for %s" % self.get_export_type_display())
            elif self.base_building.count() > 1:
                companion_sim = self.base_building.first()
            else:
                companion_sim = self.base_building.get()

        try:
            if self.building.sync_status != 1:
                errors.append(
                    "Simulation is not sync'd yet - status %s"
                    % self.building.get_sync_status_display()
                )
        except ObjectDoesNotExist:
            errors.append("Simulation incomplete - missing building details")

        try:
            if companion_sim and companion_sim.building.sync_status != 1:
                errors.append(
                    "Associated simulation is not sync'd yet - status %s"
                    % companion_sim.building.get_sync_status_display()
                )
        except ObjectDoesNotExist:
            errors.append("Associated simulation incomplete - missing building details")

        return errors
