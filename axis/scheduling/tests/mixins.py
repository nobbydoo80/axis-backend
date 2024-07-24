"""home_tasks.py: """


__author__ = "Artem Hruzd"
__date__ = "02/03/2020 15:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from axis.company.models import Company
from axis.company.tests.mixins import CompaniesAndUsersTestMixin
from axis.home.models import Home
from axis.home.tests.factories import home_factory
from axis.relationship.models import Relationship
from axis.scheduling.models import Task
from axis.scheduling.tests.factories import task_factory, task_type_factory


class SchedulingTaskMixin(CompaniesAndUsersTestMixin):
    include_company_types = ["builder", "eep", "provider", "rater", "general", "utility"]
    include_unrelated_companies = False
    include_noperms_user = False

    @classmethod
    def setUpTestData(cls):
        super(SchedulingTaskMixin, cls).setUpTestData()
        companies = Company.objects.all()

        builder_organization = Company.objects.filter(
            company_type=Company.BUILDER_COMPANY_TYPE
        ).first()
        home = home_factory(subdivision__builder_org=builder_organization)
        Relationship.objects.validate_or_create_relations_to_entity(
            home, companies.get(company_type="rater")
        )

        home_content_type = ContentType.objects.get_for_model(Home)
        global_task_type = task_type_factory(
            content_type=home_content_type, name="global task type"
        )

        # create a task and task_type for each company
        for company in companies:
            assigner = company.users.filter(is_company_admin=True).first()
            assignees = company.users.exclude(pk=assigner.pk)

            company_task_type = task_type_factory(
                content_type=home_content_type,
                name="company {} task type".format(company),
                company=company,
            )

            task_factory(
                home=home,
                status=Task.COMPLETED_STATUS,
                approval_state=Task.APPROVAL_STATE_NEW,
                assigner=assigner,
                approver=assigner,
                assignees=assignees,
                task_type=company_task_type,
            )
            task_factory(
                home=home,
                approval_state=Task.APPROVAL_STATE_APPROVED,
                approval_state_changed_at=timezone.now(),
                assigner=assigner,
                approver=assigner,
                assignees=assignees,
                task_type=global_task_type,
            )
            task_factory(
                home=home,
                approval_state=Task.APPROVAL_STATE_REJECTED,
                approval_state_changed_at=timezone.now(),
                assigner=assigner,
                approver=assigner,
                assignees=assignees,
                task_type=global_task_type,
            )
