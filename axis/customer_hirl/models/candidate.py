"""candidate.py: """

from django.db import models

__author__ = "Artem Hruzd"
__date__ = "07/26/2020 18:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class Candidate(models.Model):
    """
    DEPRECATED: This model must be removed with Certification model


    ForeignKey link between Certification and a possible matching Home.
    """

    certification = models.ForeignKey("Certification", on_delete=models.CASCADE)
    home = models.ForeignKey("home.Home", on_delete=models.CASCADE)

    levenshtein_distance = models.PositiveIntegerField()
    profile_delta = models.IntegerField()

    class Meta:
        pass

    def __str__(self):
        return "Candidate: %r" % (
            "{}".format(
                self.home,
            )
        )
