import logging
import importlib

from .models import Workflow


__author__ = "Autumn Valenta"
__date__ = "12/12/17 4:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# Add Workflow-specific tasks
for workflow in Workflow.objects.all():
    module = workflow.get_config_module()
    try:
        workflow_tasks = importlib.import_module(".".join([module.__package__, "tasks"]))
    except ImportError as e:
        log.info("No tasks module detected in %r: %r", module.__package__, e)
        continue

    globals().update(workflow_tasks.__dict__)
