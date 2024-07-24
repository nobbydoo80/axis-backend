"""Modern configurable messages for company app."""


from axis.messaging.messages import ModernMessage
from . import strings

__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CompanyProfileUpdateMessage(ModernMessage):
    content = strings.COMPANY_PROFILE_UPDATED
    sticky_alert = True
    category = "profile"
    level = "info"

    verbose_name = "Company Profile Updates"
    description = "Sent when someone updates your company information."


class HVACContractorHQUITOStatusSingleMessage(ModernMessage):
    content = strings.HVAC_HQUITO_STATUS_SINGLE
    sticky_alert = True
    category = "company"
    level = "warning"

    verbose_name = "HVAC H-QUITO Status on a project changed"
    description = (
        "Sent when someone adds an HVAC Contractor to a program on a project and "
        "it's H-QUITO status is not accredited or unknown."
    )

    unique = True


class HVACContractorHQUITOStatusMultipleMessage(ModernMessage):
    content = strings.HVAC_HQUITO_STATUS_MULTIPLE
    sticky_alert = True
    category = "company"
    level = "warning"

    verbose_name = "HVAC H-QUITO Status on multiple projects"
    description = (
        "Sent when someone adds an HVAC Contractor to a program on a multiple projects and "
        "it's H-QUITO status is not accredited or unknown."
    )

    unique = True


class EquipmentCreatedSponsorCompanyMessage(ModernMessage):
    title = "Equipment created"
    content = (
        "New equipment {equipment} created by {owner_company} "
        '<a href="{url}#/tabs/equipment" '
        "target='_blank'>View equipment list</a>"
    )
    category = "Company equipment"
    level = "info"
    sticky_alert = True

    verbose_name = "Equipment created"
    description = "Sent when new equipment has been created"
