"""fields.py: Fields definitions leveraging the Select2 tools. """


from axis.core.fields import ApiModelSelect2Widget, UnattachedOrNewMixin
from .api import CommunityViewSet, UnattachedCommunityViewSet

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CommunityChoiceWidget(ApiModelSelect2Widget):
    permission_required = "community.view_community"
    viewset_class = CommunityViewSet
    search_fields = ["name__icontains"]

    def label_from_instance(self, obj):
        return "{obj.name} {obj.city}".format(obj=obj)


class UnattachedOrNewCommunityChoiceWidget(UnattachedOrNewMixin, CommunityChoiceWidget):
    viewset_class = UnattachedCommunityViewSet
