"""models.py: Django relationship"""


import datetime
import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from axis.better_generics import BetterGenericAccessor
from axis.company.strings import COMPANY_TYPES_MAPPING
from axis.home.strings import MULTIPLE_SPECIFIC_UTILITY
from .managers import RelationshipManager, ObjectAssociationQuerySet

__author__ = "Steven Klass"
__date__ = "8/21/12 8:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# This is a simple way to establish very generic relationships


# * You may only assign `is_attached = True` to another entity if that entity is not owned.
# * You may only assign `is_viewable = True` to your own company.  Once you do this `is_owned = True`
class Relationship(models.Model):
    """Generic model that signals intent to associate a model instance to a company."""

    # NOTE: this related_name was chosen specifically so I could look to the left side of the
    # relationship in the same manner as we reverse lookups down the chain.
    company = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, related_name="relationships"
    )

    # Content-object field
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    # These three fields establish the rules relationships
    # is_attached is set when some other company tries to associate an object to you
    # is_owned is set only once is_attached was made True and you accept the association
    # is_viewable is a mechanism that allows a user to supress an item once it is dealt with
    is_attached = models.BooleanField(default=True)  # Defines what is seen by others
    is_viewable = models.BooleanField(default=False)  # Defines what is seen by self
    is_owned = models.BooleanField(default=False)  # Once owned only the company can modify it

    # Looking ahead - here is how you can control these relationships.
    is_reportable = models.BooleanField(default=True)  # Defines whether it's included in reporting

    objects = RelationshipManager()
    history = HistoricalRecords()

    class Meta:
        unique_together = ("company", "content_type", "object_id")
        verbose_name = "Association"

    def __str__(self):
        if self.is_owned:
            type_str = "Direct"
        elif self.is_attached:
            type_str = "Attached"
        elif self.is_viewable:
            type_str = "Viewable"
        else:
            type_str = "No-visibility"
        return "{} association of {} ({}) to {} -- Owned: {} Viewable: {} Attached: {}".format(
            type_str,
            self.company,
            self.company.company_type.capitalize(),
            self.content_object,
            self.is_owned,
            self.is_viewable,
            self.is_attached,
        )

    def is_accepted(self):
        if self.is_owned:
            return True
        if not self.company.is_customer and not self.is_owned:
            return True
        return False

    def can_be_deleted(self, user):
        """Check that a relationship can be deleted"""
        if user.is_superuser:
            return True

        try:
            last_update = self.history.latest().history_date
        except ObjectDoesNotExist:
            last_update = datetime.datetime(1900, 1, 1, 1, tzinfo=datetime.timezone.utc)

        # Allowed correction time was bumped from 5 minutes to 24 hours to allow raters to
        # better catch their mistakes.
        if (now() - last_update).seconds <= 24 * 60 * 60:
            return True

        if self.is_owned and self.company.is_customer:
            if self.company.id == user.company.id:
                return True
            if self.company.auto_add_direct_relationships:
                if self.company.users.count():
                    return False
                return True
        else:
            return True
        return False

    def get_content_object(self):
        content_type = self.content_type
        if content_type.app_label == "company" and content_type.model.endswith("organization"):
            content_type = ContentType.objects.get(app_label="company", model="company")

        return content_type.get_object_for_this_type(pk=self.object_id)


class RelationshipUtilsMixin(object):
    """Mixin for models that implement a ``relationships`` m2m field."""

    org_fields = tuple(COMPANY_TYPES_MAPPING.keys())

    def get_org_relationships(self, split_utilities=True):
        """
        Returns a dictionary of company types to the queryset of relationships for that type.
        If ``split_utilities`` is True, the keys for those utilities will be "gas_utility" and
        "electric_utility", instead of the generic "utility".
        """
        breakdown = {}
        company_types = {"rater", "eep", "hvac", "qa", "general", "provider"}
        if split_utilities:
            company_types |= {"gas_utility", "electric_utility"}
        else:
            company_types.add("utility")
        for company_type in company_types:
            is_split_utility = company_type.endswith("_utility")
            breakdown_type = company_type

            if is_split_utility:
                # subtype = "gas"
                # breakdown_type = "gas_utility"
                # company_type = "utility"
                subtype, company_type = company_type.split("_")
                breakdown_type = subtype + "_utility"

            relationships = self.relationships.filter_by_company_type(company_type).select_related(
                "company"
            )

            if is_split_utility:
                relationships = relationships.filter(
                    **{"utilitysettings__is_" + breakdown_type: True}
                )

            breakdown[breakdown_type] = relationships
        return breakdown

    def get_orgs(self, use_suffixes=False, use_lists=False, use_ids=False, split_utilities=True):
        """
        Returns a dict of company types mapping to the orgs related to this home.

        Setting ``use_suffixes`` to True will make the dictionary keys take the form of "rater_orgs"
        etc.  (Builder type will be "builder_org", note the singular.)

        Setting ``use_lists`` to True will force plural values to evaluate to lists instead of lazy
        querysets.
        """
        # This is implented as the system for HomeForm and API to fetch the "*_orgs" virtual fields.

        orgs = {}

        builder_rels = self.relationships.filter_by_company_type("builder")

        # FIXME
        # This may not be the absolute most appropriate place to do this, but it was in the original
        # HomeUpdateView code for fetching initial_data for the HomeForm.
        # #####################
        if len(builder_rels) > 1:
            log.error(
                "Found {} builders attached to one {} {} - removing all {}".format(
                    len(builder_rels), self._meta.model_name, self, builder_rels
                )
            )
            builder_rels.delete()
            builder_rels = []
        # #####################

        singles = {"builder", "electric_utility", "gas_utility"}

        suffix = "_org" if use_suffixes else ""
        if len(builder_rels) == 1:
            builder_value = builder_rels[0].company
        else:
            builder_value = None
        if use_ids and builder_value:
            builder_value = builder_value.id
        orgs["builder%s" % suffix] = builder_value

        if split_utilities:
            suffix = "_org" if use_suffixes else ""
            gas_lookup = "gas_utility%s" % suffix
            electric_lookup = "electric_utility%s" % suffix

            try:
                orgs[gas_lookup] = self.get_gas_company()
            except AttributeError:
                orgs[gas_lookup] = None
            else:
                if use_ids and orgs[gas_lookup]:
                    orgs[gas_lookup] = orgs[gas_lookup].id

            try:
                orgs[electric_lookup] = self.get_electric_company()
            except AttributeError:
                orgs[electric_lookup] = None
            else:
                if use_ids and orgs[electric_lookup]:
                    orgs[electric_lookup] = orgs[electric_lookup].id

            # if use_lists:
            #     orgs[gas_lookup] = [orgs[gas_lookup]] if orgs[gas_lookup] else []
            #     orgs[electric_lookup] = [orgs[electric_lookup]] if orgs[electric_lookup] else []

        # Place company ids into the various initial form data fields
        suffix = "_orgs" if use_suffixes else ""
        breakdown = self.get_org_relationships(split_utilities=split_utilities)
        for company_type, relationships in breakdown.items():
            if split_utilities and company_type.endswith("_utility"):
                continue  # Skipped because already taken care of

            objects = relationships.get_orgs(company_type, ids_only=use_ids)
            if use_lists:
                objects = list(objects)
            value = objects
            _suffix = suffix

            if company_type in singles:
                if len(value):
                    value = value[0]
                else:
                    value = None

                if use_suffixes:
                    _suffix = "_org"
            orgs["%s%s" % (company_type, _suffix)] = value

        return orgs

    def get_org_ids(self, use_suffixes=False, use_lists=False, split_utilities=True):
        return self.get_orgs(
            use_suffixes=use_suffixes,
            use_lists=use_lists,
            split_utilities=split_utilities,
            use_ids=True,
        )

    def _generate_utility_type_hints(self, gas_relationship, electric_relationship, discover=False):
        """
        Since the relationship connections themselves can't indicate extra information about the
        association, we generate that information with a related model.

        This method is safe to execute when relationships already exist.  Duplicate hints will not
        be generated.
        """
        from axis.company.models import UtilitySettings

        if discover:
            # Ignore arguments (presumably None anyway) and try to find the right companies
            existing_gas_provider = self.get_gas_company()
            existing_electric_provider = self.get_electric_company()

            gas_provider = self._discover_utility_company("gas_provider")
            electric_provider = self._discover_utility_company("electricity_provider")

            if (
                existing_gas_provider
                and gas_provider
                and existing_gas_provider.pk != gas_provider.pk
            ):
                log.warn(
                    "Discovered different gas provider for %s(pk=%r) '%r' than existing "
                    "relationship: existing='%r', new='%r'",
                    self.__class__.__name__,
                    self.pk,
                    self,
                    existing_gas_provider,
                    gas_provider,
                )
                gas_relationship = self.relationships.get(company=existing_gas_provider)
            elif gas_provider:
                gas_relationship = self.relationships.get(company=gas_provider)
            else:
                gas_relationship = None
            if (
                existing_electric_provider
                and electric_relationship
                and existing_electric_provider.pk != electric_provider.pk
            ):
                log.warn(
                    "Discovered different electric provider for %s(pk=%r) '%r' than existing "
                    "relationship: existing='%r', new='%r'",
                    self.__class__.__name__,
                    self.pk,
                    self,
                    existing_electric_provider,
                    electric_provider,
                )
                electric_relationship = self.relationships.get(company=existing_electric_provider)
            elif electric_provider:
                electric_relationship = self.relationships.get(company=electric_provider)
            else:
                electric_relationship = None

        if not gas_relationship and not electric_relationship:
            log.debug("No utility relationships given for home '%s', nothing to do.", self)
            return

        def _generate_settings(relationship, **flags):
            try:
                settings = relationship.utilitysettings
            except UtilitySettings.DoesNotExist:
                log.debug(
                    "Creating new UtilitySettings for '%s' relationship: %r",
                    relationship.company,
                    flags,
                )
                settings = UtilitySettings.objects.create(relationship=relationship, **flags)
            else:
                log.debug(
                    "Updating existing UtilitySettings for '%s' relationship: %r",
                    relationship.company,
                    flags,
                )
                for k, v in flags.items():
                    setattr(settings, k, v)
                settings.save()

        if gas_relationship == electric_relationship:
            _generate_settings(gas_relationship, is_gas_utility=True, is_electric_utility=True)
        else:
            if gas_relationship:
                _generate_settings(gas_relationship, is_gas_utility=True, is_electric_utility=False)
            if electric_relationship:
                _generate_settings(
                    electric_relationship, is_gas_utility=False, is_electric_utility=True
                )

    def _discover_utility_company(self, utility_type, raise_errors=False):
        """
        Finds and returns a single company which provides the given utility type.  If there are
        multiple companies providing the same utility, the search will be narrowed to find a
        company providing ONLY the requested utility type.

        In the event that the narrowed search still yields multiple companies, the first company
        will be returned.

        If the returned company is already type-hinted for some other type, it will be ignored.
        """

        # NOTE: This does not read the utiltysettings extension on the relationship!  This method
        # exists to discover sensible candidates for a utility type based on existing relationships.

        from axis.home.models import Home

        exclude_hinted_type = None
        if utility_type == "electricity_provider":
            utility_type_short = "electric"
            exclude_hinted_type = "gas"
        elif utility_type == "gas_provider":
            utility_type_short = "gas"
            exclude_hinted_type = "electric"

        type_flags = {utility_type: True}
        relationships = self.relationships.all()
        if exclude_hinted_type:
            # Narrow queryset to items where the opposing type hasn't already gotten a lock on the
            # company at the exclusion of other types.  Note that if a company is type-hinted to
            # fulfill both types already, then this does NOT remove them from the running for being
            # "rediscovered."
            relationships = relationships.exclude(
                **{
                    "utilitysettings__is_{other_type}_utility".format(
                        other_type=exclude_hinted_type
                    ): True,
                    "utilitysettings__is_{this_type}_utility".format(
                        this_type=utility_type_short
                    ): False,
                }
            )
        utilities = relationships.get_utility_orgs(native_org=True)
        utilities = utilities.filter(**type_flags)
        if not utilities.count():
            return None
        if utilities.count() == 1:
            return utilities.get()

        # Try again with more precision on what the company offers
        for type_flag in ["electricity_provider", "gas_provider", "water_provider"]:
            type_flags.setdefault(type_flag, False)
        narrow_utilities = utilities.filter(**type_flags)
        if narrow_utilities.count() == 1:
            return narrow_utilities.get()

        # Still finding multiple results.
        name = " ".join(utility_type.split("_"))
        msg = MULTIPLE_SPECIFIC_UTILITY.format(utility_type=name)
        if raise_errors:
            raise MultipleObjectsReturned(msg)

        # Log the erroneously certified home with bad utility configuration.
        if (
            isinstance(self, Home)
            and self.homestatuses.filter(certification_date__isnull=False).count()
        ):
            utility_cos = ", ".join(map(str, utilities))
            log.error(msg + " {} -- {}".format(self.id, utility_cos))

        # Have to return something, but there's no distictly correct Company candidate.
        return utilities[0]

    def _get_utility_company(self, utility_type, raise_errors):
        """Returns a company matching the utility type that is already type-hinted."""
        filters = {
            "utilitysettings__is_{}_utility".format(utility_type): True,
        }

        relationships = self.relationships.filter(**filters)
        try:
            relationship = relationships.get()
        except Relationship.DoesNotExist:
            return None
        except Relationship.MultipleObjectsReturned:
            if raise_errors:
                raise
            relationship = relationships[0]

        return relationship.company

    def get_electric_company(self, raise_errors=False):
        """Returns an electric company that is already type-hinted."""
        return self._get_utility_company("electric", raise_errors=raise_errors)

    def get_gas_company(self, raise_errors=False):
        """Returns a gas company that is already type-hinted."""
        return self._get_utility_company("gas", raise_errors=raise_errors)

    # def get_water_company(self, raise_errors=False):
    #     """Get the electric company"""
    #     return self._get_utility_company('water_provider', raise_errors)

    def get_company_by_type(self, company_type, raise_errors=False):
        rels = self.relationships.filter_by_company_type(company_type).select_related("company")
        try:
            relationship = rels.get()
        except Relationship.DoesNotExist:
            return None
        except Relationship.MultipleObjectsReturned:
            if raise_errors:
                raise
            relationship = rels[0]
        return relationship.company

    def get_hvac_company(self, raise_errors=False):
        return self.get_company_by_type("hvac", raise_errors=raise_errors)

    def get_qa_company(self, raise_errors=False):
        return self.get_company_by_type("qa", raise_errors=raise_errors)

    def get_builder(self):
        rels = self.relationships.filter(company__company_type="builder")
        try:
            return rels.get().company
        except Relationship.DoesNotExist:
            return None
        except Relationship.MultipleObjectsReturned:
            for old_rel in list(rels.order_by("id"))[:-1]:
                log.warning("Multiples found - removing - {}!!".format(old_rel))
                old_rel.delete()
            return list(rels)[-1].company

    def pre_relationship_modification_data(
        self, relationship_data, ids, companies, user, request=None
    ):
        """
        Called before relationship modifications take place.  Models that generate other field
        values based on relationships should return those flags here.
        """
        return

    def post_relationship_modification_data(
        self, relationship_data, ids, companies, has_new_relationships, user, request=None
    ):
        return


class BaseAssociation(models.Model):
    """Designates a connection between a user/company and an object."""

    # NOTE: Dynamic fields are added to this model via the Associations.fields dictionary during
    # the synthesize step.

    objects = ObjectAssociationQuerySet.as_manager()

    class Meta:
        abstract = True
        unique_together = ("user", "company")

    # Designates that the user/company above is an active part of the home's lifecycle in Axis.
    # Anyone with 'False' here is just a spectator, the association given to them by someone else.
    is_contributor = models.BooleanField(default=True)

    # Control flags
    # Companies can put unsolicited associations on objects to other companies, and it is up to that
    # other company to confirm that they want the association.  As such, associations that are
    # still is_accepted=False are simply candidates for attracting the company's interest, but
    # might be broken via is_active=False.
    # Associations may also be hidden after the point of is_accepted=True if an item should be
    # cleared from active dashboards without having the association broken.
    is_active = models.BooleanField(default=True)  # Set to False instead of deleting
    is_accepted = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    # Optional expiration marker
    active_until = models.DateTimeField(blank=True, null=True)
    public_token = models.CharField(max_length=512, blank=True, null=True)


class Associations(BetterGenericAccessor):
    """Accessor placed on a model to imply support for user/company connections."""

    model = BaseAssociation
    model_name = "{source_model}Association"

    fields = {
        # Manager of the association
        "owner": (
            models.ForeignKey,
            ["company.Company"],
            {
                "related_name": "owned_{related_name}_associations",
                "on_delete": models.CASCADE,
            },
        ),
        # Permission target
        # User may be null, but a company should always be specified even if a user is given, so
        # that we can disambiguate which of the user's companies is being given access.
        "user": (
            models.ForeignKey,
            [settings.AUTH_USER_MODEL],
            {
                "related_name": "{related_name}",
                "blank": True,
                "null": True,
                "on_delete": models.SET_NULL,
            },
        ),
        "company": (
            models.ForeignKey,
            ["company.Company"],
            {
                "related_name": "{related_name}",
                "on_delete": models.CASCADE,
            },
        ),
    }
