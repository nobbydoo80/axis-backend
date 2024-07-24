"""mixins.py: """

__author__ = "Artem Hruzd"
__date__ = "01/22/2021 22:17"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


import io
import os

from django.apps import apps
from django.conf import settings
from django.core.files import File

from axis.company.models import Company
from axis.customer_hirl.models import HIRLProject
from axis.customer_hirl.tasks import scoring_upload_task
from axis.filehandling.models import AsynchronousProcessedDocument

customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLScoringUploadTestsMixin:
    def prepare_scoring_upload_task(self, file_name, template_type, data_type, eep_program):
        """
        :param file_name: xlsx file name
        :param template_type: template name key
        :param data_type: HIRLProject.project_type
        :param eep_program: helps to identify HIRL Project
        :return: list of annotations values('type__slug', 'content')
        """
        hirl_company = Company.objects.get(slug=customer_hirl_app.CUSTOMER_SLUG)
        company_admin_rater_user = self.get_admin_user(company_type=Company.RATER_COMPANY_TYPE)

        file_path = os.path.join(
            settings.SITE_ROOT, "axis", "customer_hirl", "sources", "tests", file_name
        )
        with io.open(file_path, "rb") as f:
            apd = AsynchronousProcessedDocument(
                company=hirl_company,
                download=True,
                task_name="scoring_upload_task",
                document=File(f, name=os.path.basename(file_path)),
            )
            apd.save()

        scoring_upload_task.delay(
            user_id=company_admin_rater_user.id,
            result_object_id=apd.id,
            template_type=template_type,
            data_type=data_type,
            verifier_id=company_admin_rater_user.id,
        )

        hirl_project = (
            HIRLProject.objects.filter(registration__eep_program=eep_program)
            .select_related("home_status")
            .get()
        )
        annotations = hirl_project.home_status.annotations.values("type__slug", "content")
        return annotations
