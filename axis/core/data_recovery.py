"""data_recovery.py: Django core"""


import argparse
import logging
import os

from collections import defaultdict

import sys

import django
from django.contrib.admin.utils import NestedObjects
from django.db import IntegrityError
from django.db import router
from django.db import transaction
from django.db.models import QuerySet
from django.db.models.signals import (
    pre_init,
    post_init,
    post_save,
    pre_save,
    pre_delete,
    post_delete,
    post_migrate,
    pre_migrate,
)

__author__ = "Steven Klass"
__date__ = "1/28/17 08:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# In times of trouble this will help you out.
# 1.  Spin up a backup copy of the your database where you know your data lived.
# 2.  Add you settings.
# 2.  Add the read/write router to your ROUTERS

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'axis',
        'USER': env('MARIADB_USER') or env('MYSQL_ROOT_USER'),
        'PASSWORD': env('MARIADB_ROOT_PASSWORD') or env('MYSQL_ROOT_PASSWORD'),
        'HOST': 'production.cssjd9qk9ffi.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        # 'OPTIONS': {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'}
    },
    'recovery': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'axis',
        'USER': env('MARIADB_USER') or env('MYSQL_ROOT_USER'),
        'PASSWORD': env('MARIADB_ROOT_PASSWORD') or env('MYSQL_ROOT_PASSWORD'),
        'HOST': 'production-20170113-0110-utc-7.cssjd9qk9ffi.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        # 'OPTIONS': {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'}
    }
}

DATABASE_ROUTERS = ['axis.core.data_recovery.RecoveryRouter',
                    'axis.aec_remrate.routers.RemrateRouter',
                    'axis.customer_neea.routers.NEEARouter' ]


"""


class RecoveryRouter(object):
    """A recovery router - This allows reads from one Db to be written to another db."""

    outside_dbs = ["aec_remrate", "customer_neea"]

    def db_for_read(self, model, **hints):
        """All of our reads come from the recoved database."""
        if model._meta.app_label not in self.outside_dbs:
            return "recovery"
        return None

    def db_for_write(self, model, **hints):
        """All of our writes go to the default database."""
        if model._meta.app_label not in self.outside_dbs:
            return "default"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True


class DisableSignals(object):
    def __init__(self, disabled_signals=None):
        self.stashed_signals = defaultdict(list)
        self.disabled_signals = disabled_signals or [
            pre_init,
            post_init,
            pre_save,
            post_save,
            pre_delete,
            post_delete,
            pre_migrate,
            post_migrate,
        ]

    def __enter__(self):
        for signal in self.disabled_signals:
            self.disconnect(signal)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for signal in self.stashed_signals.keys():
            log.info("Re-connecting {}".format(signal))
            self.reconnect(signal)

    def disconnect(self, signal):
        self.stashed_signals[signal] = signal.receivers
        signal.receivers = []

    def reconnect(self, signal):
        signal.receivers = self.stashed_signals.get(signal, [])
        del self.stashed_signals[signal]


class DataRecovery(object):
    def __init__(self, objects):
        self.objects = objects

    def flatten(self, root):
        if isinstance(root, (list, tuple)):
            for element in root:
                for e in self.flatten(element):
                    yield e
        else:
            yield root

    def collect_nested_objects(self, objects):
        """
        Takes a model instance (or list/QuerySet of instances) and recursively lists its dependent
        objects in the database.
        """
        if not isinstance(objects, (list, tuple, QuerySet)):
            objects = [objects]

        _router = router.db_for_read(objects[0])
        log.debug("Looking up {} {} from {}".format(len(objects), objects[0], _router))
        collector = NestedObjects(using=_router)
        collector.collect(objects)

        def format_callback(obj):
            return obj

        _values = collector.nested(format_callback)
        values = list(self.flatten(_values))

        log.debug(
            "Identified {} objects associated to {} incoming objects".format(
                len(values), len(objects)
            )
        )
        return values

    def get_parent_model_data(self, objects=None):
        """This will get any parents for inherited models."""
        objects = objects if objects else self.objects
        data = []
        for obj in objects:
            for model_object, field in obj._meta.parents.items():
                parent = getattr(obj, field.name)
                if parent:
                    data.append(parent)
        log.debug("Identified {} parent class data".format(len(data)))
        return data

    def get_parents(self, objects=None):
        objects = objects if objects else self.objects
        data = []
        for obj in objects:
            for field in obj._meta.fields:
                if field.__class__.__name__ == "ForeignKey":
                    fk = getattr(obj, field.name)
                    if fk:
                        data.append(fk)
                        data += self.get_parents([fk])
        data = list(self.flatten(data))
        return data

    def identify_keep_data(self, item, model_names=None):
        associated_children = self.collect_nested_objects([item])
        parent_model_data = self.get_parent_model_data([item])
        parents = self.get_parents([item])
        log.debug("Identified {} parent items which need to be saved".format(len(parents)))

        order = [
            "group",
            "metro",
            "climatezone",
            "county",
            "city",
            "geocode",
            "geocoderesponse",
            "place",
            "company",
            "builderorganization",
            "utilityorganization",
            "eeporganization",
            "raterorganization",
            "providerorganization",
            "hvacorganization",
            "qaorganization",
            "generalorganization",
            "company_counties",
            "user",
            "eep_program",
            "customerdocument",
            "community",
            "subdivision",
            "eepprogramsubdivisionstatus",
            "home",
            "floorplan",
            "eepprogramhomestatus",
            "eepprogramhomestatusstatelog",
            "eepprogramhomestatusassociation",
            "eepprogramhomestatus_floorplans",
            "constructionstatus",
            "annotation",
            "answer",
            "qaanswer",
            "relationship",
            "utilitysettings",
            "qarequirement",
            "qastatus",
            "qastatusstatelog",
            "qanote",
            "observation",
            "observationtype",
            "incentivepaymentstatus",
            "incentivepaymentstatusstatelog",
            "apshome",
            "etoaccount",
            "fasttracksubmission",
        ]

        data = {}
        for item in list(set(associated_children + parent_model_data + parents)):
            label = item._meta.model_name
            if model_names and label not in model_names:
                continue
            if label not in data:
                data[label] = []
            data[label].append(item)

        assert set(data.keys()).issubset(set(order)), "Missing keys from order - {}".format(
            set(data.keys()) - set(order)
        )

        results = []
        for key in order:
            results += data.get(key, [])

        return results

    def recover(self, model_names=None):
        total = 0
        unrecovered_saves = []
        with DisableSignals():
            for idx, item in enumerate(self.objects, start=1):
                to_be_saved = (
                    self.identify_keep_data(item, model_names=model_names) + unrecovered_saves[:]
                )
                log.info(
                    "{}/{} Working on {} objects attached to {}".format(
                        idx, len(self.objects), len(to_be_saved), item
                    )
                )

                # for sub_object in to_be_saved:
                #     log.debug("Collecting child {} - {}".format(sub_object._meta.model_name, sub_object))
                with transaction.atomic():
                    for sub_object in to_be_saved:
                        new_kwargs = dict(
                            [
                                (fld.name, getattr(sub_object, fld.name))
                                for fld in sub_object._meta.fields
                                if fld.name != sub_object._meta.pk
                            ]
                        )
                        try:
                            x, c = sub_object._meta.model.objects.get_or_create(
                                pk=sub_object.pk, defaults=new_kwargs
                            )
                            total += 1
                        except IntegrityError:
                            if sub_object not in unrecovered_saves:
                                log.warning("Adding item {} to recovered_saves".format(sub_object))
                                unrecovered_saves.append(sub_object)
                        else:
                            log.debug(
                                "{} child {} ({}) ({}) - {}".format(
                                    "Created" if c else "Using",
                                    sub_object._meta.model_name,
                                    sub_object.pk,
                                    x.pk,
                                    x,
                                )
                            )
                            if sub_object in unrecovered_saves:
                                log.info("Removing recovered item {}".format(sub_object))
                                unrecovered_saves.pop(unrecovered_saves.index(sub_object))

        if len(unrecovered_saves):
            log.error("Unable to recover the following elements:")
            errors = []
            for i in unrecovered_saves:
                errors.append((i._meta.model_name, i.pk))
                print(i._meta.model_name, i.pk)
            print(errors)

        print(
            "Completed restore of {} fanned out to {} items".format(len(list(self.objects)), total)
        )


def main(args):
    """Main - $<description>$"""
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(filename)s] (%(name)s) %(message)s",
    )

    args.verbose = 4 if args.verbose > 4 else args.verbose
    loglevel = 50 - args.verbose * 10
    log.setLevel(loglevel)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", args.settings)

    from django.apps import apps as django_app

    if not django_app.apps_ready:
        import django

        django.setup()
    company_ids = []
    from axis.company.models import Company

    objects = list(
        Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE)
        .objects.filter(id__in=company_ids)
        .order_by("id")
    )[453:]

    data = DataRecovery(objects)
    data.recover(model_names=["relationship"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="$<description>$")
    parser.add_argument(
        "-v",
        dest="verbose",
        help="How verbose of the output",
        action="append_const",
        const=1,
        default=[1, 2, 3],
    )
    parser.add_argument("-y", dest="settings", help="Django Settings", action="store")
    parser.add_argument("-n", dest="dry_run", help="Dry Run", action="store_true")
    sys.exit(main(parser.parse_args()))
