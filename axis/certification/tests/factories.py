import os.path
import inspect
import logging
from pprint import pformat

from axis.core.tests.utils import subdict_from_prefix
from ..models import Workflow, WorkflowStatus, CertifiableObject
from ..utils import CONFIGS_DIRECTORY


__author__ = "Autumn Valenta"
__date__ = "9/20/17 4:38 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def _dict_slice(kwargs, keys_whitelist):
    return {k: kwargs.get(k) for k in keys_whitelist}


def _require(data, key):
    if data.get(key) is None:
        caller_name = inspect.stack()[1][3]
        raise ValueError(
            "'{factory}' requires '{key}' argument\nData:\n{data}\n".format(
                **{
                    "factory": caller_name,
                    "key": key,
                    "data": "{}".format(pformat(data, indent=4)),
                }
            )
        )


def ensure_related_object(data, key, factory, **extra):
    obj = data.get(key)
    if obj is None:
        # Zero or more keys each with a '{key}__' prefix
        obj_kwargs = subdict_from_prefix(data, key + "__")
        obj_kwargs.update(extra)
        obj = factory(**obj_kwargs)
    elif isinstance(obj, dict):
        # Nested dict of options
        obj_kwargs = dict(obj, **extra)
        obj = factory(**obj_kwargs)
    return obj


def workflow_factory(**kwargs):
    obj_kwargs = _dict_slice(
        kwargs,
        [
            "config_path",
        ],
    )

    if obj_kwargs["config_path"] is None:
        obj_kwargs["config_path"] = "TEST.py"

    if not os.path.dirname(obj_kwargs["config_path"]):
        obj_kwargs["config_path"] = os.path.join(CONFIGS_DIRECTORY, obj_kwargs["config_path"])

    obj, created = Workflow.objects.get_or_create(**obj_kwargs)
    return obj


def workflow_status_factory(**kwargs):
    from axis.company.tests.factories import rater_organization_factory
    from axis.eep_program.tests.factories import basic_eep_program_factory

    obj_kwargs = _dict_slice(
        kwargs,
        [
            "workflow",
            "owner",
            "eep_program",
            "certifiable_object",
            "state",
            "data",
        ],
    )

    factories = {
        "workflow": workflow_factory,
        "owner": rater_organization_factory,
        "eep_program": basic_eep_program_factory,
        "certifiable_object": certifiable_object_factory,
    }

    def _ensure_obj(key, **extra):
        return ensure_related_object(kwargs, key, factory=factories[key], **extra)

    obj_kwargs["workflow"] = _ensure_obj("workflow")
    obj_kwargs["owner"] = _ensure_obj("owner")
    obj_kwargs["eep_program"] = _ensure_obj("eep_program")
    obj_kwargs["certifiable_object"] = _ensure_obj(
        "certifiable_object",
        **{
            "owner": obj_kwargs["owner"],
        },
    )

    if obj_kwargs["state"] is None:
        obj_kwargs["state"] = "initial"

    obj, created = WorkflowStatus.objects.get_or_create(**obj_kwargs)
    return obj


def certifiable_object_factory(**kwargs):
    from axis.company.tests.factories import rater_organization_factory

    obj_kwargs = _dict_slice(
        kwargs,
        [
            "owner",
            "parent",
            "type",
            "settings",
        ],
    )

    _require(obj_kwargs, "type")

    obj_kwargs["owner"] = ensure_related_object(kwargs, "owner", factory=rater_organization_factory)

    obj, created = CertifiableObject.objects.get_or_create(**obj_kwargs)
    return obj
