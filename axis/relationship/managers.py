"""managers.py: Django relationship"""

import itertools
import logging
from collections import UserDict
from pprint import pformat

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q, Manager
from django.db.models.query import QuerySet
from django.urls import reverse, NoReverseMatch

from . import messages
from .strings import RELATIONSHIP_USED_CREATE

__author__ = "Steven Klass"
__date__ = "8/21/12 8:41 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


log = logging.getLogger(__name__)


class AssociationsInspector(object):
    def __get__(self, instance, type=None):
        if instance is None:
            return self
        return get_associations_dict(instance)


def get_associations_dict(obj):
    from axis.better_generics import get_generic_models
    from .models import Associations

    model_cache = get_generic_models(Associations)
    User = get_user_model()
    fk_type = "user" if isinstance(obj, User) else "company"
    breakdown = {}

    for model, association_model in model_cache.items():
        related_name = getattr(association_model, fk_type).field.related_query_name()
        breakdown[related_name] = getattr(obj, related_name)
    return AssociationsHub(obj, breakdown)


class AssociationsHub(UserDict):
    def __init__(self, instance, data):
        self.instance = instance
        UserDict.__init__(self, data)
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return "<Associations for %r:\n%s>" % (
            self.instance,
            pformat({k: v.count() for k, v in self.items()}, indent=4),
        )


class ObjectAssociationQuerySet(QuerySet):
    """Manager for associations on a specific model type."""

    def filter_by_company(self, company, is_active=None):
        """Returns associations managed by ``company``."""
        queryset = self.filter(owner=company)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

    def filter_by_user(self, user, is_active=None):
        """Returns associations managed by the target user's company."""
        if user.is_superuser:
            queryset = self.filter()
        else:
            queryset = self.filter_by_company(user.company)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

    def filter_for_company(self, company, is_active=None):
        """Returns associations given to ``company`` by someone else."""
        queryset = self.filter(company=company)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

    def filter_for_user(self, user, is_active=None):
        """Returns associations given to ``user`` by someone else."""
        queryset = self.filter(Q(user=user) | Q(user=None, company=user.company))
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

    def is_contributor(self, user, default=True):
        """
        Indicates if the target user is an official contributor within the queryset, or else returns
        None if no associations provide an answer one way or the other.
        """
        # If associations can't decide, we are presently assuming that this is because
        # relationships is the mechanism by which they are viewing the object, so they must be
        # a contributor, thus default=True.

        if user.is_superuser:
            return True

        associations = self.filter(company=user.company)
        if not associations.count():
            return default

        return associations.filter(is_active=True, is_contributor=True).exists()

    # def accepted(self):
    #     """ Filter associations that have been accepted by the share target. """
    #     # Relationship.objects.show_attached(False)
    #     return self.filter(is_accepted=True)
    #
    # def pending(self):
    #     """ Filter associations that have not yet been accepted but which are still visible. """
    #     # Relationship.objects.show_attached(True)
    #     return self.filter(Q(is_accepted=True, is_hidden=False) | \
    #                        Q(is_accepted=False, is_active=True))


class RelationshipManager(Manager):
    """
    Wraps all common Relationship filtering operations.  Only a few methods perform work.  Most
    forward to the RelationshipQuerySet which provides the queryset-level implementations.

    """

    def get_queryset(self):
        return RelationshipQuerySet(self.model, using=self._db)

    # Direct methods
    def _get_or_create_relationship(self, is_owned, **kwargs):
        """
        Passes through to ``get_or_create()``, with attachment flags guaranteed to be set as
        specified in ``kwargs``.

        """

        # Defaults for creating, but not for looking up an existing relationship
        defaults = {
            "is_owned": is_owned,
            "is_attached": kwargs.pop("is_attached", True),
            "is_viewable": kwargs.pop("is_viewable", True),
        }
        create, relationship = False, None
        try:
            relationship, create = self.get_or_create(defaults=defaults, **kwargs)
        except IntegrityError:
            try:
                relationship = self.get(
                    company=kwargs.get("company"),
                    content_type=kwargs.get("content_type"),
                    object_id=kwargs.get("object_id"),
                )
                create = False
            except ObjectDoesNotExist:
                try:
                    relationship = self.create(
                        company=kwargs.get("company"),
                        content_type=kwargs.get("content_type"),
                        object_id=kwargs.get("object_id"),
                    )
                    for k, v in defaults.items():
                        setattr(relationship, k, v)
                    create = True
                except IntegrityError:
                    log.error(
                        "Unable to create a relationship for %s to CT: %s ID: %s",
                        kwargs.get("company"),
                        kwargs.get("content_type"),
                        kwargs.get("object_id"),
                    )

        if not relationship:
            return
        # If the relationship was fetched, not created, we'll want to overwrite the flags with our
        # defaults.  This guarantees that any relationship returned by this method will have the
        # flags set as specified in the initial ``kwargs``.
        # We ONLY want to update this if the relationship is owned
        update = False
        if not create and not relationship.is_owned:
            for k, v in defaults.items():
                if getattr(relationship, k) != v:
                    setattr(relationship, k, v)
                    update = True
            if update:
                relationship.save()
        if relationship.content_object is None:
            log.warning("Relationship ID: %s Missing content object", relationship.id)
        if create or update:
            log.debug(
                "%s %s relation between %s [%d]",
                ("Create" if create else "Updating"),
                ("direct" if is_owned else "implied"),
                relationship,
                relationship.id,
            )

        return relationship, create

    def get_or_create_direct(self, **kwargs):
        """Creates an "owned" relationship instance."""
        kwargs.setdefault("is_owned", True)
        return self._get_or_create_relationship(**kwargs)

    def send_notification_message(self, company, object, source=None, auto_accepted=False):
        """Send a notification message"""
        from axis.company.models import COMPANY_MODELS

        Msg = messages.RelationshipInvitationMessage
        if source:
            Msg = messages.RelationshipInvitationFromCompanyMessage
        elif auto_accepted:
            Msg = messages.RelationshipInvitationFromCompanyAcceptedMessage
        context = {
            "source": source,
            "company": company,
            "verbose_name": object.content_object._meta.verbose_name.capitalize(),
            "object": "{}".format(object.content_object),
        }

        url = None
        kwargs = None

        model_name = object.content_object._meta.model_name

        # Handle the case for Companies
        if model_name in [c._meta.model_name for c in COMPANY_MODELS]:
            model_name = "company"
            kwargs = {"type": object.content_object.company_type}

        try:
            url = reverse("{}:list".format(model_name), kwargs=kwargs)
        except NoReverseMatch:
            try:
                url = reverse("{}_list".format(model_name), kwargs=kwargs)
            except NoReverseMatch:
                log.exception("Unable to find the generic list view for %s %s", object, kwargs)
        context["url"] = url
        Msg(url=url).send(context=context, company=company)

    def get_or_create_implied(self, company, **kwargs):
        """Returns an "implied" relationship instance."""
        is_owned = company.auto_add_direct_relationships or kwargs.get("is_owned", False)
        kwargs.setdefault("is_owned", is_owned)
        source = kwargs.pop("source", None)
        result, create = self._get_or_create_relationship(company=company, **kwargs)
        if not is_owned and create:
            msg_send = True
            if result.content_object:  # deletion of an object will take this away from us
                if hasattr(result.content_object, "should_send_relationship_notification"):
                    msg_send = result.content_object.should_send_relationship_notification(company)
            else:
                msg_send = False
            log.debug(
                "Relationship: %s Create: %s Owned: %s Msg Send: %s",
                result.content_object,
                create,
                is_owned,
                msg_send,
            )
            if msg_send:
                self.send_notification_message(company, result, source=source)
        return result, create

    def validate_or_create_relations_to_entity(
        self, entity, direct_relation, implied_relations=None, force=False, **kwargs
    ):
        """
        Performs ``get_or_create_xxx()`` calls for ``direct_relation`` and ``implied_relations``
        around the ``entity`` object.

        If the entity is an extension model of Company (e.g., RaterOrganization), it is normalized
        to the underlying Company instance before relationships are generated.

        Returns a 2-tuple of the direct relationship, and the queryset of implied relationships.

        """
        log = kwargs.get("log") if kwargs.get("log") else logging.getLogger(__name__)

        from axis.company.models import COMPANY_MODELS, Company

        if not implied_relations:
            implied_relations = []
        if isinstance(implied_relations, QuerySet):
            implied_relations = list(implied_relations)
        if not isinstance(implied_relations, (list, tuple)):
            implied_relations = [implied_relations]

        # Validate relation objects are companies
        error = False
        errors = []
        for relation in [direct_relation] + implied_relations:
            if not isinstance(relation, COMPANY_MODELS):
                errors.append(relation)
                imp_rels = ["{} ({})".format(rel, type(rel)) for rel in implied_relations]
                msg = "{} is not a company instance.  Direct: {} ({}) Implied: {}"
                log.error(msg.format(relation, direct_relation, type(direct_relation), imp_rels))
        if errors:
            raise TypeError(
                "direct_relation and implied_relations need to be companies you gave %r" % errors
            )

        # If the entity is an company extension model, normalize it to its Company instance
        if not isinstance(entity, Company) and isinstance(entity, COMPANY_MODELS):
            entity = entity.company_ptr  # Django's way of traversing implied one-to-one inheritance

        skip_identical_company_types = False
        if (
            not force
            and isinstance(entity, Company)
            and entity.company_type == direct_relation.company_type
        ):
            msg = "Skipping creating relationship between two {} company types for slugs: {} {}"
            log.debug(msg.format(entity.company_type, entity.slug, direct_relation.slug))
            skip_identical_company_types = True
            create, rel = None, "No relationship created"

        entity_content_type = ContentType.objects.get_for_model(entity)
        company_content_type = ContentType.objects.get_for_model(Company)

        # Ensure relationships exist or are created
        if not skip_identical_company_types:
            rel, create = self.get_or_create_direct(
                company=direct_relation, object_id=entity.id, content_type=entity_content_type
            )

        checked_implied_relationships = []
        company = None
        for company in implied_relations:
            if not isinstance(entity, Company):
                _rel, cr = self.get_or_create_implied(
                    company=company,
                    object_id=entity.id,
                    content_type=entity_content_type,
                    source=direct_relation,
                )
                checked_implied_relationships.append(_rel.pk)
                create = create if create else cr

            # If the direct and indirect company types are different, tie them together also
            if company.company_type != direct_relation.company_type:
                _rel, cr = self.get_or_create_direct(
                    company=direct_relation, object_id=company.id, content_type=company_content_type
                )
                create = create if create else cr

        if hasattr(entity, "_generate_utility_type_hints"):
            entity._generate_utility_type_hints(None, None, discover=True)

        try:
            entity_str = "<a href='{url}'>{object}</a>".format(
                url=entity.get_absolute_url(), object=entity
            )
        except:
            entity_str = "{}".format(entity)
        if create is not None:
            log.debug(
                RELATIONSHIP_USED_CREATE.format(
                    create="Create" if create else "Validated",
                    company=direct_relation,
                    object=entity_str,
                )
            )
        return rel, self.model.objects.filter(id__in=checked_implied_relationships)

    def create_mutual_relationships(self, *companies, **kwargs):
        """This is really used in tests to quickly create mutual relationships"""
        from axis.company.models import COMPANY_MODELS, Company

        # If the entity is an company extension model, normalize it to its Company instance
        for company_1, company_2 in itertools.product(companies, companies):
            if not type(company_1) is Company and type(company_1) in COMPANY_MODELS:
                company_1 = company_1.company_ptr
            if not type(company_2) is Company and type(company_2) in COMPANY_MODELS:
                company_2 = company_2.company_ptr
            err_msg = "Mutual relationships must be created for companies only - {}"
            assert type(company_1) is Company, err_msg.format(company_1)
            assert type(company_2) is Company, err_msg.format(company_2)
            if company_1 == company_2:
                continue
            self.validate_or_create_relations_to_entity(
                company_1, company_2, force=kwargs.get("force", False)
            )
            self.validate_or_create_relations_to_entity(
                company_2, company_1, force=kwargs.get("force", False)
            )

    def get_reversed_companies(self, company, ids_only=False):
        """Given a ``company``, returns other Company objects with a connecting relationship."""
        from axis.company.models import Company

        queryset = self.get_queryset().filter_company_relationships()
        queryset = queryset.filter(object_id=company.id, is_owned=True, is_viewable=True)
        id_list = queryset.values_list("company_id", flat=True)
        if ids_only:
            return id_list
        return Company.objects.filter(id__in=list(id_list))

    #######
    ## Proxy methods to the underlying queryset
    def filter_by_content_type(self, content_type=None, model=None):
        """Forwards method call to query set.
        :param model: Model Object
        :param content_type: Content Type
        """
        return self.get_queryset().filter_by_content_type(content_type=content_type, model=model)

    def get_id_list(self):
        return self.get_queryset().get_id_list()

    def filter_viewable_or_attached_and_unowned(self):
        return self.get_queryset().filter_viewable_or_attached_and_unowned()

    def show_attached(self, show_attached=True):
        return self.get_queryset().show_attached(show_attached=show_attached)

    def filter_by_company(self, company, show_attached=False):
        return self.get_queryset().filter_by_company(company, show_attached=show_attached)

    def filter_by_company_type(self, company_type):
        return self.get_queryset().filter_by_company_type(company_type)

    def filter_by_user(self, user, **kwargs):
        return self.get_queryset().filter_by_user(user, **kwargs)

    # Company operations that forward to methods in CompanyMixin definitions
    def filter_company_relationships(self):
        return self.get_queryset().filter_company_relationships()

    def filter_companies_for_company(self, company, show_attached=False):
        return self.get_queryset().filter_companies_for_company(
            company, show_attached=show_attached
        )

    def get_companies(self, show_attached=False, ids_only=False, **kwargs):
        return self.get_queryset().get_companies(
            show_attached=show_attached, ids_only=ids_only, **kwargs
        )

    # Commmunity/Subdivision operationst hat forward to methods in CommunityAndSubdivisionMixin
    def get_accepted_companies(self):
        return self.get_queryset().get_accepted_companies()

    def get_unaccepted_companies(self):
        return self.get_queryset().get_unaccepted_companies()

    def get_orgs(self, company_type=None, show_attached=True, ids_only=False):
        return self.get_queryset().get_orgs(
            company_type, show_attached=show_attached, ids_only=ids_only
        )

    def get_builder_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_builder_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    def get_rater_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_rater_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    def get_provider_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_provider_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    def get_eep_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_eep_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    def get_eep_sponsors(self, show_attached=True, ids_only=False):
        return self.get_queryset().get_eep_sponsors(show_attached=show_attached, ids_only=ids_only)

    def get_hvac_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_hvac_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    def get_utility_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_utility_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    def get_qa_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_qa_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    def get_general_orgs(self, show_attached=True, ids_only=False, native_org=False):
        return self.get_queryset().get_general_orgs(
            show_attached=show_attached, ids_only=ids_only, native_org=native_org
        )

    # Miscellaneous stubs for the various model querysets
    def filter_communities_for_company(self, company, show_attached=False):
        return self.get_queryset().filter_communities_for_company(company, show_attached)

    def get_communities(self, show_attached=False):
        return self.get_queryset().get_communities(show_attached=show_attached)

    def filter_subdivisions_for_company(self, company, show_attached=False):
        return self.get_queryset().filter_subdivisions_for_company(company, show_attached)

    def get_subdivisions(self, show_attached=False):
        return self.get_queryset().get_subdivisions(show_attached=show_attached)

    def filter_floorplans_for_company(self, company, show_attached=False):
        return self.get_queryset().filter_floorplans_for_company(company, show_attached)

    def get_floorplans(self, show_attached=False):
        return self.get_queryset().get_floorplans(show_attached=show_attached)

    def filter_homes_for_company(self, company, show_attached=False):
        return self.get_queryset().filter_homes_for_company(company, show_attached)

    def get_homes(self, show_attached=False):
        return self.get_queryset().get_homes(show_attached=show_attached)

    def filter_eepprogram_for_company(self, company, show_attached=False):
        return self.get_queryset().filter_eepprogram_for_company(company, show_attached)

    def get_eep_programs(self, show_attached=False):
        return self.get_queryset().get_eep_programs(show_attached=show_attached)


class CommunityMixin(object):
    def filter_communities_for_company(self, company, show_attached=False):
        from axis.community.models import Community

        return self.filter_by_content_type(model=Community).filter_by_company(
            company, show_attached
        )

    def get_communities(self, show_attached=False):
        from axis.community.models import Community

        id_list = (
            self.show_attached(show_attached).filter_by_content_type(model=Community).get_id_list()
        )
        return Community.objects.filter(id__in=list(id_list))


class SubdivisionMixin(object):
    def filter_subdivisions_for_company(self, company, show_attached=False):
        from axis.subdivision.models import Subdivision

        return self.filter_by_content_type(model=Subdivision).filter_by_company(
            company, show_attached
        )

    def get_subdivisions(self, show_attached=False):
        from axis.subdivision.models import Subdivision

        id_list = (
            self.show_attached(show_attached)
            .filter_by_content_type(model=Subdivision)
            .get_id_list()
        )
        return Subdivision.objects.filter(id__in=list(id_list))


class FloorplanMixin(object):
    def filter_floorplans_for_company(self, company, show_attached=False):
        from axis.floorplan.models import Floorplan

        return self.filter_by_content_type(model=Floorplan).filter_by_company(
            company, show_attached
        )

    def get_floorplans(self, show_attached=False):
        from axis.floorplan.models import Floorplan

        id_list = (
            self.show_attached(show_attached).filter_by_content_type(model=Floorplan).get_id_list()
        )
        return Floorplan.objects.filter(id__in=list(id_list))


class HomeMixin(object):
    def filter_homes_for_company(self, company, show_attached=False):
        from axis.home.models import Home

        return self.filter_by_content_type(model=Home).filter_by_company(company, show_attached)

    def get_homes(self, show_attached=False):
        from axis.home.models import Home

        id_list = (
            self.show_attached(show_attached)
            .filter_by_content_type(model=Home)
            .values_list("object_id")
        )
        return Home.objects.filter(id__in=id_list)


class EEPProgramMixin(object):
    def filter_eepprogram_for_company(self, company, show_attached=False):
        from axis.eep_program.models import EEPProgram

        return self.filter_by_content_type(model=EEPProgram).filter_by_company(
            company, show_attached
        )

    def get_eep_programs(self, show_attached=False):
        from axis.eep_program.models import EEPProgram

        id_list = (
            self.show_attached(show_attached).filter_by_content_type(model=EEPProgram).get_id_list()
        )
        return EEPProgram.objects.filter(id__in=list(id_list))


class CommunityAndSubdivisionMixin(CommunityMixin, SubdivisionMixin):
    """
    Contains a superset of Relationship QuerySet methods that are specific to community and
    subdivision relationship operations.  These are technically available on all querysets for
    maximum utility, but they are organized here for clarity.
    """

    def get_accepted_companies(self):
        """Returns companies which agree to the relationship or aren't customers."""

        from axis.company.models import Company

        query = Q(is_owned=True) | Q(company__is_customer=False, is_owned=False)
        id_list = self.filter(query).values_list("company_id", flat=True)
        return Company.objects.filter(id__in=list(id_list))

    def get_unaccepted_companies(self):
        """Returns companies which agree to the relationship or aren't customers."""

        from axis.company.models import Company

        query = Q(company__is_customer=True, is_owned=False)
        id_list = self.filter(query).values_list("company_id", flat=True)
        return Company.objects.filter(id__in=list(id_list))

    def _get_orgs(
        self, company_type=None, show_attached=True, ids_only=False, native_org=None, **kwargs
    ):
        """
        Deprecated: this is now always return Company class objects

        Returns companies with ``company_type``.  If ``native_org`` is a Company subclass, the
        returned objects will be of that type instead of the generic Company type.  For example,
        passing ``BuilderOrganization`` will return objects of that type.

        NOTE: This is intended to be used with the various ``get_XXX_orgs()`` methods, which send
        the correct ``native_org`` and ``company_type`` values.

        """
        from axis.company.models import Company

        queryset = self.show_attached(show_attached).filter(**kwargs)
        if company_type:
            queryset = queryset.filter_by_company_type(company_type)
        id_list = queryset.values_list("company_id", flat=True)

        if ids_only:
            return id_list

        return Company.objects.filter(id__in=list(id_list))

    def get_orgs(self, company_type=None, show_attached=True, ids_only=False, **kwargs):
        """
        Returns companies of type ``company_type``.  This method excludes the option of returning
        the companies as their native types.
        """
        return self._get_orgs(
            company_type, show_attached=show_attached, ids_only=ids_only, **kwargs
        )

    def get_builder_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "builder".  If ``native_org`` is True, returns
        the actual BuilderOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import BuilderOrganization

        return self._get_orgs(
            "builder",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and BuilderOrganization,
        )

    def get_rater_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "rater".  If ``native_org`` is True, returns
        the actual RaterOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import RaterOrganization

        return self._get_orgs(
            "rater",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and RaterOrganization,
        )

    def get_provider_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "provider".  If ``native_org`` is True, returns
        the actual ProviderOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import ProviderOrganization

        return self._get_orgs(
            "provider",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and ProviderOrganization,
        )

    def get_eep_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "eep".  If ``native_org`` is True, returns
        the actual EepOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import EepOrganization

        return self._get_orgs(
            "eep",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and EepOrganization,
        )

    def get_eep_sponsors(self, show_attached=True, ids_only=False):
        """
        Returns companies where `is_eep_sponsor` is True, returns generic Company instance.
        """
        from axis.company.models import Company

        queryset = self.show_attached(show_attached).filter()
        id_list = queryset.values_list("company_id", flat=True)
        if ids_only:
            return id_list
        return Company.objects.filter(id__in=list(id_list), is_eep_sponsor=True)

    def get_hvac_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "hvac".  If ``native_org`` is True, returns
        the actual HvacOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import HvacOrganization

        return self._get_orgs(
            "hvac",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and HvacOrganization,
        )

    def get_utility_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "utility".  If ``native_org`` is True, returns
        the actual UtilityOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import UtilityOrganization

        return self._get_orgs(
            "utility",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and UtilityOrganization,
        )

    def get_qa_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "qa".  If ``native_org`` is True, returns
        the actual QaOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import QaOrganization

        return self._get_orgs(
            "qa",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and QaOrganization,
        )

    def get_general_orgs(self, show_attached=True, ids_only=False, native_org=False):
        """
        Returns companies where ``company_type`` is "general".  If ``native_org`` is True, returns
        the actual GeneralOrganization instance instead of a generic Company instance.
        """
        from axis.company.models import GeneralOrganization

        return self._get_orgs(
            "general",
            show_attached=show_attached,
            ids_only=ids_only,
            native_org=native_org and GeneralOrganization,
        )


class CompanyMixin(object):
    """
    Contains a superset of Relationship QuerySet methods that are specific to company relationship
    operations.  These are technically available on all querysets for maximum utility, but they are
    organized here for clarity.
    """

    def filter_company_relationships(self):
        """
        Narrows the queryset to relationships that reference company models.  This returns a special
        CompanyRelationshipQuerySet which opens up access to operations that assume the queryset
        works on company relationships.
        """

        # TODO: Relationship creation code explicitly makes an effort to only reference the core
        # Company object (i.e., not the various subclasses).  Should this code have confidence in
        # that design?
        from axis.company.models import COMPANY_MODELS

        return self.filter_by_content_types(models=COMPANY_MODELS)

    def filter_companies_for_company(self, company, show_attached=False):
        """Filters relationships that reference companies, which belong to ``company``."""
        queryset = self.filter_company_relationships()
        return queryset.filter_by_company(company=company, show_attached=show_attached)

    def get_companies(self, show_attached=False, ids_only=False, **kwargs):
        """
        Pivots a queryset of company relationships to the Company objects they are generically
        attached to via ``object_id``.  If ``ids_only`` is True, only the ``object_id``
        ValuesQuerySet is returned.

        ``kwargs`` are convenience arguments that are used to filter the Company queryset before
        returning it.  Note that if ``ids_only`` is also True, this extra filtering stage required
        an extra query to circumvent the generic relationship querying limitations.

        """
        from axis.company.models import Company

        queryset = self.filter_company_relationships().show_attached(show_attached)
        is_viewable = kwargs.pop("is_viewable", None)
        if is_viewable is not None:
            queryset = queryset.filter(is_viewable=is_viewable)
        object_ids = queryset.get_id_list()

        # Return object_id list if no other filters are requested.
        if ids_only and not kwargs:
            return object_ids

        # It turns out that making 2 queries out of this (object_ids to list first) is a lot faster.
        companies = Company.objects.filter(id__in=list(object_ids)).filter(**kwargs)
        if ids_only:
            companies = companies.values_list("id", flat=True)
        return companies


class RelationshipQuerySet(
    CompanyMixin, CommunityAndSubdivisionMixin, FloorplanMixin, HomeMixin, EEPProgramMixin, QuerySet
):
    """
    Filtering methods that typically happen in an execution chain exist here, with the accompanying
    proxy methods found on the ``RelationshipManager`` class above.

    """

    def filter_by_content_type(self, content_type=None, model=None):
        """
        Filters by the supplied ContentType or Model instance, helping to remove repetitive calls
        to ``ContentType.objects.get_for_model()``.
        """

        assert content_type or model, "One of content_type or model must be supplied."

        if model:
            content_type = ContentType.objects.get_for_model(model)
        return self.filter(content_type=content_type)

    def filter_by_content_types(self, content_types=None, models=None):
        """
        Filters by the supplied ContentTypes or Models instances, helping to remove repetitive calls
        to ``ContentType.objects.get_for_models()``.
        """

        assert content_types or models, "One of content_types or models must be supplied."

        if models:
            content_types = ContentType.objects.get_for_models(*models).values()
        return self.filter(content_type__in=content_types)

    def get_id_list(self):
        return self.values_list("object_id", flat=True)

    def show_attached(self, show_attached=True):
        if show_attached:
            return self.filter_viewable_or_attached_and_unowned()
        # Note: This only looks at homes which I own.
        return self.filter(is_owned=True)
        # return self.filter(Q(is_owned=True) | Q(is_attached=True, is_owned=False))

    def filter_viewable_or_attached_and_unowned(self):
        """Return objects which are viewable and owned OR attached and unowned."""
        return self.filter(Q(is_viewable=True, is_owned=True) | Q(is_attached=True, is_owned=False))

    def filter_by_company(self, company, show_attached=False):
        """Filters objects through ``show_attached()`` and filter where ``company`` matches."""
        return self.show_attached(show_attached=show_attached).filter(company=company)

    def filter_by_company_type(self, company_type):
        """Filters objects where company__company_type matches ``company_type``."""
        kwargs = {"company__company_type": company_type}
        return self.filter(**kwargs)

    def filter_by_user(self, user, show_attached=False, **kwargs):
        """
        Finds the ``user``'s company and runs ``filter_by_company()``.  Superusers are explicitly
        skipped and instead returned unfiltered results.
        """
        if user.is_superuser:
            return self.all()
        kwargs["show_attached"] = show_attached
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)
