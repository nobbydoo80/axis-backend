"""managers.py: Django floorplan"""


import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.urls import reverse

from axis.core.validators import represents_integer
from axis.relationship.utils import create_or_update_spanning_relationships
from .strings import (
    FLOORPLAN_MISSING_REM_DATA,
    MISSING_FLOORPLAN,
    MULTIPLE_FLOORPLAN_FOUND,
    UNKNOWN_FLOORPLAN,
    FLOORPLAN_USED_CREATE,
    FLOORPLAN_HERS_SCORE_TOO_HIGH,
    FLOORPLAN_HERS_SCORE_TOO_LOW,
    FLOORPLAN_MISSING_REM_FILE,
    FLOORPLAN_CREATE_MISSING_REMRATE,
    FOUND_FLOORPLAN,
)
from simulation.enumerations import Location, CrawlspaceType, FuelType, WaterHeaterStyle

__author__ = "Steven Klass"
__date__ = "3/11/12 7:32 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SystemTypeManager(models.Manager):
    """A Manager for System Types"""

    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company
        :param company: Company Object
        :param kwargs: kwargs
        """
        return self.filter(Q(company=company) | Q(is_public=True), **kwargs)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user
        :param user: User Object
        :param kwargs: kwargs
        """
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class SystemManager(models.Manager):
    """A Manager for Systems"""

    pass


class FloorplanQuerySet(QuerySet):
    def filter_by_company(self, company, ids_only=False, **kwargs):
        """A way to trim down the list of objects by company
        :param company: Company Object
        :param kwargs: kwargs
        """

        show_attached = kwargs.pop("show_attached", False)

        if company is None:
            return self.none()

        floorplan_ids = list(
            company.relationships.get_floorplans(show_attached=show_attached)
            .filter(**kwargs)
            .exclude(name="", number="")
            .values_list("id", flat=True)
        )

        from axis.home.models import EEPProgramHomeStatus

        Associations = EEPProgramHomeStatus.associations.rel.related_model
        associations = Associations.objects.filter(company=company, is_active=True, is_hidden=False)
        floorplan_ids.extend(
            associations.values_list("eepprogramhomestatus__floorplans", flat=True)
        )

        if ids_only:
            return floorplan_ids

        return self.filter(id__in=floorplan_ids)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user
        :param user: User Object
        :param kwargs: kwargs
        """
        show_attached = kwargs.pop("show_attached", False)
        if user.is_superuser:
            return self.filter(**kwargs)
        kwargs["show_attached"] = show_attached
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_for_uniqueness(
        self,
        name: str,
        owner: models.Model,
        remrate_target: models.Model | None = None,
        ekotrope_houseplan: models.Model | None = None,
        simulation: models.Model | None = None,
        id: int | None = None,
    ) -> QuerySet:
        existing_floorplan = self.filter(
            Q(name=name, remrate_target=remrate_target)
            | Q(name=name, ekotrope_houseplan=ekotrope_houseplan)
            | Q(name=name, simulation=simulation),
            owner=owner,
        )
        if id:
            existing_floorplan = existing_floorplan.exclude(id=id)
        return existing_floorplan

    def filter_by_user_and_subdivision(self, user, subdivision):
        """Show attached needs to be listed here b/c there is currently no real way to attach to
        a floorplan"""

        return (
            self.filter_by_user(user=user, show_attached=True)
            .filter(Q(homestatuses__home__subdivision=subdivision) | Q(subdivision=subdivision))
            .distinct()
        )

    def filter_by_company_and_subdivision(self, company, subdivision, include=None):
        """A way to trim down the list of floorplans to a company and subdivison
        :param include:
        :param subdivision:
        :param company:
        """

        # You should not have to worry about customer status here.
        # The user had to select an Program when they created the
        # floorplan and they could only choose Programs based on thier
        # company status (ie sponsored or full )
        if include is None:
            include = []

        return (
            self.filter_by_company(company=company, show_attached=True)
            .filter(
                (
                    Q(homestatuses__home__subdivision=subdivision)
                    | Q(subdivision=subdivision)
                    | Q(id__in=include)
                )
            )
            .distinct()
        )

    def filter_by_company_and_home(self, company, home, eep_program=None):
        """Filter a floorplan by home, company and Program
        :param eep_program: Program Object
        :param home: Home Object
        :param company: Company Object
        """

        homestatuses = home.homestatuses.all()
        if eep_program:
            homestatuses = homestatuses.filter(eep_program=eep_program)
        if homestatuses.exists():
            floorplan_ids = list(homestatuses.values_list("floorplan__id", flat=True))
            return self.filter(id__in=floorplan_ids)
        return self.filter_by_company_and_subdivision(company, home.subdivision)

    def get_or_create_by_simulation(self, simulation, subdivision=None):
        is_custom_home = True if subdivision is None else False
        return self.get_or_create(
            is_custom_home=is_custom_home, **simulation.get_floorplan_data_dict()
        )

    # flake8: noqa: C901
    def verify_and_create_for_company(
        self,
        name=None,
        company=None,
        subdivision=None,
        builder=None,
        eep_program=None,
        simulation=None,
        ignore_missing=False,
        warn_on_missing_model_file=False,
        create=False,
        certification_date=None,
        user=None,
        return_eep=False,
        log=None,
    ):
        """Simply verify that a floorplan is in there relationships"""

        from axis.company.models import COMPANY_MODELS
        from axis.subdivision.models import Subdivision
        from axis.eep_program.models import EEPProgram
        from axis.remrate_data.models import Simulation

        log = log if log else logging.getLogger(__name__)

        assert isinstance(company, COMPANY_MODELS), "Company must be a Company Type"
        assert isinstance(
            builder, tuple([type(None)] + list(COMPANY_MODELS))
        ), "If specified Builder must be a Company Type"
        assert isinstance(
            subdivision, (type(None), Subdivision)
        ), "If specified subdivision must of type Subdivision"
        assert isinstance(
            eep_program, (type(None), EEPProgram)
        ), "If specified eep_program must of type EEPProgram"
        assert isinstance(
            simulation, (type(None), Simulation)
        ), "If specified simulation must of type Simulation"

        if isinstance(name, str):
            name = name.strip()

        objects, floorplan = [], None
        if name is None and simulation is None:
            if ignore_missing:
                if return_eep:
                    return None, eep_program
                return None
            log.error(MISSING_FLOORPLAN)
            if return_eep:
                return None, eep_program
            return None

        base_objects = self.filter_by_company(company=company)

        msg = ""
        if name:
            msg += " with name or number '{}'".format(name)
            objects = base_objects.filter(Q(name__iexact=str(name)) | Q(number__iexact=str(name)))
            base_objects = objects

        if simulation:
            objects = base_objects.filter(remrate_target=simulation)
            if objects.count():
                msg += " with REM/Rate® '{}'".format(simulation)
                base_objects = objects

        if subdivision:
            floorplans_in_subdivision = base_objects.filter(subdivision=subdivision)
            if floorplans_in_subdivision:
                base_objects = floorplans_in_subdivision
                if builder and not base_objects.filter(subdivision__builder_org=builder).exists():
                    log.warning(
                        "Floorplans with name '{}' not in use in subdivision with a builder '{}'".format(
                            name, builder
                        )
                    )

                msg += " with Subdivision '{}' defined ".format(subdivision)
            else:
                sub_url = "<a href='{}' target='_blank'>{}</a>".format(
                    subdivision.get_absolute_url(), subdivision
                )
                msg += " in Subdivision '{}' defined ".format(sub_url)
        else:
            base_objects = base_objects.filter(subdivision__isnull=True)

        if (
            represents_integer(name)
            and self.filter_by_company(company=company).count() == base_objects.count()
        ):
            try:
                base_objects = self.filter_by_company(company).filter(id=int(name))
            except ObjectDoesNotExist:
                pass

        objects = base_objects
        if objects.count() != 1:
            if ignore_missing:
                # Give a warning if they provided a name but it wasn't found.
                msg += " was ignored because program does not require floorplan"
                if name and objects.count() > 1:
                    _val = ", ".join(
                        [
                            "<a href='{}' TARGET='_blank'>{}</a>".format(x.get_absolute_url(), x)
                            for x in objects
                        ]
                    )
                    log.warning(
                        MULTIPLE_FLOORPLAN_FOUND.format(qty=objects.count(), links=_val, msg=msg)
                    )
                elif name:
                    log.warning(UNKNOWN_FLOORPLAN.format(msg=msg))
            else:
                if objects.count() > 1:
                    _val = ", ".join(
                        [
                            "<a href='{}' TARGET='_blank'>{}</a>".format(x.get_absolute_url(), x)
                            for x in objects
                        ]
                    )
                    log.error(
                        MULTIPLE_FLOORPLAN_FOUND.format(qty=objects.count(), links=_val, msg=msg)
                    )
                else:
                    log.error(UNKNOWN_FLOORPLAN.format(msg=msg))
            if not objects.count() and create:
                if simulation:
                    floorplan, create = self.get_or_create_by_simulation(
                        simulation=simulation, subdivision=subdivision
                    )
                    log.info(
                        FLOORPLAN_USED_CREATE.format(
                            create="Created" if create else "Used existing",
                            floorplan=floorplan,
                            url=floorplan.get_absolute_url(),
                        )
                    )
                    if create:
                        create_or_update_spanning_relationships(company, floorplan)
                else:
                    log.error(FLOORPLAN_CREATE_MISSING_REMRATE)
        else:
            floorplan = objects[0]
            log.debug(FOUND_FLOORPLAN.format(url=floorplan.get_absolute_url(), floorplan=floorplan))

        if not floorplan:
            if return_eep:
                return None, eep_program
            return None

        if floorplan and eep_program:
            from axis.eep_program.models import EEPProgram

            hers = None
            try:
                hers = floorplan.get_hers_score_for_program(eep_program)
            except (AttributeError, ObjectDoesNotExist):
                if eep_program.require_rem_data:
                    log.warning(
                        FLOORPLAN_MISSING_REM_DATA.format(
                            program=eep_program,
                            url=floorplan.get_absolute_url(),
                            floorplan=floorplan,
                        )
                    )

            aps_eeps = EEPProgram.objects.filter_for_APS(user=user)
            if eep_program not in aps_eeps:  # This is handled automatically.
                program_url = reverse("eep_program:view", kwargs={"pk": eep_program.id})
                if (
                    hers
                    and eep_program.max_hers_score
                    and float(hers) > float(eep_program.max_hers_score)
                ):
                    log.warning(
                        FLOORPLAN_HERS_SCORE_TOO_HIGH.format(
                            hers=hers,
                            max_hers=eep_program.max_hers_score,
                            program=eep_program,
                            url=program_url,
                        )
                    )

                if (
                    hers
                    and eep_program.min_hers_score
                    and float(hers) < float(eep_program.min_hers_score)
                ):
                    log.warning(
                        FLOORPLAN_HERS_SCORE_TOO_LOW.format(
                            hers=hers,
                            max_hers=eep_program.min_hers_score,
                            program=eep_program,
                            url=program_url,
                        )
                    )
            else:
                from axis.customer_aps.aps_calculator import APSInputException
                from axis.customer_aps.aps_calculator.calculator import APSCalculator

                try:
                    APSCalculator(floorplan=floorplan, electric_utility="aps", us_state="AZ")
                except APSInputException as issues:
                    log.warning(issues)

            if eep_program.require_model_file:
                if floorplan and not floorplan.remrate_data_file:
                    if warn_on_missing_model_file:
                        log.warning(
                            FLOORPLAN_MISSING_REM_FILE.format(
                                program=eep_program,
                                url=floorplan.get_absolute_url(),
                                floorplan=floorplan,
                                msg="  You will need this prior to certification.",
                            )
                        )
                    else:
                        log.error(
                            FLOORPLAN_MISSING_REM_FILE.format(
                                program=eep_program,
                                url=floorplan.get_absolute_url(),
                                floorplan=floorplan,
                                msg="",
                            )
                        )
        if return_eep:
            return floorplan, eep_program
        return floorplan

    def verify_for_company(self, **kwargs):
        kwargs["create"] = False
        return self.verify_and_create_for_company(**kwargs)

    def find_unique_floorplan_name(self, name, company):
        """
        Checks the database for 'name' uniqueness.  Adds ``_N`` numerical suffix until it finds a
        unique name.
        """
        check_name = name
        counter = 1
        while True:
            try:
                self.get(name=check_name, owner=company)
            except self.model.DoesNotExist:
                break
            except self.model.MultipleObjectsReturned:
                check_name = "{}_{}".format(
                    name, self.filter(name__startswith="{}_".format(name), owner=company).count()
                )
            else:
                check_name = "{}_{}".format(name, counter)
                counter += 1

        return check_name

    def filter_by_basement(self, with_basement: bool = True):
        locations = [
            Location.UNCONDITIONED_BASEMENT,
            Location.CONDITIONED_BASEMENT,
            Location.UNCONDITIONED_INSULATED_BASEMENT,
            Location.BASEMENT_UNINSULATED,
            Location.BASEMENT_INSULATED_WALLS,
            Location.BASEMENT_INSULATED_CEILING,
        ]
        if with_basement:
            return self.filter(Q(simulation__foundation_walls__interior_location__in=locations))
        return self.filter(~Q(simulation__foundation_walls__interior_location__in=locations))

    def filter_by_attic_type(self, attic_type: str = None):
        if attic_type == "vented":
            return self.filter(simulation__roofs__interior_location=Location.ATTIC_VENTED)
        elif attic_type == "unvented":
            return self.filter(
                ~Q(simulation__roofs__interior_location=Location.VAULTED_ROOF)
                & ~Q(simulation__roofs__interior_location=Location.ATTIC_VENTED)
            )
        else:
            return self.filter(simulation__roofs__interior_location=Location.VAULTED_ROOF)

    def filter_vaulted_ceilings(self, vaulted: bool = True):
        if vaulted:
            return self.filter(Q(simulation__roofs__interior_location=Location.VAULTED_ROOF))
        return self.filter(~Q(simulation__roofs__interior_location=Location.VAULTED_ROOF))

    def filter_by_num_stories(self, value: int = 1):
        if value < 3:
            return self.filter(simulation__floors_on_or_above_grade=value)
        return self.filter(simulation__floors_on_or_above_grade__gte=value)

    def filter_by_crawl_space(self, value):
        def _filter_by_foundation_location(location: Location) -> QuerySet:
            return self.filter(
                Q(simulation__foundation_walls__interior_location=location)
                | Q(simulation__frame_floors__exterior_location=location)
            )

        if value == CrawlspaceType.VENTED:
            return _filter_by_foundation_location(Location.OPEN_CRAWL_SPACE)
        elif value == CrawlspaceType.UNVENTED:
            return _filter_by_foundation_location(Location.CONDITIONED_CRAWL_SPACE)
        else:
            return self.exclude(
                Q(simulation__foundation_walls__interior_location__in=Location.crawlspace())
                | Q(simulation__frame_floors__exterior_location__in=Location.crawlspace())
            )

    def filter_by_water_heater_fuel_and_style(self, value: str):
        """
        Filter floorplans by water heater fuel type and style.
        """

        filter_dict = {
            "electric_tankless": {"fuel": FuelType.ELECTRIC, "style": WaterHeaterStyle.TANKLESS},
            "electric_conventional": {
                "fuel": FuelType.ELECTRIC,
                "style": WaterHeaterStyle.CONVENTIONAL,
            },
            "gas_tankless": {"fuel": FuelType.NATURAL_GAS, "style": WaterHeaterStyle.TANKLESS},
            "gas_conventional": {
                "fuel": FuelType.NATURAL_GAS,
                "style": WaterHeaterStyle.CONVENTIONAL,
            },
        }

        if value not in filter_dict.keys():
            return self

        return self.filter(
            simulation__mechanical_equipment__water_heater__fuel=filter_dict[value]["fuel"],
            simulation__mechanical_equipment__water_heater__style=filter_dict[value]["style"],
        )
