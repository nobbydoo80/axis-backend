"""utils.py Testing useful functions"""


import os

from django.conf import settings

__author__ = "Artem Hruzd"
__date__ = "06/11/19 09:19"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]


def mock_provider_start_page_data(provider_key):
    """Fake the data with static pages obtained prior to this"""
    sources = os.path.join(settings.SITE_ROOT, "axis", "resnet", "sources")
    providers_map = {
        "RESENTProvider": os.path.join(sources, "providers.html"),
        "RESNETSamplingProvider": os.path.join(sources, "sampling_providers.html"),
        "RESNETTrainingProvider": os.path.join(sources, "training_providers.html"),
        "RESNETWaterSenseProvider": os.path.join(sources, "water_sense_providers.html"),
    }

    with open(providers_map[provider_key], "r") as f:
        return f.read()
