"""messages.py: """


from axis.messaging.messages import ModernMessage

__author__ = "Artem Hruzd"
__date__ = "11/01/2019 13:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class EquipmentSponsorStatusStateChangedMessage(ModernMessage):
    title = "Equipment state changed"
    content = (
        "Equipment {equipment} for {owner_company} changed state from "
        "<b>{old_state}</b> to <b>{new_state}</b><br>"
        "<a href='{url}#/tabs/equipment' "
        "target='_blank'>View {owner_company} equipment list</a>"
    )
    category = "Company equipment"
    level = "info"
    sticky_alert = True

    verbose_name = "Equipment state changed"
    description = "Sent once the equipment sponsor status state been changed"
