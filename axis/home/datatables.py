"""views.py: Django community"""


import datetime
import logging

from datatableview import datatables, helpers

from axis.subdivision.models import Subdivision
from .models import Home

__author__ = "Autumn Valenta"
__date__ = "10/23/15 11:34 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class HomeListDatatable(datatables.Datatable):
    address = datatables.TextColumn(
        "Address",
        ["street_line1", "street_line2", "state", "zipcode", "city__name"],
        processor="get_address_data",
    )
    subdivision = datatables.TextColumn(
        "Subdivision/MF Development", "subdivision__name", processor="get_subdivision_data"
    )
    floorplan = datatables.TextColumn(
        "Floorplan", "homestatuses__floorplan__name", processor="get_floorplan_data"
    )
    programs = datatables.TextColumn(
        "Programs", "homestatuses__eep_program__name", processor="get_programs_data"
    )
    hs_states = datatables.TextColumn(
        "Project Status", "homestatuses__state", processor="get_hs_states_data"
    )
    qa_states = datatables.TextColumn(
        "QA Status", "homestatuses__incentivepaymentstatus__state", processor="get_qa_states_data"
    )
    ms_date = datatables.DateTimeColumn(
        "MS Date", "apshome__meterset_date", processor="get_ms_date_data"
    )

    class Meta:
        model = Home
        columns = [
            "lot_number",
            "address",
            "subdivision",
            "floorplan",
            "programs",
            "hs_states",
            "qa_states",
            "ms_date",
        ]
        labels = {
            "lot_number": "Lot",
        }
        processors = {
            "lot_number": helpers.link_to_model,
        }

    def __init__(self, *args, **kwargs):
        self.hints = kwargs.pop("hints", {})  # only sent during ajax
        self.company = kwargs.pop("company")
        super(HomeListDatatable, self).__init__(*args, **kwargs)

    def get_address_data(self, obj, **kwargs):
        return obj.get_home_address_display(
            include_lot_number=False, include_confirmed=True, company=self.company
        )

    def get_subdivision_data(self, obj, **kwargs):
        try:
            sub = obj.subdivision
        except Subdivision.DoesNotExist:
            return "Custom"
        else:
            try:
                name = "{}{}{}".format(
                    sub.name,
                    " at {}".format(sub.community) if sub.community else "",
                    " ({})".format(sub.builder_name) if sub.builder_name else "",
                )
                return helpers.link_to_model(obj.subdivision, text=name)
            except AttributeError:
                return "Custom"

    def get_floorplan_data(self, obj, **kwargs):
        user = self.view.request.user
        results = []
        for stat in self.hints["home_stats"][obj.id]:
            try:
                floorplan = stat.floorplan
                name = "{}".format(floorplan.name)
            except AttributeError:
                continue
            if floorplan.number and floorplan.number.strip() != floorplan.name.strip():
                name = "{} / {}".format(floorplan.name, floorplan.number)
            if floorplan in self.hints["user_floorplans"] or floorplan.owner == user.company:
                results.append(helpers.link_to_model(floorplan, text=name))
            else:
                results.append(name)

        return "<br />".join(results)

    def get_programs_data(self, obj, **kwargs):
        user = self.view.request.user
        eeps = []
        for stat in self.hints["home_stats"][obj.id]:
            if (
                stat.eep_program in self.hints["company_eep_programs"]
                or stat.eep_program.owner == user.company
            ):
                eeps.append(helpers.link_to_model(stat.eep_program, text=stat.eep_program.name))
            else:
                eeps.append(stat.eep_program.name)
        return "<br/>".join(eeps)

    def get_hs_states_data(self, obj, **kwargs):
        states = []
        for stat in self.hints["home_stats"][obj.id]:
            states.append(stat.get_state_display())

        return "<br />".join(states)

    def get_qa_states_data(self, obj, **kwargs):
        qa_string = "{type}: {state}"
        states = []
        for stat in self.hints["home_stats"][obj.id]:
            for qa in stat.qastatus_set.select_related("requirement"):
                string = qa_string.format(
                    type=qa.requirement.get_type_display(), state=qa.get_state_display()
                )
                states.append(string)
        return "<br />".join(states)

    def get_ms_date_data(self, obj, **kwargs):
        try:
            ms_date = next((x.url for x in self.hints["aps_metersets"] if x.id == obj.id))
        except:
            return ""
        return ms_date or ""


class HomeStatusListDatatable(datatables.Datatable):
    address = datatables.TextColumn(
        "Address",
        [
            "home__street_line1",
            "home__street_line2",
            "home__state",
            "home__zipcode",
            "home__city__name",
        ],
        processor="get_address_data",
    )
    subdivision = datatables.TextColumn(
        "Subdivision/MF Development", "home__subdivision__name", processor="get_subdivision_data"
    )
    floorplan = datatables.TextColumn(
        "Floorplan", "floorplan__name", processor="get_floorplan_data"
    )
    program = datatables.TextColumn("Programs", "eep_program__name", processor="get_programs_data")
    hs_state = datatables.TextColumn("Project Status", "state", processor="get_hs_state_data")
    ipp_state = datatables.TextColumn(
        "Incentive Status", "incentivepaymentstatus__state", processor="get_incentive_state_data"
    )
    qa_state = datatables.TextColumn(
        "QA Status",
        sources=["qastatus__last_update", "qastatus__state"],
        processor="get_qa_state_data",
    )

    class Meta:
        # cache_type = 'default'
        cache_queryset_count = False
        model = Home
        columns = [
            "address",
            "subdivision",
            "floorplan",
            "program",
            "hs_state",
            "ipp_state",
            "qa_state",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.company = kwargs.pop("company")
        self.hints = kwargs.pop("hints", {})
        super(HomeStatusListDatatable, self).__init__(*args, **kwargs)

    def get_cache_key_kwargs(self, **kwargs):
        kwargs = super(HomeStatusListDatatable, self).get_cache_key_kwargs(**kwargs)
        kwargs.update(
            {
                "q_filters": self.view.q_filters,
                "filters": self.view.filters,
                "filter": self.view.filter,
                "exclude": self.view.exclude,
            }
        )
        return kwargs

    def expand_object_list_from_cache(self, *args, **kwargs):
        """Re-apply select_related() to cached queryset from view's original one."""
        queryset = super(HomeStatusListDatatable, self).expand_object_list_from_cache(
            *args, **kwargs
        )
        queryset = queryset.select_related(*self.view.select_related)
        return queryset

    def count_objects(self, base_objects, filtered_objects):
        """Force caching of filter terms to help with COUNT query overhead."""

        # Set up a cached lookup of ``filtered_objects.count()``

        cache_kwargs = self.get_cache_key_kwargs(
            view=self.view, __num_filtered=self.config["search"]
        )
        if self.config["search"]:
            num_filtered = self.get_cached_data(**cache_kwargs)
            was_cached = num_filtered is not None
        else:
            was_cached = False

        # If we already have a cached number for filtered_objects, wipe out the queryset so that it
        # can't be counted again.  This has no impact on the data returned to the client, so long
        # as we remember the cached number and return that instead.
        if was_cached:
            cached_num_filtered = num_filtered
            filtered_objects = []

        num_total, num_filtered = super(HomeStatusListDatatable, self).count_objects(
            base_objects, filtered_objects
        )

        if was_cached:
            num_filtered = cached_num_filtered
        else:
            self.cache_data(num_filtered, **cache_kwargs)

        return num_total, num_filtered

    def get_address_data(self, obj, **kwargs):
        text = obj.home.get_home_address_display(
            include_lot_number=True, include_confirmed=True, company=self.company
        )

        link = """
            <a href='{url}' target='_blank'
                data-toggle='tooltip'
                data-original-title='Created by: {history_user} - {builder}'>
                {text}
            </a>
        """

        return link.format(
            **{
                "url": obj.get_absolute_url(),
                "history_user": self._get_historical_user_for_home(obj.home.id),
                "builder": obj.home.get_builder(),
                "text": text,
            }
        )

    def get_subdivision_data(self, obj, **kwargs):
        subdivision = obj.home.subdivision

        if subdivision and subdivision.community:
            url = """
            <a href='{url}' target='_blank' data-toggle='tooltip'
                data-placement='top' data-original-title='Community: {tooltip}'>
                {text}
            </a>
            """
            community = subdivision.community
            return url.format(
                **{
                    "url": subdivision.get_absolute_url(),
                    "tooltip": "{}".format(community),
                    "text": "{}".format(subdivision),
                }
            )

        elif subdivision:
            return helpers.link_to_model(subdivision)

        return "Custom"

    def get_floorplan_data(self, obj, **kwargs):
        if not obj.floorplan:
            return "-"
        return helpers.link_to_model(obj.floorplan, text=obj.floorplan.name)

    def get_programs_data(self, obj, **kwargs):
        return helpers.link_to_model(obj.eep_program, text=obj.eep_program.name)

    def get_hs_state_data(self, obj, **kwargs):
        return obj.get_state_display()

    def get_incentive_state_data(self, obj, **kwargs):
        try:
            return obj.incentivepaymentstatus.state_description
        except:
            return "-"

    def get_qa_state_data(self, obj, **kwargs):
        qa_string = "{type}: {state} {duration}"
        _states, _durations = [], []
        for qa in obj.qastatus_set.all().select_related("requirement"):
            duration_days = self._get_qa_duration(qa)
            duration = "{0:.2f}".format(duration_days) if duration_days is not None else ""

            string = qa_string.format(
                type=qa.requirement.get_type_display(),
                state=qa.get_state_display(),
                duration=duration,
            )
            _states.append(string)
            _durations.append(duration_days if duration_days is not None else 0)

        if len(_states):
            return (max(_durations), "<br/>".join(_states))

        return (0, "-")

    def _get_qa_duration(self, qa):
        if qa.state == "complete":
            return None
        else:
            # If not complete, show amount of time in current state.
            duration = datetime.datetime.now(qa.last_update.tzinfo) - qa.last_update

        days = duration.days
        days += (float(duration.seconds) / 3600) / 24

        return days

    def _get_historical_user_for_home(self, home_id):
        """
        This method was added to parity the tooltip in the Address column of IPP tables.
        Unfortunately, the ability to filter possible viewable items is much easier in IPP
        than it is here. Copying the mechanism used in IPP adds ~4-5 seconds to load times because of
        all the models being loaded into memory.
        This current mechanism adds 1 query per row used.
        It isn't called until after pagination has occurred.
        Assuming the user isn't asking for a beating and viewing all items in a
        very large queryset, this should be manageable.

        I'm sorry.
        """

        try:
            historical_home = (
                Home.history.model.objects.select_related("history_user__company")
                .filter(id=home_id)
                .first()
            )
            historical_user = historical_home.history_user
        except AttributeError:
            log.info("No history for home %r", home_id, extra={"request": self.view.request})
            historical_user = None

        if historical_user:
            return "{}".format(historical_user.company)

        return "Administrator"
