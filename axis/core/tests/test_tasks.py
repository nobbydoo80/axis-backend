__author__ = "Artem Hruzd"
__date__ = "06/28/2023 13:24"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from axis.core.tests.testcases import AxisTestCase
from axis.core.tasks import clean_all_duplicate_history_task


class CoreTasksTests(AxisTestCase):
    def test_clean_all_duplicate_history_task(self):
        clean_all_duplicate_history_task.delay()
