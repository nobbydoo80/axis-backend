"""utility_rate.py: Django factories"""

import random

from ...models import UtilityRate, SeasonalRate, Block

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def utility_rate_factory(simulation, _result_number, **kwargs):
    blg_data = kwargs.pop("blg_data", None)

    if blg_data:
        for idx, item in enumerate(blg_data):
            rate = UtilityRate.objects.create(
                simulation=simulation,
                _result_number=_result_number,
                _source_utility_rate_no=_result_number + idx,
                name=item["name"],
                fuel_type=item["fuel_type"],
                units=item["fuel_type_units"],
            )
            for sidx, rem_season in enumerate(item.get("seasons")):
                season = SeasonalRate.objects.create(
                    simulation=simulation,
                    _result_number=_result_number,
                    rate=rate,
                    _utility_rate_no=_result_number + idx,
                    _source_seasonal_rate_number=_result_number + sidx,
                    start_month=rem_season["start"],
                    end_month=rem_season["end"],
                    cost=rem_season["service_charge"],
                )
                for ridx, rem_rate in enumerate(rem_season.get("rates")):
                    Block.objects.create(
                        simulation=simulation,
                        _result_number=_result_number,
                        seasonal_rate=season,
                        _seasonal_rate_number=_result_number + sidx,
                        max_consumption=rem_rate["max"],
                        dollars_per_unit_per_month=rem_rate["rate"],
                    )
    else:
        for idx, (fuel, unit) in enumerate([(1, 4), (4, 1)]):
            rate = UtilityRate.objects.create(
                simulation=simulation,
                _result_number=_result_number,
                _source_utility_rate_no=_result_number + idx,
                name="Fuel %s" % fuel,
                fuel_type=fuel,
                units=unit,
            )
            for sidx, (start, end) in enumerate([(1, 3), (3, 12)]):
                season = SeasonalRate.objects.create(
                    simulation=simulation,
                    _result_number=_result_number,
                    rate=rate,
                    _utility_rate_no=_result_number + idx,
                    _source_seasonal_rate_number=_result_number + sidx,
                    start_month=start,
                    end_month=end,
                    cost=random.randint(0, 5) + random.random(),
                )
                for ridx, consumption in enumerate([10, 1000, 10000]):
                    Block.objects.create(
                        simulation=simulation,
                        _result_number=_result_number,
                        seasonal_rate=season,
                        _seasonal_rate_number=_result_number + sidx,
                        max_consumption=consumption,
                        dollars_per_unit_per_month=random.randint(0, 5) + random.random(),
                    )
