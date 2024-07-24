"""calculator.py: Django rtf_calculator"""

import argparse
import logging
import os
import sys

from .calculator import NEEAV2Calculator

__author__ = "Steven Klass"
__date__ = "1/11/17 11:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def main(_args):  # pylint: disable=too-many-statements  # noqa: MC0001
    """Main - $<description>$"""
    from django.apps import apps as django_app

    if not django_app.apps_ready:
        import django

        django.setup()

    sys.path.append(os.path.abspath(os.path.abspath(".")))

    kwargs = {
        "us_state": "WA",
        "heating_fuel": "electric",
        "heating_system_config": "central",  # zonal, central, all
        "home_size": "small",  # small, medium, large, all
        "heating_zone": "hz2",  # hz1, hz2, hz3
        "water_heater_tier": "electric resistance",  # tier1, tier2, tier3
        "cfl_installed": 5,
        "led_installed": 35,
        "total_installed_lamps": 40,
        "estar_std_refrigerators_installed": True,
        "estar_dishwasher_installed": True,
        "estar_front_load_clothes_washer_installed": True,
        "clothes_dryer_tier": "tier3",  # tier1, tier2, tier3
        "smart_thermostat_installed": True,
        "qty_shower_head_1p5": 3,
        "qty_shower_head_1p75": 0,
        "code_data": {
            "heating_therms": 30.0,
            "heating_kwh": 10000.0,
            "cooling_kwh": 2100.0,
        },
        "improved_data": {
            "heating_therms": 20.0,
            "heating_kwh": 8000.0,
            "cooling_kwh": 2000.0,
            "primary_heating_type": "heater",  # Add 'heat pump' to get heat_pump recognized
            "primary_cooling_type": "air conditioner",
            "primary_cooling_fuel": "electric",
            "primary_water_heating_type": "gas",  # None, 'gas', 'hpwh', 'electric resistance'
        },
        "percent_improvement": 0.15,
        "electric_utility": "puget-sound-energy",
        "gas_utility": "foo",
    }

    neea_kwargs = kwargs.copy()

    # from axis.home.models import EEPProgramHomeStatus
    # home_status = EEPProgramHomeStatus.objects.get(id=72082)
    # answers = dict(home_status.get_answers_for_home().values_list('question__slug', 'answer'))
    # neea_kwargs = {key.replace('neea-', ''): value for key, value in answers.items()}
    # neea_kwargs['home_status_id'] = home_status.id

    calculator = NEEAV2Calculator(**neea_kwargs)
    print(calculator.report())
    print(calculator.heating_cooling_report())
    print(calculator.hot_water_report())
    print(calculator.lighting_report())
    print(calculator.appliance_report())
    print(calculator.thermostat_report())
    print(calculator.shower_head_report())
    print(calculator.total_report())
    print(calculator.incentives.report())

    print("\n\n")

    manual_kwargs = calculator.dump_simulation(as_dict=True)

    if "home_status_id" in neea_kwargs:
        print("# This was reported on home Project ID: %s" % neea_kwargs["home_status_id"])
    sys.stdout.write("kwargs = ")
    print(calculator.dump_simulation())
    print("\ncalculator = NEEAV2Calculator(**kwargs.copy())\n")

    # print('print(calculator.report())')
    # print('print(calculator.heating_cooling_report())')
    # print('print(calculator.hot_water_report())')
    # print('print(calculator.lighting_report())')
    # print('print(calculator.appliance_report())')
    # print('print(calculator.thermostat_report())')
    # print('print(calculator.shower_head_report())')
    # print('print(calculator.total_report())')
    # print('print(calculator.incentives.report())\n')

    print(
        "self.assertEqual(calculator.{}, '{}')".format(
            "heating_fuel", manual_kwargs["heating_fuel"].lower()
        )
    )
    print(
        "self.assertEqual(calculator.{}, '{}')".format(
            "heating_system_config", manual_kwargs["heating_system_config"].lower()
        )
    )
    print(
        "self.assertEqual(calculator.{}, '{}')".format(
            "home_size", manual_kwargs["home_size"].lower()
        )
    )

    print(
        "self.assertEqual(calculator.{}, '{}')".format(
            "heating_zone", manual_kwargs["heating_zone"].lower()
        )
    )

    if manual_kwargs.get("cfl_installed"):
        print(
            "self.assertEqual(calculator.{}, {})".format(
                "cfl_installed", manual_kwargs["cfl_installed"]
            )
        )
    if manual_kwargs.get("led_installed"):
        print(
            "self.assertEqual(calculator.{}, {})".format(
                "led_installed", manual_kwargs["led_installed"]
            )
        )
    if manual_kwargs.get("total_installed_lamps"):
        print(
            "self.assertEqual(calculator.{}, {})".format(
                "total_installed_lamps", manual_kwargs["total_installed_lamps"]
            )
        )

    if manual_kwargs.get("smart_thermostat_installed") is not None:
        if isinstance(manual_kwargs.get("smart_thermostat_installed"), str):
            value = "False"
            if manual_kwargs["smart_thermostat_installed"].lower() == "yes":
                value = "True"
            print("self.assertEqual(calculator.{}, {})".format("smart_thermostat_installed", value))
        else:
            print(
                "self.assertEqual(calculator.{}, {})".format(
                    "smart_thermostat_installed", manual_kwargs["smart_thermostat_installed"]
                )
            )

    if manual_kwargs.get("qty_shower_head_1p5") is not None:
        print(
            "self.assertEqual(calculator.{}, {})".format(
                "qty_shower_head_1p5", manual_kwargs["qty_shower_head_1p5"]
            )
        )
    if manual_kwargs.get("qty_shower_head_1p75") is not None:
        print(
            "self.assertEqual(calculator.{}, {})".format(
                "qty_shower_head_1p75", manual_kwargs["qty_shower_head_1p75"]
            )
        )

    if manual_kwargs.get("estar_dishwasher_installed") is not None:
        if isinstance(manual_kwargs.get("estar_dishwasher_installed"), str):
            value = "False"
            if manual_kwargs["estar_dishwasher_installed"].lower() == "yes":
                value = "True"
            print("self.assertEqual(calculator.{}, {})".format("estar_dishwasher_installed", value))
        else:
            print(
                "self.assertEqual(calculator.{}, {})".format(
                    "estar_dishwasher_installed", manual_kwargs["estar_dishwasher_installed"]
                )
            )

    if manual_kwargs.get("estar_std_refrigerators_installed") is not None:
        if isinstance(manual_kwargs.get("estar_std_refrigerators_installed"), str):
            value = "False"
            if manual_kwargs["estar_std_refrigerators_installed"].lower() == "yes":
                value = "True"
            print(
                "self.assertEqual(calculator.{}, {})".format(
                    "estar_std_refrigerators_installed", value
                )
            )
        else:
            print(
                "self.assertEqual(calculator.{}, {})".format(
                    "estar_std_refrigerators_installed",
                    manual_kwargs["estar_std_refrigerators_installed"],
                )
            )

    if manual_kwargs.get("estar_front_load_clothes_washer_installed") is not None:
        if isinstance(manual_kwargs.get("estar_std_refrigerators_installed"), str):
            value = "False"
            if manual_kwargs["estar_front_load_clothes_washer_installed"].lower() == "yes":
                value = "True"
            print(
                "self.assertEqual(calculator.{}, {})".format(
                    "estar_front_load_clothes_washer_installed", value
                )
            )
        else:
            print(
                "self.assertEqual(calculator.{}, {})".format(
                    "estar_front_load_clothes_washer_installed",
                    manual_kwargs["estar_front_load_clothes_washer_installed"],
                )
            )

    if manual_kwargs.get("clothes_dryer_tier") == "ENERGY STAR\xae":
        print("self.assertEqual(calculator.{}, '{}')".format("clothes_dryer_tier", "estar"))
    elif manual_kwargs.get("clothes_dryer_tier").lower() in ["tier1", "tier2"]:
        print(
            "self.assertEqual(calculator.{}, '{}')".format(
                "clothes_dryer_tier", manual_kwargs.get("clothes_dryer_tier").lower()
            )
        )
    elif manual_kwargs.get("clothes_dryer_tier", None) == "None":
        print("self.assertEqual(calculator.{}, None)".format("clothes_dryer_tier"))

    for k, v in calculator.result_data(include_reports=False, recalculate=True).items():
        if "pretty" in k:
            continue
        if k == "builder_incentive" and isinstance(v, str):
            if v.startswith("$"):
                v = round(float(v[1:]), 2)
            else:
                continue
        if k in [
            "heating_fuel",
            "heating_system_config",
            "home_size",
            "heating_zone",
            "cfl_installed",
            "led_installed",
            "total_installed_lamps",
            "smart_thermostat_installed",
            "qty_shower_head_1p5",
            "qty_shower_head_1p75",
            "estar_dishwasher_installed",
            "estar_std_refrigerators_installed",
            "estar_front_load_clothes_washer_installed",
            "clothes_dryer_tier",
            "home_status_id",
            "from_db",
        ]:
            continue
        skip = "incentive" in k or k.startswith("bpa") or k.startswith("busbar")
        if skip or k in ["reference_home_kwh"]:
            k = "incentives.{}".format(k)
        if isinstance(v, float):
            if "percent" in k:
                print("self.assertEqual(round(calculator.{}, 3), {})".format(k, round(v, 3)))
            elif "_incentive" in k:
                print("self.assertEqual(round(calculator.{}, 2), {})".format(k, round(v, 3)))
            else:
                print("self.assertEqual(round(calculator.{}, 0), {})".format(k, round(v, 0)))
        if isinstance(v, (int, bool)):
            print("self.assertEqual(calculator.{}, {})".format(k, v))
        elif isinstance(v, str):
            if k == "pct_improvement_method":
                k = "incentives.{}".format(k)
            print("self.assertEqual(calculator.{}, '{}')".format(k, v))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="$<description>$")
    parser.add_argument(
        "-v",
        dest="verbose",
        help="How verbose of the output",
        action="append_const",
        const=1,
        default=[1, 2, 3],
    )
    parser.add_argument("-y", dest="settings", help="Django Settings", action="store")
    parser.add_argument("-n", dest="dry_run", help="Dry Run", action="store_true")
    sys.exit(main(parser.parse_args()))
