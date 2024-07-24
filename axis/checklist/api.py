from collections import defaultdict

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from axis.checklist.models import Section, CheckList, QAAnswer
from axis.checklist.serializers import SectionSerializer, CheckListSerializer, QAAnswerSerializer
from axis.examine.api.restframework import ExamineViewSetAPIMixin
from axis.eep_program.models import EEPProgram
from axis.filehandling.forms import CustomerDocumentForm
from .models import Question, QuestionChoice, Answer
from .serializers import (
    AnswerSerializer,
    QuestionSerializer,
    AnswerSerializer,
    QuestionChoiceSerializer,
)

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


def user_is_qa_company_on_home(user_company, home_id):
    from axis.home.models import Home

    programs = Home.objects.filter(id=home_id).values_list(
        "homestatuses__company", "homestatuses__eep_program__is_qa_program"
    )
    for company_id, is_qa in programs:
        if company_id == user_company.id and is_qa:
            return True

    return False


def get_serialized_question_data(request, *args, **kwargs):
    home_id = kwargs["home_id"]
    question_id = kwargs["question_id"]

    is_qa_program = user_is_qa_company_on_home(request.company, kwargs["home_id"])

    answer_storage_key = "related_answer" if is_qa_program else "answer"
    qa_answer_storage_key = "answer" if is_qa_program else "qa_answer"

    q = Question.objects.get(id=question_id)
    question = QuestionSerializer(q).data

    if is_qa_program:
        try:
            qa_answer = q.qaanswer_set.get(home_id=home_id)
        except QAAnswer.DoesNotExist as e:
            qa_answer = None
        except QAAnswer.MultipleObjectsReturned as e:
            answers = q.qaanswer_set.filter(home_id=home_id)
            answer_ids = list(answers.order_by("-pk").values_list("id", flat=True))
            answers.exclude(id=answer_ids[0]).delete()
            qa_answer = answers.get(id=answer_ids[0])
        if qa_answer:
            question[qa_answer_storage_key] = QAAnswerSerializer(qa_answer).data

    try:
        answer = q.answer_set.get(home_id=home_id)
    except Answer.DoesNotExist as e:
        answer = None
    except Answer.MultipleObjectsReturned:
        answers = q.answer_set.filter(home_id=home_id)
        answer_ids = list(answers.order_by("-pk").values_list("id", flat=True))
        answers.exclude(id=answer_ids[0]).delete()
        answer = answers.get(id=answer_ids[0])
    if answer:
        question[answer_storage_key] = AnswerSerializer(answer).data

    return question


class AnswerViewSet(ExamineViewSetAPIMixin, viewsets.ModelViewSet):
    throttle_scope = "checklist"

    @property
    def model(self):
        return self.get_serializer_class().Meta.model

    def get_queryset(self):
        return self.model.objects.select_related("question", "home")

    def get_serializer_class(self):
        """
        If any program attached to home is a QA program and the company on that status is
        the users Company, they have to be submitting or getting a QA Answer.
        A User is not allowed to provide QA AND Regular answers for a home.
        """
        if getattr(self, "home_id", False):
            if user_is_qa_company_on_home(self.request.company, self.home_id):
                return QAAnswerSerializer

        return AnswerSerializer

    def get_examine_machinery_classes(self):
        from axis.home.views.machineries import (
            HomeQAAnswerDocumentExamineMachinery,
            HomeAnswerDocumentExamineMachinery,
        )

        return {
            "HomeAnswerDocumentExamineMachinery": HomeAnswerDocumentExamineMachinery,
            "HomeQAAnswerDocumentExamineMachinery": HomeQAAnswerDocumentExamineMachinery,
        }

    def get_answer(self, serialize=False, **kwargs):
        """
        Didn't override get_object() because I don't know enough about the inner workings of
        ViewSets to be sure that I'm not impacting something down the line.
        """
        kwargs.pop("eep_program_id", None)
        try:
            answer = self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            raise ParseError(detail="{} does not exist".format(self.model.__class__.__name__))
        else:
            if serialize:
                answer = self.get_serializer(instance=answer)

        return answer

    def retrieve(self, request, *args, **kwargs):
        answer = self.get_answer(serialize=True, **kwargs)
        return Response(answer.data)

    def create(self, request, *args, **kwargs):
        data = request.data

        self.home_id = data["home"]
        self.question_id = data["question"]

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            self.perform_create(serializer)
            self.object = serializer.instance

        else:
            return Response(serializer.errors, status=400)

        kwargs.update({"home_id": self.home_id, "question_id": self.question_id})

        serialized_question_data = get_serialized_question_data(request, *args, **kwargs)
        return Response(serialized_question_data)

    def destroy(self, request, *args, **kwargs):
        answer = self.get_object()
        kwargs["home_id"] = answer.home.id
        kwargs["question_id"] = answer.question.id

        super(AnswerViewSet, self).destroy(request, *args, **kwargs)

        serialized_question_data = get_serialized_question_data(request, *args, **kwargs)
        return Response(serialized_question_data)

    def perform_destroy(self, obj):
        home = obj.home
        company = obj.user.company
        affected_stats = list(home.homestatuses.filter(company=company))

        obj.delete()
        for home_stat in affected_stats:
            home_stat.update_stats()


class QAAnswerViewSet(AnswerViewSet):
    model = QAAnswer
    queryset = model.objects.all()
    serializer_class = QAAnswerSerializer


class QuestionChoiceViewSet(viewsets.ModelViewSet):
    model = QuestionChoice
    queryset = model.objects.all()
    serializer_class = QuestionChoiceSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    model = Question
    queryset = model.objects.all()
    serializer_class = QuestionSerializer
    throttle_scope = "checklist"

    def retrieve(self, request, *args, **kwargs):
        serialized_question_data = get_serialized_question_data(request, *args, **kwargs)

        return Response(serialized_question_data)


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    model = Section
    queryset = model.objects.all()
    serializer_class = SectionSerializer


class CheckListViewSet(viewsets.ReadOnlyModelViewSet):
    model = CheckList
    queryset = model.objects.all().prefetch_related("section_set")
    serializer_class = CheckListSerializer
