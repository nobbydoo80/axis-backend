__author__ = "Steven Klass"
__date__ = "5/22/12 8:36 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import collections
import datetime
import hashlib
import inspect
import io
import logging
import os
import random
import re
import signal
import string
import timeit
from base64 import b64decode
from collections import defaultdict
from operator import attrgetter
from typing import Any

import requests
from celery import states
from celery.app import app_or_default
from django.apps import apps
from django.conf import settings
from django.contrib.admin.utils import NestedObjects
from django.core.cache import cache
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db import router
from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms import FileField
from django.http import QueryDict
from django.utils import timezone
from rest_framework.fields import SerializerMethodField
from collections import defaultdict

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_str

    force_unicode = force_str

from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import slugify, capfirst

from PyPDF2.generic import NameObject, NumberObject

from axis.core.pypdf import AxisPdfFileReader, AxisPdfFileWriter

# Import list of fields needed to make PyPDF2 behave with our PDF form

frontend_app = apps.get_app_config("frontend")


log = logging.getLogger(__name__)

PHONE_DIGITS_RE = re.compile(r"^(?:1-?)?(\d{3})[-\.]?(\d{3})[-\.]?(\d{4})$")

YEAR_CHOICES = [(year, year) for year in range(2008, datetime.date.today().year + 1)]

# NOTE: This should be string-formatted for the "contenttypes" parameter so that it knows what
# types are valid!  Contenttypes are strings such as "image/png" and "text/plain"
BASE64_CONTENT_PATTERN = r"^data:(?P<content_type>{contenttypes});base64,(?P<data>.*)$"

TEST_FEEDS = [
    {
        "name": "Energy and Environment: What’s New",
        "url": "http://eetd.lbl.gov/eetd.xml",
        "domain": "eetd.lbl.gov",
    },
    {
        "name": "U.S. EPA News",
        "url": "http://www.energystar.gov/cms/tasks/feed/?feedID=0D8F0200-188B-36F7-214FA4E76194E8AF",
        "domain": "epa.gov",
    },
    {"name": "RESBlog", "url": "http://www.resnet.us/blog/feed/", "domain": "resnet.us"},
    {
        "name": "Musings of an Energy Nerd",
        "url": "http://www.greenbuildingadvisor.com/blogs/dept/musings/rss",
        "domain": "greenbuildingadvisor.com",
    },
    {
        "name": "Midwest Energy News",
        "url": "http://www.midwestenergynews.com/feed",
        "domain": "www.midwestenergynews.com",
    },
]

SELECT2_OPTIONS = {
    "data-placeholder": "Type to search",
    "data-close-on-select": "true",
}

RANDOM_LETTER_LIKE_UNICODE = [
    chr(0x00C0),
    chr(0x00C1),
    chr(0x00C2),
    chr(0x00C3),
    chr(0x00C4),
    chr(0x00C5),
    chr(0x00C8),
    chr(0x00C9),
    chr(0x00CA),
    chr(0x00CB),
    chr(0x00CC),
    chr(0x00CD),
    chr(0x00CE),
    chr(0x00CF),
    chr(0x00D2),
    chr(0x00D3),
    chr(0x00D4),
    chr(0x00D5),
    chr(0x00D6),
    chr(0x00D9),
    chr(0x00DA),
    chr(0x00DB),
    chr(0x00DC),
    chr(0x00DD),
    chr(0x00E0),
    chr(0x00E1),
    chr(0x00E2),
    chr(0x00E3),
    chr(0x00E4),
    chr(0x00E5),
    chr(0x00E8),
    chr(0x00E9),
    chr(0x00EA),
    chr(0x00EB),
    chr(0x00EC),
    chr(0x00ED),
    chr(0x00DE),
    chr(0x00EF),
    chr(0x00F2),
    chr(0x00F3),
    chr(0x00F4),
    chr(0x00F5),
    chr(0x00F6),
    chr(0x00F9),
    chr(0x00FA),
    chr(0x00FB),
    chr(0x00FC),
    chr(0x00FD),
    chr(0x00FF),
    chr(0x00DF),
]
COMMON_UNICODE = [chr(x) for x in list(range(0xA1, 0xFF + 1))]

LONG_DASHES = re.compile(r"{emdash}|{endash}".format(emdash="–", endash="-"))


def random_sequence(
    length=8, include_letters=True, include_digits=True, include_unicode=True
) -> str:
    """This will give you a random string with some UTF-8 letters in the mix"""
    chars = ""
    if include_letters:
        chars += string.ascii_letters
    if include_digits:
        chars += string.digits * 2
    if include_unicode:
        chars += "".join(RANDOM_LETTER_LIKE_UNICODE)
    return "".join(random.sample(chars, length))


def random_digits(length=8) -> str:
    """Return random digits"""
    return random_sequence(length=length, include_letters=False, include_unicode=False)


def random_latitude() -> float:
    return random.uniform(-90, 90)


def random_longitude() -> float:
    return random.uniform(-180, 180)


def randomize_filename(filename, length=8, separator="_", name=None):
    """Get file and provide a unique name"""
    if not isinstance(filename, str):
        filename = "{}".format(filename)
    prefix = slugify(filename)
    extension = None
    if len(filename.split(".")) > 1:
        prefix = slugify(".".join(filename.split(".")[:-1]))
        extension = filename.split(".")[-1]
    name = random_sequence(length, include_unicode=False) if name is None else name
    cleaned_name = "{prefix}{separator}{name}"
    if extension:
        cleaned_name += ".{extension}"
    return cleaned_name.format(prefix=prefix, separator=separator, name=name, extension=extension)


def unrandomize_filename(filename, length=8, separator="_"):
    """Reverse the process of randomize_filename"""
    base_filename = os.path.basename(filename)
    extension = None
    prefix = base_filename[: -(length + len(separator))]
    if len(filename.split(".")) > 1:
        prefix = ".".join(base_filename.split(".")[:-1])
        prefix = prefix[: -(length + len(separator))]
        extension = base_filename.split(".")[-1]
    final = "{}".format(prefix)
    if extension:
        final += ".{}".format(extension)
    return os.path.join(os.path.dirname(filename), final)


def humanize_bytes(num):
    """Simply humanize the bytes"""
    for x in ["bytes", "KB", "MB", "GB"]:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, "TB")


def set_help_text_from_model(modelform, field_name):
    model = modelform._meta.model
    modelform.fields[field_name].help_text = model._meta.get_field(field_name).help_text


def set_verbose_name_from_model(modelform, field_name):
    """
    Make sure that all fields passed to this util have declared verbose names on the model field.
    Otherwise field label will be set to lowercased version of field name.
    """
    model = modelform._meta.model
    modelform.fields[field_name].label = model._meta.get_field(field_name).verbose_name


UNSET = "this is an unset value"


def getfirst(iterable, where=None, attr=None, getter=None, default=UNSET):
    """
    Returns the first item in ``iterable`` for which the ``where`` function returns True.

    ``where=None`` performs no filtering check.

    If set, ``default`` is the default return value if no element in ``iterable`` is available,
    either because ``iterable`` is empty or the ``where`` condition filtered away all elements.

    If supplied, ``attr`` may be an attribute name on the value that is returned in place of the
    value itself.  Alternately, ``getter`` may be a mapping function that performs this work.  Only
    one or the other should be supplied.  If the ``default`` value is returned by getfirst,
    attribute lookups via ``attr`` or ``getter`` are skipped in favor of the raw default value.
    """

    # Verify correct use of EITHER attr OR getter, not both at the same time
    assert attr is None or getter is None, "Please provide only one of 'attr' and 'getter' args."

    # Filter elements.  where=None is normally an identity function, so items such as 0, "", False,
    # None, [], (), {} would all be removed by default.  Instead, if "where" is None, we'll just
    # skip the filtering step and let the user explicitly supply an identity function if they want
    # it.
    if where is not None:
        matching_elements = filter(where, iterable)
    else:
        matching_elements = iterable

    if not matching_elements:
        if default == UNSET:
            raise IndexError("'getfirst' cannot fetch value from empty list.")
        return default

    value = matching_elements[0]

    # Turn a raw 'attr' string into an operator.attrgetter partial
    if attr:
        getter = attrgetter(attr)

    if getter is not None:
        value = getter(value)

    return value


def filter_integers(data):
    """Maps a value to an integer if possible, discards if TypeError/ValueError is raised."""
    for v in data:
        try:
            yield int(v)
        except (ValueError, TypeError):
            pass


def values_to_dict(values_queryset, key, value_key=None, value_as_list=False):
    """Re-keys a values queryset of dicts to a single dict based on ``key``."""
    # input = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 3, 'b': 5}]
    # values_to_dict(input, 'a') = {1: {'b': 2},  3: {'b': 5}}
    # values_to_dict(input, 'a', 'b') = {1: 2,  3: 5}
    # values_to_dict(input, 'a', value_as_list=True) = {1: [{'b': 2}], 3: [{'b': 4'}, {'b': 5}]}
    # values_to_dict(input, 'a', 'b', value_as_list=True) = {1: [2], 3: [4, 5]}
    result = {}
    if value_as_list:
        result = collections.defaultdict(list)
    multi = value_key is None
    for item in values_queryset:
        if multi:
            v = item.copy()
        else:
            v = item[value_key]
        if value_as_list:
            result[item[key]].append(v)
        else:
            result[item[key]] = v
    return result


def select_queryset_values(queryset, pop=False, **aliases):
    """
    Uses **kwargs keys in ``queryset.values()``, then sends the result to ``alias_valuesqueryset()``
    and **kwargs forwarded.

    Sending a **kwargs argument with a value of ``None`` will cause the key to be looked up, but no
    alias to be generated.
    """
    values_qs = queryset.values(*aliases.keys())
    return alias_valuesqueryset(values_qs, pop=pop, **aliases)


def alias_valuesqueryset(values_qs, pop=False, **aliases):
    """
    Each of the **kwargs values are used as aliases to copy the value looked up by the key to
    something simpler to access for frontend purposes. For example:

        make_valuesqueryset(queryset, **{
            # The full key name will be in the values queryset, but will be duplicated for
            # convenience as 'eep_program'.
            'home_status__eep_program__name': 'eep_program',
        })

    If ``pop`` is ``True`` and an alias was made, the original verbose key will be removed.
    """

    for data in values_qs:
        for k, v in list(data.items()):
            short_name = aliases.get(k)
            if short_name:
                data[short_name] = v
                if pop:
                    del data[k]
    return values_qs


def collect_nested_object_list(model_instance, format_callback=None):
    """
    Takes a model instance (or list/QuerySet of instances) and recursively lists its dependent
    objects in the database.
    """

    if hasattr(model_instance, "model"):
        model = model_instance.model
    else:
        model = model_instance.__class__

    collector = NestedObjects(using=router.db_for_write(model))
    if isinstance(model_instance, Model):
        model_instance = [model_instance]
    collector.collect(model_instance)

    def default_format_callback(obj):
        verbose_name = capfirst(obj._meta.verbose_name)
        repr_func = force_unicode
        if hasattr(obj, "get_absolute_url"):
            url = obj.get_absolute_url()

            def repr_func(obj):
                return '<a href="{}" target="_blank">{}</a>'.format(url, obj)

        return mark_safe("{}: {}".format(verbose_name, repr_func(obj)))

    return collector.nested(format_callback or default_format_callback)


def slugify_uniquely(slug, model, start_no=0, max_length=50, slug_field="slug"):
    """Finds a unique slug with a counter suffix to the ``slug_field`` value."""
    slug = slug if slug else "NO_NAME"
    slug = slugify("{}".format(slug[:max_length]))
    new_slug = slug
    counter = start_no
    while model.objects.filter(**{slug_field: new_slug}).exists():
        if max_length > 0:
            if len(slug) + len("-") + len(str(counter)) > max_length:
                # make room for the "-1, -2 ... etc"
                slug = slug[: max_length - (len(slug) + len("-") + len(str(counter)))]
        new_slug = "%s-%s" % (slug, counter)
        counter += 1
    return new_slug


def enforce_order(
    data, preferred_order_list, sort_remainder_alphabetically=True, key_transform=None
):
    """
    Takes data that will be sorted, and a list of key names for preferred ordering.  The
    key_transform should be a callable that maps a single data item for lookup in that preferred
    ordering list.  If a key can't be found in the priority list, that item will appear after all
    sortable items, stable to the order it came in.

    sort_remainder_alphabetically allows the un-prioritized items to be sorted naturally instead of
    being left in stable order.

    If ``data`` is a dict, it is broken down via ``data.items()`` and treated as a list where the
    keys are used for lookup in the preferred ordering list.  It is then rebuilt as an OrderedDict
    and returned instead of the raw sorted items.

    NOTE: If ``data`` is a dict and you provide a custom ``key_transform`` function, it will need to
    take a ``(k,v)`` tuple as the sorted item, not just the key.
    """

    # Build a dict in the form of {item: order}, where order is higher for being farther down the
    # preferred ordering list.
    order_lookup = dict(map(reversed, enumerate(preferred_order_list)))

    is_dict = isinstance(data, dict)
    if is_dict:
        data = data.items()

    # Coerce to our 'list' return type now.  Tuples, sets, dicts, etc will all ultimately become
    # lists anyway
    frozen_data = list(data)  # We need to use .index() for stable ordering mode anyway

    # How to look up a data item in the ordering spec
    if key_transform is None:
        if is_dict:

            def key_transform(k_v):
                return k_v[0]

        else:

            def key_transform(item):
                return item

    # How to sort items that aren't in the ordering spec
    # Note that no special lambda treatment is required for dict.items() data, because frozen data
    # will contain the item directly.
    priority_offset = len(order_lookup)  # A safe value that comes after all other priorities

    def remainder_transform(item):
        if not sort_remainder_alphabetically:
            return priority_offset + frozen_data.index(item)

        if is_dict:
            return item[0]
        else:
            return item

    def get_priority(item):
        return str(order_lookup.get(key_transform(item), remainder_transform(item)))

    sorted_data = sorted(frozen_data, key=get_priority)

    if is_dict:
        sorted_data = collections.OrderedDict(sorted_data)

    return sorted_data


def get_generic_fk_data(instance_or_queryset, as_dict=True, prefix=""):
    """
    Returns the ContentType instance and object pk of the given instance as a 2-tuple.  If the given
    data is an iterable instead of a single instance, a list of ids will be given as the second item
    of the tuple instead of just one pk.

    If ``as_dict`` is True and the given data is a queryset, the dict key will convert from
    ``object_id`` to ``object_id__in`` to simplify direct forwarding into the ORM language.
    """
    from django.contrib.contenttypes.models import ContentType

    if isinstance(instance_or_queryset, QuerySet):
        model = instance_or_queryset.model
        id = list(instance_or_queryset.values_list("id", flat=True))
        id_key = "object_id__in"
    elif isinstance(instance_or_queryset, list):
        if not len(instance_or_queryset):
            return {}  # empty list will make filtering on a None contenttype pointless
        model = instance_or_queryset[0].__class__
        id = instance_or_queryset
        id_key = "object_id__in"
    else:
        model = instance_or_queryset
        id = instance_or_queryset.pk
        id_key = "object_id"

    ct = ContentType.objects.get_for_model(model)  # This keeps its own query cache
    values = (ct, id)
    if as_dict:
        ct_key = "%scontent_type" % prefix
        id_key = "%s%s" % (prefix, id_key)
        return dict(zip((ct_key, id_key), values))
    return values


TASK_STATE_COLORS = {
    states.SUCCESS: "green",
    states.FAILURE: "red",
    states.REVOKED: "magenta",
    states.STARTED: "yellow",
    states.RETRY: "orange",
    "RECEIVED": "blue",
    "PENDING": "black",
    "UNACKNOWLEDGED": "grey",
}


def get_task_status(task_id, as_dict=False):
    """Attempt to find the status of a task - this will be limited for unack'd jobs"""

    assert task_id, "You need to provide a task id"

    status_args = [
        "task_id",
        "task_name",
        "state",
        "pretty_state",
        "time_start",
        "time_end",
        "hostname",
        "host_alive",
        "queue_name",
        "queue_depth",
        "pending",
        "state_obj",
    ]
    TaskStatus = collections.namedtuple("TaskStatus", status_args)

    def get_color(state):
        return '<b><span style="color: {};">{}</span></b>'.format(TASK_STATE_COLORS[state], state)

    data = collections.OrderedDict(
        [
            ("task_id", task_id),
            ("task_name", None),
            ("state", "UNACKNOWLEDGED"),
            ("pretty_state", get_color("UNACKNOWLEDGED")),
            ("time_start", None),
            ("time_end", None),
            ("hostname", None),
            ("host_alive", None),
            ("queue_name", None),
            ("queue_depth", "Unknown"),
            ("pending", []),
            ("state_obj", None),
        ]
    )

    tracked = False
    # First do we have it?
    from django_celery_results.models import TaskResult

    try:
        result = TaskResult.objects.get(task_id=task_id)
        data["task_name"] = result.task_name
        data["state"] = result.status
        data["pretty_state"] = get_color(result.status)
        data["state_obj"] = result
        data["hostname"] = result.result.get("hostname")
        if result.status in ["SUCCESS", "FAILURE"]:
            result["time_end"] = result.date_done
        tracked = True
    except TaskResult.DoesNotExist:
        result = None

    # Supplement this with any relevant data - This doesn't stick around long
    # but it's valuable
    app = app_or_default()
    inspect = app.control.inspect()

    # https://github.com/celery/celery/issues/5067
    try:
        with timeout(5):
            statuses = inspect.query_task([task_id])
    except TimeoutError:
        statuses = None
    except ValueError as err:
        if "signal only works in main thread" not in "{}".format(err):
            raise
        statuses = None

    if isinstance(statuses, dict):
        for host, tasks in statuses.items():
            for task, (state, task_data) in tasks.items():
                if task == task_id:
                    data["hostname"] = task_data.get("hostname")
                    try:
                        data["time_start"] = datetime.datetime.utcfromtimestamp(
                            float(task_data.get("time_start"))
                        )
                    except TypeError:
                        data["time_start"] = task_data.get("time_start")
                    data["queue_name"] = task_data.get("delivery_info", {}).get("exchange")

    if data["state"] == "RECEIVED":
        app = app_or_default()
        inspect = app.control.inspect()
        statuses = inspect.reserved()
        for host, jobs in statuses.items():
            for idx, job in enumerate(jobs):
                if job.get("id") == task_id:
                    data["hostname"] = job.get("hostname")
                    try:
                        data["time_start"] = datetime.datetime.utcfromtimestamp(
                            float(job.get("time_start"))
                        )
                    except TypeError:
                        data["time_start"] = job.get("time_start")
                    data["queue_name"] = job.get("delivery_info", {}).get("exchange")
                    data["hostname"] = job.get("hostname")
                    data["queue_depth"] = idx + 1
                    break
                else:
                    data["pending"].append((job.get("name"), job.get("id")))

    if not tracked:
        vhost = re.sub(r"amqp", "http", settings.CELERY_BROKER_URL).split("/")[-1]
        base_url = "http://{}:{}".format(settings.CELERY_BROKER_HOST, "15672")
        url = base_url + "/api/queues/{}/".format(vhost)
        try:
            req = requests.get(
                url, auth=(settings.CELERY_BROKER_USER, settings.CELERY_BROKER_PASSWORD), timeout=1
            )
        except requests.Timeout:
            req = None
            data["queue_depth"] = "Timeout waiting for answer.."
            log.warning("Timeout from RabbitMQ")

        if not req or req.status_code != 200:
            if req:
                log.warning("Bad Response from RabbitMQ: %s", req.text)
            data["queue_depth"] = "Unknown"
            data["queue_depth"] = data.get("queue_depth", "Awaiting Answer..")
            data["state"] = "UNACKNOWLEDGED"
            data["pretty_state"] = get_color("UNACKNOWLEDGED")
        else:
            request_data = req.json()
            for queue in request_data:
                # Now we are primariy focused on our celery queue:
                # TODO if we know what queue the task is then we can nail this.
                if queue.get("name") == "celery":
                    data["queue_depth"] = "Unknown"
                    if queue.get("messages"):
                        data["queue_depth"] = "< {}".format(queue.get("messages"))
                        data["pending"] = [None for x in range(queue.get("messages"))]
                        data["state"] = "PENDING"
                        data["pretty_state"] = get_color("PENDING")

    if as_dict:
        return dict(data)
    return TaskStatus(*data.values())


def get_field_verbose_names(obj):
    return {f.name: f.verbose_name for f in obj._meta.local_fields}


def clean_base64_encoded_payload(filename, data, formfield=FileField, valid_content_types=None):
    """
    Receives a base64-encoded payload and tries to do generic validation against it.  The return
    value is a standard django.forms.FileField cleaned "FieldFile", so that it may be used directly
    as a form.cleaned_data value.
    """
    if not filename:
        # Something's wrong with the form's submission
        return None

    if not data:
        return data

    if valid_content_types is None:
        valid_content_types = [r"\w+\/[\w.\+\-]+", ""]  # Everything.
    pattern = BASE64_CONTENT_PATTERN.format(contenttypes="|".join(valid_content_types))
    match = re.match(pattern, data, re.I)
    if not match:
        # This should give us what we need the first 100 chars of what is supposed to be
        # the content_type
        head = data.split("base64")[0].split("data:")[-1].split(";")[0][:100]
        log.warning(
            f"{filename} was uploaded with incorrect file type ({head}) first 128 chars"
            f" {data[:128]}"
        )
        raise ValidationError(f"That file type ({head}) is not allowed.")

    content_type = match.group("content_type")
    data = b64decode(match.group("data"))

    content_file = ContentFile(data, name=filename)
    uploaded_file = UploadedFile(content_file, filename, content_type, size=content_file.size)

    return formfield().to_python(uploaded_file)


def get_previous_day_start_end_times(now=None):
    """
    Get a previous day date range from midnight. For example:
    Today is `10 July 14:54` and function will return
    `09 July 00:00` and `10 July 00:00`
    :param now: datetime object. Default: timezone.now()
    :return: tuple(datetime, datetime)
    """
    if not now:
        now = timezone.now()
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_midnight = today_midnight - timezone.timedelta(days=1)
    return yesterday_midnight, today_midnight


def get_n_days_range(range, as_datetime=False):
    today = datetime.date.today()
    if as_datetime:
        today = datetime.datetime.now(datetime.timezone.utc)
    return (today - datetime.timedelta(days=range)), today


def get_current_quarter_range(as_datetime=False):
    today = datetime.date.today()
    if as_datetime:
        today = datetime.datetime.now(datetime.timezone.utc)
    DAY = datetime.timedelta(days=1)
    quarter_first_days = [
        datetime.date(datetime.MINYEAR + 1, month, 1) for month in [1, 4, 7, 10, 1]
    ]

    i = (today.month - 1) // 3  # get quarter index
    start = quarter_first_days[i].replace(year=today.year)
    end = (quarter_first_days[i + 1] - DAY).replace(year=today.year)

    if end < start:
        end.replace(year=today.year + 1)

    return start, end


class BlockTimer(object):
    indent = "  * "
    level = 0

    def __init__(self, name=None, **context):
        if not name:
            current_frame = inspect.currentframe()
            name = inspect.getframeinfo(current_frame.f_back).function
        self.name = name
        self.context = context

    def __enter__(self):
        self.start = timeit.default_timer()
        self.print_start()
        self.__class__.level += 1
        return self

    def __exit__(self, *args):
        self.end = timeit.default_timer()
        self.interval = self.end - self.start
        self.__class__.level -= 1
        self.print_end()

    def print_start(self):
        """Print the start Block"""
        msg = "BEGIN {name} : {context}".format(name=self.name, context=repr(self.context))
        log.debug("{indent}{msg}".format(indent=self.indent * self.__class__.level, msg=msg))

    def print_end(self):
        """Print the end Block"""
        msg = "END   {name} = {time:.03f}".format(name=self.name, time=self.interval)
        log.debug("{indent}{msg}".format(indent=self.indent * self.__class__.level, msg=msg))


class TimeoutError(Exception):
    """Timeout Exception"""

    pass


class timeout:
    """A simple class for timing out stuff"""

    def __init__(self, seconds=1, error_message="Timeout"):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        """Handle the timeout"""
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def fill_flatten_ea_pdf_template(pdf_form, data):
    filtered_data = {}
    for k, v in data.items():
        if v is not None:
            filtered_data[k] = v

    data = filtered_data

    with io.open(pdf_form, "rb") as input_stream:
        pdf_reader = AxisPdfFileReader(input_stream, strict=False)

        pdf_writer = AxisPdfFileWriter()
        num_pages = len(pdf_reader.pages)

        for i in range(num_pages):
            pdf_writer.add_page(pdf_reader.pages[i])
            if i < num_pages - 4:
                page = pdf_writer.pages[i]
                pdf_writer.updatePageFormFieldValues(page, data)

        for i in range(num_pages - 4):
            page = pdf_writer.pages[i]
            for j in range(0, len(page["/Annots"])):
                writer_annot = page["/Annots"][j].get_object()
                for field in data:
                    if writer_annot.get("/T") == field:
                        writer_annot.update({NameObject("/Ff"): NumberObject(1)})

        output_stream = pdf_writer.get_pdf_stream()

    return output_stream


def get_user_perm_cache_key(user=None, user_id=None):
    """Get user perm cache key"""
    key = "user__perms__{}_v1"

    if user:
        return hashlib.sha1(key.format(user.id).encode("utf-8")).hexdigest()

    elif user_id:
        return hashlib.sha1(key.format(user_id).encode("utf-8")).hexdigest()

    raise ValueError("Must provide a User or a User ID")


def delete_user_perm_cache(user=None, user_id=None):
    """Delete user perm cache key"""
    cache.delete(get_user_perm_cache_key(user, user_id))


def email_html_content_to_text(html_content):
    """
    Removes html tags and css styles from string to create a txt version
    of email content
    :param html_content: html string
    :return: string without html and css tags
    """
    pattern = "<style([\\s\\S]+?)</style>"
    text = re.sub(pattern, "", html_content)

    text_message = strip_tags(text)
    return text_message


class RemoteIdentifiersMixin(object):
    """
    Dynamically makes serializer fields available for fetching available ID types.  Includes all
    available ids by default in the serializer fields.  Setting ``include_remote_identifiers`` to
    False will add the convenience getters for the various available ids, but will not automatically
    add fields on the serializer; the fields will be left up to the serializer to add on its own.
    """

    include_remote_identifiers = True
    remote_identifier_name_template = "{type}_id"

    stateless_instance = None

    def to_representation(self, instance):
        self.stateless_instance = instance
        data = super(RemoteIdentifiersMixin, self).to_representation(instance)
        return data

    def get_fields(self):
        fields = super(RemoteIdentifiersMixin, self).get_fields()

        if isinstance(self.instance, list):
            instance = False
        elif self.instance and self.instance.pk:
            instance = self.instance
        elif self.stateless_instance:
            instance = self.stateless_instance
        else:
            instance = None

        # Put the remote ids in the fields list (or just add getters so that the superclass can do
        # so if it wants to).
        if instance.pk:
            for k, v in instance.get_remote_identifiers().items():
                field_name = self.remote_identifier_name_template.format(type=k)
                if self.include_remote_identifiers:
                    fields[field_name] = SerializerMethodField()

                def getter(obj):
                    return v

                setattr(self, "get_{}".format(field_name), getter)

        return fields


# DEPRECATION - THis should not be needed anymore DRF 3.8 +
def make_safe_field(FieldClass):
    """
    Subclasses the target serializer field class to block DoesNotExist errors on dotted ``source``
    lookups on read_only=True fields.  This allows us to send unsaved Model() instances to the
    serializer and correctly read default values from the model, etc.
    """

    # This is a stopgap for DRF's failure to respect a model field's ``default`` value when the
    # ``instance`` it's working on is None.  Such a ``serializer.data`` result will ignore any
    # defaults set by fields and instead return a native default (always False for boolean fields,
    # etc).

    # The options were to re-implement the method without this short-circuit on default value, or
    # to simply send along our unsaved instance to the serializer and block failed FK lookups on the
    # object when trying to fetch values for sources like "builder_org.name" where builder_org is
    # not yet defined.

    class SafeField(object):
        def get_attribute(self, obj):
            try:
                return super(SafeField, self).get_attribute(obj)
            except (ValueError, AttributeError):
                # FileField without file attached yet raises ValueError when accessing url
                return None

        def to_representation(self, obj):
            try:
                return super(SafeField, self).to_representation(obj)
            except ObjectDoesNotExist:
                return None
            except (ValueError, AttributeError):
                # Reference to an m2m from an unsaved instance
                return []

    SafeFieldClass = type(str("Safe%s" % FieldClass.__name__), (SafeField, FieldClass), {})

    return SafeFieldClass


def zipdir(path, ziph):
    """
    Zip all files in directory
    :param path: path to directory
    :param ziph: is zipfile handle
    :return:
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def get_dict_totals(obj):
    """
    Takes a dict and returns dict of totals of items that can be summed.
    """
    totals = defaultdict(int)
    try:
        for metric in obj["data"]:
            for key in metric:
                if key.endswith("_id") or key == "id":
                    continue
                try:
                    0 + metric[key]
                except Exception:
                    continue
                totals[key] += metric[key]
    except KeyError:
        pass
    return dict(totals)


def has_beta_access(request):
    if request.user.is_authenticated and request.user.is_superuser or request.user.is_impersonate:
        if (
            request.user.show_beta
            or request.user.is_impersonate
            and request.user.impersonator.show_beta
        ):
            return True
    return False


def get_frontend_url(*parts) -> str:
    """
    Create new frontend url
    :param parts: parts of url. E.g "company", company_id will create url `/app/company/<company_id>`
    :return: string
    """
    url_parts = map(str, parts)
    return "/" + frontend_app.DEPLOY_URL + "/".join(url_parts)


def query_params_to_dict(query_params: QueryDict) -> dict[str, Any]:
    """
    When you need to pass request.params to serializer like:
    Serializer(data=self.request.query_params) or to celery task,
    default behavior of QueryDict.dict() method lose lists. For example query params:
    a=1&a=2 will be converted in celery task to {'a': 2}.
    This function will return {'a': [1, 2]}
    :param query_params: QueryDict
    :return: Fixed dict of params
    """
    return {
        k: query_params.getlist(k) if len(query_params.getlist(k)) > 1 else v
        for k, v in query_params.items()
    }
