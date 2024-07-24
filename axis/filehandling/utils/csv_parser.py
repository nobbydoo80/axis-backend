import csv
import logging

from .xlsx_parser import XLSXParser

__author__ = "Steven Klass"
__date__ = "03/13/22 16:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass", "Benjamin Stürmer"]

log = logging.getLogger(__name__)


# pylint: disable
class CSVParser(XLSXParser):
    def load_workbook_and_sheet(self, **kwargs):
        raise NotImplementedError("This is not used in a CSV Parser")

    def _decode_file(self, filename):
        for encoding in ["ISO-8859-1", "utf-8"]:
            data = []
            with open(self.filename, encoding=encoding) as fh:
                reader = csv.reader(fh, dialect=self.dialect)
                try:
                    for line_number, line in enumerate(reader, start=1):
                        data.append(line)
                    return data
                except UnicodeDecodeError:
                    continue
        else:
            raise ValueError("Incorrect file encoding")

    def get_data(self):
        if hasattr(self, "_data"):
            return self._data

        try:
            self._data = self._decode_file(filename=self.filename)
        except ValueError as exc:
            raise exc
        return self._data

    def get_columns(self, **kwargs):
        row, found = 0, False
        data = self.get_data()
        for row, fieldnames in enumerate(data, start=1):
            self.row = row
            if row >= 20:
                break
            if self.uniq_header_column in fieldnames:
                log.debug("Found %s on row %s", self.uniq_header_column, self.row)
                self.column_headers = fieldnames
                found = True
                break

        if not found:
            raise IndexError(
                "Did not find {} in the first {} rows..".format(self.uniq_header_column, row)
            )
        return self.column_headers

    def get_results_dictionary_list(self, start_row=0, **kwargs):
        results = []
        data = self.get_data()
        for row, data in enumerate(data, start=1):
            if row <= start_row:
                continue
            record = dict(zip(self.column_headers, data))
            record["row_number"] = row
            results.append(record)
            log.debug("Record: %s", record)
        return results
