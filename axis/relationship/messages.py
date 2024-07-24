"""Modern configurable messages for relationship app."""


from axis.messaging.messages import ModernMessage

try:
    from . import strings
except ImportError:
    from axis.relationship import strings

__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class RelationshipInvitationMessage(ModernMessage):
    title = "Association invitation"
    content = strings.RELATIONSHIP_INVITATION
    sticky_alert = True
    category = "associations"
    level = "info"

    verbose_name = "Automatic invitations"
    description = "Sent when your company automatically receives an association to an Axis item."


class RelationshipInvitationFromCompanyMessage(ModernMessage):
    title = "Association invitation"
    content = strings.RELATIONSHIP_INVITATION_FROM_SOURCE
    sticky_alert = True
    category = "associations"
    level = "info"

    verbose_name = "Invitations"
    description = "Sent when another company adds your company to an Axis item."


class RelationshipInvitationFromCompanyAcceptedMessage(ModernMessage):
    title = "Association invitation"
    content = strings.RELATIONSHIP_INVITATION_FROM_SOURCE_AUTO_ACCEPTED
    sticky_alert = True
    category = "associations"
    level = "info"

    verbose_name = "Auto Accepted Invitation"
    description = "Sent when your company automatically accepts an association to another company."


class RelationshipCreatedMessage(ModernMessage):
    title = "Relationship has been created/updated"
    content = (
        "{action} association between {company} and {object} was initiated by {assigning_company}"
    )
    sticky_alert = True
    category = "relationships"
    level = "success"

    verbose_name = "Relationship created/updated"
    description = "Sent when relationship with company has been created/updated"


class RelationshipRejectedMessage(ModernMessage):
    title = "Relationship has been rejected"
    content = "Association has been rejected between {company} and {object}"
    sticky_alert = True
    category = "relationships"
    level = "warning"

    verbose_name = "Relationship has been rejected"
    description = "Sent when relationship with company has been rejected"


class RelationshipRemovedMessage(ModernMessage):
    title = "Relationship has been removed"
    content = "Removed association between {company} and {object}"
    sticky_alert = True
    category = "relationships"
    level = "warning"

    verbose_name = "Relationship has been removed"
    description = "Sent when relationship with company has been removed"


class RelationshipDeletedMessage(ModernMessage):
    title = "Relationship has been deleted"
    content = "Deleted association between {company} and {object}"
    sticky_alert = True
    category = "relationships"
    level = "warning"

    verbose_name = "Relationship has been deleted"
    description = "Sent when relationship with company has been deleted"


class SponsorPreferencesDoesNotExistMessage(ModernMessage):
    title = "Sponsor Preferences does not exist"
    content = (
        "Company {sponsored_company} has been associated, "
        "but it does not have affiliation by {sponsor}. <a href='{url}'>Click here to add the affiliation.</a>"
    )
    sticky_alert = True
    category = "relationships"
    level = "warning"

    verbose_name = "Relationship created, but company do not have sponsor affiliation"
    description = "Sent when relationship created, but do not have sponsor affiliation"
