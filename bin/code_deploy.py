#!/usr/bin/env python3
"""code_deploy.py - This script is used as part of the code deploy process where
the appsepc.yml file is read"""

__author__ = "Steven K"
__date__ = "4/5/20 12:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import argparse
import logging
import os
import sys

from infrastructure.amazon.code_deploy import (
    application_stop,
    before_install,
    after_install,
    application_start,
    validate_service,
)
from infrastructure.utils.logging_utils import add_json_logger


def main(args):
    """Main code_deploy script script"""

    life_cycle_event = os.environ.get("LIFECYCLE_EVENT")
    if not life_cycle_event:
        raise KeyError(
            "Expecting environment var LIFECYCLE_EVENT - cannot be called directly; "
            "called during code deploy"
        )

    log_level = {0: 25, 1: logging.INFO, 2: logging.DEBUG}.get(min([2, len(args.verbose)]))
    log_file = os.path.join(
        "/var/log" if os.path.isdir("/var/log") else "/tmp", "launch_host.log"  # nosec
    )
    log = add_json_logger(log=logging.getLogger(), log_level=log_level, filename=log_file)

    if life_cycle_event == "ApplicationStop":
        return application_stop()

    if life_cycle_event == "BeforeInstall":
        return before_install()

    if life_cycle_event == "AfterInstall":
        return after_install()

    if life_cycle_event == "ApplicationStart":
        return application_start()

    if life_cycle_event == "ValidateService":
        return validate_service()

    log.error(
        "No lifecycle event found for %(life_cycle_event)r", {"life_cycle_event": life_cycle_event}
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy a host.")
    parser.add_argument(
        "-v",
        dest="verbose",
        help="How verbose of the output",
        action="append_const",
        const=1,
        default=[
            1,
        ],
    )
    sys.exit(main(parser.parse_args()))
