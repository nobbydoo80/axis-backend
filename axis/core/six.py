"""six.py: """


__author__ = "Artem Hruzd"
__date__ = "05/12/2020 20:56"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


def safe_hasattr(obj, name):
    """
    hasattr in py3 behaves like in py2 by catching all Exceptions.
    This function is only useful with django Model objects,
    in all other cases it is recommended to use:
    getattr(obj, foo, None)
    https://medium.com/@k.wahome/python-2-vs-3-hasattr-behaviour-f1bed48b068
    :param obj: object
    :param name: attribute name
    :return: boolean
    """
    try:
        return hasattr(obj, name)
    except Exception:
        return False
