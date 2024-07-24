"""utils.py - simulation"""
import datetime
import logging
import random
import re
import string
from collections import OrderedDict

__author__ = "Steven K"
__date__ = "5/27/20 16:05"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


def pop_kwargs(prefix, kwargs):
    """In place pop and split out kwargs"""
    data = OrderedDict()
    for k, v in list(kwargs.items()):
        if k.startswith(prefix):
            data[k.replace(prefix, "")] = kwargs.pop(k)
    return data


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


def random_sequence(length=8, include_letters=True, include_digits=True, include_unicode=True):
    """This will give you a random string with some UTF-8 letters in the mix"""
    chars = ""
    if include_letters:
        chars += string.ascii_letters
    if include_digits:
        chars += string.digits * 2
    if include_unicode:
        chars += "".join(RANDOM_LETTER_LIKE_UNICODE)
    while True:
        if len(chars) > length:
            break
        chars += chars
    return "".join(random.sample(chars, length))


def random_digits(length=8):
    return random_sequence(length, False, True, False)


def random_alphanum(length=8):
    return random_sequence(length, True, True, False)


def get_factory_from_fields(ModelObject, allow_null=False, allow_blank=False):
    data = OrderedDict()

    def get_field_choies(field):
        options = None
        if field.choices is not None:
            try:
                options = [x[0] for x in field.choices]
            except TypeError:
                _args = (ModelObject.__class__.name, field.name, field.choices)
                print("Invalid field choices %s.%s %r" % _args)
        return options

    for field in ModelObject._meta.fields:
        if field.auto_created or field.is_relation:
            continue
        if field.__class__.__name__ == "NullBooleanField":
            data[field.name] = random.choice([True, False, None])
            # print('%s = random.choice([True, False, None])' % field.name)
        elif field.__class__.__name__ == "BooleanField":
            data[field.name] = random.choice([True, False])
            # print('%s = random.choice([True, False])' % field.name)
        elif field.__class__.__name__ == "IntegerField":
            options = get_field_choies(field)
            if not options:
                options = range(-100, 1000)
            data[field.name] = random.choice(options)
            # print('%s = random.choice(%s)' % (field.name, list(options)))
        elif field.__class__.__name__ == "PositiveIntegerField":
            options = get_field_choies(field)
            if not options:
                options = range(0, 1000)
            data[field.name] = random.choice(options)
            # print('%s = random.choice(%s)' % (field.name, list(options)))
        elif field.__class__.__name__ == "FloatField":
            data[field.name] = random.choice(range(-100, 1000)) * random.random()
            # print('%s = random.choice(range(-100, 1000)) * random.random()' % field.name)
        elif field.__class__.__name__ == "DateTimeField":
            if field.auto_now_add or field.auto_now:
                continue
            value = random.choice(range(-60 * 60 * 24 * 7, 60 * 60 * 24 * 7))
            now = datetime.datetime.now(datetime.timezone.utc)
            data[field.name] = now + datetime.timedelta(seconds=value)
            # print('value = random.choice(range(-60 * 60 * 24 * 7, 60 * 60 * 24 * 7))')
            # print('now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)')
            # print('%s = now + datetime.timedelta(seconds=value)' % field.name)
        elif field.__class__.__name__ in ["CharField", "TextField"]:
            chaos = random.choice(range(1, 20))
            if field.name == "name":
                data[field.name] = "Name %s" % chaos
                # print('%s = get_random_name()' % field.name)
                continue
            if field.name == "note":
                data[field.name] = "Some generated %s" % chaos
                # print('%s = "Some generated data"' % field.name)
                continue
            if allow_null and field.null and chaos == 1:
                data[field.name] = None
                continue
            if allow_blank and field.blank and chaos == 2:
                data[field.name] = ""
                continue
            else:
                options = get_field_choies(field)

            if not options:
                max_length = 20 if field.__class__.__name__ == "CharField" else 1000
                max_length = field.max_length or max_length
                options = [
                    random_sequence(random.choice(range(max_length))),
                    random_sequence(random.choice(range(max_length))),
                ]
            data[field.name] = random.choice(options)
        else:
            msg = "Fix me! %s uses %s" % (ModelObject, field.__class__.__name__)
            raise NotImplementedError(msg)

    return data
