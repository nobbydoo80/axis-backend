""" Sampling views, round 2, ding ding. """


import logging

from django.db.models import Count, Q, F
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

import datatableview.helpers
from axis.checklist.models import Answer

from axis.core.views.generic import LegacyAxisDatatableView, AxisDetailView
from axis.core.mixins import AuthenticationMixin
from axis.core.utils import filter_integers, values_to_dict
from axis.home.models import EEPProgramHomeStatus
from .models import SampleSet, SampleSetHomeStatus
from .forms import HomeQueryForm

__author__ = "Autumn Valenta"
__date__ = "07-30-14 12:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SampleSetListView(AuthenticationMixin, LegacyAxisDatatableView):
    permission_required = "sampleset.view_sampleset"
    model = SampleSet

    show_add_button = False

    datatable_options = {
        "columns": [
            ("Sample Set / Alt Name", ("uuid", "alt_name"), "get_column_unicode_data"),
            (
                "Company",
                "owner__name",
                datatableview.helpers.link_to_model(key=datatableview.helpers.attrgetter("owner")),
            ),
            (
                "Program",
                "samplesethomestatus__home_status__eep_program__name",
                "get_column_Program_data",
            ),
            (
                "Builder",
                "samplesethomestatus__home_status__home__relationships__company__name",
                "get_column_Builder_data",
            ),
            ("Is Metro", "is_metro_sampled", datatableview.helpers.make_boolean_checkmark),
            ("Complete", "complete", lambda *args, **kwargs: "[XX%]"),
            ("Test/Sampled", None, "get_column_Test_Sampled_data"),
        ],
    }

    def get_queryset(self):
        """Restrict scope to the company relationships."""
        queryset = super(SampleSetListView, self).get_queryset()

        if self.kwargs.get("subdivision_id"):
            sub_id = self.kwargs.get("subdivision_id")
            queryset = queryset.filter(home_statuses__home__subdivision_id=sub_id)

        # Searches against related fields can yield duplicate results, so preempt the issue.
        queryset = queryset.distinct()

        return queryset

    def get_column_unicode_data(self, obj, *args, **kwargs):
        return datatableview.helpers.link_to_model(obj, text=obj.alt_name or obj.uuid)

    def get_column_Builder_data(self, obj, *args, **kwargs):
        """Return a link to the discovered builder."""
        # This is set up in a way for speed.
        # It has been determined that MySQL performs nearly 4x slower than this code if we do
        # something like BuilderOrg.objects.filter(relationships__object_id__in=homeids)
        # where a subquery is used.
        prefix = "home_status__home__relationships__"
        result = (
            obj.samplesethomestatus_set.current()
            .values(prefix + "company", prefix + "company__name", prefix + "company__company_type")
            .distinct()
        )

        # No items in the sampleset causes problems, so abort now
        if not result:
            return ""

        result = values_to_dict(result, prefix + "company__company_type")
        result = result.get("builder")
        builder_id = result[prefix + "company"]
        builder_name = result[prefix + "company__name"]

        a_tag = """<a href="{url}">{text}</a>"""
        url = reverse("company:view", kwargs={"type": "builder", "pk": builder_id})
        return a_tag.format(url=url, text=builder_name)

    def get_column_Program_data(self, obj, *args, **kwargs):
        result = (
            obj.samplesethomestatus_set.current()
            .values("home_status__eep_program", "home_status__eep_program__name")
            .annotate(n=Count("home_status__eep_program"))
        )

        a_tag = """<a href="{url}">{text}</a>"""

        # Manual url reversal because we only have the pk, not the whole object
        get_absolute_url = lambda item: reverse(
            "eep_program:view", kwargs={"pk": item["home_status__eep_program"]}
        )
        get_name = lambda item: item["home_status__eep_program__name"]

        return "<br>".join(
            a_tag.format(url=get_absolute_url(item), text=get_name(item)) for item in result
        )

    def get_column_Test_Sampled_data(self, obj, *args, **kwargs):
        result = (
            obj.samplesethomestatus_set.current()
            .values("is_test_home")
            .annotate(n=Count("is_test_home"))
        )
        return "{True} / {False}".format(
            **dict(
                {"True": 0, "False": 0},
                **{"{}".format(item["is_test_home"]): item["n"] for item in result},
            )
        )


class SampleSetUIView(AuthenticationMixin, LegacyAxisDatatableView):
    permission_required = "sampleset.view_samplesethomestatus"

    template_name = "sampleset/control_center.html"

    model = EEPProgramHomeStatus
    datatable_options = {
        "columns": [
            (
                "Address",
                [
                    "eep_program__name",
                    "home__lot_number",
                    "home__street_line1",
                    "home__street_line2",
                ],
                "get_column_Home_data",
            ),
            ("Test House", "num_answers", datatableview.helpers.make_boolean_checkmark),
            ("Subdivision", "home__subdivision__name"),
            ("Builder", "home__relationships__company__name", "get_column_Builder_data"),
            (
                "Sample set",
                [
                    "samplesethomestatus__sampleset__alt_name",
                    "samplesethomestatus__sampleset__uuid",
                ],
                "get_column_SampleSet_data",
            ),
        ],
        "search_fields": ["id", "home__city__name", "home__state", "home__county__name"],
        "ordering": ["Address", "Sample set"],
    }

    def get_queryset(self):
        """Apply filters requested by UI."""
        # NOTE: We are avoiding select_related and prefetch_related in this situation, because the
        # number of objects in the queryset before paging is far too large to make this practical.
        # We get much better performance by letting the extra queries happen late in the row-level
        # serialization process.

        queryset = self.model.objects.filter_by_user(self.request.user)
        queryset = queryset.filter(
            eep_program__allow_sampling=True, eep_program__required_checklists__isnull=False
        )

        kwargs = self.prevision_kwargs(**self.request.GET)

        has_sampleset_filter = kwargs.get("has_sampleset")
        if has_sampleset_filter:
            # warning: don't factor this out into a Q object.  It doesn't work correctly somehow.
            if has_sampleset_filter == "0":
                queryset = queryset.annotate(
                    num_associations=Count("samplesethomestatus__id")
                ).filter(num_associations=0) | queryset.filter(samplesethomestatus__is_active=False)
            elif has_sampleset_filter == "1":
                queryset = queryset.filter(samplesethomestatus__is_active=True)

        # has_answers
        has_answers_filter = kwargs.get("has_answers")
        if has_answers_filter is not None:
            queryset = queryset.annotate(num_answers=Count("home__answer__id"))
            if has_answers_filter == "0":
                queryset = queryset.filter(num_answers=0)
            elif has_answers_filter == "1":
                queryset = queryset.filter(num_answers__gt=0)

        # uuid/alt_name filter
        if kwargs.get("name"):
            queryset = queryset.filter(
                Q(samplesethomestatus__sampleset__uuid__icontains=kwargs.get("name"))
                | Q(samplesethomestatus__sampleset__alt_name__icontains=kwargs.get("name"))
            )

        # start_date filter
        date_filter = kwargs.get("start_date")
        if date_filter:
            queryset = queryset.filter(samplesethomestatus__sampleset__start_date=date_filter)

        # program multi-filter
        if kwargs.get("eep_program"):
            eeps = (
                kwargs.get("eep_program")
                if isinstance(kwargs.get("eep_program"), list)
                else [kwargs.get("eep_program")]
            )
            log.debug("Filtering eeps: %s", eeps)
            queryset = queryset.filter(eep_program_id__in=eeps)

        # builder filter
        if kwargs.get("builder"):
            builders = (
                kwargs.get("builder")
                if isinstance(kwargs.get("builder"), list)
                else [kwargs.get("builder")]
            )
            log.debug("Filtering builder: %s", builders)
            queryset = queryset.filter(
                Q(home__relationships__company__company_type="builder"),
                Q(home__relationships__company_id__in=builders),
            )

        # subdivision multi-filter
        if kwargs.get("subdivision"):
            subs = (
                kwargs.get("subdivision")
                if isinstance(kwargs.get("subdivision"), list)
                else [kwargs.get("subdivision")]
            )
            log.debug("Filtering subdivisions: %s", subs)
            queryset = queryset.filter(home__subdivision_id__in=subs)

        # certification state
        certification_filter = kwargs.get("homestatus_state")
        if certification_filter:
            if certification_filter == "uncertified":
                queryset = queryset.filter(certification_date=None).exclude(state="complete")
            else:
                queryset = queryset.filter(state=certification_filter)

        if kwargs.get("owner"):
            owners = (
                kwargs.get("owner")
                if isinstance(kwargs.get("owner"), list)
                else [kwargs.get("owner")]
            )
            log.debug("Filtering owners: %s", owners)
            queryset = queryset.filter(company_id__in=owners)

        return queryset.distinct()

    def get_column_Test_House_data(self, obj, *args, **kwargs):
        return obj.num_answers

    def get_column_Home_data(self, obj, *args, **kwargs):
        self.is_locked = None
        try:
            payment_status = obj.incentivepaymentstatus
        except ObjectDoesNotExist:
            self.is_locked = bool(obj.certification_date)
        else:
            self.is_locked = not (
                payment_status.state in ["start", "ipp_payment_failed_requirements"]
            )

        text = obj.home.get_home_address_display(company=self.request.company)
        address_line = [
            datatableview.helpers.link_to_model(obj, text=text),
        ]

        if self.is_locked:
            address_line.insert(0, """<i class="fa fa-fw fa-lock"></i> """)

        if obj.certification_date:
            address_line.insert(0, """<i class="fa fa-fw fa-certificate"></i> """)

        return "<br />".join(
            [
                " ".join(address_line),
                """<span class="text-muted">{} ({})</span>""".format(
                    obj.eep_program.name,
                    obj.state_description,
                ),
            ]
        )

    @staticmethod
    def _make_sampling_ui_link(item):
        """Generates the link the UI will hook for opening a sampleset."""
        button = """
        <div class="btn-group" data-is_locked="true">
            <a role="button" data-sample_set_id="{id}" class="datatable-sampleset btn btn-default btn-sm" title="Open in editor">{text}</a>
            <a href="{url}" class="btn btn-default btn-sm" target="_blank" title="View full details"><i class="fa fa-external-link"></i></a>
        </div>
        """
        _url = item.sampleset.get_absolute_url()
        return button.format(id=item.sampleset.id, text="{}".format(item.sampleset), url=_url)

    def get_column_SampleSet_data(self, obj, *args, **kwargs):
        items = obj.samplesethomestatus_set.select_related("sampleset").order_by("-revision")
        item = items.first()
        if item and item.revision != item.sampleset.revision:
            item = None

        if item:
            return self._make_sampling_ui_link(item)

        return """
            <div data-is_locked="{locked}">
                No Sample Set
            </div>
        """.format(
            **{
                "locked": ("true" if self.is_locked else "false"),
            }
        )

    def get_column_Builder_data(self, obj, *args, **kwargs):
        return "{}".format(obj.home.get_builder())

    def get_context_data(self, **kwargs):
        context = super(SampleSetUIView, self).get_context_data(**kwargs)
        context["initial_ids"] = list(filter_integers(self.request.GET.getlist("id")))
        context["query_form"] = HomeQueryForm(self.request.user)
        return context


class SampleSetDetailView(AuthenticationMixin, AxisDetailView):
    permission_required = "sampleset.view_sampleset"
    show_delete_button = False

    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_queryset(self):
        return SampleSet.objects.filter_by_user(user=self.request.user).distinct()

    def get_edit_url(self):
        return reverse("sampleset:control_center") + "?id={id}".format(id=self.object.id)

    def get_context_data(self, **kwargs):
        context = super(SampleSetDetailView, self).get_context_data(**kwargs)

        context["sample_type"] = "subdivision"
        if self.object.is_metro_sampled:
            context["sample_type"] = "metro"
        context["confirm_eligible"] = False

        has_certification_permission = self.object.can_be_edited(self.request.user)
        context["confirm_eligible"] = (
            self.object.can_be_certified() and has_certification_permission
        )
        context["pct_complete"] = self.object.get_completion_percentage()
        context["has_failures"] = self.object.get_current_source_failing_answers().count()
        context["failures"] = self.object.get_current_source_failing_answers(combined=True)
        ss_homes_view = SampleSetAjaxHomeProvider()
        ss_homes_view.request = self.request
        ss_homes_view.kwargs = self.kwargs
        datatable = ss_homes_view.get_datatable()
        datatable.url = reverse("sampleset:homes", kwargs={"uuid": self.object.uuid})
        context["datatable"] = datatable

        ss_answers_view = SampleSetAjaxAnswers()
        ss_answers_view.request = self.request
        ss_answers_view.kwargs = self.kwargs
        datatable = ss_answers_view.get_datatable()
        datatable.url = reverse("sampleset:answers", kwargs={"uuid": self.object.uuid})
        context["answer_datatable"] = datatable

        return context


class SampleSetAjaxHomeProvider(AuthenticationMixin, LegacyAxisDatatableView):
    permission_required = "sampleset.view_sampleset"
    show_add_button = False
    model = SampleSetHomeStatus

    datatable_options = {
        "columns": [
            (
                "Home",
                ("home_status__home__street_line1", "home_status__home__city__name"),
                "get_column_Home_data",
            ),
            ("Program", "home_status__eep_program__name", "get_column_Program_data"),
            ("Test/Sampled", "is_test_home", "get_column_Test_Sampled_data"),
            ("Certifiable", "", "get_column_Can_Certify_data"),
        ],
    }

    def get_queryset(self):
        """Restrict scope to the company relationships."""
        queryset = SampleSetHomeStatus.objects.filter(sampleset__uuid=self.kwargs["uuid"]).current()
        return queryset.distinct().order_by("-is_test_home")

    def get_column_Home_data(self, obj, *args, **kwargs):
        text = obj.home_status.home.get_home_address_display(company=self.request.company)
        return datatableview.helpers.link_to_model(obj.home_status.home, text=text)

    def get_column_Program_data(self, obj, *args, **kwargs):
        return datatableview.helpers.link_to_model(obj.home_status.eep_program)

    def get_column_Test_Sampled_data(self, obj, *args, **kwargs):
        return "Test" if obj.is_test_home else "Sampled"

    def get_column_Can_Certify_data(self, obj, *args, **kwargs):
        return datatableview.helpers.make_boolean_checkmark(
            obj.home_status.can_user_certify(self.request.user)
        )


class SampleSetAjaxAnswers(AuthenticationMixin, LegacyAxisDatatableView):
    permission_required = "sampleset.view_sampleset"
    show_add_button = False
    model = Answer

    datatable_options = {
        "columns": [
            ("Question", ("question__question"), "get_column_Question_data"),
            ("Answer", "answer", "get_column_Answer_data"),
            (
                "Home",
                ("home_status__home__street_line1", "home_status__home__city__name"),
                "get_column_Home_data",
            ),
        ],
        "result_counter_id": "answers_count",
    }

    def get_queryset(self):
        """This will return all the source answers"""
        sampleset = SampleSet.objects.get(uuid=self.kwargs["uuid"])
        return sampleset.get_test_answers()

    def get_column_Answer_data(self, obj, *args, **kwargs):
        if self.request.user.is_superuser:
            return "[{}] {}".format(obj.id, obj.answer)
        return obj.answer

    def get_column_Question_data(self, obj, *args, **kwargs):
        return obj.question

    def get_column_Home_data(self, obj, *args, **kwargs):
        text = obj.home.get_home_address_display(company=self.request.company)
        return datatableview.helpers.link_to_model(obj.home, text=text)
