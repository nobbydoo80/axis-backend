"""routers.py: This will define the database router for the catalog"""


__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]


class RemrateRouter(object):
    """A router to control all database operations on models in
    the aec_remrate application"""

    def db_for_read(self, model, **hints):
        """Point all operations on remrate models to 'remrate'"""
        if model._meta.app_label == "aec_remrate":
            return "remrate_ext"
        return None

    def db_for_write(self, model, **hints):
        """Point all operations on remrate models to 'remrate'"""
        if model._meta.app_label == "aec_remrate":
            return "remrate_ext"
        return None

    def allow_migrate(self, db, app_label, **hints):
        """Make sure the remrate app only appears on the 'remrate' db"""
        if db == "remrate_ext":
            return app_label == "aec_remrate"
        elif app_label == "aec_remrate":
            return False
        return None
