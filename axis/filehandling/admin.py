__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

from django.contrib import admin
from axis.filehandling.models import UploadFile, AsynchronousProcessedDocument, CustomerDocument
from django.contrib.admin.decorators import register
from django.contrib.contenttypes.admin import GenericTabularInline


@register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    model = UploadFile
    list_display = ("file",)
    list_filter = ("file",)


@register(AsynchronousProcessedDocument)
class AsynchronousProcessedDocumentAdmin(admin.ModelAdmin):
    model = AsynchronousProcessedDocument
    raw_id_fields = ("company",)
    list_display = ("company", "document", "download", "final_status", "result")
    list_filter = ("final_status",)
    search_fields = ["company__name", "result"]
    actions = ["update_results"]

    def update_results(self, request, queryset):
        """Update a companies groups"""

        for doc in queryset.all():
            doc.final_status = None
            doc.update_results()
        if queryset.count() == 1:
            message_bit = "1 result"
        else:
            message_bit = "%s results" % queryset.count()
        self.message_user(request, "%s successfully updated." % message_bit)

    update_results.short_description = "Force a update to results"


class CustomerDocumentGenericTabularInline(GenericTabularInline):
    model = CustomerDocument
    extra = 0
    raw_id_fields = ("company",)
