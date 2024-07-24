__author__ = "Steven Klass"
__date__ = "3/3/12 5:37 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Artem Hruzd"]

import collections
import hashlib
import json
import logging
import os

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.urls import reverse
from simple_history.models import HistoricalRecords
from simulation.enumerations import Location, AnalysisEngine, AnalysisType, AnalysisStatus

from axis.core.fields import AxisJSONField
from axis.core.utils import randomize_filename, unrandomize_filename, get_frontend_url
from axis.core.utils import slugify_uniquely
from axis.relationship.models import Relationship
from axis.remrate.tasks import get_floorplan_blg_data
from axis.remrate_data.strings import HOME_TYPES, FOUNDATION_TYPES
from simulation.models import Analysis, Simulation
from . import strings
from .managers import FloorplanQuerySet


log = logging.getLogger(__name__)

User = get_user_model()


def content_blgfile_name(instance, filename):
    """Location of any Floorplan BLG Files
    :param filename: Filename for the supplementary document
    :param instance: Instance the logo is bound to.
    """
    filename = filename
    if not isinstance(filename, str):
        filename = filename.name
    return os.path.join(
        "documents",
        instance.owner.company_type,
        instance.owner.slug,
        "blg_files",
        randomize_filename(filename),
    )


def content_floorplan_name(instance, filename):
    """Location of any Floorplan BLG Files
    :param filename: Filename for the supplementary document
    :param instance: Instance the logo is bound to.
    """
    filename = filename
    if not isinstance(filename, str):
        filename = filename.name
    return os.path.join(
        "documents",
        instance.company.company_type,
        instance.company.slug,
        "floor_plan_docs",
        randomize_filename(filename),
    )


class Floorplan(models.Model):
    """
    This will establish everything that describes a home
    """

    RATING_TYPE_PRELIMINARY = "preliminary"
    RATING_TYPE_FINAL = "final"

    RATING_TYPE_CHOICES = [(RATING_TYPE_PRELIMINARY, "Preliminary"), (RATING_TYPE_FINAL, "Final")]

    INPUT_DATA_TYPE_REMRATE = "remrate"
    INPUT_DATA_TYPE_EKOTROPE = "ekotrope"
    INPUT_DATA_TYPE_BLG_DATA = "blg_data"

    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE)

    name = models.CharField(max_length=64, null=True, help_text=strings.FLOORPLAN_MODEL_NAME)
    number = models.CharField(max_length=64, null=True, help_text=strings.FLOORPLAN_MODEL_NUMBER)
    square_footage = models.IntegerField(
        null=True, help_text=strings.FLOORPLAN_MODEL_SQUARE_FOOTAGE
    )

    remrate_target = models.OneToOneField(
        "remrate_data.Simulation",
        unique=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="REM/Rate™ Data",
        help_text=strings.FLOORPLAN_MODEL_REM_RATE_TARGET,
    )

    remrate_data_file = models.FileField(
        upload_to=content_blgfile_name,
        blank=True,
        null=True,
        max_length=512,
        verbose_name="REM/Rate™ File",
        help_text=strings.FLOORPLAN_MODEL_REM_RATE_DATA_FILE,
    )
    ekotrope_houseplan = models.OneToOneField(
        "ekotrope.HousePlan", blank=True, null=True, on_delete=models.SET_NULL
    )

    simulation = models.OneToOneField(
        "simulation.Simulation",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Simulation Result",
    )

    component_serialization = AxisJSONField(blank=True, default=dict)
    simulation_result = AxisJSONField(blank=True, default=dict)

    customer_documents = GenericRelation("filehandling.CustomerDocument")

    type = models.CharField(
        "Rating Type",
        blank=True,
        null=True,
        max_length=20,
        default=None,
        choices=RATING_TYPE_CHOICES,
    )
    is_custom_home = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True, help_text=strings.FLOORPLAN_MODEL_COMMENT)

    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True)

    relationships = GenericRelation(Relationship)
    annotations = GenericRelation("annotation.Annotation")

    objects = FloorplanQuerySet.as_manager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Floorplan"
        ordering = ("name", "number")
        permissions = (("can_simulate", "Ability to simulate"),)

    def __str__(self):
        name = "{}".format(self.name)
        if self.type:
            name += " ({})".format(self.get_type_display())
        return name

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return get_frontend_url("floorplans", self.pk)

    def save(self, *args, **kwargs):
        if not self.slug:
            name = self.name if self.name else self.number
            self.slug = slugify_uniquely(name, self.__class__)

        if self.simulation:
            if not self.name:
                self.name = self.simulation.name
            if not self.square_footage:
                self.square_footage = self.simulation.conditioned_area

        elif self.remrate_target:
            if not self.name:
                self.name = self.remrate_target.building.project.name
            if not self.number:
                self.number = self.remrate_target.building.project.rating_number
            if not self.square_footage:
                self.square_footage = self.remrate_target.buildinginfo.conditioned_area
        elif self.ekotrope_houseplan:
            if not self.name:
                self.name = self.ekotrope_houseplan.data.get("name")
            if not self.square_footage:
                data = (
                    self.ekotrope_houseplan.data.get("thermalEnvelope", {})
                    .get("summary", {})
                    .get("conditionedArea")
                )
                self.square_footage = data

        existing = Floorplan.objects.filter_for_uniqueness(
            name=self.name,
            owner=self.owner,
            remrate_target=self.remrate_target,
            ekotrope_houseplan=self.ekotrope_houseplan,
            simulation=self.simulation,
            id=self.pk,
        )
        if existing.exists():
            raise ValidationError("Floorplan with this name and type already exists")

        super(Floorplan, self).save(*args, **kwargs)

    def validate_references(self):
        for home_status in self.active_for_homestatuses.all():
            home_status.validate_references()

    # INPUTS
    @property
    def input_data_type(self):
        """Return the simulation input source based on presence of available attributes."""

        # NOTE: We want 'remrate' to have precedence over 'blg_data' if both are present.

        if self.ekotrope_houseplan:
            return Floorplan.INPUT_DATA_TYPE_EKOTROPE
        elif self.remrate_target:
            return Floorplan.INPUT_DATA_TYPE_REMRATE
        elif self.remrate_data_file:
            return Floorplan.INPUT_DATA_TYPE_BLG_DATA
        return None

    def get_normalized_input_data(self):
        """Returns whichever set of data ``input_data_type`` indicates is in use."""
        input_type = self.input_data_type

        if self.ekotrope_houseplan:
            return self.get_normalized_ekotrope_input_data()
        elif self.remrate_target:
            return self.get_normalized_remrate_input_data()
        elif input_type == Floorplan.INPUT_DATA_TYPE_BLG_DATA:
            return self.get_normalized_blg_input_data()
        elif input_type is None:
            return {}

        raise ValueError("No input normalizing method available for type {!r}".format(input_type))

    def get_normalized_blg_input_data(self):
        data = {
            # Expected to match one of the 'input_data_type' strings
            "source_type": Floorplan.INPUT_DATA_TYPE_BLG_DATA,
            "source_name": "BLG File",
            "valid": False,
            "error": None,
        }
        if not self.remrate_data_file:
            return dict(data, valid=False, error="No BLG data")
        try:
            blg = get_floorplan_blg_data(self.id)
        except TypeError:
            data.update(dict(valid=False, error=f"No blg data returned with {self.id}"))
            return data
        except Exception as err:
            error_str = "{}".format(err)
            log.warning(error_str)
            data.update(dict(valid=False, error=error_str))
            return data

        from axis.floorplan.api_v3.serializers import (
            NormalizedSimulationInputSerializer,
        )

        input_data = NormalizedSimulationInputSerializer(
            instance=Simulation.objects.get(id=blg["id"])
        ).data
        data.update(input_data)
        return data

    def get_normalized_remrate_input_data(self):
        """This is normalized remrate simulation intput data"""
        data = {
            # Expected to match one of the 'input_data_type' strings
            "source_type": Floorplan.INPUT_DATA_TYPE_REMRATE,
            "source_name": "REM Export",
            "valid": False,
            "error": None,
        }
        if not self.remrate_target:
            data.update(dict(valid=False, error="No REM Export"))
            return data

        from axis.floorplan.api_v3.serializers import (
            NormalizedSimulationInputSerializer,
        )

        input_data = NormalizedSimulationInputSerializer(instance=self.simulation).data
        data.update(input_data)
        return data

    def get_normalized_ekotrope_input_data(self):
        data = {
            "source_type": Floorplan.INPUT_DATA_TYPE_EKOTROPE,
            "source_name": "Ekotrope Export",
            "valid": False,
            "error": None,
        }
        if not self.simulation:
            data.update(dict(valid=False, error="No Ekotrope Export"))
            return data

        from axis.floorplan.api_v3.serializers import (
            NormalizedSimulationInputSerializer,
        )

        input_data = NormalizedSimulationInputSerializer(instance=self.simulation).data
        data.update(input_data)
        return data

    def has_heat_pump(self):
        if self.input_data_type == Floorplan.INPUT_DATA_TYPE_REMRATE:
            heater = self.remrate_target.heater_set.filter(type__in=[6, 7]).exists()
            ashp = self.remrate_target.airsourceheatpump_set.exists()
            gshp = self.remrate_target.groundsourceheatpump_set.exists()
            dfhp = self.remrate_target.dualfuelheatpump_set.exists()
            return any([heater, ashp, gshp, dfhp])

        # Unknown
        return None

    def has_other_heating(self):
        if self.input_data_type == Floorplan.INPUT_DATA_TYPE_REMRATE:
            gas_unit_heater = self.remrate_target.installedequipment_set.filter(
                **{
                    "system_type": 1,  # 'Space Heating'
                    "heater__type__in": [2, 3, 4, 5, 7, 8, 9],
                    "heater__fuel_type": 1,  # 'Natural gas'
                }
            ).exists()
            gshp = self.remrate_target.groundsourceheatpump_set.exists()
            electric_resistance = self.remrate_target.heater_set.filter(type=4).exists()
            return any([gas_unit_heater, gshp, electric_resistance])

        # Unknown
        return None

    def has_air_source_heat_pump(self):
        if self.input_data_type == Floorplan.INPUT_DATA_TYPE_REMRATE:
            heater = self.remrate_target.heater_set.filter(type__in=[6]).exists()
            ashp = self.remrate_target.airsourceheatpump_set.exists()
            return any([heater, ashp])

        # Unknown
        return None

    def has_non_air_source_heat_pump_heating(self):
        """Has a non ASHP and NOT a Fuel fired air distribution"""
        if self.input_data_type == Floorplan.INPUT_DATA_TYPE_REMRATE:
            gas_unit_heater = self.remrate_target.installedequipment_set.filter(
                **{
                    "system_type": 1,  # 'Space Heating'
                    "heater__type__in": [2, 3, 4, 5, 7, 8, 9],
                    "heater__fuel_type": 1,  # 'Natural gas'
                }
            ).exists()
            gshp = self.remrate_target.groundsourceheatpump_set.exists()
            electric_resistance = self.remrate_target.heater_set.filter(type=4).exists()
            dfhp = self.remrate_target.dualfuelheatpump_set.exists()
            return any([gas_unit_heater, gshp, dfhp, electric_resistance])

        # Unknown
        return None

    # Outputs

    # TODO: This can be removed or updated to retrieve results data from the new Home Energy Score app
    def normalized_hes_result_data(self, user: User | None = None) -> dict:
        """Get our normalized HES data"""
        try:
            hes_status = self.remrate_target.hes_score_statuses.first()
        except AttributeError:
            return {"_engine": "DOE Hes", "valid": False, "error": "No HES data"}
        else:
            if not hes_status:
                return {"_engine": "DOE Hes", "valid": False, "error": "No HES data"}
        from axis.hes.enumerations import COMPLETE

        if not hes_status.status == COMPLETE:
            return {"_engine": "DOE Hes", "valid": False, "error": "HES Calculation not complete"}
        return hes_status.worst_case_simulation.normalized_hes_result(user=user)

    def get_normalized_result_data(self, analysis=Analysis) -> dict:
        from axis.floorplan.api_v3.serializers.analysis import AnalysisSummaryDataSerializer

        serializer = AnalysisSummaryDataSerializer(instance=analysis)
        return serializer.data

    def get_normalized_ekotrope_result_data(self) -> dict:
        try:
            analysis = self.simulation.analyses.filter(
                Q(type__contains="design") | Q(type=AnalysisType.DEFAULT),
                engine=AnalysisEngine.EKOTROPE,
                status=AnalysisStatus.COMPLETE,
            ).first()
        except (ObjectDoesNotExist, AttributeError):
            return {"source": "Ekotrope®", "valid": False, "error": "No Ekotrope data"}
        if analysis is None:
            return {"source": "Ekotrope®", "valid": False, "error": "No Ekotrope data"}
        return self.get_normalized_result_data(analysis)

    def get_normalized_remrate_result_data(self) -> dict:
        try:
            analysis = self.simulation.analyses.filter(
                Q(type__contains="design") | Q(type=AnalysisType.DEFAULT),
                engine=AnalysisEngine.REMRATE,
                status=AnalysisStatus.COMPLETE,
            ).first()
        except (ObjectDoesNotExist, AttributeError):
            return {"source": "REM/Rate®", "valid": False, "error": "No REM Export"}
        if analysis is None:
            return {"source": "REM/Rate®", "valid": False, "error": "No REM Export"}
        return self.get_normalized_result_data(analysis)

    def normalized_open_studio_eri_result_data(self) -> dict:
        try:
            analysis = self.simulation.analyses.filter(
                engine=AnalysisEngine.EPLUS,
                type__in=[
                    AnalysisType.OS_ERI_2014AEG_DESIGN,
                    AnalysisType.OS_ERI_2014AE_DESIGN,
                    AnalysisType.OS_ERI_2014A_DESIGN,
                    AnalysisType.OS_ERI_2014_DESIGN,
                    AnalysisType.OS_ERI_2019AB_DESIGN,
                    AnalysisType.OS_ERI_2019A_DESIGN,
                    AnalysisType.OS_ERI_2019_DESIGN,
                ],
                status=AnalysisStatus.COMPLETE,
            ).first()
        except (ObjectDoesNotExist, AttributeError):
            return {"source": "Energy Plus", "valid": False, "error": "No Energy Plus export"}
        if analysis is None:
            return {"source": "Energy Plus", "valid": False, "error": "No Energy Plus export"}
        return self.get_normalized_result_data(analysis)

    def process_simulation_result(self):
        if not self.simulation_result and not self.remrate_target:
            raise ValueError("No 'simulation_result' or 'remrate_target' currently recorded.")

    def get_hers_score_for_program(self, eep_program=None):
        """
        Returns most appropriate HERS score.  For REM data floorplans, an APS ``eep_program``
        will trigger a return of the Energy Star 2.5 PV version of the HERS.

        All other cases, including Ekotrope floorplans, do not use the ``eep_program`` argument, and
        it may be given as ``None``.
        """

        input_type = self.input_data_type
        if input_type == Floorplan.INPUT_DATA_TYPE_REMRATE:
            if self.remrate_target:
                # Whitelist for program owners to determine which HERS score they want to use
                # Fallback to calculated RESNET HERS with PV.
                if (
                    eep_program
                    and eep_program.owner.slug == "aps"
                    and hasattr(self.remrate_target, "energystar")
                ):
                    if self.remrate_target.energystar.energy_star_v3p2_pv_score:
                        return int(self.remrate_target.energystar.energy_star_v3p2_pv_score)
                    elif self.remrate_target.energystar.energy_star_v3p1_pv_score:
                        return int(self.remrate_target.energystar.energy_star_v3p1_pv_score)
                    elif self.remrate_target.energystar.energy_star_v3_pv_score:
                        return int(self.remrate_target.energystar.energy_star_v3_pv_score)
                    elif self.remrate_target.energystar.energy_star_v2p5_pv_score:
                        return int(self.remrate_target.energystar.energy_star_v2p5_pv_score)
                elif hasattr(self.remrate_target, "hers"):
                    return int(self.remrate_target.hers.score)
                else:
                    return None
            else:
                return None
        elif input_type == Floorplan.INPUT_DATA_TYPE_EKOTROPE:
            try:
                return self.ekotrope_houseplan.analysis.data["hersScore"]
            except (AttributeError, KeyError):
                return None

    def remrate_data_filename(self):
        """Returns the actual filename."""
        if self.remrate_data_file and self.remrate_data_file.name:
            return os.path.basename(unrandomize_filename(self.remrate_data_file.name))
        return ""

    def remrate_data_blg_xml_url(self):
        """Returns the actual filename."""
        if self.simulation:
            return reverse("api_v3:simulations-blg-remxml", args=[self.simulation.pk])

    def remrate_data_sim_xml_url(self):
        """Returns the actual filename."""
        if self.simulation:
            return reverse("api_v3:simulations-remxml", args=[self.simulation.pk])

    # Model shortcuts
    def get_company(self):
        """Return the owner"""
        return self.owner

    def get_remrate_target_with_related(self):
        """
        Prefetches the connected related models to the ``remrate_target``.  This makes use of the
        variable in templates much better on query counts.
        """
        from axis.remrate_data.models import Simulation

        if not hasattr(self.remrate_target, "pk"):
            return Simulation.objects.none()
        queryset = Simulation.objects.filter(pk=self.remrate_target.pk)
        queryset = queryset.select_related("compliance", "buildinginfo")
        queryset = queryset.prefetch_related(
            "installedequipment_set__ground_source_heat_pump",
            "installedequipment_set__dual_fuel_heat_pump",
            "installedequipment_set__air_conditioner",
            "installedequipment_set__hot_water_heater",
            "installedequipment_set__air_source_heat_pump",
            "installedequipment_set__integrated_space_water_heater",
            "ductsystem_set",
            "abovegradewall_set__type__composite_type",
            "roof_set",
            "window_set__type",
        )
        remrate = queryset[0]
        return remrate

    def filename(self):
        """Base filename for a document"""
        if self.remrate_data_file:
            return os.path.basename(self.remrate_data_file.name)
        return None

    def revoke_approval(self, user, homestatus=None, subdivision=None, eep_program=None):
        """
        Uses ``homestatus`` (or ``subdivision`` and ``eep_program`` together) to revoke a previously
        given approval, to be potentially reinstated by the program's owner.

        ``user`` can be None since the model supports it, but normally the request.user should be
        given.
        """

        if not homestatus and not (subdivision and eep_program):
            raise ValueError(
                "Need 'homestatus' argument, or else 'subdivision' and 'eep_program' " "together."
            )
        if homestatus:
            subdivision = homestatus.home.subdivision
        approval_qs = self.floorplanapproval_set.filter(subdivision=subdivision)
        previous_approval = approval_qs.exists() and approval_qs[0].is_approved
        approval_qs.update(is_approved=False, approved_by=user)
        return previous_approval

    def get_approved_status(self, subdivision=None):
        """Returns the floorplan's approval flag for the given subdivision or in general."""
        ApprovalStatus = collections.namedtuple(
            "ApprovalStatus",
            [
                "is_approved",
                "user_name",
                "date_modified",
                "thermostat_qty",
                "instance",
            ],
        )

        approvals = self.floorplanapproval_set.select_related("approved_by").order_by(
            "-date_modified"
        )
        if subdivision:
            approvals = approvals.filter(subdivision=subdivision)

        approval = approvals.first()
        if not approval:
            return ApprovalStatus(
                is_approved=None,
                user_name=None,
                date_modified=None,
                thermostat_qty=0,
                instance=None,
            )

        if approval.approved_by:
            user_name = (
                " ".join(
                    (approval.approved_by.first_name or "", approval.approved_by.last_name or "")
                ).strip()
                or approval.approved_by.username
            )
        else:
            user_name = "*Administrator"

        has_unapproved = approvals.filter(is_approved=False).exists()
        return ApprovalStatus(
            is_approved=not has_unapproved,
            user_name=user_name,
            date_modified=approval.date_modified,
            thermostat_qty=approval.thermostat_qty,
            instance=approval,
        )

    def get_aps_reviewed_status(self):
        annotation = self.annotations.filter(type__slug="aps-is_reviewed").first()
        RevStatus = collections.namedtuple(
            "RevStatus", "is_reviewed reviewed_by review_date annotation"
        )
        if annotation:
            return RevStatus(
                annotation.content == "True",
                "{}".format(annotation.user) if annotation.user else None,
                annotation.last_update,
                annotation,
            )
        return RevStatus(None, None, None, None)

    @classmethod
    def can_be_added(cls, requesting_user):
        return requesting_user.has_perm("floorplan.add_floorplan")

    def can_be_edited(self, requesting_user):
        """Who can edit a floorplan"""

        if requesting_user.is_superuser:
            return True
        if requesting_user.company != self.owner:
            return False
        if "floorplan.change_floorplan" not in requesting_user.get_all_permissions():
            return False

        return True

    def can_be_deleted(self, requesting_user):
        """Can a floorplan be deleted"""
        from axis.home.models import EEPProgramHomeStatus

        if requesting_user.is_superuser:
            return True
        if requesting_user.company != self.owner:
            return False
        if "floorplan.delete_floorplan" not in requesting_user.get_all_permissions():
            return False
        if EEPProgramHomeStatus.objects.filter(floorplan=self).count():
            return False
        return True

    def can_be_simulated(self, requesting_user):
        if requesting_user.is_superuser:
            return True
        if (
            self.can_be_edited(requesting_user)
            and "floorplan.can_simulate" in requesting_user.get_all_permissions()
        ):
            return True
        return False

    def can_download_xml(self, requesting_user):
        if self.owner_id and self.remrate_target_id:
            if requesting_user.is_superuser or requesting_user.company == self.owner:
                return True

            if requesting_user.company.has_mutual_relationship(self.owner):
                return True

        return False

    @property
    def is_restricted(self):
        return self.homestatuses.filter(
            Q(incentivepaymentstatus__isnull=True)
            | ~Q(incentivepaymentstatus__state__in=["start", "ipp_payment_failed_requirements"]),
            certification_date__isnull=False,
        ).count()

    def should_send_relationship_notification(self, company):
        """Under what criteria should a message be sent to other users"""
        return False

    def get_floorplan_blg_data(self):
        if self.remrate_data_file:
            return get_floorplan_blg_data(self.id)

    @property
    def simulation_passes_energy_star_v3(self):
        if self.remrate_target:
            try:
                return self.remrate_target.energystar.passes_energy_star_v3
            except AttributeError:
                pass

        elif self.ekotrope_houseplan:
            try:
                compliances = self.ekotrope_houseplan.analysis.data.get("compliance", [])
                compliance = next((x for x in compliances if x.get("code") == "EnergyStarV3"), {})
                return compliance.get("complianceStatus") == "Pass"
            except AttributeError:
                pass

    def get_simulation_cache_key_for_home_status(self, home_status):
        """For a given home status get a cache key"""
        dates = [
            home_status.modified_date,
            home_status.floorplan.modified_date,
            home_status.collectedinput_set.order_by("date_modified").last().date_modified,
            home_status.floorplan.simulation.modified_date,
        ]
        last_modified = max(dates).strftime("%d-%b-%Y %H:%M:%S")

        key = (
            f"sim-{home_status.id}-{home_status.floorplan.id}-"
            f"{home_status.floorplan.simulation.id}-{last_modified}"
        )
        cache_key = hashlib.sha1(key).encode("utf-8").hexdigest()
        return cache_key
