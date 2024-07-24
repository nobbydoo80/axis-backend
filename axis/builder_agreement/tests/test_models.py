from django.test import TestCase

from .factories import builder_agreement_factory
from axis.core.tests.factories import non_company_user_factory, general_super_user_factory

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class BuilderAgreementModelTests(TestCase):
    def test_can_be_deleted(self):
        """Verifies that a BuilderAgreement can only be deleted when ``lots_paid`` is zero."""
        user = general_super_user_factory()
        obj = builder_agreement_factory(lots_paid=0)
        self.assertEqual(obj.can_be_deleted(user), True)
        obj = builder_agreement_factory(lots_paid=1)
        self.assertEqual(obj.can_be_deleted(user), False)

    def test_can_be_edited(self):
        """Verifies that a BuilderAgreement can only be deleted when ``lots_paid`` is zero."""
        obj = builder_agreement_factory()

        user = general_super_user_factory()
        self.assertEqual(obj.can_be_edited(user), True)

        user = non_company_user_factory()
        self.assertEqual(obj.can_be_edited(user), False)
