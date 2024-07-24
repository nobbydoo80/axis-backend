"""track_equipment_company_sponsor_statuses.py: """

from django.apps import apps
from django.core.management import BaseCommand

from axis.company.models import Company
from axis.eep_program.models import EEPProgram
from axis.equipment.models import Equipment, EquipmentSponsorStatus

__author__ = "Artem Hruzd"
__date__ = "11/08/2019 17:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

equipment_app = apps.get_app_config("equipment")


class Command(BaseCommand):
    help = (
        "Track equipment applicable programs and companies "
        "to create/remove EquipmentCompanyStatuses when requirements changed"
    )
    requires_system_checks = []

    def _boolean_input(self, question, default=None):
        result = input("%s " % question)
        if not result and default is not None:
            return default
        while len(result) < 1 or result[0].lower() not in "yn":
            result = input("Please answer yes or no: ")
        return result[0].lower() == "y"

    def handle(self, *args, **options):
        msg = (
            "This action will create new statuses for new applicable companies. "
            "Do you want to continue? [y/N]"
        )
        if not self._boolean_input(question=msg):
            return

        created_count = 0

        for equipment in Equipment.objects.all():
            for (
                applicable_company_slug,
                applicable_programs,
            ) in equipment_app.EQUIPMENT_APPLICABLE_REQUIREMENTS.items():
                program = (
                    EEPProgram.objects.filter_by_company(equipment.owner_company)
                    .filter(slug__in=applicable_programs)
                    .first()
                )
                if program:
                    (
                        equipment_sponsor_status,
                        created,
                    ) = EquipmentSponsorStatus.objects.get_or_create(
                        equipment=equipment,
                        company=Company.objects.get(slug=applicable_company_slug),
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS("Added {}".format(equipment_sponsor_status))
                        )

        self.stdout.write(self.style.SUCCESS("Totally created {} statuses".format(created_count)))
