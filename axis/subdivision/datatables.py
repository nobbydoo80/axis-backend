"""views.py: Django community"""


import logging

from django.apps import apps
from django.urls import reverse

from datatableview import datatables, helpers

from axis.core.utils import get_frontend_url
from axis.company.models import Company
from axis.relationship.utils import get_relationship_column_supplier
from axis.home.models import Home, EEPProgramHomeStatus
from .models import Subdivision, FloorplanApproval


__author__ = "Autumn Valenta"
__date__ = "10/23/15 11:34 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
frontend_app = apps.get_app_config("frontend")


class SubdivisionListDatatable(datatables.Datatable):
    name = datatables.TextColumn("Subdivision/MF Development", "name", processor="get_name_data")
    builder = datatables.TextColumn("Builder", "builder_org__name", processor="get_builder_data")
    subdivision_type = datatables.TextColumn("Type", processor="get_subdivision_type_data")
    community = datatables.TextColumn(
        "Community", "community__name", processor="get_community_data"
    )
    city = datatables.TextColumn(
        "City", ["city__name", "city__state"], processor=helpers.format("{0[0]}, {0[1]}")
    )
    rater = datatables.DisplayColumn(
        "Rater / Provider", "relationships__company__name", processor="get_rater_data"
    )
    qa = datatables.TextColumn("QA", "qastatus__state", processor="get_qa_data")
    associations = datatables.DisplayColumn("Associations", processor="_rel_callback")

    class Meta:
        model = Subdivision
        columns = [
            "name",
            "subdivision_type",
            "builder",
            "community",
            "city",
            "rater",
            "qa",
            "associations",
        ]
        ordering = ["name"]
        search_fields = ["builder_name", "relationships__company__name"]

    def __init__(self, *args, **kwargs):
        self.hints = kwargs.pop("hints", {})
        super(SubdivisionListDatatable, self).__init__(*args, **kwargs)

        user = self.view.request.user
        self._rel_callback = get_relationship_column_supplier(user, "subdivision", "subdivision")

    def preload_record_data(self, obj):
        return {
            "relationships": obj.relationships,
            "attached": self.hints["attached"],
        }

    def get_name_data(self, obj, **kwargs):
        data = [helpers.link_to_model(obj, text=obj.name)]
        if obj.builder_name:
            data.append(" ({})".format(obj.builder_name))
        data.append(obj.get_address_designator())
        return "".join(data)

    def get_builder_data(self, obj, **kwargs):
        if (
            obj.builder_org.id in self.hints["company_relationship_ids"]
            or obj.builder_org.id == self.view.request.company.id
        ):
            return helpers.link_to_model(obj.builder_org, text=obj.builder_org.name)
        return obj.builder_org.name

    def get_community_data(self, obj, **kwargs):
        if obj.community:
            return helpers.link_to_model(obj.community, text=obj.community.name)
        return "-"

    def get_rater_data(self, obj, **kwargs):
        orgs = []
        for rel in obj.relationships.all():
            if rel.company.company_type in ["provider", "rater"]:
                if (
                    rel.company in self.hints["company_relationships"]
                    or rel.company.id == self.view.request.company.id
                ):
                    orgs.append(helpers.link_to_model(rel.company, text=rel.company.name))
                else:
                    orgs.append(rel.company.name)
        return "<br />".join(orgs) or "-"

    def get_qa_data(self, obj, *args, **kwargs):
        statuses = []
        for qastatus in obj.qastatus_set.all():
            statuses.append(qastatus.get_state_display())
        return "<br />".join(statuses) or "-"

    def get_subdivision_type_data(self, obj, *args, **kwargs):
        if obj.is_multi_family:
            return "MF Development"
        return "Subdivision"


class SubdivisionHomesDatatable(datatables.Datatable):
    address = datatables.TextColumn(
        label="Address",
        sources=["street_line1", "street_line2", "city__name", "state", "zipcode", "lot_number"],
        processor="get_address_data",
    )
    project_id = datatables.TextColumn(
        label="Project ID",
        source="homestatuses__customer_hirl_projects__id",
        processor="get_project_id",
    )
    floorplan = datatables.TextColumn(
        label="Floorplan", source="homestatuses__floorplan__name", processor="get_floorplan_data"
    )
    program = datatables.TextColumn(
        label="Program", source=["homestatuses__eep_program__name"], processor="get_program_data"
    )
    state = datatables.TextColumn(
        label="State", source="homestatuses__state", processor="get_state_data"
    )
    coordinates = datatables.TextColumn(label="Coordinates", sources=["latitude", "longitude"])
    meterset_date = datatables.DateColumn(label="MS Date", source=["apshome__meterset_date"])

    class Meta:
        model = Home
        columns = [
            "address",
            "project_id",
            "floorplan",
            "program",
            "state",
            "coordinates",
            "meterset_date",
        ]
        hidden_columns = ["coordinates"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.related_data = kwargs.pop("related_data")
        self.user_floorplans = kwargs.pop("user_floorplans")
        self.user_programs = kwargs.pop("user_programs")

        super(SubdivisionHomesDatatable, self).__init__(*args, **kwargs)

        if not self.user.is_superuser and self.user.company.slug != "aps":
            del self.columns["meterset_date"]

    def get_project_id(self, home, **kwargs):
        items = self.related_data["customer_hirl_projects"].get(home.id)
        data = []
        for item in items:
            if not any(item.values()):
                continue

            if item["id"] is not None:
                url = get_frontend_url("hi", "project_registrations", item["registration_id"])
                data.append(f'<a href="{url}">{item["id"]}</a>')
        return "<br>".join(data)

    def get_address_data(self, obj, **kwargs):
        text = obj.get_home_address_display(company=self.user.company)
        return helpers.link_to_model(obj, text=text)

    def get_floorplan_data(self, obj, *args, **kwargs):
        items = self.related_data["floorplans"].get(obj.id)
        data = []
        for item in items:
            if not any(item.values()) or not item["floorplan"]:
                continue

            if not item["number"] or (item["name"] == item["number"]):
                string = "{name}"
            else:
                string = "{name} / {number}"

            if item["floorplan"] in self.user_floorplans or item["owner"] == self.user.company.id:
                string = """<a href="{url}">{text}</a>""".format(
                    text=string, url=reverse("floorplan:view", kwargs={"pk": item["floorplan"]})
                )
            data.append(string.format(**item))
        return "<br>".join(data)

    def get_program_data(self, obj, *args, **kwargs):
        items = self.related_data["programs"].get(obj.id)
        data = []
        for item in items:
            if not any(item.values()):
                continue

            string = "{name}"

            if item["program"] in self.user_programs or item["owner"] == self.user.company.id:
                string = """<a href="{url}">{text}</a>""".format(
                    text=string, url=reverse("eep_program:view", kwargs={"pk": item["program"]})
                )
            data.append(string.format(**item))
        return "<br>".join(data)

    def get_state_data(self, obj, *args, **kwargs):
        items = self.related_data["states"].get(obj.id)
        data = []
        for item in items:
            if not any(item.values()):
                continue

            if item["state"] is not None:
                data.append(EEPProgramHomeStatus.Machine.get_state(item["state"]).description)
        return "<br>".join(data)


class HIRLSubdivisionHomesDataTable(datatables.Datatable):
    """
    Special datatable for HIRL Projects
    """

    project_id = datatables.TextColumn(label="Project ID", processor="get_project_id")
    project_building_type = datatables.TextColumn(
        label="Type", processor="get_project_building_type"
    )
    address = datatables.TextColumn(
        label="Address",
        sources=["street_line1", "street_line2", "city__name", "state", "zipcode", "lot_number"],
        processor="get_address_data",
    )
    program = datatables.TextColumn(
        label="Program", source=["homestatuses__eep_program__name"], processor="get_program_data"
    )
    state = datatables.TextColumn(
        label="State", source="homestatuses__state", processor="get_state_data"
    )

    class Meta:
        model = Home
        columns = ["project_id", "address", "program", "project_building_type", "state"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.related_data = kwargs.pop("related_data")
        self.user_programs = kwargs.pop("user_programs")
        super(HIRLSubdivisionHomesDataTable, self).__init__(*args, **kwargs)

    def get_address_data(self, obj, **kwargs):
        text = obj.get_home_address_display(company=self.user.company)
        return helpers.link_to_model(obj, text=text)

    def get_project_id(self, home, **kwargs):
        items = self.related_data["customer_hirl_projects"].get(home.id)
        data = []
        for item in items:
            if not any(item.values()):
                continue

            if item["id"] is not None:
                url = (
                    f"/{frontend_app.DEPLOY_URL}/hi/"
                    f'project_registrations/{item["registration_id"]}'
                )
                data.append(f'<a href="{url}">{item["id"]}</a>')
        return "<br>".join(data)

    def get_project_building_type(self, home, **kwargs):
        home_status = home.homestatuses.filter(customer_hirl_project__isnull=False).first()
        if home_status:
            if home_status.customer_hirl_project.is_accessory_structure:
                return "Accessory Structure"
            if home_status.customer_hirl_project.is_accessory_dwelling_unit:
                return "Accessory Dwelling Unit"
            if home_status.customer_hirl_project.commercial_space_type:
                return "Commercial Space"
        return "Building"

    def get_program_data(self, obj, *args, **kwargs):
        items = self.related_data["programs"].get(obj.id)
        data = []
        for item in items:
            if not any(item.values()):
                continue

            string = "{name}"

            if item["program"] in self.user_programs or item["owner"] == self.user.company.id:
                string = """<a href="{url}">{text}</a>""".format(
                    text=string, url=reverse("eep_program:view", kwargs={"pk": item["program"]})
                )
            data.append(string.format(**item))
        return "<br>".join(data)

    def get_state_data(self, obj, *args, **kwargs):
        items = self.related_data["states"].get(obj.id)
        data = []
        for item in items:
            if not any(item.values()):
                continue

            if item["state"] is not None:
                data.append(EEPProgramHomeStatus.Machine.get_state(item["state"]).description)
        return "<br>".join(data)


class SubdivisionFloorplansDatatable(datatables.Datatable):
    name = datatables.TextColumn(
        source="floorplan__name",
        processor=helpers.link_to_model(key=helpers.attrgetter("floorplan")),
    )
    number = datatables.TextColumn(source="floorplan__number")
    square_footage = datatables.IntegerColumn(source="floorplan__square_footage", label="Ft²")
    is_active = datatables.BooleanColumn(
        source="is_approved", label="Active", processor="get_is_active_data"
    )
    created_date = datatables.DateColumn(
        source="floorplan__created_date",
        label="Creation Date",
        processor=helpers.format_date("%m/%d/%Y"),
    )

    # Virtual columns
    simulation = datatables.DisplayColumn(label="Simulation Data", processor="get_simulation_data")
    in_use = datatables.DisplayColumn(label="In-Use", processor="get_in_use_data")
    hers = datatables.FloatColumn(
        label="HERS w/o PV",
        source="remrate_target__energystar__energy_star_v2p5_pv_score",
        processor="get_hers_data",
    )
    tstat_count = datatables.IntegerColumn(
        source="thermostat_qty", label="Qty T-Stats", processor="get_tstat_data"
    )

    class Meta:
        model = FloorplanApproval
        columns = [
            "name",
            "number",
            "simulation",
            "square_footage",
            "in_use",
            "is_active",
            "created_date",
            "hers",
            "tstat_count",
        ]
        ordering = ["-created_date"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(SubdivisionFloorplansDatatable, self).__init__(*args, **kwargs)

        if not self.user.is_superuser and self.user.company.slug != "aps":
            # APS-only column
            del self.columns["is_active"]
            del self.columns["tstat_count"]

            # Remove 'HERS' if the company isn't mutually related to APS.
            try:
                aps_company = Company.objects.get(slug="aps")
            except Company.DoesNotExist:
                pass
            else:
                aps_mutual_rels = Company.objects.filter_by_company(aps_company, mutual=True)
                if not aps_mutual_rels.filter(id=self.user.company.id).exists():
                    del self.columns["hers"]

    def get_simulation_data(self, instance, *args, **kwargs):
        obj = None
        if instance.floorplan.remrate_target:
            obj = instance.floorplan.remrate_target
            text = "{}".format(obj.get_full_name() or obj)[:45]
        elif hasattr(instance.floorplan, "ekotrope_houseplan"):
            obj = instance.floorplan.ekotrope_houseplan
            text = "{}".format(obj)

        if obj:
            return helpers.link_to_model(obj, text=text)
        return "-"

    def get_in_use_data(self, instance, *args, **kwargs):
        count = (
            instance.floorplan.homestatuses.count()
            or instance.floorplan.active_for_homestatuses.count()
        )
        return helpers.make_boolean_checkmark(count, false_value="-")

    def get_is_active_data(self, instance, *args, **kwargs):
        return helpers.make_boolean_checkmark(kwargs["default_value"], false_value="-")

    def get_hers_data(self, instance, *args, **kwargs):
        return instance.floorplan.get_hers_score_for_program(eep_program=None) or "-"

    def get_tstat_data(self, instance, *args, **kwargs):
        return instance.thermostat_qty if instance.is_approved else "-"
