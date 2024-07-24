"""Modern configurable messages for subdivision app."""


from axis.messaging.messages import ModernMessage
from . import strings

__author__ = "Autumn Valenta"
__date__ = "5/1/15 11:04 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class SubdivisionAvailableForREMUploads(ModernMessage):
    content = strings.SUBDIVISION_AVAILABLE_FOR_REM_UPLOADS
    category = "subdivision"
    level = "info"

    verbose_name = "REM/Rate™ uploads enabled"
    description = "Sent when the provider is associated to a new subdivision."

    unique = True
    company_types = ["provider"]
