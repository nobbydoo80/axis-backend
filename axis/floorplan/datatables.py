"""views.py: Django community"""


import logging

from django.urls import reverse

from datatableview import datatables, helpers

from axis.home.models import Home, EEPProgramHomeStatus
from .models import Floorplan
from .strings import FLOORPLAN_SUBDIVISION_MISMATCH


__author__ = "Autumn Valenta"
__date__ = "10/23/15 11:34 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class FloorplanListDatatable(datatables.Datatable):
    """Main List table"""

    floorplan_name = datatables.TextColumn(
        label="Floorplan Name / Number",
        sources=["name", "number"],
        processor="get_floorplan_name_data",
    )
    subdivision_names = datatables.TextColumn(
        label="Subdivision", source="subdivision__name", processor="get_subdivision_names_data"
    )
    simulation_data = datatables.CompoundColumn(
        label="Simulation Input",
        sources=[
            datatables.IntegerColumn(source="remrate_target__id"),
            datatables.TextColumn(source="ekotrope_houseplan__id"),
        ],
        processor="get_simulation_data",
    )
    owner_name = datatables.TextColumn(label="Company", source="owner__name")

    class Meta:
        model = Floorplan
        columns = [
            "floorplan_name",
            "subdivision_names",
            "simulation_data",
            "comment",
            "owner_name",
        ]
        ordering = ["floorplan_name"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(FloorplanListDatatable, self).__init__(*args, **kwargs)

        if user.company.is_eep_sponsor or user.is_superuser:
            del self.columns["owner_name"]

    def get_floorplan_name_data(self, obj, *args, **kwargs):
        show_home_counter = False
        is_certified = False

        # Get certifications (deliberate includes possible None)
        certification_dates = list(obj.homestatuses.values_list("certification_date", flat=True))
        show_home_counter = len(certification_dates)  # indirect indicator of homestatuses.exists()
        is_certified = any(certification_dates)

        name = obj.name
        if not name:
            name = "-"
        if obj.name != obj.number:
            name = "{} / {}".format(obj.name, obj.number)

        text = helpers.link_to_model(obj, text=name)

        if show_home_counter:
            MAX_HOMES = 5
            NUM_HOMES = min(
                MAX_HOMES + 1, len(certification_dates)
            )  # pad 1 for replacing to '...' if needed
            homes = ['<i class="fa fa-home"></i>' for i in range(NUM_HOMES)]
            if len(homes) > MAX_HOMES:
                homes[-1] = "&hellip;"
            text += "&nbsp;<small>{}<small>".format("".join(homes))
        if is_certified:
            text += '&nbsp;<small><i class="fa fa-lock"></i></small>'
        return text

    def get_subdivision_names_data(self, obj, *args, **kwargs):
        names = []
        fields = [
            "subdivision__id",
            "subdivision__name",
            "subdivision__builder_name",
            "is_approved",
        ]
        for id, name, builder_name, is_approved in list(
            obj.floorplanapproval_set.values_list(*fields)
        ):
            text = name
            if builder_name:
                text += " ({})".format(builder_name)
            text = """<a href="{url}">{text}</a> """.format(
                **{
                    "url": reverse("subdivision:view", kwargs={"pk": id}),
                    "text": text,
                }
            )
            names.append(text)

        if names:
            return "<br>".join(names)
        return "-"

    def get_simulation_data(self, obj, *args, **kwargs):
        if obj.ekotrope_houseplan:
            return helpers.link_to_model(obj.ekotrope_houseplan)
        elif obj.remrate_target:
            return helpers.link_to_model(obj.remrate_target)
        return "-"


class FloorplanHomesDatatable(datatables.Datatable):
    """Scoped listing of homes for a given floorplan"""

    address = datatables.TextColumn(
        label="Address",
        sources=["street_line1", "street_line2", "city__name", "state", "zipcode", "lot_number"],
        processor="get_address_data",
    )
    subdivision = datatables.TextColumn(
        label="Subdivision", source="subdivision__name", processor="get_subdivision_data"
    )
    program = datatables.TextColumn(
        label="Program", source=["homestatuses__eep_program__name"], processor="get_program_data"
    )
    state = datatables.TextColumn(
        label="State", source=["homestatuses__state"], processor="get_state_data"
    )

    class Meta:
        model = Home
        columns = ["address", "subdivision", "program", "state"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.floorplan = kwargs.pop("floorplan")  # Could be None if examine page is in create mode
        self.user_programs = kwargs.pop("user_programs")

        super(FloorplanHomesDatatable, self).__init__(*args, **kwargs)

    def get_address_data(self, obj, **kwargs):
        text = obj.get_home_address_display(company=self.user.company)
        return helpers.link_to_model(obj, text=text)

    def get_subdivision_data(self, obj, *args, **kwargs):
        if not obj.subdivision:
            return ""

        # FIXME: We might want to distinguish a home that isn't *actively* using the floorplan as
        # not being a big deal.  There are "preliminary" floorplans with data that doesn't validate
        # but shouldn't trigger loud errors.

        # Verify that home is using a subdivision that the floorplan covers
        if self.floorplan and (self.user.company == self.floorplan.owner or self.user.is_superuser):
            if self.floorplan.subdivision_set.filter(id=obj.subdivision_id).exists():
                return helpers.link_to_model(obj.subdivision)

            text = """<div class="label label-danger" data-toggle="tooltip" data-placement="top" title="{}">
                        <a style="color: white" href="{}">{}</a>
                      </div>"""
            msg = FLOORPLAN_SUBDIVISION_MISMATCH.format(subdivision=obj.subdivision)
            subdivision_url = obj.subdivision.get_absolute_url()
            return text.format(msg, subdivision_url, obj.subdivision)

        return obj.subdivision.name

    def get_program_data(self, obj, *args, **kwargs):
        data = []
        fields = ["eep_program__id", "eep_program__name", "eep_program__owner"]
        for id, name, owner in obj.homestatuses.values_list(*fields):
            text = name

            if id in self.user_programs or owner == self.user.company.id:
                url = reverse("eep_program:view", kwargs={"pk": id})
                text = """<a href="{url}">{text}</a>""".format(url=url, text=text)
            data.append(text)
        return "<br>".join(data)

    def get_state_data(self, obj, *args, **kwargs):
        states = []
        for homestatus in obj.homestatuses.all():
            states.append(homestatus.get_state_display())
        return ", ".join(states)
