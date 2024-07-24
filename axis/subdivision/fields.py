""" Fields definitions leveraging the Select2 tools. """


from axis.core.fields import ApiModelSelect2Widget, UnattachedOrNewMixin
from .api import SubdivisionViewSet, UnattachedSubdivisionViewSet

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


class SubdivisionChoiceWidget(ApiModelSelect2Widget):
    permission_required = "subdivision.view_subdivision"
    viewset_class = SubdivisionViewSet
    search_fields = ["name__icontains"]


class UnattachedOrNewSubdivisionChoiceWidget(UnattachedOrNewMixin, SubdivisionChoiceWidget):
    viewset_class = UnattachedSubdivisionViewSet
