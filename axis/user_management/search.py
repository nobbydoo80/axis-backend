"""search.py: """


from appsearch.registry import ModelSearch, search

from axis.user_management.models import Training, Accreditation

__author__ = "Artem Hruzd"
__date__ = "02/27/2020 20:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class TrainingSearch(ModelSearch):
    display_fields = (
        ("User", "trainee"),
        ("Name", "name"),
    )

    search_fields = ("name", {"trainee": ("first_name", "last_name")})

    def user_has_perm(self, user):
        return True


class AccreditationSearch(ModelSearch):
    display_fields = (
        ("User", "trainee"),
        ("Accreditation ID", "accreditation_id"),
        ("Name", "name"),
    )

    search_fields = ("accreditation_id", {"trainee": ("first_name", "last_name")})

    def user_has_perm(self, user):
        return True


search.register(Training, TrainingSearch)
search.register(Accreditation, AccreditationSearch)
