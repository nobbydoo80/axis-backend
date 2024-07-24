"""test_models.py: Django customer_neea"""


import logging

from axis.company.models import Company
from axis.core.tests.client import AxisClient
from axis.core.tests.testcases import AxisTestCase
from axis.customer_neea import strings
from axis.customer_neea.tests.mixins import CustomerNEEAModelTestMixin
from axis.eep_program.models import EEPProgram
from axis.floorplan.models import Floorplan
from axis.home.models import Home, EEPProgramHomeStatus
from axis.relationship.models import Relationship
from axis.messaging.models import Message

__author__ = "Steven Klass"
__date__ = "4/17/14 1:29 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class CustomerNEEAModelTests(CustomerNEEAModelTestMixin, AxisTestCase):
    """Test out community app"""

    client_class = AxisClient

    def test_builder_no_notification_messages(self):
        """Test HVAC Notification Messages does NOT occur for friends"""
        self.assertEqual(Message.objects.count(), 0)

        home = Home.objects.get(street_line1__icontains="Oberlin")

        neea = Company.objects.get(slug="neea")
        neea_co_ids = Company.objects.filter_by_company(neea).values_list("id", flat=True)
        self.assertIn(home.get_builder().id, neea_co_ids)

        earth_advantage = Company.objects.get(slug="earth_advantage")
        EEPProgramHomeStatus.objects.create(
            home=home,
            company=earth_advantage,
            eep_program=EEPProgram.objects.get(slug="neea-prescriptive-2015"),
            floorplan=Floorplan.objects.get(),
        )

        Relationship.objects.validate_or_create_relations_to_entity(home, earth_advantage)
        rel_ids = home.relationships.all().values_list("company_id", flat=True)
        self.assertIn(home.get_builder().id, rel_ids)
        msgs = [strings.NEEA_NO_HVAC_RELATIONSHIP, strings.NEEA_NO_BUILDER_RELATIONSHIP]
        msgs = [x[-245:] for x in msgs]
        for msg in msgs:
            self.assertEqual(Message.objects.filter(content__icontains=msg).count(), 0)

    def test_hvac_no_notification_messages(self):
        """Test HVAC Notification Messages does NOT occur for friends"""
        self.assertEqual(Message.objects.count(), 0)

        home = Home.objects.get(street_line1__icontains="Oberlin")

        neea = Company.objects.get(slug="neea")
        neea_co_ids = Company.objects.filter_by_company(neea).values_list("id", flat=True)
        hvac = Company.objects.get(slug="pyramid_hvac")
        self.assertIn(hvac.id, neea_co_ids)

        earth_advantage = Company.objects.get(slug="earth_advantage")
        EEPProgramHomeStatus.objects.create(
            home=home,
            company=earth_advantage,
            eep_program=EEPProgram.objects.get(slug="neea-prescriptive-2015"),
            floorplan=Floorplan.objects.get(),
        )

        Relationship.objects.validate_or_create_relations_to_entity(home, earth_advantage, hvac)
        rel_ids = home.relationships.all().values_list("company_id", flat=True)
        self.assertIn(hvac.id, rel_ids)
        msgs = [strings.NEEA_NO_HVAC_RELATIONSHIP, strings.NEEA_NO_BUILDER_RELATIONSHIP]
        msgs = [x[-245:] for x in msgs]
        for msg in msgs:
            self.assertEqual(Message.objects.filter(content__icontains=msg).count(), 0)

    def test_builder_hvac_notification_messages(self):
        """Test Builder Notification Messages occurs"""
        self.assertEqual(Message.objects.count(), 0)

        home = Home.objects.get(street_line1__icontains="Shaver")

        neea = Company.objects.get(slug="neea")
        neea_co_ids = Company.objects.filter_by_company(neea).values_list("id", flat=True)
        self.assertEqual(home.get_builder().id in neea_co_ids, False)

        earth_advantage = Company.objects.get(slug="earth_advantage")
        EEPProgramHomeStatus.objects.create(
            home=home,
            company=earth_advantage,
            eep_program=EEPProgram.objects.get(slug="neea-performance-2015"),
            floorplan=Floorplan.objects.get(),
        )

        Relationship.objects.validate_or_create_relations_to_entity(home, earth_advantage)
        rel_ids = home.relationships.all().values_list("company_id", flat=True)
        self.assertIn(home.get_builder().id, rel_ids)
        self.assertEqual(
            Message.objects.filter(
                content__icontains=strings.NEEA_NO_BUILDER_RELATIONSHIP[-83:]
            ).count(),
            1,
        )
        hvac = Company.objects.get(slug="unk_hvac")
        self.assertNotIn(hvac.id, neea_co_ids)
        Relationship.objects.validate_or_create_relations_to_entity(home, earth_advantage)
        self.assertEqual(
            Message.objects.filter(content=strings.NEEA_NO_HVAC_RELATIONSHIP).count(), 0
        )

        Relationship.objects.validate_or_create_relations_to_entity(home, hvac)
        self.assertNotIn(hvac.id, neea_co_ids)
        self.assertEqual(
            Message.objects.filter(content__icontains=strings.NEEA_NO_HVAC_RELATIONSHIP[-83:])
            .filter(content__icontains="HVAC")
            .count(),
            1,
        )
