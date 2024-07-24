"""tasks.py: Django resnet"""


from celery.utils.log import get_task_logger

from celery import shared_task
from django.contrib.auth import get_user_model

from .models import RESNETCompany, RESNETContact
from .data_scraper import (
    RESENTProvider,
    RESNETSamplingProvider,
    RESNETTrainingProvider,
    RESNETWaterSenseProvider,
)

__author__ = "Steven Klass"
__date__ = "7/25/14 4:41 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = get_task_logger(__name__)
User = get_user_model()


@shared_task
def submit_home_status_to_registry(home_status_id, provider_id):
    """Submit a home to the registry"""

    from axis.resnet.utils import submit_home_status_to_registry as submit_home
    from axis.home.models import EEPProgramHomeStatus

    home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
    provider = User.objects.get(id=provider_id)
    submit_home(home_status, provider)


@shared_task  # noqa: MC0001
def update_resnet_database(**kwargs):
    """Updates our end of the RESNET Provider Data"""
    log = kwargs.get("log", logger)

    scrapers = [
        RESENTProvider,
        RESNETSamplingProvider,
        RESNETTrainingProvider,
        RESNETWaterSenseProvider,
    ]

    active_company_ids, active_user_ids = set(), set()
    result_msg = "Activated {} and deactivated {} RESNET {}{}"

    company_data = []
    for scraper_class in scrapers:
        scraper = scraper_class(**kwargs)
        try:
            data = scraper.parse()
        except Exception:  # pylint: disable=broad-except
            errmsg = "RESNET Scraper issue running {name!r}"
            log.error(errmsg.format(name=scraper_class), exc_info=1, extra=kwargs)
            continue

        # company_ids = set()
        for item in data:
            users = item.pop("users", None)
            if not users:
                continue
            user_data = users[0]

            try:
                existing = next(
                    (
                        x
                        for x in company_data
                        if x.get("name") == item.get("name") and x.get("state") == item.get("state")
                    )
                )
                existing.update(item)
                existing_users = existing.get("users")
                try:
                    existing_user = next(
                        (x for x in existing_users if x.get("name") == user_data.get("name"))
                    )
                    existing_user.update(user_data)
                except StopIteration:
                    existing["users"].append(user_data)
            except StopIteration:
                item["users"] = [user_data]
                company_data.append(item)

    # if the provider RESNET link is null and we happen to have a match align it.
    from axis.company.models import Company

    axis_cos = Company.objects.filter(
        resnet__isnull=True, provider_id__isnull=False, company_type=Company.PROVIDER_COMPANY_TYPE
    )
    for axis_company in axis_cos.all():
        try:
            res_company = next(
                (x for x in company_data if x.get("provider_id") == axis_company.provider_id)
            )
            res_company["company"] = axis_company
        except StopIteration:
            pass

    for item in company_data:
        users = item.pop("users", [])
        try:
            resnet_company = RESNETCompany.objects.update_or_create(**item)
        except Exception as err:  # pylint: disable=broad-except
            log.exception("Issues with {} - {}".format(item, err))
            continue
        else:
            active_company_ids.add(resnet_company.id)
            for user_data in users:
                user_data["resnet_company"] = resnet_company
                resnet_contact = RESNETContact.objects.update_or_create(**user_data)
                active_user_ids.add(resnet_contact.id)

    ina = (
        RESNETCompany.objects.all().exclude(id__in=list(active_company_ids)).update(is_active=False)
    )
    log.debug(result_msg.format(len(list(active_company_ids)), ina, " Companies", ""))

    ina = RESNETContact.objects.all().exclude(id__in=list(active_user_ids)).update(is_active=False)
    log.debug(result_msg.format(len(list(active_user_ids)), ina, " Users", ""))
