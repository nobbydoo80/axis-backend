"""
This is a container for things that can't be removed but might not be used anymore.  If that sounds
like a stupid problem to have, dig in and figure out how to truely remove something.
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
def _content_file_name(instance, filename):
    # This is an upload_to handler
    if not isinstance(filename, str):
        filename = filename.name
    return os.path.join(
        "documents",
        instance.company.company_type,
        instance.company.slug,
        "company_shared",
        instance.shared_company.slug,
        randomize_filename(filename),
    )
