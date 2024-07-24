"""legacy.py - Axis"""

__author__ = "Steven K"
__date__ = "8/19/21 12:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import time

from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task(time_limit=60 * 60 * 2)
def audit_relationships(stat_id=None):
    """Audits the relationships to ensure they are properly added"""
    from axis.home.models import EEPProgramHomeStatus
    from axis.company.models import Company
    from axis.relationship.utils import create_or_update_spanning_relationships

    start = time.time()

    log = logger

    try:
        eep_company = Company.objects.get(slug="eto")
        qa_company = Company.objects.get(slug="csg-qa")
        provider_company = Company.objects.get(slug="peci")
    except Company.DoesNotExist:
        return

    if stat_id:
        stats = EEPProgramHomeStatus.objects.filter(id=stat_id)
    else:
        stats = EEPProgramHomeStatus.objects.filter(eep_program__slug__contains="eto").exclude(
            eep_program__slug__contains="qa"
        )

    bad = []
    for status in stats:
        relations = status.home.relationships.all().get_accepted_companies()
        companies = [eep_company, qa_company, provider_company]
        if status.eep_program.slug == "eto-2019":
            companies = [eep_company, provider_company]
        for company in companies:
            if company not in relations:
                log.warning("Missing %s on %s", company, status)
                bad.append(status.id)
                create_or_update_spanning_relationships([company], status)
                break
    if set(bad):
        log.error(
            "Corrected %s ETO Stats that were missing relationships %s", len(set(bad)), set(bad)
        )

    msg = "Completed %(task)s in %(elapsed_time)ss"
    log.info(msg, {"task": "audit_relationships", "elapsed_time": time.time() - start})
