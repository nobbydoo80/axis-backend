"""widgets.py: Django checklist"""


from itertools import chain

from django.forms.widgets import SelectMultiple, RadioSelect
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

# TODO: Create a datatable widget specifically for model relationship fields, capable of all of the
# same data rendering methods as DatatableView.  This current widget doesn't support multiple
# columns or fancy output formatting beyond what a normal <select> widget is capable of.


class DatatableSelectMultipleWidget(SelectMultiple):
    """
    Represents a ``SelectMultiple`` in a standard client-side datatable.  The table is rendered in
    two columns, the first for the checkbox, the second for the choice.

    """

    def __init__(
        self,
        column_label="Options",
        selection_label="Select",
        classname="datatable",
        *args,
        **kwargs,
    ):
        self.column_label = column_label
        self.selection_label = selection_label
        self.classname = classname

        super(DatatableSelectMultipleWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, dict(name=name))
        if "class" not in final_attrs:
            final_attrs["class"] = self.classname
        else:
            final_attrs["class"] += " " + self.classname

        output = ["<table%s>" % flatatt(final_attrs)]

        # thead
        output.append(
            "<thead><tr><th>%s</th><th>%s</th></tr></thead><tbody>"
            % (self.selection_label, self.column_label)
        )

        # options
        options = self.render_options(name, choices, value)
        if options:
            output.append(options)

        output.append("</tbody></table>")

        return mark_safe("\n".join(output))

    def render_options(self, name, choices, selected_choices):
        # Not invented here; this is normal Select.render_options without the optgroup functionality
        # Normalize to strings.
        selected_choices = set(force_unicode(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                for option in option_label:
                    output.append(self.render_option(name, selected_choices, *option))
            else:
                output.append(
                    self.render_option(name, selected_choices, option_value, option_label)
                )
        return "\n".join(output)

    def render_option(self, name, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = ' checked="checked"'
        else:
            selected_html = ""
        return '<tr><td><input type="checkbox" name="%s" value="%s"%s /></td><td>%s</td></tr>' % (
            name,
            escape(option_value),
            selected_html,
            conditional_escape(force_unicode(option_label)),
        )


## WARNING: MARKED FOR REMOVAL, Autumn 2018-10-01
# class HorizontalRadioRenderer(RadioSelect.renderer):
#     def render(self):
#         html = '<span style="margin: 0.5em 0;">'
#         html += '\n'.join(['%s &nbsp;\n' % w for w in self])
#         html += '</span>'
#         return mark_safe(html)
