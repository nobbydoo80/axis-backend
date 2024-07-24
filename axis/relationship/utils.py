"""utils.py: Django relationship"""

__author__ = "Steven Klass"
__date__ = "8/22/12 10:17 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
from functools import reduce

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models.query import QuerySet
from django.urls import reverse

from .messages import RelationshipDeletedMessage, RelationshipCreatedMessage
from .models import Relationship

from ..customer_neea.utils import NEEA_BPA_SLUGS

log = logging.getLogger(__name__)

AUTO_ASSIGNMENT_MAP = {
    "eto": ["eto", "peci", "csg-qa"],
    "eto-2015": ["eto", "peci", "csg-qa"],
    "eto-2016": ["eto", "peci", "csg-qa"],
    "eto-2017": ["eto", "peci", "csg-qa"],
    "eto-2018": ["eto", "peci", "csg-qa"],
    "eto-2019": ["eto", "peci"],
    "eto-2020": ["eto", "peci", "csg-qa"],
    "eto-2021": ["eto", "peci", "csg-qa"],
    "eto-2022": ["eto", "peci", "csg-qa"],
    "eto-fire-2021": ["eto", "peci", "csg-qa"],
    "neea-efficient-homes": ["neea", "clearesult-qa"],
    "utility-incentive-v1-single-family": ["neea", "clearesult-qa"],
    "utility-incentive-v1-multifamily": ["neea", "clearesult-qa", "clearesult"],
    "neea-bpa": ["neea"],
    "neea-bpa-v3": ["neea"],
    "wa-code-study": ["neea", "wa-code-study-qa"],
    # Requested #ZD5012
    "doe-zero-energy-ready-rev-05-performance-path": ["us-doe"],
    "doe-zero-energy-ready-rev-05-prescriptive-pat": ["us-doe"],
    "energy-star-version-3-rev-07": ["us-epa"],
    "energy-star-version-3-rev-08": ["us-epa"],
    "energy-star-version-31-rev-05": ["us-epa"],
    "energy-star-version-31-rev-08": ["us-epa"],
    "indoor-airplus-version-1-rev-03": ["us-epa"],
    "leed": ["eep-us-green-building-council-usgbc"],
    "phius": ["eep-passive-house-institute-us-phius"],
    "resnet-hers-certification": ["eep-resnet"],
    "wsu-hers-2020": ["qa-wsu", "provider-washington-state-university-extension-ene"],
    "washington-code-credit": ["peci"],
}


def get_relationship_column_supplier(user, app_label, model_name):
    """
    datatablesview currently uses a dynamically inserted column to show the "Add Remove Reject"
    text.  To remove redundancy, this utility exists to be used as the data supplier function on
    DatatableView subclasses.

    This wrapper function returns the callable function that will actually be used as the data
    supplier.

    The column data supplier expects to be given a value ``attached``, which needs to be generated
    by the view via the ``preload_record_data()`` method.  That method must either return the
    ``attached`` list as the first item in the sequence, or else as an entry in a dict, found at
    the key ``attached``.

    """

    def get_column_Add_Remove_Reject_data(obj, attached, *args, **kwargs):
        if user.has_perm("{}.change_{}".format(app_label, model_name)):
            pk = obj["pk"] if isinstance(obj, dict) else obj.pk
            reverse_kwargs = {"model": model_name, "app_label": app_label, "object_id": pk}
            if pk in attached:
                return """<a href="{}" class="add">Add</a> / <a href="{}" class="reject">Reject</a>""".format(
                    reverse("relationship:add_id", kwargs=reverse_kwargs),
                    reverse("relationship:reject_id", kwargs=reverse_kwargs),
                )
            return """<a href="{}">Remove</a>""".format(
                reverse("relationship:remove_id", kwargs=reverse_kwargs)
            )
        return ""

    return get_column_Add_Remove_Reject_data


def modify_relationships(obj, relationship_data, user, request=None):
    """Transplant the values for the *_orgs fields to actual relationships"""
    from axis.company.models import Company

    singular_items = {"builder", "gas_utility", "electric_utility"}

    # Data about the user
    company = user.company
    my_company_ids = set(Company.objects.filter_by_user(user).values_list("id", flat=True))

    # Build some data about the previous & new orgs references
    existing_orgs = obj.get_org_ids(use_suffixes=False, use_lists=True)
    new_orgs = relationship_data

    has_split_utilities = (
        "gas_utility" in relationship_data or "electric_utility" in relationship_data
    )

    existing_ids = set()
    for ids in existing_orgs.values():
        if not isinstance(ids, list):
            ids = [ids]
        existing_ids |= set(ids)

    new_ids = set()
    for org_label, orgs in new_orgs.items():
        if org_label in singular_items and not isinstance(orgs, (tuple, list, QuerySet)):
            # Convert singles into a list so we can merge it into the big list
            if orgs:
                orgs = [orgs]
            else:
                orgs = []
        new_ids |= set(org.pk for org in orgs)
    new_companies = list(Company.objects.filter(id__in=new_ids))

    obj.pre_relationship_modification_data(new_orgs, new_ids, new_companies, user, request=request)

    # Remove relationships
    for relationship in obj.relationships.select_related("company"):
        if relationship.company.id not in my_company_ids:
            continue

        company_type = relationship.company.company_type
        if has_split_utilities and company_type == "utility":
            # Pick one utility name to check for.
            # The assumption being made is that all utility subtypes appear on the form together,
            # so which one we use for an anchor doesn't matter when we go to check if the utility
            # type was in the list of things allowed to be modified.
            company_type = "gas_utility"

        # Ignore removal of types we're not supposed to be editing
        if company_type not in relationship_data:
            continue

        # Removal of stale items
        if relationship.company not in new_companies:
            if relationship.can_be_deleted(user):
                relationship.delete()
                RelationshipDeletedMessage().send(
                    context={
                        "company": str(relationship.company),
                        "object": str(relationship.get_content_object()),
                    },
                    company=relationship.company,
                )
            elif relationship.company.id in existing_ids:
                msg = (
                    "Unable to remove association for {owner} to {object}. "
                    "{owner} is an active customer; Please contact them for for removal."
                )
                msg = msg.format(object=obj, owner=relationship.company)
                messages.warning(request, msg)

    # Generate relationships
    has_new_relationships = Relationship.objects.validate_or_create_relations_to_entity(
        entity=obj, direct_relation=company, implied_relations=new_companies
    )

    obj.post_relationship_modification_data(
        new_orgs, new_ids, new_companies, has_new_relationships, user, request=request
    )

    if has_new_relationships:
        # Generate extra utility info
        gas_relationship = None
        gas_utility_org = new_orgs.get("gas_utility")
        if gas_utility_org:
            gas_relationship = obj.relationships.get(company=gas_utility_org)
        electric_relationship = None
        electric_utility_org = new_orgs.get("electric_utility")
        if electric_utility_org:
            electric_relationship = obj.relationships.get(company=electric_utility_org)
        obj._generate_utility_type_hints(gas_relationship, electric_relationship)

    url = obj.get_absolute_url()
    for company_id in [x for x in new_ids if x is not None and x not in existing_ids]:
        if company_id == user.company.id:
            continue
        RelationshipCreatedMessage(url=url).send(
            context={
                "action": "Created",
                "company": str(Company.objects.get(id=company_id)),
                "object": str(obj),
                "assigning_company": str(user.company),
            },
            company=Company.objects.get(id=company_id),
        )


def _create_or_update_spanning_relationship_for_obj(
    companies,
    target_obj,
    parent_obj=False,
    skip_implied=False,
    implied_companies=None,
    parent_exclude=None,
    check_conflicts=False,
):
    """This will add relationships for a list of companies to a target object if they don't already exist.  If a rant"""
    from axis.company.models import Company, COMPANY_MODELS

    if implied_companies is None:
        implied_companies = Company.objects.none()
    implied_ids = list(implied_companies.values_list("id", flat=True))

    company_ids = list(companies.values_list("id", flat=True))

    # log.debug("Input Companies: {} {} Target: {}".format(company_ids, target_obj._meta.verbose_name, target_obj.id))
    # log.debug("Input Implied Companies: {} {} Target: {}".format(implied_ids, target_obj._meta.verbose_name, target_obj.id))

    parent_companies, parent_direct_company_ids, parent_implied_company_ids = [], [], []
    if parent_obj and hasattr(parent_obj, "relationships"):
        # This will grab any companies from the parent that the input companies have a relationship with and propagate
        parent_companies = parent_obj.relationships.all()
        if parent_exclude:
            # log.debug('{} Excluding: {}'.format(parent_obj._meta.verbose_name, parent_exclude))
            parent_companies = parent_companies.exclude(**parent_exclude)
        parent_companies = parent_companies.values(
            "company", "is_owned", "is_attached", "is_viewable"
        )
        # log.debug("All {} Parents: {}".format(parent_obj._meta.verbose_name, [x for x in parent_companies]))

        # Companies in which the input companies actually have a relationship with
        ct = ContentType.objects.get_for_models(*COMPANY_MODELS)
        rel_companies = companies.filter(
            relationships__content_type__in=ct.values(),
            relationships__is_owned=True,
            relationships__is_attached=True,
        )
        rel_company_ids = rel_companies.values_list("relationships__object_id", flat=True)

        related_parent_companies = list(
            set([x["company"] for x in parent_companies]).intersection(set(rel_company_ids))
        )
        # log.debug("Related attached {} Parents: {}".format(parent_obj._meta.verbose_name, related_parent_companies))

        parent_direct_company_ids = [
            x["company"]
            for x in parent_companies
            if x["company"] in related_parent_companies and x["is_owned"]
        ]
        parent_implied_company_ids = [
            x["company"]
            for x in parent_companies
            if x["company"] in related_parent_companies and not x["is_owned"]
        ]
        # log.debug("Related attached {} Direct Parents: {}".format(parent_obj._meta.verbose_name, parent_direct_company_ids))
        # log.debug("Related attached {} Direct Parents: {}".format(parent_obj._meta.verbose_name, parent_implied_company_ids))

    ct = ContentType.objects.get_for_model(target_obj)
    existing_rels = Relationship.objects.filter(content_type=ct, object_id=target_obj.id)
    # log.debug("Existing: {}".format(existing_rels.values_list('company', flat=True)))
    existing_rel_ids = existing_rels.filter(is_owned=True).values_list("company", "is_owned")
    existing_direct_company_ids = [x[0] for x in existing_rel_ids if x[1]]
    existing_implied_company_ids = [x[0] for x in existing_rel_ids if not x[1]]

    direct_to_be_added = list(
        set(company_ids + parent_direct_company_ids) - set(existing_direct_company_ids)
    )
    implied_to_be_added = list(
        set(parent_implied_company_ids + implied_ids)
        - set(existing_implied_company_ids + company_ids + direct_to_be_added)
    )

    log.debug(
        "{} {} ({}) direct relationships to be added. {} {} implied relationships to be added.  D:{} I:{}".format(
            len(direct_to_be_added),
            target_obj._meta.verbose_name,
            target_obj.id,
            len(implied_to_be_added),
            target_obj._meta.verbose_name,
            direct_to_be_added,
            implied_to_be_added,
        )
    )

    if not len(direct_to_be_added) and len(implied_to_be_added):
        direct_to_be_added = [existing_direct_company_ids[0]]

    if skip_implied:
        implied_to_be_added = []

    rel_direct, rel_implied = [], []

    for company in Company.objects.filter(id__in=direct_to_be_added):
        # log.debug("Get or Verify Direct Relationships {}".format(company.id))
        implied = Company.objects.filter_by_company(company).filter(id__in=implied_to_be_added)
        # log.debug("Get or Verify Implied Relationships {}".format(implied.values_list('slug', flat=True)))
        rel_d, rel_i = Relationship.objects.validate_or_create_relations_to_entity(
            entity=target_obj, direct_relation=company, implied_relations=implied
        )
        flags = next((x for x in parent_companies if x["company"] == company.id), {})
        for element in [rel_d] + list(rel_i):
            save_required = False
            if "is_attached" in flags and flags.get("is_attached") != element.is_attached:
                # log.debug("Updating is_attached for {}".format(rel_d))
                element.is_attached = flags.get("is_attached")
                save_required = True
            if "is_viewable" in flags and flags.get("is_viewable") != element.is_viewable:
                # log.debug("Updating is_viewable for {}".format(rel_d))
                element.is_viewable = flags.get("is_viewable")
                save_required = True
            if save_required:
                element.save()
        rel_direct.append(rel_d)
        rel_implied += rel_i

    if parent_obj:
        copy_split_utility_flags(target_obj, parent_obj)

    if check_conflicts:
        company_slugs = set(target_obj.relationships.values_list("company__slug", flat=True))
        unexpected = get_unexpected_companies(company_slugs, target_obj)
        if unexpected:
            if hasattr(target_obj, "state") and target_obj.state == "complete":
                log.debug(
                    "Updating {} view/attach relationships {} complete {}".format(
                        len(unexpected), unexpected, target_obj._meta.verbose_name
                    )
                )
                Relationship.objects.filter(
                    company__slug__in=unexpected,
                    content_type=ContentType.objects.get_for_model(target_obj),
                    object_id=target_obj.id,
                ).update(is_viewable=False, is_attached=False)
            else:
                log.debug(
                    "Deleting {} relationships {} for {}".format(
                        len(unexpected), unexpected, target_obj._meta.verbose_name
                    )
                )
                Relationship.objects.filter(
                    company__slug__in=unexpected,
                    content_type=ContentType.objects.get_for_model(target_obj),
                    object_id=target_obj.id,
                ).delete()

    return rel_direct, rel_implied


def _create_or_update_floorplan_relations(home_status):
    from axis.company.models import Company

    floorplans = list(home_status.floorplans.all())
    if home_status.floorplan and home_status.floorplan not in home_status.floorplans.all():
        floorplans = list(home_status.floorplans.all()) + [home_status.floorplan]

    home_status_rels = home_status.home.relationships.values_list("company", flat=True)
    for floorplan in floorplans:
        owner_rels = floorplan.owner.relationships.get_companies().values_list("id", flat=True)
        companies = Company.objects.filter(
            id__in=list(set(home_status_rels).intersection(set(owner_rels)))
        )
        _create_or_update_spanning_relationship_for_obj(
            companies=companies, target_obj=floorplan, skip_implied=True
        )


def get_unexpected_companies(company_slugs, target_obj):
    """These are companies that shoud never be on the same object - think of this as a catch"""

    unexpected_company_slugs, program_owner_slugs = [], None

    if hasattr(target_obj, "eep_program"):
        program_owner_slugs = [target_obj.eep_program.owner.slug]
    elif hasattr(target_obj, "homestatuses"):
        program_owner_slugs = list(
            target_obj.homestatuses.values_list("eep_program__owner__slug", flat=True)
        )

    # log.debug("PROGRAM SLUGS: {}".format(program_owner_slugs))
    if program_owner_slugs is not None:
        if "eto" not in program_owner_slugs:
            unexpected_company_slugs += ["eto", "csg-qa"]
            if "neea" not in program_owner_slugs:
                unexpected_company_slugs += ["peci", "clearresult-qa"]

        # BE VERY CAREFUL HERE - This is a VERY BROAD BRUSH - WHICH ONE WINS?
        if "aps" in program_owner_slugs:
            unexpected_company_slugs += ["srp"]
        elif "srp" in program_owner_slugs:
            unexpected_company_slugs += ["aps"]

    return list(set(unexpected_company_slugs).intersection(set(company_slugs)))


def get_auto_assigned_companies(home_statuses):
    """
    Returns a 2-tuple of direct/implied company slugs that should related to the home shared by the
    home_statuses queryset.
    """
    from axis.company.models import Company
    from axis.qa.models import QARequirement

    direct_companies = []
    implied_companies = []

    # Ensure the obvious QARequirement's QACompany has a relationship to the home.
    # NOTE: We do this step first so that its easy to tell in the general AUTO_ASSIGNMENT_MAP step
    # if a QA company has already been slotted in.
    program_qa_assignments = {}  # {program_slug: qa_companies}
    for home_status in home_statuses:
        if home_status.home.state in ["WA", "OR", "ID", "MT"]:
            # Grab possible requirements but limit to items that declare required_companies, which
            # should automatically bind the requirement's QACompany to the home.
            requirements = (
                QARequirement.objects.filter_for_add(home_status.home, user=None)
                .annotate(n_required_companies=Count("required_companies"))
                .filter(eep_program=home_status.eep_program_id, n_required_companies__gt=0)
            )
            qa_company_slugs = list(
                requirements.values_list("qa_company__slug", flat=True).distinct()
            )
            if home_status.eep_program.slug in NEEA_BPA_SLUGS:
                # QA is the responsibility of the incentive payer if they choose
                # This is done to ensure that if calc_data exists we will only update the qa_slugs
                # if there is an incentive payer.  If there isn't we retain clearresult-qa
                calc_data = home_status.standardprotocolcalculator_set.first()
                if calc_data:
                    qa_company_slugs = ["clearesult-qa"]
                    if calc_data.incentive_paying_organization:
                        qa_required_companies = dict(
                            requirements.values_list(
                                "required_companies__slug", "qa_company__slug"
                            ).distinct()
                        )
                        if calc_data.incentive_paying_organization.slug in qa_required_companies:
                            qa_company_slugs = [
                                qa_required_companies[calc_data.incentive_paying_organization.slug]
                            ]
                else:
                    qa_company_slugs = []

            direct_companies.extend(qa_company_slugs)
            program_qa_assignments[home_status.eep_program.slug] = qa_company_slugs

    # Add general auto-assignments
    required_companies_info = home_statuses.values_list(
        "eep_program__slug", "eep_program__owner__slug", "company__slug"
    )
    for program_slug, owner_slug, status_company_slug in required_companies_info:
        auto_direct_companies = AUTO_ASSIGNMENT_MAP.get(program_slug, []) + [status_company_slug]

        # QA companies obtained in the first phase should stop more QA companies from coming through
        override_qa_companies = program_qa_assignments.get(program_slug)
        if override_qa_companies:
            auto_direct_companies = list(
                Company.objects.filter(slug__in=auto_direct_companies)
                .exclude(company_type="qa")
                .values_list("slug", flat=True)
            )

        direct_companies += auto_direct_companies
        if owner_slug not in direct_companies:
            implied_companies += [owner_slug]

    return direct_companies, implied_companies


def create_or_update_spanning_relationships(
    companies, target_obj, skip_implied=False, push_down=False
):
    from axis.company.models import Company, COMPANY_MODELS
    from axis.community.models import Community
    from axis.subdivision.models import Subdivision
    from axis.floorplan.models import Floorplan
    from axis.home.models import Home, EEPProgramHomeStatus

    if companies is None:
        ct = ContentType.objects.get_for_model(target_obj)
        rels = Relationship.objects.filter(content_type=ct, object_id=target_obj.id, is_owned=True)
        companies = Company.objects.filter(id__in=rels.values_list("company", flat=True))
        companies_str = ""
    else:
        if isinstance(companies, COMPANY_MODELS):
            companies = Company.objects.filter(id=companies.id)
        elif isinstance(companies, (list, tuple)):
            companies = Company.objects.filter(id__in=[x.id for x in companies])
        companies_str = ", ".join(list(companies.values_list("slug", flat=True)))

    if push_down and companies.count() > 1:
        raise SyntaxError("You can only pass one company with push down")

    log.info(
        "create_or_update_spanning_relationships called on {} [{}] Skip: {} Push-Down: {} Companies: {}".format(
            target_obj._meta.verbose_name, target_obj.id, skip_implied, push_down, companies_str
        )
    )

    if isinstance(target_obj, Community):
        rels = _create_or_update_spanning_relationship_for_obj(
            companies=companies, target_obj=target_obj, skip_implied=skip_implied
        )
        if push_down:
            sub_objs = Subdivision.objects.filter_by_company(
                companies.first(), community=target_obj, show_attached=True
            )
            log.info(
                "Pushing Community {} to {} Subdivision".format(target_obj.id, sub_objs.count())
            )
            for sub_obj in sub_objs:
                create_or_update_spanning_relationships(
                    companies, sub_obj, skip_implied=skip_implied, push_down=push_down
                )
        return rels
    if isinstance(target_obj, Subdivision):
        original_companies = companies
        companies = Company.objects.filter(
            id__in=[target_obj.builder_org_id] + list(companies.values_list("id", flat=True))
        )
        rels = _create_or_update_spanning_relationship_for_obj(
            companies=companies,
            target_obj=target_obj,
            parent_obj=target_obj.community,
            skip_implied=skip_implied,
            parent_exclude={"company__company_type": "builder"},
        )
        if push_down:
            sub_objs = Home.objects.filter_by_company(
                companies.first(), subdivision=target_obj, show_attached=True
            )
            log.info("Pushing subdivision {} to {} Homes".format(target_obj.id, sub_objs.count()))
            for sub_obj in sub_objs:
                create_or_update_spanning_relationships(
                    original_companies, sub_obj, skip_implied=skip_implied, push_down=push_down
                )
        return rels
    elif isinstance(target_obj, Home):
        return _create_or_update_spanning_relationship_for_obj(
            companies, target_obj, target_obj.subdivision, skip_implied, check_conflicts=True
        )
    elif isinstance(target_obj, EEPProgramHomeStatus):
        home_statuses = target_obj.home.homestatuses.all()

        direct_companies, implied_companies = get_auto_assigned_companies(home_statuses)
        direct_companies.extend(list(companies.values_list("slug", flat=True)))
        direct_companies = Company.objects.filter(slug__in=direct_companies)
        implied_companies = Company.objects.filter(slug__in=implied_companies)

        reldata = _create_or_update_spanning_relationship_for_obj(
            companies=direct_companies,
            target_obj=target_obj.home,
            implied_companies=implied_companies,
            check_conflicts=True,
        )

        _create_or_update_floorplan_relations(target_obj)
        return reldata

    elif isinstance(target_obj, Floorplan):
        # floorplan_owner_relations = floorplan.owner.relationships.get_companies()
        # if company.company_type not in ['rater', 'eep', 'utility', 'provider'] or \
        #   company in [home_stat.company, home_stat.eep_program.owner ] or \
        #   company in home_stat.get_providers() or \
        #   company in floorplan_owner_relations:

        home_status_rels = target_obj.homestatuses.values_list(
            "home__relationships__company__slug", flat=True
        )
        owner_rels = target_obj.owner.relationships.get_companies().values_list("slug", flat=True)
        log.debug("Floorplan home_status_rels:  {}".format(home_status_rels))
        log.debug("Floorplan owner_rels:  {}".format(owner_rels))

        overlap = list(set(home_status_rels) & set(owner_rels))

        # Consider the subdivision's relationships in the overlap set
        subdivision_ids = list(target_obj.subdivision_set.values_list("id", flat=True))
        if subdivision_ids:
            subdivision_rels = (
                Relationship.objects.show_attached()
                .filter_by_content_type(model=Subdivision)
                .filter(object_id__in=subdivision_ids)
            )
            subdivision_rels = subdivision_rels.values_list("company__slug", flat=True)
            overlap += list(set(subdivision_rels) & set(owner_rels))

        companies = Company.objects.filter(slug__in=(overlap + [target_obj.owner.slug]))
        log.debug("Companies: {}".format(companies.values_list("slug", flat=True)))
        return _create_or_update_spanning_relationship_for_obj(
            companies=companies, target_obj=target_obj, skip_implied=True
        )

    elif isinstance(target_obj, Company):
        if target_obj.auto_add_direct_relationships:
            # We should only ever hit this with 1 company in `companies`
            company = companies.get()
            log.info("%s is auto accepting a direct relationship to %s", target_obj, company)
            Relationship.objects.create_mutual_relationships(company, target_obj)
            rel = Relationship.objects.filter(company=target_obj, object_id=company.id).last()
            Relationship.objects.send_notification_message(target_obj, rel, auto_accepted=True)


def copy_split_utility_flags(destination_obj, source_obj):
    """
    Split utilities that are found on ``source_obj`` are then inspected on ``destination_obj`` and
    have the type hints generated to match.
    """
    # Note that this is tolerant of the source_obj having a utility relationship that doesn't exist
    # on the destination_obj, but the context we expect this to be used is one where source_obj
    # relationships were explicitly just copied to the destination_obj.
    gas_org = source_obj.get_gas_company()
    electric_org = source_obj.get_electric_company()

    gas_rel = destination_obj.relationships.filter(company=gas_org).first()
    electric_rel = destination_obj.relationships.filter(company=electric_org).first()

    destination_obj._generate_utility_type_hints(gas_rel, electric_rel)


def get_companies_by_path(instance, company_types):
    companies = []

    for company_type in company_types:
        company_getter = reduce(getattr, company_type.split("."), instance)

        if hasattr(company_getter, "__call__"):
            companies.append(company_getter())
        else:
            companies.append(company_getter)

    return companies


def associate_companies_to_obj(obj, owner, *companies):
    """
    Assigns Association links from ``obj`` to the given companies.  ``obj`` must be a model that
    inherits the Assocation api via the Associations() manager.
    """

    for company in companies:
        obj.associations.get_or_create(
            owner=owner,
            company=company,
            defaults={
                "is_contributor": False,
            },
        )


def replace_relationship_on_obj(obj, replace, replace_with, force=False):
    """Replace a relationship on an entity to a company with another company."""
    if replace != replace_with:
        raise ValueError("Trying to replace {} with {}".format(replace, replace_with))

    try:
        obj.relationships.get(company=replace).delete()
    except Relationship.DoesNotExist:
        log.error("%s has no relationship to %s", replace, obj)
        if not force:
            raise  # do not continue
    else:
        log.info("%s is no longer associated with %s", replace, obj)

    relationship = Relationship.objects.validate_or_create_relations_to_entity(obj, replace_with)
    log.info("%s has been created", relationship)


def get_mutual_company_ids(company):
    comps = Relationship.objects.get_reversed_companies(company, ids_only=True)
    rels = company.relationships.get_companies(ids_only=True)
    return list(set(rels).intersection(set(comps)))


def get_mutual_company_ids_including_self(company):
    return get_mutual_company_ids(company) + [company.id]


# Console/management utilities
def _group_relationships_by_quantity(for_model, company_type):
    """
    Returns a valueslist queryset of distinct object_ids to the number of relationships on that
    object_id (for the company_type specified).

    For example:

        [(23501, 3), (23502, 1), (23503, 1), (23504, 2)]

    """
    content_type = ContentType.objects.get_for_model(for_model)
    relationships = Relationship.objects.filter(
        company__company_type=company_type, content_type=content_type
    )

    # Get valuesqueryset grouped on how many utility relationships are on the same object_id.
    return relationships.values_list("object_id").annotate(n=Count("object_id"))


def _filter_relationships_by_max_quantity(for_model, company_type, max_count):
    return _group_relationships_by_quantity(for_model, company_type).filter(n__gt=max_count)


def _get_objects_with_too_many_relationships(for_model, company_type, max_count):
    """
    Returns queryset of objects carrying too many relationships for the specified type/quantity
    threshold given.  Quantity information is lost--you get back only the queryset of objects that
    satisified the query.
    """
    results = _group_relationships_by_quantity(for_model, company_type)
    results = results.filter(n__gt=max_count)
    return for_model.objects.filter(id__in=dict(results).keys())


def _get_homes_with_too_many_utilities(max_count=2):
    from axis.home.models import Home

    return _get_objects_with_too_many_relationships(Home, "utility", max_count)


def _get_relationships_with_missing_utilitysettings():
    from axis.home.models import Home

    content_type = ContentType.objects.get_for_model(Home)
    relationships = Relationship.objects.filter(
        company__company_type="utility", content_type=content_type, utilitysettings=None
    )
    return relationships


def _get_homes_with_missing_utilitysettings():
    from axis.home.models import Home

    relationships = _get_relationships_with_missing_utilitysettings()
    ids = set(relationships.values_list("object_id", flat=True).distinct())
    return Home.objects.filter(id__in=ids)
