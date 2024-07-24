"""utils.py: """


__author__ = "Rajesh Pethe"
__date__ = "2020-04-30 09:20:42"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Rajesh Pethe",
    "Steven Klass",
]


import MySQLdb
import logging
from django.conf import settings

log = logging.getLogger(__name__)


def remrate_db_scheme():  # pragma: no cover
    default_scheme = settings.DATABASES["default"]
    if "remrate_ext" in settings.DATABASES:
        remrate_scheme = settings.DATABASES["remrate_ext"]
    else:
        remrate_scheme = default_scheme
    scheme = getattr(settings, "REMRATE_MYSQL_SCHEME", remrate_scheme)
    return scheme


class RemrateUserAccountsManager:
    def __init__(self, connection_scheme=None):
        if not connection_scheme:
            connection_scheme = remrate_db_scheme()
        self.sanitized_scheme = connection_scheme.copy()
        self.sanitized_scheme["PASSWORD"] = "".join(["*" for _x in connection_scheme["PASSWORD"]])
        self.db = MySQLdb.connect(
            host=connection_scheme["HOST"],
            user=connection_scheme["USER"],
            passwd=connection_scheme["PASSWORD"],
            db=connection_scheme["NAME"],
        )
        self.cursor = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def create_new_user(self, username, password):
        try:
            with self.cursor as cursor:
                cursor.execute(
                    """CREATE USER IF NOT EXISTS %(username)s@'%%' IDENTIFIED BY %(password)s""",
                    {"username": username, "password": password},
                )
                cursor.execute(
                    "GRANT ALL PRIVILEGES ON remrate.* TO %(username)s@'%%'", {"username": username}
                )
        except Exception as error:
            log.exception(
                f"Unable to CREATE user {username!r} with {self.sanitized_scheme!r} → {error!r}"
            )
            raise
        else:
            return True

    def update_user_password(self, username, password):
        try:
            with self.cursor as cursor:
                cursor.execute(
                    """ALTER USER IF EXISTS %(username)s@'%%' IDENTIFIED BY %(newpassword)s""",
                    {"username": username, "newpassword": password},
                )
        except Exception as error:
            log.exception(
                f"Unable to ALTER user {username!r} with {self.sanitized_scheme!r} → {error!r}"
            )
            raise
        else:
            return True

    def delete_user(self, username):
        try:
            with self.cursor as cursor:
                cursor.execute("""DROP USER IF EXISTS %(username)s@'%%'""", {"username": username})
        except Exception as error:
            log.exception(
                f"Unable to DROP user {username!r} with {self.sanitized_scheme!r} → {error!r}"
            )
            raise
        else:
            return True
