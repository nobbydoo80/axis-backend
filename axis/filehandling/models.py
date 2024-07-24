"""models.py: Django models"""

__author__ = "Steven Klass"
__date__ = "11/22/11 4:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
import os
import re
from collections import OrderedDict
from functools import cached_property
from pprint import pformat

from celery.result import AsyncResult
from django.conf import settings
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django_celery_results.models import TaskResult
from hashid_field import Hashid
from picklefield import PickledObjectField
from simple_history.models import HistoricalRecords

from axis.core.utils import (
    randomize_filename,
    unrandomize_filename,
    get_task_status,
    TASK_STATE_COLORS,
)
from axis.filehandling import docusign
from . import strings
from .managers import AsynchronousProcessedDocumentManager, CustomerDocumentManager
from .utils import get_mimetype_category


log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
filehandling_app = apps.get_app_config("filehandling")

DOCUMENT_TYPES = (
    ("document", "Document"),
    ("image", "Image"),
    ("", "Other"),
)


def filepath(instance, filename):
    """Computes the logo image upload path"""
    filename = filename
    if not isinstance(filename, str):
        filename = filename.name
    return os.path.join("uploads", "csvfiles", filename)


class UploadFile(models.Model):
    file = models.FileField(upload_to=filepath, blank=True, null=True)


def uploaded_file_name(instance, filename):
    """Location of any company Documents"""
    filename = filename
    up_or_down = "uploaded_documents"
    if hasattr(instance, "download") and instance.download:
        up_or_down = "download"
    if not isinstance(filename, str):
        filename = filename.name
    return os.path.join(
        "documents",
        instance.company.company_type,
        instance.company.slug,
        up_or_down,
        randomize_filename(filename),
    )


class ResultObjectLog(object):
    def __init__(self, *args, **kwargs):
        result_object_id = kwargs.get("result_object_id", None)
        if result_object_id:
            self.result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)
        else:
            self.result_object = None

    def _update_single(self, attribute, values, row_num=None):
        try:
            attr = getattr(self, attribute)
        except AttributeError:
            setattr(self, attribute, OrderedDict())
            attr = getattr(self, attribute)

        if not isinstance(values, list):
            values = [values]

        for item in values:
            if item is not attr:
                attr[item] = []
            if row_num and row_num not in attr[item]:
                attr[item].append(row_num)

            level = attribute if attribute[-1] != "s" else attribute[:-1]
            level = getattr(logging, level.upper())
            log_level = level if settings.DEBUG else getattr(logging, "INFO")
            try:
                log.log(
                    log_level,
                    "{}{}".format("[{}]".format(row_num) if row_num else "", item),
                )
            except UnicodeDecodeError:
                log.log(log_level, "Issue found and unable to display error")
            except TypeError:
                log.exception("Can't figure out level from %(err)s", {"err": attribute})

    def update_dict(self, data_dict=None, line_no=None):
        assert isinstance(data_dict, dict), "Umm we need a dictionary"
        latest = data_dict.pop("latest", None)
        for k, v in data_dict.items():
            self._update_single(k, v, line_no)
            if isinstance(v, list) and len(v):
                try:
                    setattr(self, "latest", v[-1])
                except UnicodeDecodeError:
                    pass
            elif v:
                try:
                    setattr(self, "latest", v)
                except UnicodeDecodeError:
                    pass
        if latest not in ["", None]:
            setattr(self, "latest", latest)

    def update(
        self,
        result=None,
        result_list=None,
        errors=None,
        warnings=None,
        info=None,
        debug=None,
        latest=None,
        status="PREPARING",
        raise_errors=False,
        line_no=None,
    ):
        if result_list:
            if len(result_list) >= 4:
                result = dict(
                    errors=result_list[0],
                    warnings=result_list[1],
                    info=result_list[2],
                    debug=result_list[3],
                )
            elif len(result_list) == 3:
                result = dict(errors=result_list[0], warnings=result_list[1], info=result_list[2])
            elif len(result_list) == 2:
                result = dict(errors=result_list[0], warnings=result_list[1])
            elif len(result_list) == 1:
                result = dict(errors=result_list[0])
        if result:
            self.update_dict(result, line_no=line_no)
        if errors:
            errors = errors if isinstance(errors, list) else [errors]
            self._update_single("errors", errors, line_no)
        if warnings:
            warnings = warnings if isinstance(warnings, list) else [warnings]
            self._update_single("warnings", warnings, line_no)
        if info:
            info = info if isinstance(info, list) else [info]
            self._update_single("info", info, line_no)
        if debug:
            debug = debug if isinstance(debug, list) else [debug]
            self._update_single("debug", debug, line_no)

        if latest:
            setattr(self, "latest", latest)
            log.debug(latest)

        result_dict = self.as_dict(raise_errors=raise_errors)

        if self.result_object:
            t_result = (
                self.result_object.result if isinstance(self.result_object.result, dict) else {}
            )
            t_result.update(result_dict)
            self.result_object.result = t_result
            self.result_object.save()
        return True

    def _get_result_str(self, attribute):
        results = []
        sub_item = getattr(self, attribute, OrderedDict()).copy()
        for k, v in sub_item.items():
            if len(v) > 1:
                results.append("Lines: {} {}".format(",".join([x for x in v]), k))
            elif len(v) == 1:
                results.append("Line: {} {}".format(v[0], k))
            else:
                try:
                    results.append("{}".format(k))
                except UnicodeDecodeError:
                    results.append("Unable to display Unicode Issue")
        return results

    def get_errors(self):
        return self._get_result_str("errors")

    def get_warnings(self):
        return self._get_result_str("warnings")

    def get_info(self):
        return self._get_result_str("info")

    def get_debug(self):
        return self._get_result_str("debug")

    def as_dict(self, raise_errors=False):
        errors = self.get_errors()
        if raise_errors and len(errors):
            errors.reverse()
            errors.append("Did not do any processing because due to the following errors")
            errors.reverse()

        return dict(
            errors=errors,
            warnings=self.get_warnings(),
            info=self.get_info(),
            debug=self.get_debug(),
            latest=getattr(self, "latest", ""),
        )

    def __repr__(self):
        return pformat(self.as_dict())


def content_name(instance, filename):
    """Location of any documents"""
    filename = filename
    if not isinstance(filename, str):
        filename = filename.name
    ct = instance.content_type
    identifier = str(instance.object_id)
    return os.path.join(
        "documents",
        instance.company.company_type,
        instance.company.slug,
        ct.app_label + "." + ct.model,
        identifier,
        randomize_filename(filename),
    )


class CustomerDocument(models.Model):
    """
    GenericForeignKey model for associating document objects to our other models using a common
    interface.

    In all cases, the ``company`` attribute is set to the company of the user that added the
    document.  This is particularly important in the case of ``content_object`` being set to some
    other Company.

    Cheat sheet:

        * ``customerdoc.company`` - owner of the document
        * ``somemodel.customer_documents.all()`` - all documents shared by anybody to the SomeModel
              instance.  Filter this with a ``company`` kwarg to narrow by sharing source
        * ``company.all_customer_documents.all()`` - All CustomerDocuments shared by this company to
              any object in the system.  This is the reversename for the CustomerDocument->Company
              foreign key.
    """

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        verbose_name="Sharing company",
        related_name="all_customer_documents",
    )
    document = models.FileField(upload_to=content_name, max_length=512, null=True, blank=True)
    type = models.CharField(choices=DOCUMENT_TYPES, max_length=15, blank=True)
    filesize = models.PositiveIntegerField(editable=False, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)

    # The object to which the document is actually attached
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    login_required = models.BooleanField(
        default=True, help_text="Allows document to be pulled without login"
    )

    created_on = models.DateTimeField(default=now, editable=False)
    last_update = models.DateTimeField(auto_now=True)

    objects = CustomerDocumentManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Customer Document"
        ordering = ("-last_update",)

    def __str__(self):
        return "{}".format(self.filename)

    @property
    def filename(self):
        """Used to return the real name of the file."""
        if self.document:
            return os.path.basename(unrandomize_filename(self.document.name))
        return ""

    @property
    def filetype(self):
        return get_mimetype_category(self.filename)

    def can_be_deleted(self, user):
        return self.can_be_edited(user=user)

    def can_be_edited(self, user):
        if user.is_superuser:
            return True
        matches = [
            "Home via Bulk Upload",
            "Home via Single Home Upload",
            "Scoring upload",
        ]
        if any(match in self.description for match in matches):
            return False
        if user.company.slug == customer_hirl_app.CUSTOMER_SLUG and user.is_company_admin:
            if self.company.is_sponsored_by_customer_hirl():
                return True
        return user.company == self.company

    def get_signing_url(self, user, postback_url, **kwargs):
        docusign.get_signing_url(self, user, postback_url, **kwargs)

    def get_preview_link(self) -> str:
        url = reverse_lazy("api_v3:customer_document-preview", args=(self.id,))
        if not self.login_required:
            hash_id = Hashid(self.id, salt=filehandling_app.HASHID_FILE_HANDLING_SALT)
            url = reverse_lazy("api_v3:public_document-detail", args=(hash_id.hashid,))
        return url


class AsynchronousProcessedDocument(models.Model):
    """This will take a document and a task name and pro"""

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    document = models.FileField(
        upload_to=uploaded_file_name,
        max_length=512,
        help_text=strings.ASYNCHRONOUSPROCESSEDDOCUMENT_MODEL_DOCUMENT,
    )

    task_name = models.CharField(max_length=128, blank=True, null=True)
    task_id = models.CharField(max_length=36, blank=True, null=True)

    final_status = models.CharField(
        max_length=50,
        choices=zip(TASK_STATE_COLORS.keys(), TASK_STATE_COLORS.keys()),
        null=True,
    )

    result = PickledObjectField(null=True, default=None, editable=False)

    download = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    objects = AsynchronousProcessedDocumentManager()

    class Meta:
        verbose_name = "Processed Document"

    def filename(self):
        """Return the actual filename"""
        return os.path.basename(unrandomize_filename(self.document.name))

    def __str__(self):
        return self.filename()

    def get_absolute_url(self):
        return reverse("async_document_detail", kwargs={"pk": self.id})

    def save(self, *args, **kwargs):
        if self.task_id and self.task_id.strip() in [""]:
            self.task_id = None

        if not self.id:
            if not self.result:
                self.result = dict()
        else:
            # Force this to not give it up...
            prior = AsynchronousProcessedDocument.objects.get(pk=self.id)
            if prior.task_id and prior.task_id.strip() not in ["None", ""]:
                self.task_id = prior.task_id

        return super(AsynchronousProcessedDocument, self).save(*args, **kwargs)

    def get_state(self):
        """Get the state of the item"""
        if self.final_status:
            return self.final_status
        if not self.task_id:
            return "UNAVAILABLE"
        try:
            return TaskResult.objects.get(task_id=self.task_id).status
        except TaskResult.DoesNotExist:
            return "Pending (Unavailable) - {}".format(self.task_id)

    def update_results(self):
        """This will simply update the results"""
        if self.final_status:
            return

        t_result = self.result if isinstance(self.result, dict) else dict()
        try:
            task = TaskResult.objects.get(task_id=self.task_id)
            status = task.status
        except TaskResult.DoesNotExist:
            log.debug("No TaskResult for {task_id}".format(**self.__dict__))
            # If the job does not get scheduled..
            status, task = None, None
            if self.task_id:
                try:
                    status = get_task_status(self.task_id)
                except Exception as err:
                    t_result["latest"] = "{}".format(err)
                    self.result = t_result
                    try:
                        self.save()
                    except:
                        log.exception("%s on %s", err, self)

            msg = "Job has yet to be scheduled."
            if status and status.queue_depth and len(status.pending):
                if isinstance(status.queue_depth, int):
                    msg = "{} jobs in queue...".format(status.queue_depth)
                elif "<" in status.queue_depth:
                    value = status.queue_depth
                    try:
                        m = re.search(r"(\d+) items remaining", t_result.get("latest", ""))
                    except TypeError:
                        m = None
                    if m:
                        value_int = min([int(m.group(1)), len(status.pending)])
                        value = "< {}".format(value_int)
                    msg += "  {} items remaining before this gets scheduled.".format(value)

                t_result["latest"] = msg
                self.result = t_result
                try:
                    self.save()
                except:
                    log.error("Issue with a failure on %s", self)

        if task and status in ["SUCCESS", "FAILURE"]:
            result_dict = isinstance(task.result, dict) or isinstance(self.result, dict)
            if status == "SUCCESS" and result_dict:
                self.final_status = status
                if task.result:
                    t_result["result"] = task.result
                    if isinstance(task.result, Exception):
                        t_result["result"] = "{}".format(task.result)
                        self.final_status = "FAILURE"
                    elif isinstance(task.result, dict):
                        if len(task.result.get("errors", [])):
                            self.final_status = "FAILURE"
                        if len(task.result.get("ERROR", [])):
                            self.final_status = "FAILURE"
                    elif isinstance(task.result, str) and task.result == "null":
                        t_result["result"] = "Task %s completed." % task.task_id
                    self.result = t_result
                    self.save()
                    return
                elif self.result:
                    self.final_status = status
                    if isinstance(self.result, dict):
                        if len(self.result.get("errors", [])):
                            self.final_status = "FAILURE"
                        if len(self.result.get("ERROR", [])):
                            self.final_status = "FAILURE"
                    try:
                        self.save()
                    except:
                        log.error("Issue with a failure on %s", self)
            else:
                result = None
                if task.traceback:
                    t_result["traceback"] = task.traceback
                    # msg = "Task {task_id} ({task_name}) had traceback:\n {traceback}"
                    # log.error(msg.format(task_id=self.task_id, task_name=self.task_name,
                    #                      traceback=task.traceback))
                    result = True

                try:
                    result_obj = AsyncResult(self.task_id)
                except RuntimeError as err:
                    t_result["result"] = err.message
                    result = True
                else:
                    try:
                        ready = result_obj.ready()
                    except AttributeError:
                        pass
                    else:
                        if ready:
                            t_result["result"] = result_obj.get(propagate=False)
                            result = True

                if result:
                    self.final_status = status
                    if isinstance(t_result, dict) and len(t_result.get("errors", [])):
                        self.final_status = "FAILURE"
                    self.result = t_result
                    try:
                        self.save()
                    except:
                        log.error("Issue with a failure on %s", self)

            msg = "Task {task_id} ({task_name}) had a final status of {final_status}"
            log.info(msg.format(**self.__dict__))

    def get_exception(self):
        """Get any exceptions"""
        try:
            task = TaskResult.objects.get(task_id=self.task_id)
            if task.traceback:
                return task.traceback
        except TaskResult.DoesNotExist:
            return None
