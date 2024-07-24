"""base.py: Django ETO EPS Calculator Incentives"""


import logging

from collections import OrderedDict

from ..base import EPSBase

__author__ = "Steven K"
__date__ = "08/21/2019 08:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Incentives(EPSBase):  # pylint: disable=too-many-public-methods
    """Incentives for pre-2017"""

    def __init__(self, **kwargs):
        self.constants = kwargs.get("constants")
        self.electric_utility = kwargs.get("electric_utility")
        self.gas_utility = kwargs.get("gas_utility")
        self.us_state = kwargs.get("us_state")

        self.heat_type = kwargs.get("heat_type")
        self.has_gas_water_heater = kwargs.get("has_gas_water_heater", False)
        self.has_tankless_water_heater = kwargs.get("has_tankless_water_heater", False)
        self.hot_water_ef = kwargs.get("hot_water_ef", 0.0)

        self.pathway = kwargs.get("pathway")
        self.percentage_improvement = kwargs.get("percentage_improvement")

        self.separate_verifier_calcs = False
        self.allocation_data = self.get_allocation_data()
        if self.us_state == "WA":
            self.separate_verifier_calcs = True

        self._builder_allocation_table = None
        self._verification_allocation_table = None
        self._allocation_pct_and_waml = None
        self._builder_incentive = None
        self._verifier_incentive = None

    def get_allocation_data(self):
        """Gets the allocation data"""
        allocation_data = None
        if self.electric_utility != "other/none" and self.gas_utility != "other/none":
            allocation_data = self.constants.EPS_FULL_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS
            if self.heat_type == "gas heat":
                allocation_data = self.constants.EPS_FULL_GAS_HOME_INCENTIVE_ALLOCATION_TARGETS
            else:
                # This was added on 06/24/15 to provide an incentive for gas water heaters.
                if not self.has_gas_water_heater and self.us_state != "WA":
                    allocation_data = [x.copy() for x in allocation_data]
                    for item in allocation_data[1:]:
                        item.update({"electric_pct": 1, "gas_pct": 0, "gas_waml": 0})

        elif self.electric_utility == "other/none" and self.gas_utility != "other/none":
            self.separate_verifier_calcs = True
            _val = self.constants.EPS_GAS_ONLY_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS
            allocation_data = _val
            if self.heat_type == "gas heat":
                allocation_data = self.constants.EPS_GAS_ONLY_GAS_HOME_INCENTIVE_ALLOCATION_TARGETS
        elif self.electric_utility != "other/none" and self.gas_utility == "other/none":
            self.separate_verifier_calcs = True
            _val = self.constants.EPS_ELECTRIC_ONLY_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS
            allocation_data = _val
            if self.heat_type == "gas heat":
                allocation_data = self.constants.EPS_ELECTRIC_ONLY_HOME_INCENTIVE_ALLOCATION_TARGETS

        if allocation_data:
            return [x.copy() for x in allocation_data]

        msg = (
            "No allocation data found for Electric Utility %s and "
            "Gas Utility %s in %s with heat %s"
        )
        log.warning(msg, self.electric_utility, self.gas_utility, self.us_state, self.heat_type)

        return [
            {
                "performance_target": 0.00,
                "pathway": "code",
                "base_incentive": 0.0000,
                "electric_pct": 0,
                "gas_pct": 0,
                "electric_waml": None,
                "gas_waml": None,
            }
        ]

    def get_allocation_table(self, allocation_data):
        """Get the allocation table"""
        performance_path = "path" not in self.pathway
        pathway_found = False
        for idx, item in enumerate(allocation_data):
            item["pathway_incentive"] = item["performance_incentive"] = item["_slope"] = 0.0
            if idx == 0:
                continue
            prior = allocation_data[idx - 1]

            item["performance_range"] = max((0, item["base_incentive"] - prior["base_incentive"]))
            if not pathway_found and not performance_path:
                item["pathway_incentive"] = item["performance_range"]
            if item["pathway"] == self.pathway:
                pathway_found = True

            if item["pathway_incentive"] > 0:
                continue
            elif self.percentage_improvement >= item["performance_target"]:
                item["performance_incentive"] = item["performance_range"]
                continue
            if idx == 1:
                if self.percentage_improvement < item["performance_target"]:
                    continue

            msg = "Prior: {:12}  % Improvement: {:12} Current: {}"
            log.debug(
                msg.format(
                    prior["performance_target"],
                    self.percentage_improvement,
                    item["performance_target"],
                )
            )

            percentage_improvement = self.percentage_improvement
            if prior["performance_target"] <= percentage_improvement <= item["performance_target"]:
                _slope_partial = item["performance_target"] - prior["performance_target"]
                try:
                    item["_slope"] = _slope_partial / item["performance_range"]
                except ZeroDivisionError:
                    item["_slope"] = 0
                msg = "%s = (%s - %s) / %s - 0"
                log.debug(
                    msg,
                    item["_slope"],
                    item["performance_target"],
                    prior["performance_target"],
                    item["performance_range"],
                )
                if item["_slope"] != 0:
                    value = self.percentage_improvement - prior["performance_target"]
                    value /= item["_slope"]
                else:
                    value = 0
                msg = "%s = (%s - %s) / %s"
                log.debug(
                    msg,
                    value,
                    self.percentage_improvement,
                    prior["performance_target"],
                    item["_slope"],
                )
                _value = round(float(value) / self.constants.EPS_INCREMENTAL_INCENTIVE_VALUE)
                _value *= self.constants.EPS_INCREMENTAL_INCENTIVE_VALUE
                item["performance_incentive"] = max(0.0, _value)
        return allocation_data

    @property
    def builder_allocation_table(self):
        """Get the builder allocation table"""
        if getattr(self, "_builder_allocation_table") is None:
            self._builder_allocation_table = self.get_allocation_table(self.allocation_data)
        return self._builder_allocation_table

    @property
    def verification_allocation_table(self):
        """Get the verifier allocation table"""
        if getattr(self, "_verification_allocation_table") is None:
            if self.separate_verifier_calcs:
                _val = self.constants.EPS_FULL_HEAT_PUMP_HOME_INCENTIVE_ALLOCATION_TARGETS
                allocation_data = _val
                if self.heat_type == "gas heat":
                    allocation_data = self.constants.EPS_FULL_GAS_HOME_INCENTIVE_ALLOCATION_TARGETS
                self._verification_allocation_table = self.get_allocation_table(allocation_data)
            else:
                self._verification_allocation_table = self.builder_allocation_table
        return self._verification_allocation_table

    def get_allocation_pct_and_waml(self, key):
        """Get the allocation percent for a given key"""
        if getattr(self, "_allocation_pct_and_waml") is None:
            rev_allocation_table = self.allocation_data[:]
            rev_allocation_table.reverse()
            for item in rev_allocation_table:
                target_hit = self.percentage_improvement >= item["performance_target"]
                if self.pathway == item["pathway"] or target_hit:
                    self._allocation_pct_and_waml = {
                        "electric_utility_allocation_pct": item.get("electric_pct", 0.0),
                        "gas_utility_allocation_pct": item.get("gas_pct", 0.0),
                        "electric_waml": item.get("electric_waml", 0.0),
                        "gas_waml": item.get("gas_waml", 0.0),
                    }
                    break
            assert self._allocation_pct_and_waml is not None
        return self._allocation_pct_and_waml.get(key)

    @property
    def electric_utility_allocation_pct(self):
        """Get the electric utility allocation percent"""
        return self.get_allocation_pct_and_waml("electric_utility_allocation_pct")

    @property
    def electric_waml(self):
        """Get the electric WAML"""
        return self.get_allocation_pct_and_waml("electric_waml")

    @property
    def gas_utility_allocation_pct(self):
        """Get the gas utility allocation percent"""
        return self.get_allocation_pct_and_waml("gas_utility_allocation_pct")

    @property
    def gas_waml(self):
        """Get the gas WAML"""
        return self.get_allocation_pct_and_waml("gas_waml")

    @property
    def measure_life(self):
        """Measure Life"""
        return "-"

    @property
    def _pathway_builder_incentive(self):
        return sum([x["pathway_incentive"] for x in self.builder_allocation_table])

    @property
    def _performance_builder_incentive(self):
        return sum([x["performance_incentive"] for x in self.builder_allocation_table])

    @property
    def builder_incentive(self):
        """Amount paid to the builder"""
        if getattr(self, "_builder_incentive") is None:
            _val = self._pathway_builder_incentive + self._performance_builder_incentive
            self._builder_incentive = _val
            if self.us_state == "WA":
                if self.gas_utility != "nw natural":
                    self._builder_incentive = 0.0
                if self.heat_type == "heat pump":
                    if (self.hot_water_ef and self.hot_water_ef < 0.67) or not self.hot_water_ef:
                        self._builder_incentive = 0.0
                if self.heat_type == "heat pump" and self.has_tankless_water_heater:
                    self._builder_incentive = 0.0
        return self._builder_incentive

    @property
    def builder_electric_incentive(self):
        """Amount paid to the builder (electric portion)"""
        return self.builder_incentive * self.electric_utility_allocation_pct

    @property
    def builder_gas_incentive(self):
        """Amount paid to the builder (gas portion)"""
        return self.builder_incentive * self.gas_utility_allocation_pct

    @property
    def _pathway_verifier_incentive(self):
        return sum([x["pathway_incentive"] for x in self.verification_allocation_table])

    @property
    def _performance_verifier_incentive(self):
        return sum([x["performance_incentive"] for x in self.verification_allocation_table])

    @property
    def verifier_incentive(self):
        """Amount paid to the verifier"""
        if getattr(self, "_verifier_incentive") is None:
            self._verifier_incentive = self._pathway_verifier_incentive
            self._verifier_incentive += self._performance_verifier_incentive
            self._verifier_incentive *= self.constants.EPS_VERIFIER_MULTIPLIER

            if 0 <= self._verifier_incentive < self.constants.ETO_MININUM_RATER_INCENTIVE:
                log.debug("Raising to the minimum $%s", self.constants.ETO_MININUM_RATER_INCENTIVE)
                self._verifier_incentive = self.constants.ETO_MININUM_RATER_INCENTIVE

            if self.us_state == "WA":
                if self.gas_utility != "nw natural":
                    self._verifier_incentive = 0
                elif self.heat_type == "heat pump" or self.builder_incentive == 0:
                    self._verifier_incentive = 0
                else:
                    self._verifier_incentive = 100
        return self._verifier_incentive

    @property
    def verifier_electric_incentive(self):
        """Amount paid to the verifier (electric portion)"""
        return self.verifier_incentive * self.electric_utility_allocation_pct

    @property
    def verifier_gas_incentive(self):
        """Amount paid to the verifier (gas portion)"""
        return self.verifier_incentive * self.gas_utility_allocation_pct

    def report(self):
        """Report"""
        data = []
        data.append("\n--- Incentives ----")
        msg = "{:10}{:^18}{:^18}{:^18}{:^18}{:^18}{}"
        data.append(msg.format("Perf", "Pathway", "Full", "Perf.", "Path", "Perf", "Slope"))
        data.append(
            msg.format("Target", "Achieved", "Incentive", "Range", "Incentive", "Incentive", "")
        )

        msg = "{:<10.1%}{:^18}{:^18}{:^18}{:^18}{:^18}{:^12.6f}"
        for item in self.builder_allocation_table:
            data.append(
                msg.format(
                    item.get("performance_target"),
                    item.get("pathway"),
                    item.get("base_incentive"),
                    item.get("performance_range", "--"),
                    item.get("pathway_incentive"),
                    item.get("performance_incentive"),
                    item.get("_slope"),
                )
            )

        data.append("\n{:30} ${:10.2f}".format("Builder Incentive", self.builder_incentive))
        data.append(
            "\n    {:<18}{:12}{:15}{:<15}".format("Allocation", "Incentive", "Fuel", "WAML")
        )
        data.append(
            "    {:<18.1%} ${:<10.2f}{:<15}{:<15}".format(
                self.electric_utility_allocation_pct,
                self.builder_electric_incentive,
                "Electric",
                self.electric_waml,
            )
        )
        data.append(
            "    {:<18.1%} ${:<10.2f}{:<15}{:<15}".format(
                self.gas_utility_allocation_pct, self.builder_gas_incentive, "Gas", self.gas_waml
            )
        )

        if self.separate_verifier_calcs:
            msg = "{:<10.1%}{:^18}{:^18}{:^18}{:^18}{:^18}{:^12.6f}"
            for item in self.verification_allocation_table:
                data.append(
                    msg.format(
                        item.get("performance_target"),
                        item.get("pathway"),
                        item.get("base_incentive"),
                        item.get("performance_range", "--"),
                        item.get("pathway_incentive"),
                        item.get("performance_incentive"),
                        item.get("_slope"),
                    )
                )

        data.append("\n{:30} ${:10.2f}".format("Verifier Incentive", self.verifier_incentive))
        data.append(
            "\n    {:<18}{:12}{:15}{:<15}".format("Allocation", "Incentive", "Fuel", "WAML")
        )
        data.append(
            "    {:<18.1%} ${:<10.2f}{:<15}{:<15}".format(
                self.electric_utility_allocation_pct,
                self.verifier_electric_incentive,
                "Electric",
                self.electric_waml,
            )
        )
        data.append(
            "    {:<18.1%} ${:<10.2f}{:<15}{:<15}".format(
                self.gas_utility_allocation_pct, self.verifier_gas_incentive, "Gas", self.gas_waml
            )
        )
        return "\n".join(data)

    @property
    def project_tracker_path(self):  # pylint: disable=too-many-return-statements
        """Project Tracker Path"""
        path = self.pathway
        if path == "path 1":
            return "Pathway 1"
        elif path == "path 2":
            return "Pathway 2"
        elif path == "path 3":
            return "Pathway 3"
        elif path == "path 4":
            return "Pathway 4"
        elif path == "path 5":
            return "Pathway 5"
        elif path == "pct":
            return "Percent Improvement"
        return "Unknown - %s" % path

    @property
    def project_tracker_home_config(self):
        """Home Configuration"""
        pass

    @property
    def electric_load_profile(self):
        """Electric Load Profile"""
        pass

    @property
    def gas_load_profile(self):
        """Gas Load Profile"""
        pass

    @property
    def report_data(self):
        """Report Data"""
        return OrderedDict(
            [
                ("electric_utility_allocation_pct", self.electric_utility_allocation_pct),
                ("gas_utility_allocation_pct", self.gas_utility_allocation_pct),
                ("builder_electric_incentive", self.builder_electric_incentive),
                ("builder_gas_incentive", self.builder_gas_incentive),
                ("builder_incentive", self.builder_incentive),
                ("verifier_electric_incentive", self.verifier_electric_incentive),
                ("verifier_gas_incentive", self.verifier_gas_incentive),
                ("verifier_incentive", self.verifier_incentive),
                ("gas_waml", self.gas_waml),
                ("electric_waml", self.electric_waml),
                ("measure_life", self.measure_life),
                ("project_tracker_pathway", self.project_tracker_path),
                ("project_tracker_home_config", self.project_tracker_home_config),
                ("electric_load_profile", self.electric_load_profile),
                ("gas_load_profile", self.gas_load_profile),
            ]
        )

    @property
    def net_zero_report_data(self):
        return OrderedDict(
            [
                ("net_zero_eps_incentive", 0.0),
                ("energy_smart_homes_eps_incentive", 0.0),
                ("net_zero_solar_incentive", 0.0),
                ("energy_smart_homes_solar_incentive", 0.0),
            ]
        )

    def net_zero_report(self):
        return ""
