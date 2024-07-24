import logging

from django.urls import reverse_lazy

from .state_machine import TRCStateMachine
from .fields import populate_config_data_fields
from .reader import TRCConfigReader

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Data interface for outside inspection.
config = {
    "reader": TRCConfigReader,
    "name": "TRC",
    "object_types": {
        "project": {
            "name": "Project",
            "name_plural": "Projects",
            "state_machine": TRCStateMachine,
            "state_label": "Project Status",
            "urls": {
                # "add": reverse_lazy("certification:object:add", kwargs={'type': 'project'}),
                "list": reverse_lazy("certification:status:list", kwargs={"type": "project"}),
            },
            "parent_type": None,
            "programs": {
                "tab_label": "Project Details",
                "verbose_name": "Program Track",
                "verbose_name_plural": "Program Tracks",
                "max": 1,
                "display_link": False,
            },
            "repr_setting": "project_name",
            "settings": {},  # filled in during populate
            "data": {},  # filled in during populate
            "examine": {
                "certifiableobject": {
                    "detail": "examine/certification/trc/projectbuilding_detail.html",
                    "form": "examine/certification/trc/projectbuilding_form.html",
                },
                "workflowstatus": {
                    "detail": "examine/certification/trc/projectbuilding_status_detail.html",
                    "form": "examine/certification/trc/projectbuilding_status_form.html",
                },
            },
        },
        "building": {
            "name": "Building",
            "name_plural": "Buildings",
            "state_machine": None,
            "state_label": None,
            # "urls": {
            #     "add": reverse_lazy("certification:object:add", kwargs={'type': 'building'}),
            #     "list": reverse_lazy("certification:object:list", kwargs={'type': 'building'}),
            # },
            "parent_type": "project",
            "programs": {
                "tab_label": "Building Details",
                "verbose_name": "Program Track",
                "verbose_name_plural": "Program Tracks",
                "max": 1,
                "display_link": False,
                "parent_sync": True,
            },
            "repr_setting": "building_name",
            "settings": {},  # filled in during populate
            "data": {},  # filled in during populate
            "examine": {
                "certifiableobject": {
                    "detail": "examine/certification/trc/projectbuilding_detail.html",
                    "form": "examine/certification/trc/projectbuilding_form.html",
                },
                "workflowstatus": {
                    "detail": "examine/certification/trc/projectbuilding_status_detail.html",
                    "form": "examine/certification/trc/projectbuilding_status_form.html",
                },
            },
        },
    },
}

populate_config_data_fields(config)
