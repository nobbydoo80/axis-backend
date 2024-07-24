"""__init__.py: Django Reso package container"""


__author__ = "Steven Klass"
__date__ = "06/16/17 09:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]
__license__ = "See the file LICENSE.txt for licensing information."


class RESOUnsupportedException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, "RESO Unsupported:", *args, **kwargs)
