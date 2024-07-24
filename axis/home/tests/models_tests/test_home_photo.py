"""test_home_photo.py: """

from axis.core.tests.testcases import AxisTestCase
from axis.home.tests.factories import home_photo_factory, custom_home_factory

__author__ = "Artem Hruzd"
__date__ = "12/22/2020 12:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class HomePhotoModelTests(AxisTestCase):
    def test_home_must_have_one_primary_photo(self):
        home = custom_home_factory()

        # create
        home_photo = home_photo_factory(home=home, is_primary=False)
        self.assertTrue(home_photo.is_primary)
        home_photo2 = home_photo_factory(home=home, is_primary=False)
        self.assertFalse(home_photo2.is_primary)
        # change
        home_photo2.is_primary = True
        home_photo2.save()
        home_photo.refresh_from_db()
        home_photo2.refresh_from_db()
        self.assertTrue(home_photo2.is_primary)
        self.assertFalse(home_photo.is_primary)
        # delete
        home_photo2.delete()
        home_photo.refresh_from_db()
        self.assertTrue(home_photo.is_primary)

        # delete everything
        home_photo.delete()
