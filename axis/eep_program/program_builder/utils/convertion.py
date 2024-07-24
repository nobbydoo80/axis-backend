"""Attribute mapping utils"""


import re
import logging


__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


call_types = {
    None: lambda f, d: f(d),
    tuple: lambda f, d: f(*d),
    list: lambda f, d: f(*d),
    dict: lambda f, d: f(**d),
}


def apply_convertions(attrs, existing=None, *rules):
    """Apply each rule to matching data items in ``attrs``."""
    for rule in rules:
        for name, value in attrs.items():
            base_logging_args = {
                "replacer": rule.__class__.__name__,
                "name": name,
                "value": value,
            }
            if rule.name in (name, "*"):
                caller = call_types.get(value.__class__, call_types[None])
                apply_args = (attrs[name],)
                try:
                    attrs[name] = caller(rule.apply, *apply_args)
                except SkipFieldException as e:
                    logging_args = dict(base_logging_args, message=e)
                    log.debug(
                        "Replacer '%(replacer)s' omitted %(name)r from the converted results "
                        "(value would have been %(value)r): %(message)s",
                        logging_args,
                    )
                except:
                    log.debug(
                        "Replacer '%(replacer)s' does not apply to %(name)r=%(value)r",
                        base_logging_args,
                    )
    return attrs


class SkipFieldException(Exception):
    pass


class Rule(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def apply(self, value, existing_value=None):
        raise NotImplemented

    def skip(self, *args, **kwargs):
        raise SkipFieldException("skip() was called")


class Skip(Rule):
    apply = Rule.skip


class Keep(Rule):
    apply = lambda self, v, existing: existing or self.skip()


class StringReplace(Rule):
    apply = lambda self, v, *args: v.replace(*self.args)


class RegexReplace(Rule):
    apply = re.sub
