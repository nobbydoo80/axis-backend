"""
This is a container for things that can't be removed but might not be used anymore.  If that sounds
like a stupid problem to have, dig in and figure out how to truly remove something.
"""


import os

from axis.core.utils import randomize_filename

__author__ = "Autumn Valenta"
__date__ = "8/4/15 10:15 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


# This is stuck in our native migrations files as a dotted path for CompanyDocument.document
def _photo_location(instance, filename):
    """Returns the filesystem location for a Floorplan photo."""
    if not isinstance(filename, str):
        filename = filename.name
    company = instance.answer.user.company
    return os.path.join(
        "documents",
        company.company_type,
        company.slug,
        "answer_images",
        randomize_filename(filename),
    )


def _document_location(instance, filename):
    """Returns the filesystem location for a Floorplan BLG file."""
    if not isinstance(filename, str):
        filename = filename.name
    company = instance.answer.user.company
    return os.path.join(
        "documents",
        company.company_type,
        company.slug,
        "answer_documents",
        randomize_filename(filename),
    )
