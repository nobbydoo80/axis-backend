"""Examine Views"""


import logging

from analytics.api import AnalyticsViewSet
from analytics.views.examine import AnalyticsRollupMachinery

from axis import examine
from axis.company.models import Company
from ..api import (
    ETOAccountViewSet,
    ETO2019AnalyticsViewSet,
    ETO2020AnalyticsViewSet,
    ETO2021AnalyticsViewSet,
    WashingtonCodeCreditAnalyticsViewSet,
)
from ..forms import ETOAccountForm
from ..models import ETOAccount

__author__ = "Michael Jeffrey"
__date__ = "4/13/16 5:26 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)


class ETOAccountExamineMachinery(examine.SingleObjectMachinery):
    """ETO Account Machinery"""

    model = ETOAccount
    form_class = ETOAccountForm
    type_name = "eto_account"
    api_provider = ETOAccountViewSet
    template_set = "panel"

    region_template = "examine/customer_eto/eto_account_region.html"
    detail_template = "examine/customer_eto/eto_account_detail.html"
    form_template = "examine/customer_eto/eto_account_form.html"

    def get_helpers(self, instance):
        """Helpers"""
        helpers = super(ETOAccountExamineMachinery, self).get_helpers(instance)
        helpers["panel_heading"] = "License and Account Number"
        return helpers

    def can_delete_object(self, instance, user=None):
        """No deletions possible"""
        return False

    def get_form_kwargs(self, instance):
        """Form Kwargs"""
        kwargs = super(ETOAccountExamineMachinery, self).get_form_kwargs(instance)

        # Can't rely on company to be there on the ETOAccount instance if it's in creation mode
        # while the company itself is not.
        try:
            company = Company.objects.get(id=self.context["company_id"])
        except (Company.DoesNotExist, KeyError):
            company = None

        kwargs.update(
            {
                "user": self.context["request"].user,
                "company": company,
                "company_type": self.context["company_type"],
            }
        )
        return kwargs

    def get_region_dependencies(self):
        """Dependencies"""
        return {
            "company_new": [{"field_name": "id", "serialize_as": "company"}],
        }


class ETOAnalyticsRollupMachinery(AnalyticsRollupMachinery):
    """Allows us to override some of this"""

    detail_templates = {
        None: "examine/analytics_detail.html",
        "eto-2019": "examine/analytics_eto_2019.html",
        "eto-2020": "examine/analytics_eto_2020.html",
        "eto-2021": "examine/analytics_eto_2020.html",
        "eto-fire-2021": "examine/analytics_eto_2020.html",
        "washington-code-credit": "examine/analytics_washington_code_credit.html",
    }

    api_providers = {
        None: AnalyticsViewSet,
        "eto-2019": ETO2019AnalyticsViewSet,
        "eto-2020": ETO2020AnalyticsViewSet,
        "eto-2021": ETO2021AnalyticsViewSet,
        "eto-fire-2021": ETO2021AnalyticsViewSet,
        "washington-code-credit": WashingtonCodeCreditAnalyticsViewSet,
    }

    def get_detail_template_url(self, instance):
        """Break out the detail if needed"""
        log.info(
            "Analytics ID: Content ID %s - Slug %s",
            instance.pk,
            instance.content_object.pk,
            instance.content_object.eep_program.slug,
        )
        try:
            name = self.detail_templates[instance.content_object.eep_program.slug]
            return examine.utils.template_url(name)
        except (KeyError, AttributeError):
            return super(ETOAnalyticsRollupMachinery, self).get_detail_template_url(instance)

    def get_api_provider(self):
        """Get the right API"""
        try:
            return self.api_providers[self.instance.content_object.eep_program.slug]
        except (KeyError, AttributeError):
            return super(ETOAnalyticsRollupMachinery, self).get_api_provider()

    def get_helpers(self, instance):
        """Helpers"""
        helpers = super(ETOAnalyticsRollupMachinery, self).get_helpers(instance)

        user = self.context["request"].user
        company = self.context["request"].company
        analysis_viewers = company.slug in ["eto", "peci"]

        helpers["view_analysis"] = False
        helpers["can_refresh"] = False
        if instance:
            helpers["view_analysis"] = user.is_superuser or analysis_viewers
            valid_states = ["READY", "REQUIRES_UPDATE"]
            valid_user = user.is_superuser or user.company.slug in ["peci"]
            helpers["can_refresh"] = valid_user and instance.status in valid_states
        return helpers
