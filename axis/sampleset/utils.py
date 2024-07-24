""" Sampling models, round 2, ding ding. """


import logging
import operator
import re
from collections import namedtuple, Counter
from functools import reduce

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from axis.relationship.models import Relationship
from axis.resnet.models import RESNETCompany
from . import strings

__author__ = "Autumn Valenta"
__date__ = "07/11/14 11:15 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

UUIDMATCH = re.compile(
    r"^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z", re.I
)


def modify_sampleset(obj, test_id_list, sampled_id_list, user, simulate=True):
    """API utility that updates a target sampleset object to use the specified homestatus ids."""
    from axis.home.models import Home, EEPProgramHomeStatus
    from axis.home.tasks import update_home_states, update_home_stats
    from .models import SampleSetHomeStatus

    messages = []

    id_list = test_id_list + sampled_id_list

    # samplesethomestatus items
    current_items = (
        obj.samplesethomestatus_set.current() if obj.pk else SampleSetHomeStatus.objects.none()
    )
    to_keep = current_items.filter(home_status__id__in=id_list)
    to_keep_ids = set(to_keep.values_list("home_status__id", flat=True))
    to_remove = current_items.exclude(home_status__id__in=id_list)
    to_remove_ids = set(to_remove.values_list("home_status__id", flat=True))

    # eepprogramhomestatus items
    to_add_ids = set(id_list) - to_keep_ids
    to_add = EEPProgramHomeStatus.objects.filter(id__in=to_add_ids)

    # Discover active uses of the "to_add" homestatuses in other samplesets
    stale = (
        SampleSetHomeStatus.objects.current()
        .filter(home_status__id__in=to_add_ids)
        .exclude(sampleset_id=obj.id)
    )
    moved_info = dict(stale.values_list("home_status__id", "sampleset__id"))

    final_home_ids = set(
        EEPProgramHomeStatus.objects.filter(id__in=(to_keep_ids | to_add_ids)).values_list(
            "home_id", flat=True
        )
    )

    # Discover characteristics of the new configuration
    new_config_homestatuses = EEPProgramHomeStatus.objects.filter(id__in=(to_keep_ids | to_add_ids))
    eep_program = discover_eep_program_for_homes(new_config_homestatuses)
    is_metro_sampled = discover_is_metro_sampled(new_config_homestatuses)

    # Integrity checks

    # Enforced maximum sampleset size
    new_size = len(to_keep_ids | to_add_ids) - len(to_remove_ids)
    if new_size > settings.SAMPLING_MAX_SIZE:
        messages.append(
            {
                "level": "ERROR",
                "message": "New configuration has too many items ({})".format(new_size),
            }
        )

        return {
            "sampleset": obj.pk,
            "unchanged": to_keep_ids,
            "added": to_add_ids,
            "removed": to_remove_ids,
            "moved": moved_info,
            # Derived details
            "eep_program": eep_program.id if eep_program else None,
            "is_metro_sampled": is_metro_sampled,
            "is_certifiable": False,
            "builder_id": None,
            "builder": None,
            "messages": messages,
        }

    # Verify that if the items require the metro-sampled flag, that the program allows this
    if eep_program:
        if not eep_program.allow_metro_sampling and is_metro_sampled:
            messages.append(
                {
                    "level": "WARNING",
                    "message": strings.METRO_SAMPLING_UNSUPPORTED_BY_PROGRAM.format(
                        program=eep_program
                    ),
                    "code": "metro_unsupported",
                }
            )
        elif (
            eep_program.allow_metro_sampling
            and is_metro_sampled
            and is_metro_sampled != obj.is_metro_sampled
        ):
            messages.append(
                {
                    "level": "INFO",
                    "message": strings.METRO_SAMPLING_IN_USE,
                    "code": "using_metro",
                }
            )

    if is_metro_sampled:
        metros_in_use = set(new_config_homestatuses.values_list("home__metro_id", flat=True))
        if len(metros_in_use) > 1:
            messages.append(
                {
                    "level": "ERROR",
                    "message": strings.MISMATCHED_METROS,
                    "code": "mismatched_metros",
                }
            )
    elif eep_program is False:
        # TODO: Generate information about the current use of multiple programs.
        # This might be okay, it might be a warning.  It depends on the programs having overlap
        # in their question ids.
        messages.append(
            {
                "level": "INFO",
                "message": strings.MISMATCHED_PROGRAMS,
                "code": "mismatched_programs",
            }
        )

    if final_home_ids:
        # Verify that a consensus can be reached about the builder
        builder_rels = Relationship.objects.filter(
            object_id__in=final_home_ids,
            content_type=ContentType.objects.get_for_model(Home),
            company__company_type="builder",
        ).distinct()
        builders = dict(builder_rels.values_list("company_id", "company__name"))
        if len(builders) > 1:
            messages.append(
                {
                    "level": "ERROR",
                    "message": strings.MISMATCHED_BUILDERS,
                    "code": "mismatched_builders",
                }
            )
            builder_id = False
            builder = False
        else:
            builder_id = list(builders.keys())[0]
            builder = builders[builder_id]
    else:
        # No homes in sampleset now
        builder_id = None
        builder = None

    # TODO: Generate warning message about excessive uses of sampleset test home answers
    all_memberships = SampleSetHomeStatus.objects.filter(
        home_status_id__in=(to_keep_ids | to_add_ids)
    ).current()

    # Generate warning message for samplesets that have mixed certification statuses
    # It should generally be true that certified items aren't being moved into incomplete samplesets
    # but if an uncertified sampled house is entered late into a certified sampleset group and there
    # is sufficient slack for the test homes to have provided answers to it, the setup should be
    # accepted.
    keep_certifications = to_keep.filter(home_status__certification_date__isnull=False).count()
    add_certifications = to_add.filter(certification_date__isnull=False).count()
    total_certifications = keep_certifications + add_certifications

    # Commit!
    if simulate is False:
        if obj.pk is None:
            obj.save()

        to_remove.delete()
        stale.delete()

        obj.is_metro_sampled = is_metro_sampled
        obj.save()

        to_keep.update(revision=obj.revision)
        to_keep.filter(home_status__id__in=test_id_list).update(is_test_home=True)
        to_keep.filter(home_status__id__in=sampled_id_list).update(is_test_home=False)
        SampleSetHomeStatus.objects.bulk_create(
            [
                SampleSetHomeStatus(
                    **{
                        "sampleset": obj,
                        "home_status": home_status,
                        "revision": obj.revision,
                        "is_test_home": home_status.id in test_id_list,
                        "is_active": True,
                    }
                )
                for home_status in to_add
            ]
        )

        if len(all_memberships):
            # Select a homestatus item in the set to use for stats/state update.
            # Because the item is in the sampleset now, all sibling items will be updated too.
            update_id = all_memberships[0].home_status.id
            update_home_stats(eepprogramhomestatus_id=update_id)
            update_home_states(eepprogramhomestatus_id=update_id)
            EEPProgramHomeStatus.objects.get(id=update_id).validate_references()

    # This line appears after having saved new items!
    all_certified = total_certifications == all_memberships.count()

    has_issue = bool([item for item in messages if item["level"] in ("WARNING", "ERROR")])
    is_certifiable = False
    for sshs in all_memberships:
        if sshs.home_status.can_user_certify(user):
            is_certifiable = True
            break

    response = {
        "sampleset": obj.pk,
        "unchanged": to_keep_ids,
        "added": to_add_ids,
        "removed": to_remove_ids,
        "moved": moved_info,
        # Derived details
        "eep_program": eep_program.id if eep_program else None,
        "is_metro_sampled": is_metro_sampled,
        "is_certifiable": (not all_certified) and (not has_issue) and is_certifiable,
        "builder_id": builder_id,
        "builder": builder,
        "messages": messages,
    }
    return response


def get_homestatus_test_answers(test_statuses, include_failures=True):
    """Returns the queryset of Answers that the test homes are providing for sampling."""
    # Each test home uses a program, and each distinct program will contribute the list of
    # question IDs that are relevant for sampling purposes.
    #
    # Homes participating in more than one program (even if that program isn't explicitly part
    # of this sampleset) will provide answers from the other programs if the question id is one
    # that our sampled program wants.
    #
    # This has the effect that if ProgramA wants Question1 and Question2, and ProgramB also
    # wants the same Question1 and Question2 (identical by id numbers), the answers to these
    # questions will be pulled regardless of which program they were officially answered for
    # when the checklist was filled out.

    from axis.checklist.models import Answer

    if not test_statuses:
        # Avoid returning .none() because the queryset will lack our custom methods.
        return Answer.objects.filter(id=None)

    answer_qs = []
    handled_programs = {}
    for item in test_statuses:
        if item.eep_program_id not in handled_programs:
            handled_programs[item.eep_program.id] = item.eep_program.get_checklist_question_set()
        questions = handled_programs[item.eep_program.id]

        answer_qs.append(
            Q(
                # Answers given for this home
                home=item.home_id,
                # for any question this program wants (even if it was answered for the sake of some
                # other program on the same home)
                question__in=questions,
                # if answered by the company
                user__company=item.company_id,
            )
        )

    answers = Answer.objects.all()
    if not include_failures:
        answers = answers.filter(is_considered_failure=False)
    return answers.filter(reduce(operator.or_, answer_qs))


def discover_is_metro_sampled(queryset):
    """Returns True if there is more than one subdivision used on the given homes."""
    from axis.home.models import EEPProgramHomeStatus
    from .models import SampleSetHomeStatus

    if queryset.model is SampleSetHomeStatus:
        prefix = "home_status__"
    elif queryset.model is EEPProgramHomeStatus:
        prefix = ""
    else:
        prefix = ""
    used_subdivions = set(queryset.values_list(prefix + "home__subdivision__id", flat=True))
    return len(used_subdivions) > 1


def discover_is_test_home(home_status):
    """Returns True if the given homestatus has Answers associated with its home."""
    questions = home_status.eep_program.get_checklist_question_set()
    return home_status.home.answer_set.filter(question__in=questions).count()


def discover_builder_org_for_homes(sshomestatus_queryset):
    """
    Returns the builder if is the same for all homes in queryset.  If more than one builder is in
    use, the return value is None, and the conditions for calling this utility should be modified
    by the frontend to get a better return result.

    If no builders appear to be specified by the queryset (a technical condition allowed by our
    foreign keys using null=True), False is also returned and a log warning is issued to avoid
    causing server 500 errors.
    """
    from axis.company.models import Company
    from axis.home.models import Home

    builders = (
        Company.objects.filter(company_type=Company.BUILDER_COMPANY_TYPE)
        .filter(
            Q(
                relationships__object_id__in=sshomestatus_queryset.values_list(
                    "home_status__home_id"
                )
            ),
            Q(relationships__content_type=ContentType.objects.get_for_model(Home)),
        )
        .distinct()
    )
    builder_id_list = builders.values_list("id", flat=True)
    try:
        return builders.get()
    except Company.MultipleObjectsReturned:
        log.info(
            "Homes in queryset use more than one builder: %r [%d ids=%r]",
            builders,
            len(builder_id_list),
            list(builder_id_list),
        )
        return False
    except Company.DoesNotExist:
        log.warning(
            "No builders specified by homes! [%d ids=%r]",
            len(sshomestatus_queryset),
            list(sshomestatus_queryset.values_list("id", flat=True)),
        )
        return None


def discover_eep_program_for_homes(queryset):
    """
    Returns the program if is the same for all homes in queryset.  If more than one program is in
    use, the return value is None, and the conditions for calling this utility should be modified
    by the frontend to get a better return result.

    If no programs appear to be specified by the queryset, None is returned.
    """
    from axis.eep_program.models import EEPProgram
    from axis.home.models import EEPProgramHomeStatus
    from .models import SampleSetHomeStatus

    if queryset.model is SampleSetHomeStatus:
        prefix = "home_status__"
    elif queryset.model is EEPProgramHomeStatus:
        prefix = ""
    else:
        prefix = ""

    program_id_list = queryset.values_list(prefix + "eep_program__id", flat=True)
    programs = EEPProgram.objects.filter(id__in=program_id_list)
    try:
        return programs.get()
    except EEPProgram.MultipleObjectsReturned:
        log.info(
            "Homes in queryset use more than one program: %r [%d ids=%r]",
            programs,
            len(program_id_list),
            list(program_id_list),
        )
        return False
    except EEPProgram.DoesNotExist:
        log.warning(
            "No programs specified by homes! [%d ids=%r]",
            len(queryset),
            list(queryset.values_list("id", flat=True)),
        )
        return None


def discover_subdivision_for_homes(sshomestatus_queryset):
    """
    Returns the subdivision if is the same for all homes in queryset. If more than one subdivision
    is in use, the return value is False, and the conditions for calling this utility should be
    modified by the frontend to get a better return result.

    If no subdivisions appear to be specified by the queryset, None is returned.
    """
    from axis.subdivision.models import Subdivision

    subdivision_id_list = sshomestatus_queryset.values_list(
        "home_status__home__subdivision__id", flat=True
    )
    subdivisions = Subdivision.objects.filter(id__in=subdivision_id_list)
    try:
        return subdivisions.get()
    except Subdivision.MultipleObjectsReturned:
        log.info(
            "Homes in queryset use more than one subdivision: %r [%d ids=%r]",
            ["{}".format(x) for x in subdivisions],
            len(subdivision_id_list),
            list(subdivision_id_list),
        )
        return False
    except Subdivision.DoesNotExist:
        log.info(
            "No homes in queryset specify a subdivision. [%d ids=%r]",
            len(sshomestatus_queryset),
            list(sshomestatus_queryset.values_list("id", flat=True)),
        )
        return None


def get_used_metros(sshomestatus_queryset, ids_only=False):
    metro_ids = list(
        sshomestatus_queryset.values_list(
            "home_status__home__subdivision__metro__id", flat=True
        ).distinct()
    )
    if ids_only:
        return metro_ids
    from axis.geographic.models import Metro

    return Metro.objects.filter(id__in=metro_ids)


def can_company_sample(
    company, builder=None, provider=None, program=None, metro_check=False, report_only=None
):
    from .models import SamplingProviderApproval

    issues = []

    if company.company_type == "rater":
        if not company.is_sample_eligible:
            issues.append(strings.INVALID_GLOBAL.format(company=company))
    elif company.company_type == "provider":
        if not company.is_sample_eligible:
            issues.append(strings.INVALID_GLOBAL.format(company=company))
        provider = company

    if company.company_type not in ["rater", "provider"]:
        issues.append(strings.INVALID_SAMPLING_COMPANY_TYPE)

    if company.company_type == "rater" and provider:
        try:
            SamplingProviderApproval.objects.get(
                provider_id=provider.id, target=company, sampling_approved=True
            )
        except SamplingProviderApproval.DoesNotExist:
            issues.append(
                strings.COMPANY_NOT_APPROVED_BY_PROVIDER.format(company=company, provider=provider)
            )

    if builder:
        try:
            SamplingProviderApproval.objects.get(
                provider_id=provider.id, target=company, sampling_approved=True
            )
        except SamplingProviderApproval.DoesNotExist:
            issues.append(
                strings.COMPANY_NOT_APPROVED_BY_PROVIDER.format(company=company, provider=provider)
            )

    if program:
        if not metro_check:
            if not program.allow_sampling:
                issues.append(strings.PROGRAM_DOES_NOT_ALLOW_SAMPLING.format(program=program))
        else:
            if not program.allow_metro_sampling:
                issues.append(strings.PROGRAM_DOES_NOT_ALLOW_METRO_SAMPLING.format(program=program))
        if program.require_resnet_sampling_provider:
            if not provider:
                raise LookupError(
                    "You must provide a provider to check for resnet sampling " "requirements"
                )
            try:
                RESNETCompany.objects.get(company_id=provider, is_sampling_provider=True)
            except RESNETCompany.DoesNotExist:
                issues.append(
                    strings.PROGRAM_RESNET_SAMPLING_PROVIDER.format(
                        program=program, provider=provider
                    )
                )

    if report_only:
        if issues:
            return False, issues
        return True

    return False if len(issues) else True


# Bulk uploading utilities
SAMPLING_RATING_TYPE_NORMALIZATION_MAP = {
    # is_test_home=True, legacy rating_type=2
    "Sampled Test House": [
        "test",
        "sample test",
        "sample test home",
        "sample test house",
        "sampled test home",
        "sampled test house",
    ],
    # is_test_home=False, legacy rating_type=3
    "Sampled House": [
        "sampled",
        "sampled home",
        "sampled house",
        "sample house",
        "sample home",
    ],
}


def normalize_sampling_rating_type(name):
    if not name:
        return None
    name = name.lower()
    for normalized, choices in SAMPLING_RATING_TYPE_NORMALIZATION_MAP.items():
        if name in choices:
            return normalized
    return None


def normalize_sampling_rating_type_as_boolean(name):
    return normalize_sampling_rating_type(name) == "Sampled Test House"


SamplingDetailTuple = namedtuple(
    "SamplingDetailTuple",
    [
        "use_sampling",  # Indicates that the data intends to use a sampleset
        "sampleset",  # The object reference, if it already exists in the db
        "repr",  # The repr() of 'sampleset', or the name if it's not yet created
        "url",  # If available, sampleset.get_absolute_url()
        "given_name",  # The name given by the data, which might be a uuid or an altname
        "name_type",  # 'uuid' or 'alt_name', depending on what 'given_name' looks like
        "is_test_home",  # Boolean value that represents a rating_type==2
    ],
)


def inspect_for_sampleset(**data):
    """
    Bulk uploader utility for analyzing a blob of variables about a row item.  Returns a namedtuple
    of settings we know about the input data.

    If something is specified in the data but doesn't yet exist in the database (e.g., an altname
    is provided for a sampleset that isn't created yet) we will indicate that sampling is desired
    but the actual SampleSet object reference will be None.  The bulk uploader will have to take
    appropriate action when it's ready to finally create new objects.
    """
    from .models import SampleSet

    orig_name = data.get("sample_set", None)
    sampleset_name = data.get("sample_set", None)
    if sampleset_name:
        sampleset_name = str(sampleset_name).strip().split(" ", 1)[0]
    else:
        return SamplingDetailTuple(False, None, None, None, None, None, None)

    lookup_type = "uuid" if UUIDMATCH.match(sampleset_name) else "alt_name"
    use_sampling = True

    log.debug("Inspecting %s (%s) by %s", sampleset_name, orig_name, lookup_type)

    try:
        sampleset = SampleSet.objects.filter_by_company(data["company"]).get(
            **{
                # Looks up by 'uuid' or 'alt_name', whichever we parsed it as
                lookup_type: sampleset_name,
            }
        )
    except SampleSet.DoesNotExist:
        sampleset = None
        url = None
        sampleset_str = sampleset_name
    else:
        sampleset_str = str(sampleset)
        url = sampleset.get_absolute_url()

        # TODO: More checks, as per the old sampling.SampleSetManager.verify_for_user

    is_test_home = False
    questions = data.get("questions", {})
    questions = questions if questions else {}
    for question, answers in questions.items():
        if len(answers):
            is_test_home = True
            break
    else:
        log.debug("No questions found but..  it's identified as %s" % data.get("rating_type"))
        try:
            is_test_home = "test" in data.get("rating_type", "").lower()
        except AttributeError:
            is_test_home = False

    log.debug(
        "Inspected %s sampleset %s (%s) by %s",
        "Test" if is_test_home else "Sampled",
        sampleset_name,
        orig_name,
        lookup_type,
    )

    return SamplingDetailTuple(
        **{
            "use_sampling": use_sampling,
            "sampleset": sampleset,
            "repr": sampleset_str,
            "url": url,
            "given_name": sampleset_name,
            "name_type": lookup_type,
            "is_test_home": is_test_home,
        }
    )


def validate_bulk_sampleset_configuration(sampleset_config):
    """Receives one sampleset config at a time and returns messages about the setup."""

    report = {
        "error": [],
        "info": [],
        "warning": [],
        "debug": [],
    }

    # FIXME: should we check the existance of multiple certification dates for this sampleset.
    # do we want this to stop the process.

    sampleset = sampleset_config["sampleset"]
    if sampleset:
        current_items = sampleset.samplesethomestatus_set.current()
        new_homes = Counter(sampleset_config["homes"].values())[None]
        total_requested_homes = current_items.count() + new_homes
        report["debug"].append(
            "{} Existing Homes + {} New Homes = {}".format(
                *[
                    current_items.count(),
                    new_homes,
                    total_requested_homes,
                ]
            )
        )
        if total_requested_homes > settings.SAMPLING_MAX_SIZE:
            report["error"].append(
                strings.SAMPLESET_EXCEEDED_IF_CERTIFICATION_PROCESSES.format(
                    sampleset=sampleset_config["href"]
                )
            )

    # These booleans represent the is_test_home data compiled for a sampleset.
    if True not in sampleset_config["types"]:
        if (
            sampleset
            and not sampleset.samplesethomestatus_set.current().filter(is_test_home=True).exists()
        ):
            # sampleset truly has no test homes
            report["warning"].append(
                strings.NO_TEST_HOMES.format(sampleset=sampleset_config["href"])
            )
        else:
            # no test homes provided for this sampleset in this upload.
            report["debug"].append(
                strings.ONLY_SAMPLED_HOMES.format(sampleset=sampleset_config["href"])
            )

    if False not in sampleset_config["types"]:
        if (
            sampleset
            and not sampleset.samplesethomestatus_set.current().filter(is_test_home=False).exists()
        ):
            # sampleset truly has no sampled homes
            report["debug"].append(
                strings.NO_SAMPLED_HOMES.format(sampleset=sampleset_config["href"])
            )
        else:
            # no sampled homes provided for this sampleset in this upload.
            report["debug"].append(
                strings.ONLY_TEST_HOMES.format(sampleset=sampleset_config["href"])
            )

    return report


def autocorrect_multiple_samplesets(home_status_id):
    """(EXPIRIMENTAL) It removes duplicate sampleset statuses based on last modified date"""
    # Work through this and remove all but the latest
    from axis.home.models import EEPProgramHomeStatus

    stat = EEPProgramHomeStatus.objects.get(id=home_status_id)
    keeper = None
    if stat.samplesethomestatus_set.current().select_related("sampleset").count() == 1:
        return "Nothing to do"
    for samplesetstatus_set in stat.samplesethomestatus_set.current().select_related("sampleset"):
        ss_status = samplesetstatus_set.sampleset.samplesethomestatus_set.filter(
            home_status_id=home_status_id
        ).get()
        if keeper is None or keeper.modified_date > ss_status.modified_date:
            keeper = ss_status
            log.info("Keeping %s" % keeper.modified_date)
    for samplesetstatus_set in stat.samplesethomestatus_set.current().select_related("sampleset"):
        ss_status = samplesetstatus_set.sampleset.samplesethomestatus_set.filter(
            home_status_id=home_status_id
        ).get()
        if ss_status != keeper:
            log.warning(
                "Removing %s from %s %s" % (ss_status.id, ss_status, samplesetstatus_set.sampleset)
            )
            samplesetstatus_set.sampleset.samplesethomestatus_set.filter(
                home_status_id=home_status_id
            ).delete()
