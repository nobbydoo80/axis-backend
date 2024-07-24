from axis.resnet.RESNET.base import RESNET, RESNETMissingID, RESNETCertificationError

__author__ = "Michael Jeffrey"
__date__ = "3/6/17 10:02 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


def user_can_submit_to_resnet_registry(stat, user):
    if user.is_superuser:
        return True

    try:
        RESNET(home_status=stat, provider_user=user, rater_of_record=stat.rater_of_record)
    except (RESNETMissingID, RESNETCertificationError, AttributeError) as e:
        return False

    return True


def get_resnet_registry_action():
    return {
        "name": "Submit to RESNET Registry",
        "instruction": "resnet",
        "style": "primary",
        "icon": "rocket",
    }
