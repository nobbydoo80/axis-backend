"""Api v3 filehandling serializers."""


import logging

from django.apps import apps
from hashid_field import Hashid
from rest_framework import serializers
from rest_framework.reverse import reverse_lazy

from ..models import CustomerDocument, AsynchronousProcessedDocument

__author__ = "Autumn Valenta"
__date__ = "3/4/14 1:19 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)
filehandling_app = apps.get_app_config("filehandling")


class CustomerDocumentSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(read_only=True)
    filetype = serializers.CharField(read_only=True)
    hash_id = serializers.SerializerMethodField(read_only=True)
    preview_link = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomerDocument
        fields = (
            "id",
            "document",
            "type",
            "description",
            "is_public",
            "is_active",
            "login_required",
            "created_on",
            "last_update",
            "filesize",
            "filename",
            "filetype",
            "company",
            "hash_id",
            "preview_link",
        )
        read_only_fields = (
            "id",
            "filesize",
            "type",
            "company",
            "hash_id",
            "preview_link",
        )

    def get_hash_id(self, instance: CustomerDocument) -> str:
        hash_id = Hashid(instance.id, salt=filehandling_app.HASHID_FILE_HANDLING_SALT)
        return hash_id.hashid

    def get_preview_link(self, instance: CustomerDocument) -> str:
        url = instance.get_preview_link()
        if "request" in self.context:
            return self.context["request"].build_absolute_uri(url)
        return url


class CustomerDocumentInfoSerializer(CustomerDocumentSerializer):
    """
    Simplified version for nested usage
    """

    pass


class AsynchronousProcessedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsynchronousProcessedDocument
        fields = (
            "id",
            "company",
            "document",
            "task_name",
            "task_id",
            "final_status",
            "result",
            "download",
            "modified_date",
            "created_date",
        )
