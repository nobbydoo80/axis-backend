import logging

from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory

from . import models


__author__ = "Autumn Valenta"
__date__ = "08/10/18 2:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


def get_discoverer(discoverer=None):
    """
    Ensures discoverer is an instantiated version of its class.  If discoverer is None, then the
    DefaultDiscoverer is obtained.
    """
    from .discover import DefaultDiscoverer

    if discoverer is None:
        discoverer = DefaultDiscoverer

    if callable(discoverer):
        discoverer = discoverer()

    return discoverer


def realize(proto_obj, form_class=None, **form_kwargs):
    """
    Saves proto_obj's data in a form were proto_obj's selected object is the instance.  If the
    selected object is None, then the form is expected to create a new object from the data.
    """
    selected_id = proto_obj.selected_object_id
    selected_obj = proto_obj.content_type.model.objects.filter(id=selected_id).first()

    if form_class is None:
        form_class = modelform_factory(proto_obj.content_type.model, fields=proto_obj.data.keys())

    form_kwargs.setdefault("user", proto_obj.owner)
    form = form_class(proto_obj.data, instance=selected_obj, **form_kwargs)

    if form.is_valid():
        obj = form.save()
    else:
        obj = None
        proto_obj.assign_error(repr(form.errors))

    return obj


def identify_merges(instance=None, queryset=None):
    """ """
    if not any([instance, queryset]):
        raise ValueError("Please provide one of 'instance' or 'queryset'.")
    if instance:
        model = instance.__class__
        object_list = [instance]
    else:
        model = queryset.model
        object_list = queryset

    search_queryset = model.objects.all()
    return identify_merges_for_object_list(object_list, search_queryset=search_queryset)


def identify_merges_for_instance(instance, search_queryset, discoverer=None, **kwargs):
    """
    Identify other existing instances which might be duplicates of this one.
    """
    discoverer = get_discoverer(discoverer)

    # Create Candidate references
    proto_obj = discoverer.get_proto_object(instance)
    discoverer.discover(proto_obj, queryset=search_queryset, **kwargs)
    return discoverer


def identify_merges_for_object_list(object_list, search_queryset, discoverer=None):
    discoverer = get_discoverer(discoverer)

    for master_obj in object_list:
        identify_merges_for_instance(master_obj, search_queryset, discoverer=discoverer)

    return discoverer


def consolidate_merge_paths(master_instance, erroneous_instance, discoverer=None):
    """
    Adds a ProtoObject with data from erroneous_instance and points it to master_instance.
    Note that the erroneous_instance continues to exist, but stripped of its ProtoObject resolution
    pathways.
    """

    model = erroneous_instance.__class__
    content_type = ContentType.objects.get_for_model(model)

    discoverer = get_discoverer(discoverer)

    # Ensure at least one obvious pathway exists
    _ = discoverer.get_proto_object(erroneous_instance)

    # Get known resolution pathways for the erroneous instance
    alternate_pathways = models.ProtoObject.objects.filter(
        **{
            "content_type": content_type,
            "object_id": erroneous_instance.id,
        }
    )

    # Point all known pathways to the master instance
    alternate_pathways.update(object_id=master_instance.id)
