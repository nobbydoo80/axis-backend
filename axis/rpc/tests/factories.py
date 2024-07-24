"""factories.py: """

__author__ = "Artem Hruzd"
__date__ = "12/11/2022 16:10"
__copyright__ = "Copyright 2011-2022 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import random
import re

from django.apps import apps
from axis.core.tests.factories import rater_admin_factory
from axis.core.utils import random_sequence
from axis.rpc.models import HIRLRPCUpdaterRequest, RPCVirtualMachine, RPCService, RPCSession

customer_hirl_app = apps.get_app_config("customer_hirl")


def hirl_rpc_updater_request_factory(**kwargs):
    user = kwargs.pop("user", None)
    document = kwargs.pop("document", None)
    if user is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("user__"):
                _kwrgs[re.sub(r"user__", "", k)] = kwargs.pop(k)
        verifier = rater_admin_factory(**_kwrgs)
        verifier.company.update_permissions(customer_hirl_app.app_name())

    if document is None:
        document = __file__
    kwrgs = {
        "document": document,
        "state": HIRLRPCUpdaterRequest.IN_PROGRESS_STATE,
        "project_type": random.choice(HIRLRPCUpdaterRequest.PROJECT_TYPE_CHOICES)[0],
        "user": user,
    }
    kwrgs.update(kwargs)

    hirl_rpc_updater_request = HIRLRPCUpdaterRequest.objects.create(**kwrgs)

    return hirl_rpc_updater_request


def rpc_virtual_machine_factory(**kwargs):
    kwrgs = {
        "name": random_sequence(4),
        "state": RPCVirtualMachine.ON_STATE,
    }
    kwrgs.update(kwargs)

    rpc_virtual_machine = RPCVirtualMachine.objects.create(**kwrgs)

    return rpc_virtual_machine


def rpc_service_factory(**kwargs):
    rpc_virtual_machine = kwargs.pop("rpc_virtual_machine", None)
    if rpc_virtual_machine is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("rpc_virtual_machine__"):
                _kwrgs[re.sub(r"rpc_virtual_machine__", "", k)] = kwargs.pop(k)
        rpc_virtual_machine = rpc_virtual_machine_factory(**_kwrgs)

    kwrgs = {
        "state": RPCVirtualMachine.ON_STATE,
        "vm": rpc_virtual_machine,
        "host": "1.1.1.1",
        "port": 8888,
    }
    kwrgs.update(kwargs)

    rpc_service = RPCService.objects.create(**kwrgs)

    return rpc_service


def rpc_session_factory(session_type, **kwargs):
    rpc_service = kwargs.pop("rpc_service", None)
    if rpc_service is None:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("rpc_service__"):
                _kwrgs[re.sub(r"rpc_service__", "", k)] = kwargs.pop(k)
        rpc_service = rpc_service_factory(**_kwrgs)

    kwrgs = {
        "service": rpc_service,
        "session_type": session_type,
        "state": RPCVirtualMachine.ON_STATE,
    }
    kwrgs.update(kwargs)

    rpc_session = RPCSession.objects.create(**kwrgs)

    return rpc_session
