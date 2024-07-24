"""forms.py: Django checklist"""


import logging

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

from django_mysql.models import QuerySetMixin as JSONQuerySetMixin
from django_input_collection.managers import CollectedInputQuerySet


__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CheckListManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def filter_by_company(self, company, **kwargs):
        """
        Filters objects by the company, via ``group=company.group``, or where ``public=True`` and
        the company's related companies' group is specified.

        """
        group_ids = company.relationships.get_companies().values_list("group", flat=True)

        query = Q(group=company.group) | Q(public=True, group_id__in=group_ids)
        return self.filter(query, **kwargs)

    def filter_by_user(self, user, **kwargs):
        """
        Sends the ``user.company`` through ``filter_by_company()``.  If the user is a superuser,
        then no filtering is performed and **kwargs is applied directly to the queryset.

        """
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class SectionManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_sections(self, group):
        return self.filter(checklist__group=group)


class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def filter_by_company(self, company):
        return self.get_queryset().filter_by_company(company)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)

    def filter_by_eep(self, eep):
        return self.get_queryset().filter_by_eep(eep)

    def filter_by_home(self, home, allow_sampling=True, user=None):
        return self.get_queryset().filter_by_home(home, allow_sampling=allow_sampling, user=user)

    def filter_by_home_for_user(self, home, user, allow_sampling=True):
        return self.get_queryset().filter_by_home(home, allow_sampling=allow_sampling, user=user)

    def filter_by_home_status(self, home_status, user=None, by_association=False):
        return self.get_queryset().filter_by_home_status(home_status, user, by_association)

    def filter_by_home_status_for_user(self, home_status, user):
        return self.get_queryset().filter_by_home_status(home_status, user)

    def filter_by_sampleset(self, sampleset):
        self.get_queryset().filter_by_sampleset(sampleset)


class AnswerQuerySet(QuerySet):
    def __filter_by_home_in_set_by_company(self, company):
        from axis.home.models import Home

        return self.filter(home__in=Home.objects.filter_by_company(company))

    def _filter_by_provider_company_type(self, company):
        from axis.company.models import Company

        company_filter_kwargs = {
            "mutual": True,
            "include_self": True,
            "company_type__in": ["rater", "qa"],
        }

        companies = Company.objects.filter_by_company(company, **company_filter_kwargs)
        companies = list(companies.values_list("id", flat=True))
        companies.append(company.id)

        return self.filter(user__company__id__in=companies)

    def _filter_by_eep_company_type(self, company):
        return self.filter(question__checklist__eepprogram__owner=company)

    def _filter_by_utility_company_type(self, company):
        return self.__filter_by_home_in_set_by_company(company)

    def _filter_by_builder_company_type(self, company):
        return self.__filter_by_home_in_set_by_company(company)

    def _filter_by_general_company_type(self, company):
        return self.__filter_by_home_in_set_by_company(company)

    def _filter_by_qa_company_type(self, company):
        return self.__filter_by_home_in_set_by_company(company)

    def filter_by_company(self, company):
        try:
            _filter = getattr(self, "_filter_by_{}_company_type".format(company.company_type))
        except AttributeError:
            return self.filter(user__company=company)
        else:
            return _filter(company)

    def filter_by_user(self, user):
        if user.is_superuser:
            return self.all()

        return self.filter_by_company(user.company)

    def filter_by_eep(self, eep):
        from axis.checklist.models import Question

        questions = list(Question.objects.filter_by_eep(eep).values_list("id", flat=True))
        return self.filter(question__id__in=questions)

    def filter_by_home(self, home, allow_sampling=True, user=None):
        if user:
            queryset = self.filter_by_user(user).filter(home=home)
        else:
            queryset = self.filter(home=home)
        ans_ids = set(queryset.values_list("id", flat=True))

        # Get a list of all contributing sampleset answers if we have a concrete home.
        if home.pk and allow_sampling:
            sampleset_stats = home.homestatuses.all().in_sampleset()
            for stat in sampleset_stats:
                ss_ans_id = self.filter_by_sampleset(stat.get_sampleset()).values_list(
                    "id", flat=True
                )
                ans_ids |= set(ss_ans_id)

        return self.filter(id__in=list(ans_ids))

    def filter_by_home_status(self, home_status, user=None, by_association=False):
        # TODO: In the case where a provider makes the home_stat, and a rater answers questions on it.
        # If we go through filter_by_company, the provider will have access to the rater's answers.
        # Is that the desired functionality? Or do we want to keep it to purely answer provided
        # by user from the company on the home_stat?
        # RE: AnswerManagerTests.test_deleting_answer_from_shared_question_does_not_delete_multiple_answers
        # return self.filter(user__company=home_status.company) \

        if by_association:
            queryset = self.filter_by_company(home_status.company).filter_by_eep(
                home_status.eep_program
            )
        elif user:
            queryset = self.filter_by_user(user).filter_by_eep(home_status.eep_program)
        else:
            queryset = self.filter_by_company(home_status.company).filter_by_eep(
                home_status.eep_program
            )

            # Don't allow qa to go through sampling
        if home_status.eep_program.is_qa_program:
            return queryset.filter_by_home(home_status.home, allow_sampling=False)

        return queryset.filter_by_home(home_status.home).distinct()

    def filter_by_sampleset(self, sampleset):
        """
        Returns the queryset of answers for the given sampleset.

        If the sampleset is confirmed, answers which have a SampleSetAnswer pointing to the given
        sampleset are queried and their underlying answers are returned.

        If the sampleset is not confirmed, only answers which have been entered for the Test home(s)
        are queried and returned (i.e., Answer->Home relationship is a test home in this sampleset.)
        """
        if sampleset.confirm_date:
            return self.filter(
                samplesethomestatus__sampleset=sampleset, samplesethomestatus__is_test_home=True
            ).distinct()
        else:
            return sampleset.get_current_source_answers()

    def get_uncorrected_failures(self):
        passing_questions_ids = list(
            self.filter(is_considered_failure=False).values_list("question_id", flat=True)
        )
        return self.filter(is_considered_failure=True).exclude(
            question__id__in=passing_questions_ids
        )

    def get_passing_and_corrected(self):
        return self.filter(is_considered_failure=False)


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def filter_by_company(self, company):
        return self.get_queryset().filter_by_company(company)

    def filter_by_user(self, user):
        if user.is_superuser:
            return self.all()

        # We should always have a company
        return self.filter_by_company(user.company)

    def filter_by_eep(self, eep):
        return self.get_queryset().filter_by_eep(eep)

    def filter_by_home(self, home):
        return self.get_queryset().filter_by_home(home)

    def filter_by_home_status(self, home_status):
        return self.get_queryset().filter_by_home_status(home_status)


class QuestionQuerySet(QuerySet):
    def filter_by_company(self, company):
        return self.filter()

    def filter_by_user(self, user):
        return self.filter_by_company(user.company)

    def filter_by_eep(self, eep):
        return self.filter(checklist__eepprogram=eep)

    def filter_by_home(self, home):
        question_ids = list(
            home.eep_programs.values_list("required_checklists__questions__id", flat=True)
        )
        return self.filter(id__in=question_ids)

    def filter_by_home_status(self, home_status):
        return self.filter_by_home(home_status.home).filter_by_eep(home_status.eep_program)


class CollectedInputQuerySet(JSONQuerySetMixin, CollectedInputQuerySet):
    def get_breakdown(self, field, first=False, last=False, map_queryset=None):
        """
        Returns a dict of unique ``field`` values in this queryset, mapped to the sub-queryset
        with that value.

        Example: get_breakdown('user_role') => {'rater': [...], 'qa': [...]}
        Example: get_breakdown('instrument') => {1: [...], 2: [...]}
        """
        values = self.values_list(field, flat=True)

        def prep_entry(value):
            partial_queryset = self.filter(**{field: value})

            if first:
                result = partial_queryset.first()
            elif last:
                result = partial_queryset.last()
            else:
                result = partial_queryset

            if map_queryset:
                result = map_queryset(result)

            return result

        return {value: prep_entry(value) for value in values}
