from axis.messaging.messages import ModernMessage

__author__ = "Michael Jeffrey"
__date__ = "3/9/17 3:17 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


class HomeSubmittedToRESNETRegistry(ModernMessage):
    title = "Project Submitted to RESNET"
    content = '<a href="{home_url}">{home}</a> {response} {registry_id}'
    category = "RESNET"
    level = "info"

    verbose_name = "Project Submitted to RESNET"

    company_types = ["rater", "provider"]


class RESNETRegistryError(ModernMessage):
    title = "Registry Error"
    content = "We were unable to submit this project to the Registry."
    category = "RESNET"
    level = "error"

    company_types = ["rater", "provider"]
