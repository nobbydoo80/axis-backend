import sys
import traceback
import logging
import json
import hashlib
from operator import itemgetter

from django.db.models import Q, Model
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict

from unidecode import unidecode

from . import models, merge, normalizers


__author__ = "Autumn Valenta"
__date__ = "08/22/16 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class DefaultDiscoverer(object):
    form_class = None
    profile_field = None
    profile_field_name = None

    # Parameters for customization during the discover() step to prune candidates
    # TODO: Make a chain callable system like the normalizers so arbitrary pruning steps can be
    # specified with ease.  Each of these default customizations represent separate pruning
    # callables.
    profile_threshold = 0
    levenshtein_threshold = 0
    candidate_limit = 10

    # List of callables to turn transform the object instance into a string for fingerprinting and
    # levenshtein distance analysis.
    normalizers = ()

    def get_form_class(self, proto_obj):
        return self.form_class

    def get_queryset(self, proto_obj):
        model = proto_obj.content_type.model_class()
        return model.objects.all()

    def filter_candidate_queryset(self, proto_obj, queryset, profile_threshold=None, **kwargs):
        """
        Returns a filtered queryset of objects that are allowed to qualify as candidates for the
        given proto_obj.
        """
        if self.profile_field:
            data = self.normalize(proto_obj.data)
            profile = self.profile_object(data)
            profile_threshold = profile_threshold or self.profile_threshold
            profile_filter = Q(**{self.profile_field_name: None}) | Q(
                **{
                    self.profile_field_name + "__gte": (profile - profile_threshold),
                    self.profile_field_name + "__lte": (profile + profile_threshold),
                }
            )
            queryset = queryset.filter(profile_filter).exclude(id=proto_obj.object_id)

        return queryset.filter(**kwargs)

    def set_candidates(self, proto_obj, candidate_characteristics):
        """
        Creates candidates from the characteristics dict formatted as a dict of ids to dict of field
        values that should be set on the Candidate.  Note that those characteristics must already
        be represented by fields on the Candidate model with the same name.
        """
        models.Candidate.objects.bulk_create(
            [
                models.Candidate(
                    proto_object=proto_obj, content_type=proto_obj.content_type, **characteristics
                )
                for characteristics in candidate_characteristics.values()
            ]
        )

    # Object inspectors
    def extract_data(self, obj):
        """Reverse engineers the data from obj that should exist on its ProtoObject."""
        return model_to_dict(obj)

    def normalize(self, data):
        """Cleans data to a simpler value for similarity checks."""
        return normalizers.normalize(data, self.normalizers)

    def profile_object(self, normalized_data):
        """Treat ``data`` like a string and create a portable fingerprint for it."""
        # Think of the profile score like a hash, except it changes only by predictable amounts when
        # changes are made to the source string.  Comparing two profile scores doesn't tell you what
        # is different, only by how much.  This is useful for culling lots of results that aren't
        # worth checking levenshtein distances in python.

        # Sum the character values
        profile = sum(map(ord, normalized_data))

        return profile

    def profile_data(self, data):
        """Returns a unique fingerprint for the given data."""
        json_data = json.dumps(data, sort_keys=True, cls=DjangoJSONEncoder)
        profile = hashlib.sha512(json_data).hexdigest()
        return profile

    # MAIN ENTRY
    def do_import(self, proto_obj, **kwargs):
        """
        Takes a ProtoObject as far as it can go toward becoming a full object.  Safe for
        back-to-back calls on the same proto_obj, whether or not the previous import worked.
        """

        # Return object directly if already associated to a final candidate
        if proto_obj.content_object:
            return proto_obj.content_object

        if not self.validate(proto_obj):
            return None

        if proto_obj.selected_object_id is None:
            obj = self.discover(proto_obj, **kwargs)

            if obj is False:
                proto_obj.assign_error("Ambiguous candidates exist.")
            else:
                # obj might be None, indicating a new object would need to be created
                self.select(proto_obj, candidate=obj)

        # Put the proto_obj's data on the pre-selected candidate (or a new object if none exists)
        try:
            obj = self.realize(proto_obj)
        except Exception as e:
            proto_obj.assign_error(
                "{}".format(e), tb="".join(traceback.format_tb(sys.exc_info()[-1]))
            )
            return None
        else:
            return obj

    # Steps of import process
    def validate(self, proto_obj):
        """
        True if the proto_obj data meets business logic expectations.  False aborts all work handled
        in ``do_import()``, including the identification of candidates.
        """
        return True

    def discover(self, proto_obj, queryset=None, watch_ids=[], **kwargs):
        """
        Returns the matching object instance, False if multiple candiates are found, or None if
        there are no matches.  After running this, the ProtoObject's ``candidates_ids`` field will
        be current.

        This method is safe to run back to back if needed.

        Overrides
        """

        # FIXME: This method relies on items in the queryset having an accurate data profile in
        # the ``profile_field_name`` model field.  A missing data profile is fine, but if one is
        # already present, it is trusted.  Therefore, if data profiles were generated without
        # respecting the whole list of ``normalizers`` functions on the given discoverer, blatantly
        # obvious string-compare matches might be missed because they were excluded by the data
        # profile +/- threshold and a different normalization technique.

        # if proto_obj.content_object:
        #     return proto_obj.content_object

        model = proto_obj.content_type.model_class()
        normalized = self.normalize(proto_obj.data)
        profile = self.profile_object(normalized)
        profile_threshold = kwargs.get("profile_threshold", self.profile_threshold)
        levenshtein_threshold = kwargs.get("levenshtein_threshold", self.levenshtein_threshold)
        candidate_limit = kwargs.get("candidate_limit", self.candidate_limit)

        # Clear existing
        proto_obj.candidate_set.all().delete()

        # Get queryset
        if queryset is None:
            queryset = self.get_queryset(proto_obj)

        similar = self.filter_candidate_queryset(proto_obj, queryset, **kwargs)

        if watch_ids:
            log.error(similar.filter(id__in=watch_ids))

        # Check for an obvious direct match
        # TODO: Implement the queue of pruning callables here instead, with these behaviors set as
        # our default.
        if self.profile_field:
            log.debug("Scanning multiple candidates for obvious matches...")

            matches = []
            likely_matches = similar.filter(**{self.profile_field_name: profile})
            for obj in likely_matches:
                candidate_normalized = self.normalize(
                    {
                        self.profile_field: getattr(obj, self.profile_field),
                    }
                )
                if normalized == candidate_normalized:
                    matches.append(obj)

            if watch_ids:
                log.error([m for m in matches if m.id in watch_ids])

            if len(matches) == 1:
                obj = matches[0]
                candidate_normalized = self.normalize(
                    {self.profile_field: getattr(obj, self.profile_field)}
                )
                candidate_profile = self.profile_object(candidate_normalized)
                self.set_candidates(
                    proto_obj,
                    {
                        obj.id: {
                            "object_id": obj.id,
                            "levenshtein_distance": get_levenshtein_distance(
                                candidate_normalized, normalized
                            ),
                            "profile_delta": candidate_profile - profile,
                        },
                    },
                )
                self.select(proto_obj, candidate=proto_obj.candidate_set.get())
                return obj

            # Try harder by removing profile noise from odd suffixes.
            log.debug(
                "Falling back to suffix replacement... (profile=%d, address=%r)",
                profile,
                self.normalize({self.profile_field: proto_obj.data[self.profile_field]}),
            )

            candidate_characteristics = {}
            candidate_info = list(similar.values("id", self.profile_field, self.profile_field_name))
            for item in candidate_info:
                candidate_normalized = self.normalize(
                    {self.profile_field: item[self.profile_field]}
                )
                candidate_profile = item[self.profile_field_name]
                if candidate_profile is None:
                    candidate_profile = self.profile_object(candidate_normalized)
                    model.objects.filter(id=item["id"]).update(
                        **{self.profile_field_name: candidate_profile}
                    )

                if is_within_profile_threshold(
                    candidate_profile, profile, threshold=profile_threshold
                ):
                    d = get_levenshtein_distance(candidate_normalized, normalized)
                    # log.error([candidate_normalized,  normalized, d])
                    if d <= levenshtein_threshold:
                        profile_delta = candidate_profile - profile
                        candidate_characteristics[item["id"]] = {
                            "object_id": item["id"],
                            "levenshtein_distance": d,
                            "profile_delta": profile_delta,
                        }

            if candidate_characteristics:
                similar = model.objects.filter(id__in=candidate_characteristics.keys())
            else:
                similar = model.objects.none()

        if watch_ids:
            log.error([k for k in candidate_characteristics if k in watch_ids])

        num_similar = similar.count()
        if num_similar == 0:
            return None
        elif num_similar == 1:
            # Only select if it's a perfect match
            obj = similar.get()
            if candidate_characteristics[obj.id]["levenshtein_distance"] == 0:
                self.set_candidates(proto_obj, candidate_characteristics)
                self.select(proto_obj, candidate=proto_obj.candidate_set.get())
                return obj

        ## Only one match but it's not perfect, or there are multiple ambiguous matches

        # Trim to max limit (final order doesn't especially matter, but we sort for the top N items)
        candidate_characteristics = dict(
            sorted(
                candidate_characteristics.items(),
                **{
                    "key": lambda obj: obj[1]["levenshtein_distance"],
                },
            )[:candidate_limit]
        )
        self.set_candidates(proto_obj, candidate_characteristics)
        return False

    def select(self, proto_obj, candidate=None):
        """
        Validates a form for proto_obj's data and creates or updates a real object based on there
        being a ``candidate`` provided.

        This will raise errors if things aren't pre-validated by the import phase and given a usable
        candidate.  When called from ``do_import()``, any such error will be trapped and recorded.
        """
        if candidate:
            selected_id = candidate.object_id
        else:
            selected_id = None

        proto_obj.selected_object_id = selected_id
        proto_obj.save()

    def realize(self, proto_obj):
        """
        Pushes data on the proto_obj to its previously selected candidate.  If no candidate was
        selected, then a new concrete instance will be created with the data on proto_obj.
        """
        form_class = self.get_form_class(proto_obj)
        return merge.realize(proto_obj, form_class=form_class)

    # Merge process
    def get_proto_object(self, obj):
        """Returns a viable ProtoObject that represents an existing object instance."""
        model = obj.__class__
        data = self.extract_data(obj)
        data_profile = self.profile_data(data)
        proto_obj, _ = models.ProtoObject.objects.get_or_create(
            **{
                "content_type": ContentType.objects.get_for_model(model),
                "object_id": obj.id,
                "data_profile": data_profile,
                "defaults": {"data": data},
            }
        )
        return proto_obj

    def redirect(self, obj, to):
        merge.consolidate_merge_paths(master_instance=to, erroneous_instance=obj, discoverer=self)

    def remove(self, obj):
        """
        Deletes the target model instance.  Subclasses for specific models may arrange to deactivate
        the instance instead, if the instance supports such a thing.
        """
        obj.delete()


def is_within_profile_threshold(profile1, profile2, threshold):
    return (profile2 - threshold) < profile1 < (profile2 + threshold)


def is_within_levenshtein_threshold(s1, s2, threshold):
    return get_levenshtein_distance(s1, s2) <= threshold


def get_levenshtein_distance(s1, s2):
    """Computes a difference score for how many mutations it takes to get from s1 to s2."""
    if len(s1) < len(s2):
        s2, s1 = s1, s2
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


# FIXME: Don't keep model-specific importers in this app
from django.forms.models import modelform_factory
from axis.proto import abbreviations


class HomeDiscoverer(DefaultDiscoverer):
    form_class = None
    profile_field = "street_line1"
    profile_field_name = "street_line1_profile"
    profile_threshold = 400
    levenshtein_threshold = 6
    candidate_limit = 10

    normalizers = [
        itemgetter("street_line1"),
        unidecode,
        str.lower,
        normalizers.normalize_dict_replace(abbreviations.ADDRESS_SUFFIX_LOOKUPS),
        normalizers.normalize_dict_replace(abbreviations.ADDRESS_DIRECTION_LOOKUPS),
    ]

    def filter_candidate_queryset(self, proto_obj, queryset, **kwargs):
        queryset = super(HomeDiscoverer, self).filter_candidate_queryset(
            proto_obj, queryset, **kwargs
        )
        queryset = queryset.filter(
            **{
                "city__id": proto_obj.data["city"],
                # 'city__county__state__iexact': proto_obj.data['state'],
                "city__county__id": proto_obj.data["county"],
                # 'zipcode': proto_obj.data['zipcode'],
            }
        )
        return queryset

    def axis_merge(self, obj, to):
        model = to.__class__
        content_type = ContentType.objects.get_for_model(model)

        # Find data points that exist on the slave that can be pushed to the master
        master_data = model_to_dict(to)
        slave_data = model_to_dict(obj)
        new_data = {
            k: v for k, v in slave_data.items() if (master_data.get(k) is None) and (v is not None)
        }
        form_class = modelform_factory(model, fields=new_data.keys())
        form = form_class(new_data, instance=to)
        if form.is_valid():
            to = form.save()
        else:
            raise Exception(form.errors)

        # Relationships
        master_relationship_company_ids = list(to.relationships.values_list("company", flat=True))
        move_relationships = obj.relationships.exclude(
            company_id__in=master_relationship_company_ids
        )
        move_relationships.update(object_id=to.id)

        # Programs
        master_program_ids = list(to.homestatuses.values_list("eep_program", flat=True))
        move_homestatuses = obj.homestatuses.exclude(eep_program_id__in=master_program_ids)
        move_homestatuses.update(home=to)

        # Documents
        move_documents = obj.customer_documents.all()
        move_documents.update(object_id=to.id)


class StrictHomeDiscoverer(HomeDiscoverer):
    def filter_candidate_queryset(self, proto_obj, queryset, **kwargs):
        queryset = super(StrictHomeDiscoverer, self).filter_candidate_queryset(
            proto_obj, queryset, **kwargs
        )

        # Candidates should share the same street number
        street_line1_prefix = proto_obj.data["street_line1"].split(" ", 1)[0]
        queryset = queryset.filter(
            **{
                "street_line1__startswith": street_line1_prefix,
            }
        )

        return queryset
