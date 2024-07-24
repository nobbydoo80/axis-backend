import logging
import importlib

from django.db import ProgrammingError, OperationalError
from rest_framework.routers import SimpleRouter

from ..models import Workflow
from . import api

__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


urlpatterns = []  # Inspected in axis/core/api_v2.py


# Add Workflow-specific APIs; these get priority URL routing to avoid ambiguities in pk lookups.
# If the config has an 'api' package instead of a module, configs/FOO/__init__.py should import the
# api module into the namespace.  E.g., ``from . import api``
#
# NOTE: Because we're using a queryset to determine static urls, new Workflow objects require a
# uwsgi reload to appear in the urlconf!  Simply deploying new code would trigger this reload,
# although due to the order of deployment events, if you deploy code with a new Workflow config in
# it, then use the fresh server to add the Workflow instance powered by that config, you'll find
# uwsgi still in need of a reload!  Migrations to add the Workflow suffer from the same problem,
# since the server is typically deployed already when the ssh session begins and migrations are then
# applied.
#
# MORAL OF THE STORY: New workflows demand a uwsgi reload if they provide custom api endpoints.
#
try:
    workflows = list(Workflow.objects.all())
except (ProgrammingError, OperationalError):
    workflows = []

for workflow in workflows:
    module = workflow.get_config_module()
    try:
        workflow_api = importlib.import_module(".".join([module.__package__, "api"]))
    except ImportError as e:
        logging.info("No api module detected in %r: %r", module.__package__, e)
        continue

    urlpatterns += workflow_api.urlpatterns


# List of router registrations to perform
viewset_urls = (
    # Generic, used mostly with Examine due to query param requirements to scope the objects right
    (
        r"certification/examine/object/(?P<certifiable_object_pk>[^/]+)/status",
        api.WorkflowStatusExamineViewSet,
    ),
    (r"certification/examine/object", api.CertifiableObjectExamineViewSet),
    # Application API
    (
        r"certification/(?P<workflow_pk>\d+)/(?P<type>[^/]+)/(?P<certifiable_object_pk>[^/]+)/status",
        api.WorkflowStatusViewSet,
    ),
    (r"certification/(?P<workflow_pk>\d+)/(?P<type>[^/]+)", api.CertifiableObjectViewSet),
)

# Register viewsets with the url_basename lookup automatically performed
router = SimpleRouter()
for url, viewset in viewset_urls:
    router.register(url, viewset, viewset.url_basename)
urlpatterns += router.urls
