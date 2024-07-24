"""green_energy_badge.py: """

__author__ = "Artem Hruzd"
__date__ = "04/08/2021 17:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.db import models


class GreenEnergyBadgeQuerySet(models.QuerySet):
    def filter_by_eep_program(self, slug):
        """
        :param slug: string EEPProgram slug
        :return: QuerySet
        """
        if slug in ["ngbs-sf-new-construction-2020-new", "ngbs-mf-new-construction-2020-new"]:
            return self
        elif slug in [
            "ngbs-sf-whole-house-remodel-2020-new",
            "ngbs-mf-whole-house-remodel-2020-new",
        ]:
            return self.exclude(slug="zero_water")

        return self.none()
