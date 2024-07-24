__author__ = "Michael Jeffrey"
__date__ = "4/22/16 6:01 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

import argparse
import logging
import operator
import os
import re
import sys
from collections import defaultdict

from django.apps import apps
from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import router
from django.db import transaction
from django.db.models import Model, OneToOneField
from django.db.models import QuerySet
from django.db.models.signals import (
    pre_init,
    post_init,
    pre_save,
    post_save,
    pre_delete,
    post_delete,
    m2m_changed,
    pre_migrate,
    post_migrate,
)

# from axis.company.managers import CompanyQueryset
from infrastructure.utils import get_user_input

log = logging.getLogger(__name__)


# Given a label we will only consider the following fields when
# determining to delete or edit.  Basically these are the unique keys.
MERGE_FIELDS = {
    "builderorganization.company_ptr": {"fields": ["company_ptr"]},
    "raterorganization.company_ptr": {"fields": ["company_ptr"]},
    "providerorganization.company_ptr": {"fields": ["company_ptr"]},
    "hvacorganization.company_ptr": {"fields": ["company_ptr"]},
    "qaorganization.company_ptr": {"fields": ["company_ptr"]},
    "eeporganization.company_ptr": {"fields": ["company_ptr"]},
    "generalorganization.company_ptr": {"fields": ["company_ptr"]},
    "relationship.company": {"fields": ["content_type", "object_id"]},
    "relationship.content_object": {"fields": ["company"]},
    "raterorganization.rater_organization": {"fields": ["rater_organization"]},
    "builderorganization.builder_organization": {"fields": ["builder_organization"]},
    "company.company": {
        "fields": [
            "company",
        ]
    },
    "company.builder_organization": {"fields": ["builder_organization"]},
}


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
            m2m_changed,
            pre_migrate,
            post_migrate,
        ]

    def __enter__(self):
        for signal in self.disabled_signals:
            log.debug("Disconnecting {}".format(signal))
            self.disconnect(signal)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for signal in list(self.stashed_signals.keys()):
            log.debug("Re-connecting {}".format(signal))
            self.reconnect(signal)

    def disconnect(self, signal):
        self.stashed_signals[signal] = signal.receivers
        signal.receivers = []

    def reconnect(self, signal):
        signal.receivers = self.stashed_signals.get(signal, [])
        del self.stashed_signals[signal]


class DeleteCollectorMixin(object):
    def flatten(self, root):
        if isinstance(root, (list, tuple)):
            for element in root:
                for e in self.flatten(element):
                    yield e
        else:
            yield root

    def collect_nested_objects(self, objects, flatten=True, callback=None):
        """
        Takes a model instance (or list/QuerySet of instances) and recursively lists its dependent
        objects in the database.


        This will recursively get a list of objects which are bound to an entity.
        """

        if not isinstance(objects, (list, tuple, QuerySet)):
            objects = [objects]

        # log.debug("Looking up {} {} from {}".format(len(objects), objects[0], self.router))
        collector = NestedObjects(using=router.db_for_read(objects[0]))
        collector.collect(objects)

        def format_callback(obj):
            return obj

        _values = collector.nested(callback or format_callback)
        values = list(filter(None, list(self.flatten(_values))))

        # log.debug("Identified {} objects associated to {} incoming objects".format(len(values), len(objects)))

        if not flatten:
            return _values, len(values)
        return values

    def pretty_name(self, obj):
        return f"{obj._meta.app_label}.{obj.__class__.__name__} ({obj.pk}) - {obj}"

    def delete(self, object, prompt=True, error_on=None, allowed_objects=None):  # noqa: C901
        """This will look at an object and only safely delete it."""

        def delete_format_callback(obj):
            return self.pretty_name(obj)

        children, total = self.collect_nested_objects(
            object, flatten=False, callback=delete_format_callback
        )

        if error_on:
            prompt = False
            if total > error_on:
                prompt = True

        def flatten(aList):
            t = []
            for i in aList:
                if not isinstance(i, list):
                    t.append(i)
                else:
                    t.extend(flatten(i))
            return t

        if allowed_objects:
            if not isinstance(allowed_objects, list):
                allowed_objects = [list]
            prompt = False
            for item in flatten(children):
                label = item.split(" ")[0]
                if label not in allowed_objects:
                    prompt = True
                    break

        def print_results(objects, indent=0):
            if isinstance(objects, (list, tuple)):
                for item in objects:
                    print_results(item, indent=indent + 4)
            else:
                try:
                    print("{} • {}".format(" " * indent, objects))
                except UnicodeEncodeError:
                    print("{} * {}".format(" " * indent, objects))

        if prompt:
            msg = "The following {} items are associated to {} and will be deleted:"
            print(msg.format(total, self.pretty_name(object)))
            print_results(children)
        else:
            log.debug(
                "{} items associated to {} will be deleted".format(total, self.pretty_name(object))
            )

        if prompt:
            text = "Please confirm the deletion of {} items".format(total)
            confirmed = get_user_input(text, choices=("Yes", "No"))
        else:
            confirmed = "Yes"

        if confirmed == "Yes":
            object.delete()
            log.debug("{} Objects have been deleted".format(total))
            if prompt:
                print("{} Objects have been deleted".format(total))
            return


def safe_delete(objects, prompt=True, error_on=None, allowed_objects=None):
    """Given a list of objects this will safely delete objects.

    prompt - (bool) Ask prior to deleting anything
    on_error - (int) only prompt if the number to be deleted is greater than on_error
    """

    if not isinstance(objects, (list, tuple)):
        objects = [objects]
    if isinstance(objects, QuerySet):
        objects = [objects]

    d = DeleteCollectorMixin()
    for object in objects:
        d.delete(object, prompt=prompt, error_on=error_on, allowed_objects=allowed_objects)


class MergeItem(object):
    def __init__(self, **kwargs):
        self.type = kwargs.get("type", "unknown")

        self.model = kwargs.get("model")
        self.pk = kwargs.get("pk")
        self.field_name = kwargs.get("field_name")

        self.label = kwargs.get("label")

        self.primary = kwargs.get("primary")
        self.alternate = kwargs.get("alternate")
        self.one_to_one_model = kwargs.get("one_to_one_model")

        self.is_related = kwargs.get("is_related", False)
        self.is_one_to_one = kwargs.get("is_one_to_one", False)
        self.is_many_to_many = kwargs.get("is_many_to_many", False)
        self.is_local_many_to_many = kwargs.get("is_local_many_to_many", False)
        self.is_generic_foriegn_key = kwargs.get("is_generic_foriegn_key", False)

    def __repr__(self):
        return "<%s Merge Item> %s.%s (%s) [%s]-- %s" % (
            self.type.capitalize(),
            self.model._meta.model.__name__,
            self.field_name,
            self.label,
            self.pk,
            self.model,
        )


class ForeignKeyRelationships(DeleteCollectorMixin):
    def __init__(self, primary, alternate, **kwargs):
        self.primary = primary
        self.alternate = alternate

        if self.primary._meta.model_name == "company":
            self.skip_company_ptr = kwargs.get("skip_company_ptr", True)

        self.objects = []

    def set_order(self, model_names=None):
        order = [
            "group",
            "contenttype",
            "metro",
            "climatezone",
            "county",
            "country",
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
            "companydocument",
            "altname",
            "sponsorpreferences",
            "hirlbuilderorganization",
            "hirlcompanyclient",
            "user",
            "eepprogram",
            "builderagreement",
            "customerdocument",
            "asynchronousprocesseddocument",
            "community",
            "subdivision",
            "eepprogramsubdivisionstatus",
            "remrateuser",
            "datatracker",
            "simulation",
            "building",
            "home",
            "floorplan",
            "eepprogramhomestatus",
            "eepprogramhomestatusstatelog",
            "eepprogramhomestatusassociation",
            "eepprogramhomestatus_floorplans",
            "constructionstatus",
            "homedocument",
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
            "incentivedistribution",
            "etoaccount",
            "fasttracksubmission",
            "samplingproviderapproval",
            "apshome",
            "epaaxiscompany",
            "resnetcompany",
            "metric",
            "legacyapsbuilder",
            "hirlraterorganization",
            "project",
            "recentlyviewed",
            "contactcard",
            "location",
            "hirlprojectregistration",
            "companyaccess",
        ]

        data = {}
        for item in list(set(self.objects)):
            model_name = item.model._meta.model_name
            if model_names and model_name not in model_names:
                continue
            if model_name not in data:
                data[model_name] = []
            # You need to ensure that you only have one per model or it will nuke it..
            if item.pk not in [x.pk for x in data[model_name]]:
                data[model_name].append(item)

        err = "Missing keys from order - {}"
        assert set(data.keys()).issubset(set(order)), err.format(set(data.keys()) - set(order))
        results = []
        for key in order:
            results += data.get(key, [])
        self.objects = results

    def collect(self, model, related_one_to_one=None):
        model = model if model else self.alternate
        log.debug("Collecting related objects to {} ({})".format(model, model.id))

        one_to_one_model = model if related_one_to_one is True else None

        related = [
            f
            for f in model._meta.get_fields()
            if (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete
        ]

        for related_object in related:
            # The variable name on teh alias_object model.
            alias_varname = related_object.get_accessor_name()
            # The variable name on the related_model
            obj_varname = related_object.field.name

            try:
                related_objects = getattr(model, alias_varname)
            except Exception as err:
                log.debug("Determined {}".format(err))
                if "RelatedObjectDoesNotExist" not in "{}".format(err.__class__):
                    raise
            else:
                if isinstance(related_object.field, OneToOneField):
                    if self.skip_company_ptr and related_object.field.name == "company_ptr":
                        log.debug(
                            "Looking up anything relating to one-to-one {}".format(related_objects)
                        )
                        if related_one_to_one is None:
                            self.collect(related_objects, related_one_to_one=True)
                    else:
                        label = "{}.{}".format(
                            related_object.model._meta.model_name, related_object.field.name
                        )
                        merge_item = MergeItem(
                            type="related",
                            model=related_objects,
                            pk=related_objects.pk,
                            field_name=related_object.field.name,
                            label=label,
                            primary=self.primary,
                            alternate=model,
                            one_to_one_model=one_to_one_model,
                            is_related=True,
                            is_one_to_one=True,
                        )
                        self.objects.append(merge_item)
                else:
                    for obj in related_objects.all():
                        label = "{}.{}".format(obj._meta.model_name, obj_varname)
                        merge_item = MergeItem(
                            type="related",
                            model=obj,
                            pk=obj.pk,
                            field_name=obj_varname,
                            label=label,
                            primary=self.primary,
                            alternate=model,
                            one_to_one_model=one_to_one_model,
                            is_related=True,
                        )
                        self.objects.append(merge_item)
        if len(self.objects):
            log.info("{} related objects have been found".format(len(self.objects)))
        return self.objects

    def get_one_to_one_related(self, item):
        if not item.one_to_one_model:
            return item.primary
        return item.one_to_one_model._meta.model.objects.get(id=item.primary.id)

    def should_delete(self, item):
        fields = {
            f.name: getattr(item.model, f.name)
            for f in item.model._meta.fields
            if f != item.model._meta.pk
        }
        if item.label in MERGE_FIELDS:
            fields = {k: fields.get(k) for k in MERGE_FIELDS[item.label]["fields"]}
        fields[item.field_name] = (
            self.get_one_to_one_related(item) if item.one_to_one_model else item.primary
        )
        return item.model._meta.model.objects.filter(**fields).count()

    def merge(self, dry_run=True):
        self.set_order()
        if len(self.objects):
            log.debug(
                "Merging {} Related objects {} ({})".format(
                    len(self.objects), self.objects[0].primary, self.objects[0].primary.id
                )
            )

        for item in self.objects:
            ModelObject = item.model
            if self.should_delete(item):
                if not dry_run:
                    self.delete(ModelObject, prompt=False)
                log.debug("Deleted {}".format(item))
            else:
                if not dry_run:
                    target = (
                        self.get_one_to_one_related(item) if item.one_to_one_model else item.primary
                    )
                    setattr(ModelObject, item.field_name, target)

                    msg = "Setting Related {} ({}) {} > {} ({})"
                    log.debug(
                        msg.format(ModelObject, ModelObject.pk, item.field_name, target, target.pk)
                    )

                    # Call the parent save and skip anything we may have done.
                    try:
                        super(type(ModelObject), ModelObject).save()
                    except IntegrityError:
                        print(
                            "You will need to add a label to MERGE_FIELDS for {}".format(item.label)
                        )
                        raise
                log.debug("Edit {}".format(item))


class ManyToManyRelationships(ForeignKeyRelationships):
    def collect(self, model=None):
        model = model if model else self.alternate
        log.debug("Collecting many to many objects to {} ({})".format(model, model.id))

        related_m2m = [
            f
            for f in model._meta.get_fields(include_hidden=True)
            if f.many_to_many and f.auto_created
        ]

        for related_many_object in related_m2m:
            alias_varname = related_many_object.get_accessor_name()
            obj_varname = related_many_object.field.name

            if alias_varname is not None:
                # standard case
                related_many_objects = getattr(model, alias_varname).all()
            else:
                # special case, symmetrical relation, no reverse accessor
                related_many_objects = getattr(model, obj_varname).all()

            for obj in related_many_objects.filter(**{obj_varname: model}):
                label = "{}.{}".format(model._meta.model_name, obj_varname)
                merge_item = MergeItem(
                    type="M2M",
                    model=obj,
                    pk=obj.pk,
                    field_name=obj_varname,
                    label=label,
                    primary=self.primary,
                    alternate=model,
                    is_many_to_many=True,
                )
                log.debug("Adding {}".format(merge_item))
                self.objects.append(merge_item)
        if len(self.objects):
            log.info("{} M2M objects have been found".format(len(self.objects)))

    def _get_through_concrete_model(self, through_model, item):
        kwargs, target_field = {}, None
        for field in through_model._meta.fields:
            if field == through_model._meta.pk:
                continue
            elif field.related_model == item.model._meta.model:
                kwargs[field.name] = item.model
            elif field.related_model == item.primary._meta.model:
                kwargs[field.name] = item.alternate
                target_field = field.name
        try:
            return through_model.objects.get(**kwargs)
        except ObjectDoesNotExist as err:
            log.debug(
                "Unable to find {} with kwargs of {} - {}".format(
                    through_model._meta.model_name,
                    {"{}_id".format(k): v.id for k, v in kwargs.items()},
                    err,
                )
            )
            print(through_model, item, target_field)
            if target_field:  # target_field can be None sometimes, unclear why
                kwargs[target_field] = item.primary
            if through_model.objects.filter(**kwargs).count():
                log.info("Item has already been transitioned")
                raise KeyError("{} was already transitioned".format(item))

            raise

    def should_delete(self, item):
        thu_model = self._get_through_concrete_model(
            getattr(item.model, item.field_name).through, item
        )
        kwargs = {
            f.name: getattr(thu_model, f.name)
            for f in thu_model._meta.fields
            if f != thu_model._meta.pk
        }

        if item.label in MERGE_FIELDS:
            kwargs = {k: kwargs.get(k) for k in MERGE_FIELDS[item.label]["fields"]}

        for k, v in kwargs.items():
            try:
                if v._meta.model == self.primary._meta.model:
                    kwargs[k] = self.primary
            except AttributeError:
                pass
        return thu_model._meta.model.objects.filter(**kwargs).count()

    def merge(self, dry_run=True):
        self.set_order()
        if len(self.objects):
            log.debug(
                "Merging {} Many to Many objects {} ({})".format(
                    len(self.objects), self.objects[0].primary, self.objects[0].primary.id
                )
            )
        for item in self.objects:
            ModelObject = getattr(item.model, item.field_name)
            try:
                delete = self.should_delete(item)
            except KeyError:
                # This is for when the item has already been transitioned.
                pass
            else:
                if delete:
                    if not dry_run:
                        log.debug(
                            "Removing {} to {} as it already exists for {}".format(
                                item.model, item.label, item.primary
                            )
                        )
                        ModelObject.remove(item.alternate)
                    log.debug("Delete {}".format(item))
                else:
                    if not dry_run:
                        log.debug(
                            "Adding {} to {} for {}".format(item.model, item.label, item.primary)
                        )
                        ModelObject.add(item.primary)
                        log.debug(
                            "Removing {} to {} for {}".format(
                                item.model, item.label, item.alternate
                            )
                        )
                        ModelObject.remove(item.alternate)
                    log.debug("Edit {}".format(item))


class ManyToManyLocalRelationships(ManyToManyRelationships):
    def collect(self, model=None):
        model = model if model else self.alternate
        log.debug("Collecting many to many local objects to {} ({})".format(model, model.id))
        for field in model._meta.local_many_to_many:
            for obj in getattr(model, field.attname).all():
                label = "{}.{}".format(model._meta.model_name, field.attname)
                merge_item = MergeItem(
                    type="Local M2M",
                    model=obj,
                    pk=obj.pk,
                    field_name=field.attname,
                    label=label,
                    primary=self.primary,
                    alternate=model,
                    is_many_to_many=True,
                    is_local_many_to_many=True,
                )
                log.debug("Adding {}".format(merge_item))
                self.objects.append(merge_item)

        if len(self.objects):
            log.info("{} Local M2M objects have been found".format(len(self.objects)))

    def should_delete(self, item):
        thu_model = self._get_through_concrete_model(
            getattr(item.primary, item.field_name).through, item
        )
        kwargs = {
            f.name: getattr(thu_model, f.name)
            for f in thu_model._meta.fields
            if f != thu_model._meta.pk
        }

        if item.label in MERGE_FIELDS:
            kwargs = {k: kwargs.get(k) for k in MERGE_FIELDS[item.label]["fields"]}

        for k, v in kwargs.items():
            try:
                if v._meta.model == self.primary._meta.model:
                    kwargs[k] = self.primary
            except AttributeError:
                pass
        return thu_model._meta.model.objects.filter(**kwargs).count()

    def merge(self, dry_run=True):
        self.set_order()
        if len(self.objects):
            log.debug(
                "Merging {} Local Many to Many objects {} ({})".format(
                    len(self.objects), self.objects[0].primary, self.objects[0].primary.id
                )
            )
        for item in self.objects:
            if self.should_delete(item):
                if not dry_run:
                    getattr(item.alternate, item.field_name).remove(item.model)
                log.debug("Delete {}".format(item))
            else:
                if not dry_run:
                    getattr(item.primary, item.field_name).add(item.model)
                    getattr(item.alternate, item.field_name).remove(item.model)
                log.debug("Edit {}".format(item))


class GenericForeignKeyRelationships(ForeignKeyRelationships):
    def get_child_models(self, model):
        objects = []

        related = [
            f
            for f in model._meta.get_fields()
            if (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete
        ]

        for related_object in related:
            alias_varname = related_object.get_accessor_name()
            try:
                related_objects = getattr(model, alias_varname)
            except Exception as err:
                if "RelatedObjectDoesNotExist" not in "{}".format(err.__class__):
                    raise
            else:
                if isinstance(related_object.field, OneToOneField):
                    objects.append(related_objects)
        return objects

    def collect(self, model=None):
        model = model if model else self.alternate
        models = self.get_child_models(model) + [model]
        ct = ContentType.objects.get_for_models(*models).values()
        try:
            log.debug(
                "Collecting generic foreign objects to {} ({})".format(
                    models, [x.pk for x in models]
                )
            )
        except UnicodeDecodeError:
            pass
        for model_obj in apps.get_models():
            for field_name, field in filter(
                lambda x: isinstance(x[1], GenericForeignKey), model_obj.__dict__.items()
            ):
                kwargs = {"{}__in".format(field.ct_field): ct, field.fk_field: model.pk}
                for obj in model_obj.objects.filter(**kwargs):
                    label = "{}.{}".format(model_obj._meta.model_name, field_name)
                    merge_item = MergeItem(
                        type="Generic FK",
                        model=obj,
                        pk=obj.pk,
                        field_name=field.fk_field,
                        label=label,
                        primary=self.primary,
                        alternate=model,
                        is_generic_foriegn_key=True,
                    )
                    log.debug("Adding {}".format(merge_item))
                    self.objects.append(merge_item)
        if len(self.objects):
            log.info("{} Generic Foreign Key objects have been found".format(len(self.objects)))

    def should_delete(self, item):
        fields = {
            f.name: getattr(item.model, f.name)
            for f in item.model._meta.fields
            if f != item.model._meta.pk
        }
        if item.label in MERGE_FIELDS:
            fields = {k: fields.get(k) for k in MERGE_FIELDS[item.label]["fields"]}
        fields[item.field_name] = item.primary.id
        return item.model._meta.model.objects.filter(**fields).count()

    def merge(self, dry_run=True):
        self.set_order()
        if len(self.objects):
            log.debug(
                "Merging {} Generic Foreign Key objects {} ({})".format(
                    len(self.objects), self.objects[0].primary, self.objects[0].primary.id
                )
            )
        for item in self.objects:
            ModelObject = item.model
            if self.should_delete(item):
                if not dry_run:
                    self.delete(ModelObject, error_on=2)
                log.debug("Delete {}".format(item))
            else:
                if not dry_run:
                    setattr(ModelObject, item.field_name, item.primary.id)
                    # Call the parent save and skip anything we may have done.
                    super(type(ModelObject), ModelObject).save()
                log.debug("Edit {}".format(item))


class MergeObjects(DeleteCollectorMixin):
    def __init__(self, primary, alternates):
        if not isinstance(alternates, (list, tuple)):
            alternates = [alternates]
        if isinstance(alternates, QuerySet):
            alternates = [alternates]

        for alt in alternates:
            same_model = alt._meta.model == primary._meta.model
            same_app = alt._meta.app_label == primary._meta.app_label

            if not same_model or not same_app:
                raise TypeError("You must use the same model - {} != {}".format(primary, alt))
            if alt.id == primary.id:
                raise AttributeError("You can't reassign the same object to itself")

        if (
            primary._meta.model_name.endswith("organization")
            and primary._meta.app_label == "company"
        ):
            log.warning("Autoshifting Organization to parent Company Model")
            Organization = apps.get_model("company", "company")
            primary = Organization.objects.get(id=primary.id)
            alternates = Organization.objects.filter(
                id__in=map(operator.attrgetter("id"), alternates)
            )

        if not issubclass(primary._meta.model, Model):
            raise TypeError("Only django.db.models.Model subclasses can be merged")

        parents = primary._meta.get_parent_list()
        parents = parents if parents else [primary]
        if parents != [primary]:
            raise TypeError("{} has a parent class {} - please use that!".format(primary, parents))

        self.primary = primary
        self.alternates = alternates
        try:
            log.debug("Primary = {} ({})".format(self.primary, self.primary.id))
            log.debug(
                "Alternates = {} ({})".format(self.alternates, [x.id for x in self.alternates])
            )
        except UnicodeDecodeError:
            pass

    def __enter__(self):
        from axis.geographic.placedmodels import PlaceSynchronizationMixin

        setattr(PlaceSynchronizationMixin, "OLD_SAVE", getattr(PlaceSynchronizationMixin, "save"))
        delattr(PlaceSynchronizationMixin, "save")

    def __exit__(self, exc_type, exc_val, exc_tb):
        from axis.geographic.placedmodels import PlaceSynchronizationMixin

        setattr(PlaceSynchronizationMixin, "save", getattr(PlaceSynchronizationMixin, "OLD_SAVE"))
        delattr(PlaceSynchronizationMixin, "OLD_SAVE")

    def get_fields_to_update(self, model):
        data = {}
        for field in self.primary._meta.fields:
            if field.__class__.__name__ in ["AutoField"]:
                continue
            primary_value = getattr(self.primary, field.name)
            if primary_value in ["", None]:
                update_value = getattr(model, field.name)
                if update_value not in ["", None]:
                    data[field.name] = update_value
        return data

    def merge(self, dry_run=False, prompt=True, delete_alternates=True):
        with DisableSignals():
            total = 0
            for alternate in self.alternates:
                related = ForeignKeyRelationships(self.primary, alternate)
                related.collect(alternate)
                total += len(related.objects)

                local_many_to_many = ManyToManyLocalRelationships(self.primary, alternate)
                local_many_to_many.collect(alternate)
                total += len(local_many_to_many.objects)

                many_to_many = ManyToManyRelationships(self.primary, alternate)
                many_to_many.collect(alternate)
                total += len(many_to_many.objects)

                generic_foreign_keys = GenericForeignKeyRelationships(self.primary, alternate)
                generic_foreign_keys.collect(alternate)
                total += len(generic_foreign_keys.objects)

                log.info(
                    "Transitioning {} objects from {} ({}) to {} ({})".format(
                        total, alternate, alternate.id, self.primary, self.primary.id
                    )
                )

                # THE BUG IS WE ARE DELETING THE WRONG ONE...
                for object_type in [
                    related,
                    local_many_to_many,
                    many_to_many,
                    generic_foreign_keys,
                ]:
                    with transaction.atomic():
                        object_type.merge(dry_run=dry_run)

                with transaction.atomic():
                    kwargs = self.get_fields_to_update(alternate)
                    for k, v in kwargs.items():
                        setattr(self.primary, k, v)
                    if kwargs:
                        super(type(self.primary), self.primary).save()

                    if dry_run:
                        log.debug("Deleting {}".format(alternate))
                    else:
                        total += 1
                        if delete_alternates:
                            self.delete(alternate, prompt=prompt)

            if prompt:
                print(
                    "\n{} Objects {}have been merged to {}\n".format(
                        total, "would " if dry_run else "", self.primary
                    )
                )


def merge_model_objects(primary, alternates, prompt=True, dry_run=False):
    merge = MergeObjects(primary=primary, alternates=alternates)
    merge.merge(dry_run=dry_run, prompt=prompt)


def translate_non_alphanumerics(to_translate, translate_to="_"):
    not_letters_or_digits = "!\"#%'()*+,-./:;<=>?@[]^_`{|}\\~"
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table).lower()


def duplicate_city_finder():
    cities = {}
    from axis.geographic.models import City

    for _id, name, cid, state in City.objects.all().values_list(
        "id", "name", "county_id", "county__state"
    ):
        name = translate_non_alphanumerics(translate_non_alphanumerics(name))
        if name.endswith(" {}".format(state.lower())):
            pre = name
            name = re.sub(r"\s+{}".format(state.lower()), "", name)
            print("Fix: {} ({})  -> {}".format(pre, _id, name))

        label = (name, cid, state)
        if label not in cities:
            cities[label] = []
        cities[label].append(_id)

    for key, values in list(cities.items()):
        if len(values) == 1:
            del cities[key]
            continue
        values.sort()
        cities[key] = values

    if len(cities.keys()):
        print("The following {} will be merged please review".format(len(cities)))
        for co in cities.keys():
            print("  • {} - {}".format(co, cities[co]))

        merge = MergeObjects(City.objects.get(id=cities[co][0]), City.objects.get(id=cities[co][1]))
        confirm = get_user_input("Please confirm this is your intention", choices=("Yes", "No"))
        if confirm == "No":
            return
    else:
        return "No duplicate City found"

    for (name, cid, state), values in cities.items():
        values.sort()
        primary = City.objects.get(id=values[0])
        alternates = City.objects.filter(id__in=values[1:])

        merge = MergeObjects(primary, list(alternates))
        print(
            "The following cities will be merged into {} ({}) of {}".format(
                primary.legal_statistical_area_description, primary.id, state
            )
        )
        for alt in alternates:
            print(f"  • ({alt.id}) {alt} {alt.legal_statistical_area_description}")
        merge.merge(prompt=False)


def duplicate_company_finder(no_merge=False):
    from axis.company.models import Company

    companies = {}
    for company in Company.objects.all():
        key = (translate_non_alphanumerics(company.name), company.state, company.company_type)

        if key not in companies:
            companies[key] = []
        companies[key].append(company.id)

    for company, values in list(companies.items()):
        if len(values) == 1:
            del companies[company]
            continue
        values.sort()
        companies[company] = values

    if no_merge:
        return companies

    if len(companies.keys()):
        print("The following {} will be merged please review".format(len(companies)))
        for co in companies.keys():
            print("  • {} - {}".format(co, companies[co]))

        merge = MergeObjects(
            Company.objects.get(id=companies[co][0]), Company.objects.get(id=companies[co][1])
        )
        confirm = get_user_input("Please confirm this is your intention", choices=("Yes", "No"))
        if confirm == "No":
            return
    else:
        return "No duplicate companies found"

    changed = 0
    for (company, state, co_type), values in companies.items():
        if len(values) == 1:
            continue
        values.sort()
        primary = Company.objects.get(id=values[0])
        alternates = list(Company.objects.filter(id__in=values[1:]))

        merge = MergeObjects(primary, alternates)

        print(
            "The following {} will be merged into {} ({}) of {}".format(
                co_type, primary, primary.id, state
            )
        )
        for alt in alternates:
            print("  • ({}) {}".format(alt.id, alt))

        if len(alternates) > 2:
            confirm = get_user_input("Please confirm this is your intention", choices=("Yes", "No"))
            if confirm == "No":
                continue

        merge.merge(prompt=False)

    print("Merged {} companies".format(changed))


def merge_model(args):
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

    cities = {}
    from axis.geographic.models import City

    for _id, name, cid, state in City.objects.all().values_list(
        "id", "name", "county_id", "county__state"
    ):
        name = translate_non_alphanumerics(name)
        label = (name, cid, state)
        if name.endswith(" {}".format(state.lower())):
            if label not in cities:
                cities[label] = []
            cities[label].append(_id)

    for city in cities:
        print(city)

    # for (name, cid, state), _id in cities.items():
    #     cty = City.objects.get(id=_id[0])
    #     cty.name = re.sub(r"\s+{}".format(state), "", cty.name)
    #     cty.save()


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

    parser.add_argument("-m", dest="model_name", help="Model Name Looking to merge")
    parser.add_argument("--id", dest="primary_id", help="ID of the primary ID")
    parser.add_argument("--alt_id", dest="alt_id", help="ID of the altername")
    parser.add_argument("-D", dest="dry_run", help="Dry Run", action="store_true")

    sys.exit(merge_model(parser.parse_args()))
