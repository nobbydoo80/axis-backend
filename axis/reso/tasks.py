"""tasks.py: Django reso"""


import datetime

from celery import shared_task
from celery.utils.log import get_task_logger

from django.apps import apps

from axis.reso.models import (
    ResoHome,
    ResoGreenVerification,
    INV_RESO_HEATER_CHOICES,
    INV_RESO_COOLING_CHOICES,
)

__author__ = "Steven Klass"
__date__ = "9/5/17 15:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = get_task_logger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")

PROGRAM_OWNER_SLUGS = [customer_hirl_app.CUSTOMER_SLUG, "us-epa"]


class ResoAxisLink:
    def __init__(self, home_id, *args, **kwargs):
        self.home_id = home_id
        self.issues = False
        self.override_programs = kwargs.get("override_programs", False)

        from axis.home.models import Home

        self.home = Home.objects.get(id=self.home_id)
        self.home_statuses = self.get_home_status_queryset()

        self.data = {"latest_home_status": self.home_statuses.last()}

    def get_home_status_queryset(self):
        """This identified the home statuses we can actually consider when we build up a ResoHome"""
        from axis.home.models import EEPProgramHomeStatus

        home_statuses = EEPProgramHomeStatus.objects.filter(
            home_id=self.home_id, certification_date__isnull=False, state="complete"
        )

        # Right now the only data we can use is BPA..
        if not self.override_programs:
            home_statuses = home_statuses.filter(eep_program__owner__slug__in=PROGRAM_OWNER_SLUGS)

        return home_statuses.order_by("certification_date")

    @property
    def should_transfer(self):
        """This is where we identify whether a home has data that we can share with the WORLD."""
        if self.issues is not False:
            return False if len(self.issues) else True

        self.issues = []

        if not self.home_statuses.count():
            self.issues.append(
                "No Programs have been attached to this home: [%r] %r" % (self.home_id, self.home)
            )

        if not self.override_programs:
            if not self.home_statuses.filter(
                eep_program__owner__slug__in=PROGRAM_OWNER_SLUGS
            ).count():
                self.issues.append(
                    "No valid programs available for use for home: [%r] %r"
                    % (self.home_id, self.home)
                )

        return self.should_transfer

    def set_home_data(self):
        self.data["City"] = self.home.city
        self.data["CountyOrParish"] = self.home.city.county

        if self.home.confirmed_address:
            self.data["Latitude"] = self.home.latitude
            self.data["Longitude"] = self.home.longitude

        self.data["PostalCode"] = self.home.zipcode

        self.data["AddressLine1"] = (
            self.home.street_line1.strip() if self.home.street_line1 is not None else None
        )

        if self.home.street_line2 not in ["", None]:
            self.data["AddressLine2"] = self.home.street_line2.strip()

        if self.home.county:
            self.data["StateOrProvince"] = self.home.city.county.state
        if self.home.subdivision:
            self.data["SubdivisionName"] = self.home.subdivision.name

    def set_ekotrope_data(self, simulation):
        source = 2  # Ekotrope

        houseplan = simulation.houseplan.data

        summary = houseplan.get("thermalEnvelope", {}).get("summary")
        if summary:
            self.data["AboveGradeFinishedArea"] = float(summary.get("floorArea"))
            self.data["AboveGradeFinishedAreaSource"] = source
            self.data["AboveGradeFinishedAreaUnits"] = 1  # SquareFeet

        if houseplan.get("thermalEnvelope", {}).get("foundationType"):
            from axis.ekotrope.equivalences import FOUNDATION_TYPES

            ftype = houseplan.get("thermalEnvelope", {}).get("foundationType")
            self.data["Basement"] = next((x[0] for x in FOUNDATION_TYPES if x[1] == ftype))

        if summary:
            self.data["BuildingAreaTotal"] = float(summary.get("conditionedArea"))
            self.data["BuildingAreaSource"] = source
            self.data["BuildingAreaUnits"] = 1  # SquareFeet

        self.data["Stories"] = int(houseplan.get("details", {}).get("numberOfFloorsOnOrAboveGrade"))

    def set_remrate_data(self, simulation):
        source = 1  # REM/Rate®

        above_grade_area = sum(simulation.abovegradewall_set.values_list("gross_area", flat=True))
        if above_grade_area:
            self.data["AboveGradeFinishedArea"] = above_grade_area
            self.data["AboveGradeFinishedAreaSource"] = source
            self.data["AboveGradeFinishedAreaUnits"] = 1  # SquareFeet

        self.data["Basement"] = simulation.buildinginfo.foundation_type

        self.data["BuildingAreaTotal"] = simulation.buildinginfo.conditioned_area
        self.data["BuildingAreaSource"] = source
        self.data["BuildingAreaUnits"] = 1  # SquareFeet

        self.data["Stories"] = simulation.buildinginfo.number_stories
        self.data[
            "StoriesTotal"
        ] = simulation.buildinginfo.number_stories_including_conditioned_basement

        costing = simulation.fuelsummary_set.get_home_status_export_data([simulation.id])[0]
        costing = {x.attr: x.raw_value for x in costing}

        if costing.get("total_cost_natural_gas_therms", 0) > 0:
            self.data["GasOnPropertyYN"] = True
            self.data["GasExpense"] = costing.get("total_cost_natural_gas_therms")

        if costing.get("total_cost_electric_kwh", 0) > 0:
            self.data["ElectricOnPropertyYN"] = True
            self.data["ElectricExpense"] = costing.get("total_cost_electric_kwh")

        dominant = simulation.installedequipment_set.get_dominant_values([simulation.id]).values()[
            0
        ]
        if dominant.get("dominant_heating", {}).get("qty", 0) > 0:
            self.data["HeatingYN"] = True
            value = dict(INV_RESO_HEATER_CHOICES).get(
                dominant.get("dominant_heating", {}).get("type")
            )
            self.data["Heating"] = [value]
        elif dominant.get("dominant_heating", {}).get("qty") == 0:
            self.data["HeatingYN"] = False

        if dominant.get("dominant_cooling", {}).get("qty", 0) > 0:
            self.data["CoolingYN"] = True
            value = dict(INV_RESO_COOLING_CHOICES).get(
                dominant.get("dominant_cooling", {}).get("type")
            )
            self.data["Cooling"] = [value]
        elif dominant.get("dominant_cooling", {}).get("qty") == 0:
            self.data["CoolingYN"] = False

        self.data["YearBuilt"] = simulation.buildinginfo.year_built
        self.data["YearBuiltSource"] = source

    def set_simulation_data(self, home_status):
        if not home_status.floorplan:
            return

        self.data["BuilderName"] = home_status.floorplan.name
        self.data["BuilderModel"] = home_status.floorplan.number

        if home_status.floorplan.square_footage:
            self.data["BuildingAreaTotal"] = home_status.floorplan.square_footage
            self.data["BuildingAreaSource"] = 3  # Energy Modeler
            self.data["BuildingAreaUnits"] = 1  # SquareFeet

        if (
            home_status.floorplan.input_data_type == "remrate"
            and home_status.floorplan.remrate_target
        ):
            self.set_remrate_data(home_status.floorplan.remrate_target)
        if (
            home_status.floorplan.input_data_type == "ekotrop"
            and home_status.floorplan.ekotrope_houseplan
        ):
            self.set_ekotrope_data(home_status.floorplan.ekotrope_houseplan)

    def set_ngbs_green_data(self, home_status):
        if not self.data.get("GreenBuildingVerificationType"):
            self.data["GreenBuildingVerificationType"] = []

        if not self.data.get("_GreenBuildingVerificationData"):
            self.data["_GreenBuildingVerificationData"] = []

        green_data = {
            "GreenVerificationBody": "{}".format(home_status.company),
            "GreenVerificationDate": datetime.datetime(
                home_status.certification_date.year,
                home_status.certification_date.month,
                home_status.certification_date.day,
            ).replace(tzinfo=datetime.timezone.utc),
            "GreenVerificationSource": "Program Sponsor",
            "GreenVerificationStatus": "Complete",
            "GreenVerificationURL": "https://axis.pivotalenergy.net"
            + home_status.get_absolute_url(),
            "qualifying_home_statuses": [home_status],
        }
        if "new" in home_status.eep_program.slug:
            self.data["GreenBuildingVerificationType"].append(12)
            green_data["GreenBuildingVerificationType"] = 12
        elif ">=" in home_status.eep_program.name:
            self.data["GreenBuildingVerificationType"].append(14)
            green_data["GreenBuildingVerificationType"] = 14
        else:
            self.data["GreenBuildingVerificationType"].append(13)
            green_data["GreenBuildingVerificationType"] = 13

        annotations = home_status.annotations
        try:
            green_data["GreenVerificationRating"] = annotations.get(
                type__slug="certified-nat-gbs"
            ).content
        except:
            pass

        try:
            green_data["GreenVerificationMetric"] = home_status.annotations.get(
                type__slug="certification-standard"
            ).content
        except:
            pass

        self.data["_GreenBuildingVerificationData"].append(green_data)

    def set_epa_green_data(self, home_status):
        if not self.data.get("GreenBuildingVerificationType"):
            self.data["GreenBuildingVerificationType"] = []

        if not self.data.get("_GreenBuildingVerificationData"):
            self.data["_GreenBuildingVerificationData"] = []

        green_data = {
            "GreenVerificationBody": "{}".format(home_status.company),
            "GreenVerificationDate": datetime.datetime(
                home_status.certification_date.year,
                home_status.certification_date.month,
                home_status.certification_date.day,
            ).replace(tzinfo=datetime.timezone.utc),
            "GreenVerificationSource": "Program Sponsor",
            "GreenVerificationStatus": "Complete",
            "GreenVerificationURL": "https://axis.pivotalenergy.net"
            + home_status.get_absolute_url(),
            "qualifying_home_statuses": [home_status],
        }
        if "energy-star" in home_status.eep_program.slug:
            self.data["GreenBuildingVerificationType"].append(2)
            green_data["GreenBuildingVerificationType"] = 2
        elif "indoor-airplus" in home_status.eep_program.slug:
            self.data["GreenBuildingVerificationType"].append(9)
            green_data["GreenBuildingVerificationType"] = 9
        elif "watersense" in home_status.eep_program.slug:
            self.data["GreenBuildingVerificationType"].append(16)
            green_data["GreenBuildingVerificationType"] = 16

        green_data["GreenVerificationRating"] = home_status.eep_program.name
        green_data["GreenVerificationMetric"] = None

        self.data["_GreenBuildingVerificationData"].append(green_data)

    def transfer(self):
        self.set_home_data()

        for home_status in self.home_statuses:
            self.set_simulation_data(home_status)

            if home_status.eep_program.owner.slug == customer_hirl_app.CUSTOMER_SLUG:
                self.set_ngbs_green_data(home_status)

            if home_status.eep_program.owner.slug == "us-epa":
                self.set_epa_green_data(home_status)

            self.data["latest_home_status"] = home_status

        green_verification_data = self.data.pop("_GreenBuildingVerificationData", [])

        obj, update = ResoHome.objects.update_or_create(home_id=self.home_id, defaults=self.data)

        for dataset in green_verification_data:
            qualifying_home_statuses = dataset.pop("qualifying_home_statuses", [])
            verification_type = dataset.pop("GreenBuildingVerificationType")
            gv_obj, create = ResoGreenVerification.objects.update_or_create(
                ListingKeyNumeric=obj,
                GreenBuildingVerificationType=verification_type,
                defaults=dataset,
            )

            for stat in qualifying_home_statuses:
                gv_obj.qualifying_home_statuses.add(stat)


@shared_task()
def assign_data_to_reso_models(home_id, **kwargs):
    link = ResoAxisLink(home_id, **kwargs)

    if not link.should_transfer:
        return link.issues

    return link.transfer()
