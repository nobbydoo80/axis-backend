import datetime
import time

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import F
from django.utils.timezone import now
from infrastructure.utils import elapsed_time

from .models import EkotropeAuthDetails, Project

__author__ = "Autumn Valenta"
__date__ = "10/31/16 09:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from .utils import stub_project_list

logger = get_task_logger(__name__)


@shared_task(time_limit=60 * 5)
def import_project_tree(auth_details_id, project_id):
    from .utils import import_project_tree

    auth_details = EkotropeAuthDetails.objects.get(id=auth_details_id)
    return import_project_tree(auth_details, project_id)


@shared_task()
def spread_credentials(company_id=None):
    """Ensures every represented company has all of its users with credentials."""
    # NOTE: Existing rows are NOT effected by this update.
    from axis.company.models import Company

    kwargs = dict()
    if company_id:
        kwargs["user__company_id"] = company_id

    credentials = (
        EkotropeAuthDetails.objects.filter(**kwargs)
        .annotate(company_id=F("user__company"))
        .values_list("company_id", "username", "password")
        .order_by("company_id")
        .distinct()
    )

    for company_id, username, password in credentials:
        company = Company.objects.get(id=company_id)
        user_ids = list(
            company.users.filter(is_active=True, ekotropeauthdetails__isnull=True).values_list(
                "id", flat=True
            )
        )
        EkotropeAuthDetails.objects.bulk_create(
            [
                EkotropeAuthDetails(username=username, password=password, user_id=user_id)
                for user_id in user_ids
            ]
        )


@shared_task(time_limit=60 * 60)
def import_projects(company_id=None):
    """We need a reliable way to pull the data periodically. I will poll this few minutes"""
    start = time.time()
    seen = []
    total = []
    auth_details = EkotropeAuthDetails.objects.all()
    look_back = now() - datetime.timedelta(days=30)
    if company_id:
        auth_details = EkotropeAuthDetails.objects.filter(user__company_id=company_id)
    for ekotrope_auth in auth_details:
        if ekotrope_auth.user.company_id in seen:
            continue
        new_projects = stub_project_list(ekotrope_auth)
        for project in new_projects:
            import_project_tree.delay(ekotrope_auth.id, project["id"])
            total.append(project["id"])
        for project in Project.objects.filter(
            company=ekotrope_auth.user.company, data={}, created_date__gte=look_back
        ):
            if project.id not in total:
                import_project_tree.delay(ekotrope_auth.id, project.id)
                total.append(project.id)

        seen.append(ekotrope_auth.user.company.id)

    elapsed = elapsed_time(time.time() - start).long_fmt
    msg = "Reviewed %(company_count)d companies and imported %(total)d projects in %(elapsed)s"
    logger.info(msg, {"company_count": len(seen), "total": len(total), "elapsed": elapsed})
    return msg % {"company_count": len(seen), "total": len(total), "elapsed": elapsed}
