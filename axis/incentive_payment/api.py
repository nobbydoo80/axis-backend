"""api.py: Incentive Payment"""


from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import now
from django.template.loader import render_to_string

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_states.exceptions import TransitionCannotStart

from axis.annotation.models import Type, Annotation
from axis.builder_agreement.models import BuilderAgreement
from axis.company.models import Company
from .models import IncentiveDistribution, IPPItem, IncentivePaymentStatus
from .forms import (
    IncentiveDistributionForm,
    IncentivePaymentStatusUndoForm,
    IncentivePaymentStatusAnnotationForm,
    IncentivePaymentStatusRevertForm,
)
from .views import IncentivePaymentPendingDatatable, IncentiveDistributionDatatable
from . import strings

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class IPPItemSerializer(serializers.ModelSerializer):
    home_status = serializers.HyperlinkedRelatedField(
        view_name="apiv2:home_status-detail", read_only=True
    )
    incentive_distribution = serializers.HyperlinkedRelatedField(
        view_name="apiv2:incentive_distribution-detail", read_only=True
    )

    class Meta:
        model = IPPItem
        fields = "__all__"


class IncentivePaymentStatusSerializer(serializers.ModelSerializer):
    home_status = serializers.HyperlinkedRelatedField(
        view_name="apiv2:home_status-detail", read_only=True
    )

    class Meta:
        model = IncentivePaymentStatus
        fields = ("id", "created_on", "home_status", "last_update", "state")


class IncentiveDistributionSerializer(serializers.ModelSerializer):
    ipp_items = IPPItemSerializer(many=True, source="ippitem_set")
    company = serializers.HyperlinkedRelatedField(view_name="apiv2:company-detail", read_only=True)
    customer = serializers.HyperlinkedRelatedField(view_name="apiv2:company-detail", read_only=True)

    class Meta:
        model = IncentiveDistribution
        exclude = ("rater_incentives",)


class IncentivePaymentStatusViewSet(viewsets.ReadOnlyModelViewSet):
    model = IncentivePaymentStatus
    queryset = model.objects.all()
    serializer_class = IncentivePaymentStatusSerializer
    throttle_scope = "ipp"

    @action(detail=True)
    def full_status(self, request, pk=None, *args, **kwargs):
        """Fetches a data structure that represent the incentive status's progress status."""
        obj = self.get_object()
        return Response(obj.get_full_status(user=self.request.user))


class IncentiveDistributionViewSet(viewsets.ReadOnlyModelViewSet):
    model = IncentiveDistribution
    queryset = model.objects.all()
    serializer_class = IncentiveDistributionSerializer


class IPPItemViewSet(viewsets.ReadOnlyModelViewSet):
    model = IPPItem
    queryset = model.objects.all()
    serializer_class = IPPItemSerializer


class PendingFormMixin(object):
    def get_pending_form(self, *args, **kwargs):
        form = IncentivePaymentStatusAnnotationForm(*args, **kwargs)

        qs = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        id_list = qs.values_list("id", flat=True)

        form.fields["stats"].choices = [(x, x) for x in id_list]

        return form

    def handle_pending_form(self, form):
        info, success, error = {}, {}, {}
        if form.is_valid():
            new_state = form.cleaned_data["new_state"]
            annotation = form.cleaned_data["annotation"]
            stat_ids = [int(x) for x in form.cleaned_data["stats"]]
            stats = IncentivePaymentStatus.objects.filter(id__in=stat_ids)
            old_state = stats[0].state

            for stat in stats:
                url = stat.home_status.home.get_absolute_url()
                home_href = """<a target="_blank" href="{url}">{home}</a>""".format(
                    url=url, home=stat.home_status.home
                )

                if new_state not in [None, "", "undefined"]:
                    try:
                        stat.make_transition(
                            self.state_transitions[new_state], user=self.request.user
                        )
                    except TransitionCannotStart:
                        states = dict(IncentivePaymentStatus.get_state_choices())
                        to_state = states.get(new_state)
                        info["id"] = stat.id
                        info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                            ostate=stat.get_state_display(), tstate=to_state
                        )
                        info["url"] = home_href
                    else:
                        success["id"] = stat.id
                        success["url"] = home_href

                        # print(new_state, stat.id)
                        #
                        if new_state == "ipp_payment_failed_requirements":
                            IncentivePaymentStatus.objects.send_notification_failure_message(
                                self.request.user.company, id__in=stat_ids
                            )

                            success["undo"] = {"old_state": old_state}

                        elif new_state == "resubmit-failed":
                            IncentivePaymentStatus.objects.send_notification_corrected_message(
                                self.request.user.company, id__in=stat_ids
                            )

                        elif new_state == "ipp_payment_requirements":
                            IncentivePaymentStatus.objects.send_notification_approved_message(
                                self.request.user.company, id__in=stat_ids
                            )

                        if annotation not in [None, "", "undefined"]:
                            temp_s, temp_i, temp_e = self.create_annotation(stat, annotation)
                            success.update(temp_s)
                            info.update(temp_i)
                            error.update(temp_e)

        else:
            error = form.errors

        response = self.make_response(success, info, error)

        return response


class NewBuilderAgreementFormMixin(object):
    def get_new_form(self, *args, **kwargs):
        """Setup up a form for making a new Incentive Distribution"""
        form = IncentiveDistributionForm(*args, **kwargs)

        qs = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        qs = qs.filter(state="ipp_payment_automatic_requirements")
        id_list = qs.values_list("id", flat=True)

        _builders = IncentivePaymentStatus.objects.choice_builder_items_for_user(
            user=self.request.user, id__in=id_list
        )
        customers = Company.objects.filter(id__in=[x[0] for x in _builders])

        form.fields["stats"].choices = [(x, x) for x in id_list]
        form.fields["customer"].queryset = customers
        form.fields["customer"].required = False
        form.fields["check_requested_date"].initial = now().strftime("%Y-%m-%d")

        return form

    def handle_new_form(self, form):
        success, info, error = {}, {}, {}
        raters = []
        tracker = []

        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.total = 0
            self.object.company = self.request.user.company
            self.object.check_to_name = self.object.customer.name
            self.object.check_requested = True
            self.object.status = 1
            self.object.save()

            stats_ids = [int(x) for x in form.cleaned_data["stats"]]
            stats = IncentivePaymentStatus.objects.filter(id__in=stats_ids)

            raters, tracker, success, info, error = self.process_builder_agreement_stats(
                stats, raters, tracker, success, info, error
            )

            self.object.total = self.object.total_cost()
            self.object.save()

            if not self.object.rater_incentives.exists():
                self.process_builder_agreement_raters(form, stats, raters)

            self.object.save()

            builder_breakdown = self.process_builder_agreement_builder_breakdown(tracker)

            msg = "Successfully created <a target='_blank' href='{url}'>{text}</a>"
            messages = [msg.format(url=self.object.get_absolute_url(), text=self.object)]
            for incentive in self.object.rater_incentives.all():
                messages.append(msg.format(url=incentive.get_absolute_url(), text=incentive))

            success.update(
                {
                    "id": self.object.id,
                    "url": " <br> ".join(messages),
                    "builder_breakdown": builder_breakdown,
                }
            )
        else:
            error = form.errors

        response = self.make_response(success, info, error)

        return response

    def process_builder_agreement_stats(self, stats, raters, tracker, success, info, error):
        for stat in stats:
            home_stat = stat.home_status
            price = self.get_builder_agreement_price(home_stat)
            IPPItem.objects.create(
                home_status=home_stat, cost=price, incentive_distribution=self.object
            )

            if home_stat.company not in raters and home_stat.get_rater_incentive() > 0:
                raters.append(home_stat.company)

            try:
                stat.make_transition("pending_payment_requirements", user=self.request.user)
            except TransitionCannotStart:
                # TODO: put an error messages here.
                pass

            tracker.append({"stat": home_stat, "price": price})

        return raters, tracker, success, info, error

    def process_builder_agreement_raters(self, form, stats, raters):
        data = form.cleaned_data.copy()
        del data["stats"]
        del data["rater_incentives"]

        for rater in raters:
            data.update(
                {
                    "customer": rater,
                    "check_to_name": rater.name,
                    "company": self.request.user.company,
                    "check_requested": True,
                    "status": 1,
                    "total": 0,
                }
            )
            rater_object = IncentiveDistribution.objects.create(**data)
            # rater_object.save()

            for stat in stats:
                home_stat = stat.home_status
                price = home_stat.get_rater_incentive()
                if home_stat.company != rater:
                    continue
                if price < 0.01:
                    continue
                IPPItem.objects.create(
                    home_status=home_stat, cost=price, incentive_distribution=rater_object
                )

            rater_object.total = rater_object.total_cost()
            rater_object.save()
            self.object.rater_incentives.add(rater_object)

    def process_builder_agreement_builder_breakdown(self, tracker):
        programs = {}
        raters = {}
        total_dollars = 0

        for col in tracker:
            price = col["price"]
            total_dollars += price
            stat = col["stat"]
            rater = "{}".format(stat.company)
            program = "{}".format(stat.eep_program)

            if program in programs.keys():
                programs[program]["count"] += 1
                programs[program]["amount"] += price
            else:
                programs[program] = {"name": program, "count": 1, "amount": price}

            try:
                rater_incentive = self.object.rater_incentives.get(customer=stat.company)
            except self.object.rater_incentives.model.DoesNotExist:
                rater_check_request = None
                rater_check_detail = None
            else:
                rater_check_request = reverse(
                    "incentive_payment:print", kwargs={"pk": rater_incentive.id}
                )
                rater_check_detail = reverse(
                    "incentive_payment:print_detail", kwargs={"pk": rater_incentive.id}
                )

            if rater in raters:
                raters[rater]["count"] += 1
                raters[rater]["amount"] += stat.get_rater_incentive()
                raters[rater]["check_request_url"] = rater_check_request
                raters[rater]["check_detail_url"] = rater_check_detail
            else:
                raters[rater] = {
                    "name": rater,
                    "count": 1,
                    "amount": stat.get_rater_incentive(),
                    "check_request_url": rater_check_request,
                    "check_detail_url": rater_check_detail,
                }

        programs = [x for x in programs.values()]
        raters = [x for x in raters.values()]

        builder_breakdown = {
            "check_request_url": reverse("incentive_payment:print", kwargs={"pk": self.object.id}),
            "check_detail_url": reverse(
                "incentive_payment:print_detail", kwargs={"pk": self.object.id}
            ),
            "total_incentives": len(tracker),
            "total_amount": total_dollars,
            "programs": programs,
            "raters": raters,
        }

        return builder_breakdown

    def get_builder_agreement_price(self, home_stat):
        price = home_stat.get_builder_incentive()
        if home_stat.eep_program.per_point_adder:
            floorplan = home_stat.floorplan
            hers = 0
            if hasattr(floorplan, "remrate_target") and hasattr(
                floorplan.remrate_target, "energystar"
            ):
                hers = int(floorplan.get_hers_score_for_program(home_stat.eep_program))
                hers = int(home_stat.eep_program.min_hers_score) - hers
                if hers < 0:
                    hers = 0
            price += hers * home_stat.eep_program.per_point_adder

        return price


class AnnotateFormMixin(object):
    def get_annotate_form(self, *args, **kwargs):
        form = self.get_pending_form(*args, **kwargs)
        form.fields["annotation"].required = True
        return form

    def handle_annotate_form(self, form):
        success, info, error = {}, {}, {}
        if form.is_valid():
            annotation = form.cleaned_data["annotation"]
            stats = [int(x) for x in form.cleaned_data["stats"]]
            stats = IncentivePaymentStatus.objects.filter(id__in=stats)
            if not annotation:
                pass

            for stat in stats:
                temp_s, temp_i, temp_e = self.create_annotation(stat, annotation)
                success.update(temp_s)
                info.update(temp_i)
                error.update(temp_e)
        else:
            error = form.errors

        response = self.make_response(success, info, error)

        return response


class RevertFormMixin(object):
    def get_revert_form(self, *args, **kwargs):
        form = IncentivePaymentStatusRevertForm(*args, **kwargs)

        qs = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        id_list = qs.values_list("id", flat=True)

        form.fields["stats"].choices = [(x, x) for x in id_list]

        return form

    def handle_revert_form(self, form):
        success, info, error = {}, {}, {}
        if form.is_valid():
            stat_ids = [int(x) for x in form.cleaned_data["stats"]]
            stats = IncentivePaymentStatus.objects.filter(id__in=stat_ids)

            for stat in stats:
                home_href = """<a href='{}'>{}</a>""".format(
                    stat.home_status.home.get_absolute_url(), stat.home_status.home
                )

                if stat.state == "payment_pending":
                    try:
                        stat.make_transition("distribution_delete_reset")
                    except TransitionCannotStart:
                        info["id"] = stat.id
                        info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                            ostate=stat.get_state_display(), tstate="Approved for Payment"
                        )
                        info["url"] = home_href

                try:
                    stat.make_transition("reset_prior_approved")
                except TransitionCannotStart:
                    info["id"] = stat.id
                    info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                        ostate=stat.get_state_display(), tstate="Received"
                    )
                    info["url"] = home_href
                else:
                    stat.save()
                    success["id"] = stat.id
                    success["url"] = home_href
                    temp_s, temp_i, temp_e = self.create_annotation(
                        stat, form.cleaned_data["annotation"]
                    )
                    success.update(temp_s)
                    info.update(temp_i)
                    error.update(temp_e)

        else:
            error = form.errors

        response = self.make_response(success, info, error)

        return response


class UndoFormMixin(object):
    def get_undo_form(self, *args, **kwargs):
        form = IncentivePaymentStatusUndoForm(*args, **kwargs)

        qs = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        id_list = qs.values_list("id", flat=True)

        form.fields["stats"].choices = [(x, x) for x in id_list]

        return form

    def handle_undo_form(self, form):
        success, info, error = {}, {}, {}
        if form.is_valid():
            stat_ids = [int(x) for x in form.cleaned_data["stats"]]
            stats = IncentivePaymentStatus.objects.filter(id__in=stat_ids)

            old_state = form.cleaned_data["old_state"]

            for stat in stats:
                home_href = '<a href="{}">{}</a>'.format(
                    stat.home_status.home.get_absolute_url(), stat.home_status.home
                )
                check = "from_{}".format(old_state)
                for tran in stat.possible_transitions:
                    if check in tran.get_name():
                        transition = tran.get_name()
                        break

                try:
                    stat.make_transition(transition)
                except TransitionCannotStart:
                    info["id"] = stat.id
                    info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                        ostate=stat.get_state_display(), tstate=old_state
                    )
                    info["url"] = home_href
                else:
                    stat.save()
                    success["id"] = stat.id
                    success["url"] = home_href
                    temp_s, temp_i, temp_e = self.create_annotation(
                        stat, form.cleaned_data["annotation"]
                    )
                    success.update(temp_s)
                    info.update(temp_i)
                    error.update(temp_e)

        else:
            error = form.errors

        return self.make_response(success, info, error)


class IncentivePaymentControlCenterEndpoint(
    viewsets.ViewSet,
    PendingFormMixin,
    UndoFormMixin,
    NewBuilderAgreementFormMixin,
    AnnotateFormMixin,
    RevertFormMixin,
):
    throttle_classes = ()

    table_views = {
        "pending": IncentivePaymentPendingDatatable,
        "received": IncentivePaymentPendingDatatable,
        "required": IncentivePaymentPendingDatatable,
        "approved": IncentivePaymentPendingDatatable,
        "distribution": IncentiveDistributionDatatable,
    }

    form_templates = {
        "new": "incentive_payment/control_center/new_form.html",
        "pending": "incentive_payment/control_center/pending_form.html",
    }

    state_transitions = {
        "ipp_payment_requirements": "pending_requirements",
        "ipp_payment_failed_requirements": "failed_requirements",
        "resubmit-failed": "corrected_requirements",
        "payment_pending": "pending_requirements",
        "ipp_failed_restart": "corrected_requirements",
        "start": "reset_prior_approved",
    }

    def __init__(self):
        super(IncentivePaymentControlCenterEndpoint, self).__init__()
        self.form_handling = {
            "pending": (self.get_pending_form, self.handle_pending_form),
            "new": (self.get_new_form, self.handle_new_form),
            "annotate": (self.get_annotate_form, self.handle_annotate_form),
            "revert": (self.get_revert_form, self.handle_revert_form),
            "undo": (self.get_undo_form, self.handle_undo_form),
        }

    # ACTIONS
    def get_datatable(self, request, *args, **kwargs):
        """
        This method passes a view a response in hopes that it will be nice enough to let us
        get a datatable skeleton back.
        """
        table_class = kwargs["datatable"].lower()
        if table_class not in self.table_views.keys():
            return Response(
                {"error": "table does not exist"}, status=400, content_type="application/json"
            )

        view = self.table_views[table_class](request=request)

        datatable = view.get_datatable()
        datatable.configure()  # DT doesn't come to us configured due to plucking it from other view

        if self.request.query_params:
            return view.get_ajax(self.request)

        if table_class == "pending":
            datatable.config["result_counter_id"] = "pending_count"
        elif table_class == "review":
            datatable.config["result_counter_id"] = "correction_count"
        elif table_class == "new":
            datatable.config["result_counter_id"] = "approved_count"
        elif table_class == "distribution":
            datatable.config["result_counter_id"] = "incentive_distribution_count"

        return Response("{}".format(datatable), content_type="application/json")

    def get_form(self, request, *args, **kwargs):
        form_class = kwargs.pop("form").lower()
        if form_class not in self.form_handling.keys():
            return Response({"error": "form does not exist"}, status=400)

        get_form, _ = self.form_handling[form_class]
        form = get_form(*args, **kwargs)

        form.action = reverse("apiv2:ipp-form", kwargs={"form": form_class})

        data = {"form": form}
        temp = render_to_string(self.form_templates[form_class], data)
        return Response("{}".format(temp), content_type="application_json")

    def get_form_class(self, *args, **kwargs):
        form_class = kwargs["form"]
        submit = self.request.POST.get("submit", "").lower()

        if submit == "annotate":
            form_class = "annotate"
        elif submit == "revert":
            form_class = "revert"
        elif submit == "undo":
            form_class = "undo"

        return form_class

    def advance_state(self, request, *args, **kwargs):
        form_class = self.get_form_class(*args, **kwargs)

        get_form, handle_form = self.form_handling[form_class]
        form = get_form(data=self.request.data)
        response = handle_form(form)

        return Response(response, content_type="application/json")

    # ===============================================================================================

    def old_advance_state(self, request, *args, **kwargs):
        form_class = kwargs["form"]

        if form_class == "pending" or self.request.POST.get("submit").lower() == "annotate":
            form = self._setup_pending_form(data=self.request.data)
            response = self._pending_form_is_valid(form)
        elif form_class == "new":
            form = self._setup_new_builer_agreement_form(data=self.request.data)
            response = self._new_buidler_agreement_form_is_valid(form)

        return response

    # HELPER METHODS
    def _setup_pending_form(self, *args, **kwargs):
        form = IncentivePaymentStatusAnnotationForm(*args, **kwargs)

        queryset = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        id_list = queryset.values_list("id", flat=True)

        form.fields["stats"].choices = [(x, x) for x in id_list]

        return form

    def _setup_new_builer_agreement_form(self, *args, **kwargs):
        form = IncentiveDistributionForm(*args, **kwargs)

        stats_qs = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        stats_qs = stats_qs.filter(state="ipp_payment_automatic_requirements")
        id_list = stats_qs.values_list("id", flat=True)
        form.fields["stats"].choices = [(x, x) for x in id_list]

        _builders = IncentivePaymentStatus.objects.choice_builder_items_for_user(
            user=self.request.user, id__in=id_list
        )
        customers = Company.objects.filter(id__in=[x[0] for x in _builders])
        form.fields["customer"].queryset = customers

        form.fields["check_requested_date"].initial = now().strftime("%Y-%m-%d")

        if self.request.POST.get("submit") == "revert":
            form.fields["customer"].required = False

        return form

    def _setup_revert_form(self, *args, **kwargs):
        form = IncentivePaymentStatusRevertForm(*args, **kwargs)
        stats_qs = IncentivePaymentStatus.objects.filter_by_user(self.request.user)
        stats_qs = stats_qs.filter(state="ipp_payment_automatic_requirements")
        id_list = stats_qs.values_list("id", flat=True)
        form.fields["stats"].choices = [(x, x) for x in id_list]

        return form

    def _validate_new_builder_agreement_form(self, form):
        response, info, success, error = {}, {}, {}, {}
        cleaned_data = form.cleaned_data
        stats = [int(x) for x in cleaned_data["stats"]]
        for stat in stats:
            ipp_stat = IncentivePaymentStatus.objects.get(id=stat)
            url = ipp_stat.home_status.home.get_absolute_url()
            home_href = "<a href='{url}'>{home}</a>".format(url=url, home=ipp_stat.home_status.home)
            info.update({"id": ipp_stat.id, "url": home_href})
            response["info"] = info
        return Response(response, content_type="application/json")

    def _save_builder_agreement(self, form):
        response, info, success, error = {}, {}, {}, {}
        self.object = form.save(commit=False)
        self.object.total = 0
        self.object.company = self.request.user.company
        self.object.check_to_name = self.object.customer.name
        self.object.check_requested = True
        self.object.status = 1
        self.object.save()
        raters = []
        stat_ids = [int(x) for x in form.cleaned_data.get("stats", [])]
        ipp_stats = IncentivePaymentStatus.objects.filter(id__in=stat_ids)

        tracker = []

        for ipp_stat in ipp_stats:
            home_stat = ipp_stat.home_status
            price = home_stat.get_builder_incentive()
            if home_stat.eep_program.per_point_adder:
                floorplan = home_stat.floorplan
                hers = 0
                if hasattr(floorplan, "remrate_target") and hasattr(
                    floorplan.remrate_target, "energystar"
                ):
                    hers = int(floorplan.get_hers_score_for_program(home_stat.eep_program))
                    hers = int(home_stat.eep_program.min_hers_score) - hers
                    if hers < 0:
                        hers = 0
                price += hers * home_stat.eep_program.per_point_adder
            IPPItem.objects.create(
                home_status=home_stat, cost=price, incentive_distribution=self.object
            )
            if home_stat.company not in raters and home_stat.get_rater_incentive() > 0:
                raters.append(home_stat.company)
            tracker.append({"stat": home_stat, "price": price, "rater": home_stat.company})
            ipp_stat.make_transition("pending_payment_requirements", user=self.request.user)
        self.object.total = self.object.total_cost()
        self.object.save()
        if not self.object.rater_incentives.exists():
            data = form.cleaned_data.copy()
            del data["stats"]
            del data["rater_incentives"]
            for rater in raters:
                data.update(
                    {
                        "customer": rater,
                        "check_to_name": rater.name,
                        "company": self.request.user.company,
                        "check_requested": True,
                        "status": 1,
                        "total": 0,
                    }
                )
                rater_object = IncentiveDistribution.objects.create(**data)
                rater_object.save()
                for ipp_stat in ipp_stats.all():
                    home_stat = ipp_stat.home_status
                    if home_stat.company != rater:
                        continue
                    if home_stat.get_rater_incentive() < 0.01:
                        continue
                    IPPItem.objects.create(
                        home_status=home_stat,
                        cost=home_stat.get_rater_incentive(),
                        incentive_distribution=rater_object,
                    )
                rater_object.total = rater_object.total_cost()
                rater_object.save()
                self.object.rater_incentives.add(rater_object)
        self.object.save()
        msg = "Successfully created <a href='{}'>{}</a>"

        programs = {}
        stat_raters = {}
        total_incentives = len(tracker)
        total_amount = 0

        for col in tracker:
            price = col["price"]
            total_amount += price
            stat = col["stat"]
            rater = "{}".format(col["rater"])
            program = "{}".format(stat.eep_program)

            if program in programs.keys():
                programs[program]["count"] += 1
                programs[program]["amount"] += price
            else:
                programs[program] = {"name": program, "count": 1, "amount": price}

            if rater in stat_raters.keys():
                stat_raters[rater]["count"] += 1
                stat_raters[rater]["amount"] += price
            else:
                stat_raters[rater] = {"name": rater, "count": 1, "amount": price}

        programs = [x for x in programs.values()]
        raters = [x for x in stat_raters.values()]

        response.update(
            {
                "success": {
                    "id": self.object.id,
                    "url": msg.format(self.object.get_absolute_url(), self.object),
                    "builder_breakdown": {
                        "check_request_url": reverse(
                            "incentive_payment:print", kwargs={"pk": self.object.id}
                        ),
                        "check_detail_url": reverse(
                            "incentive_payment:print_detail", kwargs={"pk": self.object.id}
                        ),
                        "total_incentives": total_incentives,
                        "total_amount": total_amount,
                        "programs": programs,
                        "raters": raters,
                        # TODO: track homes belonging to which raters.
                        # TODO: track homes belonging to which programs.
                        # 'raters': [
                        #     {
                        #         'name': 'NAME',
                        #         'count': "number of homes",
                        #         'amount': 'dollars involved'
                        #     }
                        # ],
                        # 'programs': [
                        #     {
                        #         'name': "NAME",
                        #         'count': 'number of homes',
                        #         'amount': 'dollars involved'
                        #     }
                        # ]
                    },
                }
            }
        )
        return Response(response, content_type="application/json")

    def _new_buidler_agreement_form_is_valid(self, form):
        if form.is_valid():
            if self.request.POST.get("validate") and self.request.POST["validate"] == "true":
                response = self._validate_new_builder_agreement_form(form)
            elif self.request.POST.get("submit").lower() == "revert":
                response = self._revert_stat(form)
            else:
                response = self._save_builder_agreement(form)

        else:
            response = {"error": form.errors}
            response = Response(response, content_type="application/json")

        return response

    def _pending_form_is_valid(self, form):
        response, info, success, error = {}, {}, {}, {}
        if form.is_valid():
            cleaned_data = form.cleaned_data
            new_state = cleaned_data["new_state"]
            stats = [int(x) for x in cleaned_data["stats"]]

            for stat in stats:
                ipp_stat = IncentivePaymentStatus.objects.get(id=stat)

                url = ipp_stat.home_status.home.get_absolute_url()
                home_href = "<a href='{url}'>{home}</a>".format(
                    url=url, home=ipp_stat.home_status.home
                )

                if new_state not in [None, ""]:
                    try:
                        ipp_stat.make_transition(
                            self.state_transitions[new_state], user=self.request.user
                        )
                    except TransitionCannotStart:
                        states = dict(IncentivePaymentStatus.get_state_choices())
                        to_state = states.get(new_state)
                        # insert msg here?
                        info["id"] = ipp_stat.id
                        info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                            ostate=ipp_stat.get_state_display(), tstate=to_state
                        )
                        info["url"] = home_href
                    else:
                        success["id"] = ipp_stat.id
                        success["url"] = home_href

                if cleaned_data["annotation"]:
                    note_slug = "{}-ipp-status-note".format(ipp_stat.owner.slug)
                    content_type = ContentType.objects.get_for_model(ipp_stat)
                    a_type, _ = Type.objects.get_or_create(
                        slug=note_slug, defaults=dict(name=note_slug)
                    )
                    Annotation.objects.create(
                        type=a_type,
                        content=cleaned_data["annotation"],
                        content_type=content_type,
                        object_id=ipp_stat.id,
                        user=self.request.user,
                    )
                    success["annotation"] = cleaned_data["annotation"]
                    success["annotation_url"] = home_href

            if new_state in ["ipp_payment_failed_requirements"]:
                IncentivePaymentStatus.objects.send_notification_failure_message(
                    self.request.user.company, id__in=stats
                )
            if new_state in ["resubmit-failed"]:
                IncentivePaymentStatus.objects.send_notification_corrected_message(
                    self.request.user.company, id__in=stats
                )
        else:
            error = form.errors

        if len(success):
            response["success"] = success
        if len(info):
            response["info"] = info
        if len(error):
            response["error"] = error

        response["progress"] = self.request.POST["progress"]

        return Response(response, content_type="application/json")

    def _revert_stat(self, form):
        stat_ids = [int(x) for x in form.cleaned_data.get("stats", [])]
        ipp_stats = IncentivePaymentStatus.objects.filter(id__in=stat_ids)
        response, success, info = {}, {}, {}
        for stat in ipp_stats:
            home_href = """<a href='{}'>{}</a>""".format(
                stat.home_status.home.get_absolute_url(), stat.home_status.home
            )
            if stat.state == "payment_pending":
                try:
                    stat.make_transition("distribution_delete_reset")
                except TransitionCannotStart:
                    info["id"] = stat.id
                    info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                        ostate=stat.get_state_display(), tstate="Approved for Payment"
                    )
                    info["url"] = home_href

            try:
                stat.make_transition("reset_prior_approved")
            except TransitionCannotStart:
                info["id"] = stat.id
                info["message"] = strings.UNABLE_TO_TRANSITION_HOME_NO_HOME.format(
                    ostate=stat.get_state_display(), tstate="Received"
                )
                info["url"] = home_href
            else:
                stat.save()

                success["id"] = stat.id
                success["url"] = home_href

        if len(success):
            response["success"] = success
        if len(info):
            response["info"] = info

        return Response(response, content_type="application/json")

    # HELPER METHODS

    def make_response(self, success, info, error):
        response = {}
        if len(success):
            response["success"] = success
        if len(info):
            response["info"] = info
        if len(error):
            response["error"] = error

        return response

    def _create_annotation(self, stat, annotation_string):
        note_slug = "{}-ipp-status-note".format(stat.owner.slug)
        content_type = ContentType.objects.get_for_model(stat)
        a_type, _ = Type.objects.get_or_create(slug=note_slug, defaults=dict(name=note_slug))
        anno = {
            "type": a_type,
            "content": annotation_string,
            "content_type": content_type,
            "object_id": stat.id,
            "user": self.request.user,
        }
        annotation = Annotation.objects.create(**anno)

        return annotation

    def create_annotation(self, stat, annotation):
        success, info, error = {}, {}, {}
        home = stat.home_status.home
        home_href = """<a href="{url}">{home}</a>""".format(url=home.get_absolute_url(), home=home)
        try:
            annotation = self._create_annotation(stat, annotation)
        except:
            info["id"] = stat.id
            info["message"] = "Annotation could not be added"
            info["url"] = home_href
        else:
            success["id"] = stat.id
            success["url"] = home_href
            success["annotation"] = annotation.content

        return success, info, error
