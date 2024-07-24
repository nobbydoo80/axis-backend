"""registry.py: """


__author__ = "Artem Hruzd"
__date__ = "06/19/2020 18:43"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class AlreadyRegistered(Exception):
    pass


class NotRegistered(KeyError):
    pass


class Registry(dict):
    """
    Dictionary like object representing a collection of objects.

    To add items to the Registry, decorate the class with the ``register``
    method.

    my_registry  = Registry()

    @my_registry.register
    class Example(object):
        key = 'HDR0'


    Then when you'll be able to get the registered class back out of the
    Registry by accessing it like a dictionary with the key
    >>> my_registry['HDR0']
    <class 'path.to.module.Example'>

    """

    def __init__(self, key_name="key", display_name="display", *args, **kwargs):
        self.key_name = key_name
        self.display_name = display_name
        self.display_name_mapping = dict()
        super(Registry, self).__init__(*args, **kwargs)

    def register(self, _class):
        key = self._get_key_from_class(_class)
        if key in self:
            msg = "Key '{key}' has already been registered as '{name}'.".format(
                key=key, name=self[key].__name__
            )
            raise AlreadyRegistered(msg)

        display_name = self._get_display_name_from_class(_class)
        self.__setitem__(key, _class)
        self.display_name_mapping[key] = display_name

        return _class

    def unregister(self, _class):
        key = self._get_key_from_class(_class)
        if key in self:
            self.__delitem__(key)

    def _get_key_from_class(self, _class):
        return getattr(_class, self.key_name)

    def _get_display_name_from_class(self, _class):
        return getattr(_class, self.display_name)

    def __getitem__(self, key):
        """
        The Registry is a dictionary. Raising `NotRegistered` instead of
        a `KeyError` seems more appropriate.
        """
        if key in self:
            return super(Registry, self).__getitem__(key)

        raise NotRegistered("Key '{key}' has not been registered.".format(key=key))

    def as_choices(self):
        return [(key, self.display_name_mapping[key]) for key in self]
