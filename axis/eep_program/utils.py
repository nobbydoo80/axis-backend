"""utils.py: Django eep_program"""


import logging

from .models import EEPProgram

__author__ = "mjeffrey"
__date__ = "2/25/15 3:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["mjeffrey", "sklass"]

log = logging.getLogger(__name__)


def create_qa_program_from_base(
    base_program, owner=None, excluded_question_slugs=None, extra_question_slugs=None
):
    """
    Takes an EEPProgram instance and copies it to make a QA program.
    Because of the way django copies instances the original instance is affected.

    Checklist from base program are copied, qa-ified and added to the new QA program.
    Questions are shared between checklists.

    This allows the QA program to drop questions from checklists that may be determined
    of not needing QA.

    usage:
        base_program = EEPProgram.objects.get(...)
        qa_program = create_qa_program_from_base(base_program)
    result:
        base_program === qa_program >> True
    """

    assert isinstance(base_program, EEPProgram), "Can only work with EEPProgram mahn."

    if owner:
        from axis.company.models import Company

        assert isinstance(owner, Company), "New program owner must be of Company type."

    if base_program.collection_request:
        from django_input_collection.models.utils import clone_collection_request

        collection_request = clone_collection_request(base_program.collection_request)
    else:
        if excluded_question_slugs:
            assert isinstance(
                excluded_question_slugs, (tuple, list)
            ), "Excluded Question slugs must be provided in enumerable form."

        if extra_question_slugs:
            assert isinstance(
                extra_question_slugs, (tuple, list)
            ), "Extra Question slugs must be provided in enumerable form."

        base_checklists = base_program.required_checklists.all()
        collection_request = None

    try:
        new_program = EEPProgram.objects.get(slug=base_program.slug + "-qa")
    except EEPProgram.DoesNotExist:
        new_program = base_program
        new_program.pk = None
        new_program.id = None
        new_program.slug += "-qa"
        new_program.name += " QA"

    new_program.is_qa_program = True
    if owner:
        new_program.owner = owner

    new_program.require_rem_data = False
    new_program.require_model_file = False
    new_program.require_builder_relationship = False
    new_program.require_builder_assigned_to_home = False
    new_program.require_hvac_relationship = False
    new_program.require_hvac_assigned_to_home = False
    new_program.require_utility_relationship = False
    new_program.require_utility_assigned_to_home = False
    new_program.require_rater_relationship = False
    new_program.require_rater_assigned_to_home = False
    new_program.require_provider_relationship = False
    new_program.require_provider_assigned_to_home = False
    new_program.require_qa_relationship = False
    new_program.require_qa_assigned_to_home = False
    new_program.require_resnet_sampling_provider = False
    new_program.viewable_by_company_type = "qa,provider"
    new_program.collection_request = collection_request

    new_program.save()

    if collection_request is None:
        # Legacy
        for checklist in base_checklists:
            base_questions = checklist.questions.all()

            if excluded_question_slugs:
                base_questions = base_questions.exclude(slug__in=excluded_question_slugs)

            if extra_question_slugs:
                from axis.checklist.models import Question

                base_questions = base_questions | Question.objects.filter(
                    slug__in=extra_question_slugs
                )

            from axis.checklist.models import CheckList

            try:
                new_checklist = CheckList.objects.get(slug=checklist.slug + "-qa")
            except CheckList.DoesNotExist:
                new_checklist = checklist

                new_checklist.pk = None
                new_checklist.id = None
                new_checklist.slug += "-qa"
                new_checklist.name += " QA"
                new_checklist.save()

            new_checklist.questions = list(base_questions)
            new_program.required_checklists.add(new_checklist)

    return new_program
