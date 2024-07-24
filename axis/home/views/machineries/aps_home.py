from axis.examine.machinery import ReadonlyMachinery
from axis.customer_aps.api import APSHomeViewSet
from axis.customer_aps.models import APSHome


__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class APSHomeExamineMachinery(ReadonlyMachinery):
    model = APSHome
    type_name = "apshome"
    api_provider = APSHomeViewSet

    detail_template = "examine/home/apshome_detail.html"

    def get_helpers(self, instance):
        helpers = super(APSHomeExamineMachinery, self).get_helpers(instance)

        helpers["legacy_payments"] = [
            {
                "url": h.get_absolute_url(),
                "aps_id": h.aps_id,
            }
            for h in instance.legacyapshome_set.only("id", "aps_id")
        ]

        return helpers
