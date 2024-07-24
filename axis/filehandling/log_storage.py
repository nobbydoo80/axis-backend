"""log_storage.py: Django filehandling"""


import collections

import logging
import os
import datetime
import re
import pprint
import time

from django.apps import apps
from django.conf import settings
from django.utils import formats
from django.utils.timezone import now

__author__ = "Steven Klass"
__date__ = "1/30/14 9:33 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

if __file__[-4:].lower() in [".pyc", ".pyo"]:
    _srcfile = __file__[:-4] + ".py"
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)


class LogStorage(logging.Logger):
    """This a a natural way store results.."""

    def __init__(self, *args, **kwargs):
        level = kwargs.get("level", logging.NOTSET)
        super(LogStorage, self).__init__(name="LogStorage", level=level)

        self.storage = []
        self.row_flags = {}
        self.store_all = kwargs.get("store_all", False)
        self.context = kwargs.get("context", collections.OrderedDict())
        # Stuff for Django Interaction
        self.model_id = kwargs.get("result_id") or kwargs.get("model_id")
        self.model_name = kwargs.get("model_name", "filehandling.AsynchronousProcessedDocument")
        self.model_attr = kwargs.get("model_attr", "id")
        self.model_update_attr = kwargs.get("model_update_attr", "result")
        self.model_object = None
        self.last_model_update = now() + datetime.timedelta(hours=12)
        self._default_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.model_id:
            self.model_object = self.get_model_object()
            self.update_model(throttle_seconds=None)

    def get_model_object(self):
        if self.model_id:
            ModelObj = apps.get_model(*self.model_name.split("."))
            return ModelObj.objects.get(**{self.model_attr: self.model_id})

    def update_model(self, throttle_seconds=0.5):
        """This will set the django model"""

        if not self.model_id:
            return
        try:
            last_update = datetime.datetime.fromtimestamp(self.storage[-1].created).replace(
                tzinfo=datetime.timezone.utc
            )

        except IndexError:
            last_update = self.last_model_update

        if isinstance(throttle_seconds, (int, float)):
            delta = float((last_update - self.last_model_update).microseconds)
            if delta <= float(throttle_seconds * 1000000):
                log.debug("Throttle? %d <= %d" % (delta, float(throttle_seconds * 1000000)))
                return

        model = self.get_model_object()
        result_dict = getattr(model, self.model_update_attr)
        assert isinstance(
            result_dict, (dict, type(None))
        ), "Was expecting a dictionary - got {}".format(type(result_dict))

        if not result_dict:
            result_dict = {}

        for levelname in self._default_levels:
            keyname = (
                levelname.lower() + "s" if levelname in ["WARNING", "ERROR"] else levelname.lower()
            )

            result_dict[keyname] = self.report_by_context(levelname)

        try:
            result_dict["latest"] = self.format(self.storage[-1], skip_date=True)
        except IndexError:
            result_dict["latest"] = "Starting"
        result_dict["chronological"] = self.report_chronological()
        result_dict["by_context_row"] = self.report_by_context_row()
        setattr(model, self.model_update_attr, result_dict)
        model.save()

        self.last_model_update = last_update

    def set_context(self, **kwargs):
        for key, value in kwargs.items():
            self.context[key] = value

    def handle(self, record):
        if (not self.disabled) and self.filter(record):
            for key, value in self.context.items():
                if (key in ["message", "asctime"]) or (key in record.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                if value:
                    if "context" not in record.__dict__:
                        record.__dict__["context"] = []
                    record.__dict__[key] = value
                    record.__dict__["context"].append(key)

            # Remove duplicate messages of the same context
            if not self.store_all and self.has_message(self.format(record)):
                return

            self.storage.append(record)
            if record.levelname == "DEBUG":
                log.debug(self.format(record))
                if self.model_object:
                    self.update_model()
            elif record.levelname in ["CRITICAL", "ERROR"]:
                log.info(
                    "LogStorage [%(level)s] %(path)s:%(line)s %(msg)s",
                    {
                        "level": record.levelname.capitalize(),
                        "path": record.pathname,
                        "line": record.lineno,
                        "msg": self.format(record),
                    },
                )
                if self.model_object:
                    self.update_model(throttle_seconds=None)
            else:
                log.debug(
                    "LogStorage [%(level)s] %(path)s:%(line)s %(msg)s",
                    {
                        "level": record.levelname.capitalize(),
                        "path": record.pathname,
                        "line": record.lineno,
                        "msg": self.format(record),
                    },
                )
                if self.model_object:
                    self.update_model(throttle_seconds=None)

    def get_context_string(self, record):
        context = []
        if hasattr(record, "context"):
            context = ["{}={}".format(key, getattr(record, key)) for key in record.context]
        return "[" + ", ".join(context) + "]" if len(context) else ""

    def get_datetime_stamp(self, record):
        dts = datetime.datetime.fromtimestamp(record.created)
        return "[" + formats.date_format(dts, "SHORT_DATETIME_FORMAT") + "]"

    def format(self, record, skip_date=False):
        date_stamp = self.get_datetime_stamp(record) if not skip_date else ""
        context = " {}".format(self.get_context_string(record))
        return "{} {} {}".format(date_stamp, record.getMessage(), context).strip()

    def report_chronological(self, levelname=None):
        if levelname:
            return [
                self.format(x, True) for x in self.storage if levelname and x.levelname == levelname
            ]
        return [self.format(x) for x in self.storage]

    def set_flags(self, **kwargs):
        row = self.context.get("row") or "general"
        if row not in self.row_flags.keys():
            self.row_flags[row] = {}
        for key, value in kwargs.items():
            self.row_flags[row].update({key: value})

    def get_row_flags(self, row):
        return self.row_flags.get(row, {})

    def _logs_by_levelname_and_context(self, context=None, levelname=None):
        for record in self.storage:
            if levelname and record.levelname != levelname.upper():
                continue

            log_keys = getattr(record, "context", [])
            # Check that context keys are a valid subset of log_keys
            if context and set(context.keys()) - set(log_keys):
                continue

            yield record

    def remove_message(self, msg, context=None, levelname=None, use_current_context=False):
        """
        Remove a message from the logs of a given context if provided.
        context must only be a subset of the logs context.
        message passed may be regex.

        context examples:
            record = {
                'msg': 'this is a record',
                'context': ['row', 'arbitrary'],
                'row': 1,
                'arbitrary': 'hello'
            }

            remove_message('this is a log', context={'row': 1})                       -> DELETED
            remove_message('this', context={'row': 1})                                -> DELETED
            remove_message('this is a log', context={'row': 1, 'arbitrary': 'hello'}) -> DELETED
            remove_message('this is a log', context={'row': 1, 'different': 'hello'}) -> IGNORED
        """
        assert isinstance(
            context, (type(None), dict)
        ), "context must be provided in {key: value} pairs"

        if use_current_context:
            context = self.context

        r = re.compile(msg)

        # all logs are of the correct level, and have keys of the context provided.
        for record in self._logs_by_levelname_and_context(context, levelname):
            delete = True
            match = r.search(record.getMessage())
            if match:
                if context:
                    for key, value in context.items():
                        if getattr(record, key) != value:
                            delete = False

                if delete:
                    del self.storage[self.storage.index(record)]

    def report_by_context_row(self):
        row_data = {}
        for item in self.storage:
            if item.levelname == "DEBUG" and not settings.DEBUG:
                continue
            row = "general"
            if hasattr(item, "row"):
                row = item.row
            if row not in row_data.keys():
                row_data[row] = {"has_errors": False}
            if item.levelname in ["ERROR", "CRITICAL"]:
                row_data[row]["has_errors"] = True
            if item.levelname not in row_data[row].keys():
                row_data[row][item.levelname] = []
            row_data[row][item.levelname].append(self.format(item, True))
            row_data[row].update(self.get_row_flags(row))

        return row_data

    def report_by_context(self, levelname=None):
        """This will create a mapping on the context of the messages"""

        data = []
        for record in self.storage:
            if levelname and record.levelname != levelname:
                continue
            keys = [key for key in self.context if getattr(record, key, None)]
            key_name = (keys, record.getMessage())
            if len(keys):
                if key_name not in [key for key, value in data]:
                    data.append((key_name, []))
            else:
                data.append((key_name, []))

            row = next(((key, value) for key, value in data if key == key_name))
            data[data.index(row)][1].append(record)

        context_list = []
        for (keys, msg), records in data:
            key_dict = collections.OrderedDict()
            for key in keys:
                key_dict[key] = [getattr(v, key) for v in records if getattr(v, key)]
            context = []
            for k, v in key_dict.items():
                vals = list(set(v))
                vals.sort()
                context.append("{}={}".format(k, ",".join([str(i) for i in vals])))
            context = "[" + ", ".join(context) + "]" if len(context) else ""
            context_list.append("{} {}".format(msg, context).strip())
        return context_list

    @property
    def has_errors(self):
        error_plus_msgs = [x for x in self.storage if x.levelname in ["ERROR", "CRITICAL"]]
        return True if len(error_plus_msgs) else False

    def has_message(self, msg, levelname=None):
        if levelname:
            msgs = [x for x in self.storage if self.format(x) == msg and x.levelname == levelname]
        else:
            msgs = [x for x in self.storage if self.format(x) == msg]
        return True if len(msgs) else False

    def report(self):
        data = {
            "chronological": self.report_chronological(),
            "by_level": dict(),
            "condensed": self.report_by_context(),
            "by_level_condensed": dict(),
            "by_context_row": self.report_by_context_row(),
        }
        for level in self._default_levels:
            data["by_level"][level] = self.report_chronological(level)
            data["by_level_condensed"][level] = self.report_by_context(level)
        return data


def test():
    from django.apps import apps as django_app

    if not django_app.apps_ready:
        import django

        django.setup()

    from axis.filehandling.models import AsynchronousProcessedDocument
    from axis.core.utils import random_sequence

    doc, _ = AsynchronousProcessedDocument.objects.get_or_create(document=_srcfile, company_id=14)

    start = time.time()
    log_storage = LogStorage(model_id=doc.id)
    # l.setLevel(logging.ERROR)
    log_storage.debug("Debug me..!!")

    log_storage.info("This is INFO AWESOME!!")
    log_storage.warning("This is WARNING!")

    try:
        raise IOError("You stink..")
    except IOError:
        log_storage.exception("Whoa..")

    log_storage.warning("Oh DUP1 No...")
    log_storage.warning("Oh DUP1 No...")

    log_storage.set_context(row=1)
    log_storage.set_flags(home_created=True)
    log_storage.warning("Oh No...")
    log_storage.set_context(row=2)
    log_storage.set_flags(home_created=False)
    log_storage.warning("Oh DUP No...")
    log_storage.warning("Oh DUP No...")
    log_storage.set_context(row=3)
    log_storage.warning("Oh DUP No...")
    log_storage.error("Oh No...")

    log_storage.warning("Test (%r)", [1, 2, 3])
    log_storage.warning("Test 2 ({a})", {"a": [1, 2, 3]})
    log_storage.set_context(row=None)
    log_storage.set_flags(abitrary_flag="something")
    log_storage.debug("This is AWESOME!! {}".format(random_sequence()))

    log.warning("Test %(stuff)r", dict(stuff=[1, 2, 3]))
    log_storage.warning("Test %(stuff)r", dict(stuff=[1, 2, 3]))

    log_storage.info("End %(end).2f secs", dict(end=time.time() - start))

    pprint.pprint(log_storage.report_by_context())

    # l.remove_message('AWESOME')
    # l.remove_message('Debug me..!!')
    # l.remove_message('Oh', context={'row': 1})
    # l.remove_message('Oh', context={'row': 3})
    # l.remove_message('Oh', use_current_context=True)
    # l.set_context(row=1)
    # l.remove_message('Oh', use_current_context=True)

    pprint.pprint(log_storage.report_by_context())
    # from pprint import pprint
    # pprint(l.report_by_context())

    # import time
    # time.sleep(5)
    #
    # l.debug("This is AWESOME!! {}".format(random_sequence()))
    #
    # import pprint
    # pprint.pprint(l.report())
    #
    # print("{:.2f}".format(l.storage[-1].created - l.storage[0].created))


if __name__ == "__main__":
    test()
