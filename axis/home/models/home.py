"""home.py.py: """
__author__ = "Artem Hruzd"
__date__ = "06/26/2019 18:41"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import logging
from collections import namedtuple, OrderedDict

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q, Count
from django.urls import reverse
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

from axis.certification.models import CertifiableObjectHomeCompatMixin
from axis.checklist.models import Answer
from axis.core.utils import slugify_uniquely
from axis.customer_eto.utils import get_eto_region_name_for_zipcode
from axis.geographic.placedmodels import LotAddressedPlacedModel
from axis.home import strings
from axis.home.managers import HomeManager
from axis.home.utils import flatten_inheritable_settings
from axis.relationship.models import Relationship, RelationshipUtilsMixin
from .eep_program_home_status import EEPProgramHomeStatus
from ..messages import (
    HomeRelationshipRemovalErrorMessage,
    HomeChangeBuilderForSubdivisionMismatchMessage,
    HomeUserAttachedWithoutCompanyAssociationMessage,
    HomeIIPProgramOwnerHasNotAgreedToBeAttachedToHomeMessage,
)

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class Home(RelationshipUtilsMixin, LotAddressedPlacedModel, CertifiableObjectHomeCompatMixin):
    subdivision = models.ForeignKey(
        "subdivision.Subdivision",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Subdivision/MF Development",
    )
    is_custom_home = models.BooleanField(default=False)

    # DEPRECATION WARNING!!
    alt_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Alias/Code")

    construction_stage = models.ManyToManyField(
        "scheduling.ConstructionStage",
        through="scheduling.ConstructionStatus",
        help_text=strings.HOME_HELP_TEXT_CONSTRUCTION_STAGE,
    )

    eep_programs = models.ManyToManyField("eep_program.EEPProgram", through="EEPProgramHomeStatus")

    customer_documents = GenericRelation("filehandling.CustomerDocument")
    relationships = GenericRelation("relationship.Relationship")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    is_active = models.BooleanField(default=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    slug = models.SlugField(editable=False, unique=True, max_length=64)
    street_line1_profile = models.PositiveIntegerField(blank=True, null=True)

    bulk_uploaded = models.BooleanField(default=False)

    objects = HomeManager()
    history = HistoricalRecords()

    # ORM hint for easily retrieving common Annotations
    annotations = GenericRelation("annotation.Annotation")

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.get_home_address_display()

    def save(self, *args, **kwargs):
        """Ensures unique slug and copies county, climate zone, and state from related objects."""
        if not self.slug:
            self.slug = slugify_uniquely(self.get_home_address_display()[:60], self.__class__)
        if isinstance(self.lot_number, str):
            self.lot_number = self.lot_number.strip()

        from axis.customer_hirl.utils import profile_address

        self.street_line1_profile = profile_address(self.street_line1)

        super(Home, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Removes relationships from the deleted Home."""
        self.relationships.all().delete()
        super(Home, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return reverse("home:view", kwargs={"pk": self.id})

    @classmethod
    def can_be_added(cls, user):
        return user.has_perm("home.add_home")

    def can_be_edited(self, user):
        if user.is_superuser:
            return True

        if not user.company:
            return False
        # do not allow edit home for customer HIRL or affiliated companies
        # they must use HIRL Registration page for correct sync
        if user.is_customer_hirl_company_member() or user.is_sponsored_by_company(
            company=customer_hirl_app.CUSTOMER_SLUG, only_sponsor=True
        ):
            return False

        if user.has_perm("home.change_home"):
            if self.relationships.filter(is_owned=True, company_id=user.company.id).exists():
                return True
        return False

    def can_be_deleted(self, user) -> bool:
        return self.get_reason_cannot_be_deleted(user) is None

    def get_reason_cannot_be_deleted(self, user) -> str:
        """If the home cannot be deleted by the passed user, explain why. Generally we
        only care about whether the home can be deleted, and use can_be_deleted(), but
        this is helpful for diagnosing why."""
        if not user:
            return "No user"

        company = user.company

        if not company:
            return "User has no company"

        # do not allow delete home for customer HIRL or affilated companies
        # they must use HIRL Registration page for correct sync
        if user.is_customer_hirl_company_member() or user.is_sponsored_by_company(
            company=customer_hirl_app.CUSTOMER_SLUG, only_sponsor=True
        ):
            return "User is HIRL company member, or is sponsored by an HIRL company"

        if (now() - self.created_date).seconds <= 5 * 60:
            users = self.history.all().values_list("history_user", flat=True)
            users = list(set(filter(None, users)))
            if not users or users == [user.id]:
                return None  # This home can be deleted by this user
        if user.is_superuser:
            return None  # This home can be deleted by this user

        relations = self.relationships.filter(is_owned=True).exclude(
            company__auto_add_direct_relationships=True
        )
        relations_ids = set(relations.values_list("company__id", flat=True))
        relations_count = len(relations_ids)

        homestatus_companies = set(self.homestatuses.values_list("company__id", flat=True))
        eep_owners = set(self.eep_programs.values_list("owner__id", flat=True))

        if relations_count == 1 and relations[0].company == company:
            if len(eep_owners) == 0:
                return None  # This home can be deleted by this user
            elif {company.id} == homestatus_companies:
                # If the homestatuses involved all belong to the user, we'll allow it
                return None  # This home can be deleted by this user

            return "Home has EEP owners, and not all homestatuses belong to the user"
        elif relations_ids - eep_owners == {company.id}:
            # If owned relationships minus the program owners is just the request user, allow it
            return None  # This home can be deleted by this user

        return "Owned relationships minus program owners is not just the request user"

    def should_send_relationship_notification(self, company):
        """Under what criteria should a message be sent to other users"""
        return True if self.is_custom_home else False

    def get_builder(self):
        """Fall back to subdivision builder if not provided on the home."""
        builder = super(Home, self).get_builder()
        if builder is None and self.subdivision and self.subdivision.builder_org:
            Relationship.objects.get_or_create_implied(
                company=self.subdivision.builder_org,
                object_id=self.id,
                content_type=ContentType.objects.get_for_model(self),
            )
            return self.subdivision.builder_org
        return builder

    def get_id(self):
        """Returns a nice prepadded ID"""
        return "{:06}".format(self.id)

    def get_home_address_display_parts(
        self,
        include_lot_number=True,
        include_confirmed=False,
        include_city_state_zip=False,
        raw=False,
        company=None,
    ):
        """Returns a namedtuple of components, where unavailable items are blank strings."""
        AddressParts = namedtuple(
            "AddressParts",
            [
                "street_line1",
                "street_line2",
                "city",
                "state",
                "zipcode",
                "lot_number",
                "confirmed_designator",
            ],
        )

        if (company and company.display_raw_addresses) and (
            self.geocode_response and self.geocode_response.geocode.raw_street_line1
        ):
            raw = True

        confirmed_designator = self.get_address_designator().strip() if include_confirmed else ""
        city = ""
        state = ""
        zipcode = ""
        if raw and self.geocode_response:
            address_target = self.geocode_response.geocode
            field_prefix = "raw_"
        else:
            address_target = self
            field_prefix = ""

        def _address_field(name):
            try:
                field = getattr(address_target, f"{field_prefix}{name}")
            except AttributeError:
                return getattr(self, name)
            else:
                if field is None and name != "street_line2":
                    field = getattr(self, name)
            return field

        if include_city_state_zip:
            try:
                city = _address_field("city").name
            except AttributeError:
                city = ""
            state = _address_field("state")
            if raw and self.geocode_response and address_target.raw_city:
                state = address_target.raw_city.state
            zipcode = _address_field("zipcode")

        parts = AddressParts(
            _address_field("street_line1"),
            _address_field("street_line2"),
            city,
            state,
            zipcode,
            _address_field("lot_number") if (self.lot_number and include_lot_number) else "",
            confirmed_designator,
        )
        return parts

    def get_home_address_display(
        self,
        include_lot_number: bool = True,
        include_confirmed: bool = False,
        include_city_state_zip: bool = False,
        raw: bool = False,
        company: models.Model | None = None,
    ) -> str:
        """Return the address with lot number"""

        breakdown = self.get_home_address_display_parts(
            **{
                "include_lot_number": include_lot_number,
                "include_confirmed": include_confirmed,
                "include_city_state_zip": include_city_state_zip,
                "raw": raw,
                "company": company,
            }
        )

        city_state_zip = ""
        if include_city_state_zip:
            city_state_zip = ", {city}, {state}, {zipcode}".format(**breakdown._asdict())

        return "{}{}{}{}{}".format(
            breakdown.street_line1,
            ", {}".format(breakdown.street_line2) if breakdown.street_line2 else "",
            city_state_zip,
            ", (Lot: {})".format(breakdown.lot_number) if breakdown.lot_number else "",
            " {}".format(breakdown.confirmed_designator) if breakdown.confirmed_designator else "",
        )

    def get_addr(self, include_city_state_zip=False, raw=False, company=None) -> str:
        """Used in templates"""
        return self.get_home_address_display(
            include_lot_number=False,
            include_city_state_zip=include_city_state_zip,
            raw=raw,
            company=company,
        )

    def get_eto_region_name_for_zipcode(self, user):
        # Only relevant if the home has the ETO 2017 program
        # and the user is ETO or CLEAResult Provider/QA.
        has_eto_program = self.homestatuses.filter(
            Q(eep_program__slug="eto") | Q(eep_program__slug__startswith="eto-")
        ).exists()
        can_see_region = user.company.slug in ("eto", "peci", "csg-qa") or user.is_superuser
        if has_eto_program and can_see_region:
            return get_eto_region_name_for_zipcode(self.zipcode)

    def get_eep_program_stats(self, user, eep_program=None):
        """Returns the homestatus instances for this home associated with the user."""
        homestatuses = EEPProgramHomeStatus.objects.filter_by_user(user=user, home=self)
        if eep_program:
            homestatuses = homestatuses.filter(eep_program=eep_program)
        return homestatuses

    def discover_related_documents(self, breakdown, user):
        """Hook for adding documents determined to be connected to this object."""

        if not self.collection_request:
            # TODO: Filter for company
            answers = Answer.objects.filter(home=self).select_related("answerimage")
            breakdown["checklist"] = answers
            return breakdown

        collector = self.get_collector(user=user)
        answers = (
            collector.get_inputs()
            .annotate(num_documents=Count("customer_documents"))
            .filter(num_documents__gt=0)
        )

        breakdown["checklist"] = answers
        return breakdown

    def is_home_certified(self, company):
        """
        Is this home certified
        :param company:  :class:`company.models.company`
        """
        stats = EEPProgramHomeStatus.objects.filter_by_company(company, home=self)
        stats_count = stats.count()
        all_certified = stats.filter(certification_date__isnull=False).count() == stats_count
        return stats_count >= 1 and all_certified

    def has_sampling_lock(self):
        """Return true if any home status that has
            1) No Incentive Payment Status and a cert date.
            2) Incentive payment status that is in an allowed edit states and cert date.

        Should we allow this home to be edited when in a sampleset?  If the sampleset contains
        any member which falls into the above criteria the answer is No.  Because if the user
        changes the subdivision or builder that would mess up the viability of the sampleset."""

        from axis.sampleset.models import SampleSetHomeStatus

        samplesets = (
            SampleSetHomeStatus.objects.current()
            .filter(home_status__in=self.homestatuses.all(), is_test_home=True)
            .values("sampleset__id")
        )

        if samplesets:
            conditions = ["start", "ipp_payment_failed_requirements"]
            return (
                EEPProgramHomeStatus.objects.in_sampleset()
                .filter(
                    (
                        Q(incentivepaymentstatus__isnull=True)
                        | ~Q(incentivepaymentstatus__state__in=conditions)
                    ),
                    samplesethomestatus__sampleset__in=samplesets,
                    certification_date__isnull=False,
                )
                .distinct()
                .count()
            )
        return False

    def has_locked_homestatuses(self, include_samplesets=True):
        """Return true if this home has
            1) No Incentive Payment Status and a cert date.
            2) Incentive payment status that is in an allowed edit states
            3) A certification date or an equivalent "locked state" for the given program

        Should we allow this home to be edited when in a sampleset?  If the sampleset contains
        any member which falls into the above criteria the answer is No.  Because if the user
        changes the subdivision or builder that would mess up the viability of the sampleset."""

        if include_samplesets:
            sampling_lock = self.has_sampling_lock()
            if sampling_lock:
                return sampling_lock

        restricted_incentive_states = ["start", "ipp_payment_failed_requirements"]
        has_no_incentives = Q(incentivepaymentstatus__isnull=True)
        has_safe_incentive_states = ~Q(
            incentivepaymentstatus__state__in=restricted_incentive_states
        )
        is_certified = Q(certification_date__isnull=False)
        locked_by_inspection_complete = Q(
            **{
                "eep_program__owner__slug": "eto",
                "state": "certification_pending",
            }
        )

        past_lock_threshold = is_certified | locked_by_inspection_complete

        return (
            self.homestatuses.filter(
                past_lock_threshold & (has_no_incentives | has_safe_incentive_states),
            )
            .distinct()
            .count()
        )

    def pre_relationship_modification_data(
        self, relationship_data, ids, companies, user, request=None
    ):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        was_custom_home = self.is_custom_home
        self.is_custom_home = True
        builder_org = relationship_data.get("builder")
        sub_builder_org = None
        subdivision = None

        if self.subdivision:
            subdivision = self.subdivision
            sub_builder_org = self.subdivision.builder_org
            self.is_custom_home = False
        if was_custom_home != self.is_custom_home:
            self.save()

        # Reconcile a message for the user about having combinations of subdivision & builder
        # specified when in conflict.
        if sub_builder_org and builder_org:  # subdivision given as well as an explicit builder
            if sub_builder_org.id != builder_org.id:
                if request:
                    HomeChangeBuilderForSubdivisionMismatchMessage(
                        url=self.get_absolute_url()
                    ).send(
                        user=request.user,
                        context=dict(
                            sub_builder=sub_builder_org,
                            builder=builder_org,
                            subdivision=subdivision,
                        ),
                    )
        elif sub_builder_org:  # subdivision given, no explicit builder
            relationship = self.relationships.filter(company__company_type="builder")
            if relationship.count():
                relationship = relationship[0]
                if not relationship.can_be_deleted(user):
                    if request:
                        HomeRelationshipRemovalErrorMessage(
                            url=self.get_absolute_url(),
                        ).send(
                            user=request.user,
                            context=dict(object=self, owner=relationship.company),
                        )

        # Compare attached companies to the users m2m
        attaching_companies = companies + [user.company]
        attached_users = User.objects.filter(company__in=attaching_companies)
        linked_users = User.objects.filter(id__in=self.users.all())
        for linked_user in linked_users:
            if linked_user not in attached_users:
                if request:
                    HomeUserAttachedWithoutCompanyAssociationMessage(
                        url=self.get_absolute_url(),
                    ).send(
                        user=request.user,
                        context={
                            "user_full_name": linked_user.get_full_name(),
                            "company_name": linked_user.company.name,
                        },
                    )

    def post_relationship_modification_data(
        self, relationship_data, ids, companies, has_new_relationships, user, request=None
    ):
        from axis.relationship.utils import create_or_update_spanning_relationships

        for stat in self.homestatuses.all():
            create_or_update_spanning_relationships(companies, stat)

        # Generate messages about incentives
        is_rater = user.company.company_type == "rater"
        for home_stat in self.homestatuses.select_related("eep_program__owner"):
            eep = home_stat.eep_program

            accepted_companies = self.relationships.get_accepted_companies()
            has_relationship = eep.owner in accepted_companies
            incentives = eep.rater_incentive_dollar_value + eep.builder_incentive_dollar_value

            log.info("Relationship: %s Incentives: %s", has_relationship, incentives)
            if not has_relationship and incentives > 0 and is_rater:
                if request:
                    HomeIIPProgramOwnerHasNotAgreedToBeAttachedToHomeMessage(
                        url=home_stat.get_absolute_url(),
                    ).send(
                        user=request.user,
                        context={"program_name": eep.name, "owner_company_name": eep.owner},
                    )
            if has_new_relationships:
                home_stat.update_stats()

    # Please don't use this unless you really want them all!
    def get_home_status_breakdown(self, user, as_dict=False):
        """Please don't use this unless you really want them all!"""
        # How do you like that docstring? ^^^^^

        # This method calls each individual homestatus.get_simplified_status_for_user(),
        # and builds a master list that groups the homestatuses into their phase of completion.

        # The returned value is a namedtuple with these groupings.

        can_view, can_edit, can_transition_to_certify = [], [], []
        can_certify, completed, has_checklist = [], [], False

        stats = self.get_eep_program_stats(user)
        for stat in stats:
            data = stat.get_simplified_status_for_user(user)
            if data.completed:
                completed.append(stat)
            if data.can_certify:
                can_certify.append(stat)
            if data.can_edit:
                can_edit.append(stat)
                if data.can_transition_to_certify:
                    can_transition_to_certify.append(stat)
            if data.can_view:
                can_view.append(stat)
            if data.has_checklist and has_checklist is False:
                has_checklist = True

        # stat = EEPProgramHomeStatus.objects
        values = OrderedDict(
            [
                ("stats_count", len(stats)),
                ("stats_all", stats),
                ("stats_can_edit", can_edit),
                ("stats_can_view", can_view),
                ("stats_can_transition_to_certify", can_transition_to_certify),
                ("stats_can_certify", can_certify),
                ("stats_completed", completed),
                ("has_checklist", has_checklist),
            ]
        )
        if as_dict:
            return values
        HomeStatusConditions = namedtuple("HomeStatusConditions", values.keys())
        return HomeStatusConditions(*values.values())

    def get_current_stage(self, user):
        """
        Return the most current construction stage

        For a given company which is filling out a checklist they can assign a construction stage.
        Everyone else will need to defer to the relationships of those filling out the
        checklists.
        """
        from axis.scheduling.models import ConstructionStatus, ConstructionStage

        if user is None:
            return None
        stats = EEPProgramHomeStatus.objects.filter_by_user(user, home=self)
        co_ids = list(stats.values_list("company", flat=True))
        c_statuses = ConstructionStatus.objects.filter(home=self, company__id__in=co_ids)
        if c_statuses.count():
            c_statuses = list(c_statuses.order_by("stage__order", "-pk"))
            c_statuses.reverse()
            return c_statuses[0]
        else:
            if user.company.company_type != "qa" and user.company.id in co_ids:
                stage = ConstructionStage.objects.filter(order=0).first()
                if stage:
                    c_status, create = ConstructionStatus.objects.get_or_create(
                        stage=stage, home=self, start_date=now(), company=user.company
                    )
                    return c_status
        return None

    def get_ipp_payments(self, user):
        """Return the IPP payments attached to a home"""
        from axis.incentive_payment.models import IncentiveDistribution

        return IncentiveDistribution.objects.filter_by_company_or_customer_for_home(user, self)

    def get_ipp_annotations(self, user):
        from axis.incentive_payment.models import IncentivePaymentStatus

        return IncentivePaymentStatus.objects.filter_by_user(user).filter(home_status__home=self)

    def get_questions_and_permission_for_user(self, user):
        """
        Get questions from the home stats along with the users permission for each set of questions.
        :returns list of tuple (Question Queryset, permission string)
        """
        stats = self.homestatuses.all()
        questions = []
        for stat in stats:
            questions.append(stat.get_questions_and_permission_for_user(user))

        return questions

    def get_answers(self):
        """
        Get answers from the home stats for a home.
        :returns list of answers
        """
        return Answer.objects.filter_by_home(self)

    def get_qa_statuses(self):
        """
        Get QAStatuses from teh home stats for a home.
        :return: queryset of QA Statuses
        """
        from axis.qa.models import QAStatus

        qastats = QAStatus.objects.none()
        if self.pk:
            for stat in self.homestatuses.all():
                qastats = qastats | stat.qastatus_set.all()

        return qastats

    def get_permit_and_occupancy_settings(self, company):
        return flatten_inheritable_settings(
            company,
            manager_attr="permitandoccupancysettings_set",
            sources=[company, self.subdivision, self],
        )

    def get_references(self):
        """Data which is used by program validations"""
        builder = self.get_builder()
        electric_utility = self.get_electric_company()
        gas_utility = self.get_gas_company()
        references = {
            "home__city_id": self.city.id if self.city else None,
            "home__county_id": self.county.id if self.county else None,
            "home__us_state": self.county.state if self.county else None,
            "home__climate_zone": "%s" % self.county.climate_zone if self.county else None,
            "relationship_ids": list(self.relationships.values_list("id", flat=True)),
            "builder_id": builder.id if builder else None,
            "electric_utility_id": electric_utility.id if electric_utility else None,
            "gas_utility_id": gas_utility.id if gas_utility else None,
        }
        return references

    def validate_references(self):
        """Validate References"""
        references = self.get_references()
        for home_status in self.homestatuses.all():
            if hasattr(home_status, "validated_data"):
                home_status.validated_data.validate_references(**references)
            else:
                # Generate validated_data attribute along the way
                home_status.validate_references()

    def get_preview_photo(self):
        """
        Get preview photo for home
        :return: HomePhoto instance or None
        """
        return self.homephoto_set.filter(is_primary=True).first()
