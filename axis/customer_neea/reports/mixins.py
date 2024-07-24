"""mixins.py: Django """


import logging
from collections import OrderedDict

from openpyxl.styles import numbers as excel_numbers, Alignment

from axis.company.models import Company
from axis.home.models import EEPProgramHomeStatus

__author__ = "Steven K"
__date__ = "08/02/2019 11:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class ExtraFiltersMixin(object):
    """Additional filters for the Utility reports only"""

    def extra_filters(self, **kwargs):
        """Extra filters"""
        self.filter_by_has_bpa_association(**kwargs)

    def filter_by_has_bpa_association(self, has_bpa_association=None, **kwargs):
        """Add our extra filter"""

        if has_bpa_association is None:
            return

        bpa_company = Company.objects.get(slug="bpa")
        companies_with_bpa_association = list(
            bpa_company.sponsored_companies.values_list("id", flat=True)
        )
        if has_bpa_association is True:
            self.filter["home__relationships__company_id__in"] = companies_with_bpa_association
        elif has_bpa_association is False:
            self.exclude["home__relationships__company_id__in"] = companies_with_bpa_association
        self.add_filter("BPA Affiliation", has_bpa_association)


class NEEAMixin(object):
    """Basic Mixin for NEEA Reports"""

    currency_format = excel_numbers.BUILTIN_FORMATS[7]  # Negative in parenthesis
    # float_format = excel_numbers.BUILTIN_FORMATS[39]  # Negative in parenthesis
    # differ from 39 with the '-' along with the parens
    float_format = "#,##0.00_);(-#,##0.00)"

    def set_cell_default_style(self, cell, **kwargs):
        """Set default style"""
        if "alignment" not in kwargs:
            kwargs.update({"alignment": Alignment(horizontal="center")})

        super(NEEAMixin, self).set_cell_default_style(cell, **kwargs)

    def build_datasets(self, report=False):
        """Build the dataset"""

        results = super(NEEAMixin, self).build_datasets(report)

        if "bpa_ues" in self.report_on:
            self.log.debug("Gathering BPA UES Data")
            self.update_task(current=16)
            data = self.get_bpa_ues_data()
            results = self.munge_data(results, data)
        else:
            self.log.debug("Excluding BPA UES Data")

        if "bpa_ues_measures" in self.report_on:
            self.log.debug("Gather BPA Measures Data")
            self.update_task(current=15)
            data = self.get_bpa_ues_measure_data()
            results = self.munge_data(results, data)
        else:
            self.log.debug("Excluding BPA Measures Data")

        return results

    def get_bpa_ues_data(self):
        """Get BPA UES Data"""

        items = OrderedDict(
            [
                ("funding_source", {"label": "Funding Source", "value": ""}),
                (
                    "reference_number",
                    {"label": "Reference Number", "value": "RWBHO13263"},
                ),
                ("quantity", {"label": "Quantity", "value": "1"}),
                ("federal_facility", {"label": "Federal Facility", "value": "No"}),
                ("unique_site_id", {"label": "Unique Site ID", "value": ""}),
                ("site_name", {"label": "Site Name", "value": ""}),
            ]
        )

        objects = self.get_queryset().distinct()
        _values = [v["value"] for v in items.values()]
        base_results = []
        for obj in objects:
            base_results.append([obj.id] + _values)

        replace_dict = OrderedDict([[k, v["label"]] for k, v in items.items()])

        structure = self.assign_json(
            EEPProgramHomeStatus,
            include=["id"] + list(replace_dict.keys()),
            section="bpa_ues",
            replace_dict=replace_dict,
        )

        data = self.merge_results(base_results, structure)
        return data

    def get_bpa_ues_measure_data(self):
        """Get BPA Measure Data"""
        items = OrderedDict(
            [
                (
                    "hvac_measure_rate",
                    {
                        "label": "HVAC and Water Heat Upgrades rate per kWh",
                        "value": "$0.27",
                    },
                ),
                (
                    "lighting_measure_rate",
                    {
                        "label": "Lighting, incl. Fixtures, Showerheads, and Smart Tstats rate per kWh",
                        "value": "$0.10",
                    },
                ),
                (
                    "appliance_and_other_electronics_rater_per_kwh",
                    {"label": "Appliance Upgrades rate per kWh", "value": "$0.27"},
                ),
                (
                    "windows_insulation_and_other_shell_rate_per_kwh",
                    {
                        "label": "Shell Upgrades, incl. Windows rate per kWh",
                        "value": "$0.45",
                    },
                ),
            ]
        )

        objects = self.get_queryset().distinct()
        _values = [v["value"] for v in items.values()]

        base_results = []
        for obj in objects:
            # The last item in the list is primary_hvac_type.
            # We need a Status ID to fetch that.
            base_results.append([obj.id] + _values)

        replace_dict = OrderedDict([[k, v["label"]] for k, v in items.items()])

        structure = self.assign_json(
            EEPProgramHomeStatus,
            include=["id"] + list(replace_dict.keys()),
            section="bpa_ues_measures",
            replace_dict=replace_dict,
        )

        data = self.merge_results(base_results, structure)
        return data
