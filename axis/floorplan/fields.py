""" Fields definitions leveraging the Select2 tools. """


from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from axis.core.fields import ApiModelSelect2Widget
from .api import FloorplanViewSet

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class FloorplanChoiceWidget(ApiModelSelect2Widget):
    permission_required = "floorplan.view_floorplan"
    viewset_class = FloorplanViewSet
    search_fields = [
        "name__icontains",
        "number__icontains",
        "subdivision__name__icontains",
        "simulation__name__icontains",
    ]

    def label_from_instance(self, obj):
        EMPTY_VALUES = (None, "")

        label_rows = []
        if obj.name not in EMPTY_VALUES:
            label_rows.append(f"<label>Name</label>: {conditional_escape(obj.name)}")
        if obj.number not in EMPTY_VALUES and obj.name != obj.number:
            label_rows.append(f"<label>Name</label>: {conditional_escape(obj.number)}")
        if obj.simulation not in EMPTY_VALUES:
            label_rows.append(
                f"<label>Simulation</label>: " f"{conditional_escape(obj.simulation.as_string())}"
            )

        subdivision_names = obj.subdivision_set.values_list("name", flat=True)
        if subdivision_names:
            subdivision_label = "<label>Subdivision</label>: {}"
            label_rows.append(
                "<br>".join(
                    subdivision_label.format(conditional_escape(name)) for name in subdivision_names
                )
            )

        return mark_safe("<div id='fp-{}'>".format(obj.id) + "<br>".join(label_rows) + "</div>")
