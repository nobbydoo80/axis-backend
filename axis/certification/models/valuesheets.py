import logging

from django.db import models

from ..utils import refresh_values_sheet

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DenormalizedValuesSheet(models.Model):
    """Used to save data collection values to a place in the database that can be queried."""

    # NOTE: Values found here should be treated as readonly versions of the underlying JSON payload
    # on the associated object.

    owner = models.ForeignKey("company.Company", on_delete=models.CASCADE)  # ?

    # Hint for which type of certifiable_object is supported
    OBJECT_TYPE = None

    class Meta:
        abstract = True

    def refresh(self):
        raise NotImplementedError()


class DenormalizedCertifiableObjectSettings(DenormalizedValuesSheet):
    """Used to store customer-specific settings for the actual CertifiableObject."""

    certifiable_object = models.ForeignKey(
        "CertifiableObject", related_name="objectsettings_set", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def refresh(self):
        refresh_values_sheet(self, self.certifiable_object.settings)


class DenormalizedWorkflowStatusData(DenormalizedValuesSheet):
    """Used to store instance data for a specific WorkflowStatus of a CertifiableObject."""

    certifiable_object = models.ForeignKey(
        "CertifiableObject", related_name="workflowstatusdata_set", on_delete=models.CASCADE
    )
    workflow_status = models.ForeignKey(
        "WorkflowStatus", related_name="workflowstatusdata_set", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        unique_together = ("certifiable_object", "workflow_status")

    def refresh(self):
        refresh_values_sheet(self, self.workflow_status.data)


# Customer ValueSheets
# Fields added to a ValueSheet should always allow null, because the 'required' flag on any given
# value in the json config is only a statement that it is required before certification is allowed,
# not in the way the Forms framework means 'required'.


# TODO: Maybe just add a flag in the json files that promotes a field to a valuesheet, then, at
# import-time for this module, synthesize any models required to hold them.  Migrations would work
# the same as before, just controlled by the JSON.
class TRCProjectSettings(DenormalizedCertifiableObjectSettings):
    OBJECT_TYPE = "project"

    type = models.CharField(
        "Type",
        max_length=25,
        choices=(
            ("new", "New Construction"),
            ("retrofit", "Retrofit"),
        ),
    )


class TRCProjectData(DenormalizedWorkflowStatusData):
    OBJECT_TYPE = "project"

    # Example field:
    lead_contact_date = models.DateField("Lead Contact Date", blank=True, null=True)
