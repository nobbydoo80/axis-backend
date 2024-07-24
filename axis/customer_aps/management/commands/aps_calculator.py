"""aps_calculator.py: Django """


import logging.config

from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.core.management import BaseCommand, CommandError

from axis.customer_aps.aps_calculator.calculator import APSCalculator
from axis.home.models import Home, EEPProgramHomeStatus

__author__ = "Steven Klass"
__date__ = "02/12/2019 14:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Runs APS Calculator for a give home/homestatus"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--home", action="store", dest="home", type=int, help="Home ID")
        parser.add_argument(
            "--home-status", action="store", dest="home_status", type=int, help="Project ID"
        )
        parser.add_argument("--user", action="store", dest="user", help="User ID or username")

    def set_options(self, home=None, home_status=None, user=None, **_options):
        if not any([home, home_status]):
            raise CommandError("You must supply a home, home_status")

        result = {}
        if home:
            try:
                home = Home.objects.get(id=home)
            except Home.DoesNotExist:
                raise CommandError("Home with ID %s does not exist" % home)
            log.info("Using %s" % home)

        if home_status:
            try:
                home_status = EEPProgramHomeStatus.objects.get(id=home_status)
            except EEPProgramHomeStatus.DoesNotExist:
                raise CommandError("EEPProgramHomeStatus with ID %s does not exist" % home_status)
            log.info("Using %s" % home_status)
            result["home_status"] = home_status

        if home and not home_status:
            try:
                home_status = home.homestatuses.get()
            except MultipleObjectsReturned:
                raise CommandError(
                    "Multiple Programs on home with ID %s exist and no program given" % home.pk
                )
            log.info("Derived %s" % home_status)
            result["home_status"] = home_status

        if user:
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise CommandError("User with ID %s does not exist" % user)
            except ValueError:
                try:
                    user = User.objects.get(username=user)
                except User.DoesNotExist:
                    raise CommandError("User with username %s does not exist" % user)
            log.info("Using %s" % user)
            result["user"] = user
            log.info("Derived %s" % user.company)
            result["company"] = user.company
        else:
            if home_status:
                user = home_status.company.users.filter(is_active=True).first()
            else:
                raise CommandError("No user provided given the options")
            log.info("Derived %s" % user)
            result["user"] = user
            log.info("Derived %s" % user.company)
            result["company"] = user.company

        return result

    def handle(self, *args, **options):
        kwargs = self.set_options(**options)

        kwargs = {
            "us_state": kwargs.get("home_status").home.state,
            "home_status_id": kwargs.get("home_status").pk,
        }

        calculator = APSCalculator(**kwargs)
        print(calculator.report())
        print(calculator.simulation.report())
        print(calculator.incentives.report())

        print("\nTest Bench\n")
        manual_kwargs = calculator.dump_simulation(as_dict=True)

        if "home_status_id" in kwargs:
            print("# This was reported on home Project ID: %s" % kwargs["home_status_id"])
        print(calculator.dump_simulation())
        print("\ncalculator = APSCalculator(**kwargs.copy())\n")
        print(
            "self.assertEqual(calculator.{}, {})".format(
                "climate_zone", manual_kwargs["climate_zone"]
            )
        )
        print(
            "self.assertEqual(calculator.simulation.{}, {})".format(
                "hers_score", manual_kwargs["simulation"].get("hers_score")
            )
        )
        print(
            "self.assertEqual(calculator.simulation.{}, {})".format(
                "non_pv_hers_score", manual_kwargs["simulation"].get("non_pv_hers_score")
            )
        )
        print("self.assertEqual(calculator.{}, '{}')".format("program", calculator.program))
        if calculator.program != kwargs.get("program"):
            print(" # TWEAK PROGRAM TO BE {}".format(kwargs.get("program")))
            print(
                "self.assertNotEqual(calculator.{}, {})".format("program", "kwargs.get('program')")
            )

        from axis.eep_program.models import EEPProgram

        EEPProgram.objects.get(slug=calculator.program)
        print(
            "self.assertEqual(calculator.incentives.{}, {})".format(
                "builder_incentive", calculator.incentives.builder_incentive
            )
        )
        print(
            "self.assertEqual(calculator.incentives.{}, {})".format(
                "rater_incentive", calculator.incentives.rater_incentive
            )
        )
        print(
            "self.assertEqual(calculator.incentives.{}, {})".format(
                "total_incentive", calculator.incentives.total_incentive
            )
        )
        print(
            "self.assertEqual(calculator.incentives.{}, {})".format(
                "has_incentive", calculator.incentives.has_incentive
            )
        )
