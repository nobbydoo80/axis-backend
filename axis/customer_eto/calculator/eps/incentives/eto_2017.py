"""eto_2017.py: Django ETO EPS Calculator Incentives"""


import logging
from collections import OrderedDict

from .base import Incentives
from ..net_zero import NetZero

__author__ = "Steven K"
__date__ = "08/21/2019 08:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class Incentives2017(Incentives):  # pylint: disable=too-many-public-methods
    """Incentives for 2017"""

    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        self.constants = kwargs.get("constants")
        self.electric_utility = kwargs.get("electric_utility")
        self.gas_utility = kwargs.get("gas_utility")
        self.us_state = kwargs.get("us_state")

        self.heat_type = kwargs.get("heat_type")
        self.heating_therms = kwargs.get("heating_therms")
        self.hot_water_therms = kwargs.get("hot_water_therms")
        self.hot_water_kwh = kwargs.get("hot_water_kwh")

        self.pathway = kwargs.get("pathway")
        self.home_subtype = kwargs.get("home_subtype")
        self.percentage_improvement = kwargs.get("percentage_improvement")

        self.net_zero = kwargs.get("net_zero")
        if self.net_zero is None:
            self.net_zero = NetZero()

        if self.constants:
            self.allocation_data = self.constants.EPS_INCENTIVE_ALLOCATION_DATA
            self.load_profiles = OrderedDict(self.constants.EPS_WAML_LOAD_PROFILES)
            self.weighted_average_utility_allocation = OrderedDict(
                self.constants.WEIGHTED_UTILITY_ALLOCATIONS
            )
            if self.us_state == "WA":
                self.allocation_data = self.constants.EPS_WA_INCENTIVE_ALLOCATION_DATA
                self.load_profiles = OrderedDict(self.constants.EPS_WA_WAML_LOAD_PROFILES)
        else:
            self.allocation_data = None
            self.load_profiles = None
            log.warning("No constants provided!")

        self.load_profile = None

    @property
    def full_territory_builder_incentive(self):  # pylint: disable=too-many-return-statements
        """
        =IF(ISNUMBER(D18),
           ROUND(
              IF(D18<E6,0,
              IF(AND(D18>=E6,D18<D7),BASEINCB,
              IF(AND(D18>=$D$7,D18<$D$8),BASEINCB+((D18*100-$D$7*100)+$F$7),
              IF(AND(D18>=$D$8,D18<$D$9),$G$7+((D18*100-$D$8*100)*$F$8)+$F$8,
              IF(AND(D18>=$D$9,D18<$D$10),$G$8+((D18*100-$D$9*100)*$F$9)+$F$9,
              IF(AND(D18>=$D$10,D18<$D$11),$G$9+((D18*100-$D$10*100)*$F$10)+$F$10,
              IF(AND(D18>=$D$11,D18<$D$12),$G$10+((D18*100-$D$11*100)*$F$11)+$F$11,
              IF(AND(D18>=$D$12,D18<$D$13),$G$11+((D18*100-$D$12*100)*$F$12)+$F$12,
              IF(AND(D18>=$D$13,D18<$D$14),$G$12+((D18*100-$D$13*100)*$F$13)+$F$13,
              IF(AND(D18>=$D$14,D18<$D$15),$G$13+((D18*100-$D$14*100)*$F$14)+$F$14,
              IF(AND(D18>=$D$15,D18<$E$15),$G$14+((D18*100-$D$15*100)*$F$15)+$F$15,
              IF(D18>=E15,G15)))))))))))),100),"-")
        """
        if not isinstance(self.percentage_improvement, (float, int)):
            return 0.0

        if self.us_state == "WA":
            if self.gas_utility != "nw natural" or self.heat_type == "heat pump":
                return 0.0

        if self.percentage_improvement < 0.10:
            return 0.0
        elif 0.10 <= self.percentage_improvement < 0.11:
            return 600.00
        elif self.percentage_improvement >= 0.40:
            if self.us_state != "WA":
                return 4680.00
            return 850.0

        for idx, item in enumerate(self.allocation_data[1:], start=1):
            prior_item = self.allocation_data[idx - 1]
            try:
                next_item = self.allocation_data[idx + 1]
            except IndexError:
                next_item = {"min": 0.4}

            if item.get("min") <= self.percentage_improvement < next_item.get("min"):
                msg = "{:.2f} + (({:.6f} * 100.0 - {:.2f} * 100) * {}) + {}"
                log.debug(
                    msg.format(
                        prior_item["incentive"],
                        self.percentage_improvement,
                        item["min"],
                        item["incentive_increment"],
                        item["incentive_increment"],
                    )
                )
                _increment = self.percentage_improvement * 100.0 - item["min"] * 100
                _increment *= item["incentive_increment"]
                return prior_item["incentive"] + _increment + item["incentive_increment"]
        return 0.0

    @property
    def home_path(self):
        """
            =IF(AND(D18>=E22,D18<E23),D22,
            IF(AND(D18>=E23,D18<E24),D23,
            IF(AND(D18>=E24,D18<E25),D24,
            IF(AND(ISNUMBER(D18),D18>=E25),D25,
            "-"))))
        :return:
        """
        if 0.10 <= self.percentage_improvement < 0.20:
            return "Path 1"
        elif 0.20 <= self.percentage_improvement < 0.30:
            return "Path 2"
        elif 0.30 <= self.percentage_improvement < 0.40:
            return "Path 3"
        elif self.percentage_improvement > 0.40:
            return "Path 4"
        log.info("Unknown path due to pct improvement of %f", self.percentage_improvement)
        return "N/A"

    @property
    def project_tracker_path(self):
        """Project tracker pathway"""
        path = self.home_path
        if path == "Path 1":
            return "Pathway 1"
        elif path == "Path 2":
            return "Pathway 2"
        elif path == "Path 3":
            return "Pathway 3"
        elif path == "Path 4":
            return "Pathway 4"
        return "Unknown %s" % path

    @property
    def project_tracker_home_config(self):
        """Project Home Config"""
        config = self.home_subtype
        if config == "GH+GW":
            return "Gas Heat - Gas DHW"
        elif config == "EH+EW":
            return "Ele Heat - Ele DHW"
        elif config == "GH+EW":
            return "Gas Heat - Ele DHW"
        elif config == "EH+GW":
            return "Ele Heat - Gas DHW"
        return "Unknown %s" % config

    def _get_load_profile(self):
        if not getattr(self, "load_profile"):
            _data = self.load_profiles.get(self.home_path)
            data = OrderedDict(_data)
            sub_data = data.get(self.home_subtype, [])
            self.load_profile = OrderedDict(sub_data)
        return self.load_profile

    @property
    def electric_load_profile(self):
        """Electric Load Profile"""
        return self._get_load_profile().get("electric_load_profile")

    @property
    def gas_load_profile(self):
        """Gas Load Profile"""
        return self._get_load_profile().get("gas_load_profile")

    @property
    def measure_life(self):
        """Measure Life"""
        return self._get_load_profile().get("measure_life", 0.0)

    @property
    def gas_waml(self):
        """Get the gas WAML"""
        return int(round(self.measure_life, 0))

    @property
    def electric_waml(self):
        """Get the electric WAML"""
        return int(round(self.measure_life, 0))

    @property
    def electric_utility_allocation_pct(self):
        """Get the electric utility allocation percent"""
        if self.us_state == "OR":
            if self.electric_utility == "other/none" or self.gas_utility == "other/none":
                return OrderedDict(
                    self.weighted_average_utility_allocation.get(self.home_subtype, [])
                ).get("electric", 0.0)
        return self._get_load_profile().get("electric_benefit_ratio", 0.0)

    @property
    def gas_utility_allocation_pct(self):
        """Get the gas utility allocation percent"""
        if self.us_state == "OR":
            if self.electric_utility == "other/none" or self.gas_utility == "other/none":
                return OrderedDict(
                    self.weighted_average_utility_allocation.get(self.home_subtype, [])
                ).get("gas", 0.0)
        return self._get_load_profile().get("gas_benefit_ratio", 0.0)

    @property
    def verifier_electric_utility_allocation_pct(self):
        """Amount paid to the verifier (electric portion)"""
        if self.electric_utility != "other/none" and self.gas_utility != "other/none":
            return self.electric_utility_allocation_pct
        if self.electric_utility == "other/none":
            return 0.0
        return 1.0

    @property
    def verifier_gas_utility_allocation_pct(self):
        """Amount paid to the verifier (gas portion)"""
        if self.electric_utility != "other/none" and self.gas_utility != "other/none":
            return self.gas_utility_allocation_pct
        if self.gas_utility == "other/none":
            return 0.0
        return 1.0

    @property
    def actual_builder_electric_incentive(self):
        """Actual Builder Electric Incentive"""
        if self.electric_utility == "other/none":
            return 0.0
        return self.full_territory_builder_incentive * self.electric_utility_allocation_pct

    @property
    def builder_electric_incentive(self):
        """Amount paid to the builder (electric portion)"""
        return round(self.actual_builder_electric_incentive, 0)

    @property
    def actual_builder_gas_incentive(self):
        """Actual Builder Gas Incentive"""
        if self.gas_utility == "other/none":
            return 0.0
        return self.full_territory_builder_incentive * self.gas_utility_allocation_pct

    @property
    def builder_gas_incentive(self):
        """Amount paid to the builder (gas portion)"""
        return round(self.actual_builder_gas_incentive, 0)

    @property
    def actual_builder_incentive(self):
        """Actual Builder Incentive"""
        if self.us_state == "WA":
            if self.gas_utility != "nw natural":
                return 0.0

        # ProjectTracker expects the this to be the sum of pre-rounded values.  That means there are
        # two stages of rounding happening, and that is what they desire for it to match the
        # bookkeeping on their side.
        return (
            self.builder_electric_incentive + self.builder_gas_incentive + self.net_zero.incentive
        )

    @property
    def actual_builder_incentive_minus_net_zero(self):
        return self.actual_builder_incentive - self.net_zero.incentive

    @property
    def builder_incentive(self):
        """Actual Builder Incentive"""
        return round(max([0, self.actual_builder_incentive]), 0)

    @property
    def actual_verifier_incentive(self):
        """Actual Verifier Incentive"""
        if self.actual_builder_incentive > 0.0:
            if self.us_state == "WA":
                if self.gas_utility != "nw natural":
                    return 0.0
                return 100.00

                # if self.heat_type == 'heat pump' and self.hot_water_ef < 0.67:
                #     return 0.0
                # if self.heat_type == 'heat pump' and self.has_tankless_water_heater:
                #     self._builder_incentive = 0.0
            if self.percentage_improvement > 0.4:
                return self.full_territory_builder_incentive * 0.4
            return max(
                self.constants.ETO_MININUM_RATER_INCENTIVE,
                self.full_territory_builder_incentive * self.percentage_improvement,
            )
        return 0.0

    @property
    def verifier_incentive(self):
        """Actual Verifier Incentive"""
        return round(self.actual_verifier_incentive, 0)

    @property
    def actual_verifier_electric_incentive(self):
        """Actual Verifier Electric Incentive"""
        return self.actual_verifier_incentive * self.verifier_electric_utility_allocation_pct

    @property
    def verifier_electric_incentive(self):
        """Amount paid to the verifier (electric portion)"""
        return round(self.actual_verifier_electric_incentive, 0)

    @property
    def actual_verifier_gas_incentive(self):
        """Amount paid to the verifier (gas portion)"""
        return self.actual_verifier_incentive * self.verifier_gas_utility_allocation_pct

    @property
    def verifier_gas_incentive(self):
        """Amount paid to the verifier (gas portion)"""
        return round(self.actual_verifier_gas_incentive, 0)

    def _report_incentive_table(self):
        """Repoort"""
        data = []
        data.append("Incentive Table")
        msg = "{:<10.0%} {:<10.0%} {:<9} $ {}"
        for idx, item in enumerate(self.allocation_data):
            try:
                maxv = self.allocation_data[idx + 1]["min"] - 0.01
            except IndexError:
                maxv = 0.40

            data.append(
                msg.format(
                    item.get("min"), maxv, item.get("incentive_increment"), item.get("incentive")
                )
            )

        data.append("{:<10} {:<10}".format("% Improvement", "Full Incentive"))
        data.append(
            "{:<10.2%} {:<10}".format(
                self.percentage_improvement, self.round4d__full_territory_builder_incentive
            )
        )
        return "\n".join(data)

    def _report_load_profiles(self):
        data = [""]
        msg = "{:20} {:20} {:20} {:<15} {:<10} {:<10}"
        data.append(
            msg.format(
                "Subtype and Alloc",
                "Ele Load Profile",
                "Gas Load Profile",
                "Measure Life",
                "Elec Benefit",
                "Gas Benefit",
            )
        )
        msg = "{:20} {:25} {:25} {:<15.1f} {:<10.4f} {:<10.4f}"
        for path, _data in self.load_profiles.items():
            for subtype, _elements in OrderedDict(_data).items():
                elements = OrderedDict(_elements)
                data.append(
                    msg.format(
                        "{} {}".format(path, subtype),
                        elements.get("electric_load_profile"),
                        elements.get("gas_load_profile"),
                        elements.get("measure_life"),
                        elements.get("electric_benefit_ratio"),
                        elements.get("gas_benefit_ratio"),
                    )
                )
            data.append("")
        return "\n".join(data)

    @property
    def _report_alt_allocation_data(self):
        return None

    def report(self):
        """Report"""
        incentive_table = self._report_incentive_table()
        report_loads = self._report_load_profiles()
        alt_allocation_data = self._report_alt_allocation_data

        data = []
        msg = "{:30} {:30}"
        data.append(msg.format("\nHome Path", "Home Subtype"))
        data.append(msg.format(self.home_path, self.home_subtype))
        data.append(msg.format("This home, CE Subtype:", self.home_path + " " + self.home_subtype))

        msg = "{:20} {:20} {:<15} {:<10} {:<10}"
        data.append(msg.format("\nLoad Profiles", "", "", " Benefit Ratio", ""))
        data.append(msg.format("Electric", "Gas", "Measure Life", "Electric", "Gas"))
        msg = "{:20} {:20} {:<15} {:<10} {:<10}"
        data.append(
            msg.format(
                self.electric_load_profile,
                self.gas_load_profile,
                self.round__measure_life,
                self.round4p__electric_utility_allocation_pct,
                self.round4p__gas_utility_allocation_pct,
            )
        )

        msg = "{:30} {:20}"
        data.append(msg.format("\n% Improvement", "Initial Incentive"))
        data.append(
            msg.format(
                self.round4p__percentage_improvement, self.round4d__full_territory_builder_incentive
            )
        )

        data.append("")
        msg = "{:<20} {:20} {:20} {:20} {:20} {:20}"
        data.append(
            msg.format(
                "Allocation", "Incentive", "Fuel", "Utility", "Load Profile", "WAML-Whole Home"
            )
        )
        data.append(
            msg.format(
                self.round4p__electric_utility_allocation_pct,
                self.round4d__actual_builder_electric_incentive,
                "Electric",
                self.electric_utility,
                self.electric_load_profile,
                "",
            )
        )
        data.append(
            msg.format(
                self.round4p__gas_utility_allocation_pct,
                self.round4d__actual_builder_gas_incentive,
                "Gas",
                self.gas_utility,
                self.gas_load_profile,
                "",
            )
        )
        data.append(
            msg.format(
                "Builder Incentive",
                self.round4d__actual_builder_incentive_minus_net_zero,
                "",
                "",
                "",
                self.round__measure_life,
            )
        )

        if alt_allocation_data:
            data += alt_allocation_data

        data.append("")
        msg = "{:<20} {:20} {:20} {:20} {:20} {:20}"
        data.append(
            msg.format(
                "Allocation", "Incentive", "Fuel", "Utility", "Load Profile", "WAML-Whole Home"
            )
        )
        data.append(
            msg.format(
                self.round4p__verifier_electric_utility_allocation_pct,
                self.round4d__actual_verifier_electric_incentive,
                "Electric",
                self.electric_utility,
                self.electric_load_profile,
                "",
            )
        )
        data.append(
            msg.format(
                self.round4p__verifier_gas_utility_allocation_pct,
                self.round4d__actual_verifier_gas_incentive,
                "Gas",
                self.gas_utility,
                self.gas_load_profile,
                "",
            )
        )
        data.append(
            msg.format(
                "Verifier Incentive",
                self.round4d__actual_verifier_incentive,
                "",
                "",
                "",
                self.round__measure_life,
            )
        )

        data.append("")
        data.append("Rounded Reported Values:")
        msg = "{:<15}  Electric: {:<10} Gas: {:<10}  Total: {:10}"
        data.append(
            msg.format(
                "Builder",
                self.round4d__builder_electric_incentive,
                self.round4d__builder_gas_incentive,
                self.round4d__builder_incentive,
            )
        )
        data.append(
            msg.format(
                "Verifier",
                self.round4d__verifier_electric_incentive,
                self.round4d__verifier_gas_incentive,
                self.round4d__verifier_incentive,
            )
        )

        return incentive_table + "\n" + report_loads + "\n".join(data)
