"""utils.py: """

__author__ = "Artem Hruzd"
__date__ = "10/17/2021 1:36 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


def queryset_user_is_authenticated(method):
    """
    Decorator method for filter_by_user method that checks the passed user object
    and returns an empty queryset if user does not have a company or is not
    authenticated. For superusers, always returns full list without calling the
    actual method.

    Example:

    @queryset_user_is_authenticated
    def filter_by_user(self, user):
        return self

    :param method: filter_by_user queryset method
    :return: queryset
    """

    def wrap(self, user, *args, **kwargs):
        if not user:
            return self.none()

        if not user.is_authenticated:
            return self.none()

        if not user.company:
            return self.none()

        if user.is_superuser:
            return self

        return method(self, user, *args, **kwargs)

    return wrap
