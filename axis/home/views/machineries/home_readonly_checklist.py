from .home_readonly import HomeExamineReadonlyMachinery

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


# For the checklist app to use.
class HomeExamineReadonlyChecklistMachinery(HomeExamineReadonlyMachinery):
    detail_template = "examine/home/home_detail_no_sidebar.html"
