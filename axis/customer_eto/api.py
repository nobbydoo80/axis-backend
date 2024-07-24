"""api.py: customer_eto api"""


from analytics.api import AnalyticsViewSet
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.authentication import TokenAuthentication

from axis.core.permissions import AxisModelPermissions
from axis.examine.api.restframework import ExamineViewSetAPIMixin
from axis.incentive_payment.models import IncentiveDistribution, IncentivePaymentStatus
from .api_v3.serializers.analytics.home_analysis import get_flat_analytic_rollup_results
from .api_v3.serializers.analytics.washington_code_credit import (
    WashingtonCodeCreditAnalyticRollupSerializer,
)
from .api_v3.serializers.analytics.eto_2022 import (
    ETO2022AnalyticRollupSerializer,
)

from .models import ETOAccount, FastTrackSubmission
from .serializers import (
    FastTrackSubmissionSerializer,
    ETOAccountSerializer,
    ETO2019AnalyticRollupSerializer,
)

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

from .serializers.analytics import (
    ETO2020AnalyticRollupSerializer,
    ETO2021AnalyticRollupSerializer,
)


class FastTrackSubmissionViewSet(viewsets.ModelViewSet):
    model = FastTrackSubmission
    queryset = model.objects.select_related("home_status__home")

    authentication_classes = (TokenAuthentication,)
    permission_classes = [AxisModelPermissions]
    serializer_class = FastTrackSubmissionSerializer
    lookup_field = "project_id"

    def get_object(self):
        if "project_ids" in self.request.data:
            project_ids = self.request.data["project_ids"]
        elif "project_id" in self.request.data:
            project_ids = [self.request.data["project_id"]]
        else:
            project_ids = [self.kwargs["project_id"]]

        self._instances = FastTrackSubmission.objects.filter(project_id__in=project_ids)
        instance = self._instances.first()
        if not instance:
            raise NotFound("No submissions tracked by the provided project ids.")
        return instance

    def get_customer(self):
        # Look up the designated customer so that we can find the IncentiveDistribution with the
        # matching check number.
        try:
            eto_account = ETOAccount.objects.get(account_number=self.request.data["account_number"])
        except ETOAccount.DoesNotExist:
            raise NotFound("The provided account number does not correspond to a company in Axis.")
        except ETOAccount.MultipleObjectsReturned:
            # Outlandish scenario where we have duplicate companies in the system that should be
            # consolidated, and share the same ETOAccount number
            ids = ETOAccount.objects.filter(
                account_number=self.request.data["account_number"]
            ).values_list("company_id", flat=True)
            raise NotFound(
                "The provided account number is assigned to duplicate company entries "
                "in Axis.  Please contact an administrator to have these companies "
                "consolidated to remove the ambiguity: %s" % (", ".join(list(map(str, ids))))
            )
        else:
            customer = eto_account.company
        return customer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        customer = self.get_customer()
        company = request.user.company

        # Ensure the IncentiveDistribution exists
        DISTRIBUTION_FIELDS = ("status", "paid_date", "check_number")
        check_info = {k: request.data.get(k) for k in DISTRIBUTION_FIELDS}
        check_info.setdefault("check_number", "eto_project_%s" % kwargs["project_id"])

        try:
            request_date = IncentivePaymentStatus.objects.get(
                home_status=instance.home_status, owner=customer
            ).created_on
        except IncentivePaymentStatus.DoesNotExist:
            request_date = list(instance.history.filter(id=instance.id))[-1].history_date

        check_info["check_requested"] = True
        check_info["check_requested_date"] = request_date
        check_info["check_to_name"] = customer.name
        check_info["is_paid"] = True

        choices = dict(map(reversed, IncentiveDistribution._meta.get_field("status").choices))
        check_info["status"] = choices.get(check_info["status"])

        check_info["total"] = instance.rater_incentive
        if customer.company_type == "builder":
            check_info["total"] = instance.builder_incentive

        distribution, created = IncentiveDistribution.objects.get_or_create(
            company=company,
            customer=customer,
            check_number=check_info["check_number"],
            defaults=check_info,
        )

        # Make sure distribution details are current
        for k, v in check_info.items():
            setattr(distribution, k, v)
        distribution.save()

        # Ensure the IPPItem(s) exist for each Submission
        for idx, obj in enumerate(self._instances):
            home_status = obj.home_status
            cost = check_info["total"] if not idx else "0.00"
            ipp_info = {"cost": cost}
            home_status.ippitem_set.get_or_create(
                incentive_distribution=distribution, defaults=ipp_info
            )

        if not created:
            distribution.total = distribution.total_cost()
            distribution.save()

        return Response(self.get_serializer(instance).data)


class ETOAccountViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    model = ETOAccount
    queryset = model.objects.all()

    serializer_class = ETOAccountSerializer

    def get_examine_machinery_class(self):
        from .views.examine import ETOAccountExamineMachinery

        return ETOAccountExamineMachinery

    def get_serializer_context(self):
        context = super(ETOAccountViewSet, self).get_serializer_context()
        context["company_type"] = self.request.query_params["company_type"]
        return context


class ETO2019AnalyticsViewSet(AnalyticsViewSet):
    """ETO 209 Analytics model"""

    serializer_class = ETO2019AnalyticRollupSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        """Get our Machinery Class"""
        from .views.examine import ETOAnalyticsRollupMachinery

        return ETOAnalyticsRollupMachinery


class ETO2020AnalyticsViewSet(AnalyticsViewSet):
    """ETO 2020 Analytics model"""

    serializer_class = ETO2020AnalyticRollupSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        """Get our Machinery Class"""
        from .views.examine import ETOAnalyticsRollupMachinery

        return ETOAnalyticsRollupMachinery


class ETO2021AnalyticsViewSet(AnalyticsViewSet):
    """ETO 2021 Analytics model"""

    serializer_class = ETO2021AnalyticRollupSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        """Get our Machinery Class"""
        from .views.examine import ETOAnalyticsRollupMachinery

        return ETOAnalyticsRollupMachinery


class WashingtonCodeCreditAnalyticsViewSet(AnalyticsViewSet):
    serializer_class = WashingtonCodeCreditAnalyticRollupSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        """Get our Machinery Class"""
        from .views.examine import ETOAnalyticsRollupMachinery

        return ETOAnalyticsRollupMachinery


class ETO2022AnalyticsViewSet(AnalyticsViewSet):
    """ETO 2021 Analytics model"""

    serializer_class = ETO2022AnalyticRollupSerializer

    def get_examine_machinery_class(self, raise_exception=True):
        """Get our Machinery Class"""
        from .views.examine import ETOAnalyticsRollupMachinery

        return ETOAnalyticsRollupMachinery

    def get_serializer_context(self):
        context = super(ETO2022AnalyticsViewSet, self).get_serializer_context()

        # Note we do this here b/c we only really want to call this once.
        # I have no idea why we get_object does not work but tired of figuring it out.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.request.parser_context.get("kwargs", {}).get(lookup_url_kwarg)
        if pk:
            filter_kw = {lookup_url_kwarg: pk}
            obj = self.serializer_class.Meta.model.objects.filter(**filter_kw).last()
            if obj:
                context.update(get_flat_analytic_rollup_results(obj))
        return context
