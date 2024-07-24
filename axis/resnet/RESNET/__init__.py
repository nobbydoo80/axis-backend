"""__init__.py: Django RESNET"""


import logging


__author__ = "Steven Klass"
__date__ = "2/16/16 09:48"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def main(args):
    """Main Program - TEst

    :param args: argparse.Namespace
    """
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(filename)s] (%(name)s) %(message)s",
    )

    args.verbose = 4 if args.verbose > 4 else args.verbose
    loglevel = 50 - args.verbose * 10
    log.setLevel(loglevel)

    from django.apps import apps as django_app

    if not django_app.apps_ready:
        import django

        django.setup()

    from axis.home.models import EEPProgramHomeStatus
    from axis.resnet.RESNET.base import RESNET, RESNETAuthenticationError

    status = EEPProgramHomeStatus.objects.get(id=args.home_status_id)

    resnet = RESNET(
        rater_id=args.rater_id,
        provider_id=args.provider_id,
        debug=True,
        home_status=status,
        registry_reason=args.reason,
    )

    try:
        response, response, registryid = resnet.post(dry_run=args.dry_run)
    except RESNETAuthenticationError as err:
        log.error(err)
    else:
        print("Registry ID: {} assigned to {}".format(registryid, status))


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="TEst")
    parser.add_argument(
        "-v",
        "--verbose",
        const=1,
        default=1,
        type=int,
        nargs="?",
        help="increase verbosity: 1=errors, 2=warnings, 3=info, 4=debug. "
        "No number means warning. Default is no verbosity.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Send the debug flag with the data - It's not actually kept",
    )
    parser.add_argument(
        "-D",
        "--dry_run",
        dest="dry_run",
        action="store_true",
        help="Dry Run - Don't submit it - print out the output.",
    )

    parser.add_argument(
        "-r",
        "--rater_id",
        dest="rater_id",
        action="store",
        help="Use the following Rater ID",
        type=str,
        default="5459458",
    )
    parser.add_argument(
        "-p",
        "--provider_id",
        dest="provider_id",
        action="store",
        help="Use the following Provider ID",
        type=str,
        default="1900-003",
    )
    parser.add_argument(
        "-s",
        "--home_status_id",
        dest="home_status_id",
        action="store",
        help="Use the following Project",
        type=int,
        default=29718,
    )
    parser.add_argument(
        "-R",
        "--reason",
        dest="reason",
        action="store",
        help="The reason why you are updating the registry",
    )
    sys.exit(main(parser.parse_args()))
