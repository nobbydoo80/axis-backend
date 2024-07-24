"""reports.py: """


import datetime
import os
import re

from django.utils import formats
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.drawing.image import Image
from openpyxl.styles import colors, fills, PatternFill, Font, Alignment
from openpyxl.styles import numbers as excel_numbers

__author__ = "Artem Hruzd"
__date__ = "12/13/2019 20:44"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AxisReportFormatter(object):
    """
    Helper class to format Excel documents in Axis style
    """

    CURRENCY_FORMAT = excel_numbers.FORMAT_CURRENCY_USD_SIMPLE
    PERCENTAGE_FORMAT = "0.00%"
    NUMBER_FORMAT = excel_numbers.FORMAT_NUMBER
    FLOAT_FORMAT = excel_numbers.FORMAT_NUMBER_00
    DATE_FORMAT = "mm/dd/yy"
    DATETIME_FORMAT = "mm/dd/yy h:mm AM/PM"
    DEFAULT_NONE = "-"
    DEFAULT_TRUE = "Yes"
    DEFAULT_FALSE = "No"
    DEFAULT_COL_WIDTH = 25
    LOGO = os.path.abspath(os.path.dirname(__file__) + "/../core/static/images/Logo_Only_48.png")

    def __init__(self, user=None):
        """
        :param user: User model object is using for individual
        user preferences for formatting values
        """
        self.user = user

    # format cell

    def format_str_cell(self, cell, value):
        value = "{}".format(value)
        value = re.sub(ILLEGAL_CHARACTERS_RE, "", value)
        if value.isdigit() or value.lstrip("-").isdigit():
            self.format_integer_cell(cell, value)
        elif value.replace(".", "", 1).isdigit() or value.lstrip("-").replace(".", "", 1).isdigit():
            self.format_float_cell(cell, value)
        elif value.startswith("$"):
            self.format_currency_cell(cell, value)
        elif value.endswith("%"):
            self.format_percentage_cell(cell, value)
        else:
            cell.value = value

    def format_integer_cell(self, cell, value):
        try:
            cell.value = int(value)
            cell.number_format = self.NUMBER_FORMAT
        except ValueError:
            cell.set_cell_explicit_value(cell, value)

    def format_float_cell(self, cell, value):
        try:
            cell.value = float(value)
            cell.number_format = self.FLOAT_FORMAT
        except ValueError:
            cell.set_cell_explicit_value(cell, value)

    def format_currency_cell(self, cell, value):
        try:
            cell.value = float(value[1:])
            cell.number_format = self.CURRENCY_FORMAT
        except ValueError:
            cell.set_cell_explicit_value(cell, value)

    def format_percentage_cell(self, cell, value):
        try:
            cell.value = float(value[:-1]) / 100
            cell.number_format = self.PERCENTAGE_FORMAT
        except ValueError:
            cell.set_cell_explicit_value(cell, value)

    def format_date_cell(self, cell, value):
        cell.value = self.get_formatted_date(value)
        cell.number_format = self.DATE_FORMAT

    def format_datetime_cell(self, cell, value):
        cell.value = self.get_formatted_datetime(value)
        cell.number_format = self.DATETIME_FORMAT

    # format value

    def get_formatted_datetime(self, value):
        if not value:
            return self.DEFAULT_NONE

        if not isinstance(value, datetime.datetime):
            if isinstance(value, datetime.date):
                return self.get_formatted_date(value)
            raise ValueError("Provide datetime object")

        if self.user:
            tz = self.user.timezone_preference
            return formats.date_format(value.astimezone(tz), "SHORT_DATETIME_FORMAT")

        return formats.date_format(value, "SHORT_DATETIME_FORMAT")

    def get_formatted_date(self, value):
        if not value:
            return self.DEFAULT_NONE

        if isinstance(value, datetime.datetime):
            if self.user:
                tz = self.user.timezone_preference
                return formats.date_format(value.astimezone(tz).date(), "SHORT_DATE_FORMAT")

        return formats.date_format(value, "SHORT_DATE_FORMAT")

    def get_formatted_boolean(self, value):
        return self.DEFAULT_TRUE if value else self.DEFAULT_FALSE

    def get_formatted_null_boolean(self, value):
        if value is None:
            return self.DEFAULT_NONE
        return self.DEFAULT_TRUE if value else self.DEFAULT_FALSE

    def get_formatted_decimal(self, value):
        return "{}".format(value) if value else self.DEFAULT_NONE

    # cell styles

    @staticmethod
    def set_cell_title_style(cell):
        cell.font = Font(name="Arial", size=18, bold=True)

    @staticmethod
    def set_cell_header_style(cell):
        cell.font = Font(name="Arial", size=12, bold=True, color=colors.WHITE)
        cell.alignment = Alignment(wrap_text=True, horizontal="center")
        cell.fill = PatternFill(fill_type=fills.FILL_SOLID, start_color="FF808080")

    @staticmethod
    def set_cell_italic_small_style(cell):
        cell.font = Font(name="Arial", size=10, italic=True)

    @staticmethod
    def set_cell_large_style(cell):
        cell.font = Font(name="Arial", size=14, bold=True)

    def get_absolute_anchor(self, image, top, left):
        from openpyxl.drawing.spreadsheet_drawing import (
            AbsoluteAnchor,
            pixels_to_EMU,
            XDRPoint2D,
            XDRPositiveSize2D,
        )

        position = XDRPoint2D(pixels_to_EMU(left), pixels_to_EMU(top))
        size = XDRPositiveSize2D(pixels_to_EMU(image.width), pixels_to_EMU(image.height))
        return AbsoluteAnchor(pos=position, ext=size)

    def add_logo(self, sheet):
        image = Image(self.LOGO)
        sheet.add_image(image, anchor=self.get_absolute_anchor(image, 0, 10))
