"""base.py: Django """

__author__ = "Steven Klass"
__date__ = "1/24/13 9:16 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
    "Autumn Valenta",
]


from django.contrib.messages.storage.session import SessionStorage

from axis.messaging.constants import constants
from axis.messaging.models import Message
from axis.core.messages import AxisDjangoMessage


class MessagingStorage(SessionStorage):
    """
    Stores admin messages in the session (that is, django.contrib.sessions).
    and Axis messages in Message model. In django admin panel we show only session messages
    and on Axis we show both
    """

    def _get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return [], True
        admin_messages, all_retrieved = super(MessagingStorage, self)._get(*args, **kwargs)
        if admin_messages is None:
            admin_messages = []
        if self.request.path.startswith("/admin/"):
            return admin_messages, all_retrieved

        axis_messages = Message.objects.filter(user=self.request.user)
        return admin_messages + list(axis_messages), all_retrieved

    def _store(self, messages, response, *args, **kwargs):
        """Store in session only standard django messages"""
        messages = list(filter(lambda m: not isinstance(m, Message), messages))
        return super(MessagingStorage, self)._store(messages, response, *args, **kwargs)

    def add(self, level, message, extra_tags=""):
        if self.request.path.startswith("/admin/"):
            return super(MessagingStorage, self).add(level, message, extra_tags)
        if level < self.level:
            return

        modern_message = AxisDjangoMessage()
        modern_message.content = message
        modern_message.level = constants.DEFAULT_TAGS[level]
        modern_message.send(
            user=self.request.user,
        )
