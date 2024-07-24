"""apps.py: """


from django.conf import settings

from axis.core import platform

__author__ = "Artem Hruzd"
__date__ = "10/29/2019 16:21"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


equipment_settings = getattr(settings, "EQUIPMENT", {})


class EquipmentConfig(platform.PlatformAppConfig):
    name = "axis.equipment"

    # Make sure that you will run track_equipment_company_sponsor_statuses
    # management command after you modify this requirements
    EQUIPMENT_APPLICABLE_REQUIREMENTS = equipment_settings.get(
        "EQUIPMENT_APPLICABLE_REQUIREMENTS",
        {
            "provider-washington-state-university-extension-ene": [
                "wsu-hers-2020",
            ],
            "provider-home-innovation-research-labs": [
                "ngbs-2020-sf-demo-program",
                "ngbs-2015-sf-demo-program",
            ],
        },
    )
    EQUIPMENT_APPLICABLE_PROGRAMS = sorted(
        {x for v in iter(EQUIPMENT_APPLICABLE_REQUIREMENTS.values()) for x in v}
    )
    EQUIPMENT_APPLICABLE_COMPANIES_SLUGS = list(EQUIPMENT_APPLICABLE_REQUIREMENTS.keys())
