"""bulk_home_checklist.py: Django """


import logging
import os
import uuid

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management import BaseCommand, CommandError

from axis.checklist.tasks import bulk_checklist_process
from axis.checklist.utils import ExcelChecklist
from axis.eep_program.models import EEPProgram
from axis.filehandling.models import AsynchronousProcessedDocument

__author__ = "Steven Klass"
__date__ = "01/21/2019 14:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Upload/Download a bulk home checklist"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--action",
            action="store",
            dest="action",
            default="download",
            choices=["write", "read"],
            help="Are we reading or writing checklist",
        )
        parser.add_argument("--program", action="store", dest="program", help="Program ID or Slug")
        parser.add_argument("--user", action="store", dest="user", help="User ID or username")
        parser.add_argument(
            "--filename",
            action="store",
            dest="filename",
            help="Input or Output File (depending on action)",
            default="~/Downloads/Bulk_Checklist.xlsx",
        )
        parser.add_argument(
            "--no-lock", action="store_false", dest="lock_and_hide", help="Lock and hide sheets"
        )
        parser.add_argument(
            "--overwrite-answers",
            action="store_true",
            dest="overwrite_old_answers",
            help="Overwrite old answers",
        )

    def set_options(
        self,
        action=None,
        program=None,
        user=None,
        filename=None,
        overwrite_old_answers=False,
        **_options,
    ):
        result = {}

        if program:
            try:
                program = EEPProgram.objects.get(id=program)
            except EEPProgram.DoesNotExist:
                raise CommandError("EEPProgram with ID %s does not exist" % program)
            except ValueError:
                try:
                    program = EEPProgram.objects.get(slug=program)
                except EEPProgram.DoesNotExist:
                    raise CommandError("EEPProgram with slug %s does not exist" % program)
            log.info("Using %s" % program)
            result["program"] = program

        if user:
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise CommandError("User with ID %s does not exist" % user)
            except ValueError:
                try:
                    user = User.objects.get(username=user)
                except User.DoesNotExist:
                    raise CommandError("User with username %s does not exist" % user)
            log.info("Using %s" % user)
            result["user"] = user
            log.info("Derived %s" % user.company)
            result["company"] = user.company
        else:
            raise CommandError("No user provided given the options")

        if action == "write":
            if not os.path.exists(os.path.dirname(os.path.expanduser(filename))):
                raise CommandError(
                    "Output Path does not exist %s" % os.path.dirname(os.path.expanduser(filename))
                )
            log.info("Output to %s" % os.path.expanduser(filename))
            result["filename"] = os.path.expanduser(filename)

        else:
            if not os.path.exists(os.path.expanduser(filename)):
                raise CommandError("Input Path does not exist %s" % os.path.expanduser(filename))
            log.info("Input %s" % os.path.expanduser(filename))
            result["filename"] = os.path.expanduser(filename)
            result["overwrite_old_answers"] = overwrite_old_answers
        return result

    def handle(self, *args, **options):
        kwargs = self.set_options(**options)

        if options["action"] == "write":
            template = ExcelChecklist(
                eep_program_id=kwargs.get("program").id,
                company_id=kwargs.get("company").id,
                user_id=kwargs.get("user").id,
            )
            with open(kwargs.get("filename"), "wb") as fileobj:
                template.create_bulk_checklist(
                    kwargs.get("company"),
                    eep_program=kwargs.get("program"),
                    filename=fileobj,
                    lock_and_hide=options.get("lock_and_hide"),
                    breakout_choices=kwargs.get("breakout_choices", False),
                )
            self.stdout.write(f"Wrote file to {kwargs['filename']}")
        else:
            with open(kwargs.get("filename"), "rb") as file_obj:
                result_obj, create = AsynchronousProcessedDocument.objects.get_or_create(
                    company=kwargs.get("company"),
                    document=File(file_obj, name=os.path.basename(kwargs.get("filename"))),
                    task_name="axis.checklist.tasks.bulk_checklist_process",
                    task_id=str(uuid.uuid4()),
                )
            AsynchronousProcessedDocument.objects.filter(id=result_obj.id).update(
                final_status="STARTED"
            )
            log.info(f"Watch upload live at http://localhost:8000{result_obj.get_absolute_url()}")
            try:
                bulk_checklist_process(
                    company_id=kwargs.get("company").id,
                    user_id=kwargs.get("user").id,
                    result_object_id=result_obj.id,
                    overwrite_old_answers=kwargs.get("overwrite_old_answers"),
                    log=log,
                )
                AsynchronousProcessedDocument.objects.filter(id=result_obj.id).update(
                    final_status="SUCCESS"
                )
            except:
                AsynchronousProcessedDocument.objects.filter(id=result_obj.id).update(
                    final_status="FAILURE"
                )
                raise

            document = AsynchronousProcessedDocument.objects.get(id=result_obj.id)
            self.stdout.write(
                f"Processed file {kwargs['filename']} with {document.final_status} "
                f"see results at {document.get_absolute_url()}"
            )
