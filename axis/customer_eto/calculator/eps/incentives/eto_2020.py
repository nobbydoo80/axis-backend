"""eto_2020.py: Django """


import logging

__author__ = "Steven K"
__date__ = "12/15/2019 20:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from collections import OrderedDict

from .eto_2019 import Incentives2019

log = logging.getLogger(__name__)


class Incentives2020(Incentives2019):
    """Incentives for 2020"""

    @property
    def full_territory_builder_incentive(self):
        """OR = =MIN(4723,IF($D$18>=0.08,(36354*($D$18^2))-(4510.2*$D$18)+710.5,0))"""
        if not isinstance(self.percentage_improvement, (float, int)):
            return "-"

        if self.us_state == "WA":
            """=IF(
            OR('Input-2020'!$C$9<>'Input-2020'!$V$5,'Input-2020'!$C$13<>'Input-2020'!$X$5),0,
            IF(AND($D$15>=0.1,D15<0.2),
                2000*D15+100,
                IF(AND(D15>=0.1,D15>=0.2),
                    MIN(1300,3000*D15+100),0)))"""

            if self.gas_utility != "nw natural" or self.heat_type != "gas heat":
                return 0.0
            if self.percentage_improvement < 0.10:
                return 0.0
            elif self.percentage_improvement < 0.2:
                return 2000.0 * self.percentage_improvement + 100.00
            elif self.percentage_improvement >= 0.2:
                value = 3000.00 * self.percentage_improvement + 100.00
                return min([1300.00, value])

        # Oregon
        _eq = self.constants.EPS_OR_POLY
        if self.percentage_improvement < 0.10:
            return 0.0

        val = _eq["second_order"] * self.percentage_improvement * self.percentage_improvement
        val += _eq["first_order"] * self.percentage_improvement + _eq["scaler"]

        return min([_eq["min"], val])

    @property
    def actual_builder_electric_incentive(self):
        """Actual Builder Electric Incentive"""
        value = super(Incentives2020, self).actual_builder_electric_incentive
        if self.us_state == "OR" and self.has_heat_pump_water_heater:
            value -= 250.0
        return max([value, 0.0])

    @property
    def actual_builder_incentive(self):
        """Actual Builder Incentive"""
        if self.us_state == "WA":
            if self.gas_utility != "nw natural":
                return 0.0

        return (
            self.actual_builder_electric_incentive
            + self.actual_builder_gas_incentive
            + self.net_zero.incentive
        )

    @property
    def actual_verifier_incentive(self):
        """Actual Verifier Incentive

        =IF(D57>=0.1,MAX(300,(E48-500)*MIN(0.4,D57)),0)
        """
        if self.percentage_improvement >= 0.1:
            if self.us_state == "WA":
                if self.gas_utility != "nw natural":
                    return 0.0
                return 100.00

            value = self.full_territory_builder_incentive - 500.00
            value *= min(
                [self.constants.ETO_RATER_MIN_INCENTIVE_PCT_MUTIPLIER, self.percentage_improvement]
            )
            return max([self.constants.ETO_RATER_MAX_INCENTIVE_MUTIPLIER, value])
        return 0.0

    @property
    def mad_max_incentive(self):
        """This is the top right and really C14

        0 < 20
        =IF('Incentives-2020'!E39='Incentives-2020'!D10,
            'Calcs-2020'!E101*'ESH and NZ-2020'!M16+'ESH and NZ-2020'!N16,
            "0")
            If path name  == path 1:
                return pct improvement * m + b
            else:
                0

        20 < 30
        =IF('Incentives-2020'!E39='Incentives-2020'!D11,
            'Calcs-2020'!E101*'ESH and NZ-2020'!M17+'ESH and NZ-2020'!N17,
            "0")
            If path name  == path 2:
                return pct improvement * m + b
            else:
                0
        30 < 40
        =IF('Incentives-2020'!E39='Incentives-2020'!D12,
            'Calcs-2020'!E101*'ESH and NZ-2020'!M18+'ESH and NZ-2020'!N18,
            "0")
            If path name  == path 3:
                return pct improvement * m + b
            else:
                0
        > 40
        =IF('Incentives-2020'!E39='Incentives-2020'!D13,N19,"0")`
        """
        table = dict(self.constants.NET_ZERO_PROGRAM_MAX_INCENTIVE)
        m, b = 0, 0
        if 0.10 <= self.percentage_improvement < 0.20 and self.home_path == "Path 1":
            m = (table["Path 2"]["base_price"] - table[self.home_path]["base_price"]) / 0.1
            b = table[self.home_path]["b"]
        elif 0.20 <= self.percentage_improvement < 0.30 and self.home_path == "Path 2":
            m = (table["Path 3"]["base_price"] - table[self.home_path]["base_price"]) / 0.1
            b = table[self.home_path]["b"]
        elif 0.30 <= self.percentage_improvement < 0.40 and self.home_path == "Path 3":
            m = (table["Path 4"]["base_price"] - table[self.home_path]["base_price"]) / 0.1
            b = table[self.home_path]["b"]
        elif self.percentage_improvement >= 0.40 and self.home_path == "Path 4":
            b = table[self.home_path]["b"]
        return self.percentage_improvement * m + b

    @property
    def net_zero_eps_allocation(self):
        """C18"""
        return self.net_zero.incentive - self.net_zero_solar_allocation

    @property
    def net_zero_eps_builder_allocation(self):
        """Top Left Chart"""
        if not self.net_zero.incentive:
            return 0.0
        val = self.net_zero.net_zero_incentive / self.net_zero.incentive
        val *= self.net_zero_eps_allocation
        return max([0.0, val])

    @property
    def net_zero_eps_incentive(self):
        """Net Zero EPS Incentive"""
        return self.net_zero_eps_builder_allocation

    @property
    def net_zero_energy_smart_homes_builder_eps_allocation(self):
        """Top Right Chart"""
        if not self.net_zero.incentive:
            return 0.0
        val = self.net_zero.energy_smart_home_incentive / self.net_zero.incentive
        val *= self.net_zero_eps_allocation
        return max([0.0, val])

    @property
    def energy_smart_homes_eps_incentive(self):
        """Energy Smart Homes EPS Incentive"""
        return self.net_zero_energy_smart_homes_builder_eps_allocation

    @property
    def net_zero_solar_allocation(self):
        """C19"""
        return max([0.0, self.actual_builder_incentive - self.mad_max_incentive])

    @property
    def net_zero_solar_builder_allocation(self):
        """Bottom Left Chart
        Note: this was observed as a slightly different calculation
        """
        if not self.net_zero.incentive:
            return 0.0
        val = max([0.0, self.net_zero.net_zero_incentive / self.net_zero.incentive])
        val *= self.net_zero_solar_allocation
        return val

    @property
    def net_zero_solar_incentive(self):
        """Net Zero Solar Incentive"""
        return self.net_zero_solar_builder_allocation

    @property
    def net_zero_energy_smart_homes_builder_solar_allocation(self):
        """Bottom Right Chart"""
        if not self.net_zero.incentive:
            return 0.0
        val = self.net_zero.energy_smart_home_incentive / self.net_zero.incentive
        val *= self.net_zero_solar_allocation
        return max([0.0, val])

    @property
    def energy_smart_homes_solar_incentive(self):
        """Energy Smart Homes Solar Incentive"""
        return self.net_zero_energy_smart_homes_builder_solar_allocation

    @property
    def net_zero_report_data(self):
        """A simple way to represent this data"""
        return OrderedDict(
            [
                ("net_zero_incentive", self.net_zero.net_zero_incentive),
                ("energy_smart_home_incentive", self.net_zero.energy_smart_home_incentive),
                ("total_incentive", self.net_zero.incentive),
                ("whole_home_incentive", self.actual_builder_incentive_minus_net_zero),
                ("mad_max_incentive", self.mad_max_incentive),
                ("eps_allocation", self.net_zero_eps_allocation),
                ("solar_allocation", self.net_zero_solar_allocation),
                ("net_zero_eps_incentive", self.net_zero_eps_incentive),
                ("energy_smart_homes_eps_incentive", self.energy_smart_homes_eps_incentive),
                ("net_zero_solar_incentive", self.net_zero_solar_incentive),
                ("energy_smart_homes_solar_incentive", self.energy_smart_homes_solar_incentive),
            ]
        )

    def net_zero_report(self):
        """Net Zero Report"""
        msg = "{:30} {:30}"
        data = []
        data.append(msg.format("Incentives", ""))
        data.append(msg.format("Net Zero", self.net_zero.round4d__net_zero_incentive))
        _msg = "{:<4}{:<18}{}"
        if not self.net_zero.valid_nz_electric:
            data.append(_msg.format("", "Invalid Utility", self.net_zero.electric_utility))
        if self.percentage_improvement < 0.2:
            data.append(_msg.format("", "% Imp < .20", self.net_zero.percentage_improvement))
        if not self.net_zero.valid_nz_therms:
            if self.net_zero.improved_total_therms:
                data.append(_msg.format("", "Therms not 0", self.net_zero.improved_total_therms))
            else:
                data.append(
                    _msg.format(
                        "", "Therms % improvent < .20", self.net_zero.therms_pct_improvement
                    )
                )
        if not self.net_zero.valid_nz_solar_answer:
            data.append(
                _msg.format(
                    "",
                    "Solar Elements == Solar PV",
                    self.net_zero.solar_elements,
                )
            )
        if not self.net_zero.valid_nz_pv:
            data.append(
                _msg.format(
                    "",
                    "PV < Total kwh | {:.2f} < ".format(self.net_zero.pv_kwh_unadjusted),
                    self.net_zero.improved_total_kwh,
                )
            )
        data.append(
            msg.format("Energy Smart home", self.net_zero.round4d__energy_smart_home_incentive)
        )
        for label, item in [
            ("Base Package", self.net_zero.base_package_energy_smart_incentive),
            ("Storage Ready", self.net_zero.storage_ready_energy_smart_incentive),
            ("Advanced Wiring", self.net_zero.storage_ready_energy_smart_incentive),
        ]:
            if item:
                data.append("{:<4}{:<18}{}".format("", label, item))
        data.append(msg.format("-" * 29, "-" * 10))
        data.append(msg.format("NZ + ESH Total", self.net_zero.round4d__incentive))
        data.append(
            msg.format(
                "Whole Home Incentive",
                "${}".format(round(self.actual_builder_incentive_minus_net_zero, 4)),
            )
        )
        data.append(msg.format("Total Incentive", self.round4d__actual_builder_incentive))
        data.append("")
        data.append(msg.format("MAD Max Incentive", ""))
        data.append(
            msg.format(self.round2p__percentage_improvement, self.round4d__mad_max_incentive)
        )
        data.append("")
        data.append(msg.format("Incentive Allocations (EPS vs Solar)", ""))
        data.append(msg.format("EPS (PGE/PAC)", self.round4d__net_zero_eps_allocation))
        data.append(msg.format("Solar", self.round4d__net_zero_solar_allocation))
        data.append("\n")

        msg = "{:20}{:41}{:1}     {:38}{:40}{:5}"
        data.append(
            msg.format(
                "",
                "Builder EPS Net Zero Inc. & Alloc. for PT",
                "",
                "",
                "Builder EPS ESH Inc. & Alloc. for PT",
                "",
            )
        )

        msg = "{:20}{:10}{:50}     {:20}{:10}{:32}"
        data.append(
            msg.format(
                "Builder Incentive",
                "100.00%",
                self.round2d__net_zero_eps_incentive,
                "Builder Incentive",
                "100.00%",
                self.round2d__energy_smart_homes_eps_incentive,
            )
        )
        data.append("\n")
        msg = "{:20}{:41}{:1}     {:38}{:40}{:5}"
        data.append(
            msg.format(
                "",
                "Builder Solar Net Zero Inc. & Alloc. for PT",
                "",
                "",
                "Builder Solar  ESH Inc. & Alloc. for PT",
                "",
            )
        )
        msg = "{:20}{:10}{:50}     {:20}{:10}{:30}"
        data.append(
            msg.format(
                "Builder Incentive",
                "100.00%",
                self.round2d__net_zero_solar_incentive,
                "Builder Incentive",
                "100.00%",
                self.round2d__energy_smart_homes_solar_incentive,
            )
        )
        return "\n".join(data)
