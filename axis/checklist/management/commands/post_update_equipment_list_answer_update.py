"""post_update_equipment_list_answer_update.py:"""

import logging

from django.core.management import BaseCommand
from django.db.models import Q

from axis.checklist.collection.methods.trc_eps.lookups import (
    FURNACE_LOOKUPS,
    HEAT_PUMP_LOOKUPS,
    WATER_HEATER_LOOKUPS,
    REFRIGERATOR_LOOKUPS,
    DISHWASHER_LOOKUPS,
    CLOTHES_WASHER_LOOKUPS,
    CLOTHES_DRYER_LOOKUPS,
    VENTILATION_BALANCED_LOOKUPS,
    VENTILATION_EXHAUST_LOOKUPS,
)
from axis.checklist.collection.methods.utils import get_csv_rows
from axis.checklist.models import CollectedInput

__author__ = "Steven Klass"
__date__ = "01/12/2021 12:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "This will update checklist answers from custom to real values after the equipment "
        "lists have been updated.  Basically it will convert `is_custom` to a real value if"
        "the equipment was added to an equipment list"
    )
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--home_id", action="store", dest="home_id", help="Home ID")
        parser.add_argument(
            "--update", action="store_true", dest="update", help="Actually do the update"
        )
        parser.add_argument(
            "--skip_analytics", action="store_false", dest="skip_analytics", help="Update analytics"
        )

    def update_furnace(self, update=False, home_ids=None):
        """Updates furnaces"""
        total = 0
        home_statuses = []
        for lookup in get_csv_rows(FURNACE_LOOKUPS)[1:]:
            try:
                brand, model, capacity, afue, eae, ecm, motor_hp, ventilation_fan_watts = lookup
            except ValueError:
                log.warning("Skipping furnace parse error %r" % lookup)
                continue
            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-furnace",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom furnace matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "ecm": ecm,
                            "afue": afue,
                            "motor_hp": motor_hp,
                            "brand_name": brand,
                            "eae_kwh_yr": eae,
                            "model_number": model,
                            "capacity_mbtuh": capacity,
                            "ventilation_fan_watts": ventilation_fan_watts,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_heat_pumps(self, update=False, home_ids=None):
        """Updates heat pumps"""

        total = 0
        home_statuses = []
        for lookup in get_csv_rows(HEAT_PUMP_LOOKUPS)[1:]:
            try:
                (
                    brand,
                    outdoor_model,
                    indoor_model,
                    capacity_17,
                    capacity_47,
                    hspf,
                    cooling_cap,
                    seer,
                    motor_hp,
                    ventilation_fan_watts,
                ) = lookup
            except ValueError:
                log.warning("Skipping heat pump parse error %r" % lookup)
                continue
            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__outdoor_model_number=outdoor_model,
                    data__input__indoor_model_number=indoor_model,
                )
                | Q(
                    data__input__brand_name__istartswith=f"{brand}; {outdoor_model}/{indoor_model};"
                ),
                data__hints__is_custom=True,
                instrument__measure="equipment-heat-pump",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom heat_pump matching %s / %s %s"
                    % (custom_collection.count(), brand, outdoor_model, indoor_model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "hspf": hspf,
                            "seer": seer,
                            "brand_name": brand,
                            "capacity_17f_kbtuh": capacity_17,
                            "capacity_47f_kbtuh": capacity_47,
                            "indoor_model_number": indoor_model,
                            "outdoor_model_number": outdoor_model,
                            "cooling_capacity_kbtuh": cooling_cap,
                            "motor_hp": motor_hp,
                            "ventilation_fan_watts": ventilation_fan_watts,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_water_heaters(self, update=False, home_ids=None):
        """Updates waterheaters"""

        total = 0
        home_statuses = []
        for lookup in get_csv_rows(WATER_HEATER_LOOKUPS)[1:]:
            try:
                brand, model, capacity, ef, uef_cce, converted_ef = lookup
            except ValueError:
                log.warning("Skipping water heater parse error %r" % lookup)
                continue
            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-water-heater",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom water_heater matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "capacity": capacity,
                            "brand_name": brand,
                            "model_number": model,
                            "energy_factor": ef,
                            "uef_cce": uef_cce,
                            "converted_ef": converted_ef,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_refrigerators(self, update=False, home_ids=None):
        """Update refrigerators"""
        total = 0
        home_statuses = []
        for lookup in get_csv_rows(REFRIGERATOR_LOOKUPS)[1:]:
            try:
                brand, model, energy = lookup
            except ValueError:
                log.warning("Skipping refrigerator parse error %r" % lookup)
                continue
            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-refrigerator",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom refrigerator matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "brand_name": brand,
                            "model_number": model,
                            "annual_energy_use_kwh_yr": energy,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_dishwashers(self, update=False, home_ids=None):
        """Update dishwashers"""
        total = 0
        home_statuses = []
        for lookup in get_csv_rows(DISHWASHER_LOOKUPS)[1:]:
            try:
                brand, model, energy = lookup
            except ValueError:
                log.warning("Skipping dishwasher parse error %r" % lookup)
                continue
            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-dishwasher",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom dishwasher matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "brand_name": brand,
                            "model_number": model,
                            "annual_energy_use_kwh_yr": energy,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_clothes_washers(self, update=False, home_ids=None):
        total = 0
        home_statuses = []
        for lookup in get_csv_rows(CLOTHES_WASHER_LOOKUPS)[1:]:
            try:
                brand, model, energy, imef, volume, electric_rate, gas_rate, annual_cost = lookup
            except ValueError:
                log.warning("Skipping washer parse error %r" % lookup)
                continue

            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-clothes-washer",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom clothes-washer matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "brand_name": brand,
                            "model_number": model,
                            "volume_cu_ft": volume,
                            "annual_energy_use_kwh_yr": energy,
                            "integrated_modified_energy_factor": imef,
                            "electric_rate": electric_rate,
                            "gas_rate": gas_rate,
                            "annual_cost": annual_cost,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_clothes_dryers(self, update=False, home_ids=None):
        total = 0
        home_statuses = []
        for lookup in get_csv_rows(CLOTHES_DRYER_LOOKUPS)[1:]:
            try:
                brand, model, energy = lookup
            except ValueError:
                log.warning("Skipping dryer parse error %r" % lookup)
                continue
            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-clothes-dryer",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom clothes-dryer matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "brand_name": brand,
                            "model_number": model,
                            "combined_energy_factor": energy,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_ventilation_balanced(self, update=False, home_ids=None):
        total = 0
        home_statuses = []
        for lookup in get_csv_rows(VENTILATION_BALANCED_LOOKUPS)[1:]:
            try:
                brand, model, air_flow, watts, asre = lookup
            except ValueError:
                log.warning("Skipping ventilation balanced parse error %r" % lookup)
                continue

            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-ventilation-balanced",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom ventilation balanced matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "asre": asre,
                            "brand_name": brand,
                            "model_number": model,
                            "net_airflow_cfm": air_flow,
                            "power_consumption_watts": watts,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def update_ventilation_exhaust(self, update=False, home_ids=None):
        total = 0
        home_statuses = []
        for lookup in get_csv_rows(VENTILATION_EXHAUST_LOOKUPS)[1:]:
            try:
                brand, model, sp, cfm, power = lookup
            except ValueError:
                log.warning("Skipping ventilation exhaust parse error %r" % lookup)
                continue

            custom_collection = CollectedInput.objects.filter(
                Q(
                    data__input__brand_name=brand,
                    data__input__model_number=model,
                )
                | Q(data__input__brand_name__istartswith=f"{brand}; {model};"),
                data__hints__is_custom=True,
                instrument__measure="equipment-ventilation-exhaust",
            )
            if home_ids:
                custom_collection = custom_collection.filter(home_id__in=home_ids)
            if custom_collection.exists():
                total += custom_collection.count()
                self.stdout.write(
                    "Found %d custom ventilation exhaust matching %s / %s"
                    % (custom_collection.count(), brand, model)
                )
                home_statuses += list(custom_collection.values_list("home_status", flat=True))
                if update:
                    basis = {
                        "input": {
                            "speed_cfm": sp,
                            "brand_name": brand,
                            "model_number": model,
                            "input_power_watts": power,
                        }
                    }
                    for item in custom_collection.all():
                        value = basis.copy()
                        if item.data.get("comment"):
                            value["comment"] = item.data.get("comment")
                        item.data = value
                        item.save()
        return list(set(home_statuses))

    def handle(self, *args, **options):
        home_statuses = []

        update = options.get("update", False)
        update_string = "Updated" if update else "Identified"

        update = options.get("update", False)

        home_ids = None
        if options.get("home_id"):
            home_ids = options.get("home_id").split(",")

        _home_status = self.update_furnace(update, home_ids=home_ids)
        self.stdout.write("%s furnaces for %d homes" % (update_string, len(_home_status)))
        home_statuses += _home_status

        _home_status = self.update_heat_pumps(update, home_ids=home_ids)
        self.stdout.write("%s heat pumps for %d homes" % (update_string, len(_home_status)))
        home_statuses += _home_status

        _home_status = self.update_water_heaters(update, home_ids=home_ids)
        self.stdout.write("%s water heaters for %d homes" % (update_string, len(_home_status)))
        home_statuses += _home_status

        _home_status = self.update_refrigerators(update, home_ids=home_ids)
        self.stdout.write("%s refrigerators for %d homes" % (update_string, len(_home_status)))
        home_statuses += _home_status

        _home_status = self.update_dishwashers(update, home_ids=home_ids)
        self.stdout.write("%s dishwashers for %d homes" % (update_string, len(_home_status)))
        home_statuses += _home_status

        _home_status = self.update_clothes_washers(update, home_ids=home_ids)
        self.stdout.write("%s washing machines for %d homes" % (update_string, len(_home_status)))
        home_statuses += _home_status

        _home_status = self.update_clothes_dryers(update, home_ids=home_ids)
        self.stdout.write("%s dryers for %d homes" % (update_string, len(_home_status)))
        home_statuses += _home_status

        _home_status = self.update_ventilation_balanced(update, home_ids=home_ids)
        self.stdout.write(
            "%s balanced ventilation for %d homes" % (update_string, len(_home_status))
        )
        home_statuses += _home_status

        _home_status = self.update_ventilation_exhaust(update, home_ids=home_ids)
        self.stdout.write(
            "%s exhaust ventilation for %d homes" % (update_string, len(_home_status))
        )
        home_statuses += _home_status

        home_statuses = set(list(home_statuses))
        self.stdout.write(
            "%d home statuses need analytics %s" % (len(home_statuses), update_string)
        )

        if not options.get("skip_analytics"):
            return

        analytic_stats = EEPProgramHomeStatus.objects.filter(
            id__in=home_statuses, eep_program__metrics__isnull=False
        ).distinct()

        ready = analytic_stats.exclude(state__in=["complete", "abandoned"]).order_by("-id")

        for home_status in ready:
            if update:
                home_status.validate_references(immediate=True, force=True)

        completed = analytic_stats.filter(state__in=["complete", "abandoned"]).order_by("-id")
        for home_status in completed:
            if update:
                home_status.validate_references(
                    immediate=True, override_complete=True, freeze_post_run=True, force=True
                )
