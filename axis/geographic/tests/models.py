from django.db import models

from axis.geographic.placedmodels import GeneralPlacedModel

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


# NOTE: We're inheriting from GeneralPlacedModel because in practice, we're not using PlacedModel
# directly.  The data sync function to Place assumes that a city/county FK is available, and there
# is currently some funnybusiness concerning where *PlacedModel variants define these fields.  See
# the notes on the GeneralPlacedModelType metaclass.
#
# In the future when GeneralPlacedModelType is removed, and city/county are converted into proper
# fields on the base PlacedModel, this LogicalPlace can inhert from PlacedModel directly without
# any trouble.
class LogicalPlace(GeneralPlacedModel):
    """A test-specific model to stand in for models like ``Home`` that will
    be attached to a ``Place`` model.
    """

    address = models.TextField()

    class Meta:
        # Must supply app_label so this gets added to the db correctly.
        app_label = "geographic"
