import os
import mimetypes

__author__ = "Steven Klass"
__date__ = "03/13/22 16:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Benjamin Stürmer"]


def get_mimetype_category(filename):
    """
    Returns a mimetype major category, or if that major category is 'application' it turns instead
    the minor category.  Images return 'image' (from 'image/png', etc), and office documents return
    their gobblygook in 'application/ms-asdfasdfsadf'
    """
    type = mimetypes.guess_type(filename)[0]
    if type is None:
        # Return the extension text (without leading ".")
        return os.path.splitext(filename)[-1][1:]
    major, minor = type.split("/", 1)
    if major == "application":
        # Return the specific sub type. "application" isn't really the clarifying component
        return minor

    # Major type is categorically specific enough for a frontend decision
    return major
