"""managers.py: Django remrate_data"""


import copy
import datetime
import logging
import operator
import re
from collections import namedtuple, OrderedDict, defaultdict

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from axis.remrate_data.utils import compare_sets

__author__ = "Steven Klass"
__date__ = "3/8/13 2:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

CostingBlockRateTuple = namedtuple(
    "CostingBlockRateTuple", ["min", "max_consumption", "dollars_per_unit_per_month"]
)

SIMILAR_HOME_ALIGNMENT_DAYS = 7
REFERENCE_HOME_ALIGNMENT_SECS = 45


class SimulationManager(models.Manager):
    """Program Manager for REM/Rate Builing Data"""

    def get_queryset(self):
        return SimulationQuerySet(self.model, using=self._db)

    def filter_by_company(self, *args, **kwargs):
        return self.get_queryset().filter_by_company(*args, **kwargs)

    def filter_by_user(self, *args, **kwargs):
        return self.get_queryset().filter_by_user(*args, **kwargs)

    def verify_for_company(self, *args, **kwargs):
        return self.get_queryset().verify_for_company(*args, **kwargs)

    def filter_for_ekotrope(self, *args, **kwargs):
        return self.get_queryset().filter_for_ekotrope(*args, **kwargs)

    def filter_for_electric_only(self, *args, **kwargs):
        return self.get_queryset().filter_for_fuel_type(fuel_type=4, *args, **kwargs)

    def filter_for_gas_only(self, *args, **kwargs):
        return self.get_queryset().filter_for_fuel_type(fuel_type=1, *args, **kwargs)

    def filter_similar(self, base, *args, **kwargs):
        return self.get_queryset().filter_similar(base, *args, **kwargs)

    def filter_references(self, base, *args, **kwargs):
        return self.get_queryset().filter_references(base, *args, **kwargs)


class SimulationQuerySet(QuerySet):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company
        :param company: Company object
        :param kwargs: other search terms
        """
        from axis.relationship.models import Relationship
        from .models import DESIGN_MODELS

        ignore_sync_status = kwargs.pop("ignore_sync_status", False)
        if not ignore_sync_status:
            kwargs["building__sync_status"] = 1
        if company.company_type == "rater":
            return self.filter(company=company, **kwargs)
        if company.company_type in ["provider", "eep", "builder", "qa", "utility", "general"]:
            # These folks can see stat data for not just their company but those who have
            # relationships with them who has a relationship with me..
            comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
            # Who do I have a relationship with
            rels = company.relationships.get_companies(ids_only=True)
            # The intersection of these is what matters..
            ints = set(rels).intersection(set(comps))
            if company.company_type in ["builder"]:
                from axis.home.models import Home

                home_ids = Home.objects.filter_by_company(company, show_attached=True)
                home_ids = list(home_ids.values_list("id", flat=True))
                if "export_type__in" not in kwargs and "export_type" not in kwargs:
                    kwargs["export_type__in"] = DESIGN_MODELS + [1]
                return self.filter(
                    Q(company=company) | Q(company_id__in=ints),
                    floorplan__homestatuses__home_id__in=home_ids,
                    **kwargs,
                ).distinct()
            elif company.company_type in ["utility", "general"] and not company.is_eep_sponsor:
                from axis.home.models import EEPProgramHomeStatus

                stat_ids = EEPProgramHomeStatus.objects.filter_by_company(company)
                if "export_type__in" not in kwargs and "export_type" not in kwargs:
                    kwargs["export_type__in"] = DESIGN_MODELS + [1]
                return self.filter(
                    Q(company=company) | Q(company_id__in=ints),
                    floorplan__homestatuses__id__in=stat_ids,
                    **kwargs,
                ).distinct()
            return self.filter(Q(company=company) | Q(company_id__in=ints), **kwargs)
        return self.filter(company=company, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user
        :param user: User object
        :param kwargs: other search terms
        """
        if user.is_superuser:
            _ = kwargs.pop("ignore_sync_status", None)
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def verify_for_company(self, simulation_id, company=None, log=None):
        log = log if log else logging.getLogger(__name__)
        if simulation_id is None:
            log.warning("No REM/Rate® data provided")
            return
        object = None
        try:
            objects = self.filter_by_company(company).filter(id=simulation_id)
        except ValueError:
            log.error("REM/Rate® Axis ID '%s' is not valid", simulation_id)
            return
        if not objects.count():
            log.error("REM/Rate® Axis ID '%s' does not exist", simulation_id)
        elif objects.count() > 1:
            log.error("Multiple REM/Rate® items exist with " "Axis ID of '%s'", simulation_id)
        else:
            object = objects.get()
            log.debug("Using simulation %s", object)
        return object

    def filter_for_ekotrope(self, *args, **kwargs):
        objects = self.filter(Q(version__istartswith="14") | Q(version__istartswith="15"))

        # Only look at Non NW Flavor..
        states = ["TX", "NY", "AR", "MA", "AZ", "NV"]
        objects = objects.filter(
            Q(flavor="Rate") | Q(flavor="", building__project__property_state__in=states)
        )

        # Ekotrope requires a zipcode
        # objects = objects.filter(Q(building__project__property_zip__isnull=False)|Q(floorplan__homestatuses__isnull=False))
        objects = objects.filter(floorplan__homestatuses__isnull=False)

        # It will fail if there isn't an orientation
        objects = objects.exclude(window__orientation=None)
        return objects.filter(**kwargs)

    def filter_for_fuel_type(self, fuel_type, *args, **kwargs):
        return self.filter(
            (
                Q(airconditioner__isnull=False, airconditioner__fuel_type=fuel_type)
                | Q(airconditioner__isnull=True)
            ),
            (
                Q(airsourceheatpump__isnull=False, airsourceheatpump__fuel_type=fuel_type)
                | Q(airsourceheatpump__isnull=True)
            ),
            (
                Q(
                    dualfuelheatpump__isnull=False,
                    dualfuelheatpump__fuel_type=fuel_type,
                    dualfuelheatpump__backup_fuel_type=fuel_type,
                )
                | Q(dualfuelheatpump__isnull=True)
            ),
            (Q(heater__isnull=False, heater__fuel_type=fuel_type) | Q(heater__isnull=True)),
            (
                Q(hotwaterheater__isnull=False, hotwaterheater__fuel_type=fuel_type)
                | Q(hotwaterheater__isnull=True)
            ),
            (
                Q(groundsourceheatpump__isnull=False, groundsourceheatpump__fuel_type=fuel_type)
                | Q(groundsourceheatpump__isnull=True)
            ),
            (
                Q(
                    installedlightsandappliances__isnull=False,
                    installedlightsandappliances__fuel_type=fuel_type,
                )
                | Q(installedlightsandappliances__isnull=True)
            ),
            (
                Q(
                    integratedspacewaterheater__isnull=False,
                    integratedspacewaterheater__fuel_type=fuel_type,
                )
                | Q(integratedspacewaterheater__isnull=True)
            ),
        )

    def filter_similar(
        self,
        base,
        use_date_range=True,
        start_date_filter=None,
        end_date_filter=None,
        use_simulation_date=False,
        export_type=None,
        include_self=False,
        **kwargs,
    ):
        """Returns similar simulations"""
        from .models import DESIGN_MODELS, REFERENCE_MODELS

        start_date_filter = (
            start_date_filter
            if start_date_filter is not None
            else {"days": SIMILAR_HOME_ALIGNMENT_DAYS}
        )
        end_date_filter = (
            end_date_filter
            if end_date_filter is not None
            else {"days": SIMILAR_HOME_ALIGNMENT_DAYS}
        )

        _kw = kwargs.copy()

        kwargs = dict(
            company=base.company,
            remrate_user=base.remrate_user,
            rating_number=base.rating_number,
            building__building_info__volume=base.building.building_info.volume,
            building__building_info__conditioned_area=base.building.building_info.conditioned_area,
            building__building_info__type=base.building.building_info.type,
            building__building_info__house_level_type=base.building.building_info.house_level_type,
            building__building_info__number_stories=base.building.building_info.number_stories,
            building__building_info__foundation_type=base.building.building_info.foundation_type,
            building__building_info__number_bedrooms=base.building.building_info.number_bedrooms,
            building__building_info__num_units=base.building.building_info.num_units,
            building__building_info__year_built=base.building.building_info.year_built,
            building__building_info__thermal_boundary=base.building.building_info.thermal_boundary,
        )
        kwargs.update(**_kw)

        if use_date_range:
            start_date = base.building.created_on - datetime.timedelta(**start_date_filter)
            kwargs["building__created_on__gte"] = start_date

            end_date = base.building.created_on + datetime.timedelta(**end_date_filter)
            kwargs["building__created_on__lte"] = end_date

        if use_simulation_date:
            kwargs["simulation_date"] = base.simulation_date

        if export_type is None:
            if base.export_type in REFERENCE_MODELS:
                return self.none()

            kwargs["export_type__in"] = [1] + DESIGN_MODELS
            if include_self:
                return self.filter(**kwargs).distinct()
            else:
                return self.filter(**kwargs).exclude(id=base.id).distinct()

        # Note include self doesn't make any logical sense here so it's not available.
        return self.filter(export_type=export_type, **kwargs).exclude(id=base.id).distinct()

    def filter_references(self, base, *args, **kwargs):
        """Returns similar simulations"""

        from .models import DESIGN_MODELS, SIMULATION_EXPORT_PAIRS

        if base.export_type not in DESIGN_MODELS:
            return self.none()

        kwargs = kwargs.copy()
        reference_pair = next(
            (x[0] for x in SIMULATION_EXPORT_PAIRS if x[1] == base.export_type), None
        )
        kwargs["export_type"] = reference_pair

        version = base.numerical_version
        if version.major > 15 or (version.major == 15 and version.minor >= 7):
            kwargs["use_date_range"] = False
            kwargs["use_simulation_date"] = True
        else:
            kwargs["start_date_filter"] = {"seconds": REFERENCE_HOME_ALIGNMENT_SECS}
            kwargs["end_date_filter"] = {"seconds": REFERENCE_HOME_ALIGNMENT_SECS}

        return self.filter_similar(base, *args, **kwargs)


class BuildingManager(models.Manager):
    """Program Manager for REM/Rate Builing Data"""

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company
        :param company: Company object
        :param kwargs: other search terms
        """
        from axis.relationship.models import Relationship

        kwargs["sync_status"] = 1
        if company.company_type == "rater":
            return self.filter(company=company, **kwargs)
        if company.company_type in ["provider", "eep", "builder", "qa"] or company.is_eep_sponsor:
            # These folks can see stat data for not just their company but those who have
            # relationships with them who has a relationship with me..
            comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
            # Who do I have a relationship with
            rels = company.relationships.get_companies(ids_only=True)
            # The intersection of these is what matters..
            ints = set(rels).intersection(set(comps))
            if company.company_type in ["builder"]:
                from axis.home.models import Home

                home_ids = Home.objects.filter_by_company(company, show_attached=True)
                home_ids = list(home_ids.values_list("id", flat=True))
                return self.filter(
                    Q(company=company) | Q(company_id__in=ints),
                    floorplan__homestatuses__home_id__in=home_ids,
                    **kwargs,
                ).distinct()
            return self.filter(Q(company=company) | Q(company_id__in=ints), **kwargs)
        return self.none()

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user
        :param user: User object
        :param kwargs: other search terms
        """
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class UtilityRateManager(models.Manager):
    def get_home_status_export_data(self, simulation_ids, object_map=None, default_null="-"):
        """This simply flips a query set a bit"""

        CellObject = namedtuple(
            "CellObj", ["attr", "pretty_name", "clean_method", "section", "raw_value", "value"]
        )

        from collections import OrderedDict
        from axis.remrate_data.strings import UTILITY_UNITS, FUEL_TYPES, MONTHS

        fields = [
            ("seasonalrate__start_month", "{fuel} ({unit}) Fuel Start Month"),
            ("seasonalrate__end_month", "{fuel} ({unit}) Fuel End Month"),
            ("seasonalrate__cost", "{fuel} ({unit}) Utility Fuel Service Charge"),
            ("seasonalrate__block__max_consumption", "{fuel} ({unit}) Fuel Max Consumption"),
            (
                "seasonalrate__block__dollars_per_unit_per_month",
                "{fuel} ({unit}) Utility Rate Cost",
            ),
        ]

        key_data = [
            ("simulation", ["id", "Simulation ID", None, "remrate_utility_rates", None, None])
        ]

        fuel_type_dict = dict(FUEL_TYPES)
        unit_dict = dict(UTILITY_UNITS)
        for fuel in fuel_type_dict.values():
            for field, label in fields:
                if fuel == "None":
                    continue
                fuel_field = re.sub(r" ", "_", fuel).lower()
                for unit in unit_dict.values():
                    if unit in ["kW_Htg", "kW_Clg"]:
                        continue
                    unit_field = re.sub(r" ", "_", unit).lower()
                    field_name = "utility_rate_{}_{}_{}".format(field, fuel_field, unit_field)
                    value = [
                        field_name,
                        label.format(fuel=fuel, unit=unit),
                        None,
                        "remrate_utility_rates",
                        default_null,
                        default_null,
                    ]
                    key_data.append((field_name, value))

        # for i, data in key_data:
        #     print("    '{}',   # {}".format(i, data[1]))
        #
        results, keep = OrderedDict(), ["simulation"]
        v_fields = ["simulation_id", "fuel_type", "units"] + [x[0] for x in fields]

        for result in (
            self.filter(simulation_id__in=simulation_ids)
            .select_related("seasonalrate", "seasonalrate__block")
            .values(*v_fields)
        ):
            simulation_id = result.get("simulation_id")
            if simulation_id not in results.keys():
                results[simulation_id] = OrderedDict()
            fuel_field = re.sub(r" ", "_", fuel_type_dict.get(result.get("fuel_type")).lower())
            unit_field = re.sub(r" ", "_", unit_dict.get(result.get("units")).lower())

            for key, value in key_data:
                new_value = value[:]
                if key not in results[simulation_id].keys():
                    results[simulation_id][key] = CellObject(*new_value)
                if key == "simulation":
                    new_value[-2] = new_value[-1] = simulation_id
                    if object_map:
                        new_value[-1] = next(
                            (k for k, v in object_map.items() if v == simulation_id)
                        )
                    results[simulation_id][key] = CellObject(*new_value)
                    continue
                for field, _lbl in fields:
                    if "utility_rate_{}_{}_{}".format(field, fuel_field, unit_field) == key:
                        if result.get(field, default_null):
                            # print("  ", simulation_id, field, key, result.get(field))
                            new_value[-2] = new_value[-1] = result.get(field, default_null)
                            keep.append(key)
                            if "start_month" in field or "end_month" in field:
                                new_value[-1] = new_value[-2] = dict(MONTHS).get(
                                    int(new_value[-1]), default_null
                                )
                            if "cost" in field or "dollars" in field:
                                new_value[-1] = new_value[-2] = "${:.2f}".format(
                                    float(new_value[-1])
                                )
                            if (
                                results[simulation_id][key]
                                and results[simulation_id][key][-2] not in [None, "", default_null]
                                and new_value[-2]
                                not in [None, "", default_null, results[simulation_id][key][-2]]
                            ):
                                if isinstance(results[simulation_id][key][-2], list):
                                    new_value[-2] = results[simulation_id][key][-2] + [
                                        new_value[-2]
                                    ]
                                else:
                                    new_value[-2] = [results[simulation_id][key][-2], new_value[-2]]
                                new_value[-1] = ", ".join(["{}".format(x) for x in new_value[-2]])
                            results[simulation_id][key] = CellObject(*new_value)

        final = []
        for sim in results.values():
            final.append([v for k, v in sim.items() if k in keep])

        return final

    def compare_to_home_status(self, home_status, **kwargs):
        gas_name = next(
            (
                x.lower()
                for x in self.get_queryset().filter(fuel_type=1).values_list("name", flat=True)
            ),
            "",
        )
        electric_name = next(
            (
                x.lower()
                for x in self.get_queryset().filter(fuel_type=4).values_list("name", flat=True)
            ),
            "",
        )

        match_items = []
        if kwargs.get("verify_gas_utility_name_error") is not None:
            provided_rate = kwargs.get("verify_gas_utility_name_error")[0]
            compare = [
                provided_rate.lower(),
                gas_name,
                str,
                kwargs.get("verify_gas_utility_name_error")[1],
                "error",
            ]
            match_items.append(compare)
        if kwargs.get("verify_electric_utility_name_error") is not None:
            provided_rate = kwargs.get("verify_electric_utility_name_error")[0]
            compare = [
                provided_rate.lower(),
                electric_name,
                str,
                kwargs.get("verify_electric_utility_name_error")[1],
                "error",
            ]
            match_items.append(compare)
        return compare_sets(match_items)


class CeilingTypeManager(models.Manager):
    """A manager for ceilings"""

    def filter_unvaulted_ceilings(self):
        """Get a list of all unvaulted ceilings"""
        return self.filter(style=2)

    def filter_vaulted_ceilings(self):
        """Get a list of all vaulted ceilings"""
        return self.filter(style=1)


class RoofManager(models.Manager):
    """A manager for Roofs"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_total_u_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        return (
            sum(a * u for a, u in self.get_queryset().values_list("area", "u_value"))
            / self.get_total_area()
        )

    def get_dominant_r_value(self):
        u_values = self.get_queryset().values_list("area", "u_value")
        d_area, d_uval = 0, 0
        for area, u_value in u_values:
            if area > d_area:
                d_area = area
                d_uval = u_value
        try:
            return 1.0 / d_uval
        except ZeroDivisionError:
            return None

    def get_dominant_vaulted_r_value(self):
        u_values = self.get_queryset().filter(style=1).values_list("area", "u_value")
        d_area, d_uval = 0, 0
        for area, u_value in u_values:
            if area > d_area:
                d_area = area
                d_uval = u_value
        try:
            return 1.0 / d_uval
        except ZeroDivisionError:
            return None

    def get_dominant_flat_r_value(self):
        u_values = self.get_queryset().filter(style=2).values_list("area", "u_value")
        d_area, d_uval = 0, 0
        for area, u_value in u_values:
            if area > d_area:
                d_area = area
                d_uval = u_value
        try:
            return 1.0 / d_uval
        except ZeroDivisionError:
            return None


class WindowManager(models.Manager):
    """A manager for windows"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_total_u_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        return (
            sum(a * u for a, u in self.get_queryset().values_list("area", "type__u_value"))
            / self.get_total_area()
        )

    def get_total_shgc(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        return (
            sum(a * u for a, u in self.get_queryset().values_list("area", "type__shgc"))
            / self.get_total_area()
        )

    def get_dominant_values(self):
        data = defaultdict(int)
        for window in self.get_queryset():
            u_val = window.type.u_value
            shgc = window.type.shgc
            data[(u_val, shgc)] += window.area
        try:
            (u_val, shgc), area = sorted(data.items(), key=operator.itemgetter(1))[-1]
        except IndexError:
            u_val = shgc = area = None
        return {"u_value": u_val, "solar_heat_gain_coefficient": shgc, "gross_area": area}

    def compare_to_home_status(self, home_status, **kwargs):
        values = self.get_dominant_values()
        items = [
            (values["u_value"], kwargs.get("window_u_value"), float),
            (values["solar_heat_gain_coefficient"], kwargs.get("window_shgc_value"), float),
        ]
        match_items = []
        for fields in items:
            cmp1, cmp2, _type = fields[0], fields[1], fields[2]
            if not cmp2:
                continue
            label = cmp2[2] if len(cmp2) > 2 else "Checklist"
            match_items.append((cmp1, cmp2[0], _type, "{}: {}".format(label, cmp2[1])))
        return compare_sets(match_items)


class DoorManager(models.Manager):
    """A manager for doors"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_total_u_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        return (
            sum(a * u for a, u in self.get_queryset().values_list("area", "u_value"))
            / self.get_total_area()
        )


class SkylightManager(models.Manager):
    """A manager for skylights"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_dominant_values(self):
        data = defaultdict(int)
        for window in self.get_queryset():
            u_val = window.type.u_value
            shgc = window.type.shgc
            data[(u_val, shgc)] += window.area
        try:
            (u_val, shgc), area = sorted(data.items(), key=operator.itemgetter(1))[-1]
        except IndexError:
            u_val = shgc = area = None
        return {"u_value": u_val, "solar_heat_gain_coefficient": shgc, "gross_area": area}

    def compare_to_home_status(self, home_status, **kwargs):
        values = self.get_dominant_values()
        items = [
            (values["u_value"], kwargs.get("skylights_u_value"), float),
            (values["solar_heat_gain_coefficient"], kwargs.get("skylights_shgc_value"), float),
        ]
        match_items = []
        for fields in items:
            cmp1, cmp2, _type = fields[0], fields[1], fields[2]
            if not cmp2:
                continue
            label = cmp2[2] if len(cmp2) > 2 else "Checklist"
            match_items.append((cmp1, cmp2[0], _type, "{}: {}".format(label, cmp2[1])))
        return compare_sets(match_items)


class DuctSystemManager(models.Manager):
    """A manager for skylights"""

    def get_total_supply_area(self):
        """Return the total supply area"""
        return sum(self.get_queryset().values_list("supply_area", flat=True))

    def get_total_return_area(self):
        """Return the total return area"""
        return sum(self.get_queryset().values_list("return_area", flat=True))

    def get_total_area(self):
        """Return the total supply + return area"""
        values = self.get_queryset().values_list("return_area", "supply_area")
        return sum([x[0] + x[1] for x in values])

    def get_total_supply_leakage(self):
        return sum(self.get_queryset().values_list("supply_leakage", flat=True))

    def get_total_return_leakage(self):
        return sum(self.get_queryset().values_list("return_leakage", flat=True))

    def get_total_leakage(self):
        return sum(self.get_queryset().values_list("total_leakage", flat=True))

    def has_ducted_airconditioning(self):
        return self.get_queryset().filter(cooling_equipment_number__gte=0).exists()

    def has_ducted_heating(self):
        return self.get_queryset().filter(heating_equipment_number__gte=0).exists()


class GeneralMechanicalEquipmentManager(models.Manager):
    """A manager for general mechanicals"""

    def get_programmable_thermostats(self):
        """Return the programmable thermostats"""
        return self.get_queryset().filter(setback_thermostat=True, setup_thermostat=True)

    def get_home_status_export_data(self, simulation_ids, object_map=None, default_null="-"):
        """This simply flips a query set a bit"""

        CellObject = namedtuple(
            "CellObj", ["attr", "pretty_name", "clean_method", "section", "raw_value", "value"]
        )

        from collections import OrderedDict

        results = OrderedDict()
        v_fields = [
            "simulation_id",
            "id",
            "setup_thermostat",
            "setback_thermostat",
            "heating_set_point",
            "cooling_set_point",
        ]
        for result in self.filter(simulation_id__in=simulation_ids).values(*v_fields):
            simulation_id, trans = result.get("simulation_id"), result.get("simulation_id")
            if simulation_id in results.keys():
                raise IOError("Multiple GeneralMechanicalEquipment for {}".format(simulation_id))
            if object_map:
                trans = next((k for k, v in object_map.items() if v == simulation_id))
            sim = CellObject(
                "id", "Simulation ID", None, "remrate_mechanical", simulation_id, trans
            )
            heat_set = CellObject(
                "mech_heating_set_point",
                "Heating set point (°F)",
                None,
                "remrate_mechanical",
                result.get("heating_set_point"),
                result.get("heating_set_point", default_null),
            )
            cool_set = CellObject(
                "mech_cooling_set_point",
                "Cooling set point (°F)",
                None,
                "remrate_mechanical",
                result.get("cooling_set_point"),
                result.get("cooling_set_point", default_null),
            )
            prog = result.get("setup_thermostat") and result.get("setback_thermostat")
            prog_set = CellObject(
                "mech_programmable_thermostat",
                "Programmable Thermostat",
                None,
                "remrate_mechanical",
                prog,
                "Yes" if prog else "No",
            )
            results[simulation_id] = [sim, heat_set, cool_set, prog_set]
        return results.values()

    def compare_to_home_status(self, home_status, **kwargs):
        sim_programable_thermostats = self.get_queryset().values_list(
            "setback_thermostat", "setup_thermostat"
        )
        has_programable_thermostats = all([k for j in sim_programable_thermostats for k in j])

        match_items = []
        # if kwargs.get('has_smart_thermostat') is not None:
        #     compare = (True, True, bool, kwargs.get('has_smart_thermostat')[1], "error")
        #     if kwargs.get('has_smart_thermostat')[0] and has_programable_thermostats:
        #         compare = (True, False, bool, kwargs.get('has_smart_thermostat')[1], "error")
        #     match_items.append(compare)

        return compare_sets(match_items)


class InstalledEquipmentManager(models.Manager):
    """A manager for Installed Equipment"""

    def get_queryset(self):
        return InstalledEquipmentQuerySet(self.model, using=self._db)

    def get_installed_heating_cooling_systems(self, *args, **kwargs):
        return self.get_queryset().get_installed_heating_cooling_systems(*args, **kwargs)

    def get_heat_pumps(self):
        return self.get_queryset().get_heat_pumps()

    def get_dominant_values(self, single_include_simulation_id):
        return self.get_queryset().get_dominant_values(single_include_simulation_id)

    def compare_to_home_status(self, home_status, **kwargs):
        return self.get_queryset().compare_to_home_status(home_status, **kwargs)

    def get_home_status_export_data(self, simulation_ids, object_map=None, default_null="-"):
        """This simply flips a query set a bit"""

        CellObject = namedtuple(
            "CellObj", ["attr", "pretty_name", "clean_method", "section", "raw_value", "value"]
        )

        d_types = {
            "dominant_heating": "Primary Heating",
            "dominant_cooling": "Primary Cooling",
            "dominant_hot_water": "Primary Hot Water",
        }

        d_vals = {
            "pct_of_load": "Load Served",
            "type_name_pretty": "Type",
            "units_pretty": "Efficiency units",
            "location_pretty": "Location",
            "energy_factor": "EF",
            "tank_size": "Gallons",
            "capacity": "Capacity",
            "capacity_units": "Capacity units",
            "backup_capacity": "Backup Capacity",
            "backup_capacity_units": "Backup Capacity units",
        }

        skip_keys = ["units", "location", "load_served"]

        final = []
        for simulation_id, result in (
            self.filter(simulation_id__in=simulation_ids)
            .get_dominant_values(single_include_simulation_id=True)
            .items()
        ):
            trans = simulation_id
            if object_map:
                trans = next((k for k, v in object_map.items() if v == simulation_id))
            sim_data = [
                CellObject(
                    "id", "Simulation ID", None, "remrate_dominant_values", simulation_id, trans
                )
            ]
            for d_type, data in result.items():
                for k, v in data.items():
                    if k in skip_keys:
                        continue
                    value = default_null if v is None else v
                    sim_data.append(
                        CellObject(
                            "{}_{}".format(d_type, k),
                            "{} {}".format(d_types[d_type], d_vals.get(k, k.capitalize())),
                            None,
                            "remrate_dominant_values",
                            v,
                            value,
                        )
                    )
            final.append(sim_data)
        return final

    def get_qty_heaters(self):
        return sum(
            list(
                self.filter(
                    Q(heater__isnull=False)
                    | Q(ground_source_heat_pump__isnull=False)
                    | Q(dual_fuel_heat_pump__isnull=False)
                    | Q(air_source_heat_pump__isnull=False)
                    | Q(integrated_space_water_heater__isnull=False)
                ).values_list("qty_installed", flat=True)
            )
        )

    def get_qty_hot_water_heaters(self):
        return sum(
            list(
                self.filter(hot_water_heater__isnull=False).values_list("qty_installed", flat=True)
            )
        )

    def get_summary_analytics(self):
        return self.get_queryset().get_summary_analytics()


class InstalledEquipmentQuerySet(QuerySet):
    def get_installed_heating_cooling_systems(self):
        return self.exclude(system_type__in=[3, 7])

    def get_heat_pumps(self):
        return self.filter(
            Q(air_source_heat_pump__isnull=False)
            | Q(ground_source_heat_pump__isnull=False)
            | Q(dual_fuel_heat_pump__isnull=False)
            | Q(heater__type__in=[6, 7])
        )

    def get_dominant_values(self, single_include_simulation_id=False):
        _data = OrderedDict(
            [
                (
                    "dominant_heating",
                    {
                        "type_name_pretty": "Primary Heating",
                        "load_served": 0,
                        "units": None,
                        "units_pretty": None,
                        "efficiency": None,
                        "location": None,
                        "qty": 0,
                        "type": None,
                        "fuel": None,
                        "capacity": 0,
                        "capacity_units": None,
                        "backup_capacity": None,
                        "backup_capacity_units": None,
                    },
                ),
                (
                    "dominant_cooling",
                    {
                        "type_name_pretty": "Primary Cooling",
                        "load_served": 0,
                        "units": None,
                        "units_pretty": None,
                        "efficiency": None,
                        "location": None,
                        "qty": 0,
                        "type": None,
                        "fuel": None,
                        "capacity": 0,
                        "capacity_units": None,
                    },
                ),
                (
                    "dominant_hot_water",
                    {
                        "type_name_pretty": "Primary Water Heating",
                        "load_served": 0,
                        "tank_size": None,
                        "location": None,
                        "energy_factor": None,
                        "qty": 0,
                        "type": None,
                        "fuel": None,
                    },
                ),
            ]
        )

        results = {}
        select_related = [
            "simulation",
            "heater",
            "ground_source_heat_pump",
            "dual_fuel_heat_pump",
            "air_conditioner",
            "hot_water_heater",
            "air_source_heat_pump",
            "integrated_space_water_heater",
        ]
        for equip in self.select_related(*select_related):
            if not results.get(equip.simulation_id):
                results[equip.simulation_id] = copy.deepcopy(_data)
            data = results.get(equip.simulation_id)

            if equip.system_type == 1:  # Heater
                key = "dominant_heating"
                if equip.heating_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.heating_load_served_pct
                    data[key]["efficiency"] = equip.heater.efficiency
                    data[key]["units"] = equip.heater.efficiency_unit
                    data[key]["units_pretty"] = equip.heater.get_efficiency_unit_display()
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    heater = equip.heater.get_type_display()
                    heater = heater + " heater" if equip.heater.type in [1, 2, 5] else heater
                    data[key]["type"] = heater
                    data[key]["fuel"] = equip.heater.get_fuel_type_display()
                    data[key]["capacity"] = equip.heater.output_capacity
                    data[key]["capacity_units"] = "kBtuh"
                    # data[key]['backup_capacity'] = equip.heater.auxiliary_electric
                    # data[key][
                    #     'backup_capacity_units'] = equip.heater.get_auxiliary_electric_type_display()
                    data[key]["pct_of_load"] = equip.heating_load_served_pct
            elif equip.system_type == 2:  # AC
                key = "dominant_cooling"
                if equip.air_conditioner_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.air_conditioner_load_served_pct
                    data[key]["efficiency"] = equip.air_conditioner.efficiency
                    data[key]["units"] = equip.air_conditioner.efficiency_unit
                    data[key]["units_pretty"] = equip.air_conditioner.get_efficiency_unit_display()
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = equip.air_conditioner.get_type_display()
                    data[key]["fuel"] = equip.air_conditioner.get_fuel_type_display()
                    data[key]["capacity"] = equip.air_conditioner.output_capacity
                    data[key]["capacity_units"] = "kBtuh"
                    data[key]["pct_of_load"] = equip.air_conditioner_load_served_pct
            elif equip.system_type == 3:  # DHW
                key = "dominant_hot_water"
                if equip.hot_water_heater_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.hot_water_heater_load_served_pct
                    data[key]["energy_factor"] = equip.hot_water_heater.energy_factor
                    data[key]["tank_size"] = equip.hot_water_heater.tank_size
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = equip.hot_water_heater.get_type_display()
                    data[key]["fuel"] = equip.hot_water_heater.get_fuel_type_display()
            elif equip.system_type == 4:  # ASHP
                key = "dominant_heating"
                if equip.heating_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.heating_load_served_pct
                    data[key]["efficiency"] = equip.air_source_heat_pump.heating_efficiency
                    data[key]["units"] = equip.air_source_heat_pump.heating_efficiency_units
                    data[key][
                        "units_pretty"
                    ] = equip.air_source_heat_pump.get_heating_efficiency_units_display()
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "Air-source heat pump"
                    data[key]["fuel"] = equip.air_source_heat_pump.get_fuel_type_display()
                    data[key]["capacity"] = equip.air_source_heat_pump.heating_capacity
                    data[key]["capacity_units"] = "kBtuh"
                    data[key]["backup_capacity"] = equip.air_source_heat_pump.backup_capacity
                    data[key]["backup_capacity_units"] = (
                        "kW" if equip.air_source_heat_pump.backup_capacity else None
                    )
                    data[key]["pct_of_load"] = equip.heating_load_served_pct
                key = "dominant_cooling"
                if equip.air_conditioner_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.air_conditioner_load_served_pct
                    data[key]["efficiency"] = equip.air_source_heat_pump.cooling_efficiency
                    data[key]["units"] = equip.air_source_heat_pump.cooling_efficiency_units
                    data[key][
                        "units_pretty"
                    ] = equip.air_source_heat_pump.get_cooling_efficiency_units_display()
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "Air-source heat pump"
                    data[key]["fuel"] = equip.air_source_heat_pump.get_fuel_type_display()
                    data[key]["capacity"] = equip.air_source_heat_pump.cooling_capacity
                    data[key]["pct_of_load"] = equip.air_conditioner_load_served_pct
            elif equip.system_type == 5:  # GSHP
                key = "dominant_heating"
                if equip.heating_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.heating_load_served_pct
                    data[key][
                        "efficiency"
                    ] = equip.ground_source_heat_pump.heating_coefficient_of_performance_32f
                    data[key]["units"] = 4  # COP
                    data[key]["units_pretty"] = "COP"
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "{} {} Ground-source heat pump".format(
                        equip.ground_source_heat_pump.get_type_display(),
                        equip.ground_source_heat_pump.get_distribution_type_display(),
                    )
                    data[key]["fuel"] = equip.ground_source_heat_pump.get_fuel_type_display()
                    data[key]["capacity"] = equip.ground_source_heat_pump.heating_capacity_50f
                    data[key]["capacity_units"] = "kBtuh"
                    data[key]["backup_capacity"] = equip.ground_source_heat_pump.backup_capacity
                    data[key]["backup_capacity_units"] = (
                        "kW" if equip.ground_source_heat_pump.backup_capacity else None
                    )
                    data[key]["pct_of_load"] = equip.heating_load_served_pct
                key = "dominant_cooling"
                if equip.air_conditioner_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.air_conditioner_load_served_pct
                    data[key][
                        "efficiency"
                    ] = equip.ground_source_heat_pump.cooling_energy_efficiency_ratio_77f
                    data[key]["units"] = 2
                    data[key]["units_pretty"] = "EER"  # EER
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "{} {} Ground-source heat pump".format(
                        equip.ground_source_heat_pump.get_type_display(),
                        equip.ground_source_heat_pump.get_distribution_type_display(),
                    )
                    data[key]["fuel"] = equip.ground_source_heat_pump.get_fuel_type_display()
                    data[key]["capacity"] = equip.ground_source_heat_pump.cooling_capacity_50f
                    data[key]["pct_of_load"] = equip.air_conditioner_load_served_pct
            elif equip.system_type == 6:  # DFHP
                key = "dominant_heating"
                if equip.heating_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.heating_load_served_pct
                    data[key][
                        "efficiency"
                    ] = equip.dual_fuel_heat_pump.backup_heating_seasonal_efficiency
                    data[key]["units"] = 3
                    data[key]["units_pretty"] = "HSPF"
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "Dual Fuel heat Pump"
                    data[key]["fuel"] = equip.dual_fuel_heat_pump.get_fuel_type_display()
                    data[key]["capacity"] = equip.dual_fuel_heat_pump.heating_capacity
                    data[key]["capacity_units"] = "kBtuh"
                    data[key]["backup_capacity"] = equip.dual_fuel_heat_pump.backup_heating_capacity
                    data[key][
                        "backup_capacity_units"
                    ] = equip.dual_fuel_heat_pump.get_backup_heating_efficiency_units_display()
                    data[key]["pct_of_load"] = equip.heating_load_served_pct
                key = "dominant_cooling"
                if equip.air_conditioner_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.air_conditioner_load_served_pct
                    data[key]["efficiency"] = equip.dual_fuel_heat_pump.cooling_capacity
                    data[key]["units"] = 1
                    data[key]["units_pretty"] = "SEER"  #
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "Dual Fuel heat Pump"
                    data[key]["fuel"] = equip.dual_fuel_heat_pump.get_fuel_type_display()
                    data[key]["capacity"] = equip.dual_fuel_heat_pump.cooling_capacity
                    data[key]["pct_of_load"] = equip.air_conditioner_load_served_pct
            elif equip.system_type == 7:  # ISWH
                key = "dominant_heating"
                if equip.heating_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.heating_load_served_pct
                    data[key][
                        "efficiency"
                    ] = equip.integrated_space_water_heater.space_heating_efficiency
                    data[key]["units"] = 99  # ??
                    data[key]["units_pretty"] = "CAafue"
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "Integrated Space Water Heater"
                    data[key]["fuel"] = equip.integrated_space_water_heater.get_fuel_type_display()
                    data[key]["capacity"] = equip.integrated_space_water_heater.output_capacity
                    data[key]["pct_of_load"] = equip.heating_load_served_pct
                key = "dominant_hot_water"
                if equip.hot_water_heater_load_served_pct > data[key].get("load_served"):
                    data[key]["load_served"] = equip.hot_water_heater_load_served_pct
                    data[key][
                        "energy_factor"
                    ] = equip.integrated_space_water_heater.water_heating_energy_factor
                    data[key]["tank_size"] = equip.integrated_space_water_heater.tank_size
                    data[key]["location"] = equip.location
                    data[key]["location_pretty"] = equip.get_location_display()
                    data[key]["qty"] += equip.qty_installed
                    data[key]["type"] = "Integrated Space Water Heater"
                    data[key]["fuel"] = equip.integrated_space_water_heater.get_fuel_type_display()

        if len(results.keys()) == 1 and single_include_simulation_id is False:
            return results[list(results.keys())[0]]
        return results

    def get_summary_analytics(self):
        equipment_values = {"heating": [], "hot_water": [], "cooling": []}

        for equip in self.filter():
            heating, cooling, hot_water = None, None, None
            if equip.system_type == 1:  # Heater
                heating = {
                    "type": {
                        "label": "Space Heater Type",
                        "value": equip.heater.get_type_display(),
                    },
                    "fuel": {
                        "label": "Space Heater Fuel",
                        "value": equip.heater.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "Space Heater Capacity",
                        "value": equip.heater.output_capacity,
                    },
                    "efficiency": {
                        "label": "Space Heater Efficiency",
                        "value": "%s %s"
                        % (equip.heater.efficiency, equip.heater.get_efficiency_unit_display()),
                    },
                    "location": {
                        "label": "Space Heater Location",
                        "value": equip.get_location_display(),
                    },
                    "pct_of_load": {"label": "% of load", "value": equip.heating_load_served_pct},
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
            elif equip.system_type == 2:  # AC
                cooling = {
                    "type": {
                        "label": "A/C Type",
                        "value": equip.air_conditioner.get_type_display(),
                    },
                    "fuel": {
                        "label": "A/C Fuel",
                        "value": equip.air_conditioner.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "A/C Capacity",
                        "value": equip.air_conditioner.output_capacity,
                    },
                    "efficiency": {
                        "label": "A/C Efficiency",
                        "value": "%s %s"
                        % (
                            equip.air_conditioner.efficiency,
                            equip.air_conditioner.get_efficiency_unit_display(),
                        ),
                    },
                    "location": {"label": "A/C Location", "value": equip.get_location_display()},
                    "pct_of_load": {
                        "label": "%s of load",
                        "value": equip.air_conditioner_load_served_pct,
                    },
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
            elif equip.system_type == 3:  # DHW
                hot_water = {
                    "type": {
                        "label": "Hot Water Type",
                        "value": equip.hot_water_heater.get_type_display(),
                    },
                    "fuel": {
                        "label": "Hot Water Fuel",
                        "value": equip.hot_water_heater.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "Hot Water Capacity",
                        "value": equip.hot_water_heater.tank_size,
                    },
                    "energy_factor": {
                        "label": "Hot Water Energy Factor",
                        "value": equip.hot_water_heater.energy_factor,
                    },
                    "extra_tank_insulation_r_value": {
                        "label": "Hot Water Tank Insulation",
                        "value": equip.hot_water_heater.extra_tank_insulation_r_value,
                    },
                    "location": {
                        "label": "Hot Water Location",
                        "value": equip.get_location_display(),
                    },
                    "pct_of_load": {
                        "label": "% of load",
                        "value": equip.hot_water_heater_load_served_pct,
                    },
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
            elif equip.system_type == 4:  # ASHP
                heating = {
                    "type": {"label": "Type", "value": "Air Source Heat Pump"},
                    "fuel": {
                        "label": "ASHP Fuel",
                        "value": equip.air_source_heat_pump.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "ASHP Heating Capacity",
                        "value": equip.air_source_heat_pump.heating_capacity,
                    },
                    "efficiency": {
                        "label": "ASHP Heater Efficiency",
                        "value": "%s %s"
                        % (
                            equip.air_source_heat_pump.heating_efficiency,
                            equip.air_source_heat_pump.get_heating_efficiency_units_display(),
                        ),
                    },
                    "location": {"label": "ASHP Location", "value": equip.get_location_display()},
                    "pct_of_load": {"label": "% of load", "value": equip.heating_load_served_pct},
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
                cooling = {
                    "type": {"label": "Type", "value": "Air Source Heat Pump"},
                    "fuel": {
                        "label": "ASHP Fuel",
                        "value": equip.air_source_heat_pump.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "ASHP Cooling Capacity",
                        "value": equip.air_source_heat_pump.cooling_capacity,
                    },
                    "efficiency": {
                        "label": "ASHP Cooling Efficiency",
                        "value": "%s %s"
                        % (
                            equip.air_source_heat_pump.cooling_efficiency,
                            equip.air_source_heat_pump.get_cooling_efficiency_units_display(),
                        ),
                    },
                    "location": {"label": "ASHP Location", "value": equip.get_location_display()},
                    "pct_of_load": {
                        "label": "% of load",
                        "value": equip.air_conditioner_load_served_pct,
                    },
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
            elif equip.system_type == 5:  # GSHP
                _type = "{} {} Ground-source heat pump".format(
                    equip.ground_source_heat_pump.get_type_display(),
                    equip.ground_source_heat_pump.get_distribution_type_display(),
                )
                heating = {
                    "type": {"label": "Type", "value": _type},
                    "fuel": {
                        "label": "GSHP Fuel",
                        "value": equip.ground_source_heat_pump.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "GSHP Heating Capacity",
                        "value": equip.ground_source_heat_pump.heating_capacity_50f,
                    },
                    "efficiency": {
                        "label": "GSHP Heater Efficiency",
                        "value": "%s %s"
                        % (
                            equip.ground_source_heat_pump.heating_coefficient_of_performance_32f,
                            "COP",
                        ),
                    },
                    "location": {"label": "GSHP Location", "value": equip.get_location_display()},
                    "pct_of_load": {"label": "% of load", "value": equip.heating_load_served_pct},
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
                cooling = {
                    "type": {"label": "Type", "value": _type},
                    "fuel": {
                        "label": "GSHP Fuel",
                        "value": equip.ground_source_heat_pump.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "GSHP Cooling Capacity",
                        "value": equip.ground_source_heat_pump.cooling_capacity_50f,
                    },
                    "efficiency": {
                        "label": "GSHP Cooling Efficiency",
                        "value": "%s %s"
                        % (
                            equip.ground_source_heat_pump.cooling_energy_efficiency_ratio_77f,
                            "EER",
                        ),
                    },
                    "location": {"label": "GSHP Location", "value": equip.get_location_display()},
                    "pct_of_load": {
                        "label": "% of load",
                        "value": equip.air_conditioner_load_served_pct,
                    },
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
            elif equip.system_type == 6:  # DFHP
                heating = {
                    "type": {"label": "Type", "value": "Dual Fuel heat Pump"},
                    "fuel": {
                        "label": "DFHP Fuel",
                        "value": equip.dual_fuel_heat_pump.get_fuel_type_display(),
                    },
                    "backup_fuel_type": {
                        "label": "DFHP Backup Fuel",
                        "value": equip.dual_fuel_heat_pump.get_backup_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "DFHP Heating Capacity",
                        "value": equip.dual_fuel_heat_pump.heating_capacity,
                    },
                    "efficiency": {
                        "label": "DFHP Heater Efficiency",
                        "value": "%s %s"
                        % (equip.dual_fuel_heat_pump.backup_heating_seasonal_efficiency, "HSPF"),
                    },
                    "location": {"label": "DFHP Location", "value": equip.get_location_display()},
                    "pct_of_load": {"label": "% of load", "value": equip.heating_load_served_pct},
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
                cooling = {
                    "type": {"label": "Type", "value": "Dual Fuel heat Pump"},
                    "fuel": {
                        "label": "DFHP Fuel",
                        "value": equip.dual_fuel_heat_pump.get_fuel_type_display(),
                    },
                    "capacity": {
                        "label": "DFHP Cooling Capacity",
                        "value": equip.dual_fuel_heat_pump.cooling_capacity,
                    },
                    "location": {"label": "DFHP Location", "value": equip.get_location_display()},
                    "pct_of_load": {
                        "label": "% of load",
                        "value": equip.air_conditioner_load_served_pct,
                    },
                    "qty": {"label": "Number of Units", "value": equip.qty_installed},
                }
            if heating:
                equipment_values["heating"].append(heating)
            if cooling:
                equipment_values["cooling"].append(cooling)
            if hot_water:
                equipment_values["hot_water"].append(hot_water)

        return equipment_values

    def compare_to_home_status(self, home_status, **kwargs):
        values = self.get_dominant_values()
        items = []

        if values.get("dominant_cooling", {}).get("qty"):
            items += [
                (
                    values.get("dominant_cooling", {}).get("units"),
                    kwargs.get("air_conditioner_units"),
                    int,
                ),
                (
                    values.get("dominant_cooling", {}).get("efficiency"),
                    kwargs.get("air_conditioner_seer"),
                    float,
                ),
            ]
        if values.get("dominant_heating", {}).get("units") == 1:  # AFUE
            items.append(
                (
                    values.get("dominant_heating", {}).get("efficiency"),
                    kwargs.get("primary_heat_afue"),
                    float,
                )
            )
        elif values.get("dominant_heating", {}).get("units") == 3:  # HSPF
            items.append(
                (
                    values.get("dominant_heating").get("efficiency"),
                    kwargs.get("primary_heat_hspf"),
                    float,
                )
            )
        elif values.get("dominant_heating", {}).get("units") == 4:  # COP
            items.append(
                (
                    values.get("dominant_heating", {}).get("efficiency"),
                    kwargs.get("primary_heat_cop"),
                    float,
                )
            )
        items += [
            (
                values.get("dominant_heating", {}).get("pretty_location"),
                kwargs.get("primary_heat_location"),
                str,
            ),
            (
                values.get("dominant_hot_water", {}).get("tank_size"),
                kwargs.get("water_heater_gallons"),
                float,
            ),
            (
                values.get("dominant_hot_water", {}).get("energy_factor"),
                kwargs.get("water_heater_ef"),
                float,
            ),
            (
                values.get("dominant_hot_water", {}).get("pretty_location"),
                kwargs.get("water_heater_location"),
                str,
            ),
        ]
        match_items = []
        for fields in items:
            cmp1, cmp2, _type = fields[0], fields[1], fields[2]
            if not cmp2:
                continue
            label = cmp2[2] if len(cmp2) > 2 else "Checklist"
            match_items.append((cmp1, cmp2[0], _type, "{}: {}".format(label, cmp2[1])))
        return compare_sets(match_items)


class InfiltrationManager(models.Manager):
    """A manager for Infiiltration"""

    def get_ventilation_systems(self):
        """Return Ventilation Systems"""
        objects = []
        for item in self.get_queryset().filter(mechanical_vent_type__gt=0):
            objects.append(
                "{}: {} cfm {} watts".format(
                    item.get_mechanical_vent_type_display(),
                    round(item.mechanical_vent_cfm, 0),
                    round(item.mechanical_vent_power, 0),
                )
            )
        return objects


class BlockManager(models.Manager):
    """A manager for Costing Block Rates"""

    def as_table(self):
        """Return the queryset as a nice table.  Need this cause it only stores he max not min.."""
        return (
            "<table><thead><tr><th>Min</th><th>Max</th><th>Rate</th></tr></thead>" "{rows}</table"
        ).format(row=self.get_table_rows())

    def get_table_rows(self):
        """
        Returns only the rows as generated by ``as_table``.  This is more flexible for the bootstrap
        site.
        """
        output = []
        for data in self.get_data_lists:
            output.append("<tr><td>{:,}</td><td>{:,}</td><td>${:,}</td></tr>".format(data))
        return "".join(output)

    def get_data_lists(self):
        min = 0
        data = []
        for item in self.all():
            data.append(
                CostingBlockRateTuple(min, item.max_consumption, item.dollars_per_unit_per_month)
            )
            min = item.max_consumption
        return data

    def get_first_fuel_rate_dict(self):
        from axis.remrate_data.strings import FUEL_TYPES, UTILITY_UNITS

        data = {}
        vals = [
            "dollars_per_unit_per_month",
            "seasonal_rate__rate__fuel_type",
            "seasonal_rate__rate__units",
            "max_consumption",
        ]
        for cost, fuel, units, max_consumption in self.all().values_list(*vals):
            fuel_type = dict(FUEL_TYPES).get(fuel)
            units = dict(UTILITY_UNITS).get(units)
            if fuel_type not in data:
                data[fuel_type] = (max_consumption, cost, units)
            if max_consumption < data[fuel_type][0]:
                data[fuel_type] = (max_consumption, cost, units)
        return {k: (cost, units) for k, (_c, cost, units) in data.items()}


class FuelSummaryManager(models.Manager):
    """A manager for skylights"""

    def get_fuel_summary(self):
        """Return the values used for fuel summary costing"""
        return self.get_queryset().filter(fuel_units__in=list(range(0, 6)))

    def get_fuel_consumption(self):
        """Return Fuel Consumption"""
        costs = dict(heating=0, cooling=0, water_heating=0, lights_and_appliances=0)
        for item in self.get_queryset():
            costs["heating"] += item.heating_consumption
            costs["cooling"] += item.cooling_consumption
            costs["water_heating"] += item.hot_water_consumption
            costs["lights_and_appliances"] += item.lights_and_appliances_consumption
        return costs

    def get_winter_fuel_demands(self):
        """Return winter fuel demands"""
        return self.get_queryset().filter(fuel_units=7)

    def get_summer_fuel_demands(self):
        """Return summer fuel demands"""
        return self.get_queryset().filter(fuel_units=8)

    def get_home_status_export_data(self, simulation_ids, object_map=None, default_null="-"):
        """This simply flips a query set a bit"""

        CellObject = namedtuple(
            "CellObj", ["attr", "pretty_name", "clean_method", "section", "raw_value", "value"]
        )

        from collections import OrderedDict
        from .strings import UTILITY_UNITS, FUEL_TYPES

        fields = [
            ("heating_consumption", "Annual estimated {fuel_type} Heating consumption ({unit})"),
            ("cooling_consumption", "Annual estimated {fuel_type} Cooling consumption ({unit})"),
            (
                "hot_water_consumption",
                "Annual estimated {fuel_type} Hot Water consumption ({unit})",
            ),
            (
                "lights_and_appliances_consumption",
                "Annual estimated {fuel_type} Lights and Appliance consumption ({unit})",
            ),
            (
                "photo_voltaics_consumption",
                "Annual estimated {fuel_type} Photo voltaics consumption ({unit})",
            ),
            ("total_consumption", "Annual estimated {fuel_type} Total Consumption ({unit})"),
            ("total_cost", "Annual estimated total {fuel_type} Cost"),
        ]

        key_data = [("simulation", ["id", "Simulation ID", None, "fuel_summary", None, None])]

        fuel_type_dict = dict(FUEL_TYPES)
        unit_dict = dict(UTILITY_UNITS)
        for field, label in fields:
            for fuel in fuel_type_dict.values():
                if fuel == "None":
                    continue
                fuel_field = re.sub(r" ", "_", fuel).lower()
                for unit in unit_dict.values():
                    if unit in ["kW_Htg", "kW_Clg"]:
                        continue
                    unit_field = re.sub(r" ", "_", unit).lower()
                    field_name = "{}_{}_{}".format(field, fuel_field, unit_field)
                    value = [
                        field_name,
                        label.format(fuel_type=fuel, unit=unit),
                        None,
                        "fuel_summary",
                        default_null,
                        default_null,
                    ]
                    key_data.append((field_name, value))

        results, keep = OrderedDict(), ["simulation"]
        v_fields = ["simulation_id", "fuel_type", "fuel_units"] + [x[0] for x in fields]
        for result in self.filter(
            simulation_id__in=simulation_ids, fuel_units__in=list(range(0, 6))
        ).values(*v_fields):
            simulation_id = result.get("simulation_id")
            if simulation_id not in results.keys():
                results[simulation_id] = OrderedDict()
            fuel_field = re.sub(r" ", "_", fuel_type_dict.get(result.get("fuel_type")).lower())
            unit_field = re.sub(r" ", "_", unit_dict.get(result.get("fuel_units")).lower())
            for key, value in key_data:
                new_value = value[:]
                if key not in results[simulation_id].keys():
                    results[simulation_id][key] = CellObject(*new_value)
                if key == "simulation":
                    new_value[-2] = new_value[-1] = simulation_id
                    if object_map:
                        new_value[-1] = next(
                            (k for k, v in object_map.items() if v == simulation_id)
                        )
                    results[simulation_id][key] = CellObject(*new_value)
                    continue
                for field, _lbl in fields:
                    if "{}_{}_{}".format(field, fuel_field, unit_field) == key:
                        if result.get(field, default_null):
                            # print(simulation_id, field, key, result.get(field))
                            new_value[-2] = new_value[-1] = result.get(field, default_null)
                            keep.append(key)
                            if "cost" in field:
                                new_value[-1] = "${:.2f}".format(float(new_value[-1]))
                            if (
                                results[simulation_id][key]
                                and results[simulation_id][key][-1]
                                and new_value[-1]
                                != default_null
                                not in [None, "", results[simulation_id][key][-1], default_null]
                            ):
                                raise IOError(
                                    "We have multiple values for {} {} {} {} {}".format(
                                        simulation_id,
                                        field,
                                        key,
                                        new_value[-1],
                                        results[simulation_id][key][-1],
                                    )
                                )
                            results[simulation_id][key] = CellObject(*new_value)

        final = []
        for sim in results.values():
            final.append([v for k, v in sim.items() if k in keep])

        return final


class FoundationWallManager(models.Manager):
    """A manager for foundation walls"""

    def get_total_area(self):
        """Return the total area"""
        l_w = self.get_queryset().values_list("length", "height")
        return sum([y[0] * y[1] for y in l_w])

    def get_total_area_above_grade(self):
        """Return the total area above grade"""
        l_w = self.get_queryset().values_list("length", "height", "depth_below_grade")
        return sum([x[0] * (x[1] - x[2]) for x in l_w])

    def get_total_r_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        try:
            return (
                sum(
                    (l * w) * (u + x)
                    for l, w, u, x in self.get_queryset().values_list(
                        "length",
                        "height",
                        "type__rigid_insulation_r_value",
                        "type__batt_or_blown_insulation_r_value",
                    )
                )
                / self.get_total_area()
            )
        except ZeroDivisionError:
            return 0.0

    def get_total_u_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        try:
            return 1 / self.get_total_r_value()
        except ZeroDivisionError:
            return 0.0

    def get_dominant_r_value(self):
        u_values = self.get_queryset().values_list(
            "length",
            "height",
            "type__rigid_insulation_r_value",
            "type__batt_or_blown_insulation_r_value",
        )
        d_area, d_uval = 0, 0
        for l, w, u, x in u_values:
            area = l * w
            if area > d_area:
                d_area = area
                d_uval = u + x
        try:
            return 1.0 / d_uval
        except ZeroDivisionError:
            return None


class AboveGradeWallManager(models.Manager):
    """A manager for above grade walls"""

    def get_total_area(self):
        """Return the total area - [A = ∑ Ai for i = 1, n]"""
        return sum(self.get_queryset().values_list("gross_area", flat=True))

    def get_total_u_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        return (
            sum(a * u for a, u in self.get_queryset().values_list("gross_area", "u_value"))
            / self.get_total_area()
        )

    def get_dominant_r_value(self):
        u_values = self.get_queryset().values_list("gross_area", "u_value")
        d_area, d_uval = 0, 0
        for area, u_value in u_values:
            if area > d_area:
                d_area = area
                d_uval = u_value
        try:
            return 1.0 / d_uval
        except ZeroDivisionError:
            return None

    def get_r_value_for_largest(self):
        largest = self.order_by("-gross_area").first()

        if largest is None:
            return None
        return largest.type.continuous_insulation + largest.type.cavity_insulation


class SlabManager(models.Manager):

    """A manager for slabs"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_total_r_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        return (
            sum(
                a * u
                for a, u in self.get_queryset().values_list("area", "type__under_slab_r_value")
            )
            / self.get_total_area()
        )

    def get_total_u_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        try:
            return 1 / self.get_total_r_value()
        except ZeroDivisionError:
            return 0.0

    def get_dominant_perimeter_r_value(self):
        r_values = self.get_queryset().values_list("area", "type__perimeter_r_value")
        d_area, r_uvalue = 0, 0
        for area, r_value in r_values:
            if area > d_area:
                d_area = area
                r_uvalue = r_value
        return r_uvalue

    def get_dominant_underslab_r_value(self):
        r_values = self.get_queryset().values_list("area", "type__under_slab_r_value")
        d_area, r_uvalue = 0, 0
        for area, r_value in r_values:
            if area > d_area:
                d_area = area
                r_uvalue = r_value
        return r_uvalue


class FrameFloorManager(models.Manager):
    """A manager for frame floors"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_total_u_value(self):
        """[Uo = (∑ (Ui * Ai)) / A for i = 1, n]"""
        try:
            return (
                sum(a * u for a, u in self.get_queryset().values_list("area", "u_value"))
                / self.get_total_area()
            )
        except ZeroDivisionError:
            return 0.0

    def get_dominant_r_value(self):
        u_values = self.get_queryset().values_list("area", "u_value")
        d_area, d_uval = 0, 0
        for area, u_value in u_values:
            if area > d_area:
                d_area = area
                d_uval = u_value
        try:
            return 1.0 / d_uval
        except ZeroDivisionError:
            return None

    def get_r_value_for_largest(self):
        largest = self.order_by("-area").first()

        if largest is None:
            return None
        return largest.type.continuous_insulation + largest.type.cavity_insulation


class JoistManager(models.Manager):
    """A manager for joists"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_dominant_r_value(self):
        u_values = self.get_queryset().values_list("area", "u_value")
        d_area, d_uval = 0, 0
        for area, u_value in u_values:
            if area > d_area:
                d_area = area
                d_uval = u_value
        try:
            return 1.0 / d_uval
        except ZeroDivisionError:
            return None


class DuctManager(models.Manager):
    """A manager for ducts"""

    def get_total_area(self):
        """Return the total area"""
        return sum(self.get_queryset().values_list("area", flat=True))

    def get_pct_in_conditioned_space(self):
        conditioned = self.get_queryset().filter(location__in=[3, 5, 8])
        total = self.get_queryset()

        conditioned_area = sum(conditioned.values_list("area", flat=True))
        total_area = sum(total.values_list("area", flat=True))
        try:
            return conditioned_area / total_area
        except ZeroDivisionError:
            return 0.0
