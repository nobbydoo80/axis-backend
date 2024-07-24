"""customer_hirl_updater_request.py: """

__author__ = "Artem Hruzd"
__date__ = "11/21/2022 15:31"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.auth import get_user_model
from django.db import models
from django_fsm import FSMField
from picklefield import PickledObjectField

from axis.rpc.managers.customer_hirl_updater_request import HIRLRPCUpdaterRequestQuerySet
from axis.rpc.models import RPCSession


User = get_user_model()


class HIRLRPCUpdaterRequest(models.Model):
    """
    Contains request data from user for update document
    """

    IN_PROGRESS_STATE = "in_progress"
    SUCCESS_STATE = "success"
    ERROR_STATE = "error"

    STATE_CHOICES = (
        (IN_PROGRESS_STATE, "In Progress"),
        (SUCCESS_STATE, "Success"),
        (ERROR_STATE, "Error"),
    )

    NC_2020_SCORING_PATH = "2020_ngbs"
    REMODEL_2020_SCORING_PATH = "2020_ngbs_remodel"
    NC_2015_SCORING_PATH = "2015_ngbs"

    SCORING_PATH_CHOICES = (
        (NC_2020_SCORING_PATH, "2020 New Construction"),
        (REMODEL_2020_SCORING_PATH, "2020 Remodel"),
        (NC_2015_SCORING_PATH, "2015 New Construction"),
    )

    SINGLE_FAMILY_PROJECT_TYPE = "single_family"
    MULTI_FAMILY_PROJECT_TYPE = "multifamily"

    PROJECT_TYPE_CHOICES = (
        (SINGLE_FAMILY_PROJECT_TYPE, "Single Family"),
        (MULTI_FAMILY_PROJECT_TYPE, "Multifamily"),
    )

    document = models.FileField()
    scoring_path = models.CharField(
        max_length=48, choices=SCORING_PATH_CHOICES, default=NC_2020_SCORING_PATH
    )
    project_type = models.CharField(
        max_length=48, choices=PROJECT_TYPE_CHOICES, default=SINGLE_FAMILY_PROJECT_TYPE
    )

    result_document = models.FileField(null=True, blank=True)
    rpc_session = models.OneToOneField(RPCSession, null=True, blank=True, on_delete=models.SET_NULL)
    state = FSMField(choices=STATE_CHOICES, default=IN_PROGRESS_STATE)
    task_id = models.CharField(max_length=36, blank=True, null=True)

    result = PickledObjectField(null=True, default=None, editable=False)

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = HIRLRPCUpdaterRequestQuerySet.as_manager()

    def __str__(self):
        return f"HIRL Updater Request - {self.rpc_session} by {self.user}"

    class Meta:
        ordering = ("-created_at",)
