"""utils.py: Django resnet"""


from .RESNET.base import RESNET
from .messages import HomeSubmittedToRESNETRegistry, RESNETRegistryError

import logging

__author__ = "Steven Klass"
__date__ = "2/16/16 09:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def submit_home_status_to_registry(home_status, user):
    log.info("%s submitting %s to the RESNET Registry", user, home_status)
    resnet = RESNET(
        home_status=home_status, provider_user=user, rater_of_record=home_status.rater_of_record
    )

    try:
        response_code, response, registry_id = resnet.post()
    except Exception as err:
        log.exception(err)
        message = RESNETRegistryError()
        message.content = "We were unable to submit this home to the Registry.\n{}".format(err)
        message.send(user=user)
        return False
    else:
        context = {
            "home_url": home_status.get_absolute_url(),
            "home": home_status.home.get_addr(),
            "response": response,
            "registry_id": registry_id,
        }
        HomeSubmittedToRESNETRegistry().send(user=user, context=context)
        HomeSubmittedToRESNETRegistry().send(
            company=home_status.rater_of_record.company, context=context
        )

        return True
