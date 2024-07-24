""" Fields definitions leveraging the Select2 tools. """


import logging

from axis.core.fields import ApiModelSelect2Widget
from .api import ProjectViewSet, UnattachedProjectViewSet

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ProjectChoiceWidget(ApiModelSelect2Widget):
    viewset_class = ProjectViewSet
    search_fields = ["id__icontains", "name__icontains"]

    def label_from_instance(self, obj):
        if obj.data:
            return "<br />".join(
                (
                    "Project: {project.name} ({project.id})",
                    "Development: {data[community]}",
                    "Builder: {data[builder]}",
                    "Imported: {project.modified_date}",
                )
            ).format(project=obj, data=obj.data)
        return "<br />".join(
            ("Project: {project.name} ({project.id})", "Imported: <em>No</em>")
        ).format(project=obj)


class UnattachedProjectChoiceWidget(ProjectChoiceWidget):
    viewset_class = UnattachedProjectViewSet
