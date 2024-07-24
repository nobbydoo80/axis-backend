"""permissions.py: Django checklist"""


import logging

from axis.core.management.commands.set_permissions import AppPermission
from .models import CheckList, Section, Question, Answer, QAAnswer

__author__ = "Steven Klass"
__date__ = "2/1/13 12:31 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ChecklistPermissions(AppPermission):
    models = [CheckList, Section, Question]
    default_admin_abilities = ["view", "add", "change"]

    def get_customer_permissions(self):
        return ["view", "add", "change", "delete"], [
            "view",
        ]

    def get_sponsor_permissions(self):
        return ["view", "add", "change"], self.default_abilities

    def get_trc_permissions(self):
        return []

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []


class AnswerPermissions(AppPermission):
    models = [Answer]
    default_admin_abilities = ["view", "add", "change"]

    def get_customer_rater_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_customer_provider_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_sponsored_rater_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_sponsored_provider_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_trc_permissions(self):
        return [], []

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []


class QAAnswerPermissions(AppPermission):
    models = [
        QAAnswer,
    ]

    def get_rater_permissions(self):
        return [], []

    def get_qa_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_provider_permissions(self):
        return ["view", "add", "change", "delete"]

    def get_trc_permissions(self):
        return [], []

    def get_provider_home_innovation_research_labs_permissions(self):
        return [], []

    def get_sponsored_provider_home_innovation_research_labs_permissions(self):
        return [], []
