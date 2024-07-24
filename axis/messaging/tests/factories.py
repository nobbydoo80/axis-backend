"""factories.py: """

__author__ = "Artem Hruzd"
__date__ = "05/20/2020 19:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from collections import defaultdict

from axis.core.tests.factories import provider_user_factory
from axis.core.utils import random_sequence
from axis.messaging.messages import ModernMessage
from axis.messaging.models import Message, MessagingPreference


def modern_message_registry_factory(modern_messages):
    """
    Override default MESSAGE_CATEGORIES and MESSAGE_REGISTRY global variables
    :param modern_messages: list of modern message classes
    """
    message_categories = defaultdict(set)
    message_registry = dict()

    for modern_message in modern_messages:
        if modern_message.__name__ in message_registry:
            pass
        else:
            message_categories[modern_message.category].add(modern_message)
            message_registry[modern_message.__name__] = modern_message
    return message_registry, message_categories


def modern_message_cls_factory(cls_name, **kwargs):
    """
    :param cls_name: python class name
    :param kwargs: ModernMessage attributes. Make sure you are passing correct type
    :return: class
    """
    kwrgs = {
        "title": "title{}".format(random_sequence(4)),
        "content": "content{}".format(random_sequence(4)),
        "email_content": None,
        "email_subject": None,
        "level": "debug",
        "category": "category{}".format(random_sequence(4)),
        "url": "dummy{}".format(random_sequence(4)),
        "required": False,
        "company_admins_only": False,
        "company_slugs": None,
        "company_types": None,
    }
    kwrgs.update(kwargs)
    return type(cls_name, (ModernMessage,), kwrgs)


def message_factory(**kwargs):
    """
    Create a database Message object
    :param kwargs:
    :return:
    """
    user = kwargs.pop("user", provider_user_factory())
    sender = kwargs.pop("sender", provider_user_factory())
    kwrgs = {
        "user": user,
        "sender": sender,
        "title": "title{}".format(random_sequence(4)),
        "content": "content{}".format(random_sequence(4)),
        "level": "debug",
        "category": "category{}".format(random_sequence(4)),
        "url": "dummy{}".format(random_sequence(4)),
        "sticky_alert": True,
        "date_alerted": None,
        "date_sent": None,
        "alert_read": False,
        "email_read": False,
    }

    kwrgs.update(kwargs)

    message = Message.objects.create(**kwrgs)
    return message


def messaging_preference_factory(**kwargs):
    user = kwargs.pop("user", provider_user_factory())
    kwrgs = {
        "message_name": "MessageClass{}".format(random_sequence(4)),
        "user": user,
    }
    kwrgs.update(kwargs)
    messaging_preference = MessagingPreference.objects.create(**kwrgs)
    return messaging_preference
