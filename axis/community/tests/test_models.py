from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase

from .factories import community_factory
from ..models import Community

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class CommunityModelTests(TransactionTestCase):
    def setUp(self):
        from axis.core.tests.factories import general_super_user_factory, general_user_factory
        from axis.company.tests.factories import general_organization_factory

        self.super_user = general_super_user_factory()
        self.user = general_user_factory()

        # company_ptr is the backwards OneToOneField field for model inheritance
        self.company = general_organization_factory()
        self.user.company = self.company
        self.user.is_company_admin = True
        self.user.save()

        self.content_type = ContentType.objects.get_for_model(Community)

    def test_can_be_deleted(self):
        from axis.company.tests.factories import general_organization_factory
        from axis.subdivision.tests.factories import subdivision_factory

        obj = community_factory()

        # Super can do anything..
        self.assertEqual(obj.can_be_deleted(self.super_user), True)

        self.assertEqual(self.user.has_perm("community.view_community"), True)
        self.assertEqual(self.user.has_perm("community.change_community"), True)
        self.assertEqual(self.user.has_perm("community.add_community"), True)
        self.assertEqual(self.user.has_perm("community.delete_community"), True)

        # Without a relationship, the object cannot be deleted
        self.assertEqual(obj.can_be_deleted(self.user), False)

        # Verify that deletion is okay if the single owning relationship is the user's company
        self.company.relationships.get_or_create_direct(
            object_id=obj.id, content_type=self.content_type
        )
        self.assertEqual(obj.can_be_deleted(self.user), True)

        # Block deletion if the relationship's company doesn't match the user's.
        different_org = general_organization_factory()
        rel = obj.relationships.get(is_owned=True)
        rel.company = different_org
        rel.save()
        self.assertEqual(obj.can_be_deleted(self.user), False)
        rel.company = self.user.company
        rel.save()

        # Verify that subdivisions block deletion
        subdivision_factory(community=obj)
        self.assertEqual(obj.can_be_deleted(self.user), False)
        obj.subdivision_set.all().delete()

    def test_can_be_edited(self):
        obj = community_factory()

        # This is mostly a placeholder, since the only check is a has_perm
        self.assertEqual(obj.can_be_edited(self.user), True)

    def test_delete_removes_relationships(self):
        obj = community_factory()
        self.company.relationships.get_or_create_direct(
            object_id=obj.id, content_type=self.content_type
        )

        the_id = obj.id
        rels = self.company.relationships

        self.assertEqual(1, rels.filter(content_type=self.content_type, object_id=obj.id).count())
        obj.delete()
        self.assertEqual(0, rels.filter(content_type=self.content_type, object_id=the_id).count())

    def test_save_copies_county_data(self):
        from axis.geographic.tests.factories import city_factory

        city = city_factory()
        kwrgs = {
            "name": "Community Test",
            "cross_roads": "Main / First",
            "website": "https://www.community.com/",
            "city": city,
        }

        obj = Community.objects.create(**kwrgs)

        self.assertEqual(obj.county, city.county)
        self.assertEqual(obj.state, city.county.state)
