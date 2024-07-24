"""routers.py: This will define the database router for the customer_neea"""

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

INTERNAL_MODELS = [
    "pnwzone",
    "standardprotocolcalculator",
    "neeacertification",
    "candidate",
    "historicalneeacertification",
]


class NEEARouter(object):
    """A router to control all database operations on models in
    the customer_neea application"""

    def db_for_read(self, model, **hints):
        "Point all operations on customer_neea models to 'customer_neea'"
        if model._meta.app_label == "customer_neea":
            if model._meta.model_name not in INTERNAL_MODELS:
                return "customer_neea"
            return "default"
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on customer_neea models to 'customer_neea'"
        if model._meta.app_label == "customer_neea":
            if model._meta.model_name not in INTERNAL_MODELS:
                return "customer_neea"
            return "default"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation if a model in axis is involved"""
        if obj1._meta.app_label == "customer_neea" or obj2._meta.app_label == "customer_neea":
            if (
                obj1._meta.model_name not in INTERNAL_MODELS
                and obj2._meta.model_name not in INTERNAL_MODELS
            ):
                return True
            elif (
                obj1._meta.model_name in INTERNAL_MODELS
                and obj2._meta.model_name in INTERNAL_MODELS
            ):
                return True
            elif (
                obj1._meta.model_name in INTERNAL_MODELS
                and obj2._meta.model_name not in INTERNAL_MODELS
            ):
                return obj2._meta.app_label != "customer_neea"
            elif (
                obj1._meta.model_name not in INTERNAL_MODELS
                and obj2._meta.model_name in INTERNAL_MODELS
            ):
                return obj1._meta.app_label != "customer_neea"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        "Make sure the customer_neea app only appears on the 'customer_neea' db"
        if app_label == "customer_neea":
            if model_name not in INTERNAL_MODELS:
                return db == "customer_neea"
        return None
