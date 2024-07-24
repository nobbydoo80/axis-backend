from axis.examine.machinery import ReadonlyMachinery
from .home import HomeExamineMachinery


__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


# For the checklist app to use.
class HomeExamineReadonlyMachinery(ReadonlyMachinery, HomeExamineMachinery):
    def get_helpers(self, instance):
        return {}
