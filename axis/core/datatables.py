import logging

from timezone_field.fields import TimeZoneField

from datatableview.columns import COLUMN_CLASSES, TextColumn

__author__ = "Autumn Valenta"
__date__ = "10/23/15 11:44 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


COLUMN_CLASSES.insert(0, (TextColumn, (TimeZoneField,)))
