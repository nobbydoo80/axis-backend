"""ekotrope.py: Django ekotrope"""


import codecs
import datetime
import json
import logging
import os
import random
import re
from collections import defaultdict

__author__ = "Steven Klass"
__date__ = "1/7/16 09:09"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

ROOT = os.path.dirname(os.path.realpath(__file__))


def json_serial(obj):  # pylint: disable=inconsistent-return-statements
    """Allow JSON Formatter to handle datetimes"""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()


def main(args):
    """Main Program - Parse some data

    :param args: argparse.Namespace
    """
    from django.apps import apps
    from django.conf import settings

    apps.populate(settings.INSTALLED_APPS)

    from axis.ekotrope.Ekotrope.simulate import SimulationEngine
    from axis.remrate_data.models import Simulation

    # Set up a nice logging methodology.
    log = logging.getLogger(__name__)

    # simulations = Simulation.objects.filter_for_ekotrope(version__in=['14.5.1', '14.6', '14.6.1'])
    versions = [
        "14.0",
        "14.1",
        "14.2",
        "14.3",
        "14.4",
        "14.4.1",
        "14.5 ",
        "14.5.1 ",
        "14.6 ",
        "14.6.1 ",
        "15.0 ",
    ]
    # versions = ['14.0', '14.1', '14.2', '14.3', '14.4', '14.4.1',]
    # versions = ['14.5.1 ', '14.6 ', '14.6.1 ', '15.0 ']
    simulations = Simulation.objects.filter_for_ekotrope(version__in=versions)
    if args.send_blg_file:
        simulations = simulations.filter(floorplan__remrate_data_file__isnull=False)

    simulation_ids = list(simulations.values_list("id", flat=True))
    if args.simulation_id or args.simulation_id_ask:
        if args.simulation_id_ask:
            while True:
                try:
                    args.simulation_id = int(input("Simulation ID: "))
                    break
                except:
                    print("Invalid")
        simulations = simulations.filter(id=args.simulation_id)
        if not simulations.count():
            print("Warning:  This is not in Ekotrope filter")
        else:
            simulation_ids = [args.simulation_id]

    if not args.dry_run:
        print("{} Simulations to draw from".format(len(simulation_ids)))

    if args.randomize:
        random.shuffle(simulation_ids)

    if args.send_blg_file and args.anonymize:
        log.warning("Skipping anonymize as it conflicts with sending blg data")
        args.anonymize = False

    kwargs = {
        "anonymize": args.anonymize,
        "add_expected_hers": args.add_expected_hers,
        "send_blg_file": args.send_blg_file,
        "dry_run": args.dry_run,
    }
    e = SimulationEngine(**kwargs)

    results = defaultdict(list)
    _line = "{} {!s:<6} {!s:<6} {!s:<65} {!s:<8} {!s:<8} {!s:<8} {!s:<8}"
    if not args.dry_run:
        print(_line.format(" ", "SimID", "Home", "Address", "EKO", "REM", "% Err", "Abs D"))

    run = datetime.datetime.now().strftime("%m%d%Y-%H%M")

    if not os.path.isdir(os.path.join(ROOT, "results")):
        os.mkdir(os.path.join(ROOT, "results"))

    result_dir = os.path.join(ROOT, "results", run)
    if not os.path.isdir(result_dir):
        os.mkdir(result_dir)

    max_count = args.max_simulations or len(simulation_ids)
    temp_max_count = int(max_count)

    for idx, simulation_id in enumerate(simulation_ids, start=1):
        if idx > temp_max_count:
            break
        simulation = Simulation.objects.get(id=simulation_id)
        home = simulation.floorplan.homestatuses.first().home
        if args.send_blg_file:
            skip = False
            if simulation.floorplan.remrate_data_file:
                if not os.path.exists(simulation.floorplan.remrate_data_file.path):
                    skip = True
            else:
                skip = True
            if skip:
                temp_max_count += 1
                continue

        try:
            result = e.simulate(simulation=simulation)
        except:
            log.exception("Issue with simulation {} - skipping".format(simulation.id))
            temp_max_count += 1
            continue

        results["simulation_ids"].append(simulation.id)
        results["home_id"].append(home.id)
        results["home"].append(re.sub(r",", "", home.get_addr(1)))
        results["date"].append(datetime.datetime.now().strftime("%m/%d/%Y %H:%M%S"))
        if not args.dry_run:
            key = "failures"
            if e.success:
                results["passing"].append(True)
                key = "passed"
                abs_delta = abs(simulation.hers.score - result.get("hersValue"))
                try:
                    pct_error = (abs_delta / simulation.hers.score) * 100.0
                except ZeroDivisionError:
                    pct_error = 100

                print(
                    _line.format(
                        "+",
                        simulation.id,
                        home.id,
                        home.get_addr(1),
                        round(result.get("hersValue"), 2),
                        simulation.hers.score,
                        round(pct_error, 2),
                        round(abs_delta, 2),
                    )
                )
                results["expected"].append(simulation.hers.score)
                results["received"].append(result.get("hersValue"))
                results["pct_error"].append(pct_error)
                results["abs_delta"].append(abs_delta)

                output = os.path.join(result_dir, "{}.json".format(simulation.id))
                with open(output, "wb") as fp:
                    fp.write(json.dumps(result, indent=4, default=json_serial))

            else:
                results["passing"].append(False)
                results["expected"].append(simulation.hers.score)
                results["received"].append(None)
                results["pct_error"].append(None)
                results["abs_delta"].append(None)
                print(
                    _line.format(
                        "-", simulation.id, home.id, home.get_addr(1), "--", "--", "--", "--"
                    )
                )
            results[key].append(result)
            if args.simulation_id:
                print(json.dumps(result, indent=4, default=json_serial))
        else:
            print(result)
            if args.simulation_id:
                output = os.path.join(result_dir, "{}.xml".format(args.simulation_id))
                with open(output, "wb") as fp:
                    fp.write(result)
                print("\n Output saved to {}".format(output))

    if args.dry_run:
        return

    abs_delta = [x for x in results.get("pct_error") if x]
    try:
        abs_pct = (float(len([x for x in abs_delta if x < 2])) / float(len(abs_delta))) * 100
    except ZeroDivisionError:
        abs_pct = 0

    pct_errors = [x for x in results.get("pct_error") if x]
    try:
        mean_pct_error = sum(pct_errors) / len(pct_errors)
    except ZeroDivisionError:
        mean_pct_error = 0

    total = max_count

    with codecs.open(os.path.join(result_dir, "results.csv"), "ab", encoding="utf-8") as fp:
        for idx in range(len(results.get("simulation_ids"))):
            data = [
                run,
                "{}".format(results["passing"][idx]),
                "{}".format(results["simulation_ids"][idx]),
                "{}".format(results["home_id"][idx]),
                results["home"][idx],
                "{}".format(results["expected"][idx]),
                "{}".format(results["received"][idx]),
                "{}".format(results["pct_error"][idx]),
                "{}\n".format(results["abs_delta"][idx]),
            ]
            fp.write(",".join(data))
        fp.write(
            "\n**Total: {} -- {}/{} successfully analyzed.  Of those analyzed mean pct error: {}%  Pct with a absolute delta < 2 points: {}%**".format(
                total, len(results["passed"]), total, round(mean_pct_error, 2), round(abs_pct, 2)
            )
        )

    with codecs.open(os.path.join(result_dir, "failures.json"), "ab", encoding="utf-8") as fp:
        fp.write(json.dumps(results["failures"], indent=4, default=json_serial))

    import pprint

    print("\n" + "--" * 40)

    data = {}
    for item in results["failures"]:
        if not data.get(item.get("class")):
            data[item.get("class")] = {}
        if item.get("exception"):
            if not data[item.get("class")].get(item.get("exception")):
                data[item.get("class")][item.get("exception")] = 0
            data[item.get("class")][item.get("exception")] += 1
        else:
            if not data[item.get("class")].get("count"):
                data[item.get("class")]["count"] = 0
            data[item.get("class")]["count"] += 1

    print("\nError Summary:")
    pprint.pprint(data)

    print(
        "\n**Total: {} -- {}/{} successfully analyzed.  Of those analyzed mean pct error: {}%  Pct with a absolute delta < 2 points: {}%**".format(
            total, len(results["passed"]), total, round(mean_pct_error, 2), round(abs_pct, 2)
        )
    )


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="This will convert blg files or simualtion ids to XML"
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        help="How verbose of the output",
        action="append_const",
        const=1,
        default=[],
    )
    parser.add_argument(
        "-m", dest="max_simulations", help="Max Simulations", action="store", default=10
    )
    parser.add_argument("-B", dest="send_blg_file", help="Send BLG File", action="store_true")
    parser.add_argument("-S", dest="simulation_id", help="Axis Simulation ID", type=int)
    parser.add_argument(
        "-s", dest="simulation_id_ask", help="Ask for the simulation id", action="store_true"
    )
    parser.add_argument(
        "-A", dest="anonymize", help="Do not anonymize the data", action="store_false"
    )
    parser.add_argument(
        "-D", dest="dry_run", help="Do not send the data - print xml", action="store_true"
    )
    parser.add_argument(
        "-E", dest="add_expected_hers", help="Add the expected hers results", action="store_true"
    )
    parser.add_argument("-R", dest="randomize", help="Do not randomize", action="store_false")

    sys.exit(main(parser.parse_args()))
