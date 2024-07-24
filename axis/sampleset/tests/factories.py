""" SampleSet factories for tests. """


import logging
import random
import re

from django.conf import settings
from django.utils.timezone import now
from axis.core.tests.factories import provider_admin_factory

from axis.core.tests.utils import subdict_from_prefix
from axis.core.utils import random_sequence
from axis.home.models import EEPProgramHomeStatus
from axis.home.tasks import update_home_states, update_home_stats, certify_sampleset
from axis.home.tests.factories import (
    certified_home_with_checklist_factory,
    certified_custom_home_with_checklist_factory,
    _certify_stat,
)
from ..models import SampleSet

__author__ = "Autumn Valenta"
__date__ = "07-11-14 12:20 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def empty_sampleset_factory(**kwargs):
    kwrgs = {"uuid": kwargs.pop("uuid", None), "alt_name": kwargs.pop("alt_name", None)}

    owner = kwargs.pop("owner", None)
    if not owner:
        from axis.company.tests.factories import rater_organization_factory

        owner = rater_organization_factory(**subdict_from_prefix(kwargs, "owner__"))

    sampleset, _ = SampleSet.objects.get_or_create(
        owner=owner, alt_name=random_sequence(4), defaults=kwrgs
    )
    return sampleset


def sampleset_with_subdivision_homes_factory(**kwargs):
    num_homes = kwargs.pop("num_homes", int(settings.SAMPLING_MAX_SIZE / 2))
    num_test_homes = kwargs.pop("num_test_homes", max((int(num_homes / 3), 1)))
    pct_complete = kwargs.pop("pct_complete", None)
    revision = kwargs.pop("revision", 0)

    eep_program = kwargs.pop("eep_program", None)
    eep_programs = kwargs.pop("eep_programs", None)
    subdivision = kwargs.pop("subdivision", kwargs.pop("home__subdivision", None))
    floorplan = kwargs.pop("floorplan", None)
    certify = kwargs.pop("certify", False)
    certifier = kwargs.pop("certifier", None)

    kwargs["is_metro_sampled"] = False
    sampleset = empty_sampleset_factory(**kwargs)

    if not eep_program and not eep_programs:
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory

        eep_program = basic_eep_program_checklist_factory(
            **subdict_from_prefix(kwargs, "eep_program__", extra={"no_close_dates": True})
        )

    if not eep_programs:
        eep_programs = [eep_program]

    if not subdivision:
        from axis.subdivision.tests.factories import subdivision_factory

        subdivision = subdivision_factory(**subdict_from_prefix(kwargs, "subdivision__"))

    # Add test homes
    from axis.home.tests.factories import eep_program_home_status_factory

    home_kwargs = subdict_from_prefix(kwargs, "home__", remove_prefix=False)
    home_kwargs.update({"home__subdivision": subdivision})
    home_kwargs.update(**subdict_from_prefix(kwargs, "eepprogramhomestatus__"))
    _test_cnt, q_ids, statuses = 0, [], []
    for i in range(num_homes):
        is_test_home = _test_cnt < num_test_homes
        program = random.choice(eep_programs)
        if pct_complete and is_test_home:
            _pct = float(pct_complete) / float(num_test_homes)
            # If we are on the last home ensure that we hit the mark.
            if _test_cnt + 1 == num_test_homes:
                _pct = pct_complete
            status = certified_home_with_checklist_factory(
                certify=False,
                eep_program=program,
                floorplan=floorplan,
                pct_complete=_pct,
                exclude_question_ids=q_ids,
                **home_kwargs,
            )
            _q_ids = list(status.home.answer_set.values_list("question", flat=True))
            if i + 1 == num_test_homes:
                q_ids += list(set(_q_ids + q_ids))
            else:
                q_ids += list(set(_q_ids + q_ids))[:-1]  # Allow a bit of overlapping answers..
            _test_cnt += 1
            statuses.append(status)
        else:
            status = eep_program_home_status_factory(
                eep_program=program, floorplan=floorplan, **home_kwargs
            )
            statuses.append(status)

        sampleset.add_home_status(status, is_test_home=is_test_home, revision=0)

    if revision:
        for r in range(revision):
            sampleset.advance()

        # Separate the answers across as many revisions as was originally requested.
        for sshs in sampleset.samplesethomestatus_set.filter(revision=0):
            answers = sshs.answers.all()
            num_answers = len(answers)
            for r in range(revision):
                sshs_for_r = sampleset.samplesethomestatus_set.get(
                    home_status=sshs.home_status, revision=r
                )
                start_i = int(r * (num_answers / revision))
                end_i = int((r + 1) * (num_answers / revision))
                if r + 1 == revision:
                    end_i = num_answers

                if not sshs.is_test_home:
                    # Split up the answers across the revisions
                    to_add = answers[start_i:end_i]
                    to_remove = answers[:start_i] + answers[end_i:]
                    sshs_for_r.answers.add(*to_add)
                    sshs_for_r.answers.remove(*to_remove)

    update_home_states(eepprogramhomestatus_id=statuses[0].id)
    update_home_stats(eepprogramhomestatus_id=statuses[0].id)

    [x.validate_references() for x in statuses]

    if certify and pct_complete > 99.9:
        if not certifier:
            stat = EEPProgramHomeStatus.objects.get(id=statuses[0].id)
            if (
                not stat.company.users.filter(is_company_admin=True)
                and stat.company.company_type == "provider"
            ):
                certifier = provider_admin_factory(company=stat.company)
            else:
                certifier = stat.company.users.filter(is_company_admin=True)[0]

        certify_sampleset(certifier, sampleset, kwargs.get("certification_date", now()))
    return sampleset


def sampleset_with_metro_homes_factory(**kwargs):
    num_homes = kwargs.pop("num_homes", int(settings.SAMPLING_MAX_SIZE / 2))
    num_test_homes = kwargs.pop("num_test_homes", max((int(num_homes / 3), 1)))
    pct_complete = kwargs.pop("pct_complete", None)
    revision = kwargs.pop("revision", 0)

    eep_program = kwargs.pop("eep_program", None)
    city = kwargs.pop("city", None)
    metro = kwargs.pop("metro", None)

    kwargs["is_metro_sampled"] = True
    sampleset = empty_sampleset_factory(**kwargs)

    if not eep_program:
        from axis.eep_program.tests.factories import basic_eep_program_checklist_factory

        eep_program = basic_eep_program_checklist_factory(
            **subdict_from_prefix(kwargs, "eep_program__", extra={"no_close_dates": True})
        )

    if not metro:
        from axis.geographic.tests.factories import metro_factory

        metro = metro_factory(**subdict_from_prefix(kwargs, "metro__"))

    if not city:
        from axis.geographic.tests.factories import city_factory

        city = city_factory(**subdict_from_prefix(kwargs, "city__", extra={"metro": metro}))

    # Add test homes
    from axis.home.tests.factories import eep_program_custom_home_status_factory

    home_kwargs = subdict_from_prefix(kwargs, "home__", remove_prefix=False)
    home_kwargs.update({"home__city": city})
    home_kwargs.update(**subdict_from_prefix(kwargs, "eepprogramhomestatus__"))
    _test_cnt, q_ids = 0, []
    for i in range(num_homes):
        is_test_home = _test_cnt < num_test_homes
        if pct_complete and is_test_home:
            status = certified_custom_home_with_checklist_factory(
                certify=False,
                eep_program=eep_program,
                pct_complete=float(pct_complete) / float(num_test_homes),
                exclude_question_ids=q_ids,
                **home_kwargs,
            )
            _q_ids = list(status.home.answer_set.values_list("question", flat=True))
            if i + 1 == num_test_homes:
                q_ids += list(set(_q_ids + q_ids))
            else:
                q_ids += list(set(_q_ids + q_ids))[:-1]  # Allow a bit of overlapping answers..
            _test_cnt += 1
        else:
            status = eep_program_custom_home_status_factory(eep_program=eep_program, **home_kwargs)
        sampleset.add_home_status(status, is_test_home=is_test_home, revision=0)

    if revision:
        for r in range(revision):
            sampleset.advance()

        # Separate the answers across as many revisions as was originally requested.
        for sshs in sampleset.samplesethomestatus_set.filter(revision=0):
            answers = sshs.answers.all()
            num_answers = len(answers)
            for r in range(revision):
                sshs_for_r = sampleset.samplesethomestatus_set.get(
                    home_status=sshs.home_status, revision=r
                )
                start_i = r * (num_answers / revision)
                end_i = (r + 1) * (num_answers / revision)
                if r + 1 == revision:
                    end_i = num_answers

                if not sshs.is_test_home:
                    # Split up the answers across the revisions
                    to_add = answers[start_i:end_i]
                    to_remove = answers[:start_i] + answers[end_i:]
                    sshs_for_r.answers.add(*to_add)
                    sshs_for_r.answers.remove(*to_remove)

    return sampleset
