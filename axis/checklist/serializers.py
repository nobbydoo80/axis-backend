from django.urls import reverse_lazy, reverse
from django.utils import formats
from rest_framework.fields import SerializerMethodField

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from axis.checklist.models import Section, CheckList, QAAnswer
from axis.checklist.utils import validate_answer

from django.contrib.auth import get_user_model
from axis.home.models import Home
from axis.filehandling.api import CustomerDocumentSerializer
from .models import Answer, Question, QuestionChoice

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


User = get_user_model()


class ROSerializerMethodField(SerializerMethodField):
    read_only = True


class AnswerSerializer(ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    home = serializers.PrimaryKeyRelatedField(queryset=Home.objects.all())
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    company = serializers.CharField(source="user.company.name", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    lot_number = serializers.CharField(source="home.lot_number", read_only=True)
    delete_url = serializers.SerializerMethodField("get_delete_url_field")
    created_date = ROSerializerMethodField("get_created_date_field")
    customer_documents = CustomerDocumentSerializer(many=True, read_only=True)

    question_name = serializers.CharField(source="question.question", read_only=True)
    num_documents = serializers.SerializerMethodField()
    num_images = serializers.SerializerMethodField()
    model_type = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "id",
            "company",
            "user",
            "full_name",
            "first_name",
            "last_name",
            "home",
            "answer",
            "question",
            "comment",
            "system_no",
            "type",
            "photo_required",
            "document_required",
            "email_required",
            "email_sent",
            "failure_is_reviewed",
            "is_considered_failure",
            "display_as_failure",
            "confirmed",
            "created_date",
            "lot_number",
            "delete_url",
            "customer_documents",
            "model_type",
            # Virtual fields
            "question_name",
            "num_documents",
            "num_images",
        )
        read_only_fields = ("id", "model_type")

    @staticmethod
    def select_related():
        """
        This Serializer is used in more places than just the api Viewset.
        This is a helper so anywhere that uses this serializer doesn't need to track what things need to
        be selected along with the regular queryset separately from everywhere else.
        """
        return ("user", "user__company", "home", "question")

    @staticmethod
    def prefetch_related():
        """
        This Serializer is used in more places than just the api Viewset.
        This is a helper so anywhere that uses this serializer doesn't need to track what things need to
        be prefetched along with the regular queryset separately from everywhere else.
        """
        return ("customer_documents",)

    def get_model_type(self, obj):
        return self.Meta.model._meta.model_name

    def get_created_date_field(self, obj):
        return formats.date_format(obj.created_date, "SHORT_DATE_FORMAT")

    def get_delete_url_field(self, obj):
        return reverse_lazy(
            "apiv2:{}-detail".format(self.get_model_type(obj)), kwargs={"pk": obj.id}
        )

    def get_num_documents(self, obj):
        return obj.customer_documents.count_documents()

    def get_num_images(self, obj):
        return obj.customer_documents.count_images()

    def validate(self, attrs):
        """
        Check that the blog post is about Django.
        """
        cleaned_data = super(AnswerSerializer, self).validate(attrs)
        try:
            answer_data = validate_answer(
                question=cleaned_data.get("question"),
                answer=cleaned_data.get("answer"),
                comment=cleaned_data.get("comment"),
                ajax_error_reporting=True,
            )
            cleaned_data["answer"] = answer_data.get("answer")
            cleaned_data["type"] = answer_data.get("type")
            cleaned_data["is_considered_failure"] = answer_data.get("is_considered_failure")
            cleaned_data["display_as_failure"] = answer_data.get("display_as_failure")
            cleaned_data["email_required"] = answer_data.get("email_required")
            cleaned_data["document_required"] = answer_data.get("document_required")
            cleaned_data["photo_required"] = answer_data.get("photo_required")
        except ValueError as err:
            raise serializers.ValidationError(str(err))
        return cleaned_data


class QAAnswerSerializer(AnswerSerializer):
    class Meta:
        model = QAAnswer
        fields = (
            "id",
            "company",
            "user",
            "full_name",
            "first_name",
            "last_name",
            "home",
            "answer",
            "question",
            "comment",
            "system_no",
            "type",
            "photo_required",
            "document_required",
            "email_required",
            "email_sent",
            "failure_is_reviewed",
            "is_considered_failure",
            "display_as_failure",
            "confirmed",
            "created_date",
            "lot_number",
            "delete_url",
            "customer_documents",
            "model_type",
            # Virtual fields
            "question_name",
            "num_documents",
            "num_images",
        )
        read_only_fields = ("id",)


class SectionSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "questions",
            "checklist",
            "priority",
            "display_flag",
        )


class CheckListSerializer(ModelSerializer):
    sections = SectionSerializer(source="section_set", many=True, read_only=True)

    class Meta:
        model = CheckList
        fields = ("id", "slug", "name", "public", "description", "questions", "sections")


class QuestionChoiceSerializer(ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = (
            "id",
            "choice",
            "choice_order",
            "is_considered_failure",
            "display_as_failure",
            "photo_required",
            "document_required",
            "email_required",
            "comment_required",
        )


class QuestionSerializer(ModelSerializer):
    choices = QuestionChoiceSerializer(source="question_choice", many=True)

    # Compatibility fields for input-collection
    text = serializers.CharField(source="question")

    class Meta:
        model = Question
        fields = (
            "id",
            "slug",
            "priority",
            "question",
            "description",
            "type",
            "help_url",
            "unit",
            "allow_bulk_fill",
            "climate_zone",
            "minimum_value",
            "maximum_value",
            "is_optional",
            "choices",
            # Compatibility
            "text",
        )


class CheckListSerializerNestedQuestions(CheckListSerializer):
    questions = QuestionSerializer(many=True)


class HomeSerializer(ModelSerializer):
    class Meta:
        model = Home
        fields = (
            "id",
            "street_line1",
            "street_line2",
        )
