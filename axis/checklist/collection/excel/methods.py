"""Collection method objects and data"""


import logging


__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class ExcelCascadingSelectMethodMixin(object):
    allow_custom = False  # Raise ValidationErrors instead of doing hinting in verify_choice()

    def get_flat_choices(self):
        choices = []
        num_filters = len(self.labels) - 1  # omit 'Characteristics'
        for row in self.source_rows[1:]:  # skip header row
            main_data = dict(zip(self.label_codes, row[:num_filters]))
            leaf_data = dict(zip(self.leaf_label_codes, row[num_filters:]))
            choice = self.get_data_display(dict(main_data, **leaf_data))
            choices.append(choice)
        return choices

    def clean(self, data):
        """Transforms data into database-ready object."""
        try:
            # This is the data that normally comes in.
            data = self.parse_choice(data)
            return super(ExcelCascadingSelectMethodMixin, self).clean(data)
        except:
            # check for custom options like Not listed, Not applicable etc
            if isinstance(data, str):
                # Choice isn't built-in, so disallow explicit characteristics for data integrity.
                cleaned_data = {key: None for key in self.leaf_label_codes + self.label_codes}
                cleaned_data[self.label_codes[0]] = data
                return cleaned_data, {"hints": {"is_custom": True}}
