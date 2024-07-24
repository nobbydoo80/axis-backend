import logging
import re
from functools import reduce

__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Function for supplying data to clean and the functions to clean it with
def normalize(data, cleaner_functions):
    # Apply all cleaners in succession to the data
    data = reduce((lambda v, f: f(v)), cleaner_functions, data)

    # # This is the debug version because yikes its hard to see what's going on
    # for f in cleaner_functions:
    #     try:
    #         new_data = f(data)
    #     except:
    #         print('!!!', f, repr(data))
    #         raise
    #     else:
    #         print('---', f, repr(data), repr(new_data))
    #         data = new_data

    return data


def normalize_re(pattern, replace):
    def normalize_re(data):
        return re.sub(pattern, replace, data)

    return normalize_re


def normalize_dict_replace(replace_dict):
    def normalize_dict_replace(data):
        pattern = r"\b({})\b".format("|".join(replace_dict.keys()))

        def _rep(match):
            return replace_dict[match.group(1)]

        return normalize_re(pattern, _rep)(data)

    return normalize_dict_replace
