import os
import logging


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class AppException(Exception):
    pass


class MissingSettingError(AppException):
    pass


class MissingFormatKwargError(AppException):
    pass
