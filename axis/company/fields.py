"""fields.py: Fields definitions leveraging the Select2 tools. """


from axis.core.fields import (
    ApiModelSelect2Widget,
    ApiModelSelect2MultipleWidget,
    UnattachedOrNewMixin,
)
from . import api

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

# NOTE: Our "UnattachedOrNew" fields have a tendency to get instantiated in the form.__init__
# methods, which causes late registration in the django_select2 app.  In load-balancing situations,
# this causes trouble with ajax queries routing to servers that don't have the field registered.
# As a result, these fields are forced to register at the bottom of this file.


class BaseOrganizationChoiceApiWidget(ApiModelSelect2Widget):
    search_fields = ["name__icontains"]


class BaseOrganizationMultipleChoiceApiField(ApiModelSelect2MultipleWidget):
    search_fields = ["name__icontains"]


class BuilderOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.BuilderOrganizationViewSet


class BuilderOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.BuilderOrganizationViewSet


class UnattachedBuilderOrganizationChoiceApiWidget(BuilderOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedBuilderOrganizationViewSet


class UnattachedOrNewBuilderOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, BuilderOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedBuilderOrganizationViewSet


class RaterOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.RaterOrganizationViewSet


class RaterOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.RaterOrganizationViewSet


class UnattachedRaterOrganizationChoiceApiWidget(RaterOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedRaterOrganizationViewSet


class UnattachedOrNewRaterOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, RaterOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedRaterOrganizationViewSet


class EepOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.EepOrganizationViewSet


class EepOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.EepOrganizationViewSet


class UnattachedEepOrganizationChoiceApiWidget(EepOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedEepOrganizationViewSet


class UnattachedOrNewEepOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, EepOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedEepOrganizationViewSet


class ProviderOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.ProviderOrganizationViewSet


class ProviderOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.ProviderOrganizationViewSet


class UnattachedProviderOrganizationChoiceApiWidget(ProviderOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedProviderOrganizationViewSet


class UnattachedOrNewProviderOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, ProviderOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedProviderOrganizationViewSet


class HvacOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.HvacOrganizationViewSet


class HvacOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.HvacOrganizationViewSet


class UnattachedHvacOrganizationChoiceApiWidget(HvacOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedHvacOrganizationViewSet


class UnattachedOrNewHvacOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, HvacOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedHvacOrganizationViewSet


class QaOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.QaOrganizationViewSet


class QaOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.QaOrganizationViewSet


class UnattachedQaOrganizationChoiceApiWidget(QaOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedQaOrganizationViewSet


class UnattachedOrNewQaOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, QaOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedQaOrganizationViewSet


class UtilityOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.UtilityOrganizationViewSet


class UtilityOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.UtilityOrganizationViewSet


class UnattachedUtilityOrganizationChoiceApiWidget(UtilityOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedUtilityOrganizationViewSet


class UnattachedOrNewUtilityOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, UtilityOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedUtilityOrganizationViewSet


class GeneralOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.GeneralOrganizationViewSet


class ArchitectOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.ArchitectOrganizationViewSet


class DeveloperOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.DeveloperOrganizationViewSet


class CommunityOwnerOrganizationChoiceApiWidget(BaseOrganizationChoiceApiWidget):
    viewset_class = api.CommunityOwnerOrganizationViewSet


class GeneralOrganizationMultipleChoiceApiField(BaseOrganizationMultipleChoiceApiField):
    viewset_class = api.GeneralOrganizationViewSet


class UnattachedGeneralOrganizationChoiceApiWidget(GeneralOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedGeneralOrganizationViewSet


class UnattachedArchitectOrganizationChoiceApiWidget(ArchitectOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedArchitectOrganizationViewSet


class UnattachedDeveloperOrganizationChoiceApiWidget(DeveloperOrganizationChoiceApiWidget):
    viewset_class = api.UnattachedDeveloperOrganizationViewSet


class UnattachedCommunityOwnerOrganizationChoiceApiWidget(
    CommunityOwnerOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedCommunityOwnerOrganizationViewSet


class UnattachedOrNewGeneralOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, GeneralOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedGeneralOrganizationViewSet


class UnattachedOrNewArchitectOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, ArchitectOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedArchitectOrganizationViewSet


class UnattachedOrNewDeveloperOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, DeveloperOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedDeveloperOrganizationViewSet


# Communityowner we can't capitalize owner without updating examine code
class UnattachedOrNewCommunityownerOrganizationChoiceApiWidget(
    UnattachedOrNewMixin, CommunityOwnerOrganizationChoiceApiWidget
):
    viewset_class = api.UnattachedCommunityOwnerOrganizationViewSet


# FIXME: Don't know if this is still needed
# Forced registration for types we tend to get late registration in form.__init__
UnattachedOrNewBuilderOrganizationChoiceApiWidget()
UnattachedOrNewRaterOrganizationChoiceApiWidget()
UnattachedOrNewEepOrganizationChoiceApiWidget()
UnattachedOrNewProviderOrganizationChoiceApiWidget()
UnattachedOrNewHvacOrganizationChoiceApiWidget()
UnattachedOrNewQaOrganizationChoiceApiWidget()
UnattachedOrNewUtilityOrganizationChoiceApiWidget()
UnattachedOrNewGeneralOrganizationChoiceApiWidget()
UnattachedOrNewArchitectOrganizationChoiceApiWidget()
UnattachedOrNewDeveloperOrganizationChoiceApiWidget()
UnattachedOrNewCommunityownerOrganizationChoiceApiWidget()
