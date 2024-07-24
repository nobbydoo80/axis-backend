"""certification_metric.py: """


from axis.core.api import UserCertificationMetricViewSet
from axis.core.forms import UserCertificationMetricForm
from axis.examine import TableMachinery
from axis.home.models import EEPProgramHomeStatus

__author__ = "Artem Hruzd"
__date__ = "11/28/2019 15:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class UserCertificationMetricExamineMachinery(TableMachinery):
    model = EEPProgramHomeStatus
    form_class = UserCertificationMetricForm
    type_name = "user_certification_metric"
    api_provider = UserCertificationMetricViewSet

    can_add_new = False

    regionset_template = "examine/user/certification_metric_regionset_datatable.html"
    region_template = "examine/user/certification_metric_region_tablerow.html"
    detail_template = "examine/user/certification_metric_default_tablerow.html"

    def can_edit_object(self, instance, user=None):
        return False

    def can_delete_object(self, instance, user=None):
        return False

    def get_region_dependencies(self):
        return {
            "user": [
                {
                    "field_name": "id",
                    "serialize_as": "rater_of_record",
                }
            ],
        }
