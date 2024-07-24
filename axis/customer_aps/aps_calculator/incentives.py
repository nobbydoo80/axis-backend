"""incentives.py: Django """


import logging
from collections import OrderedDict
from decimal import Decimal

from .base import APSBase

__author__ = "Steven Klass"
__date__ = "4/6/18 4:05 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class APSIncentive(APSBase):
    """Base class for APS Programs"""

    def __init__(self, program_slug, thermostat_option, thermostat_qty):
        from axis.eep_program.models import EEPProgram

        self.program = EEPProgram.objects.get(slug=program_slug)
        self.thermostat_option = thermostat_option
        self.thermostat_qty = thermostat_qty

    @property
    def builder_incentive(self):
        """Builder Incentive"""
        return Decimal(self.program.builder_incentive_dollar_value)

    @property
    def rater_incentive(self):
        """Is there a rater incentive"""
        return Decimal(self.program.rater_incentive_dollar_value)

    @property
    def total_incentive(self):
        """What is the total incentive"""
        return self.builder_incentive + self.rater_incentive

    @property
    def has_incentive(self):
        """Do we have an incentive"""
        return self.total_incentive > 0

    def report(self):
        """Report of data"""
        data = []
        data.append("\n--- APS Incentives ----")
        msg = "{:<38} {:<10}"
        data.append(msg.format("Incentive", "Rate"))
        data.append(msg.format("Builder", self.round2d__builder_incentive))
        data.append(msg.format("Rater", self.round2d__rater_incentive))
        data.append("-" * 40)
        data.append(msg.format("Total", "", self.round2d__total_incentive))
        return "\n".join(data)

    def data(self):
        """Raw data"""
        return OrderedDict(
            [
                ("has_incentive", self.has_incentive),
                ("builder_incentive", self.builder_incentive),
                ("pretty_builder_incentive", self.round2d__builder_incentive),
                ("rater_incentive", self.rater_incentive),
                ("pretty_rater_incentive", self.round2d__rater_incentive),
                ("total_incentive", self.total_incentive),
                ("pretty_total_incentive", self.round2d__total_incentive),
                ("smart_thermostat_option", self.thermostat_option),
            ]
        )


class APSIncentive2019Tstat(APSIncentive):
    """Adds 200 + 30 * thermostats for 2019 with Thermostat option"""

    def report(self):
        """Report of data"""
        part_one = super(APSIncentive2019Tstat, self).report()
        data = [""]
        msg = "{:<38} {:<10}"
        data.append(msg.format("Option", self.thermostat_option))
        data.append(msg.format("Qty Thermostats", self.thermostat_qty))
        return part_one + "\n".join(data)

    def data(self):
        """Raw data"""
        _data = super(APSIncentive2019Tstat, self).data()
        _data["thermostat_option"] = self.thermostat_option
        _data["thermostat_qty"] = self.thermostat_qty
        return _data

    @property
    def builder_incentive(self):
        """Builder Incentive"""
        incentive = Decimal(self.program.builder_incentive_dollar_value)
        if self.thermostat_option == "complete":
            incentive += Decimal(30.0) * self.thermostat_qty
        return incentive


class APSIncentive2019Addon(APSIncentive2019Tstat):
    """Adds the 30 kicker for homes which already have smart thermostat and the old 2018 program"""

    @property
    def builder_incentive(self):
        """Builder Incentive"""
        if self.thermostat_option in ["complete", "partial"]:
            return Decimal(self.program.builder_incentive_dollar_value) * self.thermostat_qty
        return Decimal(0.0)
