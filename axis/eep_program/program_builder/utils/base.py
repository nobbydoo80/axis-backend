"""High level operations"""


import logging

from django.forms.models import model_to_dict

from . import safe_ops, unsafe_ops
from .convertion import apply_convertions

__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


def clone_program(
    eep_program, convertions, exclude_measures=[], existing=None, convert_to_collection=None
):
    """
    Clones ``eep_program`` to a new object, applying changes to the field data based on generic
    string replacement rules in the ``convertions`` list.
    """

    # FIXME: Do this better
    fks = ["owner"]
    skip = ["id", "collection_request"]
    m2ms = ["opt_in_out_list", "required_annotation_types", "required_checklists", "certifiable_by"]

    # Apply conversions to easy attributes
    attrs = dict(
        model_to_dict(eep_program, exclude=skip + fks + m2ms),
        **{k: getattr(eep_program, k) for k in fks},
    )
    attrs = apply_convertions(attrs, existing, *convertions)

    # Build new program
    cloned = safe_ops.derive_program(**attrs)

    for name in m2ms:
        getattr(cloned, name).add(*getattr(eep_program, name).all())

    if convert_to_collection is not False:
        safe_ops.convert_checklist_to_collection(cloned, exclude=exclude_measures)
        unsafe_ops.drop_checklist(cloned)

    return cloned


def unpack_settings(spec, settings_map, **attrs):
    """
    Loads condensed settings from ``spec`` given the equivalence lookups in ``settings_map``.
    """

    class missing:
        pass

    log.info("Base flags: %r", attrs)

    try:
        opposite_role = "qa" if spec.role == "rater" else "rater"
    except AttributeError:
        opposite_role = "qa"

    for setting, info in dict(settings_map, **attrs).items():
        if setting.startswith(opposite_role + "_") and setting != "rater_incentive_dollar_value":
            continue
        values = getattr(spec, setting, missing)
        if values is missing:
            if setting not in attrs:
                log.info(
                    "%s.%s is unconfigured and has not been supplied via kwargs.",
                    spec.__class__.__name__,
                    setting,
                )
                continue
            values = attrs[setting]
            log.info("Filling %s=%r from base attrs", setting, values)

        if isinstance(info, bool):
            # Use value directly
            log.info("Using provided literal for %s: %r", setting, info)
            attrs[setting] = info
        elif callable(info):
            # Send declared values into callable, get back arbitrary map of new attrs
            if not values:
                log.info(
                    "Unable to copy flag for %s (unconfigured: %r)",
                    setting,
                    values,
                )
                continue
            elif isinstance(values, dict):
                flags = info(**values)
            else:
                if not isinstance(values, (list, tuple, set)):
                    values = [values]
                flags = info(*values)
            if not isinstance(flags, dict):
                flags = {setting: flags}
            log.info("Copying flags for %s=%r: %r", setting, values, flags)
            attrs.update(flags)
        elif isinstance(info, str):
            # Copy value to keyname alias in 'info'
            log.info("Copying flag for %s: %r", setting, values)
            attrs[info] = values
        elif isinstance(info, dict):
            # Translate nested dict of settings in a scope limited to that setting's supported keys
            # Translate to dict syntax so everything is explicit before processed
            is_dict = isinstance(values, dict)
            is_iterable = isinstance(values, (list, tuple, set))
            if not is_dict and not is_iterable:
                values = [values]
                is_iterable = True
            if is_iterable:
                values = {k: True for k in values}

            for k, v in values.items():
                if k not in info:
                    raise ValueError(
                        "%r is not a known setting for %r.  Allowed %s are: %r"
                        % (
                            value,
                            setting,
                            ("values" if is_dict else "keys"),
                            list(info.keys()),
                        )
                    )

                # Ensure spec is also a dict (expand lone names to dict syntax with setting value)
                item_spec = info[k]
                if isinstance(item_spec, dict):
                    # item comes as-is with fixed presets, value can't influence it directly
                    if not v:
                        continue  # Skip when explicitly opted-out via a False-like value
                else:
                    # Alias declared values via the name given
                    item_spec = {item_spec: v}

                log.info("Selecting dependent flags for %s.%s=%r: %r", setting, k, v, item_spec)
                attrs.update(item_spec)
        else:
            # Iterate a values list and ensure names it contains are supported shorthand for that
            # setting.
            if not isinstance(values, (list, tuple, set)):
                values = [values]
            for value in values:
                if value not in info:
                    raise ValueError(
                        "%r is not a known setting for %r.  Allowed values are: %r"
                        % (
                            value,
                            setting,
                            list(info.keys()),
                        )
                    )
                log.info("Selecting dependent flags for %s=%r: %r", setting, value, info[value])
                attrs.update(info[value])
    return attrs
