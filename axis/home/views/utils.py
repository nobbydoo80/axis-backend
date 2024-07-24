from axis.home.models import EEPProgramHomeStatus

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


def _get_home_contributor_flag(home, user):
    """
    Until we string up homes with Association instances, we have to read them from the homestatuses
    on the home in question.  Deriving the flag's value in this case is a verbose hassle.

    Returns True if any association exists with is_contributor=True
    Returns False if associations exist but none with is_contributor=True
    Returns True if no associations exist (because we assume relationships got them here).
    """
    # Having mixed 'contributor' flags between homestatuses will always yield True at the home
    # level.
    association_model_class = EEPProgramHomeStatus.associations.rel.related_model
    associations = association_model_class.objects.filter(eepprogramhomestatus__home=home)
    return associations.is_contributor(user, default=True)
