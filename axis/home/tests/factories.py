"""factory.py: Django home"""

import logging
import random
import re

from django.apps import apps
from django.core.files import File
from django.utils.timezone import now

from axis.checklist.utils import get_random_answer_for_question
from axis.core.utils import random_sequence, random_latitude, random_longitude
from axis.core.tests.factories import rater_admin_factory, provider_admin_factory
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import climate_zone_factory, city_factory
from axis.home.models import Home, EEPProgramHomeStatus, HomePhoto
from axis.home.tasks import certify_single_home, update_home_states
from axis.relationship.models import Relationship
from axis.relationship.utils import create_or_update_spanning_relationships

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def warn_on_user_kwarg(func):
    def check_user(*args, **kwargs):
        if "user" in kwargs:
            log.error(
                "Keyword argument `user` should not longer be passed to certifying factories. "
                "Please specify explicity `certifying_user` and `answer_user`"
            )
        return func(*args, **kwargs)

    return check_user


def custom_home_factory(state=None, **kwargs):
    """A custom home factory.  get_or_create based on the field 'lot_number'."""
    from axis.company.tests.factories import builder_organization_factory

    city = kwargs.pop("city", None)
    county = kwargs.pop("county", None)
    metro = kwargs.pop("metro", None)
    climate_zone = kwargs.pop("climate_zone", None)
    builder_org = kwargs.pop("builder_org", None)
    geocode = kwargs.pop("geocode", False)
    subdivision = kwargs.pop("subdivision", None)

    kwrgs = {
        "lot_number": str(random.randint(1000000000, 9999999999)),
        "street_line1": f"{random.randint(1, 999)} W. Main St",
        "street_line2": f"# {random.randint(1, 999)}",
        "latitude": random_latitude(),
        "longitude": random_longitude(),
        "zipcode": str(random.randint(10000, 99999)),
        "confirmed_address": False,
        "is_custom_home": True,
        "is_multi_family": random.choice([False] * 5 + [True]),
        "alt_name": random_sequence(4),
        "subdivision": subdivision,
    }
    if geocode and "street_line1" not in kwargs:
        raise AttributeError("Need a real street address")

    if not city:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k in ["county", "state"]:
                c_kwrgs[k] = v
            if k.startswith("city__"):
                c_kwrgs[re.sub(r"city__", "", k)] = kwargs.pop(k)
        if c_kwrgs:
            raise AttributeError("Unexeptec")
        kwrgs["city"] = city_factory(**c_kwrgs)
        if not county:
            kwrgs["county"] = kwrgs["city"].county
        if not state:
            kwrgs["state"] = kwrgs["city"].county.state
        if not metro:
            kwrgs["metro"] = kwrgs["city"].county.metro
        if not climate_zone:
            cz = kwrgs["city"].county.climate_zone
            if not cz:
                cz = climate_zone_factory()
                county = kwrgs["city"].county
                county.climate_zone = cz
                cz.save()
            kwrgs["climate_zone"] = cz
    else:
        kwrgs["city"] = city
    if not county and not kwrgs.get("county"):
        kwrgs["county"] = kwrgs["city"].county
    if kwrgs["county"]:
        if not metro and not kwrgs.get("metro"):
            kwrgs["metro"] = kwrgs["county"].metro
        if not climate_zone and not kwrgs.get("climate_zone"):
            cz = kwrgs["city"].county.climate_zone
            if not cz:
                cz = climate_zone_factory()
            kwrgs["climate_zone"] = cz

    if subdivision:
        builder_org = subdivision.builder_org
    elif builder_org is None:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("builder_org__"):
                c_kwrgs[re.sub(r"builder_org__", "", k)] = kwargs.pop(k)
        if "city" not in c_kwrgs:
            c_kwrgs["city"] = city
        builder_org = builder_organization_factory(**c_kwrgs)

    kwrgs.update(kwargs)

    if geocode:
        matches = Geocode.objects.get_matches(raw_address=None, **kwrgs)
        if len(matches) == 1:
            match = matches[0]
            geocoded_data = match.get_normalized_fields()
            values = [
                "street_line1",
                "street_line2",
                "state",
                "zipcode",
                "confirmed_address",
                "latitude",
                "longitude",
            ]
            kwrgs.update({k: geocoded_data.get(k, None) for k in values})
            kwrgs["geocode_response"] = match
            kwrgs["city"] = geocoded_data.get("city") if geocoded_data.get("city") else None
            kwrgs["county"] = geocoded_data.get("county") if geocoded_data.get("county") else None
            kwrgs["metro"] = geocoded_data.get("metro") if geocoded_data.get("metro") else None
        else:
            log.warning("Fixture producing more than one geocoded address")

    home, create = Home.objects.get_or_create(lot_number=kwrgs.pop("lot_number"), defaults=kwrgs)
    if create and builder_org:
        Relationship.objects.validate_or_create_relations_to_entity(home, builder_org)

    return home


def home_factory(**kwargs):
    """A custom home factory.  get_or_create based on the field 'lot_number'."""
    from axis.subdivision.tests.factories import subdivision_factory

    subdivision = kwargs.pop("subdivision", None)
    if not subdivision:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("subdivision__"):
                c_kwrgs[re.sub(r"subdivision__", "", k)] = kwargs.pop(k)
        if "city" in kwargs and "city" not in c_kwrgs:
            c_kwrgs["city"] = kwargs["city"]
        kwargs["subdivision"] = subdivision_factory(**c_kwrgs)
    else:
        kwargs["subdivision"] = subdivision
    return custom_home_factory(**kwargs)


# Core


def eep_program_custom_home_status_factory(**kwargs) -> EEPProgramHomeStatus:
    """A custom home status factory.  get_or_create based on the field 'lot_number'."""
    from axis.company.tests.factories import provider_organization_factory
    from axis.eep_program.tests.factories import basic_eep_program_factory
    from axis.floorplan.tests.factories import basic_custom_home_floorplan_factory

    customer_hirl_app = apps.get_app_config("customer_hirl")

    home = kwargs.pop("home", None)
    eep_program = kwargs.pop("eep_program", None)
    company = kwargs.pop("company", None)
    floorplan = kwargs.pop("floorplan", None)
    skip_floorplan = kwargs.pop("skip_floorplan", False)
    field_inspectors = kwargs.pop("field_inspectors", None)

    if not home:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("home__"):
                c_kwrgs[re.sub(r"home__", "", k)] = kwargs.pop(k)
        kwargs["home"] = custom_home_factory(**c_kwrgs)
    else:
        kwargs["home"] = home

    if not eep_program:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("eep_program__"):
                c_kwrgs[re.sub(r"eep_program__", "", k)] = kwargs.pop(k)
        kwargs["eep_program"] = basic_eep_program_factory(**c_kwrgs)
        eep_program = kwargs["eep_program"]
    else:
        kwargs["eep_program"] = eep_program

    if not company:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = provider_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company

    if not floorplan and not skip_floorplan:
        c_kwrgs = {"owner": kwargs["company"]}
        for k, v in list(kwargs.items()):
            if k.startswith("floorplan__"):
                c_kwrgs[re.sub(r"floorplan__", "", k)] = kwargs.pop(k)
        kwargs["floorplan"] = basic_custom_home_floorplan_factory(**c_kwrgs)
    else:
        kwargs["floorplan"] = floorplan

    user_pool = []
    if company and company.users.count():
        user_pool = list(company.users.all())
        if user_pool and "rater_of_record" not in kwargs:
            kwargs["rater_of_record"] = random.choice(user_pool)
        if user_pool and eep_program and eep_program.owner.slug == customer_hirl_app.CUSTOMER_SLUG:
            if "customer_hirl_rough_verifier" not in kwargs:
                kwargs["customer_hirl_rough_verifier"] = random.choice(user_pool)
            if "customer_hirl_final_verifier" not in kwargs:
                kwargs["customer_hirl_final_verifier"] = random.choice(user_pool)

    stat, create = EEPProgramHomeStatus.objects.get_or_create(**kwargs)
    stat.floorplans.add(kwargs.get("floorplan"))
    if create:
        comps = [stat.home.get_builder(), stat.eep_program.owner, stat.company]
        Relationship.objects.create_mutual_relationships(*comps)
        for comp in comps:
            Relationship.objects.validate_or_create_relations_to_entity(stat.home, comp)
        create_or_update_spanning_relationships(stat.company, stat.home)
        update_home_states(eepprogramhomestatus_id=stat.id)
        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        if user_pool and field_inspectors is None:
            field_inspectors = [user_pool[i] for i in range(random.randrange(0, len(user_pool)))]
        if field_inspectors:
            for f in field_inspectors:
                stat.field_inspectors.add(f)

    if stat.eep_program and stat.eep_program.collection_request:
        stat.set_collection_from_program()
    return stat


# Core with subdivsiion


def eep_program_home_status_factory(**kwargs):
    """A custom home status factory.  get_or_create based on the field 'lot_number'."""
    from axis.company.tests.factories import provider_organization_factory
    from axis.floorplan.tests.factories import floorplan_factory

    home = kwargs.pop("home", None)
    floorplan = kwargs.pop("floorplan", None)
    company = kwargs.pop("company", None)
    if not home:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("home__"):
                c_kwrgs[re.sub(r"home__", "", k)] = kwargs.pop(k)
        kwargs["home"] = home_factory(**c_kwrgs)
    else:
        kwargs["home"] = home

    if not company:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("company__"):
                c_kwrgs[re.sub(r"company__", "", k)] = kwargs.pop(k)
        kwargs["company"] = provider_organization_factory(**c_kwrgs)
    else:
        kwargs["company"] = company

    if not floorplan:
        c_kwrgs = {"owner": kwargs["company"]}
        if kwargs["home"].subdivision:
            c_kwrgs["subdivision"] = kwargs["home"].subdivision
        for k, v in list(kwargs.items()):
            if k.startswith("floorplan__"):
                c_kwrgs[re.sub(r"floorplan__", "", k)] = kwargs.pop(k)
        kwargs["floorplan"] = floorplan_factory(**c_kwrgs)
    else:
        kwargs["floorplan"] = floorplan
    return eep_program_custom_home_status_factory(**kwargs)


# Swap out the eep with a checklist based one.


def eep_program_checklist_custom_home_status_factory(**kwargs):
    from axis.eep_program.tests.factories import basic_eep_program_checklist_factory

    eep_program = kwargs.pop("eep_program", None)
    if not eep_program:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("eep_program__"):
                c_kwrgs[re.sub(r"eep_program__", "", k)] = kwargs.pop(k)
        kwargs["eep_program"] = basic_eep_program_checklist_factory(**c_kwrgs)
    else:
        kwargs["eep_program"] = eep_program

    return eep_program_custom_home_status_factory(**kwargs)


def eep_program_checklist_home_status_factory(**kwargs):
    from axis.eep_program.tests.factories import basic_eep_program_checklist_factory

    eep_program = kwargs.pop("eep_program", None)
    if not eep_program:
        c_kwrgs = {"checklist_count": 2}
        for k, v in list(kwargs.items()):
            if k.startswith("eep_program__"):
                c_kwrgs[re.sub(r"eep_program__", "", k)] = kwargs.pop(k)
        kwargs["eep_program"] = basic_eep_program_checklist_factory(**c_kwrgs)

    else:
        kwargs["eep_program"] = eep_program

    return eep_program_home_status_factory(**kwargs)


# Now let's identify the real ones.


def _certify_stat(
    stat,
    user,
    pct=100,
    certify=True,
    exclude_question_ids=None,
    answer_user=None,
):
    from axis.checklist.models import Answer
    from axis.checklist.tests.factories import answer_factory
    from axis.scheduling.models import ConstructionStage

    ConstructionStage.objects.get_or_create(name="Completed", is_public=True, order=100)

    answer_user = answer_user or user

    ex_q_ids = exclude_question_ids if exclude_question_ids else []

    questions = stat.eep_program.get_checklist_question_set().exclude(id__in=ex_q_ids)
    question_count = float(questions.count())
    if exclude_question_ids:
        log.warning("The pct may be lower b/c you excluded %s questions", len(ex_q_ids))

    pct = float(pct)
    answers = []
    for idx, question in enumerate(questions):
        # Always round down unless we are looking for 100%
        if pct < 99.9 and idx < question_count and ((idx + 1) / question_count) * 100 >= pct:
            break
        AnsCom = get_random_answer_for_question(
            question, pct_error=0, seed=f"{random_sequence(4)} {idx}"
        )
        answers.append(
            answer_factory(
                question=question,
                home=stat.home,
                user=answer_user,
                answer=AnsCom.answer,
                comment=AnsCom.comment,
                in_bulk=True,
            )
        )

    stat.pct_complete = pct
    stat.save()
    Answer.objects.bulk_create(answers)

    stat = EEPProgramHomeStatus.objects.get(id=stat.id)
    stat.validate_references()

    issues = stat.report_eligibility_for_certification()
    if stat.pct_complete >= 99.9 and len(issues) and certify:
        raise ValueError("EEP not eligible for certification!!: {}".format(",".join(issues)))
    if pct >= 99.9 and certify:
        stat.certification_date = now()
        stat.save()
        certify_single_home(user, stat, stat.certification_date)
    else:
        update_home_states(eepprogramhomestatus_id=stat.id, user_id=user.id)
    stat = EEPProgramHomeStatus.objects.get(id=stat.id)
    return stat


### ---  Targets ---


def home_with_basic_eep_factory(**kwargs):
    stat = eep_program_home_status_factory(**kwargs)
    return stat.home


def custom_home_with_basic_eep_factory_and_remrate(**kwargs):
    from axis.floorplan.tests.factories import floorplan_with_remrate_factory

    company = kwargs.get("company")
    _fp_kwargs = {}
    if company:
        _fp_kwargs["owner"] = company

    floorplan = floorplan_with_remrate_factory(**_fp_kwargs)
    kwargs.update({"floorplan": floorplan, "company": floorplan.owner})
    stat = eep_program_custom_home_status_factory(**kwargs)
    return stat.home


@warn_on_user_kwarg
def certified_custom_home_with_basic_eep_factory_and_remrate(certify=True, **kwargs):
    certifying_user = kwargs.pop("certifying_user", False)
    answer_user = kwargs.pop("answer_user", False)

    home = custom_home_with_basic_eep_factory_and_remrate(**kwargs)
    stat = home.homestatuses.get()

    certifying_user, answer_user = get_certifying_and_answer_user(
        stat, certifying_user, answer_user
    )

    return _certify_stat(
        stat=stat,
        user=certifying_user,
        answer_user=answer_user,
        certify=certify,
    )


def custom_home_with_basic_eep_factory(**kwargs):
    stat = eep_program_custom_home_status_factory(**kwargs)
    return stat.home


@warn_on_user_kwarg
def certified_home_with_basic_eep_factory(certify=True, **kwargs):
    certifying_user = kwargs.pop("certifying_user", False)
    answer_user = kwargs.pop("answer_user", False)

    stat = eep_program_home_status_factory(**kwargs)

    certifying_user, answer_user = get_certifying_and_answer_user(
        stat, certifying_user, answer_user
    )

    return _certify_stat(
        stat=stat,
        user=certifying_user,
        answer_user=answer_user,
        certify=certify,
    )


@warn_on_user_kwarg
def certified_custom_home_with_basic_eep_factory(certify=True, **kwargs):
    certifying_user = kwargs.pop("certifying_user", False)
    answer_user = kwargs.pop("answer_user", False)

    stat = eep_program_custom_home_status_factory(**kwargs)

    certifying_user, answer_user = get_certifying_and_answer_user(
        stat, certifying_user, answer_user
    )
    return _certify_stat(
        stat=stat,
        user=certifying_user,
        answer_user=answer_user,
        certify=certify,
    )


@warn_on_user_kwarg
def certified_home_with_checklist_factory(
    certify=True, pct_complete=100, exclude_question_ids=None, **kwargs
):
    certifying_user = kwargs.pop("certifying_user", False)
    answer_user = kwargs.pop("answer_user", False)

    stat = eep_program_checklist_home_status_factory(**kwargs)

    certifying_user, answer_user = get_certifying_and_answer_user(
        stat, certifying_user, answer_user
    )

    return _certify_stat(
        stat=stat,
        user=certifying_user,
        answer_user=answer_user,
        pct=pct_complete,
        certify=certify,
        exclude_question_ids=exclude_question_ids,
    )


@warn_on_user_kwarg
def certified_custom_home_with_checklist_factory(
    certify=True, pct_complete=100, exclude_question_ids=None, **kwargs
):
    certifying_user = kwargs.pop("certifying_user", False)
    answer_user = kwargs.pop("answer_user", False)

    stat = eep_program_checklist_custom_home_status_factory(**kwargs)

    certifying_user, answer_user = get_certifying_and_answer_user(
        stat, certifying_user, answer_user
    )

    return _certify_stat(
        stat=stat,
        user=certifying_user,
        answer_user=answer_user,
        pct=pct_complete,
        certify=certify,
        exclude_question_ids=exclude_question_ids,
    )


def get_certifying_and_answer_user(stat, certifying_user=None, answer_user=None, **kwargs):
    if not certifying_user:
        if stat.eep_program.is_qa_program:
            raise NotImplementedError("Not yet supported")

        if stat.company.company_type == "provider":
            if not stat.company.users.filter(is_company_admin=True).count():
                certifying_user = provider_admin_factory(company=stat.company, **kwargs)
            else:
                certifying_user = random.choice(
                    list(stat.company.users.filter(is_company_admin=True))
                )
        else:
            certifying_user = provider_admin_factory(company__city=stat.home.city)

    if not answer_user:
        if not stat.company.users.count():
            factory = (
                rater_admin_factory
                if stat.company.company_type == "rater"
                else provider_admin_factory
            )
            answer_user = factory(company=stat.company, **kwargs)
        else:
            answer_user = random.choice(list(stat.company.users.all()))

    from axis.relationship.models import Relationship

    Relationship.objects.create_mutual_relationships(certifying_user.company, answer_user.company)

    return certifying_user, answer_user


def home_photo_factory(**kwargs):
    home = kwargs.pop("home", False)

    if not home:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("home__"):
                c_kwrgs[re.sub(r"home__", "", k)] = kwargs.pop(k)
        kwargs["home"] = custom_home_factory(**c_kwrgs)
    else:
        kwargs["home"] = home

    with open(__file__) as f:
        kwrgs = {"title": random_sequence(4), "is_primary": False, "file": File(f, name="test.jpg")}

        kwrgs.update(kwargs)
        home_photo = HomePhoto.objects.create(**kwrgs)
    return home_photo
