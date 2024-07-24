"""__init__.py: Django """


import logging

from .base import APSBase

__author__ = "Steven Klass"
__date__ = "4/6/18 12:40 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class SimulatedInputBase(APSBase):
    """Simulation base class to be used by either the REM/Rate or Ekotrope"""

    def __init__(self, **kwargs):
        self.source = "JSON data"
        self.simulation = kwargs.get("simulation", {})

    @property
    def hers_score(self):
        """The HERS score"""
        return self.simulation.get("hers_score")

    @property
    def non_pv_hers_score(self):
        """The HERS score without PV"""
        return self.simulation.get("non_pv_hers_score", self.simulation.get("hers_score"))

    @property
    def climate_zone(self):
        """The Climate Zone of the Simulations"""
        return self.simulation.get("climate_zone")

    def report(self):
        """The Report out of the simulation data"""
        data = []
        data.append("\n--- Simulation data: ----")
        msg = "{:<60}: {}"
        data.append(msg.format("Climate Zone", self.climate_zone))
        data.append(msg.format("HERS Score", self.hers_score))
        data.append(msg.format("HERS Non PV Score", self.non_pv_hers_score))
        return "\n".join(data)

    @property
    def data(self):
        """The data"""
        return {
            "climate_zone": self.climate_zone,
            "hers_score": self.hers_score,
            "non_pv_hers_score": self.non_pv_hers_score,
        }


class RemRateSimulation(SimulatedInputBase):
    """REM/Rate Simulation specific"""

    def __init__(self, **kwargs):
        super(RemRateSimulation, self).__init__(**kwargs)
        self.source = "Rem/Rate data"
        from axis.remrate_data.models import Simulation

        self.simulation_id = kwargs.get("simulation_id")
        self.simulation = Simulation.objects.get(id=self.simulation_id)

    @property
    def hers_score(self):
        """The HERS score"""
        return self.simulation.hers.score

    def get_score_attribute(self):
        """Which Score Attribute to use"""
        if self.simulation.energystar.energy_star_v3p2_pv_score:
            return "energy_star_v3p2_pv_score"
        elif self.simulation.energystar.energy_star_v3p1_pv_score:
            return "energy_star_v3p1_pv_score"
        elif self.simulation.energystar.energy_star_v3_pv_score:
            return "energy_star_v3_pv_score"
        elif self.simulation.energystar.energy_star_v2p5_pv_score:
            return "energy_star_v2p5_pv_score"
        return "N/A"

    @property
    def non_pv_hers_score(self):
        """The HERS score without PV"""
        return getattr(self.simulation.energystar, self.get_score_attribute())

    @property
    def climate_zone(self):
        """The Climate Zone of the Simulations"""
        return int(self.simulation.site.climate_zone[0])


class EkotropeSimulation(SimulatedInputBase):
    """Ekotrope Simulation specific"""

    def __init__(self, **kwargs):
        super(EkotropeSimulation, self).__init__(**kwargs)
        self.source = "Ekotrope data"
        from axis.ekotrope.models import HousePlan

        self.house_plan_id = kwargs.get("house_plan_id")
        self.house_plan = HousePlan.objects.get(id=self.house_plan_id)

    @property
    def hers_score(self):
        """The HERS score"""
        return self.house_plan.analysis.data.get("hersScore", 1e6)

    @property
    def non_pv_hers_score(self):
        """The HERS score without PV"""
        return self.house_plan.analysis.data.get("hersScoreNoPv", 1e6)

    @property
    def climate_zone(self):
        """The Climate Zone of the Simulations"""
        return self.house_plan.project.data.get("location", {}).get("climateZone", {}).get("zone")
