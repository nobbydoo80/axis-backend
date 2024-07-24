"""strings.py: Django relationship"""


import logging

__author__ = "Steven Klass"
__date__ = "6/23/14 2:10 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

RELATIONSHIP_USED_CREATE = "{create} association between {company} and {object}"

RELATIONSHIP_INVITATION = """{company} has been invited to have an association with {verbose_name} {object}.  Click <a href="{url}">here</a> to see available {verbose_name} associations"""
RELATIONSHIP_INVITATION_FROM_SOURCE = """{source} has invited {company} to have an association with {verbose_name} {object}.  Click <a href="{url}">here</a> to see available {verbose_name} associations"""
RELATIONSHIP_INVITATION_FROM_SOURCE_AUTO_ACCEPTED = (
    """{company} has automatically been associated with {object}."""
)
